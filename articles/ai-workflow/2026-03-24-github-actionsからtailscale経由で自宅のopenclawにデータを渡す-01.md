---
id: "2026-03-24-github-actionsからtailscale経由で自宅のopenclawにデータを渡す-01"
title: "GitHub ActionsからTailscale経由で自宅のOpenClawにデータを渡す"
url: "https://zenn.dev/pepabo/articles/f1499dac52c93c"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

## はじめに

自宅のRaspberry Pi 4Bで[OpenClaw](https://github.com/openclaw/openclaw)を動かしています。OpenClawはLLMを使ったAIエージェント基盤で、[Webhook API](https://docs.openclaw.ai/automation/webhook)も用意されているので外部からプロンプトを渡すこともできます。

一方、[tailscale/github-action](https://github.com/tailscale/github-action)を使えばGitHub Actionsのランナーを自宅のTailnetに参加させられることを知り、この2つを組み合わせたら面白そうだと感じていました。

私の場合は、GitHub Actionsで定期的にWebサイトをスクレイピングする[git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/)を運用しています。そこで、収集データの差分をTailscale経由でOpenClawに渡し、AIに自動分析させてDiscordに投稿するパイプラインを作ってみました。

## 全体の構成

```
GitHub Actions (cron)
  ├─ スクレイピング & git commit
  ├─ Tailscaleでホームネットワークに接続
  └─ OpenClaw (自宅Raspberry Pi上のAIエージェント) にPOST
       └─ Discordの各チャンネルに分析結果を投稿
```

GitHub ActionsのランナーからTailscale経由で自宅のRaspberry Piへアクセスするので、サーバーをインターネットに公開する必要がありません。

## tailscale/github-action

[tailscale/github-action](https://github.com/tailscale/github-action)を使うと、GitHub ActionsのランナーをTailnetに一時的に参加させられます。

```
- name: Connect to Tailscale
  uses: tailscale/github-action@v3
  with:
    oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
    oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
    tags: tag:ci
```

これだけで、ランナーから `my-pi.example-tailnet.ts.net` のようなTailscaleのDNS名でRaspberry Piへアクセスできるようになります。

OAuth clientに必要なスコープは[公式ドキュメント](https://tailscale.com/kb/1215/oauth-clients)を確認してください。`devices` ではなく `auth_keys` のwrite権限が必要です。また、`tags` に指定するタグ（上の例では `tag:ci`）はACLで事前に定義しておく必要があります。

## OpenClawのWebhook API

OpenClawは外部からHTTPリクエストでプロンプトを受け取る[Webhook API](https://docs.openclaw.ai/automation/webhook)を提供しています。`/hooks/agent` エンドポイントにPOSTすると、OpenClawがプロンプトを処理してDiscordなどのチャンネルに結果を投稿します。

```
curl -X POST https://my-pi.example-tailnet.ts.net/hooks/agent \
  -H 'Authorization: Bearer $TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"message": "今日のニュースを要約してください", "deliver": true}'
```

認証にはBearerトークンを使います。トークンはOpenClawの設定ファイルで指定します。

## 通知スクリプトの実装

Webhook APIの呼び出しをGitHub Actionsから自動化するために、設定ファイルとRubyスクリプトを用意しました。

### notify\_config.json

どのファイルが変更されたら、どんなプロンプトをOpenClawに渡すかを定義しています。

```
[
  {
    "file": "sf6_matches.json",
    "prompt": "新試合の差分: {diff}\n分析して勝敗・見直し対象を #sf6 に報告してください。"
  },
  {
    "file": "hatena_bookmark.json",
    "prompt": "本日の新着エントリ（差分）:\n{diff}\n\ntech系記事を3件以内ピックして #comms に紹介してください。"
  }
]
```

新しいデータソースを追加するときは、このJSONに1エントリ追加するだけで済みます。

### notify.rb

`git diff HEAD~1` で前回コミットとの差分を取り、変更があったファイルに対応する通知を送信します。

```
require 'json'
require 'net/http'
require 'uri'

OPENCLAW_URL = ENV.fetch('OPENCLAW_HOOKS_URL')
OPENCLAW_TOKEN = ENV.fetch('OPENCLAW_HOOKS_TOKEN')

config = JSON.parse(File.read('notify_config.json'))
changed_files = `git diff HEAD~1 --name-only 2>/dev/null`.strip.split("\n")

config.each do |entry|
  next unless changed_files.include?(entry['file'])

  diff = `git diff HEAD~1 -- #{entry['file']} 2>/dev/null`
  added_lines = diff.lines
    .select { |l| l.start_with?('+') && !l.start_with?('+++') }
    .map { |l| l[1..].rstrip }
    .join("\n")

  next if added_lines.empty?

  prompt = entry['prompt'].gsub('{diff}', added_lines)
  payload = { message: prompt, deliver: true }

  uri = URI.parse(OPENCLAW_URL)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = uri.scheme == 'https'

  req = Net::HTTP::Post.new(uri.path)
  req['Authorization'] = "Bearer #{OPENCLAW_TOKEN}"
  req['Content-Type'] = 'application/json'
  req.body = payload.to_json

  res = http.request(req)
  puts "#{entry['file']}: HTTP #{res.code}"
end
```

差分のうち追加行（`+`で始まる行）だけを抽出してプロンプトに埋め込み、OpenClawのWebhook APIにPOSTしています。

### GitHub Actionsワークフローでの組み立て

GitHub Actionsのワークフロー全体は以下のようになります。`notify.rb`が `git diff HEAD~1` を使うため、`fetch-depth: 2` で直前のコミットも取得しています。

```
name: Scrape and Notify

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2

      # スクレイピング & git commit & push

      - name: Connect to Tailscale
        uses: tailscale/github-action@v3
        with:
          oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tags: tag:ci

      - name: Notify
        run: bundle exec ruby notify.rb
        env:
          OPENCLAW_HOOKS_URL: ${{ secrets.OPENCLAW_HOOKS_URL }}
          OPENCLAW_HOOKS_TOKEN: ${{ secrets.OPENCLAW_HOOKS_TOKEN }}
```

## まとめ

GitHub Actions + Tailscale + OpenClawの組み合わせで、「データ収集→AIで分析→Discordに通知」というパイプラインを構築しました。

tailscale/github-actionでランナーを自宅のTailnetに参加させ、OpenClawのWebhook APIにPOSTする。やっていることはシンプルですが、自宅のAIエージェントをGitHub Actionsのワークフローに組み込めるのはなかなか便利です。
