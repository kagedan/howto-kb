---
id: "2026-04-11-goでclaude-cliを自作した-claude-codeが18-issueを自律実装した記録-01"
title: "GoでClaude CLIを自作した — Claude Codeが18 Issueを自律実装した記録"
url: "https://qiita.com/kai_kou/items/f5220a9aa84e075180ac"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

> **ソースコードは GitHub で公開中です**  
> <https://github.com/kai-kou/go-claude-code>  
> `go install github.com/kai-kou/go-claude-code/cmd/claude-cli@latest` で今すぐ使えます。

## はじめに

ターミナルからClaude AIを素早く呼び出せるCLIツールが欲しかった。`curl` でAPIを叩くたびにJSONを手書きするのは非効率で、繰り返し作業になる。シングルバイナリで動き、パイプやファイルと組み合わせられるツールがあれば、日々の作業効率が上がる。

そこでGoを使ったCLIツール **claude-cli** を作成しました。さらに面白いのは、その実装の大部分を **Claude Code** が自律的に行ったという点です。

### この記事で紹介すること

* claude-cli の設計と機能
* Claude Codeに18個のIssueを割り当てた自律実装の流れ（3フェーズ）
* SSEストリーミング・指数バックオフリトライ・GoReleaserのポイント
* Claude Codeを使った開発で気づいたこと

### 対象読者

* Go CLIツール開発に興味のあるエンジニア
* Claude APIをシェルスクリプトやCI/CDで活用したい方
* Claude Code（AI開発アシスタント）の実力を知りたい方

### 前提知識

* Go言語の基本
* GitHub Actions の概要
* Claude API（Anthropic）の基本概念

---

## TL;DR

* **claude-cli**: Go製シングルバイナリ、起動50ms以内でClaude APIを呼び出すCLIツール
* **SSEストリーミング** でレスポンスを逐次表示、TTY自動検出
* **リトライ機構**: 429/529エラーを指数バックオフで自動リトライ
* **プリセット**: `translate-ja`（英→日翻訳）・`summarize-ja`（日本語要約）内蔵
* **GoReleaser** でLinux/macOS/Windows向けマルチプラットフォームバイナリを自動リリース
* Claude Codeが **18 GitHub Issue** を **3フェーズ** に分けて自律実装
* **GitHub**: <https://github.com/kai-kou/go-claude-code> ⭐ Star歓迎！

---

## インストール方法

```
# go install（推奨）
go install github.com/kai-kou/go-claude-code/cmd/claude-cli@latest

# または GitHub Releases からバイナリをダウンロード
curl -L https://github.com/kai-kou/go-claude-code/releases/latest/download/claude-cli_linux_amd64.tar.gz | tar xz
sudo mv claude-cli /usr/local/bin/

# APIキーを設定（Anthropic Consoleで取得）
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## なぜ作ったか

日常的にClaude APIを使う場面で、毎回 `curl` コマンドを書くのは手間がかかる。

```
# この作業を繰り返したくない
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-4-5-20251001","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'
```

これを一発で呼び出せるツールがあれば：

```
claude-cli "Hello"
echo "The quick brown fox" | claude-cli --preset translate-ja
cat document.txt | claude-cli --preset summarize-ja
```

シェルの一等市民として使えるなら、翻訳・要約・コードレビューなど日々の作業に組み込める。

---

## claude-cli の機能概要

### 基本コマンド

```
# 引数で質問
claude-cli "Explain Go interfaces in simple terms."

# パイプで入力
echo "Hello, world!" | claude-cli --preset translate-ja
# → こんにちは、世界！

# ファイルを入力
claude-cli -f document.txt --preset summarize-ja

