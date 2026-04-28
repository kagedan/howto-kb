---
id: "2026-04-27-フォームサービス選定チェックリスト-google-forms-microsoft-forms-tal-01"
title: "フォームサービス選定チェックリスト: Google Forms / Microsoft Forms / Tally / Jotform / SurveyMonkey / FORMLOVA"
url: "https://qiita.com/lovanaut/items/0a0a7a64018c2b1c174b"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "GPT", "qiita"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

<!--
SEO implementation memo:
Primary keyword: フォームサービス 選定
Secondary keywords: フォームサービス 比較, Google Forms 代替, Microsoft Forms 制限, Tally MCP, Jotform MCP, SurveyMonkey 代替, AIフォームビルダー
Search intent: フォームサービスを比較検討している実務者が、無料枠、回答上限、公開後運用、AI/MCP対応を漏れなく確認したい。
Reader problem: 作成画面や料金だけで選ぶと、回答数上限、自動返信、リマインド、営業メール分類、権限、外部連携で後から詰まる。
What this article must answer: 要件整理テンプレート、比較時のチェック項目、用途別の選び方、MCP対応を見るときの注意点、導入前のテスト手順。
CTA role: Qiitaでは実務チェックリストを主役にし、詳細比較は自社ブログへ送る。
Internal link role: comparison-form-services, microsoft-forms-limitations, surveymonkey/tally/jotform comparison, ai-form-builder-mcp-form-serviceへの入口。
-->


![061-qiita-form-service-selection-checklist.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4385658/a9dec8ba-1a6e-4ee8-8c35-03b27ebb5b3e.png)


<!-- IMAGE: Hero / Eyecatch -- topics/blog/external/assets/061-qiita-form-service-selection-checklist.png -- alt: フォームサービス選定で見るべき回答上限、公開後運用、MCP対応、分析のチェックリスト図。 -->

フォームサービスを選ぶとき、最初に見がちなのは以下です。

- 無料で使えるか
- フォームが作りやすいか
- デザインが良いか
- テンプレートが多いか
- 有名サービスか

もちろん大事です。

ただ、問い合わせフォーム、セミナー申込、採用エントリー、資料請求、顧客アンケートのように、回答後の対応がある用途では、これだけだと足りません。

本番で困るのは、フォームを作る瞬間ではなく、公開した後です。

回答が何件まで見られるのか。自動返信は送れるのか。リマインドは出せるのか。営業メールを除外できるのか。未対応・対応済みのステータスを持てるのか。ChatGPTやClaudeから操作したい場合、MCPでどこまで扱えるのか。

この記事では、フォームサービス選定時に確認すべき項目を、実務チェックリストとしてまとめます。

詳細な横断比較は公式ブログ側にまとめています。

