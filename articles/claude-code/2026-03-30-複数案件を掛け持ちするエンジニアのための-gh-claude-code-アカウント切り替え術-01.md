---
id: "2026-03-30-複数案件を掛け持ちするエンジニアのための-gh-claude-code-アカウント切り替え術-01"
title: "複数案件を掛け持ちするエンジニアのための gh / Claude Code アカウント切り替え術"
url: "https://zenn.dev/busaiku0084/articles/20260330-dc3vcb5l"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

複数の案件を掛け持ちしていると、GitHubアカウントやClaude Codeの認証を切り替える場面が頻繁にやってきます。個人のOSSと業務用リポジトリで別アカウントを使っていたり、案件ごとにClaude Codeの組織アカウントが異なっていたりすると、切り替え忘れによるミスが起きがちです。

「間違ったアカウントでコミットしてしまった」「別の組織のClaude Codeでコードを読ませてしまった」といった経験がある方もいるのではないでしょうか。

この記事では、GitHub CLI（`gh`）の `auth switch` とClaude Codeの `auth` コマンドを使って、アカウントの切り替えをスムーズに行う方法を紹介します。

## gh: GitHubアカウントの切り替え

### 現在のログイン状態を確認する

まずは `gh auth status` で、今どのアカウントでログインしているかを確認します。

**実行結果:**

```
github.com
  ✓ Logged in to github.com account personal-account (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'

  ✓ Logged in to github.com account work-account (keyring)
  - Active account: false
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

2つのアカウントが登録されていて、`personal-account` がアクティブになっていることが分かります。`Active account: true` と表示されているのが、現在 `gh` コマンドで使われているアカウントです。

### アカウントを切り替える

業務用のリポジトリを触るときは、`gh auth switch` でアカウントを切り替えます。

**実行結果:**

```
✓ Switched active account for github.com to work-account
```

たったこれだけです。登録済みのアカウントが2つだけなら、自動的にもう一方に切り替わります。

3つ以上のアカウントを登録している場合は対話的に選択する画面が表示されますが、`--user` フラグを使えば一発で指定できます。

```
gh auth switch --user work-account
```

### 新しいアカウントを追加する

まだ1つのアカウントしか登録していない場合は、`gh auth login` で追加します。

ブラウザが開いて認証フローが始まります。完了すると、先ほどの `gh auth status` に新しいアカウントが表示されるようになります。すでに別アカウントでログイン済みでも、追加で認証すれば両方のアカウントが保持されます。

### 切り替え忘れを防ぐコツ

`gh auth status` の出力をシェルのプロンプトに組み込んでおくと、今どのアカウントで作業しているかが一目で分かります。簡易的には以下のようなエイリアスを `.zshrc` に追加しておくと便利です。

```
alias ghwho='gh auth status 2>&1 | grep "Active account: true" -B 1 | head -1'
```

**実行結果:**

```
  ✓ Logged in to github.com account work-account (keyring)
```

作業を始める前に `ghwho` と打てば、アクティブなアカウントをすぐに確認できます。

## Claude Code: 認証の切り替え

### 現在のログイン状態を確認する

Claude Codeも同様に、まずは現在の認証状態を確認します。

**実行結果:**

```
{
  "loggedIn": true,
  "authMethod": "claude.ai",
  "apiProvider": "firstParty",
  "email": "user@example.com",
  "orgId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "orgName": "MyCompany",
  "subscriptionType": "team"
}
```

どの組織のどのアカウントでログインしているかが JSON で表示されます。`orgName` を見れば、今どの案件の組織に接続しているかが分かります。

### ログアウトして別アカウントでログインする

Claude Codeには `gh` のような `switch` コマンドはありませんが、`logout` と `login` の組み合わせで簡単に切り替えられます。

**実行結果:**

続けて、別のアカウントでログインします。

ブラウザが開いて認証ページに遷移するので、切り替え先のアカウントでログインすれば完了です。

特定のメールアドレスを指定してログインページを開くこともできます。

```
claude auth login --email user@another-company.com
```

SSOを使っている組織であれば、`--sso` フラグを付けるとSSO認証フローに直接進めます。

### API経由で利用している場合

Anthropic Console（API課金）を使っている場合は、`--console` フラグを付けてログインします。

```
claude auth login --console
```

Claude.ai のサブスクリプション（Team / Enterprise）と Anthropic Console のAPI利用では認証の仕組みが異なるため、利用形態に合ったオプションを選んでください。

## 切り替え作業の流れ

実際の案件切り替えでは、`gh` と `claude` の両方を切り替えることになります。私の場合は以下のような流れで作業しています。

```
# 1. 現在の状態を確認
gh auth status
claude auth status

# 2. GitHub アカウントを切り替え
gh auth switch --user work-account

# 3. Claude Code を切り替え
claude auth logout
claude auth login --email user@work.com

# 4. 切り替え後の確認
gh auth status
claude auth status
```

頻繁に行う操作なので、シェルスクリプトにまとめておくのもよいでしょう。以下は簡単な例です。

```
#!/bin/bash
# switch-to-work.sh

echo "=== Switching to work account ==="

echo "-> gh: switching..."
gh auth switch --user work-account

echo "-> claude: switching..."
claude auth logout
claude auth login --email user@work.com

echo "=== Done ==="
gh auth status
```

ただし、`claude auth login` はブラウザでの認証が必要なため、完全な自動化は難しい点には注意してください。

## まとめ

複数案件を掛け持ちしているとアカウントの切り替えは避けて通れませんが、`gh` も Claude Code もCLIで簡潔に操作できるようになっています。

* `gh auth switch` で GitHub アカウントをワンコマンドで切り替え
* `gh auth status` でアクティブなアカウントを確認
* `claude auth logout` → `claude auth login` で Claude Code の認証を切り替え
* `claude auth status` で現在の組織・アカウントを確認

切り替え忘れによる事故を防ぐためにも、作業開始前に `status` で確認する習慣をつけておくのがおすすめです。
