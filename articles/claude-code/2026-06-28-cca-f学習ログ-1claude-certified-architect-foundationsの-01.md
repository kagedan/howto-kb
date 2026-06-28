---
id: "2026-06-28-cca-f学習ログ-1claude-certified-architect-foundationsの-01"
title: "【CCA-F学習ログ #1】Claude Certified Architect Foundationsの概要と学習リソース"
url: "https://zenn.dev/yujmatsu/articles/20260628_cca_foundations_01_overview"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-28"
date_collected: "2026-06-29"
summary_by: "auto-rss"
query: ""
---

## はじめに

この記事は、**Claude Certified Architect – Foundations（以下 CCA-F）** の受験に向けて学習プロセスを記録する連載の第1弾です。

試験の攻略まとめや合否報告ではなく、「学びながら記録する」スタイルで進めます。各回でドメインを学び、手を動かしたコードを残し、曖昧に残った点は正直に書き、末尾の理解度トラッカーを更新していきます。

**本連載のゴール**

* CCA-F の試験範囲をドメイン別に一通り手を動かして理解する
* 学習プロセスを記録として残し、後から受験する方の参考にする

**想定読者**

* Claude API / Claude Code を業務で触ったことがあり、CCA-F を受けてみたいエンジニア
* 資格の存在を最近知り、何から手をつければいいか迷っている方
* 試験まとめより、学習プロセスをいっしょに追いたい方

**著者の立ち位置**

現時点でまだ受験していません。この連載を書きながら学ぶスタイルです。  
今回会社で受験の機会を得たので、7-8月頃の取得を目指して勉強をしていくところです。

## そもそも Claude とは

Claude（クロード）は、Anthropic が開発している AI アシスタントです。大規模言語モデル（LLM: Large Language Model）と呼ばれる種類の AI で、人間が書いた文章を理解し、自然な文章やコードを生成できます。

CCA-F は「Claude を使って本番アプリケーションを作る力」を問う試験です。  
そこでまず、Claude にどう触れられるか（プロダクトの全体像）を押さえておきます。

**Claude への主な触れ方**

| 触れ方 | 何か | 主な用途 |
| --- | --- | --- |
| Claude.ai / デスクトップアプリ | ブラウザやアプリ上のチャット画面 | 対話で文章作成・要約・相談など |
| Claude API | プログラムから Claude を呼び出す窓口 | 自作アプリ・スクリプトに組み込む |
| Claude Code | ターミナルで動くコーディング支援エージェント | コード生成・リファクタ・自動化 |

さらに、これらを支える/拡張する仕組みとして、次の2つがあります。

* **Claude Agent SDK**：Claude を使ってエージェント（自律的に手順を進めるプログラム）を作るための開発キット。
* **MCP（Model Context Protocol）**：Claude を外部のツールやデータソースにつなぐための標準プロトコル。

