---
id: "2026-05-04-claude-codeユーザーのためのcodex入門-01"
title: "Claude CodeユーザーのためのCodex入門"
url: "https://zenn.dev/k9i/articles/20260504_cc_to_codex"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

最近、CodexのほうがClaude Codeより使いやすい・性能が高いと感じる人が増えている印象です。  
Claude Codeに慣れていて、Codexも使い始めてみたい方向けに、最初に知っておくとよいことを書きます！

この記事は2026年5月時点の私の利用経験と観測範囲をもとにしています。

### 私のCodex歴について

もともとはClaude Code派で、Codexは半年ほどサブで使っていました。  
GPT-5.4あたりでClaudeとモデル性能が逆転したと感じ、1ヶ月ほど前に個人では完全にCodexに乗り換えました（業務では申請のしやすさとかもあってClaude Codeも引き続き使ってます）

![claudeのコミットが減っていることで、Codexを使ってると分かる](https://static.zenn.studio/user-upload/deployed-images/dfb314e6250e5d82cf4d6193.png?sha=1fdca08e8b56071d5f822fda99bc3894eae390a6)  
*claudeのコミットが減っていることで、Codexを使ってると分かる*

### なぜCodexが選ばれるのか

私の主観とXで見かける投稿ベースだとこんな感じです

* GPT-5.5の性能が高い
* Claude CodeはOpus 4.6あたりから応答品質に不満を持つ声が増え、Opus 4.7でそれを強く感じる人が増えた
* 同じサブスク料金ならCodexのほうが多く使える
* ツール面で遅れていたが、Codex Appが進化して使いやすくなった
* OpenAIがOpenClawを始めとしたサードパーティツールに寛容
* 公式が用意しているApp Serverプロトコルで、自前アプリに組み込んだりもできる

モデル性能、料金プラン、ツールのUI/UXのいずれかでCodexが優れてると感じる人が増えてます

## Claude Codeユーザーが知っておくべきこと

ここからは、Claude Codeの機能がCodexだとどう対応するのかを中心に書いていきます

### CLI より Codex Appがおすすめ

Claude CodeはCLIで使うのが一般的だと思いますが、私の観測範囲ではCodexユーザーはCLI版よりデスクトップアプリであるCodex Appを使っている人が多そうです。  
Codexの設定はCLIからだと正直不親切で分かりづらいですが、Codex Appだと設定画面がかなり作り込まれてます。

<https://developers.openai.com/codex/app/settings>

### サブスクプランについて

一応ChatGPTの無料アカウントでもCodexは使えますが、本格的に使うなら3000円のPlus、16800円もしくは30000円のProを検討するのがよさそうです。  
ProはPlusにくらべCodexの利用量が増えて、16800円なら5倍（期間限定で10倍）、30000円なら20倍になります。

<https://chatgpt.com/ja-JP/pricing/>

#### PlusとProの使い分け

最新のGPT-5.5をガッツリ使いたいならProがおすすめです  
安く済ませたい場合はPlusプランで、GPT-5.4を使うのも良いと思います。GPT-5.4も十分高性能です！

### モードについて

Claude CodeのPermissionモード（default, accept edits, plan mode, auto mode, bypass permissions）に対応する機能はCodexだと少し複雑です。

少なくとも4つの項目に分かれています

#### approval

Permissionモードに最も近い項目

* Untrusted: 既知の安全な読み取り系コマンドは自動で実行し、状態を変更するコマンドや外部実行につながるコマンドでは確認する
* On Request: workspace内の読み取り・編集・コマンド実行は自動で行い、workspace外の編集やネットワークアクセスなどで確認する
* On Failure: コマンドが失敗したときに確認するモード（現在は非推奨。対話的に使うならOn Request、非対話実行ならNever Askが推奨）
* Never Ask: 承認プロンプトを出さず、設定されたsandboxの制約内で自動実行する（後述の.rulesでdecisionをpromptにした場合も失敗になる）

<https://developers.openai.com/codex/agent-approvals-security>

#### plan

Claude Codeでいうplan modeは、Codexだとapprovalとは独立してon/offできます  
CodexだとAIがユーザーに複数択で質問するAskUserToolはplan中しか有効じゃなかったりします（質問してと依頼しても選択UIがでないのはこの影響）

#### reviewer

ツールのレビューをユーザーが行うか、AIが行うかの項目  
approvalをOnRequest、reviewerをauto\_reviewにすると、Claude Codeのauto modeのようになる

#### sandbox

Claude CodeのPermissionモードには含まれない概念ですが、Codexではsandboxのon/offもapprovalとセットで扱われます

#### モードについてのまとめ

長々と書きましたが、Codex Appだとこれらが簡単に丸められています  
approval/reviewer/sandboxはデフォルト権限/自動レビュー/フルアクセスの3つにまとめられ、追加でplanのon/offがトグルできます

![Codex Appのモード切り替えUI](https://static.zenn.studio/user-upload/deployed-images/42b6a0b9e370adbbac5797cc.png?sha=6739a9f3975d81b1963f2adb105bde0fe2c8f20b)  
*Codex Appのモード切り替えUI*

### 設定ファイルについて

Codexでは、グローバルとプロジェクト配下の.codexに設定ファイルを置けます。  
全般的な設定ができるconfig.tomlとコマンド許可に特化した.rulesです。  
注意点としてプロジェクトかつ個人向けの設定を書くclaudeのsettings.local.jsonみたいなのはCodexには無いです（グローバルのconfig.tomlにprofileを作ると近いことはできます）

#### config.toml

詳細は公式ドキュメントを見てもらうのがいいですが、デフォルトのモデルやMCPの設定などを記述します  
Codex AppのUI上で設定をいじるとグローバルのconfig.tomlに反映されています

<https://developers.openai.com/codex/config-basic>

#### .rules

コマンドの許可設定を記述します  
patternのリストがコマンドのprefixにマッチすると発動  
decisionをallow（許可）, prompt（確認）, forbidden（ブロック）の3つから選びます

forbidden > prompt > allowの順で優先されるので、サブコマンドだけ禁止したい場合は広くallowしておいて、サブコマンド含めたprefixをforbiddenしておくとよいです

公式から引用

```
# Prompt before running commands with the prefix `gh pr view` outside the sandbox.
prefix_rule(
    # The prefix to match.
    pattern = ["gh", "pr", "view"],

    # The action to take when Codex requests to run a matching command.
    decision = "prompt",

    # Optional rationale for why this rule exists.
    justification = "Viewing PRs is allowed with approval",

    # `match` and `not_match` are optional "inline unit tests" where you can
    # provide examples of commands that should (or should not) match this rule.
    match = [
        "gh pr view 7888",
        "gh pr view --repo openai/codex",
        "gh pr view 7888 --json title,body,comments",
    ],
    not_match = [
        # Does not match because the `pattern` must be an exact prefix.
        "gh pr --repo openai/codex view 7888",
    ],
)
```

<https://developers.openai.com/codex/rules>

### リモート操作について

記事執筆時点では、スマホから直接Codex AppやCLIのセッションを操作する公式体験はまだ限定的です（モバイルアプリを出すぽい匂わせはある）  
ただCodexの場合はサブスク枠で、サードパーティツールの利用が可能なのでそちらで補うことができます

私の作っているCC Pocketを活用するとスマホからCodexを利用できるので、よかったら試してみてください

GitHub:  
<https://github.com/K9i-0/ccpocket>

LP:  
<https://k9i-0.github.io/ccpocket/install/>

## まとめ

自分がCodex使い始めたころに、知っておきたかったことを書きました  
間違ってるところあったら教えてください！
