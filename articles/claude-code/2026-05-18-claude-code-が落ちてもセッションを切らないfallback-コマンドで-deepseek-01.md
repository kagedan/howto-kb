---
id: "2026-05-18-claude-code-が落ちてもセッションを切らないfallback-コマンドで-deepseek-01"
title: "Claude Code が落ちてもセッションを切らない：/fallback コマンドで DeepSeek / Gemini / ChatGPT にシームレス切替"
url: "https://qiita.com/ryun818/items/acd7dd7eba5c4a80b456"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-05-18"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- Claude Code を使い倒していると、**利用上限**や**API障害**で作業が止まる
- `claude-code-router` (ccr) は **OAuth 認証に非対応** → Pro Max / Pro / Teams ユーザーは従量課金になってしまう
- 本記事では **UniClaudeProxy ベースのローカルプロキシ** で、**既存の認証をそのまま使いつつ**、障害時に DeepSeek / Gemini / ChatGPT にセッション維持したまま切替
- セッション内で **`/fallback deepseek`** と打つだけで即切替、**`/fallback claude`** で復帰
- macOS通知による自動検知・ワンクリック切替にも対応
- **通常時の追加コスト $0**、フォールバック時のみ従量課金
- **Pro Max / Pro / Teams / API キー** — どの認証方式でも動作

GitHub: https://github.com/ryun818/claude-code-fallback

---

## 目次

