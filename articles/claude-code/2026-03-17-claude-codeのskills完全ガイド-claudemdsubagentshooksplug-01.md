---
id: "2026-03-17-claude-codeのskills完全ガイド-claudemdsubagentshooksplug-01"
title: "Claude CodeのSkills完全ガイド — CLAUDE.md・Subagents・Hooks・Pluginsの使い分け"
url: "https://zenn.dev/haboshi/articles/claude-code-skills-complete-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

Claude Code を使い始めると、最初につまずきやすいのはコード生成そのものではない。**どこに何を書くべきか**だ。

* カスタムコマンドと Skills は何が違うのか
* `CLAUDE.md` に残すべきものは何か
* Subagent を使う場面はどこか
* Hooks や Plugins は本当に必要なのか

このあたりは古い記事ほど情報が混ざりやすい。しかも Claude Code は更新が速いので、半年違うだけで説明の前提が変わる。

そこで本記事では、**Claude Code 公式ドキュメントを一次情報として確認し直し**、2026-03-15 時点での整理をまとめた。単なる機能紹介ではなく、**実務で迷わないための切り分け**に重点を置いている。

結論から先に書く。

いまの Claude Code は次のように役割分担すると、かなり扱いやすい。

* **毎回読み込ませたい常設ルール** → `CLAUDE.md`
* **必要なときだけ呼びたい知識や手順** → `Skills`
* **重い調査や役割分担** → `Subagents`
* **必ず機械的に実行したい処理** → `Hooks`
* **再利用・配布したい拡張のまとまり** → `Plugins`

そして重要なのは、**カスタムコマンドは独立した中心機能として残っているわけではなく、現在は Skills に統合された理解で捉える方が自然**という点だ。

---

## まず押さえるべき最新整理

公式ドキュメントの現在の表現では、**Custom commands have been merged into skills** となっている。

つまり、以前の `.claude/commands/deploy.md` のようなカスタムコマンドは、今でも互換性のため動く。しかし設計思想としては、**Skill として考える方が自然**になっている。

たとえば次の2つは、現在の Claude Code ではほぼ同じ `/deploy` 体験を作れる。

* `.claude/commands/deploy.md`
* `.claude/skills/deploy/SKILL.md`

違いは、Skill 側の方ができることが多いことだ。

* supporting files を持てる
* frontmatter で挙動を調整できる
* Claude が関連タスクで自動的に読み込める
* `context: fork` で Subagent 的に走らせられる

このため、**新しく作るなら基本は Skills を選ぶ**のがよい。

---

## Claude Code の拡張を5層で理解する

Claude Code の拡張ポイントは、雑に全部並べると分かりにくい。実際は次の5層で分けると整理しやすい。

### 1. `CLAUDE.md`

これは**常設の前提知識**だ。

毎セッション読み込ませたいルールを書く場所なので、たとえば次のような内容が向いている。

* このリポジトリでは `pnpm` を使う
* 変更後は必ず `pnpm test` を実行する
* API ハンドラは `src/api/handlers` にある
* PR 前に lint を通す

逆に、長い手順書やたまにしか使わない参考資料をここに詰め込むのは悪手だ。公式も `CLAUDE.md` は短く保つことを勧めていて、目安は **200行以内**。肥大化すると、毎回コンテキストを消費するうえ、肝心のルールが埋もれやすい。

### 2. Skills

Skills は**必要なときだけ読み込む知識・手順・ワークフロー**だ。

たとえば次のようなものは Skill に向く。

* `/deploy` のような定型作業
* API 設計ルール集
* コードレビュー観点
* 特定サービスの運用手順
* リリース手順や障害切り分け手順

ここが今の Claude Code 拡張の中心だと思っていい。

### 3. Subagents

Subagent は**分業用の独立ワーカー**だ。

重要なのは、Skill と Subagent は競合ではないこと。役割が違う。

* **Skill** は知識や手順を与えるもの
* **Subagent** は別コンテキストで仕事させるもの

大量のファイルを読んで調査したい、重い探索を本流から切り離したい、役割ごとに制約を変えたい。そういうときに Subagent が効く。

### 4. Hooks

