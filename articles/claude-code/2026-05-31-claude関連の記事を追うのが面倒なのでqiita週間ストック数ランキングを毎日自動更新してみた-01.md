---
id: "2026-05-31-claude関連の記事を追うのが面倒なのでqiita週間ストック数ランキングを毎日自動更新してみた-01"
title: "Claude関連の記事を追うのが面倒なので、Qiita週間ストック数ランキングを毎日自動更新してみた"
url: "https://qiita.com/4q_sano/items/1bc5e0669a8f0166936c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "Python", "qiita"]
date_published: "2026-05-31"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude、Claude Code、MCP、AIエージェント関連の記事が増えてきました。

ただ、新しい記事や注目記事を追いたいたびにQiitaで検索して、ストック数を見比べて、というのを手動でやるのは地味に手間です。

そこで、Qiita API v2 と GitHub Actions を使って、`claude` / `ClaudeCode` / `MCP` タグの記事を毎日自動集計し、週間ストック数ランキングとして表示する仕組みを作りました。

実際に自動更新しているランキングページはこちらです。

[Qiita Claude関連タグ 週間ストック数ランキング【毎日自動更新】](https://qiita.com/4q_sano/items/b2100c31a1fb61116ace)

作成したGitHubリポジトリはこちらです。

[qiita-claude-ranking](https://github.com/TakanobuSano/qiita-claude-ranking)

## 作ったもの

QiitaのClaude関連タグ記事を自動集計するランキング生成ツールです。

対象タグは `claude` / `ClaudeCode` / `MCP` の3つです。集計条件は以下のようにしました。

- 直近7日間に投稿された記事を対象にする
- `stocks_count` の降順で並べる
- 複数の対象タグが付いた記事は記事IDで重複排除する
- Markdown と CSV を出力する
- GitHub Actions でランキング生成・Qiita記事更新を実行する
- Qiita の既存記事を自動更新する
- GitHub Actions の `schedule` が不安定な場合に備えて、cron-job.org からも起動できるようにする

最終的に、同じQiita記事URLで常に最新のランキングを見られるようにしています。

## なぜ作ったのか

一番の目的は、Claude関連の記事を追いやすくすることです。

Qiitaには技術記事が多く投稿されますが、特定テーマを継続的に追う場合、手動検索だけだと効率が悪くなります。たとえばClaude Code関連の記事を確認したいとき、毎回こんな操作をしていました。

- `ClaudeCode` で検索する
- `claude` で検索する
- MCP関連も別途確認する
- 投稿日順や人気順を切り替える
- ストック数が多い記事を探す
- 同じ記事を何度も見てしまう

この作業を自動化できれば、注目記事を効率よく追えると考えました。

## 実際のランキングページ

今回作成したランキングページはこちらです。

[Qiita Claude関連タグ 週間ストック数ランキング【毎日自動更新】](https://qiita.com/4q_sano/items/b2100c31a1fb61116ace)

このページは、GitHub Actions と Qiita API v2 を使って毎日自動更新されます。

ポイントは、毎回新しいQiita記事を投稿するのではなく、**既存のQiita記事を更新している**ことです。そのため、記事URLは変わりません。

```text
同じQiita記事URL
↓
毎日自動更新
↓
常に最新ランキングを表示
```

過去記事が増え続けることもなく、1つのランキングページとして運用できます。

## 全体構成

全体の流れは以下です。

```text
GitHub Actions
↓
fetch_ranking.py
↓
Qiita API v2から記事を取得
↓
直近7日間の記事に絞り込み
↓
記事IDで重複排除
↓
stocks_count順でランキング化
↓
Markdown / CSVを生成
↓
output/ に保存
↓
update_qiita_item.py
↓
Qiitaの既存記事をPATCH更新
```

さらに、GitHub Actions の `schedule` が期待どおり発火しない場合に備えて、cron-job.org から `workflow_dispatch` を叩く構成も追加しました。

```text
cron-job.org
↓
GitHub REST API
↓
workflow_dispatch
↓
GitHub Actions 実行
```

GitHubリポジトリはこちらです。

[qiita-claude-ranking](https://github.com/TakanobuSano/qiita-claude-ranking)

## リポジトリ構成

リポジトリ構成は以下です。

```text
qiita-claude-ranking/
├── .github/
│   └── workflows/
│       └── weekly-ranking.yml
├── output/
│   ├── qiita_claude_ranking_YYYYMMDD.md
│   └── qiita_claude_ranking_YYYYMMDD.csv
├── fetch_ranking.py
├── update_qiita_item.py
├── .gitignore
└── README.md
```

主なファイルの役割は以下です。

| ファイル | 役割 |
| --- | --- |
| `fetch_ranking.py` | Qiita API v2から記事を取得してランキングを生成する |
| `update_qiita_item.py` | 生成したMarkdownを使ってQiitaの既存記事を更新する |
| `weekly-ranking.yml` | GitHub Actionsでランキング生成・Qiita更新を実行する |
| `output/` | 生成されたMarkdownとCSVを保存する |
| `README.md` | 使い方や構成を説明する |

## Qiita API v2で記事を取得する

記事取得には、Qiita API v2 の `GET /api/v2/items` を使います。検索クエリは、タグごとに分けて実行します。

```text
tag:claude created:>=YYYY-MM-DD
tag:ClaudeCode created:>=YYYY-MM-DD
tag:MCP created:>=YYYY-MM-DD
```

最初は検索クエリでまとめて取得することも考えましたが、実装を安定させるため次の方式にしました。

```text
1. claude タグの記事を取得
2. ClaudeCode タグの記事を取得
3. MCP タグの記事を取得
4. 記事IDで重複排除
5. stocks_count 降順で並べる
```

このほうが処理の見通しがよく、重複排除もしやすいです。

## ランキングの定義

このランキングは、以下の定義で作成しています。

```text
直近7日間に投稿された claude / ClaudeCode / MCP タグ記事の
集計時点における累計ストック数ランキング
```

:::note warn
ここは誤解されやすいので補足します。これは「この1週間で増えたストック数ランキング」ではありません。
Qiita API v2 で取得できる `stocks_count` は記事の現在の累計ストック数です。
そのため今回のランキングは「週間増加数」ではなく、「直近7日間に投稿された記事の累計ストック数順」になります。
:::

## MarkdownとCSVを出力する

ランキング結果は、MarkdownとCSVの両方で出力しています。

```text
output/
├── qiita_claude_ranking_YYYYMMDD.md
└── qiita_claude_ranking_YYYYMMDD.csv
```

MarkdownはQiita記事更新用、CSVは後から分析するための保存用です。

Markdownの表示形式は、表形式ではなくランキング記事として読みやすい形式にしました。本文に表示用のMarkdownを埋め込むため、外側は4本のバッククォートで囲んでいます。

````markdown
## 1位 [記事タイトル](https://qiita.com/...)

**100ストック**　**120いいね**　/　[user_name](https://qiita.com/user_name) さん 2026-05-28 10時投稿

`Claude` `ClaudeCode` `AI` `LLM`
````

表形式よりも、順位・タイトル・ストック数が見やすくなります。

## GitHub Actionsで毎日自動実行する

GitHub Actions の設定ファイルは、以下に配置します。

```text
.github/workflows/weekly-ranking.yml
```

毎日実行するため、`schedule` を設定しました。

```yaml
on:
  workflow_dispatch:

  schedule:
    # 毎日 09:37 JST に実行
    # UTCでは 00:37
    - cron: "37 0 * * *"
```

これで毎日 09:37 JST に実行されます。`workflow_dispatch` も入れているので、GitHubのActions画面から手動実行もできます。

## GitHub Actionsのscheduleが不安定な場合に備える

GitHub Actions の `schedule` で定期実行は可能です。ただ実際に運用してみると、指定した時刻に `schedule` が実行されないケースがありました。

そこで `schedule` だけに完全依存せず、外部cronサービスの [cron-job.org](https://cron-job.org/en/) も併用する構成にしました。

cron-job.org は、指定したURLに対して定期的にHTTPリクエストを送信できるサービスです。GitHub Actions 側に `workflow_dispatch` を設定しているため、cron-job.org から GitHub API を叩くことで、外部からworkflowを起動できます。

```text
cron-job.org
↓
GitHub REST API
↓
workflow_dispatch
↓
GitHub Actions 実行
↓
Qiitaランキング生成
↓
Qiita記事をPATCH更新
```

つまり、GitHub Actions の `schedule` は保険として残しつつ、外部cronからも起動できる構成です。

## GitHub Fine-grained PATを作成する

cron-job.org から GitHub Actions を起動するには、GitHub APIを呼び出すための Personal Access Token が必要です。権限を最小化するため Fine-grained personal access token を使いました。設定内容は以下です。

```text
Repository access:
Only select repositories
→ TakanobuSano/qiita-claude-ranking

Repository permissions:
Actions: Read and write

Metadata:
Read-only
```

`Metadata: Read-only` は GitHub 側で必須として付与される権限です。

![GitHub Fine-grained PATの設定画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82835/828ebc26-044b-43aa-8449-4e940a07f339.png)


重要なのは、対象リポジトリを `qiita-claude-ranking` のみに絞ることです。また、`workflow_dispatch` を外部から起動するため、`Actions` は `Read and write` にします。

## cron-job.orgのCommon設定

cron-job.org 側では、以下のようにcronjobを作成しました。

```text
Title:
Qiita Claude Ranking Dispatch

URL:
https://api.github.com/repos/TakanobuSano/qiita-claude-ranking/actions/workflows/weekly-ranking.yml/dispatches

Execution schedule:
Every day at 9:13

Timezone:
Asia/Tokyo
```

cron-job.org 側では `Asia/Tokyo` を指定できるため、GitHub Actions の cron のようにUTCへ変換する必要はありません。

![cron-job.orgのCommon設定画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82835/86c45e01-0c60-46e0-b7bd-cf7eef991fbe.png)


## cron-job.orgのAdvanced設定

Advancedタブでは、GitHub API に対して `POST` リクエストを送る設定にします。

```text
Request method:
POST
```

Headers は以下です。

```text
Accept: application/vnd.github+json
Authorization: Bearer <GitHub Fine-grained PAT>
Content-Type: application/json
X-GitHub-Api-Version: 2022-11-28
```

Request body は以下です。

```json
{"ref":"main"}
```

![cron-job.orgのAdvanced設定画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82835/195f71e6-db37-4b73-8177-7e0bf1eacf7c.png)


`ref` には、workflowを実行するブランチ名を指定します。今回は `main` ブランチで実行するため、以下のようにしています。

```json
{"ref":"main"}
```

## TEST RUNで動作確認する

cron-job.org の設定後、`TEST RUN` を実行しました。GitHub API から `204 No Content` が返れば成功です。

`204 No Content` はレスポンス本文がないため一見分かりにくいですが、GitHub側が `workflow_dispatch` のリクエストを受け付けた状態です。

その後、GitHub の Actions タブを確認すると、cron-job.org から起動された workflow が実行されます。

## 生成結果をGitHubに自動コミットする

GitHub Actionsで生成した `output/` を、そのままGitHubに保存するようにしています。

まず、GitHub Actions からリポジトリへコミットできるように、workflowに以下の権限を付与しています。

```yaml
permissions:
  contents: write
```

ランキング生成後は、`output/` にMarkdownとCSVが出力されます。

```text
output/
├── qiita_claude_ranking_YYYYMMDD.md
└── qiita_claude_ranking_YYYYMMDD.csv
```

ただし、毎日実行すると `output/` 配下にファイルが増え続けます。

そのため、現在のworkflowでは、コミット前に **最新5日分のファイルだけを残し、それより古いファイルを削除する処理** を入れています。

```yaml
- name: Keep latest 5 days of output files
  run: |
    python - <<'PY'
    from pathlib import Path
    from collections import defaultdict
    import re

    output_dir = Path("output")
    pattern = re.compile(r"^qiita_claude_ranking_(\d{8})\.(md|csv)$")

    files_by_date = defaultdict(list)

    for path in output_dir.glob("qiita_claude_ranking_*.*"):
        match = pattern.match(path.name)
        if not match:
            continue

        date_text = match.group(1)
        files_by_date[date_text].append(path)

    # 日付の新しい順に並べて、最新5日分だけ残す
    keep_dates = set(sorted(files_by_date.keys(), reverse=True)[:5])

    for date_text, paths in files_by_date.items():
        if date_text in keep_dates:
            continue

        for path in paths:
            print(f"delete: {path}")
            path.unlink()

    print("keep dates:", ", ".join(sorted(keep_dates, reverse=True)))
    PY
```

この処理により、`output/` 配下には最新5日分のランキングファイルだけが残ります。

その後、以下のステップで生成・削除された差分をGitHubにコミットします。

```yaml
- name: Commit ranking outputs
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"

    git add -A output/

    if git diff --cached --quiet; then
      echo "No changes to commit."
    else
      git commit -m "Update weekly Qiita Claude ranking"
      git push
    fi
```

ポイントは、`git add output/` ではなく、以下を使っている点です。

```bash
git add -A output/
```

`git add -A output/` にすることで、新しく生成されたファイルだけでなく、古くなって削除されたファイルもコミット対象になります。

つまり、現在の運用では以下のようになります。

```text
ランキング生成
↓
output/ にMarkdown / CSVを出力
↓
最新5日分だけ残して古いファイルを削除
↓
追加・更新・削除の差分をGitHubにコミット
↓
GitHub上の output/ が常に最新5日分に保たれる
```

これにより、毎日自動更新しても `output/` にファイルが溜まり続けることを防げます。



## Qiita記事を更新するスクリプト

Qiita記事の更新には、`update_qiita_item.py` を使っています。このスクリプトでは、最新のMarkdownファイルを読み込み、Qiitaの既存記事を更新します。

```text
output/qiita_claude_ranking_YYYYMMDD.md
↓
本文として読み込む
↓
Qiita API v2で既存記事をPATCH更新
```

タイトルは以下のようにしました。

```text
Qiita Claude関連タグ 週間ストック数ランキング【毎日自動更新】
```

「週間ストック数ランキング」でランキング内容を伝えつつ、「毎日自動更新」で仕組みの特徴も伝える狙いです。

## GitHub Secretsに登録する値

Qiita記事を更新するには、アクセストークンなどの情報が必要です。

:::note alert
アクセストークンを YAML やソースコードに直接書いてはいけません。必ず GitHub Secrets に登録してください。
:::

必要なSecretは以下です。

| Secret名 | 内容 |
| --- | --- |
| `QIITA_ACCESS_TOKEN` | Qiitaで発行したアクセストークン |
| `QIITA_ITEM_ID` | 更新対象のQiita記事ID |

GitHub Actions側では、以下のように参照します。

```yaml
env:
  QIITA_ACCESS_TOKEN: ${{ secrets.QIITA_ACCESS_TOKEN }}
  QIITA_ITEM_ID: ${{ secrets.QIITA_ITEM_ID }}
  QIITA_POST_PRIVATE: "false"
```

:::note info
初回テストでは `QIITA_POST_PRIVATE` を `"true"` にして限定共有で確認するのが安全です。問題なく更新できることを確認してから、公開用に `"false"` に変更します。
:::

```yaml
QIITA_POST_PRIVATE: "true"
```

## QIITA_ITEM_IDとは

`QIITA_ITEM_ID` は、Qiita記事URLの末尾にあるIDです。たとえば記事URLが以下の場合、

```text
https://qiita.com/your_name/items/abcdef1234567890abcd
```

`QIITA_ITEM_ID` に入れる値は以下です。

```text
abcdef1234567890abcd
```

URL全体ではなく、最後のIDだけを登録します。

## ハマった点：GitHub Actionsのscheduleが想定どおり動かない

GitHub Actions の `schedule` を設定していても、想定した時刻に実行されないことがありました。

そこで cron-job.org から GitHub API の `workflow_dispatch` を叩く構成を追加しています。この構成により、`schedule` だけに依存せず、外部cronからworkflowを起動できます。

## 現在の運用イメージ

現在は、以下のような運用になります。

```text
毎日 09:13 JST
↓
cron-job.org が GitHub API にPOST
↓
GitHub Actions の workflow_dispatch が発火
↓
Qiita API v2から claude / ClaudeCode / MCP タグ記事を取得
↓
直近7日間の記事をランキング化
↓
Markdown / CSVを生成
↓
GitHubの output/ に保存
↓
Qiitaの既存記事をPATCH更新
↓
同じQiita記事URLで最新ランキングを表示
```

GitHub Actions の `schedule` も保険として残しています。これにより `schedule` が期待どおり発火しない場合でも、cron-job.org から `workflow_dispatch` を起動してランキング更新を継続できます。

## READMEも整備した

リポジトリにはREADMEも用意しました。

[qiita-claude-ranking](https://github.com/TakanobuSano/qiita-claude-ranking)

READMEには、できること、ランキングの定義、ファイル構成、各スクリプトの役割、GitHub Actionsの実行タイミング、必要なGitHub Secrets、ローカルでの実行方法、注意事項、今後の改善案をまとめています。リポジトリを見るだけでも全体の仕組みが分かるようにしています。

## まとめ

Claude関連の記事を追いたいと思っても、毎回Qiitaで検索するのは手間です。そこで Qiita API v2 と GitHub Actions を使い、Claude関連タグの週間ストック数ランキングを毎日自動更新する仕組みを作りました。

ポイントは以下です。

- Qiita API v2で記事を取得する
- `claude` / `ClaudeCode` / `MCP` タグを対象にする
- 直近7日間の記事を `stocks_count` 順に並べる
- GitHub Actionsでランキング生成・Qiita更新を実行する
- `schedule` が不安定な場合に備えて cron-job.org も併用する
- cron-job.org から `workflow_dispatch` を起動する
- Markdown / CSVをGitHubに保存する
- Qiita記事は新規投稿ではなくPATCHで上書き更新する
- 同じQiita記事URLで最新ランキングを見られるようにする

実際のランキングページはこちらです。

[Qiita Claude関連タグ 週間ストック数ランキング【毎日自動更新】](https://qiita.com/4q_sano/items/b2100c31a1fb61116ace)

作成したリポジトリはこちらです。

[qiita-claude-ranking](https://github.com/TakanobuSano/qiita-claude-ranking)

Claude関連の記事を効率よく追いたい人や、Qiita API v2、GitHub Actions、cron-job.org を使った自動更新の実践例を知りたい人の参考になれば幸いです。
