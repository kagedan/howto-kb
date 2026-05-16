---
id: "2026-05-15-claude-は-3-回qwen-は-6-回model-ごとに-fix-verify-の-retry-01"
title: "Claude は 3 回、Qwen は 6 回：model ごとに fix_verify の retry cap を変える設計"
url: "https://zenn.dev/zoetaka38/articles/084af47ccc3162"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

Codens Purple の `fix_verify` loop で、agent の retry cap を model 別に変えた話を書きます。具体的には Claude 系は 3 回、Qwen 系は 6 回、それ以外の model は 5 回を default にしました。最初は全 model 共通の cap 5 で運用していたんですが、production の fix rate と per-token cost を眺めていたら「これ Claude と Qwen で同じ cap にしてる方がおかしい」となって、model prefix で default を切り替える仕組みを入れた、というのが今回の CDTSK-1362 です。

「同じ task に対して、なぜ Claude は 3 回で打ち切るのに Qwen には 6 回まで chance を与えるのか」を説明するのが本題で、ついでに multi-model production を Anthropic API + self-hosted Qwen で回している我々の歴史的な選択も書きます。最近の Anthropic の `claude -p` / Agent SDK / CI restricted from subscription という発表が、結果として我々の構成を validation した形になっているので、その文脈にも触れます。

## fix\_verify loop とは何をやっている loop か

Codens Purple は、agent が「コードを修正する → verify (test / lint / type check) を回す → 落ちたら feedback を入れて再 retry する」 という loop で動いている product です。fix\_verify という名前のとおり、fix と verify が交互に走るだけのシンプルな構造です。

1 回の retry のコストは、おおざっぱに言えば

* agent への prompt cost (input token)
* agent からの応答 cost (output token)
* verify 実行のための CI / sandbox cost

の合計です。Claude の場合はこの中で input/output token cost が支配的で、Qwen を self-hosted で動かしているケースだとサーバ側の compute が支配的になります。同じ「retry を 1 回増やす」でも、model 側の単価構造が違うと、retry cap の増減がそのまま比例で効くわけではないんですよね。

retry cap を増やす意味は単純で、「もう 1 回試したら通るかもしれない」 という期待です。逆に減らす意味は、「これ以上試しても通らないだろう、credit の無駄」 という諦めです。問題は、この curve が model ごとに全然違うことに、しばらく経ってから気づいた、というところにあります。

最初の実装は cap = 5 固定でした。深く考えずに「5 回くらいやれば通るやろ」 で決めた数字で、project ごとに override する API はあるけど default は global 一つ。これで半年くらい動かしてました。

## multi-model production になるまでの経緯

Codens は最初 Claude API だけで動いていました。なぜ最初から Claude API (= raw Anthropic API、per-token billing) だったかというと、subscription を agent から叩く構成だと、tenant が増えた時の credit 配分・cost monitoring・ratelimit 切り分けがどうしても破綻するからです。我々みたいに複数の project と複数の user の task を 1 つの harness で受けて捌く側は、最初から API key で叩いて per-token で使う以外の選択肢が事実上なかった、という感じです。

subscription 系は基本的に「1 人の human user が IDE で対話するため」 の課金モデルなので、CI / background agent / multi-tenant の workload に被せようとすると、規約面でも実装面でも筋が悪い。一方 API は per-token なので「使った分だけ払う」「使う量を tenant ごとに分離できる」「rate limit の制御も自分で持てる」 という三点が揃っていて、我々が必要としているものとマッチしました。

しばらく Claude API onlyで運用してたんですが、特定の task category (細かい syntax 修正や、定型的な refactor) では Claude のコストが overkill になるケースが見えてきたんです。1 token あたりの単価が Claude より大幅に安い open model を使えば、accuracy が少し落ちても retry を増やして trade すれば、全体としては cost が下がるんじゃないか、という仮説です。

で、Qwen を AWS EC2 上のホストに self-hosted で立てて、Claude と並列で task に配れるようにしました。GPU を抱えるのでサーバ側の固定費は高いんですが、推論あたりの marginal cost は低いので、量が稼げる task category では十分割に合います。我々の自社インフラ側で動いているので、Anthropic 側の rate limit と独立にスケールできる、という運用上の効能もあります。

それから少し経って、Anthropic が `claude -p` / Agent SDK / CI 用途は API plan が必要、という方針を明文化しました。これ、subscription 経由で CI を組んでいた teams にとっては強制移行イベントなんですが、我々みたいに最初から API で叩いていた側にとっては完全に non-event でした。むしろ「API 出発で良かった」 を後追いで Anthropic 自身に追認してもらった形で、multi-model + API の構成は、cost 面だけじゃなくて optionality 面でも正解だったと思っています。

## 同じ cap を使ってた頃の問題

multi-model になった直後は、fix\_verify の retry cap は全 model 共通の 5 のままでした。これでしばらく回して、production の fix rate と cost を tenant ごとに集計したら、見たくない数字が出てきます。

Claude 系で fix\_verify が走った task を見ると、cap = 5 に対して

* 1〜3 回目で fix 成功するパターンが大半
* 4 回目以降で初めて通る、というケースはほぼゼロ
* 5 回目まで使い切って結局通らなかった task は、内容を見ると「そもそも仕様の理解がズレている」 系がほとんど

つまり Claude については、4 回目以降の retry がほぼ純粋に credit の無駄になっていて、retry を増やしてもこの「仕様理解がズレている」 という根の問題は解けないんですよね。Claude は 1 attempt あたりの精度が高いので、2〜3 回で通せない task は、5 回でも 10 回でも通らない、というのが集計から読み取れた事実です。

