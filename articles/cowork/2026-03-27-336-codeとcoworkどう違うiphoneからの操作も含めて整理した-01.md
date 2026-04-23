---
id: "2026-03-27-336-codeとcoworkどう違うiphoneからの操作も含めて整理した-01"
title: "#336 CodeとCowork、どう違う？iPhoneからの操作も含めて整理した"
url: "https://note.com/chi3jp/n/n3db5e5a19754"
source: "note"
category: "cowork"
tags: ["cowork", "note"]
date_published: "2026-03-27"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

coworkとcodeの使い分けが全然わからなかったので整理しました。

こんにちは、ちーみつです。

ClaudeのデスクトップアプリにはChat、Code、Coworkという  
3つのタブがあります。  
さらにiPhoneアプリにはDispatchという項目まであって、  
違いがわからなかったので4つの機能の違いと使い分けを調べました。

## そもそもCodeとCoworkは対象が違う

Claude Codeはコーディング向けのAIエージェントです。  
ターミナル、デスクトップアプリのCodeタブ、VS Codeの拡張機能から使えます。

Coworkはコーディング以外の知識業務向け。  
ファイル整理・レポート作成・定期的な文書更新など、  
エンジニアではない人が使うことを想定した設計です。  
デスクトップアプリのCoworkタブからのみ操作できます。

アーキテクチャは同じで、違いは  
コーディング向けかどうかとターミナルが使えるかどうか。  
それだけでした。

## iPhoneから操作できるが、仕組みが違う

ここが一番混乱した部分です。

CodeをiPhoneから操作する方法は2通りあります。

1つはClaudeアプリから直接つなぐ方法。  
もう1つはDiscordやTelegramを経由するChannels。

CoworkをiPhoneから操作するにはDispatchを使います。  
ClaudeアプリのDispatch画面から操作する仕組みです。

codeはMac上でセッションが起動していれば、Channelsという機能を設定してあればローカルファイルの操作ができます。  
iPhoneアプリのGitHub連携はリポジトリ上のファイルのみ操作でき、ローカルファイルは触れません。

## Codeが使える人にCoworkの出番はほぼない

Claude Codeを使っている環境であれば、  
Coworkを使う場面はほぼないと思います。

コーディングも、ファイル操作も、定期タスクも、  
Codeでカバーできます。  
ターミナルを触れる人にとって、  
Coworkはできることの範囲が狭くなります。

DispatchはCoworkのリモート操作機能なので、  
Coworkを使わないなら同様に不要です。

iPhoneからCodeを動かしたいなら、  
ClaudeアプリかChannels（Discord等）を使えばいい。

## まとめ

タブが3つ並んでいても、実際は対象ユーザーで分かれているだけでした。

Coworkはターミナルに抵抗がある人のための入口。  
Dispatchはそのリモート操作機能。

外出先でターミナルを起動していなかった時、iPhoneから何もできなかった経験があります。  
アプリのGitHub連携とChannelsの両方を準備しておくと、どちらかが使えない状況でもカバーできたなぁと。  
こういう状況にならないと使い所はわからないものですね…笑

皆さんはCode以外のタブ、使っていますか？

最後まで読んでいただきありがとうございます。

**Claude Codeの使い方が気になった方はこちらもどうぞ**👇

## 🎁 登録者限定：有料記事の中身を無料でお届け

AIに指示するたびにコストが跳ね上がっていた私が、  
ある変更をしてから消費量が半分以下になりました。

たとえば、私のように投稿のアーカイブをAIに読み込ませるなど、多くのファイルなどのデータを読み込ませている方が対象です。

noteでは有料の内容ですが、  
メルマガ登録者にだけ有料部分の一部無料で公開しています。

▼ 今すぐ無料で受け取る  
<https://chiii3.systeme.io/7af4ded7>

X : <https://x.com/chi3_jp>  
Instagram : <https://www.instagram.com/chi3jp_aiart/>  
私のまとめサイト : <https://chi3jp.com/>
