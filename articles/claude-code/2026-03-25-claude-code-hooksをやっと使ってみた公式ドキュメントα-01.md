---
id: "2026-03-25-claude-code-hooksをやっと使ってみた公式ドキュメントα-01"
title: "Claude Code Hooksをやっと使ってみた：公式ドキュメント+α"
url: "https://qiita.com/Maji3322/items/b9a75d12acea8ebaacc0"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

Claude Code Hooks、便利そうと思っても億劫になって今までゴリゴリ設定していませんでした。新しいプロジェクトになったら大部分を設定し直さなきゃいけないと思うとやる気にはなれませんでした。通知設定だけはしていました。(音声+バナー+効果音はとても良いです。おすすめです。)

今回機会があったので、これを利用してHooksでできることをたくさん理解していきたいと思います。公式ドキュメントを見つつ、運用を考えてみました。個人開発です。そのレポートみたいなものです。

---

以下の記事を書いた後に少し個人開発をしました。感想です。

* 今回設定した中で開発中に関与するのはおもにLinterとFormatterだけでした。
* 一つ、設定ファイルでファイルパスを間違えていたところがあったのでそれを修正してもらったのですが、その時にちゃんと通知が出ました。
* 私はまだかなり高頻度で手動のallow/denyをしているので、4でやったブロックが発動したことはまだありませんでした。
* その他もお守り的につけてあるので今後経過観察して気づいたことがあれば書き足していこうと思います。

---

## 1. プロジェクト毎運用は大して面倒じゃなかった

なんとなくできる気はしていましたが確認していなかったことです。Claude CodeはSkillsで`update-config`というのがあるのでそれを利用すれば自然言語で設定を変更することが可能です。つまり、もしプロジェクト毎に細かい設定が必要な場合はそれ自体をプロンプト化すればよいということです。2,3のformatterとlinterはその一例です。  
その他の共通部分はユーザー設定に置いておきます。量が多くて頭も使うので気が引けますが、一度やれば開発体験がさらに良くなると考えました。

↓このように、わざわざ言ってみても全く変化がないので、LinterとFormatterが適切に動いているであろうことが確認できた。  
[![スクリーンショット 2026-03-25 12.24.26.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3809025%2F6a936182-5233-413e-9aec-3fc7f48a9f01.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=960d5f7d3253c87a8893b734cfc303c2)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3809025%2F6a936182-5233-413e-9aec-3fc7f48a9f01.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=960d5f7d3253c87a8893b734cfc303c2)

## 2. Formatter

自分が扱う言語のコードフォーマッタをあらかじめ選定しておきます。私はそれほど開発経験がある方ではないので、コードフォーマッタの比較は省略し、評判が良さそうなものを選びます。今回はPythonのRuffのblack modeを選び、Claude Codeに伝えました。

## 3. Linter

Formatterと同様にコードの可読性を高めるのに効果的なので入れます。PythonにRuffを使います。