# システムプロンプトを直接指定
claude-cli --system "あなたはGoの専門家です。" -f main.go
```

### 主な機能

| 機能 | 説明 |
| --- | --- |
| SSEストリーミング | TTY検出で自動切り替え、`--stream`/`--no-stream` で強制指定 |
| プリセット | `translate-ja`（英→日）、`summarize-ja`（日本語要約）内蔵 |
| 設定ファイル | `~/.claude-cli/config.yaml` でデフォルト値を永続設定 |
| シェル補完 | bash / zsh / fish / PowerShell 対応 |
| リトライ | 429・529エラーを指数バックオフで自動リトライ |
| JSON出力 | `--json` フラグでスクリプト連携向け構造化出力 |
| Ctrl+C対応 | ストリーミング中の割り込みでクリーンにキャンセル |

### 設定ファイル

```
# ~/.claude-cli/config.yaml
system_prompt: ""    # デフォルトシステムプロンプト
max_tokens: 1024     # 最大出力トークン数
stream: true         # ストリーミングデフォルト
timeout: 30s         # API タイムアウト
```

---

## Claude Codeによる18 Issue自律実装

最も興味深い点は、このツールの大半を **Claude Code が自律的に実装した** ことです。GitHubにIssueを立ててClaude Codeに渡すと、コードの記述・テストの作成・コミット・プッシュまでを自動で行います。

### プロジェクト構成（実装前に決めたこと）

```
cmd/claude-cli/main.go          # エントリーポイント
internal/
  cli/
    root.go                     # NewRootCmd() ファクトリ
    run.go                      # メインロジック + フラグ定義
    config.go                   # config サブコマンド
    completion.go               # completion サブコマンド
    integration_test.go         # CLI統合テスト
  claude/
    client.go                   # HTTPクライアント
    stream.go                   # SSEストリーミング
    models.go                   # 型定義
  config/
    config.go                   # 設定管理
    presets.go                  # プリセット定義
  output/
    formatter.go                # 出力フォーマッタ
```

実装の詳細はリポジトリで確認できます: <https://github.com/kai-kou/go-claude-code>

### Phase 1: 基盤実装（Issue #1〜#8）

最初のフェーズでは、CLIの骨格・APIクライアント・基本的な入出力を実装しました。

**実装された主なIssue**:

* `#1` プロジェクト初期設定（go mod、Cobra/Viper導入）
* `#2` Claude APIクライアント（HTTPリクエスト、型定義）
* `#3` SSEストリーミング受信
* `#4` プリセットシステム（translate-ja/summarize-ja）
* `#5` 設定ファイル管理（Viper）
* `#6` JSONモード出力
* `#7` CI設定（GitHub Actions）
* `#8` 統合テスト

```
// Phase 1で確立したエラーハンドリング方針
type exitError struct {
    code int
    err  error
}

// 終了コード体系:
// 0: 成功
// 1: 一般エラー（入力なし等）
// 2: 設定エラー（APIキー未設定、不正プリセット等）
// 3: API エラー（認証失敗、レート制限等）
```

### Phase 2: 機能強化（Issue #9〜#14）

第2フェーズでは、実用性を高める機能を追加しました。

**主な追加機能**:

* `#9` ファイル入力（`-f` フラグ）
* `#10` `--max-tokens` フラグ
* `#11` `--timeout` フラグ
* `#12` `--verbose` フラグ（デバッグログ）
* `#13` Ctrl+C でのストリーミングキャンセル（context対応）
* `#14` シェル補完コマンド

Ctrl+C 対応は `context.WithCancel` と `os/signal` の組み合わせで実装されています。

```
func doStreamTo(out, errOut io.Writer, client *claude.Client, req claude.Request) error {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, os.Interrupt)
    defer signal.Stop(sigCh)

    go func() {
        select {
        case <-sigCh:
            cancel() // Ctrl+C でコンテキストをキャンセル
        case <-ctx.Done():
        }
    }()

    err := client.SendStreamCtx(ctx, req, func(text string) error {
        _, _ = fmt.Fprint(out, text)
        return nil
    })
    if errors.Is(err, context.Canceled) {
        return nil // Ctrl+C はクリーンな終了
    }
    // ...
}
```

### Phase 3: リリース準備（Issue #15〜#18）

最終フェーズでは、配布・公開に必要な要素を整えました。

