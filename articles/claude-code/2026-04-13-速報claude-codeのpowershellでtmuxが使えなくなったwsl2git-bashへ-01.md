---
id: "2026-04-13-速報claude-codeのpowershellでtmuxが使えなくなったwsl2git-bashへ-01"
title: "【速報】Claude CodeのPowerShellでtmuxが使えなくなった！WSL2/Git Bashへの乗り換え方法を徹底解説 🚨"
url: "https://note.com/alvis8039/n/n00e528c13156"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

「あれ？なんかtmuxが動かなくなった…🤔」

2026年4月12日ごろのClaude Codeアップデートの後、そんな声があちこちから聞こえてきました。

実はAnthropicがPowerShellツールのセキュリティを大幅に強化したことで、WindowsのPowerShellからtmuxを使ったペイン分割やエージェントチーム機能が事実上ブロックされるようになったんです😱

「え、ZWG Terminalで使えなくなるの？」「どうすればいいの？」と焦った方も多いはず。

ご安心を。解決策はあります。WSL2またはGit BashをデフォルトシェルとしてClaude Codeを起動する方法に切り替えるだけで、tmuxがちゃんと使えるようになりますよ✨

## 🔴 何が起きたの？──PowerShellとtmuxの関係

まず状況を整理させてください。

Claude CodeはWindowsでtmuxを使う際、内部で process.stdout.isTTY という値を確認してターミナル環境を判断しています。ところが、Bun SFEというClaude Codeが使っている実行環境では、Windowsでこの値が常に undefined（未定義）になってしまう、という既知のバグがありました（GitHub Issue [#26244](https://note.com/hashtag/26244) ）。

これは以前から問題ではあったんですが、今回のアップデートでPowerShellツールのセキュリティがさらに硬化されたことで、状況がより厳しくなりました。具体的には：

* バックグラウンドジョブの抜け穴をふさぐ処理が強化された
* -ErrorAction Break によるデバッガーハングの修正
* Expand-Archive などのアーカイブ展開コマンドのパス安全性チェック強化
* コマンド引数のパースに失敗した際のフォールバックルールが「拒否」に変更された

要は、セキュリティのネジが締め直されたんです🔩

その影響で、PowerShellからtmuxのペイン分割コマンド（split-window、send-keys など）を呼び出す処理がことごとくブロックされるようになってしまいました。

あなたはZWG Terminalでtmuxを活用してAIコーディングをしていましたか？

## 🟡 なぜWSL2/Git Bashなら動くの？

「じゃあなんでWSL2やGit Bashなら動くの？」という疑問、もっともです。

WSL2（Windows Subsystem for Linux 2）の中では、LinuxネイティブのtmuxバイナリがそのまX動きます。process.stdout.isTTY の問題もなく、Claude Codeはきちんとターミナル環境を認識してtmuxモードに切り替わります。

Git Bashの場合も同様で、MINGWというLinux互換レイヤーを経由することでtmuxの動作環境が整います。

実のところ、GitHub上ではWindowsネイティブでtmuxを動かすための psmux というRust製ツールも登場しています。76個のtmuxコマンドに対応し、PowerShell 7・5、cmd.exe、Git Bash、WSLすべてを同一セッションで扱える優れもの。ただしまだClaude Codeとの公式統合は開発中なので、現時点では公式サポートのあるWSL2/Git Bashを使うのが一番確実です。

## ✅ 今すぐできる！WSL2/Git Bashへの切り替え方法

### ① WSL2をデフォルトにする場合

**手順：**

1. Windowsターミナルを開く
2. 「設定」→「スタートアップ」
3. 「既定のプロファイル」を **Ubuntu（または任意のLinuxディストリ）** に変更
4. WSL2のターミナルから以下を実行：

bash

```
# Claude Codeを起動
claude
```

ZWG Terminalをお使いの方は、設定画面でデフォルトシェルをWSL2のシェルパス（例：wsl.exe）に変更してから起動してください。

1. tmuxセッションを張ってからClaude Codeを起動：

bash

```
tmux new-session -s dev
claude
```

これでエージェントチームのペイン分割が復活します🎉

### ② Git Bashをデフォルトにする場合

Git for Windowsをインストール済みの方はこちらが手軽です。

1. Windowsターミナルの設定で「Git Bash」を既定のプロファイルに設定
2. あるいは直接 Git Bash を起動
3. tmuxがインストール済みであれば：

bash

```
tmux new-session -s mywork
claude
```

で動作するはずです。

Git BashでのtmuxはMSYS2経由でインストールできます：

bash

```
pacman -S tmux
```

ZWG Terminalでは、シェル設定から C:\Program Files\Git\bin\bash.exe をデフォルトシェルとして指定することで対応できます💡

もし今まで何のシェルを使っていたか覚えていない方は、どちらを試してみるとよいでしょうか？

## 📋 Claude Codeのtmux設定をおさらい

せっかくなので、tmuxを正しく使うための設定も確認しておきましょう。

**settings.jsonでのtmux設定例：**

json

```
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**tmuxセッション内でのAgent Teams有効化：**

bash

```
# セッション開始
tmux new-session -s claude-dev

# Claude Code起動
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude
```

この環境変数を設定することで、tmuxのペイン分割を使ったマルチエージェントチームが有効になります。

**ZWG Terminalユーザーへの補足：**

ZWG Terminal v1.3.0の場合、ターミナル設定から「デフォルトシェル」をWSL2またはGit Bashのパスに設定し直してから、上記のコマンドを実行してください。DirectX 12 GPUレンダリングの恩恵はそのまま受けながら、tmuxのマルチペイン機能も活用できるようになります✨

## 🔮 今後の見通し──psmuxという希望の光

少し先の話をすると、実は「psmuxでWindowsネイティブ対応を実現しよう」というGitHub Issue（#34150）が立てられていて、コミュニティで活発に議論されています。

psmuxはRust製のWindowsネイティブtmux実装で、WSLなしでもtmuxコマンドが使えるツールです。Claude Codeの検出ロジックに小さな変更を加えるだけで統合できるとされており、将来的にはWSL2なしでPowerShellからtmuxが使えるようになるかもしれません。

とはいえ、2026年4月現在では実験的な段階。公式サポートが整うまでは、WSL2/Git BashでClaude Codeを起動するのが最も安定した解決策です🌟

## ✨ まとめ

今回の変更を整理するとこうなります。

* Claude Codeの4月アップデートでPowerShellツールのセキュリティが強化された
* その影響でPowerShellからのtmux操作がブロックされる状態になった
* 根本原因はBun SFE on Windowsにおける process.stdout.isTTY バグ（Issue [#26244](https://note.com/hashtag/26244) ）
* **今すぐの対処法：WSL2またはGit BashをデフォルトシェルとしてClaude Codeを起動する**
* ZWG Terminalではデフォルトシェル設定をWSL2/Git Bashに変更するだけでOK
* 将来的にはpsmux統合によるWindowsネイティブ対応が期待される

「また仕様変更か〜😅」と思う気持ちはよくわかります。でも、セキュリティが強化されたということはそれだけツールが成熟してきているということでもあります。

一度WSL2をメインにしてしまえば、Linux環境の恩恵でむしろ開発体験が上がることも多いですよ。この機会に、ぜひWSL2環境を整えてみてくださいね💪

## 参考リンク 🔗

皆様の意見はどうでしょうか？   
良かったらコメントで教えて下さい。   
フォロー＆スキもお願いします♪

この記事への感想やご質問、お仕事のご依頼など、   
お気軽にメッセージをお送りください♪   
📩 メッセージはこちらから

[#ClaudeCode](https://note.com/hashtag/ClaudeCode) [#PowerShell](https://note.com/hashtag/PowerShell) [#WSL2](https://note.com/hashtag/WSL2) [#tmux](https://note.com/hashtag/tmux) [#Windows開発](https://note.com/hashtag/Windows%E9%96%8B%E7%99%BA) [#AIコーディング](https://note.com/hashtag/AI%E3%82%B3%E3%83%BC%E3%83%87%E3%82%A3%E3%83%B3%E3%82%B0) [#GitBash](https://note.com/hashtag/GitBash) [#ターミナル](https://note.com/hashtag/%E3%82%BF%E3%83%BC%E3%83%9F%E3%83%8A%E3%83%AB) [#開発環境](https://note.com/hashtag/%E9%96%8B%E7%99%BA%E7%92%B0%E5%A2%83) [#エラー解決](https://note.com/hashtag/%E3%82%A8%E3%83%A9%E3%83%BC%E8%A7%A3%E6%B1%BA) [#Anthropic](https://note.com/hashtag/Anthropic) [#AI開発](https://note.com/hashtag/AI%E9%96%8B%E7%99%BA) [#プログラミング](https://note.com/hashtag/%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0) [#Windows](https://note.com/hashtag/Windows) [#ZWGTerminal](https://note.com/hashtag/ZWGTerminal) [#エージェントチーム](https://note.com/hashtag/%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%E3%83%81%E3%83%BC%E3%83%A0) [#Claude](https://note.com/hashtag/Claude) [#開発ツール](https://note.com/hashtag/%E9%96%8B%E7%99%BA%E3%83%84%E3%83%BC%E3%83%AB) [#テクノロジー](https://note.com/hashtag/%E3%83%86%E3%82%AF%E3%83%8E%E3%83%AD%E3%82%B8%E3%83%BC) [#ITニュース](https://note.com/hashtag/IT%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9)
