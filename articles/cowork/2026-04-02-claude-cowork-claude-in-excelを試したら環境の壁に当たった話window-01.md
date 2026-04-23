---
id: "2026-04-02-claude-cowork-claude-in-excelを試したら環境の壁に当たった話window-01"
title: "Claude Cowork + Claude in Excelを試したら環境の壁に当たった話：Windows ユーザーへの動作確認ガイド"
url: "https://zenn.dev/hiroakikody/articles/45bcee8a37c76e"
source: "zenn"
category: "cowork"
tags: ["cowork", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

## はじめに

「プログラミング不要でデータ分析ができる」という触れ込みで、Anthropicが2026年1月にリリースしたClaude新機能「Cowork」と「Claude in Excel」。

筆者はナナカファームという農場を運営しながらAI・農業テックをテーマにZennで発信している。「農業データを自然言語で分析できるなら、たとえば積算気温から桜の開花予想をClaude任せで作れるのでは」と試してみた。

**結論から言うと、手元のWindows環境では両方とも動かなかった。**

ただ、その原因を調べていくと「なぜ動かないか」が非常に明確で、かつ日本のWindowsユーザーにとって他人事ではない内容だとわかった。同じ壁に当たる前に確認してほしいポイントをまとめる。

---

## Claude Cowork・Claude in Excelとは

### Claude Cowork

通常のClaudeチャットは「質問→回答」の一問一答型だ。Coworkはこれを大きく超えた**エージェント型**の動作をする。

* フォルダへのアクセス権を付与すると、Claudeが自律的にファイルを読み書き・整理・作成する
* 複雑なタスクを複数ステップに分解して自動実行する
* **Excelファイル（VLOOKUPや条件付き書式つきの完成品）を生成できる**
* スケジュール実行（例：毎朝8時に前日データを自動集計）も可能

開発者向けの「Claude Code」と同じアーキテクチャを、ターミナル不要・コーディング不要で使えるようにしたものと理解するとわかりやすい。

### Claude in Excel × Claude Coworkでできること

#### 「Claude in Excel」とのシームレスな連携

Coworkで作った土台を、Excel上で直接動作する「Claude in Excel」で微調整する、強力なワークフローが実現します。

Coworkで自動生成: 散在する領収書やメモから、一気に集計Excelを作成。

Claude in Excelで仕上げ: 作成された表を見ながら、「この列の計算方法を少し変えて」「グラフを追加して」と対話形式で修正。

ポイント: ユーザーは一度もセルに関数を打ち込むことなく、高度な分析ファイルを手に入れることができます。

#### 実務を激変させる活用例

収穫・売上の自動集計: バラバラの記録ファイルを指定フォルダに入れるだけで、月次レポートが完成。

経費精算の自動化: レシート画像を読み取り、日付・金額・品目を整理した経費一覧表を作成。

定期的な自動更新: 「毎朝8時に前日のログを集計してExcelを更新する」といったスケジュール実行も可能です。

#### 導入のメリットと注意点

メリット: 「AI秘書」から、実際に手を動かす「AI実務担当者」へ進化。PCスキルの差による業務停滞が解消されます。

注意点: 本機能はClaude Desktop（有料プラン）が必要なリサーチプレビュー版です。実行には多くのトークンを消費するため、複雑な実務に特化して活用するのが効率的です。

### 今回やりたかったこと

```
① pydata-book（有名Pythonデータ分析教材）のサンプルCSVをCoworkで分析
② tips.csvをExcel形式で整形・グラフ化
③ 気象庁から熊本の気温CSVをダウンロード
④ 積算気温（2月1日起算・5℃超で加算）を計算し桜の開花予測Excelを作成
```

桜の開花予測に使う「積算気温法（DTS法）」は、日平均気温が5℃を超えた日の気温を2月1日から累積し、600℃に達した日を開花予測日とするモデルだ。農業における「農作業計画への積算気温活用」の応用例としてZennに書こうと思っていた。

---

## 動作環境の壁：詰まったポイント3つ

### 検証環境

| 項目 | 実際の値 |
| --- | --- |
| OS | Windows 10 Home 22H2 |
| CPU | Intel Core i5-1035G1 |
| RAM | 24 GB |
| ストレージ | 239 GB SSD（空き **4.27 GB**） |
| Office | Microsoft Office Personal **2019**（永続ライセンス） |

### 詰まりポイント① Windows 10 Home → Cowork 起動不可

Coworkを開こうとすると以下のエラーが表示された。

```
Claudeのワークスペースの起動に失敗しました
Not enough disk space to set up the workspace.
Free up space and try again.
```

原因を調べていくと、**ディスクの問題だけではなかった**。

CoworkはVM（仮想マシン）上で動作する。このVMの起動に**Hyper-V**（Windowsの仮想化技術）が必要なのだが、**Windows 10/11 のHomeエディションにはHyper-Vのフルスタックが搭載されていない**。

Anthropicの公式GitHubには、このことが明記されていないとして「ドキュメントの不備」として複数のIssueが立っている状況だ（2026年2月時点）。つまり**公式サイトに「Windowsに対応」と書いてあっても、HomeエディションではCoworkは動かない**。

> ✅ Coworkが使えるWindowsエディション：**Pro / Enterprise / Education**  
> ❌ 使えないエディション：**Home**（Windows 10・11 どちらも）

Windowsのエディション確認方法：

```
Windowsキー + R → winver と入力してEnter
```

### 詰まりポイント② ディスク空き 4GB → Cowork 起動不可

エディションの問題に加えて、ディスクの空き容量も基準に達していなかった。

Coworkが必要とする最低ディスク空き容量：**10 GB以上**（推奨20 GB+）

手元のPCは239 GB SSDのうち空きが**4.27 GB**しかなく、VMの展開領域が確保できずに即エラーとなった。

Windows 10 Homeのユーザーは、Officeのバックアップや古いWindowsアップデートのキャッシュで空き容量が少なくなっているケースが多い。ディスククリーンアップ（特に「システムファイルのクリーンアップ」→ Windowsアップデートの古いファイル）で数GB確保できることが多いが、Hyper-Vの問題があるため根本解決にはならない。

### 詰まりポイント③ Office 2019 永続ライセンス → Claude in Excel 利用不可

Coworkをあきらめ、Claude in Excelに切り替えようとした。しかしExcelのアカウント画面を確認すると「Microsoft Office Personal **2019**」の表示。

Claude in ExcelはMicrosoft MarketplaceのアドインとしてExcelに統合するのだが、**対応しているのはMicrosoft 365のサブスクリプション版のみ**で、2016・2019の永続ライセンス版は非対応と明記されている。

> 対応バージョン：
>
> * Excel on the web（office.com）
> * Windows：Microsoft 365（build 16.0.13127.20296以上）
> * Mac：バージョン 16.46以上
> * iPad：バージョン 2.51以上
>
> ❌ 非対応：Excel 2016 / 2019（永続・ボリュームライセンス）、Android

日本ではPCに「Office 2019」や「Office 2021」が最初からバンドルされているケースが多く、**買い切り版を使っているユーザーはClaude in Excelを使えない**。

---

## 動作要件チェックリスト（試す前に確認）

### Claude Cowork

| 確認項目 | 要件 | 確認方法 |
| --- | --- | --- |
| OS | macOS 11以上 / Windows 10(1909以上)・11 | Windowsキー+R → winver |
| Windowsエディション | **Pro / Enterprise / Education**（Homeは非対応） | 上記winverで確認 |
| CPU（macOS） | **Apple Silicon（M1以上）**（Intelは非対応） | Apple → このMacについて |
| ディスク空き | **10 GB以上**（推奨20 GB+） | エクスプローラー → PC |
| RAM | 8 GB以上（推奨16 GB） | タスクマネージャー |
| Claudeプラン | **Pro / Max / Team / Enterprise**（無料プランは不可） | claude.ai/settings |
| アプリ | Claude Desktop（最新版）が必要 | claude.com/download |

### Claude in Excel

| 確認項目 | 要件 |
| --- | --- |
| Excelバージョン | **Microsoft 365サブスクリプション版**（2016/2019永続は非対応） |
| 代替オプション | **Excel on the web（office.com）なら無料で試せる** |
| Claudeプラン | Pro / Max / Team / Enterprise |
| インストール | Microsoft Marketplace から「Claude by Anthropic」で検索 |

---

## 代替手段：Excel Online で試す

CoworkとローカルのExcelが使えなくても、**Excel Online（office.com）ならClaude in Excelが動作する**。

Microsoftアカウント（Hotmail・Outlookアドレスでも可）があればExcel Onlineは無料で使える。手順は以下のとおり。

1. `https://office.com` にアクセスしてMicrosoftアカウントでサインイン
2. 「Excel」を選択して新規または既存ファイルを開く
3. 「ホーム」タブ → 「アドイン」→ 「Claude by Anthropic」を検索してインストール
4. Claudeアカウント（Proプラン以上）でサインイン
5. サイドバーが開いたら自然言語で指示するだけ

---

## まとめ：3点チェックを先にやろう

Claude CoworkとClaude in Excelは、プログラミング不要でデータ分析・ファイル整理・Excelモデル作成ができる非常に強力なツールだ。しかし**試す前に環境確認を怠ると、エラーで詰まって時間を無駄にする**。

特にWindowsユーザーは以下の3点を必ず確認してほしい。

```
チェック① Windowsエディション
  → Home ならCoworkは動かない。Pro/Enterprise/Educationが必要。

チェック② ディスクの空き容量
  → 10 GB以上必要。エクスプローラー → PCで確認。

チェック③ Officeのライセンス種別
  → Microsoft 365サブスクリプション版か確認。
    2019などの買い切り版はClaude in Excel非対応。
    office.comのExcel Onlineなら代替可能。
```

Coworkが動く環境は **macOS（Apple Silicon）** か **Windows Pro以上** が現実的な選択肢だ。Zennブログのネタとして両ツールを紹介したかったが、「動かなかった経緯と環境要件の整理」という形で記事にした。同じ壁に当たる前にこの記事が役立てば幸い。

---

## 参考リンク

---

*七花ファーム（ナナカファーム）の農業×AIの取り組みは他の記事でも発信しています。*