* `#15` GoReleaser設定（マルチプラットフォームビルド）
* `#16` マルチプラットフォームビルド検証
* `#17` README.md / LICENSE 作成
* `#18` v1.0.0 タグ・リリース

---

## 技術的なポイント

### SSEストリーミングの実装

Claude APIはServer-Sent Events（SSE）でレスポンスをストリーミングします。各イベントをパースして逐次表示することで、長い応答でも最初のトークンが届き次第表示が始まります。

```
func (c *Client) doStream(ctx context.Context, body []byte, handler StreamHandler) error {
    httpReq, err := http.NewRequestWithContext(ctx, "POST", APIBaseURL, bytes.NewReader(body))
    // ...
    scanner := bufio.NewScanner(resp.Body)
    for scanner.Scan() {
        line := scanner.Text()
        if !strings.HasPrefix(line, "data: ") {
            continue
        }
        data := strings.TrimPrefix(line, "data: ")
        if data == "[DONE]" {
            break
        }
        var event StreamEvent
        if err := json.Unmarshal([]byte(data), &event); err != nil {
            continue
        }
        if event.Type == "content_block_delta" && event.Delta.Type == "text_delta" {
            if err := handler(event.Delta.Text); err != nil {
                return err
            }
        }
    }
    return scanner.Err()
}
```

### 指数バックオフリトライ

レート制限（429）やサーバー過負荷（529）は一時的なエラーのため、自動リトライが有効です。テスト時は遅延をゼロにできるよう `var` で定義しています。

```
var retryDelays = []time.Duration{
    1 * time.Second,
    3 * time.Second,
    9 * time.Second,
}
```

### GoReleaser でのマルチプラットフォームリリース

```
builds:
  - id: claude-cli
    main: ./cmd/claude-cli
    binary: claude-cli
    env:
      - CGO_ENABLED=0
    goos: [linux, darwin, windows]
    goarch: [amd64, arm64]
    ldflags:
      - -s -w
      - -X main.version={{.Version}}
      - -X main.commit={{.Commit}}
      - -X main.buildDate={{.Date}}
```

---

## Claude Codeを使った開発で気づいたこと

### うまくいったこと

* **Issue単位の実装**: 1 Issue = 1コミットの粒度が明確だと、Claude Codeが迷わず進める
* **テスト駆動**: `httptest.NewServer` を使ったモックAPIサーバーをClaude Codeが自律的に書いてくれた
* **CLAUDE.md の活用**: プロジェクトルール・コーディング規約を `CLAUDE.md` に書いておくと、セッションをまたいでも一貫した実装になる

### 注意が必要だった点

* **グローバル状態**: Cobraコマンドをグローバル変数で使い回すとテストが干渉する。`NewRootCmd()` ファクトリパターンで毎回新規生成するルールを明示した
* **セッション圧縮**: コンテキストが長くなると圧縮が発生し、口頭指示が失われる。重要なルールは `CLAUDE.md` に書いておく必要がある

---

## まとめ

Go + Cobra/Viper で作成した `claude-cli` は、シェルからClaude AIを素早く呼び出せるシングルバイナリCLIツールです。

今回の開発で確認できたポイント：

* Claude Codeは **明確なIssue・明確なルール** があれば、フェーズを分けて自律的に実装を進められる
* **SSEストリーミング**・**Ctrl+C対応**・**指数バックオフリトライ** はCLIツールとして本番利用に必要な要素
* **GoReleaser** + GitHub Actions で、タグひとつでマルチプラットフォームリリースが完結する
* テストカバレッジ80%以上を維持しながら進めることで、リグレッションを防げた

> **今すぐ試せます**
>
> ```
> go install github.com/kai-kou/go-claude-code/cmd/claude-cli@latest
> export ANTHROPIC_API_KEY="sk-ant-..."
> echo "Hello, world!" | claude-cli --preset translate-ja
> ```
>
> GitHub: <https://github.com/kai-kou/go-claude-code>  
> ⭐ Starをいただけると励みになります！

---

## 参考リンク
