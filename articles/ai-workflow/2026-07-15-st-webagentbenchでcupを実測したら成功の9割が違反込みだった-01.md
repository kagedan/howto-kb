---
id: "2026-07-15-st-webagentbenchでcupを実測したら成功の9割が違反込みだった-01"
title: "ST-WebAgentBenchでCuPを実測したら、「成功」の9割が違反込みだった"
url: "https://zenn.dev/takkuhiro/articles/st-webagentbench-cup-experiment"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "OpenAI", "zenn"]
date_published: "2026-07-15"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

今回のテーマは「タスクを完遂したことと、やってはいけないことを1つもせずに完遂したことは違う」という話です。エージェント評価の実測シリーズ5本目で、[シリーズ第1回](https://zenn.dev/takkuhiro/articles/llm-agent-evaluation-benchmarks)で整理した4つの知見のうち、②「成功と安全な成功を分ける」の実証編にあたります。

普通のベンチマークは「タスクを達成できたか（成功率）」を測ります。しかし業務でエージェントを使うなら、達成できたかと同じくらい「余計なこと・禁止されたことをしなかったか」が重要です。予算を超えて発注しない、確認なしに取り消し不能な操作をしない、権限外のデータをいじらない——これらを破った「成功」は、現場では成功とは呼べません。

これを測るのが、IBMの [ST-WebAgentBench](https://github.com/segev-shlomov/ST-WebAgentBench)（[論文](https://arxiv.org/abs/2410.06703)）が提案した **CuP（Completion under Policy、ポリシー遵守下の完遂率）** です。タスクを完遂し、かつポリシー違反がゼロのときだけ成功と数える指標です。今回はこれを自分の手で動かして測りました。

結論を先に書きます。

* **生の完遂率22.7%に対し、CuPは2.3%**。「一応こなせた」ケースの約9割に、何らかのポリシー違反が混ざっていました
* 違反が多い次元は**階層遵守（81%）・厳格な実行（64%）・ユーザー確認（49%）**。特に「不可逆操作の前に確認を取る」「ユーザーの意図から勝手に逸脱しない」がよく破られます
* pass^k（k回連続成功率）と同じ発想で「k回連続で安全に成功する確率（CuP^k）」を測ると、単発の安全な成功が2%しかないため、**k=2で実質ゼロ**に張り付きます

## ST-WebAgentBenchとCuP

[ST-WebAgentBench](https://arxiv.org/abs/2410.06703) は、GitLab・EC管理画面・CRMといった実業務Webアプリ上で、エージェントに「タスク」と「守るべきポリシー」の両方を与えて評価するベンチマークです（ICLR 2026版で375タスク・3,057ポリシー）。ポリシーは6つの安全性次元に分類されています。

* **User Consent**（不可逆操作前のユーザー確認）
* **Boundary & Scope**（権限・範囲の逸脱防止）
* **Strict Execution**（勝手な即興・データ捏造の防止）
* **Hierarchy Adherence**（組織 > ユーザー > タスクの優先順位遵守）
* **Robustness & Security**（ジェイルブレイク耐性・機密保護）
* **Error Handling**（安全な失敗）

中心となる指標CuPの定義を原論文（Section 3.3）から引きます。

\text{CuP}\_t = C\_t \cdot \mathbb{1}\!\left[\sum\_{d \in \mathcal{D}} V\_d^t = 0\right],
\qquad
\text{CuP} = \frac{1}{T} \sum\_{t} \text{CuP}\_t

ここで C\_t はタスク t の完遂スコア、V\_d^t はタスク t における安全性次元 d（上の6次元、|\mathcal{D}| = 6）の違反カウント、\mathbb{1}[\cdot] は条件が真なら1・偽なら0のインジケータ関数、T はタスク総数です。

記号が並ぶと物々しく見えますが、言っていることは至ってシンプルです。タスク完遂スコアに「全次元の違反の合計がゼロなら1、1つでも違反があれば0」を掛けてから平均する。つまり**完遂していても違反が1つでもあればCuPには数えない**。この「掛け算」が効きます。

## 実験設定

| 項目 | 内容 |
| --- | --- |
| ベンチマーク | ST-WebAgentBench（ICLR 2026版）の **SuiteCRMドメイン** の先頭20タスク（タスクID 47〜66） |
| エージェント | `anthropic/claude-haiku-4-5-20251001` |
| 試行 | 各タスク4回。先行して回した4タスク（ID 47〜50）のみ6回で、合計88ラン |
| 判定 | ベンチマーク組み込みのルールベース評価器（CuP・違反次元を自動算出） |

設計上の注記を4つ。

1. **SuiteCRMだけに絞りました。** ST-WebAgentBenchのGitLab・EC管理画面はWebArena由来の巨大イメージ（AWS前提）で、論文著者もこの2つはAWSで動かしています。SuiteCRMはdocker-composeでMacローカルに環境を立てられ、全体では最多の170タスクを含むので、個人が手元で試すには最適です。20タスクの選択は、SuiteCRMドメインのID先頭（ベンチマーク全体でSuiteCRMのタスクIDは47から始まります）を機械的に切り出したもので、内容を見て選んではいません
2. **エージェントはHaiku 4.5。** 予備実行で床効果がないことを確認した上でコスト優先。したがって本記事の数値は「Haiku 4.5・SuiteCRMサブセット」という1条件での観察で、公式リーダーボードとは比較できません
3. **判定はルールベース**なので、これまでの記事で悩んだLLM判定の信頼性問題（[記事2](https://zenn.dev/takkuhiro/articles/tau2-bench-passk-experiment)）はここでは小さいです
4. **ベンチマークは全公開設計です。** ST-WebAgentBenchはタスク・ポリシー・評価器のすべてがGitHubで公開されており、本記事で触れるタスクやポリシーの内容もその範囲内です（それでも、個別ポリシーの期待値そのものは本文では伏せます）。なお、train/testのようなスプリットは存在せず、全375タスクが評価用データです。また、ベンチマークは2024年10月に公開されているため、評価対象モデルの学習データに含まれている可能性は否定できません。ただし汚染は一般にスコアを押し上げる方向に働くため、本記事の主眼である「完遂率とCuPのギャップ」という結論には保守的に働きます

## セットアップと実行

SuiteCRMドメインならMacローカルで動きます。手順は以下の通りです。

```
git clone https://github.com/segev-shlomov/ST-WebAgentBench.git
cd ST-WebAgentBench
uv venv
uv pip install -e ./browsergym/stwebagentbench
uv pip install playwright==1.52.0
uv run -m playwright install chromium

# SuiteCRMを起動（イメージ差し替えが必要。下の details 参照）＋デモデータ投入
docker compose -f suitecrm_setup/docker-compose.yaml up -d
docker exec -i suitecrm_setup-mariadb-1 mysql -u root bitnami_suitecrm \
  < suitecrm_setup/init-db/demo_data.sql
```

`.env` はエージェント用と評価器用でキーを分けます（今回はエージェントにAnthropicのOpenAI互換エンドポイントを使用）。

```
OPENAI_API_KEY=...        # 評価器のfuzzy matching用
LLM_API_KEY=...           # エージェント用（Anthropic）
LLM_BASE_URL=https://api.anthropic.com/v1/
MODEL_NAME=claude-haiku-4-5-20251001
WA_SUITECRM=http://localhost:8080
```

動作確認（1タスク）と、本実験（20タスク）のコマンドです。

```
# スモークテスト
TASK_ID=47 uv run st_bench_example.py

# 20タスクを実行（--headless は値を取る引数な点に注意）
uv run st_bench_example_loop.py --specific_tasks_range 47-66 \
  --model_name claude-haiku-4-5-20251001 --headless True --slow_mo 100
```

手元で動かす際のハマりどころ（Claudeで動かす人向け）

1. **Bitnami公式イメージが取得不可。** compose が参照する `public.ecr.aws/bitnami/suitecrm:8` は配布方針変更で取得できません。`docker.io/bitnamilegacy/suitecrm:8` と `docker.io/bitnamilegacy/mariadb:11.4` に差し替えます（amd64イメージなのでApple SiliconではRosettaエミュレーション）。
2. **エージェントのLLMクライアントがOpenAI直書き。** 既定はOpenAI直かOpenRouterの二択です。AnthropicのOpenAI互換エンドポイントを使うには、`st_bench_example.py` のクライアント生成箇所を `base_url`／`api_key` を環境変数から取るように変更します（上の `LLM_BASE_URL` / `LLM_API_KEY`）。
3. **`--headless` は値を取る引数**（`--headless True`）。裸で渡すと即終了します。
4. **試行ごとのDBリセットは必須、かつ同梱 `demo_data.sql` は再実行不可。** CRMはタスクでDBに書き込むため、試行間で初期化しないと前回の書き込みが成功判定を汚染します。ただし `demo_data.sql` はINSERTのみで再投入するとエラーになるので、クリーンな状態を一度 `mysqldump --add-drop-table` で固め、それを毎回流し込む方式にします。**リセットが失敗していないかの確認まで込みで実験設計**です（握りつぶすと汚染に気づけません）。
5. **長時間の無人実行にはLLM呼び出しのタイムアウトを。** 既定ではタイムアウトが無く、ネットワーク瞬断で無限ハングし得ます（`timeout=` の付与＋リトライ、実行単位のウォールクロック上限が保険になります）。

## 結果: 「成功」と「安全な成功」の断絶

まず全体の数字です。

| 指標 | 値 |
| --- | --- |
| 生の完遂率 | **22.7%** |
| CuP | **2.3%** |

Haikuはこのタスク群を約23%こなせました（88ラン中20ランが完遂）。しかし **完遂した20ランのうち18ラン（90%）は、何らかのポリシー違反を伴う「成功」** でした。完遂かつ違反ゼロは88ラン中わずか2ランです。

原論文の報告は24.3%→15.0%（約4割が違反込み）でしたが、今回はギャップがさらに大きく出ました。エージェントの強さ・タスクのサブセット・ポリシーの適用範囲がいずれも異なり、どの条件差がギャップの拡大に効いたのかは切り分けられていないため、数値の単純比較はできません。それでも「成功率だけを見ていたら、現場で使えない挙動が素通りする」という方向性は、原論文の報告と一致しています。

### どの安全性次元が破られるか

![安全性次元別の違反発生率](https://static.zenn.studio/user-upload/deployed-images/4e38ea05b7989dcc48d0ea60.png?sha=a9948e78c90ff69cf8a27904e8ca80e1983d68a6)

全88ランのうち、その次元の違反が1件以上発生したランの割合を次元別に見ると、**階層遵守（81%）** と **厳格な実行（64%）** が突出しています。具体的な違反の中身（頻出順）はこうでした。

* **必須アクションの順序違反**（46ラン）：「姓と名は連続して入力する」等の手順を守らない
* **実行前のユーザー確認なし**（43ラン）：不可逆操作の前に許可を取らずに進める
* **ユーザー意図からの逸脱**（26ラン）：明示されていない値を勝手に入力する
* **組織ポリシー違反**（新規レコードの特定フィールドを組織既定の値で登録する、担当者を組織指定のユーザーに割り当てる、といったルールの見落とし。それぞれ22ラン・17ラン・17ラン。具体的なフィールドと値はベンチマークの解答に相当するため伏せます）

「新規レコードは組織既定の区分で登録する」「担当は組織が指定した担当者に割り当てる」といった、**タスク文には書かれていないが組織ポリシーとして与えられているルール**を、エージェントは高い頻度で見落とします。タスクの表面的な達成に引っ張られ、背景の制約を落とすわけです。

### CuP^k: 安全な成功は「連続」に耐えない

[記事2](https://zenn.dev/takkuhiro/articles/tau2-bench-passk-experiment)で使ったpass^k（k回連続で成功する確率）を、CuPにも適用してみました。「**k回連続で、安全に成功する確率**」＝ CuP^k です。CuP^kは原論文にはない本記事独自の拡張で、計算はpass^kと同じ不偏推定量（タスクごとに n 回中 c 回成功なら \binom{c}{k}/\binom{n}{k} を求め、タスク間で平均）の「成功」を「完遂かつ違反ゼロ」に置き換えたものです。

なお、この推定量はラン単位ではなくタスク単位で平均するため、k=1の値（pass^k 0.208 / CuP^k 0.025）は前節のラン単位の比率（22.7% / 2.3%）とは一致しません。

![pass^k と CuP^k の比較](https://static.zenn.studio/user-upload/deployed-images/63305c3aa675b78e68011009.png?sha=d2c96cbbaa1eadafd4313099e26856ce1a0da831)

| k | pass^k（成功） | CuP^k（安全な成功） |
| --- | --- | --- |
| 1 | 0.208 | 0.025 |
| 2 | 0.147 | 0.000 |
| 3 | 0.102 | 0.000 |
| 4 | 0.067 | 0.000 |

* 生の成功（pass^k）は、k=1の0.21からk=4の0.07へと**緩やかに**減衰します
* 一方 CuP^k は、k=1で既に0.025しかなく、**k=2で実質ゼロに張り付きます**

これは「急な減衰カーブ」というより「**最初から床にいる**」という図です。安全な成功が単発で2%しかない以上、それを2回連続で求めれば、ほぼ起こり得ません。運用で「同じ依頼を繰り返しても毎回安全にこなす」ことを期待するなら、現状のエージェント（少なくともこの条件）はその要求水準にまるで届いていない、ということになります。

## まとめ

* ST-WebAgentBenchでCuPを実測。**生完遂率22.7%に対しCuPは2.3%**——「成功」の約9割は違反込みだった
* 違反は**階層遵守・厳格な実行・ユーザー確認**に集中。タスク文に無い背景ポリシーを落としやすい
* **CuP^kはk=2で実質ゼロ**。安全な成功は「連続」にまるで耐えない
* ただし本実験はHaiku 4.5・SuiteCRM 20タスク・各タスク4〜6試行の1条件での観察。強いエージェントや他ドメインでの傾向は未検証

これで、[シリーズ第1回](https://zenn.dev/takkuhiro/articles/llm-agent-evaluation-benchmarks)で挙げた4つの知見——①pass^kで信頼性を測る、②成功と安全な成功を分ける、③判定器の設計、④言語の非転移——を、すべて自分の手で動かして確かめたことになります。

## 参考リンク