Hook は**モデルの気分に任せず、機械的に必ず走らせたい処理**向けだ。

たとえば以下。

* Claude が編集したら Prettier を走らせる
* 特定ファイルの編集をブロックする
* セッション終了時に通知する
* compact 後に注意事項を再注入する

「Claude に覚えておいてもらう」ではなく、**システムとして確実に実行する**のが Hook の役割だ。

### 5. Plugins

Plugin は、Skills / Agents / Hooks / MCP / LSP などを**配布可能なまとまり**にしたものだ。

個人や単一プロジェクトで試す段階では `.claude/` 配下の standalone 構成で十分なことが多い。複数プロジェクトで再利用したい、チームに配りたい、コミュニティに公開したい、という段階で Plugin 化を考えると筋がいい。

---

## Skills をどう設計するか

Claude Code の Skill は、`SKILL.md` と frontmatter で構成される。ここで大事なのは、**Skill を「知識Skill」と「実行Skill」に分けて考えること**だ。

### 知識Skill

Claude にときどき参照してほしい知識を渡す。

例:

* API 設計の流儀
* ドメイン固有の用語集
* 障害対応時の確認観点
* UI 文言のトーンガイド

このタイプは Claude が自動で読みにいく価値があるので、`description` を丁寧に書くのが重要になる。

### 実行Skill

`/deploy` や `/review-security` のように、ユーザーが明示的に呼ぶ手順型 Skill だ。

このタイプでは、むしろ Claude が勝手に発火しない方がいい場面も多い。そういうときに使うのが `disable-model-invocation: true` だ。

つまり、

* **自動発火してほしい** → 通常の Skill
* **手動でだけ呼びたい** → `disable-model-invocation: true`

という整理になる。

### 重要フロントマター

実務で特に効くのはこのあたりだ。

* `description`: いつ使うかを Claude に伝える。最重要
* `disable-model-invocation`: 自動発火を止める
* `user-invocable`: `/` メニューに出すか制御する
* `allowed-tools`: Skill 実行中に許可するツールを絞る
* `context: fork`: 分離コンテキストで動かす
* `agent`: `context: fork` 時にどの Subagent 系を使うか指定する
* `model`: Skill 実行時のモデルを切り替える

ここでよくある誤解は、**Skill はただの長いプロンプトではない**ということだ。Claude Code 側が frontmatter を解釈して、呼び出し方・権限・実行コンテキストまで変えられる。

たとえば、手動でだけ使いたいレビューSkillならこうなる。

```
---
name: review-auth
description: 認証・認可・秘密情報の扱いを重点確認する。認証フロー変更、権限変更、公開APIの追加時に使う。
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
---

認証・認可・秘密情報の扱いをレビューする。
次を確認する:
1. 権限境界の破れ
2. secret の露出
3. token/session の扱い
4. 失敗系の考慮漏れ
```

この定義なら、Claude が勝手に起動しにくく、必要なときに `/review-auth` として呼びやすい。

---

## カスタムコマンド時代からの移行で理解しておくこと

古い記事では `.claude/commands/` を前提に説明しているものが多い。しかし今から読む側は、次の理解で十分だ。

1. **既存の commands は互換性のため動く**
2. ただし **新規作成は Skills ベースで考える**
3. commands では難しかった supporting files や拡張設定を、Skills では自然に持てる

つまり「カスタムコマンドはもう使えない」のではない。**互換性はあるが、設計の主役が Skills に移った**と理解するとズレない。

---

## `CLAUDE.md` と Skill の切り分け

ここは実務上かなり重要だ。

### `CLAUDE.md` に書くべきもの

* 毎回守るべきルール
* リポジトリ固有の前提
* build / test / lint コマンド
* 絶対にやってはいけないこと
* アーキテクチャ上の重要原則

たとえば `CLAUDE.md` はこのくらいの密度がちょうどいい。

```
# Workflow
- Use pnpm, not npm
- Run pnpm test before commit
- Prefer targeted tests before full test suite

# Architecture
- API handlers live in src/api/handlers
- Never read secrets from client-side code

# Safety
- Do not edit .env files
- Ask before destructive migration changes
```

