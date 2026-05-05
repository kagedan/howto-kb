---
id: "2026-05-04-claude-gemini-cliで学習データに使われないようにする設定まとめ-01"
title: "Claude / Gemini CLIで学習データに使われないようにする設定まとめ"
url: "https://qiita.com/zygm/items/49ca9350d03fa9f19c88"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "qiita"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## 概要

LLMを上手に使いこなすことは、エンジニアとして業務を行う上で今や必須だ。
ここでは、Claude DesktopとClaude Code（CLI）、そしてGemini CLIについて、
入力した情報がLLMの学習データとして利用されないようにする設定方法をまとめる。

---

## Claude Desktopにて入力した情報が学習データに取り込まれないようにする方法

下記のトグルをオフにする。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4274663/bcd01825-9e0a-4d90-b049-f33aefeb8206.png)

![u2sn0WHdKF.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4274663/dad4ecd6-33eb-43ec-9147-25b9d4d007f2.png)

---

## Claude Code CLIにて入力した情報が学習データに取り込まれないようにする方法

### ① アカウント設定（最重要）

Claude Code CLIはAnthropicアカウントに紐づいているため、**claude.aiのプライバシー設定がCLIセッションにも共通で適用される。**
Desktop同様の設定を、ブラウザから行うだけでよい。

1. [claude.ai](https://claude.ai) にブラウザでアクセス
2. **Settings → Privacy → Privacy Settings**
3. **「Help improve Claude」（モデル改善への協力）をオフ**

> **補足：** Team・Enterprise・APIプランなど商用利用の場合は、デフォルトで学習には使用されない。

### ② テレメトリ・エラーログのオプトアウト（追加対策）

学習データとは別に、CLIから送信される運用ログを止める環境変数がある。

```bash
# ~/.bashrc や ~/.zshrc に追記
export DISABLE_TELEMETRY=1
export DISABLE_ERROR_REPORTING=1
```

| 変数 | 効果 |
|---|---|
| `DISABLE_TELEMETRY` | Statsigへのレイテンシ・使用パターン等のログを無効化 |
| `DISABLE_ERROR_REPORTING` | Sentryへのエラーログを無効化 |

### ③ セッション終了時のフィードバック送信に注意

セッション評価後に「トランスクリプトをAnthropicに送信してもよいか？」という追加確認がまれに表示される。その際は、**明示的に「Yes」を選択しない限りアップロードされない。**「Don't ask again」を選べば今後この確認も表示されなくなる。

### まとめ

```
Claude Code CLIのプライバシー設定

① アカウント設定（claude.ai）
   └─ Settings → Privacy → 「Help improve Claude」をオフ
      ※ CLIセッションにも適用される

② 環境変数（ローカル設定）
   └─ DISABLE_TELEMETRY=1
   └─ DISABLE_ERROR_REPORTING=1

③ セッション終了時
   └─ トランスクリプト送信の確認は「Don't ask again」を選択
```

---

## Gemini CLIにて入力した情報が学習データに取り込まれないようにする方法

Claudeと異なり、Geminiは**認証方法・アカウント種別によって学習利用の可否が変わる。**
まず自分がどのパターンで使っているかを確認するところから始める。

### 認証方法別：学習に使われるか一覧

| 認証方法 | 学習に使われるか |
|---|---|
| 個人Googleアカウント（Gemini Code Assist個人版） | **使われる**（オプトアウト可） |
| Google Workspace（Standard/Enterprise） | **使われない** |
| Vertex AI / Google Cloud APIキー | **使われない** |
| Gemini Developer API 無料枠 | **使われる** |
| Gemini Developer API 有料枠 | **使われない** |

### 個人Googleアカウントでオプトアウトする方法

CLIから以下のコマンドで確認・設定できる。

```bash
> /privacy
```

または Usage Statistics の設定を変更する。

```bash
> /stats
```

「Usage Statistics」をオフにすることで、匿名テレメトリとプロンプト・回答の収集を無効にできる。

なお、Webブラウザ版・スマホアプリ版と共通のアカウント設定として [myaccount.google.com](https://myaccount.google.com) から「Geminiアプリ アクティビティ」をオフにする方法も有効だ。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4274663/c60afdb3-9242-4db1-94fb-145c57c7f79b.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4274663/6d93c9c1-de1d-413f-9f48-4868414b0a19.png)

### ⚠️ 注意点

2025年6月リリースの公式Gemini CLIにおいて、GitHubのIssueで「CLIのヘルプ出力やコマンド内にプライバシー通知やオプトアウト方法の案内がない」と指摘されており、**設定方法が非常にわかりにくい状態**だ。
個人アカウントで業務利用する場合は、後述の「確実に学習されない方法」への移行を検討したい。

### 確実に学習されない方法（推奨）

- Google Workspaceアカウントで利用する
- Vertex AI APIキーで利用する（有料）
- Gemini Developer API 有料プランで利用する

### まとめ

```
Gemini CLI のデータ学習オプトアウト

① 個人Googleアカウントの場合
   └─ CLIで /privacy または /stats を実行
   └─ Usage Statistics をオフに設定
   └─ または myaccount.google.com でアクティビティをオフ

② 確実に学習されない方法（推奨）
   └─ Google Workspaceアカウントで利用する
   └─ Vertex AI APIキーで利用する（有料）
   └─ Gemini Developer API 有料プランで利用する
```

---

## ClaudeとGemini：プライバシー設定の構造比較

| | Claude | Gemini CLI |
|---|---|---|
| 設定の複雑さ | **シンプル**（1箇所で一元管理） | **複雑**（認証方法によって異なる） |
| 個人利用のデフォルト | 学習に使われる（オプトアウト可） | 学習に使われる（オプトアウト可） |
| 商用・API利用 | デフォルトで学習されない | 認証方法による |
| CLI固有の設定 | 環境変数でテレメトリ制御可 | `/privacy` `/stats` コマンドで制御 |

ClaudeはDesktop・CLI・ブラウザの設定が**同一のアカウント設定で一元管理**されているのに対し、Geminiは**認証方法によって挙動が全く異なる**点に大きな違いがある。

いずれにしても、業務でLLMを使う際はまずプライバシー設定を確認することを習慣にしたい。
