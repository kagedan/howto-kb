---
id: "2026-05-16-claude-cowork-dispatch-のセットアップガイドqr-ペアリング廃止後の最新フロー-01"
title: "Claude Cowork Dispatch のセットアップガイド──QR ペアリング廃止後の最新フロー"
url: "https://zenn.dev/and_dot/articles/e42520784892a2"
source: "zenn"
category: "cowork"
tags: ["API", "AI-agent", "Gemini", "GPT", "cowork", "zenn"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは、アンドドット CTO の高根沢です。

Claude Cowork の **Dispatch** は、スマホ（Claude アプリ）から Mac 上の Cowork セッションに指示を送り、ローカル環境でタスクを実行させる機能です。  
※リリース当初は QR ペアリングが必要でしたが、現在は **設定のトグル1つで両端末がリンクされる** 仕様に変わっています。  
本記事では、最新フローでのセットアップ手順と、外出先からスライドの作成を発注した実例などをご紹介します。

なお、Dispatch で生成した PPTX/Excel などのバイナリ成果物をスマホで受け取りたい場合は、Google Drive デスクトップ版を併用することをお勧めしています（現状コネクタ経由の Google Drive アップロードが安定しないため）。そちらは別記事にまとめていますので、こちらもぜひご覧ください！

→ [Claude Dispatch で生成ファイルをスマホで見るなら、Google Drive デスクトップ版を入れること(Mac)](https://zenn.dev/and_dot/articles/c8f3a2d5e1b047)

## Dispatchの対応プラン・利用するための前提条件

はじめに、プランごとの利用可否について触れておきます。

| プラン | 利用可否 | 備考 |
| --- | --- | --- |
| Free | 不可 |  |
| Pro | 可 |  |
| Max | 可 |  |
| Team | 可 | 管理者が組織設定で有効化する必要あり |
| Enterprise | 可 | 管理者が組織設定で有効化する必要あり |

リリース当初Team プランでは未対応でしたが、2026年3月25日から利用できるようになっています。  
組織管理者が Cowork の組織設定画面で「ディスパッチを有効化」トグルをオンにすることで、使用できるようになりました。

![Cowork組織設定画面。「ディスパッチを有効化」トグルがオンになっている状態。同画面では「コード権限」やOpenTelemetry連携も管理できる](https://static.zenn.studio/user-upload/deployed-images/969326745c4923ea9efab7c5.png?sha=5ecba313e05b5f8a1584da647b2f7f0028ccdf13)  
*Cowork の組織設定画面。「組織で有効にする」に加えて「ディスパッチを有効化」を別途オンにする必要がある。管理画面に項目が見当たらない場合は管理者側の有効化待ちの可能性が高い*

また、Dispatchを利用するためには、まず以下の前提条件がクリアになっているか確認しておきましょう。

* Claude Desktop（Mac / Windows x64）が最新版
* Claude モバイルアプリ（iOS / Android）が最新版、Mac と**同じアカウントでサインイン済み**
* **Mac がスリープしていないこと**（スリープ中は Dispatch が動かない）

## Dispatch 最新セットアップ手順

### 1. Mac の設定で Dispatch をオンにする

まずは、Claudeアプリの設定 → Cowork と進み、Cowork内の「Dispatch」のトグルをオンにします。  
以前は QR コードを使ったペアリングが必要でしたが、現在は同じアカウントでサインインしていれば**トグル1つで両端末がリンクされる**仕様に変わっています。

![Claude Desktop の設定画面。「Cowork（プレビュー）」セクション内の「Dispatch」トグルが青色のオン状態。説明文には「スマートフォンからこのコンピュータを使ってClaudeにタスクを指示できます。オフにすると、スマートフォンからこのコンピュータに作業を指示できなくなります」と表示](https://static.zenn.studio/user-upload/deployed-images/3151dc94ad61cffbb2e5421a.png?sha=1ef70069f57f91fb2f4b104bae3147b2f7360446)  
*Dispatch のオン/オフはここ1箇所のみ*

### 2. サイドバーに Dispatch が出ていることを確認する

オンにすると、Mac 側の Claude Desktop には左サイドバーに「Dispatch」項目が追加され、同じアカウントでサインイン済みのスマホアプリ側にも自動的に Dispatch メニューが現れます。

![Claude Desktop の左サイドバーに「Dispatch」項目が追加された状態。右ペインには「Claudeにタスクを指示して、スマートフォンやコンピューターから確認できます。すべてシームレスな会話の中で完結します。」の説明と、「スリープしない」トグル（オン）「すべてのブラウザアクションを許可」トグルが表示](https://static.zenn.studio/user-upload/deployed-images/96974a082e98c3a81894d722.png?sha=efd9ba376d96df18d48537e50f2c2f2efb95eec5)  
*有効化後の Dispatch ホーム。スマホ側も追加操作なしでメニューが出てくる*

### 3. 権限を設定する

初回セットアップでは以下 4項目の権限が確認されます。  
すべてオンにしておかないと、外出先から指示を送っても期待通りに動かないので注意しましょう。

![Dispatchの「指示の準備」権限設定画面。ファイルへのアクセス許可、スリープしない、ChromeでのClaude動作、コネクタ利用の4項目が一覧されている](https://static.zenn.studio/user-upload/deployed-images/482b5fc67f361e03fdfdb410.png?sha=990b97a4a627dce4ce7e35f498ff4602d48e500b)  
*権限設定の 4 項目。とくに「このコンピュータをスリープさせない」はオンにしないと外出先では動かない*

| 設定項目 | 役割 | 推奨 |
| --- | --- | --- |
| Claudeにファイルへのアクセスを許可 | ローカルのファイル読み書き | オン |
| このコンピュータをスリープさせない | Dispatch実行中のスリープ抑止 | オン |
| ClaudeでChromeを使用する準備ができました | ブラウザ操作（閲覧・入力・クリック） | オン |
| すべてのコネクタがオンになっています | Gmail/Slack/Drive等の連携 | オン（必要なもののみ） |

## 実際に使ってみた！──外出中に CTO 向けのスライド作成を発注

実際に移動中の空き時間に、スマホからこのような指示を投げました。

> スライド作成したい。今週の最新AIニュースについて教えて

Claude は「用途と対象は？」「ボリューム感は？」と 2 点だけ確認してきます。「15 枚くらいで、CTO 経営向け資料として」と返すと、タスクとして起動しました。

![スマホのDispatch画面。ユーザーが「スライド作成したい。今週の最新AIニュースについて教えて」と投稿し、Claudeが用途と対象・ボリューム感を逆質問し、「15枚くらいで、CTO経営向け資料として」という指示で「AI news slides for CTO」タスクを起動した様子](https://static.zenn.studio/user-upload/deployed-images/5261ccf8d0d4bc5524239cc0.png?sha=b5633cafde2a7f12de786d7e0db10de9d8595c59)  
*スマホ側のやり取り。曖昧な指示でも Claude が逆質問で不足情報を埋めてから実行に入る*

さて同時刻、Mac 側の Cowork では同じスレッドでタスクが動いています。  
Web で最新 AI ニュースを調査 → 構成整理 → PPTX 生成、という流れをローカルで自律実行します。

![Mac 側 Claude Desktop の Cowork タブで、「AI news deck May 8 + Drive sync」タスクが進行中の画面。設定ペインの「スリープしない」「モバイル通知」がオン、出力ペインに Claude が共有したファイルのリスト、右側のチャット領域には Claude が「今日 (5/8) 時点の最新トピック」として GPT-5 Enterprise、Anthropic Sonnet 4.7、Gemini Personal Intelligence、Microsoft Agent SDK、ServiceNow×Accenture×NVIDIA、中国Qwenなどを箇条書きで整理している様子（左サイドバーのチャット履歴はモザイク処理）](https://static.zenn.studio/user-upload/deployed-images/a77455bd49445db7a404cc1c.png?sha=128459e4cd8803d1587527e7f7b5c38830b292b0)  
*Mac 側でタスクが進行中。同じスレッドがスマホと Mac で共有されるため、Mac に戻ってから会話の続きを入力することもできる。出力ペインには Claude が生成・参照したファイルのリストもまとまる*

帰社してからMac を開くと、指定通りの 15 枚構成の PPTX が出力されていました。  
**この「コネクタ連携済みの定型タスクをスマホから投げる」使い方が、Dispatch の最も使う頻度が多い用途です。**

ただし、生成された PPTX をスマホ側からそのまま開くには Drive Desktop を併用する必要があります。  
（詳しくは冒頭で記載した別記事にて記載していますのでご覧ください。）

## Dispatch と Managed Agents の使い分け

2026年4月8日に公開された **Managed Agents** についても触れておきたいと思います。  
Managed Agentsは、スケジュール実行やイベントトリガーでタスクを自律的に走らせる仕組みで、Dispatch と混同しやすいので注意が必要です。

|  | Dispatch | Managed Agents |
| --- | --- | --- |
| **起動方法** | スマホから手動で指示 | スケジュール or イベント |
| **実行環境** | ローカル Mac | クラウド |
| **コネクタ** | Mac 上の設定をそのまま利用 | API 経由で設定 |
| **用途** | アドホックなタスク指示 | 定期・自動タスク |

**筆者の使い分け:**  
私はこれらをこのような形で使い分けています。「定期はクラウドで自動、思いつきはスマホから投げて Mac で実行」という役割分担で、手元の作業時間を圧倒的に空けられるようになりました。

* 「毎朝の日報まとめ」「週次の進捗集約」などの定期タスク → **Managed Agents**
* 「今この議事録を要約して Slack に流して」「移動中にスライドを作らせる」など思いつきベース → **Dispatch**

## まとめ

Dispatch のセットアップは、QRペアリングが廃止後は **設定のトグル + 4 項目の権限確認**で完結するようになったりと、かなり手軽になりました。  
※Team/Enterprise だけは管理者の組織設定の有効化を最初に依頼する必要があるので忘れずに！

外出先から「スライドを作って」と投げて Mac が裏で動かしてくれる体験は、思考のキャッシュアウト先としてかなり強力です。  
ぜひご興味がある方は使ってみてください！

## 一緒に"爆速文化"をつくる仲間を募集しています

アンドドットでは、生成AIとともにプロダクトを創り上げ、少数精鋭で大きな成果を出す組織を目指しています。AI活用を前提とした新しい開発スタイルに興味のある方、ぜひ一度カジュアルにお話しましょう。

<https://calendar.google.com/calendar/appointments/schedules/AcZssZ2betA1myxHjAccbO6w6EEDYG6SGfdlymYyx2MJBIwHamQtmzI66cm7Da7aLiC4sYSbXv-CP846>
