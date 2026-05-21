---
id: "2026-05-20-無料gpuでai論文を自動復元するfeynmanとcolab-mcpで研究パイプラインを構築した-01"
title: "無料GPUでAI論文を自動復元する——FeynmanとColab-MCPで研究パイプラインを構築した"
url: "https://zenn.dev/bayar/articles/357285c1e785e5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "Python", "zenn"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

> 論文を読むところから実験を回すところまで、クラウド費用ゼロで完結させる

---

こんにちは！バヤルです。  
ここ2ヶ月、ひとつの問いを追いかけていた。

**「無料ツールだけで、"AI科学者"に近い研究パイプラインは作れるか？」**

結論から言う。作れる。しかも想定以上に実用的だった。

使うツールは2つだけ——**Feynman**（AIリサーチエージェント）と**colab-mcp**（Google ColabのMCPサーバー）。これを組み合わせると、文献調査から実際のGPU実験まで、ほぼ自動で流れるパイプラインができあがる。

---

## 解決したい問題

ML研究には2つの現実的な壁がある。

ひとつは**計算資源**だ。ローカルマシンでは本格的なトレーニングは回せない。クラウドGPUは時間課金。A100クラスターは大学の研究室にある。

もうひとつは**情報の密度**だ。arXivは1日に何百本もの論文を公開する。手動でトリアージして復元まで検証するのは、それだけで専業になれる作業量だ。

このパイプラインは両方を同時に攻略する。

---

## 2つのツール

### Feynman（feynman.is）

ローカルで動くオープンソースのAIリサーチエージェント。CLIツールとして使う。

主要コマンド：

| コマンド | 用途 |
| --- | --- |
| `feynman "質問"` | 分野の現状を素早く把握 |
| `feynman lit "トピック"` | 合意点と論争点を含む深い文献調査 |
| `feynman deepresearch "トピック"` | マルチエージェントによる並列深掘り調査 |
| `feynman audit 2401.12345` | 論文の主張とコードの一致性を監査 |
| `feynman replicate "論文タイトル"` | 完全な復元計画を生成 |

特に重要なのは最後の2つだ。`audit`は論文の主張とコードの実態のギャップを浮き彫りにする——ハイパーパラメータの不一致、データ処理の省略、評価指標の定義のズレ。`replicate`は環境設定・依存関係リスト・ハイパーパラメータ・期待指標レンジ・実験手順を構造化して出力する。

### colab-mcp（github.com/googlecolab/colab-mcp）

2026年3月にGoogleが公開した。MCPプロトコルを通じて、AIエージェントがGoogle Colabのノートブックを直接操作できるようにするサーバーだ。

実際の動作はこうなる——Claude Codeに「このコードをColabで実行して」と伝えると、ブラウザで開いているColabタブの中にセルが自動生成され、コードが書かれ、実行され、出力が読み返される。

そのColabには無料のT4 GPUがある。

---

## パイプラインの全体像