![図1: Claude への主な触れ方（全体像）](https://static.zenn.studio/user-upload/deployed-images/6af40dd176feea99f0a3210b.png?sha=3509cb5a200faa5760cadf18dce6c995ca37c34d)  
*図1: Claude への主な触れ方（全体像）。Claude.ai・Claude API・Claude Code と、それらを支える Agent SDK / MCP。*

**モデルのラインナップ**：Claude には用途に応じて複数のモデルがあり、おおまかに「高性能重視」「速度と性能のバランス」「高速・軽量」といった方向性で分かれています。モデル名や性能は更新されるため、最新は公式ドキュメントで確認してください。

CCA-F の出題範囲（Claude Code / Claude Agent SDK / Claude API / MCP）は、ちょうどこの「Claude への触れ方」と重なります。本記事では全体像だけを示し、それぞれの基本的な使い方は **#2 基礎編** で手を動かしながら詳しく扱います。

## Claude Certified Architect – Foundations とは

### 位置づけ

CCA-F は **Anthropic が 2026年3月12日に発表した初の技術認定試験** です。  
同日に発表された Claude Partner Network への投資拡大と合わせて公開されました。

公式の説明によると、**本番アプリケーションを構築するソリューションアーキテクト向けの技術認定** と位置づけられています。Claude を使ったシステム設計・実装の能力を評価するものです。

### 入手・受験経路

公式アナウンスでは「パートナー向けに提供」とされており、受験は **Claude Partner Network の Partner Portal 経由** が基本です。学習教材は **Anthropic Academy**（Anthropic が eラーニング基盤 Skilljar 上で運営する無料の学習サイト）で提供されます。Academy 単体で受験できると公式に明言されているわけではない点に注意してください。2026年6月時点では Early Adopter Program（EAP）のベータ段階で、一般公開（GA）の状況は要確認です。

なお Partner Portal へのアクセスや EAP への参加にはパートナー登録が前提になる場合があります（具体的な手続きは公式で要確認）。

### 上位資格ラダー

公式が明言している点として、**Foundations は資格ラダーの入口層** です。2026年後半に seller / architect / developer 向けの認定を追加予定と公式がアナウンスしています。

![図2: CCA-F 資格ラダー図](https://static.zenn.studio/user-upload/deployed-images/a405786333b67dd26947b6e6.png?sha=44ae999de35b64fad716a6ae2da287432b973eda)  
*図2: Foundations は入口層。2026年後半に追加予定の上位層は現時点で詳細未公開（破線で表現）。*

## 試験の概要

CCA-F は、**Claude Code・Claude Agent SDK・Claude API・MCP（Model Context Protocol）** という、Claude で本番アプリケーションを作るための中核技術を横断して問う試験です。対象は本番アプリを設計・実装するソリューションアーキテクトとされています。

!

**出典についてのお断り**  
詳しい試験要項は、公式の「Claude Certified Architect – Foundations Certification Exam Guide」に記載されています。ただしこの資料は各ページに **「Anthropic, PBC · Confidential Need to Know (NTK)」** と明記された非公開文書（EAP参加者向け）です。そのため本記事では、サンプル問題・タスクステートメント・各シナリオの具体的な内容・出題範囲の詳細リストといった機密部分は引用しません。以下は、Anthropic が公開しているページで確認できる情報と、出題範囲の大枠（対策コミュニティでも広く共有されているレベル）に絞って整理しています。

### Anthropic が公開している情報

次の点は Anthropic の公開ページで確認できます。

* 認定は **Anthropic Partner Academy の試験** で取得し、**個人に帰属**します（会社単位ではありません）。認定者は **直近90日以内に Claude を利用していること** が条件とされています（[パートナーハブの説明](https://www.anthropic.com/news/services-track-partner-hub)）。
* 2026年3月の開始以降、**パートナー企業のコンサルタント1万人以上**が Claude 認定（CCA-F を含む各認定）を取得済みと公表されています（同上）。
* CCA-F は現在 **Early Adopter（EAP / ベータ）** 段階で、Claude Partner Network 経由で提供されています。
* 学習教材は **Anthropic Academy** で提供され、上位資格（seller / architect / developer 向け）が2026年後半に追加予定です。

### 出題ドメインと配分（大枠）

試験範囲は5つのドメインに分かれます。本連載は #2 以降でこの5ドメインを1つずつ扱います。配分の数値は対策コミュニティで共有されているもので、Anthropic の公開ページに一覧として掲載されているわけではありません（最新は公式で確認してください）。

| ドメイン | 配分 |
| --- | --- |
| Agentic Architecture & Orchestration（エージェント設計・オーケストレーション） | 27% |
| Claude Code Configuration & Workflows（Claude Code の構成と運用） | 20% |
| Prompt Engineering & Structured Output（プロンプト設計・構造化出力） | 20% |
| Tool Design & MCP Integration（ツール設計・MCP 連携） | 18% |
| Context Management & Reliability（コンテキスト管理・信頼性） | 15% |

出題は多肢選択式・シナリオベースで、合否はスケールドスコア（受験者ごとの難易度差を補正した統一スコア。100〜1,000 で合格ライン 720）で判定される、という形式情報も共有されています。

### 公開ページには載っていない項目

問題数・試験時間・受験費用・監督の有無・対応言語・再受験ポリシーは、Anthropic の公開ページには掲載されていません（詳細は非公開の試験ガイドや Partner Portal 側にあります）。対策サイトには「60問・120分・$99」等の記載がありますが、公式での裏取りはできていません。受験前に Partner Portal で確認してください。

## 学習リソースの地図（Anthropic Academy）

Anthropic Academy（前述の無料学習サイト）には、CCA-F の出題範囲をカバーするコースが揃っています。CCA-F の発表時、Anthropic は「学習教材を Partner Portal 経由で提供する」と案内しており、特定の「CCA-F 専用コース一覧」を公式に固定しているわけではありませんが、公式のコースカタログはレベル100（基礎）/ 200（中級）/ 300（上級）に分かれています。

出題範囲（Claude Code / Claude Agent SDK / Claude API / MCP）に対応する主なコースを抜粋します。全コースは [anthropic.skilljar.com](https://anthropic.skilljar.com) で確認できます。

### レベル100（基礎）

### レベル200（中級）

### レベル300（上級）

（Amazon Bedrock 版 / Google Cloud Vertex AI 版もあります。これらは Claude API コースの内容を各クラウド向けにしたもので、利用環境に合わせて選べる選択肢です。）

なお **AI Fluency: Framework & Foundations / Claude 101 / Building with the Claude API（前半）** は、特定の試験ドメインに紐づくというより、全ドメインに共通する「土台」です。下の図3のドメイン対応マップには出てきませんが、#2 の基礎編でまとめて扱います。

![図3: 学習リソースマップ](https://static.zenn.studio/user-upload/deployed-images/206282454d52449d259062ee.png?sha=eba8680b4deb685eeb65c95194ca1c4750294890)  
*図3: 各ドメインに対応する主なコースのマップ（●=主要・○=補完）。下段は全ドメインの土台となる基礎コース（#2 基礎編で扱う）。対応づけは筆者の整理です。*

## 学習の進め方

### ループの設計

各回の学習は次のループを意識しています。

1. **その回のテーマを把握する** — Academy コースを流し読みし、何を学ぶか・何を問われるかを押さえる
2. **手を動かす** — コードを書いて動かす。動いた事実を記録する
3. **曖昧な点を残す** — わからなかったこと・迷ったことをそのまま書く（わかったふりをしない）
4. **理解度トラッカーを更新する** — 各回の末尾に理解度を記録する

### Anthropic Academy への登録手順

学習サイト（Anthropic Academy）のコースは、パートナーでなくても誰でも無料で登録・受講できます（受験そのものは前述のとおりパートナー経由が基本です）。

1. <https://anthropic.skilljar.com> にアクセスする
2. 「Sign In」または「Create Account」からアカウントを作成する
3. 検索ボックスでコース名（例：「Claude Code in Action」「Model Context Protocol」）を入力して探す
4. 「Enroll」「Start Course」など（ボタン名は画面により異なります）でコースに参加する（無料）
5. 動画・テキスト・小テストを順に進める

コース自体は無料で公開されています。アカウント作成に費用はかかりません。

## 本連載の進め方（予定）

回数はあらかじめ固定しません。まず基礎を固め、そのあと試験ドメインを1つずつ深掘りし、学習の進み具合に応じて回を増減・分割していきます。大まかな流れは次のとおりです。

| 回 | テーマ | 主に参照する Academy コース |
| --- | --- | --- |
| #1（本記事） | 概要と学習リソースの地図 | 全体マップ |
| #2 | **基礎編** — レベル100 の基礎コースを一通り整理する | AI Fluency / Claude 101 / Building with the Claude API（前半） |
| #3 以降 | 試験ドメインを順に深掘り（エージェント設計・オーケストレーション → Claude Code の構成 → プロンプト・構造化出力 → ツール設計・MCP → コンテキスト管理・信頼性 …） | 各ドメインに対応するコース |
| 最終回 | 模試・受験記録・振り返り | 全体の総復習 |

試験範囲だけを追うのではなく、まず #2 で土台（基礎コース）を固めてから各ドメインに入ります。ドメイン別の回は、手応えに応じて1つのドメインを複数回に分けたり、補足回を足したりすることがあります。

![図4: 本連載の流れ](https://static.zenn.studio/user-upload/deployed-images/10f9099590d234f809a67008.png?sha=4a69fd68b65a8253ebe636c7a5d4c12e18805b86)  
*図4: 本連載の流れ。#1 概要 → #2 基礎編 → #3 以降でドメイン別に深掘り（回数は可変） → 最終回に総括。*

## 理解度トラッカー

各回の末尾で、下の図のような「ドメイン別の理解度（5段階）」を自己評価して更新していきます（1=全くわからない、5=説明できる）。#1 はこれから学び始める段階なので、本格的な記録は #2 以降で行います。

![図5: 理解度トラッカー見本](https://static.zenn.studio/user-upload/deployed-images/75f2fe4cd15fa39c0624ac42.png?sha=08080f98b86026102b5da069ea0699cee2ebc7e5)  
*図5: ドメイン別理解度トラッカーの表形式イメージ。各回末尾で更新する。*

## 次回へのつなぎ：Messages API の最小呼び出し

#2 以降では実際にコードを動かします。準備として、Claude Messages API の最小呼び出し例を示します。

```
import anthropic

client = anthropic.Anthropic()  # 環境変数 ANTHROPIC_API_KEY を参照

message = client.messages.create(
    model="claude-sonnet-4-6",  # 最新のモデルIDは公式ドキュメントで確認
    max_tokens=256,
    messages=[
        {"role": "user", "content": "こんにちは。一文で自己紹介してください。"}
    ]
)

print(message.content[0].text)
```

必要なもの：

環境変数の設定例：

```
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."
```

```
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

レスポンスのテキストは `message.content`（リスト）の先頭要素に入るため、`content[0].text` で取り出します。このコードが動く環境を準備しておくと、#2 以降のハンズオンにそのまま使えます。設定でつまずいたら公式の [API スタートガイド](https://docs.anthropic.com/ja/api/getting-started) も参照してください。

## まとめ

この記事で整理したことをまとめます。

* CCA-F は Anthropic が 2026年3月12日に発表した技術認定試験。Claude Code / Agent SDK / Claude API / MCP を横断して問う。受験は Claude Partner Network（Partner Portal）経由で、現在は Early Adopter 段階。
* 認定は Anthropic Partner Academy の試験で取得し**個人に帰属**、**直近90日の Claude 利用**が条件。2026年3月以降、パートナー企業のコンサルタント1万人超が Claude 認定を取得済み。
* 出題ドメインは5つ（Agentic 27% / Claude Code 20% / Prompt 20% / Tool・MCP 18% / Context 15%）・多肢選択シナリオ形式・合格720点が大枠として共有されている。詳しい要項は機密の公式試験ガイド（**Confidential NTK**）側で、問題数・時間・費用などは公開ページに掲載がない。
* 学習リソースは無料の Anthropic Academy（レベル100〜300）。本連載は #2 で基礎を固め、#3 以降でドメイン別に手を動かし、最終回で受験記録を書く予定（回数は固定しません）。

## 次回予告

**#2「基礎編 — レベル100 の基礎コースを一通り整理する」**

参照する Academy コース: AI Fluency: Framework & Foundations / Claude 101 / Building with the Claude API（前半）

Claude の基本機能や効果的・安全な使い方、Claude API の最小実装（認証・基本プロンプト・簡単な評価）を、手を動かしながら整理します。試験範囲に入る前に、まず土台を固める回です。