一方 Qwen 系を同じ cap = 5 で見ると

* 1〜2 回目の fix rate は Claude より明確に低い
* 3〜5 回目で初めて通る、というケースが Claude より明らかに多い
* cap が 5 で打ち切られた task の中に、「あと 1 回試せていれば通っていた」 が含まれている形跡

これは model の癖というか挙動の違いで、Qwen は「最初の修正で全部のテストを通そうとして部分的に的外れになる → feedback を受けてターゲットを絞り込む」 という path を辿ることが多くて、retry を重ねるほど fix rate curve が改善していくタイプでした。Claude の「1 発でほぼ正解か、根本的にダメか」 という curve とは別物。

最初は single cap で済まそうとして、「とりあえず cap を 7 に上げれば Qwen 側はカバーできるんじゃないか」 とも考えたんですが、これだと Claude 側の credit 無駄遣いが酷くなる。逆に cap を 3 に下げると Qwen の合格率が低下しすぎて、結局 retry の上で別 model で再実行する hand-off が増えてしまう。同じ cap で両方の model を最適化することは原理的にできないと判断して、model ごとに default を分けることにしました。

## per-model default に分けた実装

実装は CDTSK-1362 で入れました。やったことは 4 つです。

1. `purple_projects` table に nullable な `fix_verify_retry_cap` column を追加 (NULL なら model-based default)
2. `_default_fix_verify_cap(model)` という helper を新設、model 名の prefix で 3 / 6 / 5 を返す
3. API schema 側で project 単位の override を `Optional[int]` + `Field(ge=1, le=20)` で受け取れるようにする
4. TaskUseCase 内で「project の override 値 or model default」 を解決して effective\_cap として使う

helper はこれだけです。

```
def _default_fix_verify_cap(model: str) -> int:
    """Return per-model default retry cap for fix_verify loop."""
    if model.startswith("claude"):
        return 3
    if model.startswith("qwen"):
        return 6
    return 5
```

prefix で雑に分けているのは、`claude-sonnet-4-5` でも `claude-opus-4-7` でも基本 curve は同じ、`qwen2.5-coder` でも `qwen3-coder` でも基本 curve は同じ、という production data からの判断です。完全な model 単位の table にすることもできたけど、新 model を足すたびに table を更新しないと default が落ちる、という運用負荷を嫌って prefix base に倒しました。

API schema 側はこんな感じ。

```
class ProjectUpdate(BaseModel):
    fix_verify_retry_cap: Optional[int] = Field(
        default=None, ge=1, le=20,
        description="Override retry cap. NULL = use model-based default."
    )
```

上限を 20 にしたのは、これ以上にしても fix rate curve が flat になることが Qwen でも確認できているからです。下限 1 は debug 用 (1 attempt で打ち切って verify 結果を見たい、というケース) を想定しています。

DB migration は alembic で 1 行追加。

```
op.add_column(
    "purple_projects",
    sa.Column("fix_verify_retry_cap", sa.Integer(), nullable=True),
)
```

そして TaskUseCase 内で実際に使う側。

```
effective_cap = (
    pp.fix_verify_retry_cap
    or _default_fix_verify_cap(execute_model)
)
```

`pp.fix_verify_retry_cap` が NULL (= 未設定) なら model default を取り、何か値が入っていれば project override を尊重する、というだけの 3 行です。`or` で書いているのは、`fix_verify_retry_cap` が 0 になることを schema 側で禁じているので falsy = None と等価だからです。

この 3 行を入れただけで、Claude 系 task は cap 3 で短く切れるようになり、Qwen 系 task は cap 6 まで retry を許容するようになって、production の cost / fix rate のバランスが目に見えて変わりました。具体的には Claude 側で「4〜5 回目を消費して結局落ちる」 task の credit 消費が一気に消えて、Qwen 側で「あと 1 回あれば通った」 が減った、という二段の効果が出ています。

## tradeoff：新 model を足すたびの default 決定 cost

この設計には明確な tradeoff があって、それは「新しい model 系列を導入するたびに、その model の最適な retry cap default を決めなきゃいけない」 という運用負荷です。

prefix が `claude` でも `qwen` でもない model を入れる場合、`_default_fix_verify_cap` は 5 を返します。これは「とりあえず安全な default」 という意味で 5 を置いているだけで、その model にとっての optimal とは限らない。本当に optimal を決めるには、Claude / Qwen でやったのと同じく、ある程度の production volume を走らせて fix rate curve を観測する必要があります。

実務的には、新 model 入れた直後は cap 5 (= 安全 default) で 2 週間くらい流して、fix rate curve を集計してから default を上書きする、という運用にしています。完全な「全自動で最適 cap を決める」 までは行けていなくて、ここは判断付きの operations を残している領域です。

もう一つ、model prefix match で雑に切っていることの副作用として、`claude-3-haiku` のような将来的に「Claude 系列だけど 1 attempt の cost が低い model」 が来た時に、cap 3 のままでいいのか、という議論が出てくる気がします。これは出てきた時に考える、ということにしています。

## 〆

「全 model で同じ retry cap」 を、production data を見て model ごとに分けるところまで持っていった、という小さな話でした。Claude が 3 で Qwen が 6 という数字自体は我々の workload 固有のもので、他社が同じ numbers になるとは限らないけど、「単一 cap を model 別に分割すべきタイミングが必ず来る」 という構造の話は、multi-model production を回している人には共通する話だと思います。

Codens は API 出発の multi-model 構成で、こういう細かい cap 設計を 1 つずつ詰めながら回しています。興味があれば <https://www.codens.ai/> を覗いてみてください。
