---
id: "2026-05-31-supabase-stripe-ai-で-b2b-saas-を出す前にやる-公開前-checklis-01"
title: "Supabase + Stripe + AI で B2B SaaS を出す前にやる 公開前 checklist 12 項目"
url: "https://zenn.dev/toriai/articles/6278b18ac88308"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "zenn"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

TORIAI は、鋼材の切断計画を Web で作る B2B 向け SaaS です。1 人の人間が方針を決め、Claude と Codex が実装・レビューを分担する体制で進めています。

公開前に一番効いたのは、派手な機能追加ではなく「出す前に必ず見る checklist」を固定することでした。AI は速く書けますが、RLS、課金境界、キャッシュ、守秘、migration の事故は速さでは相殺できません。経験ベースで 12 項目をまとめます。

## 1. RLS は「有効」だけでなく境界テストまで見る

RLS enabled は開始地点です。anon / member / owner の 3 境界をテストデータで分け、別 branch や別 workspace の ID 直指定で 0 行になることを確認します。RPC は `search_path` 固定、column は table alias で qualify します。

## 2. 課金 gate は UI と DB enforcement を分ける

Stripe を入れる前に、誰がどの単位で Pro なのかを決めます。client の `isPro` は表示用、権限の正本は webhook が更新する entitlement table に寄せます。

## 3. smoke test は「最低限壊れたと分かる」範囲に絞る

最小構成は `npm test`、主要 JS の `node --check`、Playwright smoke、generated artifact parity です。bundle、schema、sitemap は CI で再生成差分を見ます。

## 4. Service Worker cache は release 手順に入れる

PWA は便利ですが、古い JS/CSS が残ると「直したのに変わらない」が起きます。`CACHE_NAME` と script query を release 手順に入れ、内部 tool や noindex page を誤って長期 cache しないようにします。

## 5. cleanup protocol を先に書く

本番に近い環境で smoke や stress を回すなら、投入した test row を追跡します。作成 ID の一覧、cleanup 実行、0 件確認までを 1 セットにし、destructive cleanup は人間の明示承認なしに走らせません。

## 6. migration は deploy と cleanup を分ける

新規 table / policy / RPC と、過去オブジェクトを消す cleanup migration は分けます。production では `IF EXISTS` と rollback 手順を置き、`supabase db push` は人間承認 gate を通します。

## 7. 守秘ルールは公開記事の前に固定する

技術記事でも、個人 email、会社名、顧客名、実案件、実 Supabase URL、secret key は出しません。URL は `https://{your-project}.supabase.co` のような placeholder に置き換え、handle は `haganedev` に統一します。

## 8. SEO は事実と product 状態を一致させる

記事タイトル、canonical、meta description、CTA は公開中の product と一致させます。未実装の paid 機能を「使えます」と書かず、内部 PoC は `noindex,nofollow` にして sitemap に入れません。

Supabase、Stripe、analytics、画像、font、worker を使うと、`connect-src` や `script-src` が後から広がります。必要な外部 origin を表にし、Cloudflare Pages では `_headers` で no-cache と security header を管理します。

## 10. API key 露出を grep で見る

anon key は公開 client で使う前提ですが、service role key、Stripe secret、Discord webhook、LLM API key は frontend に置きません。公開前に `rg -n "service_role|sk_live|webhook|api_key|supabase.co"` をかけます。

## 11. 監視は「個人情報を流さない通知」にする

GitHub Actions failure、UptimeRobot、Discord 通知、Umami / GSC などは無料枠でも始められます。ただし通知に email、会社名、顧客名、申請内容をそのまま流さず、詳細は権限のある場所で見ます。

## 12. DR runbook は障害が起きる前に 1 ページ作る

復旧手順は、障害時に考えると遅いです。DNS rollback、直近 commit の revert、Supabase migration の戻し方、localStorage export、問い合わせ窓口、最終判断者を 1 ページにまとめます。

## まとめ

公開前 checklist は、開発速度を落とすためではなく、出した後に戻れない事故を減らすためのものです。RLS、課金 gate、smoke、SW cache、cleanup、migration、守秘、SEO、CSP、API key、監視、DR runbook。この 12 項目を release 前に見ます。

---

この記事は Claude (Anthropic) と Codex (OpenAI) が下書き、最終的な公開内容は handle `haganedev` が確認予定です。記事中の数字 / コード / 設計の裏取りは AI / 公開 repo の commit から確認できます。
