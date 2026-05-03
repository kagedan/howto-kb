---
id: "2026-05-02-github-copilot-従量課金化pre-pr-self-review-cross-model-01"
title: "GitHub Copilot 従量課金化：Pre-PR Self Review × cross-model 視点分離で Claude Code + Codex CLI へ移行した話"
url: "https://qiita.com/akatsuki39/items/aea601a3680b20882f5b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "OpenAI", "GPT", "qiita"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月、GitHub から「Copilot が PRU（Premium Request Unit）を廃止し、従量課金に移行する」という案内メールが届いた。Pro / Pro+ / Business / Enterprise すべてに及ぶ変更で、個人開発者だけでなく Organization 利用者にも影響する。

私の運用は次のような構成を主に使用していた：

- **コード生成・設計**: Claude Code（Opus / Sonnet）—— 設計判断・大規模リファクタ・整合性レイヤの読みは Opus、日常の生成・修正は Sonnet という使い分け
- **PR レビュー**: GitHub PR に Copilot をレビュワー追加（Codex / GPT 系モデルが担当）—— 厳密な型・境界条件・例外網羅で Claude の見落としを補う cross-model クロスチェック

異なるモデルファミリにレビューさせる **cross-model のクロスチェック設計**で、観点バイアスを減らしてきた。これが今回の変更で揺らぐ可能性がある。

本記事は変更内容のまとめではなく、**ひとりの開発者としてどう移行するか**という実用論。以下のいずれかに当てはまる人向け：

- PR を出す前にローカルで AI レビューを完走させる「Pre-PR Self Review」を試してみたい
- Anthropic 系（Opus / Sonnet）と Codex 系（GPT 系モデル / Codex CLI）のレビュー癖の違いを cross-model で活用してみたい
- Copilot の PR レビュワー機能を使っており、プラン従量課金化に困っている


## 用語

"Codex" という単語は、CLI ツール名（Codex CLI）とモデル ID（gpt-5.3-codex 等）の両方で登場するため、以下の表記に統一する。

| 表記 | 意味 |
|---|---|
| **Codex CLI** | OpenAI が提供するコーディングエージェント CLI（ツール名） |
| **モデル ID** | `gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex` 等の識別子。 |
| **ChatGPT サブスク** | Plus / Pro / Business 等の有料プラン総称 |
| **API キー認証** | `OPENAI_API_KEY` を使った従量課金認証経路 |
| **GitHub Copilot Review** | GitHub の PR レビュー機能 |


## 1. 機能改善が利用減を招く――待ち時間とラウンド累積の話

新課金の話が出る前から、私は GitHub Copilot Review を既に抑制していた。理由は**金額ではなく、待ち時間**。

```
当初: 全 PR で Copilot Reviewer を追加
  ↓
現在: 軽微な PR はセルフチェックのみ、本番影響のある PR だけ GitHub Copilot Review
```

GitHub Actions が裏で走るので、Reviewer 追加から返事までに10分程度の待ちがある。

加えて、GitHub Copilot Review は **1回の指摘数が控えめ**で、修正コミットの後に再レビューを依頼すると新たな指摘が返ってくることが多かった。
1 PR あたり実際は2〜3ラウンドの review が走り、**ラウンドごとの待ち時間が累積**する。指摘が後出しで出てくる構造のため、「次こそ all clear だろう」と思って依頼したレビューでまた新たな指摘が返ってくる――こうした不毛なレビュー依頼も生じていた。

小さな修正 PR に待ちは割に合わず、自然と「**重要な PR だけ依頼する**」運用に変わっていた。

Copilot のカスタムインストラクションで「1 ラウンドで網羅的にレビューしてほしい」と方向付ける試みも検討していた。
しかしながら、公式の改善とバッティングする可能性を考慮しやめていた。

今回の従量課金化で「1 ショット完結」へ向かうなら、それはラウンド累積問題への構造的な答えにもなる。
だが各プランに付与されるクレジット枠は **Pro: $10、Pro+: $39、Business: $19 分相当**（[GitHub 公式ブログ](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/) 参照、1 credit = $0.01）。agentic レビュー 1 回あたりの予想クレジット消費と突き合わせると、**従来感覚の頻度では回せない可能性が高い**。


## 2. 何が変わるのか（要点）

詳細は[GitHub 公式ブログ](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)に譲り、要点だけ：