[FORMLOVAと主要フォームサービスの違い](https://formlova.com/ja/blog/comparison-form-services)

## 1. まず要件を文章にする

フォームサービス比較で失敗しやすいのは、サービス一覧から見始めることです。

Google Forms、Microsoft Forms、Tally、Jotform、SurveyMonkey、Typeform、formrun、FORMLOVAは、同じ「フォームサービス」でも中心にしている仕事が違います。

先に要件を書いたほうが判断しやすいです。

```text
用途:
  - 問い合わせ受付
  - セミナー申込
  - 採用エントリー
  - 顧客アンケート
  - 社内アンケート

想定回答数:
  - 月10件
  - 月100件
  - 月1,000件
  - キャンペーン時だけ急増

回答後の作業:
  - 自動返信
  - 担当者通知
  - リマインド
  - 営業メール/スパム除外
  - ステータス管理
  - 分析
  - PDF/CSV/Sheets出力

AI/MCP:
  - AIでフォームを作りたい
  - AIで回答を要約したい
  - AIでメール設定まで変えたい
  - ChatGPT / Claude / Cursor から操作したい
```

この時点で、候補はかなり絞れます。

社内の簡単なアンケートなら、Microsoft FormsやGoogle Formsで十分なことが多いです。無料で綺麗なフォームを素早く作るならTallyが強いです。テンプレート、決済、署名、PDFなど周辺機能まで欲しいならJotformが候補になります。調査・アンケート分析ならSurveyMonkeyが向いています。

一方で、問い合わせや申込のあとに対応フローが続く場合は、回答後の運用を重視したほうがよいです。

## 2. サービスごとの向き不向きを先に分ける

最初の比較では、細かい機能を全部見るより、中心用途を分けるのが実務的です。

| サービス | 向いている用途 | 最初に確認すること |
| --- | --- | --- |
| Google Forms | 無料で簡単な受付、社内外の軽いアンケート | デザイン、権限、スプレッドシート運用、メール運用 |
| Microsoft Forms | Microsoft 365内の社内アンケート、教育、Teams連携 | 回答上限、外部共有、Power Automate前提の運用 |
| Tally | 無料で見た目のよいフォームを速く作る、AI/MCP作成 | 有料機能、チーム運用、公開後メール・分類の深さ |
| Jotform | テンプレート、決済、署名、PDF、アプリ的な使い方 | 無料枠、フォーム数、送信数、設定項目の多さ |
| SurveyMonkey | 顧客満足度、NPS、従業員調査、市場調査 | 無料プランで見られる回答数、分析機能、料金 |
| Typeform | 体験重視のフォーム、マーケティングフォーム | 月間回答数、ブランド削除、分析・連携の範囲 |
| formrun | 日本語の問い合わせ管理、CRM寄りの受付 | プラン別機能、チーム対応、外部連携 |
| FORMLOVA | 公開後の運用をチャット/MCPで進める | フォーム作成だけでなくメール、分類、分析まで必要か |

![061-qiita-selection-checklist-matrix.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4385658/3974d4ae-1b03-4944-8fd3-980e45b5046e.png)
<!-- IMAGE: Inline / Insert after the comparison in "2. サービスごとの向き不向きを先に分ける" -- topics/blog/external/assets/061-qiita-selection-checklist-matrix.png -- alt: Google Forms、Tally、Jotform、SurveyMonkey、FORMLOVAを選定観点で比較するマトリクス。 -->


ここで大事なのは、表の右端です。

「向いている用途」だけを見ると、どれも良さそうに見えます。選定時は、各サービスが苦手になりやすい領域を先に見ます。無料枠が小さいのか、公開後の運用が別ツール前提なのか、調査には強いが問い合わせ管理には重いのか、MCPで作成はできるがメール設定までは届かないのか。

この見方をすると、後から「思っていたのと違う」が減ります。

## 3. 回答数と閲覧制限を確認する

無料プランを見るときは、「フォームを作れるか」ではなく「集まった回答をどこまで扱えるか」を確認します。

```text
[ ] 月間回答数に上限があるか
[ ] 上限超過時に回答の受付が止まるか
[ ] 上限超過時に回答を閲覧できるか
[ ] CSV/Excel/Sheets出力に制限があるか
[ ] 添付ファイルの容量や保存先に制限があるか
[ ] フォーム数、質問数、メンバー数に制限があるか
```

たとえば、Typeformの料金ページではBasicプランに月100回答、Plusに月1,000回答、Businessに月10,000回答といった回答数の目安が示されています。JotformやSurveyMonkeyも無料枠や回答閲覧に制約があります。

一方で、Tallyは無料プランの範囲が広く、無料でフォーム数・回答数を広く使える点が強みです。Google Formsも無料で始めやすいですが、Googleアカウント、Drive、スプレッドシート、ファイルアップロード、組織の共有設定など、周辺の制約を確認する必要があります。

Microsoft FormsはMicrosoft 365環境では自然な選択肢ですが、フォーム・質問・回答・文字数などに公式の上限があります。社内アンケート程度なら問題になりにくい一方、キャンペーンや外部受付で大量回答を想定する場合は、事前に上限を見ます。

ポイントは、テストフォームではなく本番のピーク件数で考えることです。

普段は月20件でも、ウェビナー告知、キャンペーン、採用募集、資料配布で一時的に増えることがあります。フォームは一度公開するとURLが外に出るため、あとからサービスを差し替えるコストもあります。

## 4. 公開後の運用をチェックする

フォームを選ぶとき、作成画面だけ見ていると抜けやすいのが公開後の運用です。

```text
[ ] 回答者へ自動返信メールを送れるか
[ ] 自動返信の件名・本文・差し込み変数を変更できるか
[ ] 条件付きメールを送れるか
[ ] リマインドメールを送れるか
[ ] 回答ステータスを管理できるか
[ ] 担当者やチームに通知できるか
[ ] 営業メールやスパムを分類できるか
[ ] 回答を分析できるか
[ ] PDFレポートやCSVを出せるか
[ ] Google SheetsやCRMへ連携できるか
```

セミナー申込フォームを例にします。

作るだけなら、名前、会社名、メールアドレス、参加希望日、同意チェックボックスを並べれば終わりです。

しかし、本番運用では次が必要になります。

- 申込直後に確認メールを送る
- 開催前日にリマインドを送る
- キャンセルや重複申込を確認する
- 当日の参加者リストを作る
- 欠席者へアーカイブ案内を送る
- 終了後アンケートを集める
- ホットリードを営業へ渡す

問い合わせフォームなら、営業メールの除外、担当者通知、未対応・対応済みのステータス、返信漏れ確認が出てきます。

採用フォームなら、応募受付、書類確認、面接案内、選考ステータス、個人情報の管理が必要です。

このあたりをフォームサービス内で扱えるのか、Zapier/Make/Power Automate/スプレッドシート/CRMへ逃がすのかで、運用設計は変わります。

## 5. MCP対応は「作成」「回答」「運用」で分ける

AIチャットからフォームを操作したい場合は、MCP対応を見ます。

ただし、「公式MCPがある」だけでは不十分です。何をtool化しているかを分けて確認します。

```text
[ ] 公式MCPサーバーか
[ ] OAuthなどの認証方式が明確か
[ ] フォーム作成ができるか
[ ] 既存フォームの編集ができるか
[ ] 回答一覧を取得できるか
[ ] 回答詳細を取得できるか
[ ] 回答ステータスを変更できるか
[ ] 自動返信やリマインド設定を変更できるか
[ ] 分析やレポートを取得できるか
[ ] write操作に承認フローを入れられるか
```

Tallyは公式にMCP対応を出しており、フォーム作成、編集、ワークスペース閲覧、回答取得・分析などを扱えます。無料フォーム作成とAIからの操作を組み合わせたい場合に強いです。

Jotformも公式MCPを提供しており、フォーム一覧、作成、編集、送信作成、送信取得などが公開されています。さらにMCP-Appとして、チャット内でフォームのライブプレビューや送信データのテーブル表示を行う方向も示されています。

FORMLOVAは、フォーム作成だけではなく、回答管理、自動返信、リマインド、条件付きメール、営業メール分類、分析、A/Bテスト、Google Sheets連携、チーム管理など、公開後の運用をMCPに載せる設計です。

Google Forms、Microsoft Forms、SurveyMonkey、formrunについては、2026年4月27日時点でフォームサービス単体の公式MCPサーバーは確認できませんでした。APIや外部自動化ツール経由で近いことはできますが、公式MCPとしてAIクライアントから直接扱う話とは分けて考えたほうがよいです。

## 6. 選定時のテスト手順

候補を2つか3つに絞ったら、同じテストを流します。

```text
1. セミナー申込フォームを作る
2. スマホで入力する
3. テスト回答を20件入れる
4. 自動返信を確認する
5. CSV/Sheets出力を確認する
6. 未対応/対応済みを管理できるか見る
7. リマインドを送る想定で設定を見る
8. 営業メールっぽい回答を混ぜて分類方法を見る
9. 担当者へ通知する方法を見る
10. AI/MCPから同じ作業がどこまでできるか確認する
```

このテストをやると、作成画面だけでは見えない差が出ます。

特に見るべきなのは、手戻りの多さです。フォーム項目の修正、自動返信の変更、回答一覧の確認、CSV出力、担当者通知、メール送信前確認。このあたりを毎回別画面で探す必要があると、運用担当者の負荷は増えます。

また、MCPを使う場合は、read操作から始めるのが安全です。

まずは回答の要約、未対応回答の抽出、営業メール候補の分類、回答傾向の分析から試します。フォーム変更、メール送信、データ削除のようなwrite操作は、承認フローを入れられるか確認してから本番に入れます。

## 7. 用途別の結論

ざっくり用途別に選ぶなら、以下です。

| 用途 | 最初に見る候補 | 理由 |
| --- | --- | --- |
| とにかく無料で簡単に作る | Google Forms / Tally | 始めやすく、学習コストが低い |
| Microsoft 365内の社内アンケート | Microsoft Forms | Teams、Excel、組織アカウントとの距離が近い |
| 見た目や入力体験を重視する | Typeform / Tally | 体験やデザインの印象を作りやすい |
| 決済、署名、PDF、テンプレートまで欲しい | Jotform | フォーム周辺機能が広い |
| 調査・NPS・市場調査をしたい | SurveyMonkey | アンケート分析や調査用途に強い |
| 日本語の問い合わせ管理をしたい | formrun | 問い合わせ受付・管理の文脈に強い |
| 公開後の運用をAI/MCPで進めたい | FORMLOVA | 作成後のメール、分類、分析、ワークフローまで見る |

「無料かどうか」だけで決めるなら、Google FormsやTallyが候補になりやすいです。

「アンケート結果を分析したい」ならSurveyMonkeyが自然です。

「フォームをアプリ的に使いたい」ならJotformが強いです。

「回答後の対応が重い」なら、公開後運用まで含めて選びます。

## まとめ

フォームサービス選定では、作成画面だけ見ないほうがよいです。

本番で困るのは、だいたい公開後です。

- 回答数と閲覧制限
- 自動返信
- リマインド
- 回答ステータス
- 営業メール/スパム分類
- 分析
- CSV/Sheets/CRM連携
- MCP対応の深さ
- write操作の承認

このあたりを先に確認すると、用途に合った選択がしやすくなります。

フォームは入力画面ではなく、外部から届いた意思表示を次の仕事へ渡す入口です。選定時も、作る前ではなく、回答が届いた後から逆算するのが良いと思います。

## 参考

- [FORMLOVAと主要フォームサービスの違い](https://formlova.com/ja/blog/comparison-form-services)
- [Microsoft Formsの制限と代替](https://formlova.com/ja/blog/microsoft-forms-limitations-alternatives)
- [SurveyMonkeyとFORMLOVAを比較](https://formlova.com/ja/blog/surveymonkey-alternative-formlova-comparison)
- [TallyとFORMLOVAを比較](https://formlova.com/ja/blog/tally-alternative-formlova-comparison)
- [Jotform代替ならFORMLOVA？](https://formlova.com/ja/blog/jotform-alternative-formlova-comparison)
- [AIフォームビルダーとMCPフォームサービスの違い](https://formlova.com/ja/blog/ai-form-builder-mcp-form-service)

公式情報:

- [Typeform Pricing](https://www.typeform.com/pricing/)
- [Jotform Pricing](https://www.jotform.com/pricing/)
- [SurveyMonkey response limits](https://help.surveymonkey.com/en/surveymonkey/billing/response-limits/)
- [Microsoft Forms limits](https://support.microsoft.com/en-us/office/form-question-response-and-character-limits-in-microsoft-forms-ec15323d-92a4-4c33-bf88-3fdb9e5b5fea)
- [Tally MCP guide](https://tally.so/help/best-mcp-form-builders)
- [Jotform MCP Server docs](https://www.jotform.com/developers/mcp/)
