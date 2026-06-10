---
id: "2026-06-10-claude-code-と-codex-のレート残量を確認するためにブラウザを開くのをやめた話-01"
title: "Claude Code と Codex のレート残量を確認するためにブラウザを開くのをやめた話"
url: "https://qiita.com/tatsuya582/items/5ca0c12a8495530f7d09"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "GPT", "qiita"]
date_published: "2026-06-10"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code と Codex を Pro / Plus プランで併用していると、レートリミット（5時間枠・週枠）にそれなりの頻度で当たります。当たると作業が止まるので、私は枠に当たらないように Codex と Claude を切り替えたり、モデルを切り替えたりと、調整をしながら使っていました。

ただ、その判断をするには「今どちらがどれだけ残っているか」を把握していないといけません。そのため、ブラウザを開いてレートリミットを確認していました。

この手間をなくしたくて、最終的に**Claude / Codex のレート残量を端末の1ペインに常時表示するツール**を自作することになりました。

- **想定読者**: Claude Code / Codex を併用していて、レート残量の確認が面倒だと感じている人
- **動作環境**: Claude Code 2.1.169 / Codex CLI 0.137.0 / macOS 26.5.1（Claude: Pro、Codex: ChatGPT Plus）
- **スクリプト全文**: 末尾の gist に置いています


## レート残量を何度も確認しに行っていた

冒頭の通り、私の使い方では「5時間のレートリミットはどれぐらいか」「1週間はどれぐらいか」「いつリセットされるか」を把握しておく必要がありました。

- バランスよく使う
- 5時間枠に当たりそうなら、Claude → Codex に切り替える
- 1週間枠が偏っていれば調整する
- それも厳しければモデルを変える

この判断のたびに残量を確認しにブラウザを開く、という状態でした。

## まず statusLine に出してみた

