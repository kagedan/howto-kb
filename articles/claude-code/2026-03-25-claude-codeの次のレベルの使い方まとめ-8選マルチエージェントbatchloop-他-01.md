---
id: "2026-03-25-claude-codeの次のレベルの使い方まとめ-8選マルチエージェントbatchloop-他-01"
title: "Claude Codeの「次のレベル」の使い方まとめ 8選【マルチエージェント・/batch・/loop 他】"
url: "https://qiita.com/tai0921/items/e93332e85cca058c6ef1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

Claude Code Meetup Japan #3（2026年3月）で共有された内容と、その周辺を調べてまとめた記事。

「インタラクティブにコードを書いてもらう」という使い方は入門編で、現在のClaude Codeはもう一段上のフェーズに来ている。この記事はそこを掘り下げる。

---

## Claude Codeの現在地

2026年に入って約2ヶ月半で、60バージョン・869の変更点がリリースされた。2025年の10ヶ月分を既に上回るペースで、リリース項目は2倍以上になっている。

使い方の進化も同じく速い。今の最先端は「エージェントを複数走らせて、自分はオーケストレーターとして指示だけ出す」フェーズに入りつつある。

---

## 1. /simplify と /batch ── PRを出す前に使わないと損をする

Claude Code v2.1.63 から入った組み込みコマンド。知らない人がまだ多い。

### /simplify ── 3つのエージェントが並列でコードを審査する

`/simplify` を打つと、3つの専門エージェントが同時に起動してコードをレビューする。

* **コード再利用エージェント**：複数箇所に出てくる同じパターンを探し、共通化できる部分を特定する
* **コード品質エージェント**：変数名・関数の分解・制御フローをレビュアー目線で読む
* **効率エージェント**：無駄なアロケーション・冗長なループ・バッチ処理できる操作を見つける

3つが終わると結果をまとめて、修正を自動で適用してくれる。

```
# 使い方
/simplify

# 特定のPRをレビューしたい場合
/simplify #123
```

Linterは構文エラーやスタイルを見る。`/simplify` はアーキテクチャの問題を見る。役割が違うので、両方使う。実際、PRごとに3〜5件の問題を見つけることが多いと報告されている。

PRを出す前に `/simplify` を打つことを習慣にするだけで、レビューで指摘される量が目に見えて減る。

---

### /batch ── 大規模変更を並列エージェントで一気に終わらせる

「このリポジトリ全体のAPIエラーレスポンスを `{ error: string, code: number }` に統一して」という作業、手でやったら何日もかかる。

`/batch` に投げると、こうなる。

```
# 使い方
/batch migrate src/ from Solid to React
/batch add input validation to all API endpoints
/batch standardize all API error responses to use { error: string, code: number } format
```

内部でこういう動きをする。

重要なのが**Worktreeによる分離**だ。各エージェントは独自のgit worktreeと独自のブランチを持つ。つまりエージェント同士がコンフリクトすることがない。1つ失敗しても他には影響しない。

全エージェントが `/simplify` を通してからPRを出すので、レビュアーが受け取るPRの品質が最初からある程度担保されている。

**向いているタスク：**「このパターンを全ファイルに適用する」という一様な変更。フレームワーク移行、命名規則の統一、型定義の追加。

\*\*向いていないタスク：\*\*ユニット間に依存関係がある変更、設計判断が必要な変更。

---

## 2. /loop ── 離席中も監視を続けてくれる

v2.1.71 から入ったコマンド。「デプロイが終わったか確認して」「CIが通ったか見て」というのを5分ごとに自分で確認していた人はこれで解放される。

```
# 5分ごとにデプロイ状況を確認
/loop 5m check the deploy status and report any changes

# 20分ごとにPR #1234 のレビューを確認
/loop 20m /review-pr 1234

# 1時間後に一回だけリマインダー
remind me in 1 hour to push this branch
```

`/loop` に投げた後は別のことをしていていい。間隔を指定しなかった場合のデフォルトは10分。

いくつか制約がある。

