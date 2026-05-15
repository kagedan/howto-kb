---
id: "2026-05-14-anthropic公式プラグインhookifyでclaude-codeのフックを自然言語で作る-01"
title: "Anthropic公式プラグイン「hookify」でClaude Codeのフックを自然言語で作る"
url: "https://zenn.dev/shirochan/articles/198a0537a79469"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "Python", "TypeScript", "zenn"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Codeのフック機能は強力です。ファイル編集前に確認を挟んだり、危険なコマンドをブロックしたり、`.env` への書き込みを防いだりできます。

しかし実際に設定しようとすると、`settings.json` に JSON を手書きする必要があり、書式を調べながら試行錯誤するうちに諦めた、という経験がある人も少なくないはずです。

`hookify` は、そのハードルをほぼゼロにするプラグインです。自然言語でやりたいことを伝えるだけでフックが生成され、**再起動なしに即時有効**になります。

<https://claude.com/plugins/hookify>

## hookify とは

`hookify` は [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) で公開されているAnthropicの公式プラグインです。

フックの定義を `settings.json` の複雑な JSON として書く代わりに、**マークダウンファイル**として書けるようにします。そのマークダウンの生成を自然言語の指示から自動で行うのが `/hookify:hookify` コマンドです。  
公式のREADME.mdには`/hookify`コマンドと書いてありますがこれだとエラーになるので注意が必要です。  
<https://github.com/anthropics/claude-plugins-official/tree/main/plugins/hookify>

主な特徴は次の通りです:

* 自然言語の指示からルールファイルを自動生成
* 会話履歴を解析して「繰り返し修正したパターン」を自動で検出
* JSON を一切書かずに完結
* `warn`（警告のみ）と `block`（実行阻止）を選択可能
* **変更即時反映**（再起動不要）

## インストール

```
/plugin install hookify@claude-plugins-official
/reload-plugins
```

前回の `claude-code-setup` 同様、マーケットプレイスから1行でインストールできます。

前回の記事はこちら

<https://zenn.dev/shirochan/articles/1a9c4b51f4ef7b>

## 基本的な使い方

### 指示を渡して使う

やりたいことを引数として渡します:

```
/hookify:hookify rm -rf を実行するときは警告して
```

Claude が以下を行います:

1. 指示を解析してルールを設計
2. `warn` か `block` かを確認
3. `.claude/hookify.warn-rm.local.md` を生成
4. 「即時有効です」と通知

実行結果

```
❯ /hookify:hookify  rm -rf を実行するときは警告して

⏺ Skill(hookify:writing-rules)
  ⎿  Successfully loaded skill

⏺ rm -rf 実行時に警告するルールを作成します。まず .claude/ ディレクトリを確認します。

  Listed 1 directory (ctrl+o to expand)

⏺ Write(.claude/hookify.dangerous-rm.local.md)
  ⎿  Wrote 17 lines to .claude/hookify.dangerous-rm.local.md
      1 ---
      2 name: warn-dangerous-rm
      3 enabled: true
      4 event: bash
      5 pattern: rm\s+-rf
      6 action: warn
      7 ---
      8
      9 ⚠️ **危険なコマンドが検出されました: rm -rf**
     … +7 lines (ctrl+o to expand)

⏺ ルールを作成しました。

  作成ファイル: .claude/hookify.dangerous-rm.local.md

  - トリガー: rm -rf を含む Bash コマンド
  - アクション: 警告を表示（実行はブロックしない）
  - 有効化: 即座に有効 — 再起動不要

  次回 rm -rf を含むコマンドを実行しようとすると、確認を促す警告メッセージが表示されます。
```

### 引数なしで使う（会話解析モード）

引数なしで実行すると、直近の会話を解析して「繰り返し修正が発生したパターン」や「ユーザーが明示的に否定した操作」を自動で検出し、フック化の候補を提示します。

例えば次のような発言が過去の会話にあった場合:

```
なぜ console.log を追加したんですか？ 削除してください
```

これを検出して「TypeScriptファイルへの console.log 追加を警告するフック」を候補として提示してくれます。

### ヘルパーコマンド

| コマンド | 説明 |
| --- | --- |
| `/hookify:list` | 設定済みルール一覧を表示 |
| `/hookify:configure` | ルールの有効/無効を対話的に切り替え |
| `/hookify:help` | ドキュメントを表示 |

## ルールファイルの構造

生成されるファイルは `.claude/hookify.{rule-name}.local.md` という名前で、プロジェクトルートの `.claude/` に置かれます。フォーマットはシンプルです。

### 基本形（単一パターン）

```
---
name: warn-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
action: warn
---

⚠️ **危険な rm コマンドを検出しました**

パスが正しいか確認してください。
バックアップがあることを確認してから実行してください。
```

### 複数条件の組み合わせ

```
---
name: warn-hardcoded-api-key
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.tsx?$
  - field: new_text
    operator: regex_match
    pattern: (API_KEY|SECRET|TOKEN)\s*=\s*["']
---

🔐 **TypeScript ファイルにハードコードされた認証情報を検出しました**

環境変数を使用してください。
```

