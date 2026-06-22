---
id: "2026-06-21-claude-code-の-channels-機能でclaude-code-をai-社員にする-01"
title: "Claude Code の channels 機能で「Claude Code を」AI 社員にする"
url: "https://zenn.dev/yamitzky/articles/08a2493b527b4f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

こんにちは、小笠原みつき([@yamitzky](https://x.com/yamitzky))です。

Claude Code で AI 社員を何人も並べて、Discord から動かす仕組みを作ったので共有します。  
人間は Discord に書き込むだけで、AI 社員(エージェント)同士もお互いにメッセージを送り合いながら応答する、マルチエージェントな仕組みです。

マルチエージェントな Hermes Agent や OpenClaw を、Claude Code で再現した、と言った方が伝わりやすいかもしれません。

![](https://static.zenn.studio/user-upload/6534042ee575-20260621.png)

その正体は、Discord チャネルごとに、1つひとつが独立した **Claude Code のセッション** です。Claude Agent SDK などではなく、チャンネルごとに Claude Code そのものを動かしている、ということです。

全体を支えているのは、Claude Code の **channels** という機能です。

## 全体像

先に、やっていることの全体像を1枚の図で示します。

土台にあるのが Claude Code の **channels** という機能で、その上に Discord と claude-peers という2つの channel が乗っています。  
人間は Discord 越しに話し、セッション同士は claude-peers 越しに話します。  
受け手の Claude Code から見ると、どちらも同じ形のメッセージとして届きます。

ここから、土台の channels から順に見ていきます。

## channels とは

**channels** は、ターミナルの外で起きたことを [Claude Code のセッションに流し込む機能](https://code.claude.com/docs/ja/channels)です（執筆時点では research preview で、Claude Code v2.1.80 以降が必要です）。例えば、Discord や Telegramなどで受け取ったメッセージを、Claude Code のセッションに push 型で流し込むことができます。

仕組みはシンプルで、1つの channel は1つの MCP サーバーです。  
ふつうの MCP サーバーは Claude が呼び出すツールを生やしますが、channel はその逆で、サーバー側から Claude にイベントを push します。

MCP サーバーを channel にするのは、capability を1つ宣言するだけです。

```
const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    // このキーがあると Claude Code が channel として扱ってくれる
    capabilities: { experimental: { 'claude/channel': {} } },
    instructions: 'イベントは <channel source="webhook" ...> の形で届きます。',
  },
)
```

あとはイベントが起きたときに `notifications/claude/channel` を投げると、Claude のセッション内にこういう形で割り込みます。

```
<channel source="webhook" severity="high" run_id="1234">
hello world
</channel>
```

自分で作った channel を試すときは、`--dangerously-load-development-channels` を付けて起動します。

```
claude --dangerously-load-development-channels server:webhook
```

いくつか、[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins) に公式の実装も用意されています(現在は Telegram、Discord、iMessage のみが対応)。

## 2つの channel を組み合わせる

今回の仕組みは、この channels の上に2つの channel を載せただけです。

### Discord（公式の channel）

人間の入口には Discord を使っています。(ただし後述するように、フォークしています)  
Discord は公式プラグインに入っている双方向の channel で、ローカルで Discord の API をポーリングし、新しい発言を `<channel>` として Claude に届けます。

受付になる1つのセッションに、Discord の channel を載せて起動します。

```
claude --dangerously-skip-permissions \
  --dangerously-load-development-channels \
  server:discord-router server:claude-peers
```

人間が Discord に書き込むと、受付セッションにこう届きます。

```
<channel source="discord" chat_id="..." user="..." ts="...">
本文
</channel>
```

返信は `reply` ツールに `chat_id` を渡すだけです。  
ちなみに channel は、送り主を allowlist で絞る作りになっています。  
誰でも書き込める口をそのまま Claude に流すと prompt injection の経路になるので、ペアリングで許可した相手だけを通します。

### claude-peers（OSS の channel）

セッション同士の会話には、[louislva/claude-peers-mcp](https://github.com/louislva/claude-peers-mcp) を channel として使っています。  
これは `localhost:7899` で動くブローカー1つを介して、同じマシンの Claude Code 同士を発見させ、メッセージを送り合わせるものです。  
あるセッションが相手を一覧して `send_message` を呼ぶと、相手のコンテキストに同じ `<channel>` の形で届きます。

```
<channel source="claude-peers" from_id="..." from_cwd="channels/general">
今日のリマインダーは何件ある？
```

## 担当セッションへ振り分ける

Discord channel が届くのは受付セッション1つだけとしています。これは Discord への接続数を多くしすぎないためです。

そのうえで、公式の Discord channel をフォークし、担当セッションへ振り分ける処理を自分で足しました。

```
# ルーティング用
claude --dangerously-skip-permissions --dangerously-load-development-channels server:discord-router server:claude-peers
```

各セッションは、作業ディレクトリで識別します。Discord の `chat_id` から作業ディレクトリへの対応表を1枚の JSON に持たせ、その対応をたどって宛先を決めます。フォークした discord-router が claude-peers を使ってメッセージを分配します。

```
// channel-map.json
{
  "661226294062612493": {
    "name": "リマインダー", // Discord のチャンネル名
    "category": "秘書室", // Discord のカテゴリ
    "path": "/path/to/reminder" // Claude Code を動かすフォルダ
  }
}
```

各セッションのディレクトリには `CLAUDE.md` を置いて、役割と固有ルールを書いておきます。  
同じ Claude Code を起動しても、置き場所が違えば読み込む `CLAUDE.md` が違うので、別の社員として振る舞います。  
社員の人格を起動引数ではなく、ファイルの置き場所で表しているわけです。

```
cd /path/to/channel/dir && claude --dangerously-skip-permissions --dangerously-load-development-channels server:claude-peers
```

## 実際の動き方

実際の流れを1つ見てみます。  
人間が Discord の「一般」チャンネルに書き込みます。

```
<channel source="discord" chat_id="6612..." user="yamitzky">
このブログのドラフト書いて
```

受付セッションがこれを担当の作業ディレクトリへ解決して、claude-peers 経由で送ります。  
担当セッションには、こう届きます。

```
<channel source="claude-peers" from_id="discord-router" ...>
[discord chat_id=6612... user=yamitzky]
このブログのドラフト書いて
```

実際の Discord の様子

![](https://static.zenn.studio/user-upload/dc1711fd3859-20260621.png)

内部の Claude Code の様子

![](https://static.zenn.studio/user-upload/12254012952a-20260621.png)

## メリット・デメリット

良くも悪くも、仕組みはただの Claude Code です。

良い点としては、

* Claude Code なので内部の仕組みがわかりやすい
  + セッションやコンテキスト圧縮、モデル選択、CLAUDE.md、Agent Skill、MEMORY.md などの仕組みで動いていることがわかる
* Claude Code で使える機能は全部使える
  + ultracode で実装したり、Web 検索したり
* 多分 Claude のサブスクリプションの中で動く

悪い点としては、

* 各セッションがフルの Claude Code プロセスなので重い
  + AI 社員(Discord チャンネル)の数だけプロセスが立ち上がり、メモリを食う
* zellij 経由で Claude Code を動かしているため不安定なことがある
* 再起動すると (/resume しないと)コンテキストが揮発する

実際のスタートアップでもよく「◯人の壁」という言葉が言われますが、この仕組みも Claude Code のセッションのためのメモリが足りないため、AI 社員の採用が途中で止まります。笑

私は、Hermes Agentも併用しているのですがこのようなメリット・デメリットがあるために、

* Claude Code でやりたいごく一部のユースケースをこの記事で説明した仕組み
* リマインダーなどカジュアルな用途は Hermes Agent

という使い分けに落ち着きました。

もしよかったら参考に AI 社員作ってみてください〜！
