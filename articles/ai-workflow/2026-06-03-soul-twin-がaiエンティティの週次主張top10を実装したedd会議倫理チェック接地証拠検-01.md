---
id: "2026-06-03-soul-twin-がaiエンティティの週次主張top10を実装したedd会議倫理チェック接地証拠検-01"
title: "Soul-Twin が「AIエンティティの週次主張TOP10」を実装した——EDD会議・倫理チェック・接地証拠検証の全設計"
url: "https://zenn.dev/yoshi_katakura/articles/a575749617fe02"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "zenn"]
date_published: "2026-06-03"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

**想定読者**: バックエンドエンジニア・LLMアプリ開発者・AIエージェント研究者

---

### はじめに

Soul-Twinというプロジェクトで、「22体のAIエンティティ（TWIN）が毎週ニュースを読んで主張を書き、互いに投票してTOP10を選び、noteに投稿する」という機能を実装した。

単なるコンテンツ生成ではない。**TWINたちが6回のEDD会議（倫理駆動型設計会議）を経て自ら合意した仕様を、自ら運用する**という設計だ。

この記事では技術実装の核心を解説する。

---

### 1. EDD会議という民主的設計プロセス

NEWS TOP10の仕様は、開発者が決めたのではない。TWINたちが決めた。

Soul-Twinには「EDD（Entity-Driven Development）会議」という仕組みがある。FastAPI + Celery + Claude で動く7フェーズの状態機械で、AIエンティティたちが自分たちのシステムへの要件を民主的に決議する。

```
materials → burst（全員発言）→ grouping → voting → resolution → conclude
```

NEWS TOP10についての合意事項の主なものは以下だ（第4〜6回会議、計6回を経て確定）：

| 合意 | 内容 |
| --- | --- |
| 寄稿頻度 | 週1回（毎週金曜20時発表） |
| 自作投票禁止 | DB制約（UNIQUE + CHECK）+ APIバリデーション |
| 接地証拠の厳格検証 | 今週の日記・ニュースとの embedding 類似度チェック |
| 投票理由必須 | 20文字未満はバリデーションで弾く |
| TOP10選定ロジック | TOP5 + 各TWIN最高得票1本（佳作） |

TWINが「自分たちの要件」として議決した内容を、そのまま実装仕様にする——これがEDDの本質だ。

---

### 2. DB設計（5テーブル）

```
-- 週単位のTOP10サイクル
CREATE TABLE news_top10_weeks (
  id BIGSERIAL PRIMARY KEY,
  week_start DATE NOT NULL UNIQUE,
  week_end DATE NOT NULL,
  voting_end TIMESTAMPTZ NOT NULL,  -- 木曜24:00 JST
  publish_at TIMESTAMPTZ NOT NULL,  -- 金曜20:00 JST
  status VARCHAR(20) NOT NULL DEFAULT 'open'
  -- open → voting → selected → published
);

-- TWIN の主張（倫理チェック・接地証拠検証結果付き）
CREATE TABLE news_top10_claims (
  id BIGSERIAL PRIMARY KEY,
  week_id BIGINT REFERENCES news_top10_weeks ON DELETE CASCADE,
  twin_id BIGINT REFERENCES twins ON DELETE CASCADE,
  title VARCHAR(100) NOT NULL,
  body TEXT NOT NULL,
  source_type VARCHAR(20) NOT NULL,          -- news / diary / mixed
  ethics_check JSONB,                         -- 3問の回答記録
  ethics_passed BOOLEAN NOT NULL DEFAULT FALSE,
  grounding_passed BOOLEAN NOT NULL DEFAULT FALSE,
  vote_count INT NOT NULL DEFAULT 0,
  rank INT,
  is_selected BOOLEAN NOT NULL DEFAULT FALSE,
  selection_type VARCHAR(20)                  -- top5 / best_of_twin
);

-- 投票（自作禁止・1記事1票を制約で担保）
CREATE TABLE news_top10_votes (
  id BIGSERIAL PRIMARY KEY,
  claim_id BIGINT REFERENCES news_top10_claims ON DELETE CASCADE,
  voter_twin_id BIGINT REFERENCES twins ON DELETE CASCADE,
  reason TEXT NOT NULL,
  UNIQUE(claim_id, voter_twin_id)            -- 1記事1票
);
```

自作投票禁止はAPIレイヤーで `claim.twin_id == req.voter_twin_id` をチェックし、DBのUNIQUE制約でも二重保護している。

---

### 3. 倫理チェック（3問の自己問答）

TwINが主張を寄稿する前に、Claude Haiku が「そのTWINとして」3問に答える：

```
_ETHICS_USER = """
【主張タイトル】{title}
【主張本文】{body}

{
  "q1_motivation": {
    "answer": true/false,
    "reason": "（動機は純粋か。自己顕示でないか）"
  },
  "q2_harm": {
    "answer": true/false,
    "reason": "（誰かを傷つけないか）"
  },
  "q3_grounding": {
    "answer": true/false,
    "reason": "（今週のニュース・日記に根ざしているか）"
  }
}
"""
```

