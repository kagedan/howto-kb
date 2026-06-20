---
id: "2026-06-19-claude-code-artifactsを試したらteamenterprise限定で自分には使えな-01"
title: "Claude Code Artifactsを試したら、Team/Enterprise限定で自分には使えなかった話"
url: "https://zenn.dev/lnest_knowledge/articles/claude-code-artifacts-verification"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年6月18日、Claude CodeにArtifactsが追加されました。

<https://claude.com/blog/artifacts-in-claude-code>

公式ブログでは、Claude Codeのセッション中の作業を、PRウォークスルー、システム説明、ダッシュボード、リリースチェックリストのようなライブで共有できるページにできる、と説明されています。

これを見て、自分がClaude Codeのルーチン(定期実行)で毎朝やっている作業に合いそうだと思いました。AI界隈や気になるアカウントのXと技術トレンドをざっと集めて、その日の発信テーマ候補、SNS下書き、試したい検証ネタを長めのMarkdownにまとめています。Slackに全文を投げるより、フィルタできる1枚のページにしたほうが読みやすいはずです。

ただ、実際に触ると「ClaudeのArtifacts」と「Claude CodeのArtifacts」はかなり違いました。そして肝心のArtifactsは、自分の環境では試せませんでした。

理由は自分のプランです。元々はTeamにいたんですが、Claudeをはちゃめちゃに使うのでMax(20x)に移りました。個人の上限を上げる代わりに、Team/Enterprise向けのArtifactsは自分のアカウントからは触れません。ついでに、Teamで共有しているArtifactsやSkillも自分だけ見られなくなりました。使用量と引き換えに共有物から外れた格好で、これがまあまあ悲しい。

この記事では、公式ソースで確認できたこと、手元で試せたこと、自分の環境ではできなかったことを分けて書きます。Artifactsと組み合わせたかった、毎朝のルーチンの話もあわせて。

## 先に結果

今回分かったことはこのあたりです。

* Claude Code Artifactsは、Claude Codeの作業セッションから作る組織内共有向けのライブページ
* Claude.aiの従来Artifactsのような「公開URLを誰でも見られる」機能として扱うとズレる
* 公式docs上はbetaで、Team/Enterprise、`/login`、Anthropic APIなどの条件がある
* 自分はMax(個人プラン)でTeam/Enterprise条件を満たさず、非対話CLIでも対話セッションでもpublishツールは出なかった
* ただし、毎朝のルーチン出力をダッシュボード形の共有ページにまとめる発想は相性がよかった

記事用に、公開して問題ない範囲のデータだけでダッシュボードの再現画面を作りました。実Artifact URLや社内情報は載せていません。

