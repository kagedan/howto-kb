---
id: "2026-04-24-claude-designで大学院生が自分のポートフォリオを1時間で作った話-01"
title: "Claude Designで大学院生が自分のポートフォリオを1時間で作った話"
url: "https://zenn.dev/kk_data13/articles/claude-design-portfolio"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "Gemini", "zenn"]
date_published: "2026-04-24"
date_collected: "2026-04-25"
summary_by: "auto-rss"
query: ""
---

## この記事の要約

## はじめに

こんにちは、[KK (@KK\_Data3)](https://x.com/KK_Data3)です。慶應義塾大学大学院で統計・機械学習・NLPを専攻している修士1年で、将来はデータサイエンティストを目指しています。

先日Zennで自己紹介記事を書いたのですが、「**X・Zenn・GitHubがバラバラに散らばっている状況、ハブになるサイトがあった方が便利だな**」と思ったのがきっかけでした。

ただ、ポートフォリオサイトをゼロから設計する時間も、デザインにこだわるスキルもない。そこで話題の **Claude Design** を試してみたところ、**想像の10倍のクオリティ**で完成してしまったので、詳細を公開します。

## 使ったツール

| ツール | 用途 | コスト |
| --- | --- | --- |
| Claude Design (Anthropic Labs) | プロトタイプ・コード生成 | Claude Pro/Maxに付帯 |
| GitHub | ソース管理 | 無料 |
| Cloudflare Pages | ホスティング | 無料 |

**合計コスト: Claude Proのサブスク代のみ**。新規で課金したものはゼロです。

## Step 1: Zenn自己紹介記事をベースにプロンプト設計

まず材料となるプロフィール情報を整理しました。すでにZennの自己紹介記事があったので、そこから以下の要素を抽出しました。

* 所属・専攻
* 研究テーマ（学部・大学院）
* インターン経験
* 個人プロジェクト3つ
* 資格
* SNSアカウント（X / Zenn / GitHub）

次に、**デザイン方針**と**構成**を決めてから一気にプロンプトに落とします。

**デザイン方針**

* ダークネイビー × パープル→ブルーグラデ
* グラスモルフィズム・wireframe accent
* Inter + Noto Sans JP のフォント組み合わせ
* 「研究室のサイト」のような知的で落ち着いた雰囲気

**セクション構成（Hero → Footerまで6セクション）**

1. Hero
2. About
3. Projects（Bento Grid）
4. Experience & Research
5. Connect（Contact + Links統合）
6. Footer

### 投入したプロンプト（一部抜粋）

```
Build a personal portfolio / hub site for "KK" (@KK_Data3), a graduate 
student aspiring to become a data scientist.

DESIGN SYSTEM:
- Dark navy (#0A0E1A) to near-black background
- Purple-to-blue gradient accents (#8B5CF6 → #3B82F6)
- Glassmorphism, soft glows, thin wireframe accents
- Inter + Noto Sans JP typography
- Mood: precise, intelligent, academic aesthetic
- Think: personal site of a researcher at a top lab

TONE & STYLE:
- Academic, understated, professional
- DO NOT use emojis anywhere in the copy

PERSONA:
- Name: KK
- Handle: @KK_Data3
- Title: Aspiring data scientist & AI builder
- Affiliation: Keio University, Graduate School of Science 
  and Engineering, M1
- Focus: Statistics / ML / NLP / LLM agent development

STRUCTURE: 6 sections in exactly this order.

1. HERO
- English tagline: "Aspiring data scientist. Building with AI every day."
- JP subtitle: "データサイエンティストを目指す大学院生。"
- Primary CTA: "View my work"
- Secondary CTA: "Follow on X"

（以下、各セクションの詳細指示が続く...）
```

ポイントは\*\*「色コードまで具体的に指定する」「トーン指示を明文化する」\*\*こと。これをやると一発目のクオリティが爆上がりします。

## Step 2: Claude Designに投入、一発生成

プロンプトを投入して待つこと約1分。

出力された時点で**完成度が9割**でした。

![Heroセクション - プロンプト一本でこのクオリティ](https://static.zenn.studio/user-upload/deployed-images/40ef5b3f5d010bfa19af4b32.png?sha=26d4c6da250b4cc6ade71cf5cf58338f6e692166)

特に驚いたのが、Heroセクションに自動で生成された**データパイプライン風のHUDビジュアル**。プロンプトで明示していなかった`SCENE_01 · INGEST` `input → embed → infer → agent.run()` といった要素まで自発的に配置してくれました。

## Step 3: 等身大のトーンに微調整

初回出力ではやや**専門家風**なトーンだったため、「学生として学びながら発信する」ポジションに寄せる調整を入れました。

### 調整した点

* 右上バッジ: `available for collabs` → `student · learning in public`
* Connect本文: 「コラボ・メンタリング・登壇・執筆のご依頼」→ 「一緒に学んだり情報交換できたら嬉しい」
* プロジェクト説明: 技術スタック羅列 → 「何が嬉しいか」ベースの平易な説明
* カード下部の `inquire →` / `personal project` タグを削除（受託感排除）

## Step 4: アバター画像を差し替え

アバターはXやZennで使用しているサッカーとパソコンが大好きな自分に差し替えました。

Claude Designに「円形」→「縦長ポートレートの角丸カード」に変更する指示を出し、フレームもイラストに合わせて再設計。ダーク×テックな全体デザインに対して温かい水彩イラストが入るギャップが、逆に**個性のあるポートフォリオ感**を演出してくれました。

![Aboutセクション - ジブリ風アバターが溶け込む](https://static.zenn.studio/user-upload/deployed-images/35fef4215c78c5d79205f11b.png?sha=5c2be171f3ef14e8ebfc3c395ce312720d24267e)

### 他のセクションもこんな仕上がりに

プロジェクト紹介はBento Gridで、個人開発3つをコンパクトに紹介。

![Projectsセクション - Bento Gridで個人プロジェクトを紹介](https://static.zenn.studio/user-upload/deployed-images/cb729323290ec4cadcdb0209.png?sha=c63a64ba4e66ede00f4e5600ce574bd7941d24c0)

Experience & Researchは研究・インターン・資格をミニマルなタイムライン形式に。

![Experienceセクション - 研究とインターンの歩み](https://static.zenn.studio/user-upload/deployed-images/8d6220c40b551ecda2370129.png?sha=a93e429465d19b187587a112afc87ab4f6ce80ea)

## Step 5: スタンドアロンHTMLとしてエクスポート

Claude Designには\*\*「Save as standalone HTML」**機能があり、画像・CSS・フォントを**1ファイルに全部埋め込んだindex.html\*\*として書き出せます。

```
✅ CSS インライン化
✅ アバター画像をbase64で埋め込み
✅ フォントもインライン化
✅ 1ファイルでオフラインでも動作
```

ダウンロードして、ローカルで動作確認。

```
cd /Users/kokiakimoto/dev/projects/kk-data3-site
open index.html
```

ここでひとつ落とし穴がありました。**エクスポートされたファイル名が `KK Personal Site.html` だったこと**。Cloudflare Pagesはトップページとして `index.html` を探すので、**リネームが必要**です。

```
mv "KK Personal Site.html" index.html
```

## Step 6: GitHubリポジトリを作成してpush

後で更新しやすいようにGitHub連携を選択しました。

### リポジトリ作成

GitHubで新規リポジトリ `kk-data3-site` を作成（Public・MIT License）。

### ローカルからpush

```
cd /Users/kokiakimoto/dev/projects/kk-data3-site

git init
git branch -M main
git remote add origin https://github.com/kkkka16/kk-data3-site.git

git add index.html
git commit -m "Initial deploy: KK Data3 personal site"
git push -u origin main
```

READMEを先に作成していた場合は先にpullが必要です。

```
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## Step 7: Cloudflare Pagesにデプロイ

ここで**最大のハマりポイント**がありました。

### 詰まりポイント: Workersフローに入ってしまう罠

Cloudflareダッシュボードから `Workers & Pages` → `Create application` と進むと、**デフォルトで Worker プロジェクトとしてのフロー**に入ってしまいます。

* 画面左上に「**Create a Worker**」と表示
* デプロイコマンド欄に **`npx wrangler deploy`** が初期入力されている

これは**静的サイト向けのPagesフロー**ではありません。そのままDeployしても動きません。

### 正しいPagesフローへの入り方

画面中央〜下部にある以下のリンクから入る必要があります。

```
Looking to deploy Pages? Get started →
```

これをクリックすると、**Pages専用のフロー**に切り替わります。

```
Get started with Pages. How would you like to begin?

[Import an existing Git repository]   ← GitHub連携
[Drag and drop your files]            ← 直接アップロード
```

今回はGitHubにpush済みなので **「Import an existing Git repository」** を選択。

### ビルド設定

静的HTML単体なのでビルドは不要。以下のように設定します。

| 項目 | 値 |
| --- | --- |
| Project name | `kk-data3-site` |
| Production branch | `main` |
| Framework preset | **None** |
| Build command | **空** |
| Build output directory | `/` or 空 |

「Save and Deploy」を押すと、**数十秒で完了**。

![Cloudflare Pagesデプロイ成功 - Region: Earth](https://static.zenn.studio/user-upload/deployed-images/fcacc3667e26bbe831e7e6a4.png?sha=3c6ae472bb64c6dcf03c79c0575b0b4a21dd3fa4)

```
✅ Success! Your project is deployed to Region: Earth
https://kk-data3-site.pages.dev
```

## かかった時間とコスト

### 時間の内訳

| フェーズ | 時間 |
| --- | --- |
| プロンプト設計 | 10分 |
| Claude Design で初回生成 & 調整 | 20分 |
| アバター画像生成・差し込み | 10分 |
| HTMLエクスポート & ローカル確認 | 5分 |
| GitHubリポジトリ作成 & push | 10分 |
| Cloudflare Pages デプロイ（詰まり含む） | 15分 |
| **合計** | **約70分** |

### コストの内訳

| 項目 | 月額 |
| --- | --- |
| Claude Pro（元から契約） | $20/月 |
| Gemini | 無料枠内 |
| GitHub | 無料 |
| Cloudflare Pages | 無料 |
| **追加コスト** | **0円** |

独自ドメイン（`kk-data3.dev` 等）を取得する場合、Cloudflare Registrarで**年2,000円程度**。

## 学んだこと・所感

### 1. プロンプト設計 = デザインディレクション

Claude Designの出力クオリティは、**プロンプトの具体性に比例**します。色コード、フォント、雰囲気（「研究室のサイトのような」）まで言語化すると、一発目から9割の完成度が出ます。

### 2. 「トーン」の調整がAIと人間の協働ポイント

初期出力は`available for collabs`のように**専門家風**になりがちです。これを「学生として」「等身大で」といったポジションに**言葉で寄せていく**作業は、今もなお人間の判断が光る部分だと感じました。

### 3. Claude Designの出力、プロダクション品質

正直、**プロに外注したレベル**の出力が出ます。一発生成したHeroのHUDビジュアルは、自分では絶対に思いつかなかった表現でした。

### 4. Cloudflareの新UIは罠がある

「Create application」がWorker中心になっている設計は、\*\*静的サイトを作りたい初見ユーザーにとってはわかりにくく感じました。\*\*Pagesに入るには `Looking to deploy Pages?` のリンクを辿る必要があります。

## まとめ

個人ポートフォリオを持っていないエンジニア・大学院生の方は、Claude Proに加入しているなら**今夜試してみる価値**があります。
