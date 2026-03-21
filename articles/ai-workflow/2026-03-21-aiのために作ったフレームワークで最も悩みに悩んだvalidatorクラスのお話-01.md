---
id: "2026-03-21-aiのために作ったフレームワークで最も悩みに悩んだvalidatorクラスのお話-01"
title: "AIのために作ったフレームワークで、最も悩みに悩んだValidatorクラスのお話"
url: "https://qiita.com/fallout/items/eff6923a9f303615c51c"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

[AIでAIによるAIのためのフレームワークを作り、AIで爆速開発するというお話](https://qiita.com/fallout/items/3d1d96f4e40d3766aaad) にも書きましたが、最近、**AI様のためのフレームワーク**（Claude先生が `Lattice` という[名前をつけてくれた](https://qiita.com/fallout/items/d4867c023df3537c8fd8)ので以下 `Lattice`）を作る事にハマっていました。

もう既に何度か実践投入も済ませており、**AIが間違える事なく爆速コーディングするための専用道路**はほぼ完成した…と満足しています。

今回は、そんな `Lattice` の設計において最も苦労した `Validator` クラスの話をしたいと思います。

--------------------

## 違う 違う そうじゃ そうじゃなーい

- ぼく：`Validator` クラス作り直してみたよ。セットで `SKILL.md` も更新したから使ってみて！

- Claude先生：分かりました。
