---
id: "2026-03-26-building-an-ai-powered-sql-agent-01"
title: "Building an AI-Powered SQL Agent"
url: "https://zenn.dev/flp/articles/building-an-ai-powered-sql-agent"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

Throughout my career as a backend engineer, I've built and maintained countless API endpoints and business logic, handled database operations either through an ORM layer like Prisma, or even handwritten raw SQL in some tricky cases. Yet when it comes to ad-hoc data analysis, whether for production debugging or analytics purposes, I still struggle writing SQL queries, let alone joining multiple tables and complex aggregations. So when business teams, who shouldn't need to know SQL, have to pull their own insights from the data, the friction is even worse.

Right now we already have a well-established data pipeline that captures production data from various projects and mirrors it to BigQuery, and it is accessible through Metabase. The Metabase visual query builder is more than enough for simple aggregations. However, for deep insights more often than not we have to rely on complex, hard to read and maintain SQL queries. That's where the idea came in: what if users could just describe what they want in plain text, and let an AI agent handle the SQL?

Since Metabase already has a REST API to discover the database schema and execute SQL queries, I built a web-based agentic chatbot powered by Tanstack Start and Cloudflare Workers. It works by finding the right dataset and relevant table schema and using that information to build the correct SQL query. With Cursor and just two days of work, I got it to a working state despite having little experience in frontend development.

Despite the quick turnaround, the project wasn't without its hurdles. I ran into three problems worth sharing.

## BigQuery Schema Overload

Metabase's BigQuery connector surfaces all tables for every single dataset in the GCP project, meaning that without filtering, the LLM would have to process almost 200 tables including their schemas. This was very inefficient since it consumed a lot of input tokens and most of the time it couldn't pinpoint the correct table anyway.

After splitting the tool into something like `list_datasets`, `list_tables_in_dataset`, and `get_table_schema`, it could quickly pinpoint the correct schema needed to construct the SQL query.

Implementing tool call approvals in order to protect Metabase from arbitrary SQL query execution was also not a small feat. Vercel AI SDK's `useChat` is great out of the box, but couple that with conversation history for later revisits and execution approval, and it quickly spiraled out of control ranging from duplicate chat bubbles to endless tool call loops. Patience was the key here: reading through the `useChat` documentation and proper use of callbacks and hooks solved a lot of the issues without going down the custom `useChat` implementation rabbit hole.

## The Invisible Firewall

Finally, after everything was working correctly in my local environment, I deployed the app to Cloudflare Workers and API calls to Metabase started failing, telling me that the response was not JSON encoded. The classic "works locally, breaks in prod" situation. I tried to get the raw response of the failed tool call output and to my surprise, it was Cloudflare Access all along! Locally it was no problem because Cloudflare WARP was installed and thus requests to Metabase were not restricted. All it needed was to set up a service token for the app and it was good to go.

---

None of these problems were something I could have anticipated without actually trying to build something end-to-end. Using AI tools like Cursor and frameworks like Tanstack Start didn't make me a fullstack engineer overnight since I still had to consult the documentation and do manual debugging for things to work. But it lowered the barrier of entry, enough to ship something useful without having to master the entire stack. If you're a backend engineer sitting on a similar idea, just start building.

### PS:

