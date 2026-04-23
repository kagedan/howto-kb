---
id: "2026-04-01-自然言語でターミナルを自動化するai-clivexis-cli-2を公開しました-01"
title: "自然言語でターミナルを自動化するAI CLI「VEXIS-CLI 2」を公開しました"
url: "https://zenn.dev/ainohogosya/articles/4ff116785396bc"
source: "zenn"
category: "ai-workflow"
tags: ["OpenAI", "Gemini", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

![](https://static.zenn.studio/user-upload/634fce1212b1-20260401.png)

VEXIS-CLI 2 を正式にリリースしました。

このツールは、自然言語で指示を出すだけで、AIが最適なCLIコマンドを生成・安全検証・実行・結果確認まで一貫して行うAIエージェント型CLIです。前バージョンから大幅に進化し、対応AIプロバイダーを大幅に拡大しました。

#### 主なアップデート

* **16種類以上のAIプロバイダー対応**  
  Ollama（ローカル）、Groq、Google Gemini、OpenAI、Anthropic、xAI、Mistral、Azure OpenAI、AWS Bedrockなど、好みのプロバイダーを簡単に切り替え可能。
* **5フェーズ実行エンジン**  
  自然言語理解 → コマンド計画 → 安全検証 → 実行・自動回復 → 結果検証  
  単なるコマンド生成ではなく、エンドツーエンドで責任を持って処理します。
* **強化された安全機構**  
  safety\_mode、dry-run、コマンド検証、ブラックリスト/ホワイトリスト、システム重要パスの保護を標準搭載。  
  エラー発生時は詳細なガイダンスを表示します。
* **Yellow Selection Menu**  
  複数の候補が出た場合に直感的に選択できる、特徴的なUIを採用。
* **開発者向けの品質**  
  Black/isort/flake8/mypy準拠、pytestによるテスト、充実したドキュメント群を完備。

#### クイックスタート

```
git clone https://github.com/vexis-project/VEXIS-CLI-2.git
cd VEXIS-CLI-2

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

cp config.yaml.example config.yaml
```

Ollamaで試すのがおすすめです：

```
ollama serve
ollama pull gemma3:4b
```

その後、`config.yaml` で `preferred_provider: "ollama"` を設定して実行してください。

#### 使用例

```
python run.py "最新のログファイルをgzip圧縮して backup フォルダに移動して"
python run.py "プロジェクト内のPythonファイルから未使用importを安全に削除して"
```

詳細なドキュメントはリポジトリ内の  
ARCHITECTURE.md / CONFIGURATION.md / OLLAMA\_INTEGRATION.md をご覧ください。

**GitHub**： <https://github.com/vexis-project/VEXIS-CLI-2>

ぜひ試してみて、フィードバックやPull Requestをお待ちしています。
