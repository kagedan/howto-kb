---
id: "2026-06-02-codex-claude-codeからopencodeに移行した話-01"
title: "Codex, Claude CodeからOpenCodeに移行した話"
url: "https://zenn.dev/digeon/articles/012ea7f9d19236"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "OpenAI", "zenn"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

## 始めたきっかけ

普段は会社で使う Codex と私用で使う Claude Code を使用していました。  
２つの違う特徴を持つCLIを使い分けるのは大変だと感じ  
調べて見つけたのが**OpenCode**でした。

### OpenCode とは？

OpenCode は、たくさんの model を役割や用途によって切り替えられる AI エージェントです。

### 移行して良かったこと

CodexやClaude Code両方のmodelを1つのサービスで**簡単に切り替える**ことができ、操作性が高くなったと感じました。

### modelとの相性比較

| ツール | 特徴 |
| --- | --- |
| Codex | OpenAI との統合が強い |
| Claude Code | Claude との相性が良い |
| OpenCode | 特定のmodelに依存せず、使い分けができる |

### OpenCode のカスタマイズ性

OpenCode は leader key を設定可能です。

leader keyとは特定の動作の後に押すkeyによってショートカットを割り当てることができます。

/skillsで確認するところを ctrl + x → sでできるということです。

これは慣れるとすごく早い作業を行うことができます

* leader + u 戻る
* leader + r 次へ
* leader + n 新しいセッション
* leader + l セッション一覧表示

など..

他にも theme がたくさんあったり、自分でコマンドを作成できたりします

<https://opencode.ai/docs/ja/cli/>  
*OpenCode CLIの操作画面とTODO管理*  
![](https://static.zenn.studio/user-upload/f3bb24745bef-20260522.png)

### Web で動く OpenCode が優秀

OpenCode には Web 版があります。

と入力すると、この画面が開けます。

![](https://static.zenn.studio/user-upload/8be87d07c64a-20260522.png)

左に表示されているアイコンで、リポジトリごとに分けることができます。

ワークスペースごとにworktreeを分けることができ、並列にタスクを進めることができます。

### Model の使い分け

モデルは簡単に使い分けることができます。

使用例は以下です。

* 壁打ちしたいときは Claude に投げる：設計用
* 実装は Codex に任せる：書き込み用
* エラーを読むときは DeepSeek を使う：料金が安い

Codex や Claude Code は完成度が高い一方で、基本的にはそれぞれのサービスに寄った使い方になります。

OpenCode はそのあたりの自由度が高いです。

## Skills について

OpenCode の skills を認識する条件は、以下のような構成になっていることです。

また、`SKILL.md` にディレクトリと同じ `name` と `description` があることが条件です。

Codex は同じ条件なので、基本的に互換性があります。

一方 Claude Code は `name` が任意なので、`name` がない場合は OpenCode で読み取れない可能性があります。

また、Claude Code 標準の skills などは使用できません。

Plugin については、hooks は使用できません。

### OpenCodeのセットアップ

以下のコマンドを実行することでOpenCodeをインストールすることができます。

```
npm install -g opencode-ai
```

次にOpenCodeを起動しましょう

最後にmodelをつなげて終了です！

## まとめ

カスタマイズ性が非常に高く、  
model を切り替えて使いたい人には非常におすすめできるツールです！
