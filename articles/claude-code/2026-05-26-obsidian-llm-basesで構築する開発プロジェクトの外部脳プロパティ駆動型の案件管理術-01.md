---
id: "2026-05-26-obsidian-llm-basesで構築する開発プロジェクトの外部脳プロパティ駆動型の案件管理術-01"
title: "Obsidian + LLM + Basesで構築する「開発プロジェクトの外部脳」：プロパティ駆動型の案件管理術"
url: "https://qiita.com/gmo-co-kitaura/items/7112baf1437877bfa799"
source: "qiita"
category: "claude-code"
tags: ["CLAUDE-md", "MCP", "API", "LLM", "cowork", "qiita"]
date_published: "2026-05-26"
date_collected: "2026-05-27"
summary_by: "auto-rss"
query: ""
---

# はじめに

「特定のツールは使っていない。チームが数名だから、今まで人依存でなんとかなっていた」

SI案件を抱えるPMなら、似たような状況に心当たりがあるかもしれません。相談から始まり、見積・受発注・要件定義・設計・実装・テスト・検収・保守まで、11工程にまたがる案件ライフサイクルを、Excelやメモとメンバーの頭の中で回している状態です。

これをAIと連携しながら省力化できないか——そう考えてObsidianを試したところ、思ったより深いところまで実用できました。ポイントは2025年にObsidianコアに加わった新機能「**Bases**」です。

この記事では実際に構築したVaultの設計思想と、Dataview・AI（Claude）との役割分担、そして試行錯誤の過程をまとめます。

## この記事で扱うツール・バージョン

| ツール | バージョン目安 |
|---|---|
| Obsidian | 1.8以降（Bases対応） |
| Dataview（コミュニティ） | 0.5系以降 |
| Templater（コミュニティ） | 2.x系 |
| Kanban Bases View（コミュニティ） | 最新版 |
| Claude（AI） | Cowork / API どちらでも |

---

# 1. なぜObsidianか：ローカルファースト × AIが読み書きできるテキスト

## 機密情報を守りながらAIを使う

SIの案件には、顧客名・金額・未公開の仕様といった機密情報が自然に含まれます。SaaSのプロジェクト管理ツールにそのまま投げ込むのはリスクがあります。

Obsidianは**ローカルファースト**です。すべてのデータはPC上のMarkdownファイルとして保存されます。Claudeを使う場合も、Cowork（デスクトップアプリ）のローカルエージェントモードで動作させれば、ファイルをクラウドに上げずにAIに読み書きさせられます。

## AIが扱いやすい理由：すべてがテキスト

Obsidianのノートは`.md`ファイルです。AIにとって、これはそのまま読める・書けるフラットなテキストです。

特に重要なのが**YAMLフロントマター**です。

```yaml
---
type: project
status: in_progress
client: 顧客A
phase: design
due: 2026-09-30
priority: P1
---
```

このプロパティ情報があれば、AIは「どのプロジェクトが、今どのフェーズで、誰が担当で、いつ期限か」を一瞬で把握できます。自然言語の本文を読む前に、メタデータだけでコンテキストを掴めるのが強みです。

## 既存ツールとの共存

Obsidianは「なんでもObsidianに移す」ツールではなく、**索引・ステータス管理・AI入力面**として使います。

| ツール | 役割 |
|---|---|
| **Google Drive** | 契約書・仕様書PDF・見積ExcelなどのMaster正本 |
| **SVN / Git** | ソースコード管理（変わらず） |
| **Obsidian** | ステータス追跡・議事録・課題・保守チケット・AIへの文脈ハブ |

DriveとSVNはそのまま残す。ObsidianはそこへのリンクとステータスをYAMLで持つ。この役割分担を最初に決めることが重要です。

---

# 2. Vault設計：フォルダ構造と役割分担

実際に構築したフォルダ構成はこちらです。

```
プロジェクト管理/
├── 00_Index/          ← MOC・Baseファイル（俯瞰用）
│   ├── 案件MOC.md
│   ├── 案件ボード.base
│   ├── 課題ボード.base
│   └── 内部ToDoボード.base
├── 01_Guides/         ← 運用ガイド（人間向け）
├── 02_Templates/      ← テンプレート12種
├── 03_Projects/       ← 案件ごとにフォルダを切る
│   ├── _例_案件A_受発注システム/
│   └── <案件名>/
│       ├── 00_案件サマリ.md   ← フロントマター付きトップノート
│       ├── 01_相談/
│       ├── 02_見積/
│       ├── 03_受発注/
│       ├── 04_要件定義/
│       ├── 05_基本設計/
│       ├── 06_実装/
│       ├── 07_テスト/
│       ├── 08_課題/
│       ├── 09_検収/
│       └── 10_保守/
├── 04_Maintenance/    ← 案件外の保守チケット
├── 05_Inbox/          ← 仕分け前メモ（議事メモをここに投げ込む）
├── 06_Archive/        ← 完了・失注済み
├── 99_Attachments/
├── CLAUDE.md          ← AIへの「システムプロンプト」（後述）
└── README.md
```

