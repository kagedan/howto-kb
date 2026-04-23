---
id: "2026-03-25-google-antigravityでaiをプログラミングに統合するlaravelとreactjsの-01"
title: "Google AntigravityでAIをプログラミングに統合する：LaravelとReactJSのための「Agent-First」実践ガイド"
url: "https://qiita.com/Adachit-1411/items/473c0e61d0e24d1bc4f9"
source: "qiita"
category: "antigravity"
tags: ["AI-agent", "antigravity", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

# Google AntigravityでAIをプログラミングに統合する：LaravelとReactJSのための「Agent-First」実践ガイド

[![1.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2F61be2d87-c30c-4b0e-ba06-a74c07f8ad9f.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=29824428a987cdf097aa549631984622)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2F61be2d87-c30c-4b0e-ba06-a74c07f8ad9f.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=29824428a987cdf097aa549631984622)

第一世代のAIコーディング支援ツールは、主に構文の予測やコードの補完を行う「タイピングアシスタント」として機能していました。しかし、**Google Antigravity**（Agent-first IDEプラットフォーム）の登場により、私たちは新しい時代に突入しています。プログラマーはもはや1行ずつコードを書くのではなく、自律型AIエージェントを指揮する「アーキテクト」へと進化しました。

本記事では、**ReactJS**（フロントエンド）と**Laravel**（バックエンド）に焦点を当て、実際の開発ワークフローにGoogle Antigravityを統合する方法を解説します。

## 1. Google Antigravityの特徴とは？

オープンソースのVisual Studio Codeをベースにしつつも、全く新しい設計思想を持つAntigravityは、ワークスペースを主に2つのビューに分割します：

* **Editor View（エディタビュー）：** AIによって強化された使い慣れたコーディングインターフェース。
* **Manager View（マネージャービュー）：** 複数のエージェントに並行してタスクを割り当てる指令センター。エージェントは自律的に計画を立て、コードを書き、ターミナルを実行し、ブラウザでテストを行います。

[![2.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2F9be3bfec-2b4e-43ae-b57b-7097d7456247.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9a59da9387d60358ee34efc4f1303255)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2F9be3bfec-2b4e-43ae-b57b-7097d7456247.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9a59da9387d60358ee34efc4f1303255)

## 2. コアワークフロー（Workflow）

1行ずつプロンプトを入力するのではなく、Antigravityでのワークフローは以下の3つのステップに従います：

1. **計画（Planning）：** 大規模な要件を伝え、エージェントにアーキテクチャを作成させる。
2. **実行（Execution）：** エージェントが自動的にファイルを開き、コードを記述し、ターミナルコマンドを実行する。
3. **検証（Verification - Artifacts）：** AIが生成したレポートやスクリーンショットを通じて結果を確認する。

[![3.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2Fa8471838-63f4-492b-a369-532e5afa9652.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2739fce4bb9c1d4189448f4872fb6655)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2Fa8471838-63f4-492b-a369-532e5afa9652.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2739fce4bb9c1d4189448f4872fb6655)

## 3. ReactJS向けの実践的プロンプト（フロントエンド）

ReactJSの開発において、AntigravityはゼロからのUI構築やステートの最適化を極めて高速に行うことができます。

### プロンプト：ゼロからコンポーネントを構築する（Fast Mode）

エージェントのチャットウィンドウでこのプロンプトを使用し、UIと基本的なロジックを全体的に作成させます。

> **プロンプト:**  
> 「あなたはプロのフロントエンドエンジニアです。ReactJSとTailwind CSSを使用して `TaskList.jsx` コンポーネントを作成してください。  
> 要件：
>
> 1. UIには、新しいタスクを追加するための入力フィールドと、その下にタスクのリストを含める。
> 2. タスクを『完了』または『削除』としてマークするボタンを配置する。
> 3. 初期状態として、3つのサンプルタスクを自動生成する。  
>    ファイルを作成し、コードを記述し、内蔵ブラウザで開発環境を起動して結果を確認できるようにしてください。」

[![4.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2Fcffe1057-a005-4bd5-8acb-e08f39b8047f.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=536a348faefcbc72f3b2e1a1c8295695)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2Fcffe1057-a005-4bd5-8acb-e08f39b8047f.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=536a348faefcbc72f3b2e1a1c8295695)

### プロンプト：リファクタリングと状態管理

コンポーネントのファイルが大きくなりすぎた場合、エージェントに構造の再編成を依頼できます。

> **プロンプト:**  
> 「`TaskList.jsx` ファイルにロジックが多すぎます。リファクタリングを行ってください：状態管理（State）のロジックを `useTasks.js` というカスタムフックに分離し、メインコンポーネントを更新してください。すべての機能が正常に動作し続けることを確認してください。」

## 4. Laravel向けの実践的プロンプト（バックエンド）

Antigravityの真の力は、ターミナルコマンドを自動実行できる点にあります。以下はバックエンドのセットアップを依頼する方法です。

### プロンプト：APIアーキテクチャの初期化（Planning Mode）

RESTful APIの構造作成をすべてエージェントに任せることができます。

> **プロンプト:**  
> 「あなたはプロのバックエンドエンジニアです。タスク管理アプリ用のRESTful APIを提供するLaravel 11プロジェクトをセットアップしてください。
>
> 1. 'tasks' テーブル（title, description, is\_completed）のマイグレーションとモデルを作成する。
> 2. 完全なCRUDエンドポイントを含む `TaskController` を作成する。
> 3. MySQLに接続するための `.env` ファイルを設定する。注意：私のローカル環境では `root` ユーザーを使用し、パスワードは空（`DB_PASSWORD=""`）に設定しています。  
>    このセットアップを完了するために必要な `php artisan` コマンドをターミナルで自動的に実行してください。」

[![5.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2Fc43fa001-b246-45d9-b5ed-53fb6fa71be1.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a01f1e4367e0bf7534b200873baf3322)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2Fc43fa001-b246-45d9-b5ed-53fb6fa71be1.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a01f1e4367e0bf7534b200873baf3322)

### プロンプト：自動ユニットテストの作成

> **プロンプト:**  
> 「作成した `TaskController` に基づいて、Pest PHP（または PHPUnit）を使用して完全なテストスイートを記述してください。ターミナルでテストスイートを実行し、すべてのテストケースがパス（緑色）するまで、発生したエラーを自動的に修正してください。」

## 5. Artifacts：コードを読まずに結果を検証する

Antigravityの最も価値のある機能は **Artifacts（アーティファクト）** です。AIが生成した何百行ものコードを読ませる代わりに、システムは作業の証拠（アーキテクチャの概要、ターミナルのログ、機能が正常に動作していることを証明するブラウザのスクリーンショットなど）を提示します。

[![6.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2F99948ff7-af5f-4b20-bd1d-44ede864336d.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=db83fb5ab9503f014fa8467e1e1e9e9d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4304656%2F99948ff7-af5f-4b20-bd1d-44ede864336d.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=db83fb5ab9503f014fa8467e1e1e9e9d)

## まとめ

Google Antigravityは、コーディングを高速化するだけでなく、ソフトウェア開発の考え方を根本的に変えます。Laravel（バックエンド）とReactJS（フロントエンド）向けのプロンプトを柔軟に組み合わせることで、一人でフルスタックアプリケーション全体を記録的な速さで構築することが可能です。

---

### 📚 参考資料 (References)
