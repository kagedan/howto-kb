---
id: "2026-05-04-claude-codeとgithub-projectsでissue駆動開発-01"
title: "Claude CodeとGitHub ProjectsでIssue駆動開発"
url: "https://zenn.dev/misumith/articles/01ca0394dc4a53"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

こちらの記事を参考にissueベースでの開発をやってみました。  
<https://dev.classmethod.jp/articles/claude-github-gemini/>

今回は一人でやりましたが、チームでやると便利そうです。

## 開発の流れ

1. ProjectsのBacklogレーンにIssueを作る
2. 開発するIssueをReadyに移動
3. Claude CodeにReadyにあるIssueに着手してもらう
4. Claudeがブランチ作成、開発、コミット、PR作成する
5. IssueがIn reviewレーンに移動
6. PRを確認、マージ
7. IssueがDoneに移動

## CLAUDE.md

参考にした記事を元に、Claudeに相談しながら修正して、最終的にできたファイル。  
他にもブランチの運用ルールなど色々書いてますが、今回やったことで必要なのはこの部分です。

```
## タスク管理（GitHub Projects Kanban）

### セッション開始時の手順

1. カンバンの状態を確認する:
   
   gh project item-list <PROJECT_NUMBER> --owner <OWNER> --format json --limit 100
   
2. "In progress" のissueがあれば、その作業を継続する
3. なければ、優先度順に "Ready" のissueを選んで着手する

### ステータス定義

| ステータス | 意味 |
|---|---|
| Backlog | 未着手・未スケジュール |
| Ready | 着手可能な状態 |
| In progress | 作業中 |
| In review | レビュー待ち |
| Done | 完了 |

### カンバン操作コマンド

**ステータス変更**:

gh project item-edit \
  --project-id <PROJECT_ID> \
  --id $ITEM_ID \
  --field-id <STATUS_FIELD_ID> \
  --single-select-option-id $OPTION_ID

**ステータスオプションID**:
| ステータス | オプションID |
|---|---|
| Backlog | <OPTION_ID> |
| Ready | <OPTION_ID> |
| In progress | <OPTION_ID> |
| In review | <OPTION_ID> |
| Done | <OPTION_ID> |

**優先度変更** (Priority Field ID: <PRIORITY_FIELD_ID>):
| 優先度 | オプションID |
|---|---|
| P0 | <OPTION_ID> |
| P1 | <OPTION_ID> |
| P2 | <OPTION_ID> |

**issueのアイテムIDを取得**:

gh project item-list <PROJECT_NUMBER> --owner <OWNER> --format json --limit 100 \
  | jq '.items[] | select(.content.number == <ISSUE_NUMBER>) | .id'

**issue完了時**（ステータスをDoneに変更 + issueをclose）:

gh project item-edit \
  --project-id <PROJECT_ID> \
  --id $ITEM_ID \
  --field-id <STATUS_FIELD_ID> \
  --single-select-option-id <OPTION_ID>

gh issue close <NUMBER> --repo <OWNER/REPO> --reason completed
```

### 設定値の取得方法

gh コマンドはGitHub CLIが必要なので、未インストールの場合は brew install gh → gh auth login で準備してください。

**<OWNER>**  
GitHubのユーザー名（または組織名）です。  
例：`https://github.com/hoge` なら hoge

**<PROJECT\_NUMBER>**  
GitHub ProjectsのURL末尾の数字です。  
例：`https://github.com/users/hoge/projects/3` なら 3

**<PROJECT\_ID>**  
PROJECT\_NUMBERとは別の内部IDです。以下のコマンドで取得できます。

```
gh project list --owner <OWNER>
```

**<STATUS\_FIELD\_ID> と <OPTION\_ID>**  
カンバンのステータスフィールドのIDと、各ステータス選択肢のIDです。以下で取得できます。

```
gh project field-list <PROJECT_NUMBER> --owner <OWNER> --format json
```

JSONの中に "name": "Status" というフィールドがあり、その中に各ステータス（In progress / Done など）のIDが含まれています。

**<OWNER/REPO>**  
オーナー名/リポジトリ名 の形式です。  
例：hoge/my-app

以下は動的な値で、変数（$ITEM\_ID）や文脈から判断できる値なので、Claude Codeが実行時に自動で埋めてくれます。変更する必要はありません。

**$ITEM\_ID**

`gh project item-list` の結果から自動取得

**<NUMBER>（Issue番号）**

作業対象のIssueをカンバンから読んで判断

## 開発

claudeを立ち上げて「ReadyにあるIssueを対応して」と言うだけ

---

参考記事にあるslack通知も今度やってみたい。  
開発ではよくフロントエンドとバックエンドそれぞれのリポジトリを作っていたけど、この開発手法というかAIでまるっと開発してもらう場合モノレポの方がいいんだろうかとXで調べるとけっこうそういう声があったので、一つのリポジトリにおいた方がいいようだ