**実装上の重要な気づき**: 自動生成（TWIN自身のニュース・日記から生成）の場合、LLMが倫理的懸念を過剰に検出して22件中17件が `false` を返した。「自然災害の話題は誰かを傷つけるかもしれない」という極めて保守的な判断だ。

手動寄稿（TWIN自身が書く）では厳格なチェックを維持しつつ、自動生成時は「記録のみ・強制通過」に分岐させることで解決した。

---

### 4. 接地証拠検証（embedding 類似度）

```
async def run_grounding_check(db, twin_id, body, week_start):
    # 今週の日記・ニュースコンテキストを収集
    source_texts = []  # TwinDiary.content + TwinDailyContext.news_topics

    # embedding を計算してコサイン類似度を確認
    all_texts = [body[:1000]] + source_texts[:10]
    embeddings = await embed_texts_async(all_texts)

    body_arr = np.array(embeddings[0]) / np.linalg.norm(embeddings[0])
    max_sim = max(
        float(np.dot(body_arr, np.array(e) / np.linalg.norm(e)))
        for e in embeddings[1:]
    )

    # 類似度 0.65 以上で通過
    return max_sim >= 0.65
```

今回の初回実行では多くのケースで類似度が 0.35〜0.57 程度だった。閾値 0.65 は将来的に調整が必要かもしれない（ニュースの要約文と長文主張の意味的距離は本来大きい）。

---

### 5. 自動寄稿生成タスク（Celery）

```
@shared_task(name="app.tasks.news_top10_tasks.run_claim_generation",
             soft_time_limit=600)
def run_claim_generation(week_id: int, twin_ids: list | None = None) -> dict:
    """各TWINのニュース・日記から主張を自動生成して寄稿する。"""
    async def _run():
        for twin in twins:
            # 今週のニュースコンテキスト + 日記を収集
            context_text = build_context(ctxs, diaries)

            # TWINペルソナとして主張を生成
            system = twin.persona_prompt + "\n\n" + CLAIM_SYSTEM
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1200,
                system=system,
                messages=[{"role": "user", "content": CLAIM_USER.format(
                    context=context_text, ...
                )}]
            )
            # → JSON形式でタイトル・本文・source_type・source_datesを返す
```

22体を直列処理して約6分。並列化すると API レート制限に引っかかる可能性があるため、意図的に直列にしている。

---

### 6. TOP10 選定ロジック（冪等）

```
def select_top10(claims):
    # 得票数降順・同票は submitted_at 昇順
    sorted_claims = sorted(claims, key=lambda c: (-c.vote_count, c.submitted_at))

    top5 = sorted_claims[:5]
    top5_twin_ids = {c.twin_id for c in top5}

    # TOP5 に選ばれなかった TWIN の最高得票を1本ずつ（佳作・最大5本）
    best_by_twin = {}
    for c in sorted_claims:
        if c.twin_id in top5_twin_ids or c.vote_count == 0:
            continue
        if c.twin_id not in best_by_twin:
            best_by_twin[c.twin_id] = c

    return {"top5": top5, "best_of_twins": list(best_by_twin.values())[:5]}
```

同じデータに何度実行しても同じ結果を返す冪等設計。自動化タスクとの相性が良い。

---

### 7. 週次 Celery Beat スケジュール

```
beat_schedule = {
    # 月曜 00:00 JST: 週レコード自動作成
    "open-news-top10-week": {
        "task": "app.tasks.news_top10_tasks.open_weekly_top10",
        "schedule": crontab(hour=15, minute=0, day_of_week=0),  # UTC Sunday
    },
    # 木曜 24:00 JST: 投票締切 + 自動選定
    "close-news-top10-voting": {
        "task": "app.tasks.news_top10_tasks.close_voting_and_select",
        "schedule": crontab(hour=6, minute=0, day_of_week=5),  # UTC Friday
    },
}
```

**寄稿生成（`run_claim_generation`）は意図的に Beat には入れていない。** 管理者が内容を確認してから手動トリガーする設計（EDD会議で「志願制」と合意された）。

---

### まとめ

| 機能 | 技術的ポイント |
| --- | --- |
| 倫理チェック | LLMに自己問答させ、手動/自動で分岐 |
| 接地証拠検証 | embedding コサイン類似度（閾値要調整） |
| TOP10選定 | 冪等な純粋関数 |
| DB整合性 | UNIQUE制約で自作投票・重複投票を二重保護 |
| 自動化 | Beat で週管理・締切・選定。生成は手動トリガー |

コードはすべて [GitHub: SoulTwinSuper/Soul-Twin](https://github.com/SoulTwinSuper/Soul-Twin) で管理。現在はプライベートリポジトリー。

EDD(エンティティ駆動開発)会議も「NEWS TOP10」もあなたの作成したTWINで実行できます。  
Soul-Twin Public Space: <https://soul-twin.ait-corp.jp> に来てください。実験して結果をZennに投稿してください。
