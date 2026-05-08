---
id: "2026-05-07-claude-codeやcopilotが生成するコードは安全aiコードに潜む脆弱性パターンを解説-01"
title: "Claude CodeやCopilotが生成するコードは安全？AIコードに潜む脆弱性パターンを解説"
url: "https://zenn.dev/mapellion/articles/44499b324995f4"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "zenn"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

## はじめに

Claude Code、GitHub Copilot、Cursor——AIコーディングアシスタントは今や開発の現場に欠かせないツールになっています。プロンプト一発でコードが生成される体験は、開発速度を大きく向上させます。

ただし、ここで一度立ち止まって考えてほしいことがあります。

> **「AIが生成したコードは、安全なのか？」**

結論から言うと、**必ずしも安全ではありません。** そしてその規模は、想像以上に大きいです。

この記事では、データに基づいてAI生成コードのリスクを整理し、実際に起きやすい脆弱性パターンを解説します。

---

## どのくらいの割合で脆弱性が混入するのか

まず現状を数字で把握しましょう。

Veracodeが100以上のLLMを対象に実施した2025年の調査では、**AI生成コードの45%がセキュリティテストで失敗し、OWASP Top 10の脆弱性が混入していた**という結果が出ています。

> 参考：[2025 GenAI Code Security Report - Veracode](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/)

Fortune 50企業を対象にしたApiiroの2025年調査では、**AI支援チームは非AI開発者と比べて4倍多くのコミットを生成し、セキュリティ上の問題は10倍以上に増加した**と報告されています。また、2025年6月時点でAI生成コードによるセキュリティ上の問題が月間1万件を超え、半年で10倍のペースで急増していることも示されています。

