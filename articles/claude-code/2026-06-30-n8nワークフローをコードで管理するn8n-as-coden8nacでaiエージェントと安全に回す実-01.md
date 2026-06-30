---
id: "2026-06-30-n8nワークフローをコードで管理するn8n-as-coden8nacでaiエージェントと安全に回す実-01"
title: "n8nワークフローをコードで管理する：n8n-as-code（n8nac）でAIエージェントと安全に回す実践"
url: "https://zenn.dev/yushiyamamoto/articles/7f6b26327754ee"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "TypeScript", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

2026-06-20 / n8n の GUI でワークフローを育てていくと、必ずどこかで「誰がいつ何を変えたか分からない」「dev で直したつもりが本番に反映されていない」「壊れたので戻したいが GUI に履歴がない」という壁に当たる。`n8n-as-code`（CLI 名 `n8nac`）は、この壁を **「ワークフローをコードとして Git 管理し、push/pull を明示的に行う」** モデルで解く。さらに AI エージェント（Claude Code など）に n8n のノードスキーマと安全な操作手順を渡せるため、エージェントにワークフロー編集を任せる土台にもなる。

本稿は公式ドキュメント（[n8nascode.dev/docs](https://n8nascode.dev/docs/)、最終更新 2026-06-05）と [GitHub リポジトリ](https://github.com/EtienneLescot/n8n-as-code) を一次情報として、**CLI のセットアップ → 同期 → dev から prod への昇格 → 失敗パターン回避** までを、実際に手を動かす順に整理する。GUI 運用から「壊れない・戻せる・レビューできる」運用へ移すための実装メモだ。

## TL;DR（導入チェックリスト）

---

## n8nac が解決する3つの痛み

n8n の標準 GUI 運用では、次の3つが構造的に起きる。

| 痛み | GUI 運用での実態 | n8nac の解 |
| --- | --- | --- |
| 変更履歴がない | 「保存」で上書き、誰の変更か残らない | ワークフローをファイル化し Git で履歴管理 |
| 環境の混線 | dev と prod を手動コピペで同期、ズレる | 環境（env）を分離し `promote` で一方向反映 |
| サイレント上書き | 同時編集で相手の変更が消える | push/pull がコンフリクト時にブロックする |

公式ドキュメントは同期の思想をこう明言している。

> 原文: Sync is explicit. The CLI and extension do not silently overwrite local or remote work.
>
> 日本語訳: 同期は明示的である。CLI と拡張機能は、ローカルやリモートの作業をサイレントに上書きしない。
>
> （出典: [Getting Started | n8n-as-code](https://n8nascode.dev/docs/getting-started/)）

`git pull` がコンフリクト時に勝手にマージせず止まるのと同じ発想だ。「黙って上書きされない」ことが、複数人・複数エージェントでワークフローを触るときの安全弁になる。

---

## コマンドは3グループだけ覚える

n8nac の世界は、覚えるべきコマンドグループが3つに整理されている。最初にこの地図を持っておくと迷わない。

| グループ | コマンド | 役割 |
| --- | --- | --- |
| 主操作 | `n8nac env` | 環境（接続先・同期フォルダ・アクティブ選択）の管理 |
| 状態確認 | `n8nac workspace` | ワークスペースのスナップショット取得 |
| ローカル実体 | `n8n-manager` | ローカル管理インスタンスの作成・起動・停止・トンネル |

ポイントは **「環境（env）」と「ローカルの n8n 本体（n8n-manager）」が別レイヤー** だということ。すでに動いている n8n Cloud / self-hosted があるなら `n8n-manager` は使わず、`n8nac env` で接続先を登録するだけでよい。

---

## セットアップ：リモート n8n に接続する

すでに稼働している n8n（Cloud か self-hosted）に接続する最小手順は次の通り。`<url>` は自分の n8n のベース URL に置き換える。

```
# 1. 環境を登録（接続先 URL と、ワークフローを置くフォルダを指定）
n8nac env add Dev --base-url https://n8n.example.com --workflows-path workflows/dev

# 2. API キーをローカルに保存（標準入力経由でキーを渡す）
n8nac env auth set Dev --api-key-stdin

# 3. この環境をアクティブにする
n8nac env use Dev

# 4. エージェント用コンテキスト（AGENTS.md）を生成（任意）
n8nac update-ai
```

ここで効いてくる安全設計が **`--api-key-stdin`** だ。API キーをコマンドライン引数に直接書くと、シェル履歴（`~/.zsh_history` など）やプロセス一覧に平文で残る。標準入力経由なら履歴に残らない。地味だが、秘密情報を漏らさないための重要な作法だ。

### 何が生成されるか

セットアップ後、プロジェクトはこうなる。

```
your-project/
├── n8nac-config.json   # 環境定義。秘密が無ければ commit してよい
├── AGENTS.md           # ローカルAIエージェント向けの n8n 指示書
├── workflows/
│   └── dev/
│       └── my-workflow.workflow.ts
└── .git/
```

* `n8nac-config.json` … 環境（接続先・パス）を保存。**API キーはここには入らない**ので、秘密が無ければ commit して共有してよい。
* `AGENTS.md` … エージェントに「このリポジトリでの n8n 作法」を渡すファイル。
* API キーやローカルインスタンスの状態は、リポジトリ外（`n8nac env auth` の保管領域や `n8n-manager` ストレージ）に留まる。

つまり **「設定はコミットできる／秘密はコミットされない」** が構造的に担保されている。これは「APIキーをリポジトリに置かない」という運用ルールと自然に噛み合う。

---

## 同期：pull で落として push で戻す

接続できたら、Git とほぼ同じ感覚で同期する。

```
# リモートのワークフロー一覧を見る
n8nac list

# 特定のワークフローをローカルに落とす（id を指定）
n8nac pull <workflow-id>

# ローカルの変更を検証してから push する
n8nac push workflows/dev/my-workflow.workflow.ts --verify
```

`--verify` を付けると push 前に検証が走る。CI やスクリプトから自動 push する場合は、**`--verify` を必須にしておく** と、壊れた定義をそのまま本番へ送る事故を1段階で止められる。

ワークフローファイルは「TypeScript Workflows」という任意のデコレータ形式でも書ける。公式はこれを「人間とエージェントが読み・差分を取り・編集しやすい形式」と位置づけている。`.workflow.ts` として保存されるので、**プルリクのレビューで普通に diff が読める** のが大きい。GUI のスクリーンショット比較から卒業できる。

---

環境を分けたら、本番反映は手コピーではなく `promote` を使う。

```
# まず差分だけ確認（実際には反映しない）
n8nac promote --from Dev --to Prod --dry-run

# 差分に納得したら、--dry-run を外して実行
n8nac promote --from Dev --to Prod
```

`--dry-run` を挟む癖をつけると、「dev で試したつもりの未完成ノードが prod に混ざる」事故を防げる。**変更は dev → prod の一方向**に固定し、prod を直接編集しない運用にすると、環境間のズレが起きにくい。

> 補足: 本番 n8n に対する `promote` は不可逆な副作用（外部送信・課金トリガを含むワークフローの有効化など）を伴いうる。`--dry-run` の差分確認は省略しないこと。最終的な本番反映は人間がレビューしてから行うのが安全だ。

---

## エージェントにワークフロー編集を任せる土台

n8nac のもう一つの価値は、AI エージェントに **「537 ノードのスキーマ・テンプレート・検証ルール・安全な操作手順」** を渡せる点にある（[GitHub README](https://github.com/EtienneLescot/n8n-as-code) より）。エージェントが n8n のノード仕様を知らないまま JSON を捏造する、という典型的な失敗を避けられる。

Claude Code から使う場合は、プラグインとして導入できる。

```
/plugin marketplace add https://github.com/EtienneLescot/n8n-as-code
/plugin install n8n-as-code@n8nac-marketplace
```

VS Code 拡張を入れていないエージェントには、ポータブルな「Generic Agent Skills」を渡す方法もある（リポジトリの `skills/` 配下、明示パスが要る場合は `skills/n8n-architect`）。

ただしエージェント連携で気をつけたいのは **「コンテキストルートを固定し、設定ファイルを手で書かせない」** こと。`n8nac-config.json` やキー保管領域をエージェントに直接編集させると、環境定義が壊れる。エージェントには `n8nac env ...` コマンド経由でだけ環境を触らせ、`env status --json` / `workspace status --json` を「真実の源」として読ませるのが安全だ。これは複数のAIツールを同じリポジトリで動かすときの一般原則（状態は backend に解決させ、設定ファイルを手書きしない）とも一致する。

---

## 失敗パターンと回避策

実際に踏みやすい落とし穴を、回避策とセットで挙げる。

### 1. API キーをコマンド引数に直書きする

`--api-key xxxx` のように引数で渡すと、シェル履歴やプロセス一覧に平文で残る。  
**回避**: 必ず `n8nac env auth set <Env> --api-key-stdin` を使い、標準入力からキーを渡す。

### 2. `workflowsPath` を推測で組み立てる

「たぶん `workflows/dev` だろう」と決め打ちすると、別環境のファイルを上書きしかねない。  
**回避**: `n8nac env status --json` の出力が、いま効いている環境と `workflowsPath` の **唯一の正** だと扱う。生の config ファイルからパスを再構築しない。

差分を見ずに昇格すると、未完成ノードや無効化したかったトリガが prod に流れる。  
**回避**: `--dry-run` で差分を確認 → 納得してから本番反映。本番反映は人間レビューを通す。

### 4. push の検証を省く

`--verify` を付けない自動 push は、壊れた定義をそのまま本番へ送る。  
**回避**: CI/スクリプトでは `n8nac push <file> --verify` を必須にする。

### 5. エージェントに設定ファイルを手書きさせる

`n8nac-config.json` やキー保管ファイルをエージェントに直接編集させると環境が壊れる。  
**回避**: 環境操作は `n8nac env ...` コマンド経由だけに限定し、`*.json` を手書きさせない。状態確認は `--json` 系コマンドの出力を読ませる。

---

## まとめ：GUI 運用から「戻せる・レビューできる」運用へ

n8nac の本質は「ワークフローを Git で扱えるようにする」ことに尽きる。整理すると次の3点だ。

1. **同期は明示的**。pull/push が黙って上書きしないので、複数人・複数エージェントでも事故りにくい。
2. **環境は分離し、promote は一方向 + dry-run**。dev の未完成物が prod に漏れない。
3. **設定はコミット可・秘密はコミット不可**が構造で担保される。`--api-key-stdin` と `n8nac-config.json` の分離がその要。

まずは1つの非クリティカルなワークフローを `pull` してファイル化し、`.workflow.ts` の diff を1回プルリクで眺めてみるところから始めるのがよい。GUI のスクリーンショット比較に戻れなくなるはずだ。

## 参考リンク
