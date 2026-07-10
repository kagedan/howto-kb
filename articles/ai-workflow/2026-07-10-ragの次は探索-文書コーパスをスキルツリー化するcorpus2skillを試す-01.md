---
id: "2026-07-10-ragの次は探索-文書コーパスをスキルツリー化するcorpus2skillを試す-01"
title: "RAGの次は「探索」？ 文書コーパスをスキルツリー化するCorpus2Skillを試す"
url: "https://qiita.com/Xim2jp/items/e16bf414e44371be4a10"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "Python", "qiita"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

# RAGの次は「探索」？ Corpus2Skillを試す

論文「Don't Retrieve, Navigate」（[arXiv:2604.14572](https://arxiv.org/abs/2604.14572)）とその実装 [Corpus2Skill](https://github.com/dukesun99/Corpus2Skill) が面白かったので紹介します。日本語解説サイトも公開しました。

**解説サイト**: https://corpus2skill.businesshub.trueone.co.jp/

## コンセプト: 検索するな、ナビゲートせよ

従来のRAGでは、LLMは検索結果の**受動的な消費者**です。コーパス全体がどう構成されているか、何をまだ見ていないかを知る術がありません。

Corpus2Skillは発想を変えます。

1. **オフライン**で文書コーパスを階層スキルツリーにコンパイルしておく
2. **サーブ時**はLLMエージェントが鳥瞰ビューから要約階層をドリルダウンし、外れたブランチはバックトラックして文書に到達する

サーブ時のランタイム構成要素は**LLMのみ**。ベクトルDBも検索APIも不要です。

## コンパイルパイプライン（6段階）

```
Load → Embed → Cluster → Summarize → Label → Build
```

- **Load**: .txt / .md / .json / .jsonl を読み込み
- **Embed**: sentence-transformers（既定は Qwen3-Embedding-0.6B）
- **Cluster**: 再帰的K-means＋凝集マージで階層ツリーを構築
- **Summarize / Label**: 各クラスタノードの説明文と短いトピックラベルをLLMが生成
- **Build**: `SKILL.md` / `INDEX.md` / `documents.json` として実体化。出力は `.claude/skills/` 規約でAnthropic Skills API互換

## 使ってみる

```bash
pip install -e .
cp .env.example .env   # Anthropic APIキーを設定

python -m corpus2skill \
    --input ./corpus_dir \
    --output ./compiled_output \
    --p 10 \          # 分岐率（ノードあたり子数）
    --max-top 8 \     # トップレベルスキル数の上限
    --model claude-sonnet-4-6
```

サーブ側はPython APIから:

```python
from corpus2skill.serve import answer_query
from corpus2skill.config import ServeConfig

config = ServeConfig(skills_dir=Path("./compiled/.claude/skills"))
result = answer_query("How do I add a custom domain?",
                      skills_dir=skills_dir, output_dir=output_dir, config=config)
```

エージェントはトップレベルのスキル説明→ブランチ→リーフの文書IDと辿り、`get_document` ツールで全文を取得して回答します。

## ベンチマーク結果の要点

- エンタープライズ顧客サポートQAで、single-shot dense / ハイブリッド / 階層検索 / エージェント型RAGの**全ベースラインを回答品質とグラウンディングで上回る**
- コストは中程度の増加。ただし**プロンプトキャッシュで1クエリ$0.172→$0.089（48%削減）**（WixQA、入力の約70%がキャッシュヒット）

## 重要な注意: 万能ではない

論文の10サブセット汎化実験が誠実で、

- ✅ **単一ドメイン＋復元可能なトピック分類体系**を持つコーパス → ナビゲーションが一貫して有効
- ❌ オープンドメインの事実断片プール、均質な表形式データ → **フラット検索の方が強い**

「社内マニュアル・製品ドキュメント向き、雑多なFAQ寄せ集めには不向き」と覚えておくとよさそうです。

## まとめ

実装はWIPで粗削りですが、「検索インフラなしのRAG代替」という方向性は追う価値があります。クラスタリングの内部やコスト構造の深掘りはZennに書きました。

- 解説サイト: https://corpus2skill.businesshub.trueone.co.jp/
- パイプライン詳細: https://corpus2skill.businesshub.trueone.co.jp/page-02-compile-pipeline.html