> 参考：[4x Velocity, 10x Vulnerabilities - Apiiro](https://apiiro.com/blog/4x-velocity-10x-vulnerabilities-ai-coding-assistants-are-shipping-more-risks/)

同じくVeracodeの2025年レポートでは、**AI生成コードは人間が書いたコードより有意に多くの脆弱性を含む**と報告されています。詳細は以下のレポートを参照してください。

> 参考：[2025 GenAI Code Security Report - Veracode](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/)

さらにCloud Security Allianceの調査では、**AI生成コードの62%に設計上の欠陥または既知の脆弱性が含まれている**という結果も報告されています。

> 参考：[Understanding Security Risks in AI-Generated Code - CSA](https://cloudsecurityalliance.org/blog/2025/07/09/understanding-security-risks-in-ai-generated-code)

「動くコード」と「安全なコード」は別物です。AIは前者を得意としますが、後者は別途検証が必要です。

---

## なぜAI生成コードに脆弱性が生まれるのか

AIコーディングアシスタントが脆弱なコードを生成しやすい理由は、主に3つあります。

### ① 学習データに脆弱なコードが含まれている

GitHubなどの公開リポジトリを学習データとして使っているLLMは、セキュアなコードも脆弱なコードも区別なく学習しています。統計的に「よく書かれるパターン」を再現するため、脆弱なパターンもそのまま出力されることがあります。人間が犯す間違いもよく学習しているということです。

### ② コンテキスト全体を把握しきれない

AIはプロンプトで与えられた範囲のコードを生成しますが、システム全体のアーキテクチャや認証フロー・データフローを把握した上でコードを生成するわけではありません。ローカルには正しく見えても、システム全体で見ると脆弱になるケースがあります。すでにAIを利用している方はわかると思いますが、大規模なプロジェクト・ソースコードのコンテキストを把握することは現状ではテクニックが必要です。

### ③ セキュリティ要件を明示しないと考慮されない

Veracodeの調査でも「開発者がセキュリティ要件を明示せずにコードを生成させると、AIはセキュリティの考慮をLLM自身の判断に委ねてしまう」と指摘されています。「動くコードを作って」と頼んだら、動くコードを作ります。セキュアなコードを作ってほしければ、そう伝える必要があります。

---

## AIが生成しやすい脆弱性パターン5選

ここで紹介する5つのパターンは、2つのソースをもとに選定しています。

これら2つの調査に共通して登場する、重大度が高くAI生成コードで特に検出されやすい脆弱性を中心に5つ選びました。

### ① SQLインジェクション（CWE-89）

AIが生成するコードでも頻出する脆弱性の代表格です。Veracodeの調査ではSQLインジェクションは比較的マシで80%のパスレートでしたが、**残り20%は脆弱なコードが生成された**ことを意味します。

**脆弱なパターン（Before）**

```
# ユーザー入力を直接クエリに埋め込んでいる
def get_user(username):
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return db.execute(query)
```

`username` に `' OR '1'='1` のような入力を渡されると、意図しないデータが取得されます。

**安全なパターン（After）**

```
# プレースホルダーを使ってパラメータを分離する
def get_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))
```

AIにSQLを生成させるときは「プレースホルダーを使って」と明示するだけで改善されるケースが多いです。

---

### ② ハードコードされた秘密情報（CWE-798）

APIキー・パスワード・トークンをコードに直書きするパターンです。Apiiroの調査で**秘密情報の露出が40%増加**したと報告されているように、AIコードで特に多く見られます。

**脆弱なパターン（Before）**

```
# APIキーをコードに直書き
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

def call_api():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    ...
```

**安全なパターン（After）**

```
# 環境変数から取得する
import os

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

def call_api():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    ...
```

AIはサンプルコードをそのまま補完しやすく、サンプルに含まれるダミーキーを実際のキーに置き換えただけのコードを生成することがあります。

---

### ③ 安全でない暗号化・ハッシュ（CWE-326 / CWE-916）

パスワードのハッシュ化にMD5やSHA-1を使うパターンです。これらは計算速度が速いためブルートフォース攻撃に弱く、パスワードのハッシュ化には使うべきではありません。

**脆弱なパターン（Before）**

```
import hashlib

def hash_password(password):
    # MD5は速すぎてブルートフォースに弱い
    return hashlib.md5(password.encode()).hexdigest()
```

**安全なパターン（After）**

```
import bcrypt

def hash_password(password):
    # bcryptはストレッチングと自動ソルトで安全
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)
```

AIは「動くコード」として古いハッシュアルゴリズムを使ったコードを生成することがあります。「パスワードのハッシュ化にはbcryptを使って」と指定するのが確実です。

---

### ④ OSコマンドインジェクション（CWE-78）

arXiv論文で**CVSSスコアが特に高い重大脆弱性**として挙げられているパターンのひとつです。ユーザー入力をそのままOSコマンドに渡すことで、攻撃者にシステムを乗っ取られるリスクがあります。

**脆弱なパターン（Before）**

```
import subprocess

# ユーザー入力をそのままコマンドに渡している
def ping_host(hostname):
    result = subprocess.run(f"ping -c 1 {hostname}", shell=True, capture_output=True)
    return result.stdout
```

`hostname` に `google.com; rm -rf /tmp/*` のような入力を渡されると、意図しないコマンドが実行されます。

**安全なパターン（After）**

```
import subprocess

# 引数をリスト形式で渡してshell=Falseにする
def ping_host(hostname):
    result = subprocess.run(["ping", "-c", "1", hostname], shell=False, capture_output=True)
    return result.stdout
```

`shell=True` はコマンドインジェクションの温床になりやすく、AIが生成する際に無意識に使いがちなオプションです。

---

### ⑤ クロスサイトスクリプティング（CWE-80）

Veracodeの調査では、 **XSSの失敗率は86%** と最も高い数値を示しています。ユーザー入力をそのままHTMLに出力するパターンが典型例です。

**脆弱なパターン（Before）**

```
// ユーザー入力をそのままDOMに挿入
function showMessage(userInput) {
    document.getElementById("message").innerHTML = userInput;
}
```

`userInput` に `<script>document.cookie</script>` のようなコードが入ると実行されてしまいます。

**安全なパターン（After）**

```
// textContentを使えばHTMLとして解釈されない
function showMessage(userInput) {
    document.getElementById("message").textContent = userInput;
}
```

---

## レビュー・対策のポイント

### AIコードをレビューするときのチェックリスト

AIが生成したコードをレビューするときは、以下の観点を意識してください。

### SASTと組み合わせる

人間によるコードレビューだけでなく、SASTツールを組み込むことで機械的に検出できる脆弱性は自動化しましょう。AI生成コードの量が増えるほど、手動レビューだけでは追いつかなくなります。

SASTについては以前の記事で詳しく解説しているので、あわせて読んでもらえると理解が深まります。

### プロンプトにセキュリティ要件を含める

AIにコードを生成させるときは、セキュリティ要件を明示的にプロンプトに含めましょう。毎回設定しているとコンテキストを圧迫するので注意が必要です。

```
# セキュリティ要件を含めたプロンプトの例
「ユーザー認証のAPIエンドポイントを実装してください。
以下の要件を満たしてください：
- SQLインジェクション対策のため、プレースホルダーを使うこと
- パスワードはbcryptでハッシュ化すること
- 認可チェックを含めること」
```

### Security Reviewerのサブエージェントを用意する

サブエージェントでレビュアーを用意すると、コーディングしたエージェントと持っているコンテキストが異なるので効果的なレビューを得られます。人間と同じように作成者ではない別の人間（エージェント）がレビューすることで品質を高めることができます。

プロンプトの要領とおなじで、セキュリティに関するロール・観点を与えたサブエージェントを用意しましょう。ReviewerエージェントにはCodingエージェントよりもリッチなLLMモデルを使うのもおすすめです。

### Coding Standard を用意する

セキュリティから少し逸れますがCoding Standardを用意してもいいでしょう。コーディング、レビュアー、エージェントから参照できるリファレンスを準備し、参照してもらうようにします。

レビュー・対策は複数の方法を組み合わせると効果的です。

---

## まとめ

* AI生成コードは**45〜62%の割合で脆弱性を含む**という調査結果がある（Veracode 2025 / CSA 2025）
* 脆弱性が生まれる理由は「学習データの質」「コンテキスト不足」「セキュリティ要件の未指定」
* 特に注意すべきパターンは **SQLi・ハードコード秘密情報・弱いハッシュ・認可漏れ・XSS**
* 対策は「レビューチェックリスト」「SASTの組み込み」「プロンプトへのセキュリティ要件明示」の3本柱
* AIは「動くコード」を生成する。「安全なコード」にするのは開発者の責任

AIコーディングアシスタントを使うこと自体は問題ありません。ただし「AIが書いたから大丈夫」という過信が一番危険です。速度と安全性を両立させるために、セキュリティの目線を忘れないようにしましょう。

---

## 関連記事

SASTを使った静的解析の詳細はこちら。

<https://zenn.dev/mapellion/articles/71aa17e4a2c8b1>

AIによるコードレビューについてはこちら。

<https://zenn.dev/mapellion/articles/cc24fe64c1b131>

AIを組み込んだアプリのセキュリティリスク全般はこちら。

<https://zenn.dev/mapellion/articles/807f0414456620>

AIを信じてたらアカBANされた話はこちら。

<https://zenn.dev/mapellion/articles/7b83f40017112f>
