---
id: "2026-04-27-github-copilotの本当の強み-2-01"
title: "GitHub Copilotの本当の強み 2"
url: "https://zenn.dev/headwaters/articles/f79b8d64ba1442"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "zenn"]
date_published: "2026-04-27"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

## コスパじゃなくなりそう

[前回の記事](https://zenn.dev/headwaters/articles/0595f9c0a1fadb)で、GitHub Copilot の最大の強みは**コスパ**だと紹介しました。

しかし、6月1日から、GitHub Copilot の課金体系が変更されるようです。  
本日(2026/4/28)日本時間の午前1時頃、Githubから公式に発表がありました。  
<https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/>

現在の「プレミアムリクエスト」から「トークンベース」に変更されるとのことです。（恐れていたことが現実に…。）

そうなると、前回の記事はすぐに意味のないものになってしまい、  
私は**オクトキャットフィギュアをいただけなくなってしまいます**。

それは困る！まじで欲しいのに！  
ということで、個人的に助かっている GitHub Copilot の**機能的な強み**を紹介していきます。

!

この変更について、Githubを責めるのはお門違いです。  
当然の流れだと思います。

実際、Github Copilot は少し前から赤字である状況を報告していました。  
ユーザによってはたった1週間で月の損益分岐点に達してしまうこともあったのだとか。

正直、AIサービスはこれからもっと値上がりしていくと思います。  
明らかに電気を食いすぎている。

新しいチップや省エネなモデルの研究が進むことを祈るばかりです…。（**みんなSNNを研究しよう！**）

---

## VSCode との統合

散々言われていることかもしれませんが、GitHub Copilot は VSCode と**非常に密接に統合**されています。  
正直、ここが GitHub Copilot の唯一の強みであり、しかし、他のツールにはない最大の魅力だと思っています。

一言に統合と言っても色々あるので、個人的に特に助かっている点をいくつか紹介します。

### 1. DevContainerとの連携

GitHub Copilot は VSCode の DevContainer としっかり連携しています。

DevContainer とは

#### DevContainer とは

まず DevContainer について簡単な説明をしておきます。  
DevContainer は、VSCodeの機能の一つで、開発環境をコンテナ化して管理できる機能です。

これを使うと、プロジェクトごとに異なるコンテナの定義を用意し、その中で VSCode を動かせます。  
また、拡張機能や設定も定義ファイルに記載できるので、開発環境のすべてをコード化して管理できます。

すべての開発メンバで**完全に同じ環境を簡単に共有**できるのが大きなメリットです。

さて、DevContainer を使うとなった場合、他のツールだったらどうでしょうか？

例えば、Claude Code でコンテナ内で作業をしようと思うとめんどくさくないですか？  
ツールのインストールだけでなく、認証方法の検討も必要になりますよね。  
Claude Code を使っていないメンバーのことも考えたりすると、、あーめんどい、。

これがGitHub Copilotなら、DevContainerを立ち上げても**ローカルと全く同じ使用感で利用できます**。  
VSCode上で自動的に認証を引き継いでくれますし、ターミナル等も自然にコンテナ内のものを使ってくれます。

もちろんタブ補完も効きますし、コンテナ内のファイルの編集も行ってくれます。

コンテナ化の恩恵はそのままに、手間なくGitHub Copilotを利用できるのはとても大きなメリットです。

---

### 2. 拡張機能との連携

皆さん、VSCodeの拡張機能色々使ってますよね？

例えば、LinterやFormatterなどのコード品質を保つための拡張機能や、GitLensなどのGit管理を便利にする拡張機能など、様々なものがあると思います。  
GitHub Copilotはこれらの拡張機能と**自然に連携**してくれます。

例えば `editor.formatOnSave` という設定が有効になっていれば、GitHub Copilot が生成してくれたコードも自動で整形されます。

また、GitHub Copilot はツールを通して Linter の出力を確認できます。  
指示の中で「生成したコードにLinterの警告やエラーが無いか毎回チェックし、ある場合は修正してください」といった指示を出すことで、生成されたコードが Linter のルールに従うようにすることもできます。

他にも、拡張機能側で MCP ツールをサポートしていることがあります。  
その場合、GitHub Copilot が拡張機能をツールとして呼び出すことができ、AIの動きにより一層の柔軟性が生まれます。

---

### 3. 懐が深い

Github Copilot以外で契約しているAPIや、OllamaのようなローカルLLMを利用できます。  
**しかも無料。**

すでにAPIの契約がある方や、セキュリティの観点からローカルで完結させたい方にとっては、GitHub Copilotのこの懐の深さは非常にありがたいポイントです。

![image](https://static.zenn.studio/user-upload/deployed-images/4381238f0ad867e4bf9ff855.png?sha=92a613bf58e04e695683a81762b7fd825aa7011b)

---

### 4. ログインが簡単

小さなことかもしれませんが、  
GitHub Copilotって、**VSCodeにGithubアカウントでログインしたら即使える**んですよね

個人的に、ちょくちょくメインPCのLinuxが壊れて入れ直したりすることがあります。  
その際、Chrome、VSCode、Git、Podmanさえ入れればもとの状況に戻せるのが激アツです。

VSCodeにログインすれば、設定・拡張機能・GitHub Copilotが全て復元されて即使える状態になる。  
個人的には超嬉しいポイントです。

環境構築の手間が減らせるのは、PCで遊ぶハードルを下げてくれます。  
使いみちがあったりなかったりする変な知識を入れるチャンスが増えて楽しいですよ。

---

## 結論：DevContainer使え

GitHub Copilot の最大の強みは VSCode との統合であり、  
個人的にはその中でも特に DevContainer との連携が素晴らしいと思っています。

そもそも、DevContainer 使わない意味がわからない。  
開発環境の構築や共有にかかる時間も、環境の違いによるトラブルも減らせるし、何より気持ちがいいのに！

DevContainer 使え！そしたら GitHub Copilot を使う意味が分かるから！
