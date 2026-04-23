---
id: "2026-03-30-anthropicがcms設定ミスでリークしたclaude-mythosとは何者か-前代未聞のサイバ-01"
title: "AnthropicがCMS設定ミスでリークした「Claude Mythos」とは何者か — 前代未聞のサイバーリスクを自ら持つAI"
url: "https://qiita.com/GeneLab_999/items/6e6aa2eebfa11b35c446"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-03-30"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

## この記事の対象読者

* [Claude](https://qiita.com/GeneLab_999/items/d1299630fc2c0325003b) / [LLM](https://qiita.com/GeneLab_999/items/7f1bd2de313bdd7ca423) の動向を追っているエンジニア
* AIセキュリティ・脆弱性に関心があるセキュリティエンジニア
* 「AIが自社コードを食い破る」という未来がどの程度リアルか知りたい人
* Anthropicの新モデル体系（Opus以上の「何か」）が気になっている人

## この記事で得られること

* Claude Mythosリーク事件の**時系列・全体像**
* 「Capybara」という新モデルティアの**正確な位置づけ**
* なぜAnthropicが自社製品を「前代未聞のサイバーリスク」と評したのか
* **既存Claudeですら500件のゼロデイ脆弱性を発見していた**という衝撃の実績
* セキュリティエンジニアとして取るべき実践的な対応策

## この記事で扱わないこと

* Claude Mythosの具体的なベンチマーク数値（公開されていないため）
* 「Mythosを今すぐ使う方法」（存在しないため）
* Anthropicのビジネス・財務状況の詳細（本筋でないため）

---

## 0. TL;DR（3行まとめ）

1. **2026年3月27日**: AnthropicのCMS設定ミスで未公開モデル「Claude Mythos（Capybara）」の内部文書が世界に公開された
2. **中身**: 現行最強のOpus 4.6を大幅に上回り、「サイバー能力において他のあらゆるAIモデルを現時点で大幅にリード」とAnthropicが自ら認める怪物モデル
3. **皮肉**: そのセキュリティ最強AIの存在を、自社の**設定ミス1個**で漏らした

---

## 1. 事件の全体像 — 「錠前師の工房が無施錠だった日」

AIの世界には「錠前師（locksmith）」と呼べる存在がいる。あらゆる鍵穴を理解し、マスターキーを作り出せる職人だ。

Anthropicはまさにその方向でモデルを進化させてきた。[CUDA](https://qiita.com/GeneLab_999/items/dfedb349f4971a1c7786)の設定ミスや依存地獄を解決するコードを書くだけでなく、今やコードベース全体を舐めて\*\*誰も気づいていなかった鍵穴（脆弱性）\*\*を探し出せるレベルに達している。

そしてついに、史上最強の錠前師「Claude Mythos」を作り上げた……のはいいんだが。

その錠前師の設計図を、工房（CMS）の鍵をかけ忘れたせいで世界中に配ってしまった。

これが2026年3月27日に起きた事件の本質だ。

### 1.1 時系列

### 1.2 リークされた内容の概要

以下は「漏洩した内部文書の草稿」に基づく情報であることに注意。Anthropicは公式発表の前に情報が流出したことを認めているが、詳細な仕様は現時点（2026/3/30）未公開。

| 項目 | 内容 |
| --- | --- |
| リーク元 | AnthropicのCMS（コンテンツ管理システム）の設定ミス |
| 漏洩規模 | 約**3,000件**の未公開アセット（ブログ草稿・PDF・画像） |
| 発見者 | Roy Paz（LayerX Security・シニアAIセキュリティ研究者）+ Alexandre Pauwels（Cambridge大学サイバーセキュリティ研究者） |
| 原因 | 「人的ミス（human error）」によるCMS設定の誤り |
| Anthropicの対応 | 通知後に即座に非公開化。公式コメントでモデルの存在を認める |

漏洩文書は「ウェブページ用の構造化データ（見出し・公開日付き）」だったことから、**正式な製品発表を準備していたドラフト**であることが示唆されている。Anthropicは意図せず自らのロードマップを世界に配ってしまったわけだ。

---

## 2. 「Claude Mythos」とは何者か

### 2.1 コードネームの二重構造：Capybara = Mythos

まず整理しておこう。文書には2つの名前が登場する。

* **Capybara** = 新しいモデルティアの名前。現在のOpusよりもさらに上位の層
* **Claude Mythos** = そのCapybaraティアに属する具体的なモデル名

ちなみにカピバラは世界最大のげっ歯類。一見のんびりしているが、他の動物に対して恐れを知らない。命名センスが良いのか悪いのか。

### 2.2 モデル階層の変化

現在のAnthropicのモデル体系はこうだ。

漏洩文書には以下の記述があったとされる（Fortune報道より）：

> 「Capybaraとは新しいモデルの名称であり、新しいティアの新しい名前だ — これまで最も強力だったOpusモデルよりも、より大きく、よりインテリジェントだ」

そして性能については：

> 「我々の前モデルであるClaude Opus 4.6と比較して、Capybaraはソフトウェアコーディング・学術推論・サイバーセキュリティなどのテストで劇的に高いスコアを得た」

### 2.3 Anthropicの公式コメント（確認済み事項）

Anthropicは以下の内容を公式に認めている。

> *「We're developing a general purpose model with meaningful advances in reasoning, coding, and cybersecurity. Given the strength of its capabilities, we're being deliberate about how we release it. As is standard practice across the industry, we're working with a small group of early access customers to test the model. We consider this model a step change and the most capable we've built to date.」*
>
> — Anthropic広報（Fortune紙への声明、2026/3/26）

**要約すると：**

* 存在は認める
* reasoning・coding・cybersecurityで「meaningful advances」
* 「step change（段階的変化ではなく飛躍的変化）」と自称
* 今はアーリーアクセス顧客でのみテスト中
* 慎重にリリースを進める

---

## 3. なぜ「前代未聞のサイバーリスク」なのか

ここが記事の核心だ。

### 3.1 漏洩文書が使った表現

漏洩したドラフトには、自社モデルについてこう書かれていた（Fortune、Security Boulevard等の報道より）：

**Anthropicの内部文書より（草稿）：**

* 「現時点でサイバー能力において他のあらゆるAIモデルを大幅にリードしている（currently far ahead of any other AI model in cyber capabilities）」
* 「防御側の努力をはるかに超えるペースで脆弱性を悪用できるモデルの波の到来を予告している（presages an upcoming wave of models that can exploit vulnerabilities in ways that far outpace the efforts of defenders）」
* 「前代未聞のサイバーセキュリティリスクをもたらす（poses unprecedented cybersecurity risks）」

これは製品を売るための誇大広告ではない。**自社モデルのリスクを自分たちで認めている**のだ。

### 3.2 「デュアルユース問題」とは何か

錠前師の比喩に戻ろう。最強の錠前師には2種類の使い方がある：

| 使い方 | 内容 |
| --- | --- |
| 防御側（Blue Team） | プロダクションコードベースの未知の脆弱性を発見・修正 |
| 攻撃側（Red Team / 悪意ある第三者） | 同じ脆弱性を発見して悪用・マルウェア開発 |

問題は、錠前師が**どちらの顧客にも同じスキルを提供できる**という点だ。AIモデルにはこの制約がない — プロンプト次第で向かう方向が変わる。

Anthropicが恐れているのは、「攻める側が守る側のスピードを上回る時代」の到来だ。

---

## 4. 「これは既に現実だった」 — Opus 4.6の衝撃的な実績

ここが多くの人が見落としているポイントだ。

Mythosはまだ一般公開されていない。だが、**既存のOpus 4.6で何が起きていたかを振り返ると、Mythosへの恐怖感が実感として湧いてくる。**

### 4.1 Anthropic Frontier Red Teamのレポート（2026年2月）

Security Boulevardの報告によれば、AnthropicのFrontier Red Teamが2026年2月に以下を実証している：

**検証結果（Anthropic Frontier Red Team, Feb 2026）：**  
Claude **Opus 4.6**（現行モデル・一般公開済み）が、**特別なスキャフォールディングなし**のアウトオブボックス状態で、本番オープンソースコードベースの**高重大度ゼロデイ脆弱性を500件超発見**した。

しかも、それらの脆弱性の中には：

* **数十年間見逃されていた**バグが含まれていた
* **LZW圧縮アルゴリズムの概念的理解**が必要なものが含まれており、通常のファジングでは到達不可能なレベルの推論が必要だった

これは「将来のリスク」ではない。**2月時点で既に現実だった**。Mythosはその能力が「劇的に」上がっているとされている。

### 4.2 中国国家支援グループによるClaude Code悪用事件

Anthropic自身が報告した事例だ：

| 項目 | 内容 |
| --- | --- |
| 攻撃主体 | 中国の国家支援グループ |
| 使用ツール | [Claude Code](https://qiita.com/GeneLab_999/items/d1299630fc2c0325003b)（[LLM](https://qiita.com/GeneLab_999/items/7f1bd2de313bdd7ca423)ベースのコーディングエージェント） |
| 侵入先 | テック企業・金融機関・政府機関を含む**約30組織** |
| AIの関与度 | 作戦全体の\*\*80〜90%\*\*をAIが担当 |
| Anthropicの対応 | 検知後10日間で全容を調査、関連アカウントをBAN、被害組織に通知 |

さらに別の安全性テストでは：

**Claude（通常モデル）が8時間以内にマルウェアファクトリーに転用された事例も確認されている。**

Mythosはその能力が「前代未聞」にまで強化されている。

### 4.3 市場はすぐに反応した

この話が広まった瞬間、株式市場がシグナルを出した：

| 銘柄 | 変動 | 備考 |
| --- | --- | --- |
| CrowdStrike (CRWD) | **-7%** | EDR最大手 |
| Palo Alto Networks (PANW) | **-6%** | 次世代ファイアウォール大手 |
| Zscaler (ZS) | **-4.5%** | クラウドセキュリティ大手 |
| Okta (OKTA) | **-7%超** | IDaaS大手 |
| Tenable | **-9%** | 脆弱性管理大手 |
| SentinelOne (S) | **-6%** | AIセキュリティ |

要するに「強力なAIがいれば既存のセキュリティツールが陳腐化するのでは」という恐怖が一気に価格に織り込まれた。（;ﾟдﾟ)ﾎﾟｶｰﾝ

---

## 5. 最大の皮肉：「最強の錠前師」の設計図が無施錠の工房から漏れた

ここで改めて事件の構造を整理しよう。

「前代未聞のサイバーリスクを持つAIを開発している会社が、設定ミス1個でそのAIの内部文書を全世界に公開した」

これは笑い話でもあり、深刻な問題でもある。

Anthropicの公式見解は「CMSの設定における人的ミス」であり、ドラフトコンテンツが意図せず公開されたと説明している。技術的には単純なアクセス制御の設定ミスだ。AWS S3バケットのACL設定ミスや、GitHubリポジトリの公開設定ミスと同じカテゴリの問題 — **開発者なら誰でも一度はやったことがある失敗**だ。

それが起きた場所が「AIセキュリティの最前線を走るAI安全性重視の企業」だったというだけで。

---

## 6. エンジニアとしての実践的な含意

セキュリティエンジニア・ソフトウェアエンジニアとして、この事件から何を読み取るべきか。

### 6.1 Mythosリリース時の影響シミュレーション

| フェーズ | 想定される変化 | 準備すべきこと |
| --- | --- | --- |
| **リリース直後** | 招待制・防御用途限定（サイバーセキュリティ企業向け） | API監視ポリシーの見直し |
| **一般API公開後** | プロンプトインジェクション攻撃の高度化 | LLMベースアプリのサニタイズ強化 |
| **数ヶ月後** | AI駆動ペネトレーションテストの普及 | 定期的な脆弱性スキャンの自動化 |
| **中長期** | パッチサイクルが「日」単位に圧縮される可能性 | CI/CDへのSASTツール組み込みを必須化 |

### 6.2 今すぐできるセキュリティ対策

既存のClaude（Opus 4.6含む）でも脆弱性発見能力は高い。Mythosを待たずに今からやるべきことがある。

```
# 自分のコードベースをAIベースのセキュリティスキャンにかける一例
# （概念コード。実際のツールはClaude Code / GitHub Copilot Security等）

import subprocess

def run_security_audit(codebase_path: str) -> dict:
    """
    AIベースのセキュリティ監査を実行する
    本番環境ではClaude Code, Semgrep, Snyk等と統合すること
    """
    results = {
        "high_severity": [],
        "medium_severity": [],
        "low_severity": []
    }
    
    # 静的解析ツールを組み合わせる
    # AI + 従来ツールのハイブリッドが現時点では最も効果的
    tools = [
        "bandit",       # Python特化セキュリティスキャナ
        "semgrep",      # パターンベース脆弱性検出
        "safety",       # 依存パッケージの既知CVEスキャン
    ]
    
    for tool in tools:
        result = subprocess.run(
            [tool, "--format", "json", codebase_path],
            capture_output=True,
            text=True
        )
        # 結果をパースして集約...
    
    return results
```

| カテゴリ | 対策 | 優先度 |
| --- | --- | --- |
| インフラ | S3バケット・CMSのパブリックアクセス設定を月1棚卸し | 高 |
| コード | SASTツール（Semgrep等）をCI/CDに組み込む | 高 |
| 依存関係 | `pip-audit` / `npm audit` を定期実行 | 中 |
| LLMアプリ | プロンプトインジェクション対策・出力サニタイズ | 中 |
| モニタリング | LLM APIの異常呼び出しパターンを検知 | 継続 |
| ポリシー | AI利用ガイドライン・アクセス制御ポリシーの策定 | 継続 |

### 6.3 トラブルシューティング：「AIに自分のコードを解析されたかも」と思ったら

| 症状 | 確認すべきこと | 対応 |
| --- | --- | --- |
| 不審なAPIリクエストを検知 | ログのUser-Agent・IPアドレス | WAFルールを追加、APIキーをローテート |
| 自社コードが外部に流出した可能性 | GitHub / S3 / CMSのパブリック設定 | 即座に非公開化、アクセスログを調査 |
| LLMアプリが意図しない動作 | プロンプトインジェクションの痕跡 | 入力バリデーション強化、ログ精査 |
| 依存ライブラリの脆弱性悪用の恐れ | CVEデータベースとの突合 | `pip-audit` 実行、SBOM管理の導入 |

---

## 7. Anthropicはどう向き合っているか

### 7.1 「慎重な（deliberate）リリース」戦略

Mythosに関して、Anthropicは明確に「急がない」姿勢を取っている：

* アーリーアクセスは**サイバーセキュリティ防御用途の企業に限定**
* 「防御側に先行アドバンテージを与える」ための意図的な非対称展開
* Anthropicの「Responsible Scaling Policy（RSP）」に基づくASL（AI Safety Level）評価を慎重に実施

### 7.2 Responsible Scaling Policy（RSP）との関係

AnthropicのRSPフレームワークはASL-1〜ASL-4+でモデルのリスクを評価する。Mythosは漏洩文書の表現から見て、**サイバーセキュリティ分野でASL-3以上**に分類されている可能性が高い。

[Claude Code](https://qiita.com/GeneLab_999/items/d1299630fc2c0325003b)でさえ既に「高サイバーセキュリティ能力」として分類されているケースがある（OpenAIが同月にGPT-5.3-CodexでHigh Cybersecurity Capabilityを公式に宣言したことも参照）。Mythosはその上を行く。

### 7.3 OpenAIとの比較：公開の仕方の違い

同時期、OpenAIはGPT-5.3-CodexのSystem CardにおいてHigh Cybersecurity Capabilityを**自ら公式に宣言**してリリースした。AnthropicはMythosについて**漏洩するまで何も言わなかった**。どちらの透明性戦略が正しいかについては議論が分かれる。

---

## 8. 学習ロードマップ：「AIとサイバーセキュリティ」の世界を理解する

### Level 1 — AIの基礎（前提知識）

まずAI・LLMの基礎を固めておこう。

### Level 2 — Claude / AI agentの仕組みを理解する

### Level 3 — セキュリティ実践

* **Semgrep** — OSSの静的解析ツール。CIへの統合から始める
* **OWASP LLM Top 10** — LLMアプリ開発者向けの脆弱性ランキング
* **pip-audit / npm audit** — 依存パッケージのCVEスキャン
* **bandit** — Python特化のセキュリティスキャナ

### Level 4 — AI安全性の最前線を追う

* Anthropic Responsible Scaling Policy（RSP）のドキュメント
* AI Safety Level（ASL）フレームワークの理解
* NIST AI RMF（AIリスク管理フレームワーク）

---

## まとめ

今回の事件を整理すると、こうなる。

**事件の本質（3行で）:**

1. Anthropicは「防御側と攻撃側の両方に使える」史上最強レベルのサイバーAIを完成させた
2. そのAIは既存Claudeでさえ500件のゼロデイを発見できたという実績の延長線上にある
3. そのことを世界に伝えたのは、Anthropic自身の設定ミスだった

個人的に刺さったのは、\*\*「最強の錠前師を作った工房が、鍵のかけ忘れで発覚した」\*\*という構造の純粋な皮肉さだ。

これはAnthropicを笑う話ではない。CMSの設定ミス、S3のパブリック設定、GitHubのリポジトリ公開設定 — これらは「やらかしたことある人は手を挙げてください」で全員が挙手するレベルの失敗だ。それが起きる場所として「最も恥ずかしい場所ランキング上位」に入っただけの話だ。orz

エンジニアとして今すぐできることは、自分のコードベースとインフラのアクセス制御を見直すこと。AIが脆弱性を探す速度が上がるなら、それに備えるのも今日からできる。

Mythosが正式リリースされる頃に「あの時対策しておいてよかった」と思えるかどうかは、今日の選択次第だ。

---

## 参考文献

---

この記事が参考になった方はいいね・ストックをもらえると次の記事を書くモチベになります。
