---
id: "2026-03-28-claude-codeで海外saas-hightouch-のuiを日本語化するブラウザ拡張機能を作っ-01"
title: "Claude Codeで海外SaaS (Hightouch) のUIを日本語化するブラウザ拡張機能を作ってみた"
url: "https://qiita.com/justin_hieher/items/dcac59891591219e168c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

## はじめに

私は業務で[Hightouch](https://growth-marketing.jp/hightouch/)という海外SaaSの提供に携わっているのですが、UIが英語中心なこともあり、幅広いユーザーの利用を考えると少し敷居が高いよな…と感じることが多くありました。

製品のUI自体はかなり使いやすいので「言語が日本語に対応してくれたらな」と思いHightouch社にも何度か伝えていましたが、日本語対応には少し時間がかかりそうでした。

また「翻訳のアプリケーションを自分で作るか」と思いもしましたが、私はエンジニアではないのでハードルは高く、これまでは諦めていました。

そんな中、昨今話題の[Claude Code](https://claude.ai/claude-code)を興味本位で個人で使っていた時に、「これでブラウザの拡張機能作れるんじゃないか？」と思い作ってみたところ、思いの他ちゃんとしたものができたので紹介します。

---

## Hightouchとは

![image.png](https://qiita-image-store.s3.ap-no