**設計のポイントは「案件フォルダ = サブフォルダ10個」の固定構造**です。どの案件も同じ構造を持つことで、Claudeが「このVaultのパターン」を学習し、初見の案件でも正しいパスに書き込めます。

`03_Projects/_例_案件A_受発注システム/` はサンプル案件です。新規案件起票時の参照先として残しておきます。

---

# 3. YAMLフロントマター設計：AIに伝わるプロパティ語彙

## 案件ノート（`type: project`）

案件の「ステータス」は2軸で管理します。

- `status`：受注プロセス上の状態（相談か、進行中か、完了か）
- `phase`：開発工程（要件定義中か、実装中か）

この2軸を分離することで、「受注確定（`status: in_progress`）だが要件定義フェーズ（`phase: requirement`）」という実態を正確に表現できます。

```yaml
---
type: project
status: in_progress       # 受注プロセスの状態
client: 顧客A
pm: yamada-taro
assignee: dev-team
phase: requirement        # 開発工程
started_at: 2026-05-01
due: 2026-11-30
priority: P1              # P1（最優先）〜 P4
related_systems: [基幹会計, 在庫管理]
tags: [type/project, phase/requirement]
updated: 2026-05-20
---
```

`status`の取り得る値はこちら。

| status | 意味 |
|---|---|
| `consultation` | 相談中・概算見積もり前（受注未確定） |
| `backlog` | 受注確定だが未着手 |
| `in_progress` | 進行中 |
| `review` | 顧客・社内レビュー待ち |
| `blocked` | 顧客回答待ちなどで停止 |
| `done` | 検収完了 |
| `lost` | 失注 |
| `cancelled` | 中止 |
| `archived` | アーカイブ済み |

`phase`の取り得る値は `estimate` / `requirement` / `design` / `implementation` / `test` / `acceptance` / `maintenance` です。

## 課題・保守チケット・ToDoも同様に

案件ノート以外も`type`フィールドで区別します。

```yaml
# 課題ノート
type: issue
status: open          # open / in_progress / review / done
severity: S2          # S1（最重要）〜 S4
project: "[[案件名/00_案件サマリ]]"

# 保守チケット
type: maintenance
category: bug         # bug / feature / inquiry / maintenance
sla_due: 2026-06-01

# 内部ToDo
type: todo
status: backlog       # backlog / in_progress / done
priority: P2
```

この`type`フィールドが後述のBasesクエリの起点になります。**すべてのノートがfrontmatterという"共通言語"を持つ**ことが、このシステム全体の肝です。

---

# 4. Dataview vs Bases：2つのクエリ機能の使い分け

ここが本記事の核心部分です。

## Dataviewとは

Dataviewは長らくObsidianのデファクト標準だったクエリプラグインです。frontmatterを読み取って、条件でフィルタリング・集計・テーブル表示できます。

```sql
-- 案件MOC.md に書くDataviewクエリ例
TABLE client AS "クライアント", phase AS "フェーズ", due AS "期限"
FROM "03_Projects"
WHERE type = "project" AND status = "in_progress"
SORT due ASC
```

**強み：** 表示のカスタマイズが柔軟、集計・GROUP BYができる  
**弱点：** **読み取り専用**。ステータスを変更するには該当ノートを開いてfrontmatterを手で書き換える必要がある

## Basesとは

Basesは**2025年にObsidianコアに入った標準機能**です。Dataviewと同じくfrontmatterをクエリしますが、決定的な違いがあります。

**BasesはGUIから直接frontmatterを編集できます。**

テーブルのセルをクリックして`status`を書き換えたり、カードビューで列間をドラッグするだけでノートのfrontmatterが更新されます。Claudeを介さなくていい。ファイルを開かなくていい。

## `.base`ファイルの実例

BasesはYAMLで記述します。実際の案件ボードがこちらです。