* **セッションスコープ**：ターミナルを閉じると全タスクが消える。永続化したければDesktop scheduled tasksかGitHub Actionsを使う
* **最大3日で自動消滅**：忘れたループが永遠に動き続けることがない設計
* **コストに注意**：5分ごとに走るタスクが1回0.05ドルかかると1日1,400円になる

一回のコストを `/cost` で確認してから間隔を決めた方がいい。

---

## 3. Worktreeサポート ── 並列作業のコンフリクトを根絶する

`--worktree` フラグでClaude Codeを起動すると、独立したWorktreeの中でセッションが動く。

```
# 認証機能の開発を独立したWorktreeで開始
claude --worktree feature-auth

# バグ修正を別のWorktreeで同時並行
claude --worktree bugfix-prod-123
```

どちらのセッションも同じリポジトリの履歴を共有しながら、別々のブランチ・別々の作業ディレクトリで動く。片方が `src/auth.ts` を書き換えている間に、もう片方が同じファイルの別アプローチを試せる。

カスタムサブエージェントにも設定できる。

```
---
name: refactor-agent
description: 独立したリファクタリング専用エージェント
isolation: worktree
---
```

前述の `/batch` も内部的にこの仕組みを使っている。

---

## 4. CLAUDE.md の本格的な使い方

CLAUDE.mdは「プロジェクトの説明ファイル」ではなく、「Claudeへの憲法」と捉えた方がいい。

### 用途別に分けて管理する

1つにまとめると肥大化して読み込みが重くなる。用途ごとに別のCLAUDE.mdを持てる。

```
.claude/
├── CLAUDE.md              # デフォルト（常時読み込み）
├── CLAUDE.review.md       # コードレビュー時に渡す
├── CLAUDE.research.md     # 調査モード用
└── CLAUDE.deploy.md       # デプロイ作業用
```

```
# CLAUDE.review.md

## レビュー観点
- セキュリティ：SQLインジェクション、XSS、認証バイパス
- パフォーマンス：N+1クエリ、不要なループ
- 型安全性：any使用禁止、nullチェック必須

## 指摘スタイル
- 修正が必須のものは「[MUST]」をつける
- 提案は「[SUGGEST]」をつける
- 絶対にほめない（ほめる時間は無駄）
```

### 禁止事項を明記する

CLAUDE.mdで最も効果があるのは「やらせたくないこと」の明記だ。

```
## 禁止事項（絶対に守ること）

### コード
- `as any` の使用禁止。型を正確に定義する
- `console.log` でのデバッグ禁止。`logger.error` を使う
- カバレッジを上げるためだけのテスト禁止（意味のないassertを書かない）

### 操作
- /src/legacy/ 以下は絶対に変更しない
- DBマイグレーションは生成するが実行しない（必ず人がレビューしてから実行）
- .env ファイルにはアクセスしない
```

これを書いておくと、「またasanyを使いやがって」というストレスがなくなる。

### CLAUDE.mdのサイズ管理

推奨は1ファイル200行以内。大きくなったらファイルを分割するか、重複を削る。プロジェクトが成長したら、Claudeに「このCLAUDE.mdを整理して」と頼むことも有効。

---

## 5. Agent Teams ── エージェントたちが直接会話して協調する

実験的機能（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`）。

従来のサブエージェントは「上司→部下」の一方向だった。Agent Teamsは「横並びのチーム」として動く。エージェント同士がメッセージを送り合い、共有タスクリストを通じて調整する。

```
# 環境変数を設定して起動
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
claude
```

```
# セッション内でチームを立ち上げる
決済モジュールをリファクタリングするチームを作って。
3人のメンバーを立ち上げてほしい：
- APIレイヤー担当
- DBマイグレーション担当
- テストカバレッジ担当

