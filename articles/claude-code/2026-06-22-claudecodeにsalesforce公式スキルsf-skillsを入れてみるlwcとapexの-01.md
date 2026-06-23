---
id: "2026-06-22-claudecodeにsalesforce公式スキルsf-skillsを入れてみるlwcとapexの-01"
title: "ClaudeCodeにSalesforce公式スキル「sf-skills」を入れてみる｜LWCとApexのベストプラクティス構築を実現"
url: "https://zenn.dev/pacific_creator/articles/ebd995006fc30d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

「Apex書いてもらったけど、SOQL がループの中に入ってて怒られた…」って経験、ありませんか？

私も1年前は、AIが出してくれたコードをそのままデプロイしようとして、Code Analyzerに叩き落とされたことが何度かありました。コードは動くのに、なんでこんなに直すとこがあるんだろうって。

実はそれ、AIに「Salesforceのお作法」を教えてあげていないのが原因なんです。

そこで最近注目しているのが、SalesforceがClaude Code向けに公式公開した **sf-skills** というスキルパッケージ。これを入れるだけで、LWCもApexも「最初からベストプラクティス準拠」のコードが生成されるようになります。

この記事では、sf-skillsの概要・インストール手順・使い方を、Salesforce開発に触れ始めて間もない方でもわかるよう解説します。

## sf-skillsって何？ Salesforce開発専用の「先生」をAIに追加するイメージ

sf-skillsは、**Salesforceが公式GitHubで公開しているAIスキルのパッケージ**です。

要するに「SalesforceのことをよくわかっているAI家庭教師」をClaude Codeに追加するようなものです。

普通のClaude Codeは汎用AIなので、Salesforceのガバナ制限や共有モデル、テストカバレッジのルールまでは自力で判断しきれないことがあります。でもsf-skillsを入れると、そのあたりの「お作法」を自動で守ってコードを書いてくれるようになります。

2026年6月現在、**60以上のスキル**が収録されており、代表的なものはこちらです。

* **generating-apex**：Apexクラスを生成するスキル
* **generating-apex-test**：テストクラスを自動生成するスキル（カバレッジ75%以上を担保）
* **generating-lwc-components**：Lightning Webコンポーネント（LWC）を生成するスキル
* **debugging-apex-logs**：デバッグログを解析して問題を特定するスキル
* **generating-flow**：フローのメタデータを生成するスキル

これらのスキルは、**Claude Code、Cursor、Codex、OpenCodeなど多くのAIツールに対応**しています。

