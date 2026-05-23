---
id: "2026-05-22-nobel-824-openai-共同創業者karpathyの-claudemd-がgithub-ト-01"
title: "@nobel_824: OpenAI 共同創業者Karpathyの CLAUDE.md が、GitHub トレンドで1位独走中。 中身はライブラ"
url: "https://x.com/nobel_824/status/2057643942980751527"
source: "x"
category: "claude-code"
tags: ["CLAUDE-md", "LLM", "OpenAI", "x"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

OpenAI 共同創業者Karpathyの CLAUDE.md が、GitHub トレンドで1位独走中。
中身はライブラリでもアプリでもなく、たった65行のテキストファイル。Karpathy のコーディング観察を圧縮した1ファイルが、累計10万スター超え。
そこに書かれた4つの原則について解説します。 https://t.co/CGs0MQ0OSP

①Think Before Coding（書く前に考える）
LLM の一番厄介な癖は、曖昧な指示を勝手に解釈して突き進むこと。だから「前提を声に出す／複数解釈があれば全部出す／詰まったら聞く」を強制する。要は黙って暴走するな、と。

②Simplicity First（最小で解く）
LLM はすぐ抽象化したがる、1000行で書きたがる、デッドコードを残したがる。 なので「200行で書けたものが50行で書けるなら書き直せ」「シニアが見て過剰だと言う設計はやめろ」と明示する。

③Surgical Changes（外科的に変える）
頼まれてもいない周辺コードを"改善"するな、リファクタするな、コメントを消すな。変更した1行ずつが、ユーザーの依頼内容まで辿れること。
これだけで PR レビューがかなり楽になります。

④Goal-Driven Execution（成功条件で動かす）
Karpathy 曰く「LLM は目標を満たすまでループするのが超得意。命令するな、成功条件を渡せ」。
「バグを直して」より「バグを再現するテストを書いて、通せ」のほうが、AI が自走する距離が10倍違う。

この CLAUDE.md が面白いのは、新技術じゃなくて、みんな薄々感じてた"AI コーディングの不満"を65行に言語化しただけ、ってこと。

https://t.co/jGIMDfXGNw

Xでは発信できない、より有益な情報は LINEオプチャで発信しています。
固定ポストからぜひご参加ください。
