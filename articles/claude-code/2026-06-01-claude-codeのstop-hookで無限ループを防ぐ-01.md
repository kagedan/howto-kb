---
id: "2026-06-01-claude-codeのstop-hookで無限ループを防ぐ-01"
title: "Claude CodeのStop hookで無限ループを防ぐ"
url: "https://qiita.com/ohakutsu/items/bc97ebfdc87877b94561"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

Claude Codeには、メインのエージェントが応答を終了したときに実行されるStop hookがあります。
応答を終了したときに発火するので、以下のような使い方ができます。

- デスクトップ通知
- フォーマッターやリンターを最後に実行する
- クリーンアップ
- テストや型チェックが通るまで実行を続けさせる
- 変更した内容をコミットさせる

ただ、実行を続けさせると無限ループになり、終わらないのではないかと気になると思います。

この記事では無限ループを防ぐClaude Codeの機能を紹介します。

## `stop_hook_active`フィールド

Stop hookで`decision: "block"`を返してClaudeが応答を継続するとき、再度Stop hookが呼ばれる際の入力JSONに`stop_hook_active`というフィールドが含まれます。

https://code.claude.com/docs/en/hooks#stop-input

```jsonc:例
{
  "stop_hook_active": false,
  // 略...
}
```

`stop_hook_active`は、「Stop hookによってすでに継続が要求されている状態か」を表すフラグになっており、hookスクリプトの先頭でこの値をチェックして、`true`なら早期exitするようにすることで、無限ループを防ぐことができます。

```bash:例
#!/usr/bin/env bash

INPUT="$(cat)"
if [ "$(echo "${INPUT}" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0
fi

# 略...
```

## `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` 環境変数

実はClaude Code側でも無限ループにならないように上限が設けられています。
（何もしてなくても無限ループにならんのかい）

デフォルトでは、Stop hookが連続8回ブロックすると、それ以降のブロックは無視されてClaudeが止まるようになっています。
この上限を変更したい場合に使うのが、`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`環境変数です。

https://code.claude.com/docs/en/hooks-guide#stop-hook-hits-the-block-cap

ただ、トークンの無駄遣いになるだけだと思うので、`stop_hook_active`フィールドや別の手段で早期exitするようにするのが良いと思います。

## さいごに

Stop hookで継続させるロジックを書くときは、`stop_hook_active`のチェックを定型として入れておくのが簡単なのでおすすめです。
（Claudeが期待していることを終わらせるまでの場合は使えないですが）