共有タスクリストを通じて調整しながら進めて。
```

実際の効果として、1年以上開発停止していたライブラリを数時間で書き換えた事例や、複数リポジトリ（管理画面・バックエンド・フロントエンド）を一つの命令で並列実装した事例が報告されている。単一エージェントと比べ2〜3倍の速度向上が出ることもある。

**使い分けの整理：**

| 状況 | 使うもの |
| --- | --- |
| 独立した大量変更を並列実行 | `/batch` |
| エージェントが結果だけ返せばいい | サブエージェント |
| エージェント同士が調整しながら進める | Agent Teams |

---

## 6. /loop × GitHub Actions × Hooksの組み合わせ

単体ではなく組み合わせることで強くなる。

### パターン①：PRが出たら自動でレビューが走る

```
# .github/workflows/claude-review.yml
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            このPRをレビューして。
            CLAUDE.mdのルールに従って指摘すること。
            セキュリティとパフォーマンスを優先して。
```

### パターン②：コードが書かれたらHooksでフォーマットが走る

```
// ~/.claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "prettier --write $CLAUDE_TOOL_INPUT_PATH 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### パターン③：タスク完了を通知する

```
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude finished\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

この3つを組み合わせると、「Claudeに投げたらデスクを離れても大丈夫」という状態が作れる。通知が来たときだけ確認すればいい。

---

## 7. Chrome DevTools MCPとの連携

ChromeのDevToolsチームが公式開発したMCPサーバー。ClaudeからChromeを直接操作できる。

できることの例：

* UIを実装してもらい → DevToolsで確認 → コンソールエラーを自動取得 → 修正 → 再確認、のサイクルを自動化
* GitHubやNotionへのスクリーンショット自動アップロード
* ログイン状態を保持したままの操作

従来のスクリーンショットベースのアプローチと違って、DevToolsのデータを構造化された形でClaudeに渡せる。トークン効率がいい。

セットアップについては[Chrome DevTools公式のMCPドキュメント](https://developer.chrome.com/docs/devtools/mcp)を参照。

---

## 8. 「AIっぽくないUI」を作るための2つのアプローチ

AIに任せると「よく見るUI」になりがちな問題。これを防ぐ方法がある。

### アプローチ①：入力を偏らせる

**画像で渡す：**  
PinterestやDribbbleで「これが好き」というUIを集めて全画面スクショし、「このデザインを言語化してから実装して」と指示する。言語化のステップを挟むことで、AIが意図を正確につかみやすくなる。

**ブランド名で渡す：**

```
Appleっぽい、ミニマムなオンボーディング画面を作って。
Stripeのダッシュボードのような、データの見やすさを重視したレイアウトで。
```

ブランド名はAIとの共通言語になる。Apple・Stripe・Linear・Vercelあたりは特に通りやすい。

### アプローチ②：出力を磨く

具体的なテクニック：

* **メッシュグラデーション**：直線的なグラデーションの代わりに使うだけで印象が変わる
* **ガラ背景（ドット・グリッド）**：無地の背景にドット or グリッドを敷くだけで見栄えが上がる
* **絵文字・アイコンを使わない**：シンプルになる
* **フォントを1つ変える**：デフォルトのsans-serifを外すだけで雰囲気が変わる

これをCLAUDE.mdのUIデザイン方針として書いておくと、毎回指示しなくて済む。

```
## UIデザイン方針
- グラデーションはメッシュグラデーションを使う（直線的なものは使わない）
- 背景にはドットパターンを敷く
- 絵文字は使わない
- フォントはGeistかMonaを使う
```

---

## 今すぐ試すならこの順番で

全部一気にやる必要はない。効果が大きい順で並べると：

1. **CLAUDE.mdに禁止事項を書く** → すぐ効く、今日できる
2. **PRを出す前に `/simplify` を打つ** → レビューコストが下がる
3. **`/install-github-app` でPR自動レビューを設定** → 一回設定すれば以後自動
4. **大きめの一様変更に `/batch` を使う** → 初めて使うと感動する
5. **`/loop` でビルド監視を自動化** → 待ち時間のストレスがなくなる

Claude Codeのアップデートは毎週のように来る。`claude --version` と `claude update` を定期的に打っておくと、新機能を取りこぼしにくい。

---

*情報は2026年3月時点。Claude Code Meetup Japan #3、Chrome DevTools MCP & Claude活用事例の共有会（2026年3月）の内容をもとに作成。*