`conditions` を使うと「ファイルパス」と「追加されるテキスト」を同時に評価できます。すべての条件が一致したときだけルールが発火します。

## イベントタイプ

| event | 対象ツール | 用途の例 |
| --- | --- | --- |
| `bash` | Bash | 危険なコマンドのブロック・警告 |
| `file` | Edit / Write / MultiEdit | 特定ファイルへの書き込み制御 |
| `stop` | セッション停止 | テスト未実行のまま終了を阻止 |
| `prompt` | ユーザー入力 | 特定の指示パターンに反応 |
| `all` | すべて | 横断的なルール |

## warn と block の違い

| action | 動作 |
| --- | --- |
| `warn` | 警告メッセージを表示するが操作は続行される |
| `block` | 操作を阻止する（`bash`/`file` では実行停止、`stop` ではセッション終了を阻止） |

迷ったら `warn` から始め、問題が繰り返すようなら `block` に切り替える運用が安全です。

## 実用的なルール例

以下のルールは [公式の examples ディレクトリ](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/hookify/examples) に収録されているサンプルをもとにしています。一部アレンジを加えていますが、実際のファイルも参考にしてください。

### 1. .env ファイルへの書き込みをブロック

```
---
name: block-env-edit
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$
---

🔒 **.env ファイルへの書き込みをブロックしました**

API キーなどの機密情報を誤って変更・コミットするリスクを防ぐため、.env への直接編集はブロックしています。
変更が必要な場合は手動で編集してください。
```

### 2. デバッグコードの混入を警告

```
---
name: warn-debug-code
enabled: true
event: file
pattern: console\.log\(|debugger;
action: warn
---

🐛 **デバッグコードを検出しました**

コミット前に console.log や debugger を削除してください。
```

### 3. テスト未実行のままセッションを終了させない

[公式サンプル](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/hookify/examples/require-tests-stop.local.md)では以下のように書かれています。

```
---
name: require-tests-before-stop
enabled: false
event: stop
action: block
conditions:
  - field: transcript
    operator: not_contains
    pattern: npm test|pytest|cargo test
---

**テストが実行されていません**

作業を終了する前に、テストを実行して変更が壊れていないか確認してください。
```

ただし、[`not_contains` の実装](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/hookify/core/rule_engine.py#L172-L173)は Python の単純な部分文字列チェック（`pattern not in text`）です。`|` は正規表現の OR ではなくリテラル文字として扱われるため、上記は「`npm test|pytest|cargo test` という文字列がトランスクリプトに含まれない場合に発動」という挙動になります。この文字列がトランスクリプトに現れることはほぼないため、**テストを実行していても常に block が発動してしまいます**。

正しく動作させるには、条件を1つずつ分割します（条件は AND で評価されるため、「どれも含まれない場合に発動」になります）。

```
---
name: require-tests-before-stop
enabled: false
event: stop
action: block
conditions:
  - field: transcript
    operator: not_contains
    pattern: npm test
  - field: transcript
    operator: not_contains
    pattern: pytest
  - field: transcript
    operator: not_contains
    pattern: cargo test
---

**テストが実行されていません**

作業を終了する前に、テストを実行して変更が壊れていないか確認してください。
```

> テスト必須チェックは厳格すぎる場面もあるため、デフォルト `enabled: false` にしておき、必要なプロジェクトでだけ有効化するのがおすすめです。

## settings.json との比較

従来のフック設定と hookify を比較します。

**従来（settings.json を手書き）:**

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import sys, json; data=json.load(sys.stdin); cmd=data.get('tool_input',{}).get('command',''); sys.exit(1 if 'rm -rf' in cmd else 0)\"",
            "blocking": true
          }
        ]
      }
    ]
  }
}
```

**hookify:**

```
---
name: block-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
action: block
---

🛑 rm -rf をブロックしました。パスを確認してから再実行してください。
```

フックの意図が読みやすく、メッセージを自由に書けるのが hookify の強みです。また JSON の書式ミスでサイレントに動かなくなるリスクもありません。

## 注意点

* ルールファイルは `.local.md` という名前のため、`.gitignore` でバージョン管理から除外するかどうかを意識する必要があります。チーム共有したい場合はファイル名の命名規則を検討してください。
* パターンは Python の正規表現構文です。複雑なパターンは `python3 -c "import re; print(re.search(r'pattern', 'test'))"` で事前確認できます。
* `stop` イベントの `block` は強力なため、意図せずセッションが終了できなくなる場合があります。使用する際は `enabled: false` を初期値にしておくことを推奨します。

## まとめ

`hookify` は、Claude Codeのフック機能を「知っているが設定が面倒で使えていない」状態から「自然言語で即座に設定できる」状態に変えるプラグインです。

自分が繰り返し修正していた操作を `/hookify:hookify`（引数なし）で解析してルール化するだけでも、日常の作業を大きく改善できます。

---

**参考リンク**
