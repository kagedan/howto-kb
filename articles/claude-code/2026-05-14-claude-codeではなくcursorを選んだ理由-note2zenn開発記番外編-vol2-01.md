---
id: "2026-05-14-claude-codeではなくcursorを選んだ理由-note2zenn開発記番外編-vol2-01"
title: "Claude Codeではなく、Cursorを選んだ理由 ｜ note2Zenn開発記（番外編 / Vol.2）"
url: "https://zenn.dev/hanav1ye/articles/note2zenn-vol2"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "Gemini", "GPT", "zenn"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

**Claude Code**は非常に優れたツールです。  
非エンジニアの方でもnoteを見ていたら、  
言葉を見たことがある方も多いと思います。  
開発だけでなく、さまざまなことに活用できる**AIエージェント**です。

逆にCursorはエンジニアの方には馴染みがあるかもしれませんが、  
非エンジニアの方にはあまり知られていないかもしれません。  
CursorもClaude Codeと同様のタスクをこなせますが、  
私は**使用感や役割が明確に異なる**と考えています。

## Cursor × Claude Code

簡単に違いを示します。

![image](https://static.zenn.studio/user-upload/deployed-images/138baf29f28c97fb4118b8aa.png?sha=1e1028d5dabcc8da0867c92fdfbc4528716692ca)  
**Cursor**は**VS Codeというコードエディタとほぼ同じ使用感**で、  
エンジニア視点から見ても使いやすいツールです。  
コード補完や差分表示がわかりやすく、  
『なんでも答えてくれる助手』です。

**Claude Code**は**AIエージェントと呼ばれ、  
『「タスク」を与え、実施してもらう』が基本スタイル**です。  
エディタを超えた処理が可能で、  
デバッグやブラウザ上でのテストも行えます。

なお、CursorはAutoモードを使用している場合、  
ユーザーの指示内容に応じて使用するAIモデルを切り替えます。

![これらが選べるAIモデル。ただの相談くらいならGPTにして、コードを書くときはCodex, Sonnet(Claude)とかにしたりできます。](https://static.zenn.studio/user-upload/deployed-images/b12241da6e8ad2f89240a82e.png?sha=dff6ddb55eb3ebea3d4ef0b3aefa455553c4bce8)  
これらが選べるAIモデルです。  
ただの相談くらいならGPTを使用し、  
コードを書くときはSonnet(Claude)を使用できます。  
そのため、Cursorが大きくコーディング性能が劣化する  
ことはないと考えています。  
※詳細なスペックの差よりも、実用上の使用感を重視しています

## なぜ、私が今回Cursorを採用したか

私がCursorを採用した理由は大きく2つあります。

### ➡①コードを理解した上で開発することがモットー！

Cursorはコードエディタ上で動作するため、  
**常にソースを確認しつつ、指示を出すことができます。**  
”特定のここを”や”このファイルを見て！”  
という渡し方も非常に容易です。

Claude Codeも同じことは可能ですが、  
使用感が大きく異なります。CLI上で出力される差分や、  
適用または却下というのが基本スタイルのため、  
**何が書かれているかの理解度に大きく差が生じる**と思いました。

先に述べた通り、**同じことはできます**。  
それでも無意識に理解しておきたいという考えを重視しています。

### ➡②安心できる料金体系！

![image](https://static.zenn.studio/user-upload/deployed-images/78b048b9635f8e6b50271e94.png?sha=ddba19e62d688c4204babd24f9b527b0205e72bb)  
料金周りの比較はこのようになります。  
Claude Codeはプラン上限を超えると  
従量課金が始まります。

完全に個人的な感覚ですが、  
AI駆動に慣れていない私が  
Claudeを使うと0から1を何度かやり直す可能性がありそうです。  
そのため、**いくらやっても固定料金！が安心です。**

まあ全然足りたじゃんという結果もあるかもしれませんが。

これでうまくいくはずだという見通しがあれば、  
**規模感からトークンをどのくらい消費するかイメージできる**  
ようになれば、計画的にClaudeも使えるのですが・・・

お金がたくさんあればそんなことを考えなくて済むのですが。  
現状のリソースで考えた結果、今はCursorを選択しました。

## Cursor課金の流れ

私が課金したときの流れを示します。  
まず、無料版を使い切った状態で、  
Cursor上のAgentウィンドウに指示すると以下のようになります。

![image](https://static.zenn.studio/user-upload/deployed-images/ef39ee07d2a7f6d12af0e404.png?sha=fac6ca6530fc6717d3e611e060df0996c01a7c4a)  
右上の歯車アイコンからも確認できます。

![image](https://static.zenn.studio/user-upload/deployed-images/e065927fa9d0495773bba239.png?sha=1bd8d6812dc2b5926c3a144ced2a87a4ef0cdf88)  
[Upgrade to Pro now]からProプランに課金しようと思います。

![ログイン画面が出てくるのでログインしましょう。Cursorをインストールする際に登録しているはずです！](https://static.zenn.studio/user-upload/deployed-images/6ace95e642d1373a22e08bc6.png?sha=d1c2fdd406c4eea2cf4c2ccd18e849d2ca12bebb)  
ログイン画面が出てくるのでログインしましょう。  
Cursorをインストールする際に登録しているはずです。

![ログインするとこの画面にいけます。赤枠のところがProプランなのでこちらにします！](https://static.zenn.studio/user-upload/deployed-images/f494d27d5419841bbd5c01b2.png?sha=a10761217cc8c3b92a76cab9e155354d3c8da620)  
ログインするとこの画面にいけます。  
赤枠のところがProプランなのでこちらにします。

![海外の課金画面なのであまり見慣れないですが、円マークがあるので値段は想定通りですね！こちらを入力して更新します！](https://static.zenn.studio/user-upload/deployed-images/df6a7840d70d55d0b94b971b.png?sha=485f7ea04fc2cad8dad5dc63c5074b7773d83fa4)  
海外の課金画面なのであまり見慣れないですが、  
円マークがあるので値段は想定通りです。こちらを入力して更新します。  
先に述べた通り、Cursorは従量課金ではなく、  
月単位（または年単位）の固定料金のサブスクリプションです。  
※よくある年単位だと安くなるプラン（月700円くらい安くなる）。

私の開発スタイルは、  
”頻繁に”というよりは”一気に”なので、  
1ヶ月課金したら停止する予定です。  
その点も含めて自分に合ったものを選択しましょう。

登録後、再度Cursor内で確認すると以下のようになります。

![image](https://static.zenn.studio/user-upload/deployed-images/cc40431047d6bc47573ebb4a.png?sha=93ab9a83183fdd73272cb6824b5be7dfcef267b0)  
見ての通り、**どのくらいAPIを利用したかが確認できます。**  
**上限を超えると低速モードになる**ので注意が必要です。  
ただ**使われるAIモデルは同じ**なのでご安心ください。

## まとめ

ともかく自分に合ったスタイルで、  
AIは選択するのが良いと思います。  
成り行きで使うことになったAIと向き合うのも  
大事だと思います。

いろんな記事がある中で、どれが良いか  
という結論を出すのは難しいです。  
**使う人によって、合うものが変わるからです。**

私は普段はGeminiとCursorを使っていますが、  
GeminiはChatGPTを使って比較したわけではありません。  
スマホがAndroidだったからというのが大きいです。  
**だって容量ももらえるし、ありがたいです。**

開発に使うツールも手に取りやすいところから始めて、  
さまざまなツールに触れていきたいと思います。

以上、番外編の  
\*\*「Claude Codeではなく、Cursorを選んだ理由」\*\*でした！
