---
id: "2026-06-15-kagawatomo-httpstcomzvg23vhrd-01"
title: "@KagawaTomo: https://t.co/MZVG23VhRD"
url: "https://x.com/KagawaTomo/status/2066643303760892003"
source: "x"
category: "claude-code"
tags: ["LLM", "x"]
date_published: "2026-06-15"
date_collected: "2026-06-16"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

https://t.co/MZVG23VhRD


--- Article ---
## Macが先行し、AMDがWindows/x86へ、NVIDIAがCUDA/RTX付きWindows PCへ

## はじめに

AI時代のパソコン選びが、根本から変わり始めています。

これまで高性能PCを考えるとき、多くの人はCPU、GPU、メモリ、ストレージを別々に見ていました。

CPUはIntelかAMDか。
GPUはNVIDIAかAMDか。
メモリは32GBか64GBか128GBか。
SSDは1TBか2TBか。

しかし、ローカルLLM、AIエージェント、生成AI、フィジカルAI、ロボットシミュレーションの時代になると、従来の見方だけでは足りなくなります。

なぜなら、AI時代のPCで一番重要になるのは、単純なCPU性能でも、単純なGPU性能でもなく、

**巨大なAIモデルをメモリ上に載せられるかどうか**

だからです。

ここで一気に重要になってきたのが、

**ユニファイドメモリ**

です。

ユニファイドメモリとは、CPU用メモリとGPU用メモリを別々に分けるのではなく、CPU、GPU、NPUなどが同じ大容量メモリを共有する仕組みです。

この仕組みを、一般ユーザーにも分かりやすい形で最初に強く打ち出したのがAppleでした。

Apple SiliconのMacは、M1の時代からユニファイドメモリを前面に出していました。
そしてMac Studioでは、100GBを超える大容量ユニファイドメモリを選べるようになり、M3 Ultra世代では発売時に「512GB」のユニファイドメモリをうたう水準まで到達しました。

ただ、2026年6月時点の公式仕様では256GBが中心ですが、それでもAppleが先に見せた方向性は非常に大きい。

それは、

**AI時代のPCは、CPUメモリとGPUメモリを分けるのではなく、大容量メモリをCPU・GPU・AIエンジンで共有する方向へ進む**

という方向性です。

そして今、その流れをAMDとNVIDIAが追いかけています。

AMDは、Ryzen AI Max+ 395 / Ryzen AI Haloによって、Macが先に示したユニファイドメモリ型AI PCを、Windows / Linuxのx86世界に持ち込みました。

NVIDIAは、DGX Sparkによって、128GBのコヒーレント・ユニファイドメモリを持つ小型AIスーパーコンピュータを出しました。さらにRTX Sparkによって、Windows PCにも最大128GBユニファイドメモリとNVIDIAのAI / RTXスタックを持ち込もうとしています。

つまり、これは単なる新型PCの話ではありません。

これは、

**AI時代のパソコンの設計思想が変わる話**

です。

## この記事の結論

この話の核心は、「CPUが速いか」「GPUが速いか」だけではありません。
AI時代のPCでは、巨大モデルを載せるための**メモリ設計**が主役になります。

Macは、ユニファイドメモリPCの価値を先に見せました。
AMDは、それをWindows / Linuxのx86世界に持ち込みました。
NVIDIAは、CUDA / RTX / ロボティクスまで含めたAI開発スタックとして、Windows PCとデスクサイドAIマシンへ広げようとしています。

つまり、これからのPC選びは、単なるCPU・GPUの比較ではなく、**自分がどのAIエコシステムに乗るのか**を決める話になります。

## 目次

1. これまでのPCは「CPUメモリ」と「GPUメモリ」が分かれていた
1. ユニファイドメモリは、普通のPCのメモリと何が違うのか
1. なぜPCは最初からユニファイドメモリではなかったのか
1. 128GBユニファイドメモリの意味
1. メモリは「容量」だけではない。「帯域幅」も主役になる
1. Appleが先に見せた「ユニファイドメモリPC」の強さ
1. AMD Ryzen AI Max+ 395の意味
1. NVIDIAも128GBユニファイドメモリPCへ来た
1. RTX Sparkは、単体GPUボードを駆逐するのか
1. 机からデータセンターへ ―― DGX Station for WindowsとVera Rubin
1. Mac、AMD、NVIDIAの違い
1. Mac向けの人、AMD向けの人、NVIDIA向けの人
1. どのPCを選ぶべきか
1. これは「AI PC」の定義が変わる話
1. ローカルLLMはクラウドAIを置き換えるのか
1. フィジカルAIではNVIDIAの重要性は変わらない
1. 日本企業にとっての