最初に思いついたのは Claude Code / Codex の statusLine に残量を出す方法でした。statusLine は CLI の画面下部に常時表示される1行のことで、Claude Code では設定でスクリプトを指定すると、その標準出力をそのまま表示できます。スクリプト側にはモデル名やセッション情報が JSON で渡ってくるため、表示内容はかなり自由に作れます（[公式ドキュメント](https://docs.claude.com/ja/docs/claude-code/statusline)）。

私もレート残量のほかに、コンテキスト使用量・git のブランチ名・docker のコンテナ数などをいろいろ表示してみて、「これで解決か」と思ったのですが、実際に使ってみると微妙でした。

### やめた理由

- Claude を開いているときは Claude、Codex のときは Codex の残量しか見えず、両方を同時に把握できない
- Codex 側は statusLine のカスタマイズの自由度があまり高くなかった
- claude / codex を起動している端末でしか表示されず、普段の作業中は見えない
- いつ時点の値なのか確信が持てず、結局「最新」を確認するためにブラウザを開いていた

残念ながら statusLine に表示しても結局ブラウザを見にいっていたので意味がありません。なので statusLine 路線はやめました。

### 収穫：残量の取得方法はわかった

ただ、statusLine をいじる過程で、Claude と Codex それぞれのレート残量の取り方はわかりました。

## 完成形：cmux の1ペインに常時表示する

私は普段 [cmux](https://cmux.com/ja) というマルチペイン端末を使っているので、1ペインを占有して残量を常時描画することにしました。表示はこんなイメージです。

```
 Agent Status  · updated 20:13:41                  ports
 ─────────────────────────────────────────         3001   api-api-1     …/apps/api
  Claude  5h ██████████░░░░  73% 1h3m  → 20:20     3308   api-db-1 …/apps/api
          7d █░░░░░░░░░░░░░  10% 6d4h  → 6/7 00:00 6380   api-redis-1   …/apps/api
  Codex   5h ██░░░░░░░░░░░░  16% 4h19m → 23:35
          7d ░░░░░░░░░░░░░░   2% 6d23h → 6/7 18:35
```

- Claude / Codex を同時に、5時間枠・週枠の利用率＋バー＋リセットまでの残り時間＋リセット時刻を表示
- CLI で何を開いていても、作業中ずっと見える
- 一定間隔で更新するので「いつ時点の値か」が明確
- ついでに、空いたスペースに使用中のポート一覧も出しました（開発サーバの待受ポートが一目でわかる）

地味ですが、視界の端に常に残量があるというのは想像以上に快適で、作ったその日からブラウザで確認しにいくことはなくなりました。

> ⚠️ ここから使う Claude の usage エンドポイントと Codex の `app-server` は、いずれも公開・安定した API ではありません。CLI のバージョンでフィールド名やエンドポイントが変わりうる前提の「自分用ツール」として読んでください。

### Claude の残量を取得する

Claude は OAuth の usage エンドポイントから取得します。トークンは `~/.claude/.credentials.json` か keychain にあります。

```sh
# トークンは credentials.json か keychain から
tok=$(jq -r '.claudeAiOauth.accessToken // empty' "$HOME/.claude/.credentials.json")
[ -z "$tok" ] && tok=$(security find-generic-password -s "Claude Code-credentials" -w \
                         | jq -r '.claudeAiOauth.accessToken // empty')

resp=$(curl -s --max-time 10 "https://api.anthropic.com/api/oauth/usage" \
         -H "Authorization: Bearer $tok" \
         -H "anthropic-beta: oauth-2025-04-20")
```

レスポンスはこのような形です（実際のもの。利用率は `0〜100` の数値、`resets_at` は ISO8601 / UTC）。

```json
{
  "five_hour": { "utilization": 3.0,  "resets_at": "2026-06-09T15:30:00+00:00" },
  "seven_day": { "utilization": 26.0, "resets_at": "2026-06-13T15:00:00+00:00" },
  "seven_day_opus":   null,
  "seven_day_sonnet": { "utilization": 0.0, "resets_at": null },
  "extra_usage": { "is_enabled": false }
}
```

- `anthropic-beta: oauth-2025-04-20` ヘッダが必要です
- 使うのは `five_hour` / `seven_day` だけ（ほかに内部用らしきフィールドも返ってきます）
- 高頻度で叩くと 429 になるので、最短55秒キャッシュ＋失敗時は前回値、という対策を入れています

### Codex の残量を取得する（`codex app-server`）

Codex は `codex app-server` に JSON-RPC を流すと現在の値が取れます。`initialize` してから `account/rateLimits/read` を呼びます。

```sh
rl=$( { printf '%s\n' \
          '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"agent-status","version":"1.0"}}}' \
          '{"jsonrpc":"2.0","id":2,"method":"account/rateLimits/read","params":{}}'
        sleep 6
      } | codex app-server 2>/dev/null \
        | jq -c 'select(.id==2).result.rateLimits' | head -1 )
```

`sleep 6` は、レスポンスが返ってくる前に stdin を閉じて `app-server` が終了してしまわないための待ち時間です（環境に合わせて調整してください）。

jq で `.result.rateLimits` を抜き出した結果はこのような形です（`credits.balance` などはマスク済み）。

```json
{
  "primary":   { "usedPercent": 1,  "windowDurationMins": 300,   "resetsAt": 1781030643 },
  "secondary": { "usedPercent": 24, "windowDurationMins": 10080,  "resetsAt": 1781150626 },
  "credits":   { "hasCredits": true, "unlimited": false, "balance": "***" },
  "planType": "plus"
}
```

- `primary` が5時間枠（`windowDurationMins: 300`）、`secondary` が週枠（`10080` = 7日）
- `resetsAt` は epoch 秒です。Claude は ISO8601 文字列なので、形式変換の処理を分けています

## 取得（daemon）と表示（viewer）を分ける

私は普段、複数プロジェクトを触っていて cmux のワークスペースを複数使っているため、表示ペインも複数箇所で開きたくなります。ただ、各ペインがそれぞれ API を叩くと、Claude は 429 になりかねませんし、Codex の `app-server` も無駄に何度も起動してしまいます。実際に 429 に当たったわけではないのですが、ペインの数だけ同じ値を取りにいくのは明らかに無駄なので、先回りして次の2つに分けました。

- **取得（daemon）**: 一定間隔で Claude / Codex / ポートを集めて、1つの `state.json` に書くだけ
- **表示（viewer）**: その `state.json` を読んで描画するだけ。各ペインで動かす

API を叩くのは daemon の1本だけなので、表示ペインをいくつ増やしても JSON を読むだけで済みます。daemon は viewer が居なくなると自動で止まり、viewer は daemon が居なければ自動で起こすようにしてあるので、ペインを開けば集計が始まり、閉じれば止まる状態になっています。後始末を気にしなくてよいのが楽です。

## 起動方法

cmux はタブを分割できるので、分割したペインで viewer を起動するだけです。ペインで `agent-status-pane` と打てば常駐表示が始まります（daemon は viewer が勝手に起こします）。

```sh
# 構成（3ファイル）
~/scripts/agent-status/agent-status-daemon.sh   # 取得（API → state.json）
~/scripts/agent-status/agent-status-pane.sh     # 表示（state.json → 画面）
~/scripts/agent-status/agent-status-labels.conf # パス → ラベル置換

# PATH の通った場所に symlink を張る（pane.sh は symlink 解決に対応）
ln -s ~/scripts/agent-status/agent-status-pane.sh ~/.local/bin/agent-status-pane
```

## まとめ

結局やったことはシンプルで、Claude と Codex の残量を API から取って `state.json` に書く daemon と、それを読んで cmux の1ペインに描く viewer に分けて常駐させただけです。statusLine ではうまくいきませんでしたが、そこで得た取得方法をもとに、最終的に自分にちょうどいいツールができました。

ちなみに製作はほぼ Claude Code 任せで、YouTube を見ながらたまに進捗を確認する、という進め方で2時間かかっていません。自分が実際に手を動かした時間だけで言えばもっと短いです。

ここで改めて思ったのは、**今は AI に指示すれば、自分専用のツールを簡単に作れる**ということです。既製のアプリやツールを入れても、欲しい機能の存在に気づいていなかったり、「なんか違う」となって結局使いこなせなかったりしがちです。一方で、自分で作ったものは機能を理解していますし、何より自分が欲しかったものそのものです。

「いいツールはないかな」と探す前に、積極的に自分で作ってしまうのもありだと思います。
同じような細かな面倒を感じている方の参考になれば幸いです。

## （付録）スクリプト全文

3ファイルとも gist に置いています（macOS ならそのまま動きます）。

👉 **[agent-status（gist）](https://gist.github.com/tatsuya582/a1d47e79370240bf9c1b7f70aead8b30)**

- `agent-status-daemon.sh` — 取得（API → `state.json`）
- `agent-status-pane.sh` — 表示（`state.json` → 画面）
- `agent-status-labels.conf` — パス → ラベル置換（サンプル）

なお、スクリプトは `date -j` / `date -r` / `security` / `osascript` といった macOS 専用コマンドを使っているため、Linux ではそのまま動きません（日付処理と keychain まわりの置き換えが必要です）。

## 株式会社シンシア

<a href="https://corp.xincere.jp/" target="_blank" rel="noopener noreferrer">株式会社xincere</a>では、実務未経験のエンジニアの方や学生エンジニアインターンを採用し一緒に働いています。
※ シンシアにおける働き方の様子はこちら

https://www.wantedly.com/companies/xincere-inc/stories

シンシアでは、年間100人程度の実務未経験の方が応募し技術面接を受けます。
その経験を通し、実務未経験者の方にぜひ身につけて欲しい技術力（文法）をここでは紹介していきます。
