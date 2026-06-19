---
id: "2026-06-18-obsidian-loop-engineeringで開発を自動化-01"
title: "Obsidian ＋ Loop Engineeringで開発を自動化！"
url: "https://qiita.com/naochanz/items/2f99eef21e43c81fc56f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "qiita"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

※本実装は、後述する方々のQiita記事を**大いに、大いに**参照しております。先行して開発手法を確立されているエンジニアの方々に、まずは敬意を表します。
## はじめに：Loop Engineering と、なぜ Obsidian を組むのか

Loop Engineering は「人間が毎回プロンプトを打つ」のをやめ、プロンプトを生成・実行・検証して繰り返す“システム”を設計する考え方だ。Claude Code の `/goal` がその中核で、完了条件を一度書くと達成するまで自走する。

ただ自走には **外部メモリ** が要る。エージェントはセッションやサブエージェント間で記憶を失うので、進捗をディスクに永続化しないと迷子になる。多くの実装は Linear や git worktree を使うが、本記事では **Obsidian を「外部メモリ＋並列制御の看板」** として使う構成を紹介する。Markdown で全部見える・手元で即編集できる・既存のノート資産と地続き、が利点。

## 全体像

停止（人間の確認）は2箇所だけ：

```
Phase1 並列調査 → Phase2 仕様書 → [停止① 人間レビュー]
→ Phase3 並列実装 → Phase4 統合ゲート → Phase5 並列検証 → [停止② 構造化レビュー]
```

このフローで Obsidian が担うのは:

- **仕様書の保存先**（仕様生成スキルが vault に出力）
- **Task Board（Kanbanプラグイン）= 実装タスクの看板**（後述の肝）
- **進捗の永続化**（カードの status 遷移そのものが外部メモリになる）

## worktree をやめ、看板でファイル独立性を担保する

並列実装で worktree が要るのは「複数エージェントが同じファイルを同時に書くと衝突するから」。逆に言えば、**触るファイルが互いに素だと保証できれば worktree は要らない**。

そこで、仕様の各実装セットを Obsidian の Task Board に「触るファイル(`files`)」と「波(`wave`)」付きのカードとして書き出す:

```
- [ ] 認証(GitHub OAuth) #myapp @implementer %%{"id":"TASK-018","wave":1,"files":["app/(auth)/**","lib/supabase/**"],"status":"backlog"}%%
- [ ] SRSエンジン #myapp @implementer %%{"id":"TASK-019","wave":1,"files":["lib/srs/**"],"status":"backlog"}%%
```

司令塔（オーケストレーター）は、同じ `wave` のカードの `files` が**互いに素か**だけ確認し、素なものを同時に implementer サブエージェントへ投げる。被るカードは「統合ゲート」へ回す。これで**同じ作業ツリーのまま衝突なく並列実装**でき、worktree は「ファイル独立が怪しい時の保険」に格下げできる。

ポイント：互いに素の判定は実パスでなく**ディレクトリ/領域粒度**にすると頑健（実際の生成パスは予想とズレるため）。

## 構成

雛形はグローバル（`~/.claude/`）に置き、全プロジェクトから使えるようにする:

```
~/.claude/
├── commands/  loop-init / loop-goal
├── agents/    implementer(opus) / reviewer(sonnet)
└── skills/    feature-spec / structured-review / e2e-runner
```

プロジェクト固有設定は各プロジェクトの `.claude/loop.local.md` を**単一ソース**にする（CLAUDE.md に直書きすると二重管理でズレる）:

```md
---
project: myapp
turn_limit: 25
---
## 検証コマンド
- test: npm test
- lint: npm run lint
- build: npm run build
## 制約
- 各実装セットは宣言した files 以外を変更しない
```

## サーキットブレーカー：/goal の張り方

```
/goal 全テスト緑(npm test exit 0) かつ lint緑 かつ /structured-review 承認 or stop after 25 turns
```

注意点が一つ。`/goal` の評価器は **会話に出た文字しか見ない**（自分でコマンドを実行しない）。だから司令塔は検証コマンドを実行して **出力を会話に貼る** 必要がある。これを忘れると永遠に達成判定されない。

## 実践：新規アプリを調査から MVP まで自走させた

題材は「エンジニア向け学習管理アプリ」。

- **Phase1**：3体並列で調査（学習科学／競合ギャップ／機能・形態）。各自コードは書かず箇条書きで報告。
- **Phase2**：仕様生成スキルが2部構成（人間レビュー用＋AI実装用）の仕様と並列グループを生成し、Task Board にカード化 → **停止①で承認**。
- **Phase3**：波ごとに implementer を同時起動（認証／SRSエンジン／UI基盤 → 画面群 → 通知）。
- **Phase4**：統合ゲートで共有ファイルを結線。
- **Phase5**：reviewer を4観点（正しさ／仕様カバレッジ／重複漏れ／型・データ整合）で並列起動。

結果：Next.js + Supabase + PWA の MVP が lint/test/build 緑・**201テスト**で完成。実装は司令塔が一切書かず、全部サブエージェントに委譲した。

## ハマったところと対策

**1. /goal × 人間ゲートの無限ナッジ（最重要）**
`/goal` をフロー開始時に張ると、停止①②の人間承認待ちで「未達→続行」を繰り返し、承認が出るまで無限にナッジしてトークンを溶かす。
→ 対策：**/goal は実装フェーズ（Phase3）から arm する**。調査・仕様・承認は /goal なしの対話で進め、レビュー承認はループの外 or 最後のゲートに置く。

**2. サブエージェントの「緑」が信用できない**
並列実装中、各 implementer は「緑」と報告するのに合体すると赤、が頻発した（他セットが編集中の状態を踏むため）。
→ 対策：**各波の後に司令塔がフレッシュに検証**。サブの自己申告は信用しない。

**3. テスト設定の奪い合い**
テスト設定（vitest.config 等）の対象範囲が狭いと、各セットが設定を編集したり自前 config を乱立させ、統合時に掃除が要る。
→ 対策：**最初の scaffold で設定を完備**（include を全領域＋jsdom/jest-dom）、以降どのセットも触らない。

## まとめ

- Loop Engineering の「外部メモリ」を Obsidian で担うと、Markdown で全部見えて手元で編集でき、看板で並列制御まで賄える。
- worktree の代わりに「看板カードの files が互いに素」で並列衝突を回避できる。
- 自走の最大の罠は **人間ゲートと /goal の相性**。承認はループの外に出す。

### 参考
- Zenn: Loop Engineering と Claude Code `/goal`（ino_h） https://zenn.dev/ino_h/articles/2026-06-16-loop-engineering-goal
- Qiita: Claude Code 並列ループエージェント（kumai_yu） https://qiita.com/kumai_yu/items/54ded70a5a68a5ca15d5
- Addy Osmani: Loop Engineering https://addyosmani.com/blog/loop-engineering/
- Claude Code 公式ドキュメント: `/goal` https://code.claude.com/docs/en/goal