参考：[編集後にコードを自動フォーマットする - Claude Code Docs](https://code.claude.com/docs/ja/hooks-guide#%E7%B7%A8%E9%9B%86%E5%BE%8C%E3%81%AB%E3%82%B3%E3%83%BC%E3%83%89%E3%82%92%E8%87%AA%E5%8B%95%E3%83%95%E3%82%A9%E3%83%BC%E3%83%9E%E3%83%83%E3%83%88%E3%81%99%E3%82%8B)

##### pre-commitのhooksとの比較検討

私は今回初めて知ったのですが、pre-commitによって、git commitに応じて同じくHooksを仕掛けておくこともできるようです。  
しかし、コミットしないとコードが整わないというのは今回の意図とは違うため、こちらにFormatterとLinterは入れていません。

##### VS Codeの設定との干渉

当然ですが、VS CodeのFormatterやLinterと、Claude Code Hooksで別のものを使ってたら二度手間です。`editor.defaultFormatter` で確認してClaude Codeに伝えましょう。

## 4. 保護されたファイルへの編集をブロックする

Claude Codeでは設定ファイルの`permissions.deny`の他に、Hooksでブロックすることもできます。なぜあえてこちらでやるのかというと、ブロックされるのはわかるが、本当にそれを見たいときに適当な代替案を考えさせてしまうのを防ぐことができるから...というのが本来の意図と思われます。

たとえば、無理やり読もうとしてエラーを何度も繰り返したりしてしまうことを防ぐことができます。(私はまだ出くわしたことがありませんが...)

`.env.local`などは説明不要ですから、`permissions.deny`にグローバル設定に入れておくほうが良い....

と思っていたのですが、今(2026/03/25)は不具合が起きていて、`permissions.deny`が適用されない？というようなissueが開いています。`permissions.deny`よりもHooksによる保護もやっておいたほうが良いと思います。

ドキュメントからの変更点は、`PreToolUse`をmatcher: Read|Write|Edit|Bashに対して設定してあります（""にしておく）。また、グローバル設定にし、Bash用の処理を加えてあります。

ただし、`cat .e''nv` や `cat $DOTENV_PATH` は検知できないので、限界はあることに注意してください。

`~/.claude/hooks/protect-files.sh`

```
#!/bin/bash
INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
BASH_CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
  if [[ "$BASH_CMD" == *"$pattern"* ]]; then
    echo "Blocked bash command: touches '$pattern'" >&2
    exit 2
  fi
done

exit 0
```

その後、chmodします。(macOS/Linux)

```
chmod +x ~/.claude/hooks/protect-files.sh
```

設定には以下のように書きます。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

参考：

1. [https://code.claude.com/docs/ja/hooks-guide#保護されたファイルへの編集をブロックする](https://code.claude.com/docs/ja/hooks-guide#%E4%BF%9D%E8%AD%B7%E3%81%95%E3%82%8C%E3%81%9F%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%B8%E3%81%AE%E7%B7%A8%E9%9B%86%E3%82%92%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF%E3%81%99%E3%82%8B)
2. [https://code.claude.com/docs/ja/permissions#権限ルール構文](https://code.claude.com/docs/ja/permissions#%E6%A8%A9%E9%99%90%E3%83%AB%E3%83%BC%E3%83%AB%E6%A7%8B%E6%96%87)
3. [https://code.claude.com/docs/ja/permissions#権限を管理する](https://code.claude.com/docs/ja/permissions#%E6%A8%A9%E9%99%90%E3%82%92%E7%AE%A1%E7%90%86%E3%81%99%E3%82%8B)
4. <https://github.com/anthropics/claude-code/issues/30519>

## 5. Compact後にコマンド実行結果をコンテキストに注入する

`SessionStart.matcher`でcompactを指定します。覚えておくと思い出したときに使えるかもしれません。

* `echo`: `CLAUDE.md`と異なり、matcher時にのみ注入するプロンプト向け
* `git log --format="%s%n%b" -5`: 最近のコミットのタイトルとメッセージを表示し、開発の姿勢と進捗を維持。全てのmatcherにつけておきました。
  + `%s` : タイトル（subject）
  + `%b` : ボディ（body、メッセージ本文）
  + `%n` : 改行

matcherに使えるのは以下です。

* startup: `CLAUDE.md`との使い分けが重要そうです。
* resume: セッションコンテキスト自体は生きているので、時間が経った後に戻ってくる想定で何か伝えることがあれば...。
* clear: コンテキストを開ける目的ならcompactを使ったほうが良いので、ここは空欄のほうが良いと考えられます。
* **compact**: おもにcompact後にechoで自動指示する用途が良いと思います。skillsの指示をするのも良いかもしれません。

参考: [https://code.claude.com/docs/ja/hooks-guide#圧縮後にコンテキストを再注入する](https://code.claude.com/docs/ja/hooks-guide#%E5%9C%A7%E7%B8%AE%E5%BE%8C%E3%81%AB%E3%82%B3%E3%83%B3%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88%E3%82%92%E5%86%8D%E6%B3%A8%E5%85%A5%E3%81%99%E3%82%8B)

## 6. **設定変更検知**

`user_settings`、`project_settings`、`local_settings`、`policy_settings`、`skills`で使えます。`policy_settings`は組織設定のポリシーです。  
設定変更を通知する設定をグローバルの方につけました。これに関しては付け得だと思います。

```
{
  "hooks": {
    "ConfigChange": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
			"command": "osascript -e 'display notification \"Claude Code changed its setting.\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

参考: [https://code.claude.com/docs/ja/hooks-guide#設定変更を監査する](https://code.claude.com/docs/ja/hooks-guide#%E8%A8%AD%E5%AE%9A%E5%A4%89%E6%9B%B4%E3%82%92%E7%9B%A3%E6%9F%BB%E3%81%99%E3%82%8B)

## 7. 許可プロンプトを自動承認

`permissions.allow`は静的ですが、hooks経由では高度なスクリプトによって動的に設定することができます。正直私の手に余る設定だったので今回は置いておきます。

参考: [https://code.claude.com/docs/ja/hooks-guide#特定の許可プロンプトを自動承認する](https://code.claude.com/docs/ja/hooks-guide#%E7%89%B9%E5%AE%9A%E3%81%AE%E8%A8%B1%E5%8F%AF%E3%83%97%E3%83%AD%E3%83%B3%E3%83%97%E3%83%88%E3%82%92%E8%87%AA%E5%8B%95%E6%89%BF%E8%AA%8D%E3%81%99%E3%82%8B)

## 8. エージェントベースのhooks

プロンプトベース（つまり単一のLLM呼び出し）も可能です。  
エージェントベースのhooksではサブエージェントを起動し目的を持って活動させます。サブエージェントなので完全にはコンテキストは受け継いでいないと思われます。

しかしこれも正直、活用するのは難しかったですが、覚えておくと便利そうなのは以下の仕様です。ドキュメントから引用しています。  
[https://code.claude.com/docs/ja/hooks#エージェント-フックの仕組み](https://code.claude.com/docs/ja/hooks#%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88-%E3%83%95%E3%83%83%E3%82%AF%E3%81%AE%E4%BB%95%E7%B5%84%E3%81%BF)

> エージェント hooks はプロンプト hooks と同じ `"ok"` / `"reason"` 応答形式を使用しますが、デフォルトのタイムアウトが 60 秒で、最大 50 ツール使用ターンです。

参考:

## 9. セキュリティについて

Hooks作成をClaudeに頼む際には以下をコンテキストに入れましょう。  
引用: [https://code.claude.com/docs/ja/hooks#セキュリティ-ベストプラクティス](https://code.claude.com/docs/ja/hooks#%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3-%E3%83%99%E3%82%B9%E3%83%88%E3%83%97%E3%83%A9%E3%82%AF%E3%83%86%E3%82%A3%E3%82%B9)

```
- **入力を検証およびサニタイズ**: 入力データを盲目的に信頼しないでください
- **常にシェル変数を引用**: `$VAR` ではなく `"$VAR"` を使用
- **パス トラバーサルをブロック**: ファイル パスで `..` をチェック
- **絶対パスを使用**: スクリプトの完全なパスを指定し、プロジェクト ルートに `"$CLAUDE_PROJECT_DIR"` を使用
- **機密ファイルをスキップ**: `.env`、`.git/`、キーなどを避ける
```

特に4つ目、絶対パスの指定に独自の変数が使えるのは整理もしやすくなって助かりますね。  
6の設定変更検知と組み合わせるのも良いと思います。以下のように付け加えました。

```
{
  "hooks": {
    "ConfigChange": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code changed its setting.\" with title \"Claude Code\"'"
          },
          {
            "type": "command",
            "command": "echo 'もしhooksの変更なら以下に注意してください。- 入力を検証およびサニタイズ: 入力データを盲目的に信頼しないでください - 常にシェル変数を引用: $VAR ではなく \"$VAR\" を使用 - パストラバーサルをブロック: ファイルパスで .. をチェック - 絶対パスを使用: スクリプトの完全なパスを指定し、プロジェクトルートに \"$CLAUDE_PROJECT_DIR\" を使用 - 機密ファイルをスキップ: .env、.git/、キーなどを避ける'"
          }
        ]
      }
    ]
  }
}
```

## 10. gitignore通知

これはドキュメント外です。まず私がやりたかったのはうっかり`.gitignore`に環境変数のファイルを入れ損ねていないかを確認するスクリプトを`SessionStart`に書いています。(今思えばpre-commitのほうがよかったかもしれません...)  
[![スクリーンショット 2026-03-25 12.21.32.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3809025%2F82000e31-87bf-42b5-98f3-4ea76c58f3f9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ffce71b514ec68e40aa0cd48800b0963)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3809025%2F82000e31-87bf-42b5-98f3-4ea76c58f3f9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ffce71b514ec68e40aa0cd48800b0963)

`~/.claude/hooks/gitignore-notify.sh`

```
#!/bin/bash

git rev-parse --git-dir > /dev/null 2>&1 || exit 0

SENSITIVE_FILES=(
    ".env"
    ".env.local"
    ".env.production"
    ".env.secret"
)

MISSING=()
for f in "${SENSITIVE_FILES[@]}"; do
    git check-ignore -q "$f" 2>/dev/null || MISSING+=("$f")
done

if [ ${#MISSING[@]} -gt 0 ]; then
    JOINED=$(IFS=', '; echo "${MISSING[*]}")
    echo "{\"systemMessage\": \"警告: .gitignore に次のエントリが見つかりません: $JOINED\"}"
else
    echo "{\"systemMessage\": \".gitignore チェック: ヒットしませんでした\"}"
fi

exit 0
```

```
"SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$HOME\"/.claude/hooks/gitignore-notify.sh"
          }
        ]
      }
    ]
```

---

ありがとうございました。誤りやより良い案などがあれば気軽にコメントしてほしいです。