- 2026年6月1日: **PRU 廃止 → AI Credits** 化（1 credit = $0.01 USD）
- Pro $10/月、Pro+ $39/月、Business $19/月
- Code Review は **AI Credits + GitHub Actions 分の二重消費**（[2026-04-27 Changelog](https://github.blog/changelog/2026-04-27-github-copilot-code-review-will-start-consuming-github-actions-minutes-on-june-1-2026/)）
- Pro/Pro+ は **新規登録停止中**（2026/4/20〜）
- **Opus models は Pro から削除、Pro+ のみ Opus 4.7 残存**（個人プランのモデルアクセス縮小）
- **2026年5月上旬: billing preview にメーター機能搭載予定** （自分の利用実績を AI Credits 換算で確認できる）
- 既存ユーザーの解約返金は **5月20日まで**


## 3. 何が問題か：1レビューのコストが読めない

旧課金は **1 PRU = 1レビュー** で固定。実行できる回数が確定していた。

新課金は **トークン消費 × モデル単価**。**agentic アーキテクチャ化**したので、1回あたりのトークン消費は増える方向。

ただし公式 docs では「**Copilot Code Review が使うモデルは自動選択かつ非開示**、**1 レビューあたりのトークンコストはレビューごとに変動する**」と明記されている（[GitHub Docs: Models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)）。**正確な事前予測は構造的に不可能**。
それを踏まえた上で「**もしこのモデルなら**」のシナリオ試算を以下に示す。単価は **2026年5月時点の GitHub Copilot 公式記載**を使用、入力50K + 出力10K トークン（agentic レビューで diff + 関連 context を読み込む前提で控えめに見積もった仮定値）で算出：

| モデル | 入力単価 | 出力単価 | 1レビュー概算 | $10で約 |
|--------|---------|---------|------------|--------|
| GPT-5.3-Codex | $1.75/M | $14/M | $0.23 | 43回 |
| GPT-5.4 | $2.50/M | $15/M | $0.28 | 36回 |
| Claude Sonnet 4.6 | $3/M | $15/M | $0.30 | 33回 |
| Claude Opus 4.7 | $5/M | $25/M | $0.50 | 20回 |

「**プラン料金は据え置きだが、モデル × トークン量 × ラウンド数の 3 軸で実質コストが大きく揺れる**」設計になった——事前にコストを読みにくい構造そのものが、本記事の主題。

### 自分の数字を出してみる：billing preview

GitHub は移行準備のために billing preview を提供している（[公式 docs: Preparing for your move to usage-based billing](https://docs.github.com/en/copilot/how-tos/manage-and-track-spending/prepare-for-your-move-to-usage-based-billing)）。アナウンスバナーの「Preview my bill」から、**現在の利用実績を AI Credits 換算で試算**できるとのこと。
さらに **2026年5月初旬からは usage report CSV をアップロードしてインタラクティブに試算できるツール**も公開予定とのこと。

→ 上の試算表で示した回数感（20〜40 回程度）は仮定値で、自分のリポジトリでの実消費は preview で確認してください。


## 4. 移行先：Claude + ChatGPT 併用

私が選んだ移行先：

| 用途 | サブスク | ツール | 月額 |
|------|---------|------|------|
| コード生成 | Claude | Claude Code | Pro $20～ |
| コードレビュー | ChatGPT | Codex CLI | Plus $20～ |
| **合計** | | | **$40/月～** |

参考：Copilot Pro+ は $39/月 + 従量超過分。

### 主動機は cross-model 視点分離の維持

コスト削減ではなく定額化、および、**異なるモデルファミリでレビューする cross-model 構成を維持すること**が主動機。具体的にどう違うかは、使い込んでいる人ほど実感があると思う：

- **Claude（Anthropic）** は意図と整合性、設計レイヤーの一貫性、可読性に強い
- **Codex / GPT 系** は例外処理の網羅性、エッジケースの想定、型と境界の厳密性に厳しい

Claude で生成したコードを Claude にレビューさせると、観点が同じため**チェックが甘くなる**。Codex 系に渡すと、Claude が見落としやすい例外処理や境界条件を厳しく指摘されることが多い。これが**異なるモデルファミリでクロスチェックする実益**で、GitHub Copilot Review が提供していた価値だった。

### 実走行で確認

ここまでの主張は、自分のリポジトリで実際の PR を題材に同じプロンプトを両モデルに通すことで具体的に確かめることができた。

検証は Codex CLI に独自の日本語プロンプトを直接投入して行った。
`codex review-pr` / `/review` は AGENTS.md の言語指示を無視して英語固定で出力する既知の挙動があるため（[Codex Issue #5113](https://github.com/openai/codex/issues/5113)）、日本語で結果が欲しいなら interactive + 自前プロンプトが現実的と思われる。

Claude Opus と Codex CLI（`gpt-5.3-codex`）に同じプロンプトで通したところ、事前の実感どおりの強みが確認できた:

- **Claude**: 広い文脈での本番運用視点、フレームワーク内部理解、コード間の整合性、PR スコープ判断
- **Codex CLI (`gpt-5.3-codex`)**: 境界条件の厳密性、リポジトリ衛生、テスト方針、PR の責任範囲意識

両者の指摘は重複しない部分が多かった。「視点が違う」という cross-model の実益が、具体的な指摘の差として確認することができた。

### 構成の3つの利点

**1. cross-model 視点分離の維持**

観点バイアスを打ち消す効果が得られた。$40/月～で GitHub Copilot Review と同等の cross-model 体験をローカルで再構築できる。

**2. モデル提供者直営はサブスク制を維持しやすい**

Anthropic や OpenAI は自社モデルを定額サブスクで提供している。GitHub のような自社でモデルを保持しない場合 API 仕入れがありサブスクでの提供は難しいと思われる。

**3. コストが完全に固定（ラウンド数の自由度を取り戻す）**

「1レビューいくら」を意識せずに済む。実行時間も、GitHub Copilot Review に比べ、Codex CLI の方が格段に速い。

### Free 期間限定解放中──踏み出しやすい今

ここまで「移行先」として Plus 契約前提で書いてきたが、実は **2026-05 時点で Codex CLI は Free プランにも期間限定で解放**されている（OpenAI 公式アナウンスは "limited time" 表記で具体期限の明示なし）。

つまり、Plus 契約に踏み切る前に、**自分のプロジェクトで cross-model レビューがどの程度効くかを Free でまず試す**ことができる。Free 枠で複数回のレビュー実行が可能で、判断材料を集めるには充分（具体的な可能回数は環境・PR 規模・プロンプトで変動）。

今のうちに自分のワークロードで体験しておくほうが、移行の意思決定の質が上がる。Copilot の解約返金期限も 5/20 と近いので、「とりあえず触って」みてほしい。

### Codex CLI の他情報

→ Codex CLI 自体のセットアップ・認証経路・利用可能モデル・レート制限・Free 枠の期間限定解放など、本文で踏み込まなかった事実情報は補足記事「[Codex CLI 実用リファレンス：モデル・認証・料金（2026-05 時点）](https://qiita.com/akatsuki39/items/936806eba6098d830432)」にまとめた。
網羅的な公式リファレンス翻訳としては [@nogataka 氏「Codex CLI 完全リファレンス」](https://qiita.com/nogataka/items/d053468277b37c83ec3a)（2025-11 時点、Pro $100 tier・Free 期間限定解放等の最新情報は反映前）も併せて参考。


## 5. ワークフロー：Pre-PR Self Review

Copilot Reviewer 追加 UX の代わりに、PR 作成前にローカルでレビューする運用に切り替える。

本記事ではこの運用を **Pre-PR Self Review** と呼ぶ。これは Codex CLI（OpenAI）と Claude Code（Anthropic）という両陣営の公式 CLI ツールを組み合わせた一形態。Copilot レビュワー追加 UX の代替として、開発者が組める最小構成として整理する。

### レビュー用プロンプト

Codex CLI を interactive 起動して投入するプロンプト例。観点と出力体裁を指定すると、そのまま PR コメントに使える形で返ってくる:

```text
PR #<番号> を Pre-PR self review として日本語でレビューしてください。

【観点】
1 ショットで見つけられる issue を全て出してください。
バグ・セキュリティ・設計・命名・型・境界条件・テスト不足など、観点に制限はありません。

【出力】
- 画面にレビュー結果を表示
- 体裁は、そのまま `gh pr comment <PR番号> -F <file>` で投稿できるマークダウン
  - サマリ
  - 指摘一覧（重大度ラベル high / med / low 付き）
```

### 通常 PR（小〜中規模）

```bash
# コードを書き終えたら、push 前に Codex CLI でレビュー
codex
# → 上記「レビュー用プロンプト」を投入して指摘を受け取る

# 指摘を反映
git add .
git commit -m "fix: address review feedback"

# push & PR 作成
git push origin feature-branch
gh pr create
```

PR 上では人間レビューのみ、AI レビューは依頼しない。

### 重要 PR（本番影響・大規模）

レビュー履歴を PR 上に残したい場合は、上記「レビュー用プロンプト」で得た出力を `/tmp/review.md` 等に保存し、`gh` で PR コメント投稿:

```bash
# Codex CLI で「レビュー用プロンプト」を投入 → 出力を /tmp/review.md に保存

# gh CLI で PR コメントとして投稿
gh pr comment <PR番号> -F /tmp/review.md
```

### iterative review pattern の解消

Copilot 時代に問題だった「指摘が後出しで来る／ラウンドごとに10程度分待つ」構造は、ローカル CLI に移すと改善する。対話的に review → 修正 → 再 review を必要なだけ回しても、待ち時間短縮、コストはサブスク定額内。Copilot Reviewer の UX （PRからレビュワー追加するだけ、インラインコメント含めてレビュー）を失うが、メリットは大きい。

### この方式の副次的メリット

- **自分で消化する学びが増える**：レビュー指摘 → 理解 → 修正のサイクルを自分で回す
- **PR 本文の質が上がる**：レビューで気づいた論点を「こう考えた」と PR 本文に書ける
- **チームレビュアーの負担が減る**：基本品質が担保されてから PR に上がる
- **ラウンドの自由度が戻る**：「もう1回回そうか」を躊躇する必要がない


## 6. やってはいけないこと（利用規約）

コスト削減目的でも、サブスクリプションの利用規約に反する使い方は避ける。

| 行為 | 規約上の判定 |
|------|---------|
| ローカルで対話的に Codex CLI を使う | OK |
| Codex CLI 出力を手動で gh 投稿する | OK |
| GitHub Actions で Codex CLI を自動実行 | NG濃厚 |
| 自分のサブスクをチームで共有 | NG |

※ 上記は一般的な傾向であり、正確には各公式のドキュメントをご確認ください。

CI/CD で自動レビューを回したい場合は、API利用など公式で認められている方法を使うこと。
ただし、コスト的には GitHub Copilot Review と変わらなくなってくるものと考えられる。


## 7. GitHub Copilot はどこへ向かうのか

Copilot の本来の強みは「**コードのある場所＝GitHub**」のネイティブ統合。PR Reviewer 追加から自動インラインコメントまでの UX は、他のツールでは出せない便利さがある。

しかし AI モデル提供者直営サブスクが充実するにつれ、ユーザー市場では構造的に厳しくなる。AI Credits（従量課金）への移行は GitHub 側にとっても経済合理性の観点で避けられない選択だったとも読める。


## まとめ：判断のタイムライン

| 日付 | アクション |
|-----|----------|
| 5月初旬 | Copilot billing preview で4月実績の新換算確認 |
| ~5月20日 | Copilot 解約 or 継続の最終判断（解約は新規登録停止中＝片道切符） |
| 6月1日 | 従量課金切替日 |

Copilot Reviewer UX を失う代わりに、Pre-PR Self Review というローカル完結の構成が手に入る。ラウンド数の自由度・cross-model 視点分離・固定サブスク――Copilot 時代に諦めていた3点が同時に戻ってくる。これは単なるコスト最適化ではなく、プラットフォームリスクの分散でもある。1社の AI 戦略変更（今回のような従量化や値上げ）に振り回されない、より硬いセットアップになると期待したい。


## 参考リンク

### 公式ソース

- [GitHub Copilot is moving to usage-based billing - The GitHub Blog](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)
- [Changes to GitHub Copilot Individual Plans - The GitHub Blog](https://github.blog/news-insights/company-news/changes-to-github-copilot-individual-plans/)
- [GitHub Copilot Code Review will start consuming GitHub Actions minutes - 2026-04-27 Changelog](https://github.blog/changelog/2026-04-27-github-copilot-code-review-will-start-consuming-github-actions-minutes-on-june-1-2026/)

### Codex / OpenAI

- [Codex CLI Features - OpenAI Developers](https://developers.openai.com/codex/cli/features)
- [Use Codex in GitHub - OpenAI Developers](https://developers.openai.com/codex/integrations/github)
- [GitHub Action – Codex - OpenAI Developers](https://developers.openai.com/codex/github-action)

### Claude / Anthropic

- [Claude Code overview - Claude Code Docs](https://code.claude.com/docs/en/overview)
- [Claude Code GitHub Actions - Claude Code Docs](https://code.claude.com/docs/en/github-actions)
- [Claude Code Action - GitHub](https://github.com/anthropics/claude-code-action)

### 参考記事

- [Zenn imudak: 「Copilot で十分」と書いた私が、料金を詳しく調べて Claude に乗り換えることにした話](https://zenn.dev/imudak/articles/copilot_vs_claude_pricing)
- [Zenn yokoi_ai: 「AI 使い放題」の終わり ― GitHub Copilot 停止と 6月 Token 課金の経済学](https://zenn.dev/yokoi_ai/articles/ai-2026-04-24)
- [ビューローみかみ: GitHub Copilot を「最強のハブ」として使い続ける理由](https://www.bureau-mikami.jp/github-copilot-usage-based-billing-strategy/)
- [openai/codex-plugin-cc - GitHub](https://github.com/openai/codex-plugin-cc) — Claude Code 内から Codex を呼ぶ OpenAI 公式プラグイン。cross-model レビューの別アプローチ