1. [背景：なぜフォールバックが必要か](#背景なぜフォールバックが必要か)
2. [なぜ ccr ではダメだったか](#なぜ-ccr-ではダメだったか)
3. [アーキテクチャ：プロキシ方式](#アーキテクチャプロキシ方式)
4. [モデル比較とコスト試算](#モデル比較とコスト試算)
5. [セットアップ手順](#セットアップ手順)
6. [使い方](#使い方)
7. [カスタマイズ](#カスタマイズ)
8. [トラブルシューティング](#トラブルシューティング)
9. [まとめ](#まとめ)

---

## 背景：なぜフォールバックが必要か

Claude Code をメイン開発環境にしていると、避けて通れない問題が2つあります。

### 問題1: 利用上限

Pro ($20/月) でも Max ($100/月) でも使用量制限があります。ヘビーユーザーは「Usage limit reached」を週に何度も踏みます。制限中は応答速度が極端に低下するか、完全にブロックされます。

### 問題2: API 障害

Anthropic のサービスは比較的安定していますが、数ヶ月に一度は数時間規模の障害があります。日本時間の朝〜昼に集中する傾向があり、ちょうど生産性時間帯を直撃します。

### 従来の対処法と限界

| 対処法 | 問題 |
|---|---|
| じっと待つ | フローが切れる |
| claude.ai に切り替え | CLI のエージェント動作なし |
| 別のAIに乗り換え | Claude Code の体験を失う |
| ccr でフォールバック | **Pro Max の OAuth に非対応** |

---

## なぜ ccr ではダメだったか

[claude-code-router (ccr)](https://github.com/musistudio/claude-code-router) は Claude Code のリクエストを他プロバイダにルーティングする優秀なツールです。しかし **Pro Max / Pro / Teams ユーザーには致命的な問題** があります。

### ccr の認証フロー

```
Claude Code → ccr (localhost:3456) → Provider の API キーで認証 → Anthropic API
```

ccr は Provider 設定の `api_key` を使ってバックエンドに認証します。つまり：

- **ccr 経由 = API キー従量課金**（Opus で $15/100万出力トークン）
- Pro Max / Pro / Teams の OAuth トークンは ccr を通らない
- 通常作業も ccr 経由なので、**サブスクリプション料金が無駄になる**

### ccr の model 分割問題

ccr は内部で `model` フィールドを `provider,model` 形式（カンマ区切り）で分割します。Claude Code が送る素の `claude-opus-4-6` にはカンマがないため、`Router.default` が未設定だとエラーになります。

```
❌ "model": "claude-opus-4-6" → provider="claude-opus-4-6", model="" → "Missing model"
✅ "model": "deepseek,deepseek-chat" → provider="deepseek", model="deepseek-chat" → OK
```

### 結論

ccr は **API キー認証の従量課金ユーザー向け**。サブスクリプション（Pro Max / Pro / Teams）ユーザーには OAuth パススルーが必要です。

---

## アーキテクチャ：プロキシ方式

本記事のアプローチは、**UniClaudeProxy をベースにした OAuth パススルー対応のローカルプロキシ** です。

```
┌────────────────────────────────────────────────┐
│  Claude Code                                    │
│  ANTHROPIC_BASE_URL=http://localhost:3456        │
│  Pro Max OAuth ヘッダー付きでリクエスト送信       │
└────────────────────┬───────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│  ローカルプロキシ (localhost:3456)               │
│  UniClaudeProxy + OAuth パッチ                  │
│                                                │
│  毎リクエスト: sticky-config.json を読む         │
│                                                │
│  mode=claude:                                  │
│    → api.anthropic.com にそのまま転送            │
│    → OAuth ヘッダーもそのまま（Pro Max）          │
│                                                │
│  mode=deepseek/gemini/chatgpt:                 │
│    → Anthropic形式 → OpenAI形式に変換           │
│    → 各プロバイダの APIキーを付与                 │
│    → 各プロバイダに送信                          │
│    → レスポンスを Anthropic形式に逆変換          │
└───────┬────────────────────────┬───────────────┘
        │                        │
        ▼                        ▼
  api.anthropic.com        api.deepseek.com
  (Pro Max OAuth, $0)      (従量課金)
```

### ポイント

- **通常時**: OAuth ヘッダーがそのまま Anthropic に転送される → **Pro Max のまま、追加コスト $0**
- **フォールバック時**: UniClaudeProxy のフォーマット変換（ツール呼び出し、ストリーミング対応済み）で DeepSeek 等に転送
- **セッション維持**: Claude Code は常に `localhost:3456` に接続。裏のバックエンドが変わってもセッションは切れない
- **会話履歴**: クライアント側に保持されるため、バックエンド切替後も引き継がれる

### ccr との比較

| | ccr | 本記事のプロキシ |
|---|---|---|
| Pro Max OAuth | :x: 使えない | :white_check_mark: パススルー |
| 通常時コスト | $50-100+/月 (API従量) | **$0** (Pro Max) |
| セッション維持 | :white_check_mark: | :white_check_mark: |
| フォーマット変換 | :white_check_mark: (成熟) | :white_check_mark: (UniClaudeProxy) |
| 保守 | npm update | git pull + patch |

---

## モデル比較とコスト試算

### フォールバック先の比較（2026年5月時点）

デフォルトでは Opus 4.6 と同等クラスのフラッグシップモデルを設定しています。

| モデル | Input ($/M) | Output ($/M) | Tool Calling | Opus 4.6 対比 |
|---|---|---|---|---|
| **DeepSeek V3** | $0.14 | $0.28 | 良好 | コスパ重視（品質8-9割、1/80の価格） |
| **Gemini 2.5 Pro** | $1.25 | $10.00 | 良好 | Google フラッグシップ |
| **o3** | $2.00 | $8.00 | 完璧 | OpenAI 最上位推論モデル |

config.json の `fallback_models` でモデルを変更できます。コストを抑えたい場合：

```json
{
  "fallback_models": {
    "gemini": "gemini/gemini-2.5-flash",
    "chatgpt": "openai/gpt-4.1"
  }
}
```

### フォールバック時のコスト試算

「1セッション = 入力50K + 出力20K token」で試算：

| 頻度 | DeepSeek V3 | Gemini 2.5 Pro | o3 |
|---|---|---|---|
| 月8セッション | **約15円** | 約600円 | 約500円 |
| 月30セッション | **約110円** | 約4,500円 | 約3,800円 |
| 月100セッション | **約760円** | 約30,000円 | 約25,000円 |

**推奨**: 普段は DeepSeek V3（最安）、品質が必要な場面で `/fallback gemini` や `/fallback chatgpt` に手動切替。

---

## セットアップ手順

### 前提条件

- macOS (Apple Silicon)
- Claude Code インストール済み、Pro Max / Pro でログイン済み
- Python 3.10+
- Homebrew

### ワンコマンドセットアップ

```bash
git clone https://github.com/ryun/claude-code-fallback.git
cd claude-code-fallback
./setup.sh
```

setup.sh が以下を自動実行します：

1. 依存チェック (python3, jq, terminal-notifier)
2. [UniClaudeProxy](https://github.com/vibheksoni/UniClaudeProxy) を `~/.claude-code-proxy` に clone
3. OAuth パススルーパッチを適用
4. Python venv + pip install
5. config テンプレートを配置
6. launchd サービス登録（自動起動 + 自動復旧）
7. `~/.zshrc` に `ANTHROPIC_BASE_URL` を追加

### API キーの設定

セットアップ後、`~/.claude-code-proxy/config.json` を編集してフォールバック先の API キーを設定します：

```bash
vi ~/.claude-code-proxy/config.json
```

最低限、`providers.deepseek.api_key` に DeepSeek の API キーを設定すれば動きます。

:::note info
Anthropic の API キーは不要です。Pro Max の OAuth がプロキシ経由でそのまま転送されます。
:::

### 動作確認

```bash
source ~/.zshrc

# プロキシのヘルスチェック
curl http://127.0.0.1:3456/health
# {"status":"ok"}

# Pro Max 経由で動作確認
claude -p "say hi" --model haiku
# 応答があればOK
```

---

## 使い方

### 普段（何も変わらない）

```bash
claude
```

これだけ。追加コスト $0。プロキシは透過的に動作します。

### `/fallback` コマンドで切替（推奨）

Claude Code のセッション内からスラッシュコマンドで即切替できます：

```
/fallback deepseek   ← DeepSeek に切替
/fallback gemini     ← Gemini に切替
/fallback chatgpt    ← ChatGPT に切替
/fallback claude     ← Claude に戻す
/fallback            ← 現在のモードを確認
```

**セッションは一切切れません。** 次のリクエストから選んだプロバイダが使われます。会話履歴・メモリ・タスクはすべて引き継がれます。

:::note info
どのモデルに切り替えても、Claude Code は「私は Claude Code です」と名乗ります。これはシステムプロンプトに従った正常な動作です。現在どのプロバイダで動いているかは `/fallback`（引数なし）で確認できます。
:::

### 制限/障害が発生した時（自動通知）

手動で `/fallback` を打つ以外に、自動検知もあります：

1. Claude が 429/5xx を返す
2. **macOS 通知**が届く：「Claude 制限検知」
3. ボタンを選択：`[deepseek]` `[gemini]` `[chatgpt]` `[様子見]`
4. 選んだプロバイダで**同じセッションが継続**

### 復旧した時

1. 1時間ごとに自動で Claude の復旧をチェック
2. 復旧したら**macOS 通知**：「Claude 復旧」
3. 「Switch back」ボタンで復帰、またはセッション内で `/fallback claude`

---

## カスタマイズ

### プロバイダの追加

`~/.claude-code-proxy/config.json` に追加するだけ。hot-reload 対応で再起動不要。

#### 例: Qwen (通義千問) を追加する

1. [DashScope](https://dashscope.console.aliyun.com/) でAPIキーを取得
2. config.json に追加:

```json
{
  "fallback_models": {
    "deepseek": "deepseek/deepseek-chat",
    "gemini": "gemini/gemini-2.5-pro",
    "chatgpt": "openai/o3",
    "qwen": "qwen/qwen3-max"
  },
  "providers": {
    "qwen": {
      "provider_type": "openai",
      "api_key": "sk-your-dashscope-api-key",
      "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
      "headers": {},
      "models": {
        "qwen3-max": {
          "name": "Qwen3 Max",
          "max_output_tokens": 65536
        },
        "qwen3.5-plus": {
          "name": "Qwen3.5 Plus",
          "max_output_tokens": 65536
        }
      }
    }
  }
}
```

3. すぐに使える:

```
/fallback qwen
```

#### 汎用的な追加パターン

OpenAI 互換 API を提供しているプロバイダなら、3箇所の変更で追加できます:

1. `fallback_models` にエントリ追加
2. `providers` にプロバイダ設定追加（`provider_type: "openai"`）
3. `/fallback <name>` で切替

```json
{
  "fallback_models": {
    "my-provider": "myprov/model-name"
  },
  "providers": {
    "myprov": {
      "provider_type": "openai",
      "api_key": "YOUR_KEY",
      "base_url": "https://api.example.com/v1",
      "headers": {},
      "models": {
        "model-name": { "name": "Model Name" }
      }
    }
  }
}
```

Gemini は OpenAI 互換エンドポイント (`https://generativelanguage.googleapis.com/v1beta/openai`) を使用し、`provider_type: "openai"` で設定します。

### 復旧チェック間隔の変更

```bash
# 30分に変更（1800秒）
vi ~/Library/LaunchAgents/com.$(whoami).claude-proxy-recovery.plist
# StartInterval を 1800 に変更

launchctl unload ~/Library/LaunchAgents/com.$(whoami).claude-proxy-recovery.plist
launchctl load -w ~/Library/LaunchAgents/com.$(whoami).claude-proxy-recovery.plist
```

### モデル切替時の品質維持

バックエンドが切り替わっても会話履歴は引き継がれますが、モデルの「思考スタイル」は変わります。

CLAUDE.md に以下を追加しておくと、どのモデルが入っても作法が揃います：

```markdown
## モデル中立な作業ルール

- 重要な決定をしたら `docs/checkpoints/` に記録
- ファイル編集前に必ず現状を確認（前任の記憶に依存しない）
- コードコメントは英語
- 推測で動かず、不明点は確認
```

---

## トラブルシューティング

### プロキシが起動しない

```bash
cat /tmp/claude-proxy.err
# Python のエラーメッセージを確認
```

### 通知が出ない

1. `which terminal-notifier` でパス確認
2. システム設定 → 通知 → terminal-notifier → 「通知を許可」をON
3. 手動テスト：`terminal-notifier -title "test" -message "hello"`

### Claude Code が 401 エラー

`ANTHROPIC_BASE_URL` が設定されているか確認：

```bash
echo $ANTHROPIC_BASE_URL
# http://127.0.0.1:3456 であるべき
```

### パッチが適用できない

UniClaudeProxy が更新された場合：

```bash
cd ~/.claude-code-proxy
git stash
git pull
git stash pop  # コンフリクトがあれば手動解決
```

### DeepSeek で "Insufficient Balance"

[platform.deepseek.com](https://platform.deepseek.com) でチャージ。$5 あれば数ヶ月持ちます。

---

## まとめ

| 項目 | Before | After |
|---|---|---|
| 制限到達時 | 作業停止 | ボタン1つで DeepSeek/Gemini に切替 |
| 障害時 | 待つしかない | 自動検知 → 通知 → ワンクリック切替 |
| セッション | 切替で失われる | **維持される** |
| 通常時コスト | - | **$0**（Pro Max そのまま） |
| フォールバック時コスト | - | 月¥100〜3,000（DeepSeek利用量次第） |
| 復旧確認 | 手動チェック | 1時間ごと自動 → 通知 |

### 構築時間

- setup.sh で **5分**（API キー設定込みで10分）

### 次のステップ

- 時間帯別の自動ルーティング
- コスト上限アラート

### 関連リンク

- [claude-code-fallback (GitHub)](https://github.com/ryun818/claude-code-fallback)
- [UniClaudeProxy](https://github.com/vibheksoni/UniClaudeProxy)
- [DeepSeek Platform](https://platform.deepseek.com)
- [Anthropic Status Page](https://status.anthropic.com)

---

ここまで読んでくださってありがとうございます。質問・改善案などコメントいただけると嬉しいです。

#ClaudeCode #DeepSeek #Gemini #macOS #LLM
