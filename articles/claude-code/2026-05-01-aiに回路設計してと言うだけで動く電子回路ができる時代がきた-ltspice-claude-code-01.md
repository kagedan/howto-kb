---
id: "2026-05-01-aiに回路設計してと言うだけで動く電子回路ができる時代がきた-ltspice-claude-code-01"
title: "AIに「回路設計して」と言うだけで動く電子回路ができる時代がきた — LTSpice × Claude Code を MCP で繋ぐ"
url: "https://qiita.com/trailfusion_ai/items/c8604bc73aac4b12d5c4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "LLM", "qiita"]
date_published: "2026-05-01"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

![LTSpice × Claude Code MCP連携](https://raw.githubusercontent.com/hiroakiyasa/meeting-minutes-2026-04-21/main/incoming/20260501-005402-7304F2EE-9820-452A-83FE-6FC7C4C91A60.jpg)

## TL;DR

AI に「5V で赤色 LED を安全に光らせる回路を作って、電流値も教えて」と打つだけで、本物の LTSpice が回路図を生成し、シミュレーションを実行し、`I = 10.8 mA` という数値で返してくる時代になった。

仕組みは **MCP (Model Context Protocol)**。Anthropic が作った「AI に外部ツールを使わせる標準規格」。Claude Code だけでなく Codex CLI / GitHub Copilot Chat / Cursor / Windsurf など、対応する任意のクライアントから同じ MCP サーバーが使い回せる。

## 何が嬉しいのか

### これまで
- LTSpice の UI 操作を覚える
- 部品ピンの座標を 16 グリッドで合わせる
- ワイヤーをドラッグで繋ぐ
- パラメータを試行錯誤
- 「なぜか動かない」で 2 時間溶ける

### これから
- **日本語で要件を伝えるだけ**
- AI が `.asc` 回路図とネットリスト両方を生成
- 物理的にちゃんと動くシミュレーション結果
- **波形データも JSON で取れる** → グラフ化や次の設計判断まで AI が担当

## アーキテクチャ

```
あなた  ─[日本語]→  Claude / Codex / Copilot
                       │
                       │ MCP プロトコル (stdio)
                       ▼
                LTSpice MCP サーバー (TypeScript)
                       │
                       ▼
                 LTSpice 本体 (バッチ実行)
                       │
                       ▼
                .asc / .net / .log / .raw
                       │
                       ▼
                  AI が結果を解釈 → あなたに返答
```

## セットアップ (3ステップ・所要15分)

### Step 1: LTSpice をインストール

```bash
brew install --cask ltspice
```

### Step 2: MCP サーバーをビルド

```bash
git clone <repo>
cd ltspice-mcp
pnpm install
pnpm build
```

### Step 3: AI クライアントに登録

**Claude Code** (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "ltspice": {
      "command": "node",
      "args": ["/path/to/ltspice-mcp/dist/index.js"],
      "env": {
        "LTSPICE_EXECUTABLE": "/Applications/LTspice.app/Contents/MacOS/LTspice"
      }
    }
  }
}
```

**Codex CLI** (`~/.codex/config.toml`):

```toml
[mcp_servers.ltspice]
command = "node"
args = ["/path/to/ltspice-mcp/dist/index.js"]

[mcp_servers.ltspice.env]
LTSPICE_EXECUTABLE = "/Applications/LTspice.app/Contents/MacOS/LTspice"
```

**GitHub Copilot Chat** (`.vscode/mcp.json`):

```json
{
  "servers": {
    "ltspice": {
      "type": "stdio",
      "command": "node",
      "args": ["/path/to/ltspice-mcp/dist/index.js"]
    }
  }
}
```

## 提供ツール

| ツール | 説明 |
|--------|------|
| `ltspice_check_install` | LTSpice のインストール確認 |
| `ltspice_list_templates` | 回路テンプレート一覧 |
| `ltspice_get_template` | テンプレート詳細取得 |
| `ltspice_create_circuit` | テンプレートから `.asc` / `.net` を生成 |
| `ltspice_validate_circuit` | `.asc` の構文・接続性チェック |
| `ltspice_run_simulation` | LTSpice バッチシミュレーション実行 |
| `ltspice_parse_log` | `.log` ファイルの結果解析 |
| `ltspice_parse_raw` | `.raw` バイナリ波形データ取得 |

## 実例: LED 電流制限回路

**入力**:

> 5V 電源で赤色 LED を安全に光らせる回路を作って、電流値も教えて。Rlimit=330Ω で。

**AI の処理**:

1. `ltspice_create_circuit` で LED + 330Ω 回路を生成 → `.asc` / `.net` 出力
2. `ltspice_run_simulation` で LTSpice をバッチ実行 → `.log` 生成
3. `ltspice_parse_log` でログを解析 → 測定値抽出

**出力**:

```
I(D1) = 10.82 mA  ✅ 安全範囲
V(N001) = 1.43 V (LED 順方向電圧)
```

計算と一致:
- V_R = Vcc - Vf = 5 - 1.43 = 3.57 V
- I = 3.57 / 330 = 10.82 mA

## RC ローパスフィルタの例

**入力**:

> R=1k, C=1u の RC ローパスフィルタを AC 解析して。

**結果**:

- カットオフ周波数: fc = 1 / (2π × 1k × 1u) ≈ **159 Hz**
- シミュレーションでも -3dB ポイントが約 160 Hz で一致 ✅

## なぜ MCP が革命的か

従来の LLM は「公式を返す」だけだった。
MCP を使うと **AI が実際にツールを動かして検証した数値** を返してくる。

- ソフトウェアの世界 (AI) と ハードウェアの世界 (回路) が **プロンプト一行で繋がる**
- stdio トランスポートなのでクライアント非依存。Claude Code / Codex / Copilot / Cursor / Windsurf すべてで同じサーバーが動く
- 既存の LTSpice 資産 (`.asc` / `.net` / `.raw`) をそのまま活用できる

## こんな人にぶっ刺さる

- 📚 電子工作・Arduino・Raspberry Pi が好きな人
- 🔬 物理・電気を勉強中の学生
- 🛠️ 「作りたいけど計算が面倒」なメイカー
- 💡 IoT デバイスのプロトタイピング屋
- 🎓 教育者 (生徒に手を動かしながら教えられる)

## まとめ

設計 → シミュレーション → 結果解釈 → 改善
このループを **AI が全部やる**。あなたは「こういうの欲しい」と言うだけ。

電子工作の民主化、ガチで来てる。

## 出典

- [Model Context Protocol 公式](https://modelcontextprotocol.io/)
- [LTSpice 公式 (Analog Devices)](https://www.analog.com/jp/resources/design-tools-and-calculators/ltspice-simulator.html)
- [Anthropic MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
