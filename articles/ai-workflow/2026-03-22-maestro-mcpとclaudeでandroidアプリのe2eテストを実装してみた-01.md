---
id: "2026-03-22-maestro-mcpとclaudeでandroidアプリのe2eテストを実装してみた-01"
title: "Maestro MCPとClaudeでAndroidアプリのE2Eテストを実装してみた"
url: "https://zenn.dev/banananana/articles/maestro-mcp-android-e2e-test"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## はじめに

こんにちは、しがないモバイルエンジニアです。フリーランスしてます。

モバイルアプリのE2Eテスト、実際にプロジェクトで実行しているところはほぼないと思います。  
「やった方がいいのはわかってるけど、ハードルが高い」というのが現実ではないでしょうか。

### モバイルE2Eテストのハードルが高い理由

* **環境構築が面倒** — エミュレータ/シミュレータのセットアップ、テストフレームワークの導入、CIとの連携...
* **テストコードの記述コストが高い** — Espresso や UI Automator のAPIを覚える必要がある。セレクタの指定が煩雑
* **メンテナンスが大変** — UIを変更するたびにテストが壊れる。修正コストが積み重なって放置されがち

しかし、AI時代においてはこのあたりのハードルをかなり下げられるのでは？と思い、**Maestro MCP × Claude** の組み合わせで試してみました。

結論から言うと、**テストケースを日本語で書いてClaudeに渡すだけで、E2Eテスト用のYAMLが生成され、エミュレータ上で自動実行**できました。

## Maestroとは

[Maestro](https://maestro.mobile.dev/) は、モバイルアプリ向けのE2Eテストフレームワークです。

特徴をざっくりまとめると：

* **YAML でテストを記述** — コードを書かずにテストフローを定義できる
* **iOS / Android 両対応** — 同じ記法で両プラットフォームをテスト可能
* **テキストベースで要素特定** — `tapOn: "ログイン"` のように画面上のテキストでUI要素を指定できる
* **MCP (Model Context Protocol) 対応** — AIエージェントからMaestroを操作できる

Espresso のようにコードを書く必要がなく、YAMLで `tapOn` や `assertVisible` を並べるだけなので、学習コストが非常に低いです。

## 前提

### Maestroのインストール

以下のコマンドでインストールできます。Java 17以上が必要です。

```
curl -Ls "https://get.maestro.mobile.dev" | bash
```

詳細は[公式ドキュメント](https://maestro.mobile.dev/)を参照してください。

### サンプルアプリ

Android (Kotlin) で、簡単なCRUD + ユーザー登録・ログイン機能を持つサンプルアプリを作りました。

![サンプルアプリのログイン画面](https://static.zenn.studio/user-upload/deployed-images/87091b2f0a91661129c5b797.gif?sha=256f27cb647e10b64352267e2639f3cd90c2c28d)

## 導入手順

今回は**ログイン機能のテスト**を自動化します。

### 1. テストケースを洗い出す

まず、ログイン画面のテストケースを日本語で整理しました。

| # | 種別 | テスト内容 |
| --- | --- | --- |
| 1 | 正常系 | 初期表示の要素が全て表示されている |
| 2 | 正常系 | 登録済みユーザーでログイン成功→一覧画面へ遷移 |
| 3 | 異常系 | 空欄のままログイン→両フィールドにエラー表示 |
| 4 | 異常系 | 不正なメールアドレス形式→エラー表示 |
| 5 | 異常系 | メールのみ入力→パスワード未入力エラー |
| 6 | 異常系 | パスワードのみ入力→メール未入力エラー |
| 7 | 異常系 | 間違ったパスワード→Snackbarエラー |
| 8 | 異常系 | 未登録メール→Snackbarエラー |
| 9 | 画面遷移 | 登録画面へ遷移→戻るボタンで帰還 |
| 10 | バリデーション | エラー表示後に入力再開→エラーがクリア |

### 2. Claudeにテストを書かせる

このテストケース一覧をClaudeに伝えて、Maestro用のYAMLを生成してもらいました。

実際に生成されたYAMLの一部を紹介します：

```
appId: com.example.e2esample
name: "ログイン画面テスト"

---

# ============================================
# 1. 初期表示の確認
# ============================================
- launchApp:
    clearState: true

- assertVisible: "トレーニング記録"
- assertVisible: "ログイン"
- assertVisible: "メールアドレス"
- assertVisible: "パスワード"
- assertVisible: "アカウントをお持ちでない方はこちら"

# ============================================
# 3. 異常系: 空欄のままログインボタン押下
# ============================================
- launchApp:
    clearState: true

- tapOn:
    text: "ログイン"
    index: 1

- assertVisible: "メールアドレスを入力してください"
- assertVisible: "パスワードを入力してください"
```

共通処理（テストユーザーの登録など）はサブフローとして切り出されます：

```
# .maestro/shared/register_test_user.yaml
appId: com.example.e2esample
name: "テスト用ユーザー登録サブフロー"
---
- tapOn: "アカウントをお持ちでない方はこちら"
- assertVisible: "アカウント登録"
- tapOn: "名前"
- inputText: "Test User"
- tapOn: "メールアドレス"
- inputText: "test@example.com"
- tapOn: "パスワード (6文字以上)"
- inputText: "password123"
- tapOn: "登録"
- assertVisible: "トレーニング記録"
- tapOn: "ログアウト"
- assertVisible: "ログイン"
```

メインのテストから `runFlow` で呼び出すだけです：

```
- runFlow: shared/register_test_user.yaml
```

### 3. テストを実行する

```
maestro test .maestro/login.yaml
```

これだけです。エミュレータ上でアプリが自動操作され、全テストケースが順番に実行されます。

![Maestroテスト実行の様子](https://static.zenn.studio/user-upload/deployed-images/cf923fab53df60c3a883ac6f.gif?sha=0770654ad9504ebe295b16dc3f00b7a8a207a19e)

### 実行結果

```
✅ 1. 初期表示の確認
✅ 2. 正常系: 登録済みユーザーでログイン成功
✅ 3. 異常系: 空欄のままログインボタン押下
✅ 4. 異常系: 不正なメールアドレス形式
✅ 5. 異常系: メールのみ入力でパスワード未入力
✅ 6. 異常系: パスワードのみ入力でメール未入力
✅ 7. 異常系: 間違ったパスワードでログイン
✅ 8. 異常系: 未登録のメールアドレスでログイン
✅ 9. 画面遷移: 登録画面へ遷移し戻る
✅ 10. バリデーション: 入力再開でエラーがクリアされる
```

全10テストケース、PASSED。

## 所感

突き詰めれば、**仕様書に沿ったテストはかなり自動化できそう**だと感じました。

人間は「何をテストすべきか」という本質的な設計に集中し、「テストの実施」という作業はAIに任せる。そんな開発体験がもうすぐそこまで来ていると感じました。
