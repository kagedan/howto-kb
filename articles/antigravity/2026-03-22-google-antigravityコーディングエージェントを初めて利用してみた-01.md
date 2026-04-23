---
id: "2026-03-22-google-antigravityコーディングエージェントを初めて利用してみた-01"
title: "【Google Antigravity】コーディングエージェントを初めて利用してみた"
url: "https://zenn.dev/lunette/articles/338e87552faa6b"
source: "zenn"
category: "antigravity"
tags: ["antigravity", "zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## はじめに

ここ最近、コーディングエージェントが急速に進化しているという話は何度か耳にしていた。  
特に昨年以降は、従来の「コード補完ツール」という枠を超えて、設計・実装・デバッグまで一貫して担うパートナーのような存在へと変化しつつある。

そんな中、Googleが新たにリリースしたのが「Google Antigravity」だ。  
従来のエディタとAIチャットを単に組み合わせたものではなく、エージェントが主体となって開発を進めることを前提に設計されたIDEとなっている。

というわけで、今回の記事では簡単なWebアプリをGoogle Antigravityに作成させ、所感について語っていこうと思う。

## Google Antigravityとは

<https://antigravity.google/>

* Googleが2025年11月に発表した次世代のAIエージェント型IDE（統合開発環境）
* `Editor`と`Agent Manager`という2つのメインウィンドウがある
  + `Editor`はVSCodeと同じUI。なんならVSCodeの設定を引き継ぐこともできる
  + `Agent Manager`はChatGPT等とほぼ同じUI。このウィンドウでエージェントに指示する
  + ウィンドウの切り替えは`Cmd + E` (Mac) / `Ctrl + E` (Windows)で行う
* リリースされてから日が浅いのでWeb上に情報が少ないのが難点

## Antigravityを使って分かったこと

### `implementation_plan.md`で実装計画を教えてくれる

プロンプト

```
## 実装
- ダッシュボードにGmailの利用状況をデータビジュアライゼーションとして可視化
    - KPIメトリクスカード（未読数などのシンプルな数字）
    - 過去7日間の送受信推移（折れ線グラフ）
    - カテゴリ割合（円グラフ）
```

* 上記のようなプロンプトをAIエージェントに投げると、下記のような実装計画を詳細かつ素早く教えてくれる。
* この段階でユーザーの想定通りの計画になっていない部分があった場合、当該箇所にコメントを入れてエージェントに教えることもできる。

implementation\_plan.md

```
# Gmailダッシュボード実装計画

## ユーザーの確認が必要な事項
> [!IMPORTANT]
> Gmail APIにアクセスするためには、SupabaseのGoogle OAuth設定に必要なスコープ（例：`https://www.googleapis.com/auth/gmail.readonly`）を追加する必要があります。この設定が正しく行われていることを確認してください。また、利用にあたって再度ログインが必要になります。

## 目的
認証されたユーザーのGmail利用状況を可視化するダッシュボードを実装します。ダッシュボードには以下を含めます：
1. 未読件数などを示すKPIメトリクスカード
2. 過去7日間の送受信の推移を示す折れ線グラフ
3. メールのカテゴリ割合を示す円グラフ

## 提案する変更内容
### 認証のアップデート
- **[MODIFY] `features/auth/components/google-login-button.tsx`**: `signInWithOAuth`のオプションにGmail APIのスコープ（`https://www.googleapis.com/auth/gmail.readonly`）を追加します。また、リフレッシュトークンを取得するために`access_type: 'offline'`を設定します。

### Gmail APIユーティリティ
- **[NEW] `features/dashboard/api/gmail.ts`**: Supabaseのセッションからアクセストークンを取得し、Gmail APIからデータを取得する関数を作成します：
  - `fetchUnreadCount`: 未読メールの件数を取得します。
  - `fetchEmailTrends`: 過去7日間の送受信メール数を取得します。
  - `fetchCategoryRatios`: メイン、プロモーション、ソーシャルなどのカテゴリごとの件数を取得します。

### UIコンポーネント
- **Command**: グラフとアイコン用ライブラリをインストールします（`npm install recharts lucide-react`）。
- **[NEW] `features/dashboard/components/kpi-cards.tsx`**: KPI（未読数など）を表示するコンポーネント。
- **[NEW] `features/dashboard/components/trend-chart.tsx`**: Rechartsを使用した折れ線グラフコンポーネント。
- **[NEW] `features/dashboard/components/category-chart.tsx`**: Rechartsを使用した円グラフコンポーネント。
- **[MODIFY] `app/dashboard/page.tsx`**: データ取得ロジックと上記のグラフコンポーネントを統合します。

## 検証計画
### 手動での検証
- ユーザーがダッシュボードを開いた際に、実際のGmailデータを用いて各コンポーネントが正しくレンダリングされるか確認します。
```

### `task.md`で実装に必要なタスクを可視化してくれる

* タスクを必要な分だけ細分化し、ユーザー側に提示してくれる
* タスクは基本的に上から順番に消化する仕様となっている
* タスクの進捗状況の確認もできる
* 完了したタスクにはチェックマークが付く

task.md

```
# Gmail可視化ダッシュボードの実装

- [x] SupabaseのGoogle Auth設定を調査し、Googleプロバイダートークン（アクセストークン）が取得可能か確認する。
- [x] サーバーサイドでのGmail APIデータ取得ロジックを定義する：
  - [x] 未読メール件数を取得する（KPIカード用）。
  - [x] 過去7日間の送受信の推移データを取得する。
  - [x] メールのカテゴリ/ラベルを取得し、割合を計算する。
- [x] 必要なUIライブラリ（recharts, lucide-react等）がなければインストールする。
- [x] Tailwind CSSとshadcn/uiのコンポーネントを用いてUIを作成する：
  - [x] KPIメトリクスカードコンポーネント
  - [x] トレンド折れ線グラフコンポーネント
  - [x] カテゴリ円グラフコンポーネント
- [x] ダッシュボードページにデータ取得ロジックとUIコンポーネントを統合する。
- [ ] 実際のユーザーデータで機能が正常に動作するかテスト・検証する。
```

### `walkthrough.md`で何を実装したのかを教えてくれる

* 実装が完了するとwalkthroughが出力される
* ユーザーが手動でやる必要のある部分についてはネクストアクションを提示してくれる

walkthrough.md

```
# Gmail可視化ダッシュボードの実装完了

ダッシュボードへのGmailデータの可視化機能の実装が完了しました！

## 実装内容
- `features/auth/components/google-login-button.tsx` にGmail読み取り用スコープ（`https://www.googleapis.com/auth/gmail.readonly`）を追加しました。
- `features/dashboard/api/gmail.ts` を作成し、Googleプロバイダートークンを元に以下のデータを取得するロジックを実装しました。
  - 受信トレイの全体の未読・総メッセージ数
  - 直近7日間の送受信ログ（`in:inbox` および `in:sent` を日付ごとにカウント）
  - Primary, Social, Promotionsなどの各種カテゴリ・ラベルのメール件数
- `recharts` と `lucide-react` をインストールし、ダッシュボード用のUIを構築しました。
  - `KPICards`: メトリクス数字を表示
  - `TrendChart`: 7日間の折れ線グラフを表示
  - `CategoryChart`: カテゴリ割合の円グラフを表示
- `app/dashboard/page.tsx` を修正し、これらすべてを結合しました。

## 次のステップ（ユーザーによる手動確認）
1. 一度ログアウトし、**再度Googleログイン**を行ってください。（「Googleアカウントへのアクセスを許可」という画面でGmailへのアクセス許可が求められます）
2. ログイン後、ダッシュボード画面が表示されることを確認してください。データがない場合は、Google Cloud Console側でGmail APIが有効化されているかエラー表示をご確認ください。
```

## Antigravityが作成したWebアプリの紹介

Googleアカウントでサインインすると、先程の`walkthrough.md`の通りにGmailのデータビジュアライゼーションが実装できていることが分かる。また、モダンでクリーンなデザインの実現およびレスポンシブ対応もできている。なお、UIが英語表記で統一されてしまっているが、これは後述する`Rules`のUI要件に日本語を指定していなかったためである。

補足

Gmail APIのような制限付きスコープを利用するにあたり、本来はGoogleの厳しい審査が必要となる。しかし、ローカル環境でのテスト用途であれば、Google Cloud Consoleの「OAuth同意画面」の設定で、アプリの公開ステータスを「テスト中」にした上で、自分のアカウントを「テストユーザー」として追加するという方法で動作確認をすることができる。

### ログイン画面

![ログイン画面のUI](https://static.zenn.studio/user-upload/c3d43f29f7d5-20260322.png)

### ダッシュボード画面

![ダッシュボード画面のUI](https://static.zenn.studio/user-upload/f1ab4aa182b0-20260322.png)

### レスポンシブ対応

![レスポンシブ対応を示す画像](https://static.zenn.studio/user-upload/a1df58facb07-20260322.png)

## Tips

### `Rules`を設定してエージェントに制約を与えよう

`Rules`というものを予め設定しておくと、技術スタックやアーキテクチャ方針を毎回プロンプトとして入力しなくても良くなるので、是非とも設定しておきたい。Antigravityの場合は`.agents/rules/`配下に`code-style-guide.md`というファイルを作成することで簡単に設定することができる。下記の例は一見するとかなり厳しい制約に見えるかもしれないが、これくらいガチガチに縛った方が人間にとってはむしろコントロールしやすくなる。

.agents/rules/code-style-guide.md

```
## プロジェクト設定

### 技術スタック

* フロントエンド：Next.js（App Router）+ TypeScript
* スタイリング：Tailwind CSS + shadcn/ui
* バックエンド：Supabase（Auth / Database / Storage）
* バリデーション：Zod
* フォーム管理：React Hook Form
* テスト：Vitest

---

## 出力要件

以下を必ずすべて出力すること：

* ディレクトリ構成
* 各ファイルのコード（省略しない）
* Supabaseのテーブル作成SQL
* 環境変数の説明
* セットアップ手順

---

## アーキテクチャ方針

### データ取得

* Server Componentsを基本とする
* クライアントでのデータ取得は最小限にする
* SupabaseクライアントまたはServer Actionsを使用する
* 不要なAPI Routesは作成しない

### コンポーネント設計

* UIとビジネスロジックを分離する
* 再利用可能なコンポーネントを作成する
* components/uiに共通UIを配置
* Server Component / Client Componentを適切に使い分ける

### ディレクトリ構成ルール

* app/：ルーティング
* components/：共通UI
* features/：機能単位のロジック
* lib/：ユーティリティ・設定
* types/：型定義

---

## 認証・認可

* Supabase Auth（Email + Password）を使用
* セッション管理はSupabaseの公式クライアントを使用
* middlewareでログイン状態を判定
* 未ログインユーザーはログインページへリダイレクト
* 認証が必要なページは保護する

---

## データベース設計

* 命名規則はsnake_case
* 主キーはUUIDを使用
* 全テーブルに以下を含める：
  * created_at
  * updated_at
* 外部キー制約を適切に設定
* 必要に応じて論理削除（deleted_at）を使用

---

## フォーム仕様

* React Hook Form + Zodを使用
* リアルタイムバリデーションを行う
* エラーは項目の下に赤字で表示
* フォーカス時にスタイル変更
* サーバー側バリデーションも実装する

---

## UI要件

* モダンでクリーンなデザイン
* レスポンシブ対応
* shadcn/uiベースで構築
* ローディング状態を適切に表示
* 空データ時のUIも用意する

---

## エラーハンドリング

* try-catchで適切に処理する
* ユーザー向けメッセージと開発者向けログを分離
* フォームエラーはフィールド単位で表示
* 予期しないエラーは共通UIまたはトーストで表示

---

## 環境変数

* NEXT_PUBLIC_とサーバー専用変数を明確に分離
* 秘密情報はクライアントに渡さない

---

## テスト

* Vitestを使用
* ユーティリティ関数の単体テストを作成
* バリデーションのテストを作成
* 正常系・異常系を網羅する

---

## セキュリティ

* Supabaseのクエリを使用しSQLインジェクションを防ぐ
* XSS対策を行う（dangerouslySetInnerHTMLは極力使用しない）
* 認証・認可を必ずサーバー側でも検証する

---

## パフォーマンス

* 不要な再レンダリングを防ぐ
* キャッシュを適切に利用する
* Server Componentsを活用する

---

## 補足

* 実務で動くレベルの品質で実装すること
* ダミーデータは禁止（必ずDBと接続する）
* 可読性・保守性を重視する
* 型安全を担保する（TypeScriptを厳密に使用）
* コメントは必要最小限にする（冗長にしない）

---
```

## おわりに

### 偏見の解消

かつてはコーディングエージェントに対して下記のような偏見を持っていたが、実際に使ってみることで「そんなことはない」という気付きを得ることができた。

| 偏見 | 実際 |
| --- | --- |
| エージェントを利用するとアプリがブラックボックス化してしまうのでは？ | むしろ実装計画、タスク、実装ログをちゃんと説明してくれる。個人的には割と参考になる。 |
| エージェントは余計な機能を勝手に追加してきたりするのでは？ | 基本的にそういうことはしない。もしそういった現象に遭遇したらルールで縛ることもできる。 |
| 正直GitHub Copilotのようなコード補完とあまり変わらないのでは？ | 「設計 → 実装 → 修正 → テスト」まで一貫してやってくれるので、作業効率が大幅に上がっている。 |

### 今後への期待

#### レガシーコードのリファクタリングにかかる工数を大幅に短縮できそう

これまで「触ると壊れる」と敬遠されていたコードに対しても、エージェントが段階的に安全な修正案を提示してくれるようになれば、技術的負債の解消スピードは一気に上がりそうだと感じた。

#### コーディングエージェントのスマホアプリ化によって開発の民主化が進行しそう

将来的には、エンジニアではない主婦や学生さんが自らの課題を解決するためのアプリを素早く形にできる世界が現実になるかもしれない。イメージとしては`Claw Empire`のスマホ版みたいなものかな？既にどこかのゲーム会社が開発を開始してそうではある。  
<https://github.com/GreenSheep01201/claw-empire/tree/main?tab=readme-ov-file>

#### プロトタイピングの速度が桁違いに向上する

アイデア検証のハードルが大きく下がるため、MVP（Minimum Viable Product）をいとも容易く仕上げることができる。これに伴いアジャイル開発やDevOpsがさらに浸透する可能性が高い。

## 参考資料

### Antigravityの公式ドキュメント

<https://antigravity.google/docs/home>

### Google Codelabs

<https://codelabs.developers.google.com/getting-started-google-antigravity?hl=ja#0>