短いが、毎回効いてほしいルールは十分入る。ここに長文の運用手順まで足し始めたら、Skill に分ける合図だ。

### Skill に書くべきもの

* たまにだけ必要な参考資料
* 特定作業の手順書
* 長めの運用ノウハウ
* ある役割だけで使う知識
* ユーザーが `/xxx` で呼びたい機能

判断基準はシンプルだ。

\*\*「毎回読ませる価値があるか」\*\*で考える。

毎回必要なら `CLAUDE.md`。必要なときだけでよければ Skill。これを守るだけで、コンテキストの無駄遣いがかなり減る。

---

## Subagents はいつ使うべきか

公式ドキュメントでも、Subagent の価値は主に次の3つに整理できる。

たとえばコードベース探索を毎回メインスレッドでやると、読んだファイルの履歴が本流に残ってコンテキストを圧迫する。Subagent に調査を投げれば、メイン側には要約だけ返せる。

特に有効なのは次のような場面だ。

* 巨大リポジトリの探索
* セキュリティ観点だけのレビュー
* テスト失敗の切り分け
* 競合する仮説の並列検証

逆に、小さい修正や単発タスクなら、無理に Subagent を使う必要はない。

---

## Hooks を入れると Claude Code が実用品になる

Hook は地味だが強い。

Claude に「編集後は必ず整形して」と書くこともできる。しかしそれは**守られない可能性があるルール**だ。Hook にすれば、**必ず走る仕組み**になる。

たとえば実用性が高いのはこのあたり。

* `PostToolUse` で `Edit|Write` に反応して formatter を実行する
* `PreToolUse` で `.env` や lockfile への編集を止める
* `Notification` で入力待ちをデスクトップ通知する
* `SessionStart` で compact 後の注意事項を再注入する

実務では、**判断は Skill / 自動化は Hook** と分けると分かりやすい。

---

## Plugins は「育ったら」使えばいい

最初から Plugin を作る必要はない。

公式も、まずは `.claude/` で standalone に試し、再利用したくなったら Plugin 化する流れを勧めている。これはかなり妥当だと思う。

Plugin 化のメリットは次の通り。

* 複数プロジェクトで共有しやすい
* スキル名が namespaced され衝突しにくい
* バージョン管理しやすい
* チーム配布や公開に向く

一方で、個人の試作段階では管理コストが増える。だから順番としては、

1. `.claude/skills` で試す
2. 運用が固まる
3. Plugin にまとめる

が一番失敗しにくい。

---

## ベストプラクティス

ここからは、公式ドキュメントを踏まえつつ、実務で効くポイントを絞って書く。

### 1. `CLAUDE.md` を太らせすぎない

これは本当に重要だ。何でも `CLAUDE.md` に足すと、毎回トークンを食い、しかもルールの効きが落ちる。

**常設ルールだけを残し、参考資料は Skill に逃がす。** これが基本になる。

### 2. Skill の `description` を雑に書かない

Claude が自動で使うかどうかは、`description` の質にかなり依存する。

悪い例は「コードレビューをする」。

良い例は「認証・認可・秘密情報の扱い・権限境界を確認するセキュリティレビュー。認証実装、権限変更、API公開範囲の確認時に使う」のように、**いつ使うかまで書く**ことだ。

### 3. 長い手順は supporting files に逃がす

Skill を1ファイルに詰め込みすぎると読みにくい。`SKILL.md` には判断の骨格だけを書き、テンプレート・参考例・補助スクリプトを別ファイルに分けた方が保守しやすい。

### 4. 重い探索は Subagent に切り出す

巨大コードベースで毎回メイン会話に探索ログを積むと、後半で精度が落ちやすい。調査専用の役割は Subagent に寄せた方が安定する。

### 5. 「絶対やる」は Hook にする

* 毎回整形する
* 特定ファイルは編集禁止
* 変更後に静的チェックする

この手のものはプロンプトで祈るより Hook で固定する方がいい。

### 6. まずは verification を用意する

これは Claude Code 全体のベストプラクティスでもある。Claude に何かさせるなら、**成功条件を自分で検証できる状態**を作る。

* テスト
* スクリーンショット比較
* lint
* 期待出力
* 再現コマンド