Follow FLP on [GitHub](https://github.com/flpstudio) and [LinkedIn](https://www.linkedin.com/company/fujitsu-launchpad/) to stay updated on new products and technologies from our team.

---

---

---

# 🇯🇵 日本語版

バックエンドエンジニアとして働いてきた中で、これまで数えきれないほどの API endpoint や business logic を作って保守してきました。データベース操作も、Prisma のような ORM layer 経由でやることもあれば、ややこしいケースでは raw SQL を手書きすることもあります。

ただ、それでも ad-hoc なデータ分析となると話は別です。production のデバッグでも analytics 用途でも、SQL query を書くのはいまだに苦手ですし、複数テーブルの join や複雑な aggregation になると、もうなかなか大変です。なので、本来 SQL を知らなくていい business チームが自分たちでデータから示唆を引き出そうとすると、その摩擦はさらに大きくなります。

今のところ、各プロジェクトの production データを取り込んで BigQuery にミラーする、かなり整った data pipeline はすでにあります。そしてそれには Metabase からアクセスできます。Metabase の visual query builder は、シンプルな aggregation なら十分便利です。

ただ、もう少し踏み込んだ分析をしようとすると、結局は複雑で読みづらく、保守もしにくい SQL query に頼ることが多いんですよね。そこで出てきたのが、「ユーザーが plain text でやりたいことを書くだけで、SQL は AI agent に任せられないか？」という発想です。

Metabase には database schema の探索や SQL query 実行のための REST API がすでにあるので、Tanstack Start と Cloudflare Workers を使って、web ベースの agentic chatbot を作りました。仕組みとしては、正しい dataset と関連する table schema を見つけて、その情報をもとに正しい SQL query を組み立てる、というものです。Cursor を使いながら 2 日ほどで、frontend 開発経験がほとんどない状態でも、ひとまず動くところまで持っていけました。

とはいえ、短期間でできたからといって、ハマりどころがなかったわけではありません。共有する価値がありそうな問題が 3 つありました。

## BigQuery の schema 過多

Metabase の BigQuery connector は、GCP project 内のすべての dataset について、全 table をまとめて見せてきます。つまり filter しないと、LLM は schema 付きでほぼ 200 table ぶんを処理しないといけません。これはかなり非効率でした。input token を大量に消費するうえに、たいてい正しい table を特定できないんです。

そこで tool を `list_datasets`、`list_tables_in_dataset`、`get_table_schema` のように分割したところ、SQL query の構築に必要な schema をすばやく特定できるようになりました。

Metabase を任意の SQL query 実行から守るために、tool call の承認フローを実装するのも、なかなか一筋縄ではいきませんでした。Vercel AI SDK の `useChat` は、そのままでもかなり便利です。

でも、そこに「あとから見返せる conversation history」と「実行承認」を組み合わせると、あっという間に制御が難しくなります。chat bubble が重複したり、tool call の無限ループに入ったり……といった具合です。ここはとにかく辛抱強さが大事でした。`useChat` の documentation をちゃんと読み込んで、callback や hook を適切に使うことで、custom `useChat` 実装の沼に入らずにかなりの問題を解消できました。

## 見えない firewall

最後に、local 環境では全部うまく動いていたのに、Cloudflare Workers に deploy した途端、Metabase への API call が失敗するようになりました。しかも「response が JSON encoded されていない」と言われるんです。典型的な「local では動くのに prod で壊れる」やつですね。

失敗した tool call の生 response を取ってみたところ、原因はなんと Cloudflare Access でした。local で問題なかったのは、Cloudflare WARP を入れていたので、Metabase への request が制限されていなかったからです。必要だったのは、app 用の service token を設定することだけでした。それで無事動くようになりました。

---

こういう問題って、実際に end-to-end で作ってみないと、なかなか予想できないものばかりでした。Cursor のような AI tool や Tanstack Start のような framework を使ったからといって、一晩で fullstack engineer になれたわけではありません。ちゃんと documentation を読みながら、手で debugging もしないと動きませんでした。

ただ、参入障壁を下げてくれたのは確かです。stack 全体を完全にマスターしていなくても、ちゃんと役に立つものを ship できるくらいにはなりました。同じようなアイデアを温めている backend engineer の方がいたら、とにかくまず作り始めてみるのがおすすめです。

### PS:

FLP の最新プロダクトやテクノロジー情報は、[GitHub](https://github.com/flpstudio) と [LinkedIn](https://www.linkedin.com/company/fujitsu-launchpad/) で確認できます。ぜひフォローしてください