```yaml
# 00_Index/案件ボード.base
filters:
  and:
    - file.inFolder("03_Projects")
    - type == "project"
formulas:
  is_overdue: if(due, due < today(), false)
  days_to_due: if(due, (due - today()) / "1d", null)
properties:
  file.name:
    displayName: 案件
  status:
    displayName: ステータス
  phase:
    displayName: フェーズ
  client:
    displayName: クライアント
  due:
    displayName: 期限
  formula.days_to_due:
    displayName: 残日数
  formula.is_overdue:
    displayName: 期限超過
views:
  - type: cards
    name: ステータスボード
    groupBy:
      property: status
      direction: ASC
  - type: table
    name: 進行中のみ
    filters:
      and:
        - status == "in_progress"
    order:
      - file.name
      - phase
      - due
      - formula.days_to_due
  - type: table
    name: 期限近い順
    filters:
      and:
        - status != "done"
        - due != null
    order:
      - file.name
      - due
      - formula.days_to_due
      - formula.is_overdue
```

**注意点：** Basesのフィルタ式は`==`（Dataviewは`=`）です。ここを間違えるとビューが空になります。実際にハマった落とし穴です。

## 使い分けの結論

| 用途 | 使うもの |
|---|---|
| 日常のステータス変更 | **Bases** |
| 週次レビュー・俯瞰 | **Dataview MOC** |
| 集計・GROUP BY | **Dataview** |
| AIへの文脈渡し | **両方**（同じfrontmatterを参照するため） |

Basesでステータスを更新すると、DataviewのMOCにも自動で反映されます。データソースが同じfrontmatterだからです。

---

# 5. MOC設計：AIへ文脈を渡す「地図」を作る

## 案件サマリノートの構成

案件ごとの`00_案件サマリ.md`はこのような構成にしています。

```markdown
---
type: project
status: in_progress
client: 顧客A
phase: design
...
---

# 顧客A 基幹システムリプレイス

## 1. 概要
## 2. スコープ（やる・やらない）
## 3. 主要関係者（役割・名前・連絡先）
## 4. リンク（DriveURL・SVNブランチ）

## 5. 現在の課題（自動集計）
```dataview
TABLE ... WHERE type = "issue" AND contains(project, this.file.link) AND status != "done"
```

## 6. 保守チケット（自動集計）
```dataview
TABLE ... WHERE type = "maintenance" AND contains(project, this.file.link)
```

## 7. 直近の更新（自動集計）
```dataview
TABLE ... FROM "03_Projects" WHERE contains(project, this.file.link) SORT file.mtime DESC LIMIT 10
```

## 8. 経緯メモ
- 2026-05-01: キックオフ。スコープ確定。
- 2026-05-15: 基本設計レビュー完了。
```

**ポイントは「自動集計セクション」**です。このノートを開くだけで、案件に紐づく課題・保守チケット・最近の動きが一覧されます。Claudeに「案件Aの現状を教えて」と依頼するとき、このサマリノートを読ませれば十分なコンテキストが渡ります。

## CLAUDE.mdが「システムプロンプト」になる

Vault直下に置いた`CLAUDE.md`は、Claudeがこのフォルダを開くたびに自動で読み込まれます。ここに運用ルールを書いておくことで、毎回説明しなくて済みます。

最も効いたのが**自然言語→frontmatterマッピング表**です。

```markdown
## 自然言語 → frontmatter マッピング（案件）

| 自然言語表現 | status | phase | 備考 |
|---|---|---|---|
| 相談 / 引き合い | `consultation` | `estimate` | 経緯メモに受付経路を追記 |
| 見積もり提出 / 提出済み | `review` | `estimate` | 顧客判断待ち |
| 受注 / 発注確定 | `in_progress` | `requirement` | 開始フェーズは要件定義から |
| 実装中 / 開発中 | `in_progress` | `implementation` | |
| ブロック / 回答待ち | `blocked` | （現状維持） | |
| 失注 | `lost` | （現状維持） | 経緯メモに失注理由を追記 |
```

これがあると「顧客Aが発注確定した」という一文を受け取ったClaudeが、`status: in_progress, phase: requirement`に自動変換してfrontmatterを更新してくれます。

またCLAUDE.mdにはClaudeの**コスト削減ルール**も書いています。

```markdown
## Claudeの作業原則（コスト・品質）

1. テンプレートを毎回読まない。CLAUDE.mdの規約に従って直接書き出す
2. ステータス変更だけの依頼は、ファイル全体を読まずに編集する
   （`Edit`でfrontmatterの該当行のみを差し替える）
3. `updated`は同時に今日の日付に更新する
4. 経緯メモに必ず1行追記する（書式：`- YYYY-MM-DD: <変更内容>`）
```

