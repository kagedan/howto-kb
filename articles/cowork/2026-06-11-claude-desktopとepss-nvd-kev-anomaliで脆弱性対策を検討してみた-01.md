---
id: "2026-06-11-claude-desktopとepss-nvd-kev-anomaliで脆弱性対策を検討してみた-01"
title: "Claude DesktopとEPSS, NVD, KEV, Anomaliで脆弱性対策を検討してみた"
url: "https://qiita.com/hisashiyamaguchi/items/47607c6657028700fe57"
source: "qiita"
category: "cowork"
tags: ["MCP", "API", "cowork", "qiita"]
date_published: "2026-06-11"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

脆弱性対策は、サイバーセキュリティに携わっている方にとって最も頭の痛いテーマの1つかもしれません。AIネイティブな昨今、ひっきりなしに発見されるソフトウェアの脆弱性の全てが同じ意味を持っているわけではなく、意味合いや重要度は組織にとって異なるはずです。この記事では、一般公開されている脆弱性データベースと有償の脅威インテリジェンスを利用活用した脆弱性対策の案をご案内しています。

# 前提条件
Claude DesktopとNodeをラップトップにインストール済、[Anomali](https://www.anomali.com/)のライセンスを契約済であることを前提としています。ラップトップはMacBookを想定しています。

# 実験
## MCP Bundlesの設定
EPSS, NVD, KEVをClaudeをMCP連携するため、[MCP Bundles](https://www.mcpbundles.com/)にサインアップします。**詳細な手順は割愛します。**
![1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/86fb87f5-5a98-44ba-b5a0-04af771ce0cf.png)
<br>
<br>

検索バーにepss, nvd, kevと入力して対象のMCPサーバを検索、*Connect*をクリックします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/d712acc4-d2f8-4e0d-9e10-625c6639e2f6.png)
<br>
<br>

右上の*Start*をクリックします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/332e6a97-fa26-4e8f-b5b5-03bb8445a910.png)
<br>
<br>

接続が成功するとチャット画面が開きます。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/defae4c7-e7cd-43d6-9bfc-fb426965825e.png)
<br>
<br>

MCPサーバに戻って*Manage*をクリック、*Claude Desktop(.mcpb)*をクリックしてパッケージをダウンロードします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/eb2ec537-b2b1-4968-8c6f-890332027fde.png)
<br>
<br>

ダウンロードしたパッケージをダブルクリックすると、Clade DesktopがのConnectorインストール画面に遷移します。*Install*をクリックします。成功すると、MCP BundlesのAPIキーを入力するよう促されます。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/38a9cdd2-164f-4abf-af48-f81c67a5cf7a.png)
<br>
<br>

MCP Bundlesに戻って右上のプロファイルから*Settings*を選択します。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/78f539ff-9da8-4232-95d2-072ddfcef08d.png)
<br>
<br>

左のぺーンで*API Keys*を選択してAPIキーを作成、クリップボードにコピーします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/2c8be82d-7d42-4cd0-9a03-027f7197d97a.png)
<br>
<br>

Claudeに戻ってAPIキーをペースト、*SAVE*をクリックします。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/fde25e70-81f2-4fc1-a68b-36886dbeae35.png)
<br>
<br>

成功するとMCPサーバと利用可能なToolsを確認することができます。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/4d5496fe-c2e3-4659-bd38-357f87ae3b0b.png)
<br>
<br>

## Claudeとやってみる
以下、Claudeに投げたプロンプトです。Chatを利用しました。Coworkに投げると、MCPサーバではなくインターネット上のEPSS, NVD, KEVをリサーチし始めます。やるなって言ってるのに。意味不明。

```text
xxxxxxx, a xxxx xxxx group, is one of my top customers, and I've been working with their proactive threat hunting team, and I'm trying to create a vivid vulnerability prioritization strategy and tactics for them. I want you to create a vivid vulnerability prioritisation briefing for them with the following chapter structure. Please put the nice chapter names that give clear understandings for them.

Executive summary.
Top20 vulnerabilities that matters Coupang.
Adversaries, campaigns and TTPs mapping with the vulnerabilities.
Detailed patching steps with clear timeline and owner.
Appendeix.

The report should be 6 pages of PDF.  All information should be gathered through my connects, EPSS, NVD, CISA-KEV, ThreatStream. Do not gather through websearch.
```
<br>

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/8fb7a594-5df0-46d6-9e03-f67d0da01f8f.png)
<br>

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/71683c73-0608-4e88-98e6-f1e5c0e3c5e6.png)
<br>

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/84e6d776-b361-4205-9a66-605bf85d09fe.png)
<br>

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/298405/6173f103-bd01-4dbf-a5f9-48874133a1c5.png)
<br>


# おわりに
最後までお付き合いいただきありがとうございます。お気づき等コメントいただけると嬉しいです。最近では、EPSSより更に進化した、Lively Exploited Vulnerabilitiesという概念も登場しているようです。いずれの脆弱性データソースを利用するにしても、大切なことは、自組織がどんな業界でどんなことをやっていて、どんな資産を持っていて、それらの資産がどんなソフトウェアテクノロジーで管理されたり守られているか、を把握することが出発点になるかと思います。
