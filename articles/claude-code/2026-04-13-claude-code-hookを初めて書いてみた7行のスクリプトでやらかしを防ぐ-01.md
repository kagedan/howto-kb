---
id: "2026-04-13-claude-code-hookを初めて書いてみた7行のスクリプトでやらかしを防ぐ-01"
title: "Claude Code Hookを初めて書いてみた——7行のスクリプトで「やらかし」を防ぐ"
url: "https://qiita.com/yurukusa/items/e387a4bcfab4272dabdc"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

Claude Codeを使い始めて1週間で、作りかけのファイルをAIに消された。

リファクタリングを頼んだだけなのに、Claudeは「不要なファイルを整理しよう」と判断して、いくつかのファイルをまとめて削除した。Gitにcommitしていない変更も含めて。

GitHubにはもっと深刻な事例がある。[C:\Usersフォルダが全部消された](https://github.com/anthropics/claude-code/issues/36339)という報告。Claude Codeは便利だが、「何でもできる」ということは「何でも壊せる」ということでもある。

この事故の後、「hookを入れなきゃ」と思った。hookというのは、AIが何かをやろうとした瞬間に「ちょっと待て」と割り込んで止める仕組みだ。

## 最初のhookを書いてみる

hookは実はすごくシンプルだ。たった7行のスクリプトで書ける。

やることは1つ。AIが`rm -rf /`（ファイルを全部消すコマンド）を実行しようとしたら、ブロックする。

まず、`jq`（JSONを処理するコマンド）が必要。入っていなければ先にインストールする:

```
# macOS
brew install jq

# Ubuntu/Debian
sudo apt install jq
```

次に、hookを保存する場所を作る:

次に、スクリプトを書く:

```
cat > ~/.claude/hooks/my-first-hook.sh << 'EOF'
#!/bin/bash
COMMAND=$(cat | jq -r '.tool_input.command // empty' 2>/dev/null)

if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+/'; then
    echo "BLOCKED: rm -rf on root" >&2
    exit 2
fi

exit 0
EOF
chmod +x ~/.claude/hooks/my-first-hook.sh
```

7行。何をやっているか:

1. `cat` — Claude Codeが「これからこのコマンドを実行するよ」と送ってくるデータを受け取る
2. `jq` — そのデータからコマンドの部分だけを取り出す
3. `grep` — `rm -rf /`というパターンが含まれているか調べる
4. `exit 2` — 含まれていたらブロック。Claude Codeは「exit 2」を受け取ると、そのコマンドを実行しない

`exit 0`は「問題なし、実行していいよ」という意味。

## 登録する

スクリプトを書いただけでは動かない。Claude Codeに「このスクリプトを使って」と教える必要がある。

`~/.claude/settings.json`に以下を追加する:

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/my-first-hook.sh"
          }
        ]
      }
    ]
  }
}
```

`PreToolUse`は「ツールを使う前に」という意味。`matcher: "Bash"`は「Bashコマンドの実行前に」という意味。つまり「AIがBashコマンドを実行する前に、毎回このスクリプトを走らせて」という設定。

Claude Codeを再起動すれば、hookが有効になる。

## 動くか確かめる

本当に`rm -rf /`を実行して確かめるわけにはいかないので、シミュレーションで確認する:

```
# 危険なコマンドがブロックされるか
echo '{"tool_input":{"command":"rm -rf /"}}' | bash ~/.claude/hooks/my-first-hook.sh
echo $?  # 2が出れば成功（ブロックされた）

# 安全なコマンドは通るか
echo '{"tool_input":{"command":"ls -la"}}' | bash ~/.claude/hooks/my-first-hook.sh
echo $?  # 0が出れば成功（許可された）
```

テストコマンドは`bash`で明示的に実行しているので`chmod +x`がなくても動く。だが後述の`settings.json`では`bash`プレフィックスなしでパスだけを指定している。Claude Codeがhookを直接実行する場合、実行権限がないとフックが無視される。`chmod +x`は忘れずにつけておくこと。

**macOSユーザーへ**: Claude Codeはhookを制限されたPATHで実行する（[#46954](https://github.com/anthropics/claude-code/issues/46954)）。Homebrewでインストールした`jq`（`/opt/homebrew/bin/jq`）がhookから見つからず、**hookが何もせずに終了する**ことがある。hookの先頭に `export PATH="/opt/homebrew/bin:$PATH"` を追加するか、絶対パス `/opt/homebrew/bin/jq` を使うと確実。

## 手動で書かなくてもいい

ここまで読んで「面倒だな」と思った人は、`cc-safe-setup`を使えば全部自動でやってくれる。

```
# 8個の安全hookを一発でインストール
npx cc-safe-setup

# 自然言語でhookを作る（JSONもスクリプトも書かなくていい）
npx cc-safe-setup --guard "データベースを消すな"
```

ただ、仕組みを知っておくと、自分で好きなhookを作れるようになる。「AIに○○をさせたくない」というルールを自分で追加できる。

## hookの種類

hookには複数のタイミングがある。よく使うのはこの4つ:

| タイミング | いつ動く | 例 |
| --- | --- | --- |
| **PreToolUse** | AIがコマンドを実行する前 | 「rm -rfを止める」「mainへのpushを止める」 |
| **PostToolUse** | AIがコマンドを実行した後 | 「構文エラーがないかチェック」 |
| **Notification** | AIが通知を送るとき | 「通知内容をログに記録」 |
| **Stop** | セッションが終わるとき | 「作業ログを保存」 |

他にもSessionStart（セッション開始時）、UserPromptSubmit（ユーザー入力時）などがある。最初はPreToolUseだけ覚えればいい。「AIが何かをする前に、止めるかどうかを判断する」——これがhookの基本。

---

「どのhookを入れればいいかわからない」なら、[Hook Selector](https://yurukusa.github.io/cc-safe-setup/hook-selector.html)で5つの質問に答えるだけで最適なhookセットが分かる。

hookの設計パターンや自律セッション運用の実践例は[Anthropic公式ガイドにない事故防止——800+時間で19点→85点にした全記録](https://zenn.dev/yurukusa/books/6076c23b1cb18b)（¥800・第3章まで無料）にまとめている。655個のhookを作るまでの800時間の全記録は[AIに仕事を任せてみた](https://zenn.dev/yurukusa/books/3c3c3baee85f0a19)（¥800・第2章まで無料）。

---

**📖 トークン消費に困っているなら** → [Claude Codeのトークン消費を半分にする——800時間の運用データから見つけた実践テクニック](https://zenn.dev/yurukusa/books/token-savings-guide?utm_source=qiita-e387a4bc&utm_medium=article&utm_campaign=token-book)（¥2,500・はじめに+第1章 無料）

---

**関連記事**: [Claude Codeのトークン消費を減らす5つの方法——Opus 4.7対応](https://qiita.com/yurukusa/items/435810e1e8a046c99916)

---

**⚠️ CVE-2026-21852（2026年4月公開）**: プロジェクト内`.claude/settings.json`経由でAPIキー窃盗。対策: `npx cc-safe-setup`（ユーザーレベル設定で免疫）→ [詳細](https://yurukusa.github.io/cc-safe-setup/opus-47-survival-guide.html#cve-settings-exfil)