> 出典：[Salesforce Developers Blog](https://developer.salesforce.com/blogs/2026/06/build-production-ready-apps-in-claude-code-with-salesforce-skills)

つまり、generating-apexスキルを使うと普通にApexを書いてもらうことでOKです！

## インストール方法｜たった1コマンドで完了します

sf-skillsのインストールは驚くほど簡単です。Salesforceプロジェクトのディレクトリで、以下の1コマンドを実行するだけです。

```
npx skills add forcedotcom/sf-skills
```

私も最初「これだけ？」と半信半疑だったのですが、本当にこれだけでした。

実行すると、インストールするスキルを選択する画面が出てきます。**スペースキーで選んで、Enterで確定**します。

初心者の方には、この4つからスタートするのがおすすめです。

* `generating-apex`
* `generating-apex-test`
* `generating-lwc-components`
* `debugging-apex-logs`

インストール時に「スコープ」を選べます。

* **Project**：今いるプロジェクトだけに入れる（チームと共有したいときはこちら。`git`にコミットされます）
* **Global**：自分のPC全体に入れる（すべてのプロジェクトで使いたいときはこちら）

また、インストール方法も選べます。

* **Symlink**（推奨）：ファイルを1箇所に置いてリンクで参照。更新が全体に自動反映されます
* **Copy to all agents**：各エージェントにファイルをコピー。更新時は手動で全コピーを変更する必要があります

![](https://static.zenn.studio/user-upload/ae42fa0c3b7b-20260616.png)

インストールが完了すると、プロジェクトフォルダの中に `skills-lock.json` が作成されて、どのスキルが入っているかを確認できます。

```
// skills-lock.json のイメージ
{
  "skills": ["generating-apex", "generating-lwc-components", ...]
}
```

つまり、「npmパッケージをインストールするのと同じ感覚でOK」という理解でOKです！

> 出典：[sf-skills GitHub リポジトリ](https://github.com/forcedotcom/sf-skills)

## 実際に使ってみる｜自然言語で話しかけるだけでLWC＋Apexが生成される

インストールが終わったら、プロジェクトディレクトリでClaude Codeを起動します。

あとは普通に話しかけるだけです。たとえば次のように入力します。

```
Account作成フォームをLWCで作って。
AccountName（必須）とPhone（9桁以上のバリデーションあり）を入力できるようにして、
保存ボタンでApexコントローラ経由でInsertする仕組みにしてほしい。
エラーハンドリングとトースト通知もつけて。
```

![](https://static.zenn.studio/user-upload/6bfaa0fbf713-20260616.png)

すると、Claude Codeが自動的に関係するスキルを起動して、以下のファイルを一気に生成してくれます。

* `accountCreationForm.html`（LWCテンプレート）
* `accountCreationForm.js`（コンポーネントロジック）
* `accountCreationForm.css`（スタイル）
* `accountCreationForm.js-meta.xml`（App Builderで配置できるようにするメタデータ）
* `AccountCreationController.cls`（Apexコントローラ）
* `AccountCreationController.cls-meta.xml`（Apexメタデータ）

![](https://static.zenn.studio/user-upload/fd4212eda5c7-20260616.png)

実際の画面に配置してみました。ちゃんと使えることを確認できました。  
![](https://static.zenn.studio/user-upload/f09db2ffcdd9-20260616.png)

正直、生成が終わった瞬間「これ、1年前の私が半日かけて書いたコードと同じ品質だ…」と思いました。

コード生成後、sf-skillsは自動でSalesforce Code Analyzerを実行し、テストも走らせてくれます。もし問題があればそのままClaude Codeが修正まで対応してくれます。

> 出典：[Salesforce Developers Blog](https://developer.salesforce.com/blogs/2026/06/build-production-ready-apps-in-claude-code-with-salesforce-skills)

つまり、「コードを書く→チェックする→修正するまでの一連の作業をAIが自動でやってくれる」ということです！

## ここは注意！つまずきポイントと注意点

### sf-skillsはnpmパッケージとは別物です

`npx skills add` というコマンドを使いますが、sf-skillsそのものはnpmのパッケージとして配布されていません（["skills" npmパッケージ](https://www.npmjs.com/package/skills)とは別物）。あくまでGitHubのリポジトリからスキルを取得する仕組みです。混同しないようにご注意ください。

---

### 生成されたコードは必ずレビューすること

sf-skillsを使っても、自動生成されたコードは**本番デプロイ前に必ず目視確認**してください。

特に気をつけたいのは、以下の点です。

* フィールドのAPI名が自分の組織のスキーマと一致しているか
* カスタムオブジェクト・項目が対象の組織に存在するか
* 共有モデル（`with sharing`など）がビジネスルール上正しいか

実務で経験した話ですが、テスト環境で100%動いたコードが、本番のフィールド名の差異で失敗したことがあります。**まずSandboxでテスト、その後本番デプロイ**という流れは必ず守りましょう。

---

### Claude Codeの環境構築が前提です

sf-skillsを使うには、以下が必要です。

* Claude Code（個人向けは無料で利用可能）
* Node.js（`npx`を実行するため）
* Salesforce CLI（デプロイや認証のため。`sf org login web`で認証）

「Salesforce CLIって何？」という方は、まずこちらのTrailheadで学んでおくと理解が深まります。→ [Trailhead: Apex Testing](https://trailhead.salesforce.com/content/learn/modules/apex_testing)

---

### スキルを入れすぎると弊害があります

#### パフォーマンス面

スキルはシステムプロンプトとして読み込まれるため、コンテキストウィンドウを消費します。スキルが多いほどトークン数が増え、レスポンスが遅くなったりコストが上がったりします。

#### 精度面

関係ないスキルが誤って発動し、意図しない挙動になることがあります。またスキル同士が競合して、どれを使うべきか判断が混乱することもあります。

#### 管理面

どのスキルが何をするか把握しにくくなり、古いスキルや使わないスキルが残り続けます。

#### 推奨アプローチ

実際に使うものだけを入れましょう。グローバル（-g）インストールは最小限にして、プロジェクト単位でインストールするのが理想です。定期的に npx skills check で棚卸しすることもおすすめです。

現在開いているファイルがApexクラス（AccountCreateFormController.cls）なので、Salesforce開発であれば generating-apex や generating-apex-test など用途に絞ったスキルだけで十分なケースが多いです。

## まとめ

* sf-skillsは、Salesforce公式のAIスキルパッケージ。`npx skills add forcedotcom/sf-skills`の1コマンドでインストールできる
* インストール後はClaude Codeに自然言語で指示するだけで、LWC＋Apexコントローラ＋テストクラスを一括生成してくれる
* 生成されたコードはSalesforce Code Analyzerを自動通過、テストカバレッジ75%以上を担保する設計
* 本番デプロイ前には必ず目視レビューとSandboxテストを行うこと

Salesforce開発にAIを使うのって、最初は「本当に大丈夫かな？」って不安になりますよね。でもsf-skillsがあれば、ベストプラクティスをちゃんと守ってくれるので、AIをより信頼して使いやすくなります。一緒に少しずつ慣れていきましょう！

---

**AI×資格学習・Salesforce業務活用の情報をnoteでも発信しています。**  
→ <https://note.com/pacific_creator1>