Skill を作るときも、最後に何を確認するかまで書いておくと、出来がかなり安定する。

---

## 個人的におすすめの実践パターン

### パターン1: 最小構成

* `CLAUDE.md`: build/test/lint と禁止事項だけ
* Skill: `/deploy`, `/review`, `/release-note`
* Hook: formatter だけ

まずはここからで十分強い。

### パターン2: チーム運用向け

* `CLAUDE.md`: チーム共通ルール
* `.claude/rules/`: 言語別・ディレクトリ別ルール
* Skills: 長い運用手順、レビュー観点、障害対応
* Hooks: guardrail と通知
* Plugin: 複数repoに配る共通資産

チームで効いてくるのはこの構成だ。

### パターン3: 巨大リポジトリ向け

* `CLAUDE.md` はかなり薄く保つ
* 探索系は Subagent 中心
* 知識は Skill に逃がす
* Hook で compaction 後の再注入も補助する

コンテキスト管理が主戦場になるので、この設計が効く。

---

## よくある誤解

### 誤解1: Skill = ただの slash command

違う。Skill は slash command として呼べるが、同時に**Claude が自動発火できる知識/手順モジュール**でもある。

### 誤解2: `CLAUDE.md` に全部書けばいい

逆。全部書くほど毎回重くなる。常設ルールに絞るべきだ。

### 誤解3: Hook があれば Skill は不要

Hook は決め打ち自動化。Skill は判断と手順の再利用。役割が違う。

### 誤解4: Plugin は最初から必要

不要。最初は standalone で十分。広く配る段階で Plugin 化すればいい。

---

## いま作るなら、どう始めるのがいいか

私なら次の順で始める。

1. `CLAUDE.md` を 100〜150 行くらいで作る
2. 毎回は不要な長文手順を Skill に分ける
3. 事故りやすい処理だけ Hook で固定する
4. 重い調査が増えたら Subagent を足す
5. 何度も使う資産になったら Plugin 化する

この順番なら、過剰設計になりにくい。

Claude Code は拡張ポイントが多いぶん、最初は全部同じ箱に見える。しかし整理してみると、やることは単純だ。

* **常設知識**は `CLAUDE.md`
* **必要時知識/手順**は Skill
* **分業**は Subagent
* **強制自動化**は Hook
* **配布**は Plugin

ここが腑に落ちると、Claude Code のカスタマイズは一気に扱いやすくなる。

---

## 直近アップデートで見えてきた方向性

2026-03-14 公開の Claude Code 2.1.76 の changelog を見ると、このツールがどこへ向かっているかが少し見えやすい。

今回の更新で目立つのは、MCP と Hooks の広がりだ。

まず、**MCP elicitation support** が追加された。これは MCP server 側が、作業途中で構造化された入力を要求できる仕組みだ。単なるテキストの聞き返しではなく、フォーム入力やブラウザ URL を使った対話が前提に入ってきている。

さらに、**`Elicitation` / `ElicitationResult` hooks** も追加された。これによって Hook は、単なる前後処理や通知だけではなく、対話の途中に入って応答を調整する方向にも広がっている。

同じ 2.1.76 では、`PostCompact` hook、`/effort` コマンド、`-n` / `--name`、`worktree.sparsePaths` なども追加されている。細かい改善に見えるが、全部まとめると方向はかなり一貫している。

Claude Code は、単なる「賢いCLIラッパー」から、**状態を持ち、途中で情報を取りに行き、複数の拡張ポイントで運用を組み立てる基盤**に寄ってきている。

だからこそ、`CLAUDE.md`、Skills、Subagents、Hooks、Plugins を個別機能として覚えるだけでは足りない。**どこに何を置くと運用しやすいか**まで考えて初めて、全体像が噛み合う。

## 参考にした一次情報

* Claude Code Docs: Skills
* Claude Code Docs: Features overview
* Claude Code Docs: Memory / CLAUDE.md
* Claude Code Docs: Subagents
* Claude Code Docs: Hooks guide
* Claude Code Docs: Plugins
* Claude Code Docs: Plugins reference
* Claude Code Docs: Best practices
* Claude Code Docs: CLI reference
