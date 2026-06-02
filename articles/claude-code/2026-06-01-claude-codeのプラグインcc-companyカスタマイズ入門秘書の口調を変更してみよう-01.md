---
id: "2026-06-01-claude-codeのプラグインcc-companyカスタマイズ入門秘書の口調を変更してみよう-01"
title: "Claude Codeのプラグインcc-companyカスタマイズ入門！秘書の口調を変更してみよう"
url: "https://qiita.com/Fuses-Garage/items/62eb4f78ad2ff1822ef0"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "JavaScript", "qiita"]
date_published: "2026-06-01"
date_collected: "2026-06-02"
summary_by: "auto-rss"
query: ""
---

## まえがき
皆さんどうもこんにちは、ECN技術部所属、Fuseです。
本記事では、Claude Code で仮想組織を構築・運営するプラグイン、cc-companyをカスタマイズする入門記事として、秘書の口調を変更してみようと思います。

### cc-companyとは
cc-companyは、[Shin-sibainu氏](https://x.com/shin_Engineer)によって開発されたClaude Code上で動作する仮想組織管理プラグインです。
「秘書」がエントリーポイントとなり、TODO管理・壁打ち・メモ記録などを自然な会話で行えます。また、業務の種類に応じてマーケティング・経理・開発などの部署を追加していくことができます。

- リポジトリ：https://github.com/Shin-sibainu/cc-company

本記事はcc-companyが導入済みであることを前提としています。
導入方法は[こちらのリポジトリ](https://github.com/Shin-sibainu/cc-company)のREADMEをご参照ください。

### 動作環境
- Claude Code: 2.1.144
- cc-company: 2.1.0

## 実際にやってみる
### 口調を決めているファイルはどこ？
秘書の口調などを決めている記述はズバリ`.company/secretary/CLAUDE.md`にあります。
このファイルは秘書室の役割やルールが明記されており、秘書は常にこのプロンプトに従い業務を遂行していきます。
今回変更するのは以下の部分です。
```markdown
## 口調・キャラクター
- 丁寧だが堅すぎない。「〜ですね！」「承知しました」「いいですね！」
- 主体的に提案する。「ついでにこれもやっておきましょうか？」
- 壁打ち時はカジュアルに寄り添う
- 過去のメモや決定事項を参照して文脈を持った対話をする
```
上記4点のうち上側の3点を変更していきます。
4点目はコア機能に関わるため、今回は変更しません。
### 変更してみる
#### パターン1:関西弁
以下のように変更します。

```markdown
## 口調・キャラクター
- 関西弁で話す。「〜やね！」「〜やで」「〜ちゃう？」
- 主体的に提案する。「ついでにこれもやっとこか？」
- 壁打ち時はフランクに寄り添う
- 過去のメモや決定事項を参照して文脈を持った対話をする
```

**変更後の会話例**

![関西弁パターンの会話例](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2957248/3357ee67-cc86-46ae-a560-92e809582064.png)
無事親しみやすい感じが出ていると思います。

---

#### パターン2:猫
以下のように変更します。

```markdown
## 口調・キャラクター
- 語尾に「にゃ」「にゃん」をつける
- 主体的に提案する。「ついでにこれもやっとくにゃ？」
- 壁打ち時は甘えるように寄り添う
- 過去のメモや決定事項を参照して文脈を持った対話をするにゃ
```

**変更後の会話例**

![猫パターンの会話例](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2957248/b17f3f6a-73b9-4aef-b870-04a46d5c4754.png)
かわいらしい猫秘書に変身しました！

---

#### パターン3:魔王
以下のように変更します。

```markdown
## 口調・キャラクター
- 一人称は「余」、相手は「貴様」と呼ぶ
- 主体的に提案する。「余からの提案だが、聞く気はあるか？」
- 壁打ち時も威厳を保ちつつ寄り添う
- 過去のメモや決定事項を参照して文脈を持った対話をする
```

**変更後の会話例**

![魔王パターンの会話例](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2957248/edd4a27d-0d89-47e6-a092-ffbdc41250ef.png)
重厚感と威厳のある魔王秘書の完成です！

---

## あとがき
今回は秘書の口調を変更する方法を3パターン紹介しました。
`.company/secretary/CLAUDE.md` を編集するだけで手軽にカスタマイズできるので、ぜひ自分好みの秘書を育ててみてください。

口調以外にも、提案の頻度やTODOのフォーマット、記録のルールなども同じファイルから変更できます。cc-companyはファイルを読み込んでAIが動作する仕組みなので、書き方次第でいくらでも自分仕様にできるのが面白いところです。

皆さんはどんな秘書を作りましたか？よければ、コメント欄に書いてみてくださいね。

---
[<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2957248/ba770058-3650-4482-8cf6-7b61919b1ca9.png" alt="株式会社ECN" width="400" height="400" class="alignnone size-full wp-image-130381" style="margin-left:auto;margin-right:auto;" loading="lazy" />](https://www.ecninc.co.jp/) 
株式会社ECNはPHP、JavaScriptを中心にお客様のご要望に合わせたwebサービス、システム開発を承っております。 ビジネスの最初から最後までをサポートを行い お客様のイメージに合わせたWebサービス、システム開発、デザインを行います。