![毎朝のルーチン出力をArtifact化する想定のダッシュボード](https://static.zenn.studio/user-upload/deployed-images/2c7fcd7ae1340054325148bb.png?sha=dc53013bd2272eeb5849a2c0dac1101d974f78b8)  
*公開用に作った再現画面。実Artifactの共有URLではありません*

## Claude Code Artifactsとは

Claude Code Docsでは、Artifactsを「Claude Codeの作業を、組織内で共有できるprivate URL上のライブでインタラクティブなページにするもの」と説明しています。現時点ではbetaです。

<https://code.claude.com/docs/en/artifacts>

ポイントは、セッションの出力を見やすいページにするところです。ターミナルの長いログやMarkdownをそのまま渡す代わりに、表、チェックリスト、簡単な操作UI、ダッシュボードとして渡せる。

ただし、アプリではありません。docs上でも、外部リクエスト不可、バックエンドなし、単一ページ、HTML/Markdown、16MiB以下という制約が書かれています。つまり「見せるための1枚ページ」として考えるほうが近いです。

記事中の主張がズレないよう、ソースごとに言えることと言えないことを先に分けました。

![ソースごとに言えることと言えないことを整理した表](https://static.zenn.studio/user-upload/deployed-images/aa20a7b2346882631ff83e5b.png?sha=95a317293f6829c9963d556214467b8a9ea19a62)

## 従来のClaude Artifactsとの違い

ここが一番混同しやすいところです。

Claude.aiの従来Artifactsは、チャットの横に出る専用ウィンドウの成果物です。Markdown、コード、HTML、SVG、React componentなどを表示・編集できます。2024年の一般提供開始時の記事でも、Claude.ai上の会話で作った成果物を専用スペースで見て反復する機能として説明されています。

<https://claude.com/blog/artifacts>

<https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them>

一方で、Claude Code ArtifactsはClaude Codeのセッション出力をページにして共有するものです。特に共有範囲が違います。

Claude Help Centerでは、従来ArtifactsのFree/Pro/Max向けpublishは公開リンクをコピーして共有できると説明されています。一方、Team/Enterpriseの共有は組織内共有です。

<https://support.claude.com/en/articles/9547008-publish-and-share-artifacts>

Claude Code Docsのほうでは、Claude Code Artifactsは組織内のauthenticated membersだけが見られ、外部公開はできないと書かれています。なので、Zenn記事にArtifactの公開URLを貼って「見てください」とはできません。

ここは最初に知っておいたほうがいいです。自分も最初は「Codex Sitesみたいに外へ見せられるのかな」と思っていましたが、少なくともdocs上の位置づけは違いました。

## 検証環境

手元のClaude Codeは`2.1.173`でした。Linearの検証Issueに書かれていた想定バージョンとも一致しています。

![Claude Codeのバージョンと入力ファイルの確認](https://static.zenn.studio/user-upload/deployed-images/6e7a49bda101c56c782387f7.png?sha=b2a39a68d5bcd890ab6037b6a193cf9deacb3e97)

今回の入力にしたのは、その毎朝ルーチンの2026年6月19日の出力です。

```
data/2026-06-19/      # その日に集めた生データ
drafts/2026-06-19.md  # その日のSNS下書き
```

中身は、トレンド取得、Xの取得結果、ウォッチ対象の要約、SNS下書きです。Xのguest取得は鮮度不明のものが混ざるので、記事の主根拠にはしていません。公式ブログとdocsを主根拠にして、ルーチンの出力は「こういうページにしたい」という素材として扱いました。

## 作りたかった画面

毎朝のMarkdown出力をそのまま読むと、必要な情報にたどり着くまで少し時間がかかります。Artifactにするなら、次の構成が合っています。

* 今日の入力と鮮度メモ
* 公式ソースで言えること
* 下書き候補の一覧
* publishや共有まわりの確認状況
* 未確認のまま残す項目

下書き候補は、Claude、Codex、Slackのようにテーマで切り替えられると読みやすいです。

![下書き候補をテーマで切り替える想定](https://static.zenn.studio/user-upload/deployed-images/39e954a2c7b5de99b56a13fe.png?sha=d0759d130c1a9464d68e66387f4cb7a842cf7e07)

スマホで見たときも、メタ情報と下書き一覧が先に見える形にしました。実運用では、移動中に今日の候補だけ見ることが多いので、モバイルで破綻しないことはけっこう大事です。

![モバイル幅での見え方](https://static.zenn.studio/user-upload/deployed-images/30b698775370bf3e28b3b073.png?sha=bfb75ff057d43b78143e66ef0deebe35ce7f750d)

このくらいなら、Claude Code Artifactsの単一HTML制約にも収まります。外部APIをview時に呼ばず、セッション中に集めた結果をページに焼き込むだけだからです。

## publishテスト

次に、最小のArtifact公開テストをしました。

公開して困らない1行だけを入れたページを作るように、非対話CLIで`claude -p`を実行しています。予算上限も付けました。

結果は失敗です。このセッションではArtifact公開ツールが見えず、ページもファイルも作られませんでした。

![非対話CLIでのArtifact publishテスト結果](https://static.zenn.studio/user-upload/deployed-images/4567bd3d62153e1ae9b77175.png?sha=400d060203d82432983e28181bce374d73094262)

ここで言えるのは「自分が今回使った非対話CLI実行面ではpublishできなかった」までです。公式docsにある利用条件そのものを否定する結果ではありません。

Claude Code Docs上の条件は、Team/Enterprise、`/login`、Anthropic API、CLIまたは対応desktop app、組織ポリシーなどです。実セッションでArtifact toolが有効かどうかは別途見る必要があります。

なので、この記事では「Artifactとしてpublishできた」とは書きません。ここを盛ると、あとで自分が困ります。

## 共有と制約

公式docsによると、新しいArtifactは最初は自分だけが見られます。Share controlから特定の人か組織内の人に共有します。閲覧者は同じ組織のメンバーとしてclaude.aiにログインする必要があります。外部公開はできません。

![共有範囲とバージョン更新の再現図](https://static.zenn.studio/user-upload/deployed-images/776abcd319cdab1ac92c3d4d.png?sha=654f3e141dcf4f80e39aaea6793492ebbcb1501f)

自分の用途では、Claude Code Artifactsは外部公開用ではなく社内共有用として見るのが合っています。毎朝のルーチン出力にはウォッチ対象の投稿や社内Slackの話題が混ざるので、外へ出せない制約はむしろ都合がいい。

Zenn読者に動くデモを見せる用途では使えません。その場合はHTMLを別でホストするか、スクショで見せるほうが現実的です。

## 公開できる内容で1枚作ってみる

publishはできなかったので、中身の側だけ確かめました。今回はルーチンの実データではなく、公開して問題ない内容で単一HTMLのサンプルを作っています。この記事の要点(beta、Team/Enterprise、組織内共有、単一HTMLの制約、向き不向き)を1枚にまとめたものです。

![公開できる内容だけで作った単一HTMLサンプル](https://static.zenn.studio/user-upload/deployed-images/19afc489253fce5710b3e3c7.png?sha=a72164bd04a66aa925fa9409fa53955520460a61)  
*公開してOKな内容だけで作ったサンプル。Artifactにする中身の形を示すもので、実publishはしていません*

外部リクエストなし、バックエンドなし、単一HTMLという制約には収まります。中身を1枚ページにまとめる部分は、公開できる題材でも問題なく作れました。

ただ、題材を公開OKにしても、Zennには結局この画像を貼っています。Claude Code Artifactは組織内限定なので、題材が公開できることと、公開URLとして貼れることは別でした。最初は「中身さえ公開OKならArtifactのURLを貼れるのでは」と思っていたんですが、そこは関係なかったです。

## 使いどころ

今回の題材だと、Claude Code Artifactsは「Slackに長文を投げる代わり」に向いていそうです。

毎朝の出力は、全部が同じ重さではありません。今日すぐ使いたい下書き、後で読むソース、鮮度が怪しい取得結果、Linear化した検証候補が混ざっています。これを1本のMarkdownで渡すと、読む側が毎回仕分けることになります。

Artifactにすると、仕分けた状態で渡せます。

![公開前チェックの再現チャート](https://static.zenn.studio/user-upload/deployed-images/ea382a1e5d317df8e2e3cb6f.png?sha=21d0d9c610041534fe2b6845fa1279b0594ce31d)

たとえば、次のような見せ方ができます。

* source確認済みの候補だけを先に表示する
* 鮮度不明のX guest取得を警告として出す
* 下書き候補をClaude / Codex / Slackで切り替える
* Linear issueへのリンクをまとめる
* publish後も同じURLで更新する

Slack投稿やDMは流れていきます。Artifactは「今日の作業ページ」として残る。ここはかなり違います。

## 注意点

実運用で使うなら、次の点は気をつけます。

### 社内情報の扱い

Artifactは組織内共有とはいえ、共有した相手はページを見られます。社内Slack本文、DM、非公開URL、トークン、Cookie、実名の扱いは分けたほうがいいです。

今回のスクショも、実データをそのまま出さず、公開用に再構成しています。

### 外部公開デモ

Claude Code Artifactsは、少なくともdocs上は外部公開できません。Zennで動くURLを貼る用途なら、別のホスティング手段を考えたほうが早いです。

### 「できる」と「今回できた」

公式docsでできると書かれていることと、自分の環境でできたことは分けて書くべきです。今回で言うと、単一HTMLのダッシュボード案は作れましたが、Artifactとしてpublishするところは未達です。

## まとめ

今回の用途では、Claude Code Artifactsを長い作業ログを社内向けの1枚ページにまとめる道具として見ています。

毎朝のルーチンのように、収集、判断、下書き、検証Issueが混ざる出力とは相性がいい。Slackに全部貼るより、ダッシュボードとして渡したほうが読みやすいです。

ただ、自分はそのArtifacts自体を試せていません。Team/Enterpriseが条件で、自分はMaxに移ったからです。形(単一HTMLのダッシュボード)は公開できる題材でも作れたので、あとはプランの問題、というのが正直なところです。

試すならTeam/Enterpriseのアカウントが要ります。Maxに移った自分は、当面はHTMLを手元で作って画像で貼るか、別のところにホストするのが現実的でした。Teamで共有されているArtifactsやSkillを横目に、毎朝のルーチンの出力だけでもきれいに渡したい、という気持ちは残っています。

## 参考リンク
