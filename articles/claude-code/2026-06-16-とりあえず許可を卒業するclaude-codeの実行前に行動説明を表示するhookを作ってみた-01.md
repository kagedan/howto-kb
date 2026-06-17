---
id: "2026-06-16-とりあえず許可を卒業するclaude-codeの実行前に行動説明を表示するhookを作ってみた-01"
title: "「とりあえず許可」を卒業する：Claude Codeの実行前に行動説明を表示するHookを作ってみた"
url: "https://zenn.dev/nttdata_tech/articles/d2edb6a9fe5d7f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-06-16"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは、株式会社NTTデータグループの松本です。  
今回は、Claude CodeのHookを使って、Claudeによるコマンド実行やファイル編集を説明させることで、ユーザーからの行動許可を根拠をもって安全に判断できる仕組みを作ってみました。

私は日々AIを使って業務をしており、プライベートでもClaude Codeを中心に触っています。  
そんな中で、最近こんな自問をすることが増えました。  
**「あ、これ許可していいやつだっけ...？」**

Claude Codeはファイル編集やコマンド実行の前に許可を求めてくれます。  
これは安全のための大事な仕組みですが、特にClaude Codeを使い始めたばかりの方や、新人エンジニアの方で、次のような経験はないでしょうか？

* 表示されたコマンドやプログラム差分をよく読まずに「とりあえず許可」してしまう
* 「Always allow」はセキュリティ的に危なそうなので都度確認にしているが、結局コマンドやプログラム差分の意味が分からず、「多分大丈夫だろう」となんとなく許可している
* 大量の変更をまとめて提案され、影響範囲が分からないまま許可してしまう

許可ダイアログが表示されても、「何をしようとしているのか」「どんな影響があるか」が分からないまま「Yes」を押してしまっては、せっかくの安全機構が形骸化してしまいます。

そこで本記事では、Claude Codeの**CLAUDE.md**と**Hooks**を組み合わせて、ユーザーに許可を求める前に「何をしようとしているのか」「どんな影響があるのか」をClaude自身に説明させ、ユーザーが確認・承認の判断をしやすくする仕組みを作ります。

## 完成形

セットアップが終わると、Claude Codeがツールを実行しようとしたタイミングで、次のような確認メッセージが表示されます。

**Bashコマンドを実行しようとしたとき**  
許可ダイアログが出る前に、こうした説明が表示されるようになります。

```
🔐 Claude Code が許可を求めようとしています
- ツール: Bash
- 内容:
実行予定コマンド: rm -rf node_modules && npm install

Claudeによる説明:
【やろうとしていること】
node_modulesを削除して、package.jsonに基づいて依存関係をクリーンインストールし直します。

【影響】
・対象範囲: プロジェクト直下のnode_modules/とpackage-lock.json
・可逆性: package-lock.jsonはgit管理下なのでrevert可能。node_modulesは再インストールで復元可能
・副作用: npm registryへの外部通信、postinstallスクリプトの実行
・セキュリティ: 秘密情報の読み書きはなし
・想定外時のリスク: ネットワーク失敗時はnode_modulesが中途半端な状態になる可能性あり

確認ポイント:
1. この操作が本当に必要か
2. 変更・削除・外部通信・秘密情報の読み取りが含まれないか
```

**ファイル編集をしようとしたとき**  
ファイル編集の場合は、許可ダイアログ自体が編集前後の差分を表示してくれるので、Hookでは「直前のClaudeの説明を確認しよう」という案内を出します。

```
🔐 Claude Code が許可を求めようとしています
- ツール: Edit
- 内容:
対象ファイル: /Users/{username}/project/src/config.js

👆 許可ダイアログで編集前後の内容を確認できます。
👆 直前のClaudeの発話で、以下2点が説明されているか確認してください:
   ・どんなことをやろうとしているのか
   ・その行動によってどんな影響があるのか

確認ポイント:
1. この操作が本当に必要か
2. 変更・削除・外部通信・秘密情報の読み取りが含まれないか
```

これにより、Claudeの行動を一から自分で理解してから許可するのではなく、**Claudeの説明**と**実際にツールへ渡される入力**を照合してから判断できるようになります。

## 仕組みの全体像