これを書くだけで、ステータス変更1件あたりのトークン消費が大幅に減ります。

---

# 6. 実際に使ってわかったこと：試行錯誤の記録

## 失敗①：Coworkが別フォルダに書き込んでいた

Vaultを構築するとき、Cowork（ClaudeのデスクトップAIエージェント）に「このフォルダに書き出して」と指示しました。ところが、しばらく作業した後に確認すると、ファイルが`プロジェクト管理 (1)`というフォルダに書き込まれていました。

`プロジェクト管理`と`プロジェクト管理 (1)`という、微妙に違う名前の2フォルダが並んでいた状態です。原因は、Coworkのフォルダ接続時に誤ったパスで許可を出してしまったことでした。

**教訓：** Coworkでフォルダを接続するときは、パスをターミナルで確認してから許可する。接続後も最初の数ファイルが正しい場所に書き込まれているか確認する。

## 失敗②：Dataview + Claudeのトークンコストが高い

最初はDataviewだけで運用し、ステータス変更もClaudeに依頼していました。1案件を登録するたびに、Claudeはテンプレートを読み→既存案件のフォルダ構造を読み→サマリを書き→関連ファイルも更新……と大量のファイルを読み込みます。

体感として1件の案件登録で**入力トークン10〜20k、出力2〜3k**程度消費していました。案件が増えると、ステータス変更のたびに毎回この量が発生します。

「このVaultをClaudeで回し続けると料金が馬鹿にならないのでは？」と感じたタイミングで、**Basesへの切り替えを検討**しました。

**解決：** 日常のステータス変更はBasesのGUIで直接行う。Claudeに依頼するのは「テンプレート展開だけでは済まない作業」（新規案件起票、議事メモの整形、週次レポート作成など）に絞る。

この役割分担にしてから、Claude利用は週に数回のまとまった作業のみになり、コストが安定しました。

## 発見①：BasesとDataviewの構文差異

Basesのフィルタ式にDataviewの癖で`=`を書くとビューが空になります。

```yaml
# ❌ Dataviewの癖で書いてしまうパターン
filters:
  - status = "in_progress"

# ✅ Basesの正しい構文
filters:
  and:
    - status == "in_progress"
```

また、Basesはカードビューのグループ化にDataviewと異なるキー名を使います。`groupBy.property`にfrontmatterのキー名をそのまま指定するだけでOKです。

## 発見②：CLAUDE.mdの「ステータス変更だけならファイル全体を読まない」ルールが効く

Dataview+Claudeの高コスト問題を受けて、CLAUDE.mdにトークン節約ルールを明示したところ、Claude自身がそれに従って「このステータス変更は1行だけ差し替えます」と判断して動くようになりました。

人間がルールを書いておけば、AIが自律的にコスト最適な動きをする——この感触は、CLAUDE.mdを育てるモチベーションになっています。

---

# 7. セットアップ手順

## ステップ1：プラグインを準備する

Obsidianを起動し、設定 → コミュニティプラグイン から以下をインストール・有効化します。

| プラグイン | 用途 | 必須度 |
|---|---|---|
| **Dataview** | MOCのクエリ表示 | 必須 |
| **Templater** | テンプレートからノート生成 | 推奨 |
| **Kanban Bases View** | BasesにKanbanビューを追加 | 推奨 |

Basesはバージョン1.8以降のObsidianに標準搭載されています。コミュニティプラグインのインストール不要です。

## ステップ2：フォルダ構造を作る

Obsidianの「New folder」でフォルダを作成します。命名規則は数字プレフィックス（`00_`〜`06_`）で並び順を固定します。

## ステップ3：`CLAUDE.md`を作成する

Vault直下に`CLAUDE.md`を作成します。最低限以下を書いておきます。

```markdown
# このVaultのClaudeルール

## フォルダ規約
- 00_Index/: MOC・Baseファイル
- 03_Projects/<案件名>/: 案件サマリ（00_案件サマリ.md）＋サブフォルダ10個

## frontmatter語彙
- type: project の status値: consultation / backlog / in_progress / review / blocked / done / lost / cancelled / archived
- type: project の phase値: estimate / requirement / design / implementation / test / acceptance / maintenance

## 自然言語 → frontmatterマッピング
| 自然言語 | status | phase |
|---|---|---|
| 相談・引き合い | consultation | estimate |
| 受注確定 | in_progress | requirement |
| 実装中 | in_progress | implementation |
| 完了・検収完了 | done | acceptance |

## 作業原則
- テンプレートは毎回読まない
- ステータス変更はfrontmatterの該当行のみ編集（ファイル全体を読まない）
- updatedを今日の日付に更新する
- 経緯メモに1行追記する
```

