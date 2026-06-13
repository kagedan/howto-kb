---
id: "2026-06-13-claude-design入門-テキストだけでプロトタイプスライドlpを即作成するanthropic-01"
title: "Claude Design入門 — テキストだけでプロトタイプ・スライド・LPを即作成するAnthropicの新ツール"
url: "https://qiita.com/kai_kou/items/e174e7448bc3e2909efe"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-06-13"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月17日、Anthropicは [Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs) をリサーチプレビュー公開しました。Anthropic Labs が開発した初のビジュアル生成プロダクトで、テキストプロンプトを入力するだけでインタラクティブなプロトタイプ・スライドデッキ・ランディングページを生成できます。

### この記事で学べること

- Claude Design の概要と主な機能
- 利用できるプランと料金体系
- プロトタイプ・スライド生成の操作フロー
- Claude Code へのハンドオフの仕組み
- 注意点と現時点での制約

### 対象読者

- デザインツールの操作に慣れていないエンジニア・PdM・スタートアップ創業者
- Claude を普段から使っているエンジニアで、ビジュアル生成にも活用したい方
- プロトタイプやスライド作成のコストを下げたい方

### 前提条件

- Claude Pro / Max / Team / Enterprise のいずれかのプラン
- [claude.ai/design](https://claude.ai/design) にアクセス可能な環境

## TL;DR

- Claude Design は Claude Opus 4.7 搭載のビジュアル生成ツール（Anthropic Labs）
- **追加料金なし**。既存の有料プラン（Pro/Max/Team/Enterprise）で利用可能
- プロトタイプ・スライド・LP を日本語プロンプトで生成し、Canva・PDF・PPTX・HTML にエクスポート
- チームのコードベースを読み込み、**デザインシステムを自動構築**
- Claude Code へのハンドオフバンドルで設計→実装を一気通貫に

## Claude Design とは

Claude Design は Anthropic Labs（Anthropicの実験的プロダクト部門）が開発した AI 駆動のビジュアル生成ツールです。

従来のデザインツール（Figma・Canva・PowerPoint）は、ある程度のデザインリテラシーや操作スキルが必要でした。Claude Design は「アイデアを言葉で説明するだけで、見栄えのよいアウトプットを即座に得る」ことに特化しており、デザイン経験のないエンジニア・プロダクトマネージャー・マーケターがターゲットです。

Claude Opus 4.7 を基盤としており、2026年4月17日にリサーチプレビューとしてリリースされました。

## 利用プランと料金

| プラン | 月額料金（目安） | Claude Design |
|--------|----------------|---------------|
| Pro | $20/mo | ✅ 利用可能（週次上限あり） |
| Max | $100〜$200/mo | ✅ 利用可能（上限緩め） |
| Team | $20〜$25/seat/mo（Standard seat: 年次$20・月次$25） | ✅ 利用可能（管理者設定不要） |
| Enterprise | カスタム | ✅ 利用可能（管理者による有効化が必要） |
| Free | - | ❌ 非対応 |

> [公式: Claude Design 料金と利用量](https://support.claude.com/en/articles/14667344-claude-design-subscription-usage-and-pricing)

Claude Design 専用の週次使用量が chat / Claude Code の使用量とは**別枠**で管理されています。上限に達した場合は「Extra Usage」を有効化することで継続利用が可能です。

Enterprise プランの場合は管理者が Organization Settings から Claude Design を有効化する必要があります（[Admin ガイド](https://support.claude.com/en/articles/14604406-claude-design-admin-guide-for-team-and-enterprise-plans)）。

## 主な機能

### 1. テキストプロンプトから生成

`claude.ai/design` にアクセスし、作りたいアウトプットを選択してプロンプトを入力するだけです。

**対応する成果物の種類:**

| 種別 | 用途例 |
|------|--------|
| インタラクティブプロトタイプ | Web アプリ・モバイルアプリのクリッカブルモック |
| スライドデッキ | 提案書・ピッチデック・社内プレゼン |
| ランディングページ | 製品紹介 LP・マーケティングページ |
| マーケティング素材 | SNS 投稿用画像・ワンページャー |
| コードパワードプロトタイプ | 音声・動画・シェーダー・3D を含む高度なプロトタイプ |

**入力できる素材:**

- テキストプロンプト（日本語可）
- 画像・ドキュメント（DOCX / PPTX / XLSX）
- 自社コードベースへの参照
- Web キャプチャツール（既存 Web サイトから要素を直接取得）

### 2. 対話的な反復修正

生成後は以下の方法でブラッシュアップが可能です。

- **インラインコメント**: 特定の部分を選択してコメントで修正指示
- **直接編集**: テキストや要素を直接書き換え
- **カスタムスライダー**: Claude が生成した調整スライダーで細かなパラメータを変更

### 3. エクスポート

| エクスポート先 | 備考 |
|--------------|------|
| Canva | 完全編集可能 |
| PDF | 印刷・配布用 |
| PPTX | PowerPoint で引き続き編集 |
| HTML（スタンドアロン） | そのままホスティング可能 |
| 共有 URL | 組織内部向け（閲覧のみ / 編集権限を設定可） |

> 現時点では Figma への直接エクスポートには対応していません。

### 4. チームデザインシステムの自動構築

チームのコードベースやデザインファイルを読み込ませると、Claude が色・タイポグラフィ・コンポーネントを抽出してデザインシステムを構築します。以降のプロジェクトでは自動的にそのデザインシステムが適用され、一貫したアウトプットが得られます。

複数のデザインシステムの管理・切り替えにも対応しています。

### 5. Claude Code へのハンドオフ

設計が固まったら、Claude Code に引き渡して実装を進める「ハンドオフバンドル」を生成できます。

ハンドオフバンドルは tar アーカイブ形式で、README にはコーディングエージェントへの指示が含まれています。Claude Code に以下のように渡すだけで実装フェーズに移行できます。

```bash
# ハンドオフバンドルを展開して Claude Code で実装開始
# （Claude Code の /upload またはファイル参照機能から利用）
```

この「設計 → 実装」の一気通貫フローが Claude Design の最大の特徴のひとつです。

> [公式発表](https://www.anthropic.com/news/claude-design-anthropic-labs)

## 使い方のステップ

### Step 1: アクセス

[claude.ai/design](https://claude.ai/design) にアクセスします（Pro 以上のプランでログイン済みであること）。

### Step 2: 成果物タイプを選択

トップ画面のタブから生成したいアウトプットの種別を選びます。

- **Prototype**: インタラクティブなクリッカブルモック
- **Slide deck**: 提案書・プレゼン
- **その他（テキスト自由記述）**: LP・ワンページャーなど

### Step 3: プロンプトを入力

日本語でそのまま記述できます。例:

```
AIリスキリングプログラムの提案書を作ってください。
対象: 非エンジニア社員（50名規模）
内容: 研修カリキュラム、費用感、スケジュール
テイスト: プロフェッショナル、信頼感のある配色
```

### Step 4: インタラクティブに修正

生成結果を確認し、気になる箇所はチャットで追加指示するか、インラインコメントで修正します。

### Step 5: エクスポートまたはハンドオフ

完成したら目的に応じてエクスポート形式を選択します。実装が必要な場合はハンドオフバンドルを生成して Claude Code に渡します。

## 注意点・現時点での制約

| 制約事項 | 内容 |
|---------|------|
| Figma エクスポート | 未対応。現在は Canva / PDF / PPTX / HTML のみ |
| データレジデンシー | 未対応。データレジデンシー要件がある企業は現時点では利用不可 |
| Enterprise 有効化 | 管理者が Organization Settings で有効化が必要 |
| 使用量上限 | chat / Claude Code とは別枠の週次上限あり。Pro は上限が厳しめ |
| リサーチプレビュー | GA（一般提供）ではなくリサーチプレビュー段階のため、仕様変更の可能性あり |

> Claude Design は Canva の代替ではなく補完ツールであることを Anthropic は明言しています。
> — [Introducing Claude Design by Anthropic Labs](https://www.anthropic.com/news/claude-design-anthropic-labs)（2026-04-17）

## まとめ

Claude Design のポイントを整理します。

- **対象**: デザイン経験を問わない。エンジニア・PdM・マーケターが主なターゲット
- **追加料金不要**: 既存の Pro/Max/Team/Enterprise プランで即利用可能
- **生成物**: プロトタイプ・スライド・LP・SNS素材など幅広い
- **強み**: Claude Code とのハンドオフ、チームデザインシステムの自動構築
- **制約**: Figma 未対応・データレジデンシー未対応・リサーチプレビュー段階

現時点では研究プレビュー段階ですが、Claude Opus 4.7 と Claude Code のエコシステムに深く統合されており、「アイデアから実装まで」を Claude ひとつで完結させるという Anthropic の戦略がよく表れているプロダクトです。

今後の GA（一般提供）に向けて Figma 連携・API 開放・データレジデンシー対応なども予定されているため、引き続き注目する価値があります。

## 参考リンク

- [Introducing Claude Design by Anthropic Labs](https://www.anthropic.com/news/claude-design-anthropic-labs) — Anthropic 公式発表（2026-04-17）
- [Get started with Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design) — ヘルプセンター: 始め方
- [Claude Design subscription usage and pricing](https://support.claude.com/en/articles/14667344-claude-design-subscription-usage-and-pricing) — ヘルプセンター: 料金・使用量
- [Claude Design admin guide for Team and Enterprise](https://support.claude.com/en/articles/14604406-claude-design-admin-guide-for-team-and-enterprise-plans) — Team/Enterprise 管理者向けガイド
- [Anthropic launches Claude Design | TechCrunch](https://techcrunch.com/2026/04/17/anthropic-launches-claude-design-a-new-product-for-creating-quick-visuals/) — TechCrunch 報道（2026-04-17）