この仕組みは、2つのレイヤーで構成されています。  
![Claude CodeのHooksとCLAUDE.mdを組み合わせた仕組みの全体像](https://static.zenn.studio/user-upload/b18b7c1e594e-20260526.png)

### **レイヤー1: CLAUDE.md**

CLAUDE.mdにルールを書くことで、Claudeに対して「2観点(やろうとしていること/影響)を必ず説明する」というルールを与えます。

これは、Claudeのプロンプトレベルでの制約です。

コマンド実行やファイル編集などのツール実行の許可ダイアログが出る直前に、Claudeがツールに渡そうとしている実データを整形して表示します。

これは、Claude Codeの仕組みとして強制される検証レイヤーです。

本記事では、ツール実行前に発火する`PreToolUse`を使います。  
`PreToolUse` Hookでは、Claudeがツールへ渡そうとしている`tool_name`や`tool_input`を受け取れます。  
例えば、Bashであれば実行予定のコマンド、Editであれば対象ファイルなどを確認できます。

---

Claude Codeには、`PermissionRequest`というHookもあります。  
名前だけ見ると、今回のような「許可前に説明を出したい」用途では、`PermissionRequest`が自然に見えるかもしれません。

ただし、下図のフックライフサイクルの図のように、両者は動くタイミングが異なります。  
`PermissionRequest`は、許可ダイアログが表示されるタイミングで動くHookです。  
一方、`PreToolUse`は、ツール呼び出しが実行される直前に動くHookです。

つまり、今回やりたいことは「許可プロンプトを自動で処理すること」ではなく、以下の目的には、`PreToolUse`の方が適しています。

* ツールが実行される前に、実際の入力内容を確認する
* Bashのコマンド内容や、Edit/Writeの対象ファイルを表示する
* Claudeの説明と実際の`tool_input`を照合できるようにする

以上の理由から、本記事では`PreToolUse`を使って、ツール実行前の安全確認レイヤーを作ることで、許可ダイアログで「とりあえず許可」を防止します。

![Hookライフサイクル](https://static.zenn.studio/user-upload/cc4d03bd9aa7-20260526.png)  
[公式ドキュメント](https://code.claude.com/docs/en/hooks)から引用

### なぜCLAUDE.mdとHooksの両方を使うのか

CLAUDE.mdは万能ではありません。  
ルールを書いたからといってClaudeが100%守るとは限らず、必ず行動の説明をさせることはできません。  
つまり、ユーザーに行動の説明をせずにその行動の許可を求めることがあります。

一方、Hooksだけでは、ツール入力の生データは表示できますが、それがなぜ必要でどんな影響があるかという文脈は伝えられません。

両方を組み合わせることで、「Claudeの説明」と「実際にツールに渡すデータ」を並べて確認できるようになり、説明と実態の照合が可能になります。  
CLAUDE.mdが守られなかったときも、Hooksが最後の砦として実データを見せてくれます。

## セットアップ

ここから、実際に設定していきます。  
手順は以下の3つのステップです。

1. CLAUDE.mdにルールを追記する
2. Hookスクリプトを作成する
3. `settings.json`にHookを登録する

!

**📝 注釈: 設定の適用範囲について**  
この記事では、`~/.claude/`配下に設定を置く「グローバル設定」の手順を紹介します。  
全てのプロジェクトで共通の動作になるので、まずはこの構成がおすすめです。

特定のプロジェクトでだけこの仕組みを使いたい場合は、以下のように読み替えてください。

* `~/.claude/CLAUDE.md`  
  → プロジェクトルートの`./CLAUDE.md`
* `~/.claude/hooks/explain-permission.js`  
  → プロジェクトルートの`./.claude/hooks/explain-permission.js`
* `~/.claude/settings.json`  
  → プロジェクトルートの`./.claude/settings.json`

なお、プロジェクト設定はグローバル設定よりも優先されます。  
チームで共有したい場合はプロジェクト配下に置いてgit管理するのがおすすめです。

### Step 1: CLAUDE.mdにルールを追記する

`~/.claude/CLAUDE.md`を開いて(なければ新規作成)、以下を追記します。

```
## コマンド実行・ファイル編集の事前説明ルール

Bash/Edit/Write/MultiEdit を実行する前に、必ず以下の2観点を日本語で説明すること。

### 説明の観点

1. **どんなことをやろうとしているのか**: 操作の目的と内容
2. **その行動によってどんな影響があるのか**: 対象範囲、可逆性、副作用、セキュリティ、想定外時のリスク

### ツール別の出し方

**Bash の場合**: ツールの `description` フィールドに、以下の形式で記入する。

```
【やろうとしていること】
(目的と内容)

【影響】
・対象範囲: ...
・可逆性: ...
・副作用: ...
・セキュリティ: ...
・想定外時のリスク: ...
```

**Edit/Write/MultiEdit の場合**: ツール実行の**直前のアシスタント発話**で、上記2観点を明示して説明する。

複数の操作をまとめて実行する場合は、操作ごとに上記を説明する。
```

このルールにより、Claudeに「実行前に説明する」習慣を持たせます。  
ただし、これはあくまでプロンプトレベルのルールです。  
そのため、次にHookで実際のツール入力を確認できるようにします。

### Step 2: Hookスクリプトを作成する

ディレクトリを作ってスクリプトを配置します。

`~/.claude/hooks/explain-permission.js`を以下の内容で作成します。

explain-permission.js

```
#!/usr/bin/env node
let input = "";
process.stdin.on("data", chunk => input += chunk); 
process.stdin.on("end", () => {
  const event = JSON.parse(input);
  const tool = event.tool_name;
  const toolInput = event.tool_input || {};
  let detail = "";

  if (tool === "Bash") {
    detail = `実行予定コマンド: ${toolInput.command || "(不明)"}`;
    if (toolInput.description) {
      detail += `\n\nClaudeによる説明:\n${toolInput.description}`;
    } else {
      detail += `\n\n⚠️ Claudeからの説明がありません。「やろうとしていること」と「影響」の説明を求めてください。`;
    }
  } else if (tool === "Edit" || tool === "Write" || tool === "MultiEdit") {
    detail = `
      対象ファイル: ${toolInput.file_path || "(不明)"}
      👆 許可ダイアログで編集前後の内容を確認できます。
      👆 直前のClaudeの発話で、以下2点が説明されているか確認してください:
        ・どんなことをやろうとしているのか
        ・その行動によってどんな影響があるのか
    `;
  } else if (tool === "Read") {
    detail = `対象ファイル: ${toolInput.file_path || toolInput.path || "(不明)"}`;
  } else {
      detail = `入力内容: ${JSON.stringify(toolInput, null, 2)}`;
  }

console.log(`
  🔐 Claude Code が許可を求めようとしています
  - ツール: ${tool}
  - 内容:
  ${detail}

  確認ポイント:
    1. この操作が本当に必要か
    2. 変更・削除・外部通信・秘密情報の読み取りが含まれないか
  `);
});
```

作成したら、実行権限を付与します。

```
chmod +x ~/.claude/hooks/explain-permission.js
```

### Step 3: settings.jsonでHookを登録する

`~/.claude/settings.json`を開いて(なければ新規作成)、以下の内容にします。  
既存の設定がある場合は`hooks`セクションだけマージしてください。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "node ~/.claude/hooks/explain-permission.js"
          }
        ]
      }
    ]
  }
}
```

`matcher: "*"`と設定しているため、全てのツール呼び出しを対象にしています。

## 動作確認

セットアップが終わったら、動作を確認します。

### スクリプト単体で確認する

Claude Codeを起動する前に、ターミナルからHookスクリプト単体で動作確認できます。

```
echo '{
  "tool_name": "Bash",
  "tool_input": {
    "command": "ls -la",
    "description": "【やろうとしていること】\nファイル一覧表示\n\n【影響】\n・対象範囲: カレントディレクトリのみ\n・可逆性: 該当なし(読み取りのみ)"
  }
}' | node ~/.claude/hooks/explain-permission.js
```

以下と同じような出力が表示されればOKです。

```
🔐 Claude Code が許可を求めようとしています
- ツール: Bash
- 内容:
実行予定コマンド: ls -la