## ステップ4：案件テンプレートを作る

`02_Templates/案件_テンプレート.md`を作成します。Templaterを使う場合は以下の形式です。

```markdown
<%*
const today = tp.date.now("YYYY-MM-DD");
-%>
---
type: project
status: backlog
client: 
pm: 
phase: estimate
started_at: <% today %>
due: 
priority: P2
tags: [type/project, phase/estimate]
updated: <% today %>
---

# <% tp.file.title %>

## 1. 概要
- クライアント: 
- 対象システム: 
- 目的・背景: 

## 2. スコープ
### やる
- 
### やらない
- 

## 5. 現在の課題（自動集計）
```dataview
TABLE WITHOUT ID file.link AS "課題", severity AS "重大度", due AS "期限"
FROM "03_Projects"
WHERE type = "issue" AND contains(project, this.file.link) AND status != "done"
SORT severity ASC, due ASC
```

## 8. 経緯メモ
- 
```

## ステップ5：Baseファイルを作る

`00_Index/案件ボード.base`を作成し、前述のYAMLを貼り付けます。Obsidianで開くとビューが自動生成されます。

Kanban Bases Viewを入れている場合は、「+ Add view」からKanbanビューを追加し、`groupBy`に`status`を指定するとドラッグでステータス変更できるカンバンになります。

---

# 8. 定型プロンプト集：AIを効果的に使う

CLAUDE.mdを整備したあとに有効だった定型プロンプトを紹介します。

**案件の現状サマリ（週次レビュー前に）**
```
03_Projects/[案件名]/ 配下を読み、現在のステータスをA4 1ページで要約して。
含める項目：案件概要・現フェーズと進捗・直近1週間の動き・
未解決課題Top5（severity高い順）・次週の主要タスク・リスク
```

**議事メモを要件定義ノートへ整形**
```
05_Inbox/[日付]_要件ヒアリング.md の内容を読み、
03_Projects/[案件名]/04_要件定義/[日付]_要件.md として整形して。
要件は[REQ-001]から連番化。ヒアリングにない項目は（未確認）と明記。
```

**保守チケットのトリアージ**
```
04_Maintenance/ 配下のstatus: backlog または in_progress のチケットを読み、
severity・SLA期限・残日数・推奨アクションの表にして。SLA超過行には先頭に警告を付ける。
```

---

# 9. このシステムの限界と次のステップ

## 向いていないケース

- **日次・時間単位でステータスが変わるタスク管理**：本システムは数週間〜数ヶ月単位で動くSI案件に最適化されています。スプリントのタスクボードには向きません。
- **10人以上のチームでの共有**：ObsidianはローカルファーストなのでGit同期等が必要になり、コンフリクト管理のコストが上がります。

## 次のステップ

**Templaterによる自動起票**：`Ctrl+Shift+N`で案件名を入力するだけで、テンプレートから10個のサブフォルダ＋サマリノートが一気に展開される仕組みを作れます。

**Claude MCPによる深い連携**：ObsidianのMCPサーバーを使うと、Claudeがファイルシステムに直接アクセスでき、Coworkよりさらに低コストで動作します。

**週次レポートの自動化**：CLAUDE.mdに「毎週金曜17時に週次レポートを生成する」とスケジュール指示を書くと、定期実行が設定できます（Claude Coworkのスケジュールタスク機能）。

---

# おわりに

Obsidian + Bases + Dataview + Claude.mdの組み合わせで実現したのは、**AIが扱いやすい形で案件情報が構造化されたシステム**です。

重要なのは「何をAIに任せるか」の役割設計です。

- **Bases**：ステータス変更などの日常操作（AIなし・ゼロトークン）
- **Dataview MOC**：週次俯瞰・読み物（AIなし）
- **Claude**：議事メモの整形・週次レポート・類似案件検索など、テンプレ展開では済まない作業

最初からすべてをAIに任せようとすると、コストがかさんで続きません。「AIを使わなくていい操作はAIを使わない」という設計が、長続きする外部脳の条件だと感じています。

Vault全体のファイル数は現在40本ほどで、案件2件・保守チケット数件を登録した状態です。小さく始めて、使いながらルールを育てていくのが現実的なアプローチです。

CLAUDE.mdに書いたルールをAI自身が守りながら動く体験は、「自分たちのAIエージェント」を育てている感覚があります。興味があればぜひ試してみてください。