![](https://static.zenn.studio/user-upload/864656a1a177-20260520.jpg)

```
feynman（研究インテリジェンス層）
    ↓  復元計画を生成
Claude Code（オーケストレーション層、colab-mcp設定済み）
    ↓  計画を解析して実行
colab-mcp → Google Colab（GPU計算層）
    ↓  結果を返す
feynman（差異分析、レポート生成）
```

Feynmanが論文を読む。Colabが実験を回す。Claude Codeがその神経系として両者をつなぐ。

---

## 事前準備

5つのツール、すべて無料：

| ツール | インストール | 役割 |
| --- | --- | --- |
| uv | `curl -LsSf https://astral.sh/uv/install.sh | sh` | Pythonパッケージ管理 |
| Feynman | `curl -fsSL https://feynman.is/install | bash` | リサーチエージェント |
| Claude Code | `npm install -g @anthropic-ai/claude-code` | オーケストレーション層 |
| colab-mcp | 下記セットアップ参照 | Colab MCPサーバー |
| Google Colab | ブラウザで開くだけ | GPU実行環境 |

---

## セットアップ手順

### Step 1：colab-mcpのインストール

```
git clone https://github.com/SebastianGilPinzon/colab-mcp.git
cd colab-mcp
```

まず接続だけ確認したい場合は公式版でも動く：

```
uvx git+https://github.com/googlecolab/colab-mcp
```

### Step 2：Claude Code MCP設定

プロジェクトルートに`.mcp.json`を作成する。

**公式版：**

```
{
  "mcpServers": {
    "colab-mcp": {
      "command": "uvx",
      "args": ["git+https://github.com/googlecolab/colab-mcp"],
      "timeout": 30000
    }
  }
}
```

**コミュニティfork（GPU制御あり）：**

```
{
  "mcpServers": {
    "colab-mcp": {
      "command": "uv",
      "args": ["run", "colab-mcp", "--client-oauth-config", "oauth.json"],
      "cwd": "/path/to/SebastianGilPinzon/colab-mcp",
      "timeout": 30000
    }
  }
}
```

### Step 3：Feynmanのインストール

```
curl -fsSL https://feynman.is/install | bash
feynman --version
```

### Step 4：Colabを開いてキープアライブセルを追加

colab.google.comを開き、新しいノートブックを作成してタブを開いたままにする。

最初のセルにこのコードを実行する。アイドルによる切断を防ぐために必須だ：

```
import threading, time

def keep_alive():
    while True:
        time.sleep(55)
        print(".", end="", flush=True)

t = threading.Thread(target=keep_alive, daemon=True)
t.start()
print("Keep-alive started")
```

セットアップはこれで完了だ。

---

## 5フェーズのワークフロー

### フェーズ1：文献偵察

復元する論文を決める前に、分野の全体像を把握する：

```
# 分野の現状を素早く把握
feynman "what do we know about space debris detection with deep learning"

# 合意点と論争点を含む深掘り調査
feynman lit "YOLOv8 for space debris"

# 未知の分野にはマルチエージェント並列調査
feynman deepresearch "vision transformer object detection 2024"
```

### フェーズ2：論文監査

復元する論文を決めたら、コードに触れる前に必ず監査する：

```
feynman audit 2401.12345
# 出力：論文の主張 vs 実際のコードの差分レポート
# 注目点：ハイパーパラメータ、データ前処理、評価指標の定義
```

### フェーズ3：復元計画の生成

```
feynman replicate "Enhanced YOLOv8 for space debris detection" > replicate_plan.md
```

生成される`replicate_plan.md`の内容：

* データセットの取得方法
* 依存関係リスト（pip installでそのまま使える）
* ハイパーパラメータ設定
* 期待される指標（accuracy / mAP / lossのレンジ）
* ステップごとの実験フロー

### フェーズ4：Colabで実行

計画をClaude Codeに渡す：

```
claude "
replicate_plan.mdを読んで、Colab内で以下の順番に実行してください：
1. 実験目標を説明するmarkdownセルを作成
2. すべての依存関係をインストール
3. データセットをダウンロード・準備
4. モデルを実装
5. トレーニングと推論を実行
6. 指標を出力し、論文と比較
各ステップの出力を記録してください。
"
```

ブラウザのColabタブにセルが次々と自動生成され、コードが一行ずつ実行されていくのを見ることになる。

**GPU選定の目安：**

| タスク | 設定 | 所要時間 |
| --- | --- | --- |
| 推論・クイック検証 | Colab T4（無料） | 数分 |
| 中規模トレーニング（10エポック未満） | Colab T4（無料） | 数時間 |
| 大規模トレーニング | Colab Pro A100 / RunPod | 要確認 |
| 短時間バーストジョブ | Modal（Feynman純正対応） | 秒単位で起動 |

GPU切り替え：`ランタイム → ランタイムのタイプを変更 → T4 GPU`。コミュニティforkを使えばClaude Codeに直接「T4に切り替えて」と伝えるだけでいい。

### フェーズ5：結果分析

実験が終わったらFeynmanに差異分析を依頼する：

```
feynman "
実験結果: [Colabの出力を貼り付け]
対象論文: [arXiv IDまたはタイトル]
分析してください：このギャップの原因は何か？
許容範囲内の分散か、それとも再現性の問題を示しているか？
"
```

---

## よくある失敗パターン

| 問題 | 原因 | 対処法 |
| --- | --- | --- |
| Colab が途中で切断される | アイドルタイムアウト | キープアライブセルを実行する |
| GPU切り替えができない | 公式colab-mcpがruntime制御を削除 | コミュニティforkを使うかブラウザで手動切り替え |
| MCPツールが表示されない | 公式版は`tools/list_changed`通知に依存 | コミュニティfork（全ツール事前登録済み）を使う |
| `feynman replicate`がタイムアウト | Dockerコンテナのリソース制限 | Feynmanの実行層をスキップし、計画だけClaude Codeに渡す |
| Colabの出力が切れる | セル出力の長さ制限 | ファイルに書き出す：`open('results.txt', 'w')` |

---

## 推奨ディレクトリ構成

```
research-pipeline/
├── .mcp.json              # colab-mcp設定
├── papers/                # 論文PDFとarXiv ID
├── plans/                 # feynman replicateの出力
│   └── replicate_plan.md
├── notebooks/             # Colabからエクスポートした.ipynb
├── results/               # 実験出力と指標
└── reports/               # 最終分析レポート
```

---

## このパイプラインの範囲

**カバーできること**：文献トリアージ、コード監査、実験の復元、ベースライン比較、結果のドキュメント化。計算ベースの研究（ML・データ分析・シミュレーション）であれば実行層はほぼカバーできる。

**代替できないこと**：研究方向の判断、想定外の結果の解釈、真に新規な仮説の生成。これらは依然として人間が担う。

これは**力の倍増器**であって、研究の自動機ではない。この区別は重要だ。

---

## まとめ

このパイプラインの本質的な価値を一文で言う。

**研究室へのアクセスがない独立した研究者が、研究室と同じスピードでアイデアを検証できるようになる。**

無料GPU・自動化された実験実行・AI支援の文献調査——この3つの組み合わせは2年前には不可能だった。今はツールが揃っている。

---

## 次のステップ

このパイプラインにはまだひとつ制約がある。FeynmanのデフォルトはDockerサンドボックスで実行されており、Colabとは独立した計算環境だ。2つは直接連携していない。

Feynmanをforkして、実行バックエンドをcolab-mcpに置き換える計画を進めている。目標はこのループを閉じることだ：

```
Feynmanが仮説を生成
    ↓
colab-mcpが実GPUで実験を実行
    ↓
Claude Codeが結果を読み、継続するか判断
    ↓
目標指標に達したらFeynman /draftがレポートを書く
```

今は流水線だ。forkが完成すれば自律的な研究ループになる。進捗は続報で報告する。

---

## 参考リンク

---

*スタック：Feynman + colab-mcp + Claude Code*
