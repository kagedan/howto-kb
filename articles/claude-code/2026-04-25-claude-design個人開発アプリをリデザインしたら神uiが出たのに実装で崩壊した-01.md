---
id: "2026-04-25-claude-design個人開発アプリをリデザインしたら神uiが出たのに実装で崩壊した-01"
title: "【Claude Design】個人開発アプリをリデザインしたら神UIが出たのに実装で崩壊した"
url: "https://qiita.com/skwt20/items/46bf18dbc8e92e363c91"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

# はじめに
いま超話題の[Claude Design](https://claude.ai/design)を雑に試してみました。

# Claude Designを試してみた結論

- UI案の生成はかなり優秀（デザイナーの叩き台として使える）
- ただし「実装への落とし込み」はかなり不安定
- 利用制限が厳しく、連続使用が難しい
- 現時点では「デザイン生成ツール」として割り切るのが良さそう

とりあえず実際に触ってみた結果をまとめていきます。

## できたもの
今回リデザイン対象としたアプリ：
- 英語のセッションを聞くことに特化したリアルタイム翻訳アプリ (自作)

### 現状 (Claude Codeデザイン)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/92bd9077-4447-4011-b8ab-a14f5231c3f8.png)

### Claude Design 提案
 ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/4f482044-d5ef-4e5b-bbdf-ed2568e049d4.png)

### 実際にできたもの
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/718113d6-8e8a-4edd-83f5-e9db9a0d26fe.png)

# 実際にやってみた
## デザイン生成

Claude Designの画面から新しいプロトタイプを作成します。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/c087e7fe-3a65-429e-933d-5e698d75a46e.png)


「コードベースを添付する」を選択します。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/5166070d-2baf-45b0-bd39-624b4759816b.png)

「翻訳アプリのUIデザインを行けてる感じにしてほしい。」（誤字）とプロンプトに入力して動かしてみました。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/1478dc7f-4266-4f59-b41f-ecbb9ba08658.png)

「デザイン案を何通り提示するか」などいろいろ質問されるため回答していきました。

今回は４～５案を提案してもらった中から選択しました。

以下がClaude Designで作成したデザインになります。
 ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/4f482044-d5ef-4e5b-bbdf-ed2568e049d4.png)


おお！カッコいい！！イケてますね！
これはキャプチャですが、実際は動く様子を見せてくれます。
デザイナーの仕事はわかりませんが、これを基の顧客とデザインを詰めていくことができそうです。

ちなみに私が選択しなかった残り４つのデザインは以下になります。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/25ca8880-4859-4d49-96a9-eabfce272937.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/43768039-9f4d-49d5-b57e-fefafeaeb455.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/5d19aa4f-7510-4165-a19d-24fa777ed840.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/129f36bf-89f2-425d-bacf-17656b417d7f.png)

デザインが確定したので、このデザインで実装してもらおうと思います。

・・・と、実装を開始したところで、残念ながら利用料上限を迎えてしまいました。（早）
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/746dc1a3-6c20-4622-b33b-e3534ed3cc8a.png)

モデルを確認したところ、Opus4.7がデフォルトで選択されていました。あー、なるほどねぇ…
とりあえずSonnetに変更しました。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/a9a94dea-aa61-4224-b562-d23dabd6a0ae.png)

24時間後にリトライしてと書かれてましたが、24時間後ではダメでした。
何度かリトライしていたら1週間後の火曜日にリトライして、とポップアップには出ましたが、何故か土曜日には使えるようになってました。

::: note
↓公式では7日でリセットされると公言されています。
[Claude Designのサブスクリプションの利用方法と料金](https://support.claude.com/en/articles/14667344-claude-design-subscription-usage-and-pricing?utm_source=chatgpt.com)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/42fea853-396b-40fd-82a3-f962e99f7042.png)

以下の画面で現在の使用量が確認できます。
[使用量](https://claude.ai/settings/usage)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/aefe2c04-25b2-46b0-86cd-f17a68166889.png)
:::

## 実装

時が経ち、使用制限が解除されたため実装を開始してもらいました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/d26f9da7-ca77-4879-9482-d4fc4022d695.png)

ローカルフォルダへのアクセスを許可しました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/11825ad9-ec0a-48e2-b735-4ae4df45fd33.png)

実装が完了したかのような表示が出て処理が止まりました。
ワクワクしながら画面を更新しましたが、デザインが変わらないため聞いてみました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/edaa95df-0599-46ab-b3c6-3d8891ef3201.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/63137d1e-a408-4624-ac65-2d3992bfb68c.png)

さっきローカルフォルダへのアクセス許可したのは何だったのか分かりませんが、書き込めないようです。
提示されたファイルをダウンロードしてローカルのファイルに上書きしました。


![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/b2ec1741-9ae2-4b53-984a-d0eb0c184941.png)

おお！！なんかデザイン変わってる！！
　
　
  
　
  
・・・あれ？デザインこんなんだっけ。。

↓最初に提示されたデザイン
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/45b1ad34-4933-4599-8542-fb3fa9c533ea.png)
全然違う。。
ほぼ色しか変わってないじゃん。。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/e1c69008-7a66-4356-8012-09ba710aef39.png)
現在の画面キャプチャをみせて、デザインがあまり変わっていないことを指摘します。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/d97e1e01-a261-42f9-8c1d-eb9857b2bb3e.png)

再びファイルの差し替えを指示されたのでやってみましたが、あまり変わりませんでした。

この後、何度かリトライした結果が↓こんな感じ。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4239919/718113d6-8e8a-4edd-83f5-e9db9a0d26fe.png)

うーん、最初のデザインを上辺だけパクッて作ったようなデザイン…。
単純に見づらくなったのとバグが出てきました。

Claude Designの利用上限に達したため、今回の検証はここで終わります。

# 使ってみた感想
リデザインは大量のコードを読ませるため、やはり難しそうです。
最初にClaude Designでデザインを決めてからClaude Codeでコーディングすればもっとうまくいくと思います。

私もまだ全然試せていませんが、いったん現状で情報共有しておきます。
まだClaude Designの情報があまり出回っていない理由は、
すぐに利用上限を迎えてしまい試しきれていない人が多いためと予想します。
自分もまさにその状態でした。

私の検証が誰かの役に立てば幸いです。