Claudeによる説明:
【やろうとしていること】
ファイル一覧表示

【影響】
・対象範囲: カレントディレクトリのみ
・可逆性: 該当なし(読み取りのみ)

確認ポイント:
1. この操作が本当に必要か
2. 変更・削除・外部通信・秘密情報の読み取りが含まれないか
```

説明なしのケースも確認しておきましょう。  
ターミナルで以下を入力し、`⚠️ Claudeからの説明がありません。`の警告が出ればOKです。

```
echo '{
  "tool_name": "Bash",
  "tool_input": {"command": "curl https://example.com"} }'
  | node ~/.claude/hooks/explain-permission.js
```

これで単体動作が確認できたので、次は実際にClaude Codeで動かしてみましょう

### Claude Code上での確認

Claude Codeを起動して、登録状況を確認します。

`PreToolUse`のセクションに`node ~/.claude/hooks/explain-permission.js`が表示されていればOKです。  
![/hooksの結果1](https://static.zenn.studio/user-upload/911a8f49ec2c-20260526.png)  
![/hooksの結果2](https://static.zenn.studio/user-upload/2f91620a8a98-20260526.png)

実際にコマンド実行を依頼してみます。

> `touch /tmp/hook-test.txt`を実行してください

許可ダイアログの直前にHookの出力が表示されれば成功です。

## まとめ

本記事では、Claude Codeの許可ダイアログを「とりあえず許可」してしまう問題に対して、**CLAUDE.md**と**Hooks**の2つのレイヤーを組み合わせ、Claudeがツール呼び出しを実行する前に**その行動の説明を表示する**仕組みを紹介しました。  
これにより、「許可ダイアログでとりあえず許可する」習慣を改善できます。

Hooksの仕組みは今回の事前説明以外にも応用できます。  
シェルコマンドであれば何でも実行できるので、用途に応じて柔軟に拡張できます。

皆さんもぜひHooksを活用してみてください！

**Hooksを応用した改善案**

* 危険コマンド(`rm -rf` など)を検知して警告色や警告メッセージを追加
* 操作ログをファイルに記録して、あとから監査できるようにする
* 説明文の長さや観点の充足度をチェックして、不十分なら警告
* 特定のディレクトリ配下の編集だけ追加の確認を要求する

## 参考リンク
