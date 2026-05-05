---
id: "2026-05-03-claude-codeの設定を育てた話-permissionhooksclaudemdsubagen-01"
title: "Claude Codeの設定を育てた話 — permission・hooks・CLAUDE.md・subagentで「任せられる環境」を作る"
url: "https://zenn.dev/yt8220/articles/f0465e79d0abd9"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "zenn"]
date_published: "2026-05-03"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

Claude Codeを使い始めた頃、設定はほぼデフォルトでした。  
とりあえず動かして、詰まったら調べる、という進め方です。

ところが使い込むほど「なんか違う」という感覚が積み重なってきました。  
確認ダイアログが多すぎる。  
テストなしでコミットしてバグを見逃す。  
Opusを使おうとしたら全部Opusになってコストが跳ね上がる。

設定は一気に完成させるものではなく、**痛みに応じて育てるもの**だと気づいたのは、しばらく経ってからでした。

この記事では、実際に直面した課題とその解決として積み上げてきた4つの仕組みを紹介します。

* **permission設計**：確認ラリーを減らしながら危険操作はブロックする
* **hooks**：セキュリティと品質を自動で担保する
* **CLAUDE.md**：エージェントを自分好みにパーソナライズする
* **subagent**：役割とモデルを分けてコストと精度を両立する

---

## permission設計：確認ラリーを減らす

### 最初の問題

デフォルト状態のClaude Codeは、ほぼすべての操作で「許可しますか？」と聞いてきます。  
安全ではあるのですが、`git status` のたびに確認を求められると作業のリズムが完全に崩れます。

かといって「全部許可」にするのは怖い。  
`rm -rf` や `git push --force` をエージェントに自由に実行させたくはありません。

### allow / deny / ask の3段構え

`settings.json` で3種類の権限を使い分けることにしました。

```
{
  "permissions": {
    "allow": ["Bash(git *)", "Bash(pnpm *)", "Bash(gh *)"],
    "deny": ["Bash(rm *)", "Bash(sudo *)", "Bash(git push --force*)"],
    "ask": ["Bash(vercel --prod*)", "Bash(pnpm convex deploy --prod*)"]
  }
}
```

* **allow**：作業中に頻繁に使う安全なコマンドを事前許可します。`git`・`pnpm`・`gh`・`docker` など40コマンド以上を登録しています
* **deny**：`rm`・`sudo`・`git rebase`・`git reset --hard`・`git push --force` など、取り消しが難しい破壊的操作を機械的にブロックします
* **ask**：本番デプロイ（`vercel --prod`・`convex deploy --prod`）や`pnpm dlx` など、実行前に必ず人間が確認すべき操作はここに入れます

「毎回確認が必要なもの」「確認不要のもの」「絶対させないもの」を明確に分けただけで、ラリーの量が大幅に減りました。

---

## hooks：個人開発だからこそセキュリティを重視する

### 個人開発ならではのリスク

チーム開発ならコードレビューやCI/CDがセーフティネットになります。  
個人開発にはそれがありません。  
エージェントがうっかり`.env`の内容をコミットしてしまうかもしれません。  
`main`に直接pushしてしまうかもしれません。

その怖さから、hooksを積極的に入れることにしました。  
Claude Codeのhooksは、ツール実行の前後やセッション終了時にシェルスクリプトを自動実行できる仕組みです。

ツール実行前に走るhooksで、危険な操作を未然に防ぎます。

**`guard-secrets.sh`**：`git commit` の直前にステージされた差分をスキャンし、APIキーや秘密鍵のパターンを検出したらコミットをブロックします。  
AWSのアクセスキー（`AKIA...`）、AnthropicのAPIキー（`sk-ant-...`）、Stripeのキー（`sk_live_...`）など主要なパターンを網羅しています。

**`guard-main-branch.sh`**：`main`/`master`への直接commit・pushをブロックします。  
エージェントが「とりあえずmainにコミット」するのを防ぎます。

**`guard-force-push.sh`**：`git push --force` を検出してブロックします。  
denyリストとの二重ガードです。

**`guard-security-edit.sh`**：`Edit`・`Write`ツールで認証・決済・Webhook関連のファイルを変更しようとした場合に警告を出します。

**`guard-pipe-to-shell.sh`**：`curl | bash` のようなパイプ経由のシェル実行を検出します。  
サプライチェーン攻撃への対策です。

### 品質ゲートhooks（PostToolUse / Stop）

**`auto-lint-format.sh`**（PostToolUse）：`Edit`・`Write`でファイルを変更するたびに自動でlint・formatを実行します。  
ESLint・Prettier・Biomeを検出して適用するので、手動でフォーマットをかける必要がなくなりました。

**`quality-gate.sh`**（Stop）：エージェントが作業を終了しようとするとき（Stopイベント）に自動でテストを実行します。  
テストが通らないとエージェントは「完了」を宣言できません。  
これを入れてからテストなしでコミットされるケースがなくなりました。

**`audit-log.sh`**（PostToolUse, async）：全ツール呼び出しをログファイルに非同期で記録します。  
「エージェントが何をしたか」をあとから追えるようにしています。  
機密情報はマスキングしてから記録します。

**`pre-compact-save.sh`**（PreCompact）：会話のコンテキストが圧縮される直前に、現在のブランチ・最近のコミット・未コミット変更などをスナップショットとして保存します。  
コンテキスト圧縮後も作業状況を把握できます。

### hooksの全体マップ

| タイミング | hook | 役割 |
| --- | --- | --- |
| PreToolUse | guard-secrets.sh | シークレット検出でコミットブロック |
| PreToolUse | guard-main-branch.sh | mainへの直接操作をブロック |
| PreToolUse | guard-force-push.sh | force pushをブロック |
| PreToolUse | guard-security-edit.sh | 高リスクファイル編集に警告 |
| PreToolUse | guard-pipe-to-shell.sh | curl|bash 系を検出 |
| PreToolUse | guard-secret-access.sh | .envや秘密鍵ファイルへのアクセスを検出 |
| PostToolUse | auto-lint-format.sh | 自動lint/format |
| PostToolUse | audit-deps.sh | 依存追加時に脆弱性スキャン |
| PostToolUse | audit-log.sh | 全操作をログ記録（非同期） |
| Stop | quality-gate.sh | 終了前に自動テスト |
| Stop | macOS通知 | 作業完了を通知 |
| PreCompact | pre-compact-save.sh | コンテキスト圧縮前にスナップショット保存 |

---

## CLAUDE.md：エージェントをパーソナライズする

### 汎用エージェントを「自分用」に育てる

デフォルトのClaude Codeは汎用的に設計されています。  
どのプロジェクトでも、どんな開発者にでも使えるように。

ただ、自分の開発スタイルや判断基準はある程度固まっています。  
「`npm`じゃなく`pnpm`を使う」「mainブランチを最新化してからfeatureブランチを切る」「型エラーを残したまま次のタスクに進まない」——これらを毎回指示するのは無駄です。

CLAUDE.mdに書いておくと、セッションをまたいでも毎回同じルールが適用されます。  
エージェントへの「チーム規約」みたいなものです。

### グローバルルールとプロジェクトルール

CLAUDE.mdは2層構造で管理しています。

**`~/.claude/CLAUDE.md`（グローバル）**：どのプロジェクトにも共通するルールを書きます。  
「禁止操作」「コード品質ゲート」「subagentの使い分け」「セキュリティ原則」などです。  
`@rules/security.md` のように別ファイルを参照させることで、分野ごとに管理できます。

**`.claude/CLAUDE.md`（プロジェクト）**：プロジェクト固有の技術スタック、ディレクトリ構造の方針、API仕様などを書きます。  
Zenn記事を管理するリポジトリにはZennの記事執筆ルールが入っています。

### prototypeモードの仕組み

本番プロジェクトとプロトタイプでは、エージェントに求める厳密さが違います。

プロトタイプ段階では「型エラーを全部直してから次のタスクへ」「コミット前に必ずreviewerを通す」といったルールが邪魔になることがあります。  
とにかく動くものを作りたいフェーズです。

そこでプロジェクトルートに `.claude/prototype` というファイルを置くだけで、品質ゲートの強制やsubagent必須化などを解除する「軽量モード」に切り替わるようにしました。  
本番昇格時にファイルを削除すれば通常モードに戻ります。

セキュリティ系のhooksと禁止操作だけはprototypeモードでも解除しません。  
いくら速度優先でも、シークレットをコミットしてしまっては取り返しがつきません。

---

## subagent：役割とモデルを分ける

### 同じエージェントでテストしても発見率が低かった

コードを書いたのと同じエージェントにテストを任せると、見落としが多くなりました。  
人間と同じで、実装者と検証者が同じだと、同じ思い込みで動いてしまいます。

そこで「実装するエージェント」と「テストするエージェント」を分けました。  
別のエージェントは実装の文脈を持っていないので、違う角度から確認してくれます。  
これだけでバグの発見率が明らかに上がりました。

### 役割×モデルの対応

役割を分けるなら、モデルも役割に合わせて使い分けます。

| agent | model | 用途 |
| --- | --- | --- |
| advisor | Opus | 設計判断・方針決定 |
| reviewer | Opus | コードレビュー |
| planner | Opus | タスク分解・計画 |
| researcher | Sonnet | Web調査・ライブラリ比較 |
| tester | Sonnet | テスト設計・実行 |
| Explore（組み込み） | Haiku | コードベース検索（read-only） |

「重い判断」はOpus、「調査・実行系」はSonnet、「ファイル検索だけ」はHaikuという分け方です。

最初にOpusを指定すると全タスクにOpusが使われてしまいます。  
それを避けるには「何をどのモデルに頼むか」を明示的に設計する必要がありました。  
これをCLAUDE.mdに書いておくことで、Executorがタスクの複雑さに応じて適切なsubagentを選べるようになっています。

### どのsubagentをいつ使うか

タスクの複雑さとsubagentの選択をCLAUDE.mdにルールとして明文化しています。

| 複雑さ | subagent |
| --- | --- |
| 単一ファイルの変更 | なし（Executor単独） |
| コードベース検索 | Explore |
| 複数ファイルの変更 | Explore + reviewer |
| 外部調査を伴う変更 | researcher + reviewer |
| アーキテクチャ判断 | planner + advisor + reviewer |

重要なのは「全タスクにsubagentを使わない」という判断です。  
typoの修正にadvisorを呼ぶのは明らかに過剰で、コストと時間の無駄になります。

---

## まとめ

Claude Codeの設定は、使い始めた日に完成するものではありません。

「確認が多すぎる」と気づいてpermissionを整理し、「テストを見逃した」と気づいてhooksを追加し、「コストが膨らんだ」と気づいてsubagentを分けました。  
CLAUDE.mdも最初は数行でしたが、毎回同じことを指示している自分に気づくたびに少しずつ育てていきました。

どこから始めるかを聞かれたら、こう答えます。

1. **まず`deny`リストを作る**：`rm`・`sudo`・`git push --force` だけでも入れておけば最悪のケースを防げます
2. **次に`guard-secrets.sh`を入れる**：シークレットの誤コミットは個人開発で一番リカバリーが大変なミスです
3. **CLAUDE.mdを育て始める**：毎回同じことを指示していると気づいたタイミングで書きます

設定に正解はなく、自分の開発スタイルと失敗の履歴が答えになります。
