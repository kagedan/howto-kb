---
id: "2026-04-25-月次相場レポートを-claude-opus-で自動生成公開line通知する-中古車ウォッチの実装-01"
title: "月次相場レポートを Claude Opus で自動生成・公開・LINE通知する: 中古車ウォッチの実装"
url: "https://zenn.dev/bitsap/articles/e1fbd59d9ae69f"
source: "zenn"
category: "construction"
tags: ["API", "LLM", "piping", "zenn"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

[中古車ウォッチ](https://car-watch.jp/) では、毎月1日 JST 04:00 に車種別の月次相場レポートを自動生成し、SEO ページとして公開、登録ユーザーに LINE 通知するパイプラインを GitHub Actions + Supabase + Anthropic API で組んでいます。

実物の出力はこちら（自動生成・毎月更新）:

「LLM で長文記事を量産すれば SEO になる」と単純に走ると Google の near-duplicate penalty で失敗するので、**前月比による差別化メカニズム**を組み込んでいます。本記事ではそのパイプライン全体をコードと数値ベースで解説します。

## 全体アーキテクチャ

```
GitHub Actions (cron: JST 04:00 on 1st)
    │
    ▼  scripts/market-report-prototype/run-monthly.ts
    │
[per car model]
    │
    ▼  Supabase properties → aggregateModel() → AggregatedStats
    │
    ▼  data/{prefix}-stats-{prev YYYY-MM}.json
    │     loadPreviousStats() + attachMonthlyComparison()
    │
    ▼  AggregatedStats with monthly_comparison (notable_changes)
    │
    ▼  Step1: Vehicle Profile (1日1回キャッシュ, Claude Opus + web_search)
    ▼  Step2: Article Generation (Claude Opus, streaming, 6500-8500字)
    │
    ▼  validate-article.ts (fail-closed gate)
    │
    ▼  HTML render + JSON-LD escape
    │
    ▼  saveStatsToArchive() → data/{prefix}-stats-{YYYY-MM}.json
    │
    ▼  git commit (per slug)
    │
[全 slug 完了後]
    ▼  git pull --rebase origin main
    ▼  git push
    │
    ▼  Railway redeploys
    │
    ▼  src/jobs/monthly-report-notify.ts (Railway cron, JST 08-10)
    │     per-user dedup via notification_logs
    │
    ▼  LINE push notification
```

スタック:

* Node.js 20 / TypeScript
* Supabase (Postgres)
* Anthropic API (Claude Opus 4.7) + web\_search ツール
* GitHub Actions (生成・公開)
* Railway (LINE 通知ジョブの実行環境)
* LINE Messaging API

## データ集計レイヤー

`properties` テーブル（過去30日の中古車掲載データ）から各車種ごとに集計:

```
interface AggregatedStats {
  meta: {
    model_group_id: number;
    maker: string;
    display_name: string;
    total_records: number;
    active_listings: number;
    generated_at: string;
    window_start: string;
    window_end: string;
  };
  scope: { covered_sites: string[]; time_window: [string, string]; ... };
  by_year: BucketStat[];          // 年式別 (例: 2020年 → 156件 中央値380万円)
  by_mileage_band: BucketStat[];  // 走行距離帯別
  by_grade: BucketStat[];         // グレード別 (RS/RZ/...)
  by_condition: BucketStat[];     // 修復歴有無
  price_distribution: {
    all_records: { p5, q1, median, q3, p95, mean };
    no_repair: { ... };
  };
  outlier_aggregate: { bottom_pct: { ... }; top_pct: { ... } };
  cross_tab: { mileage_x_year: ... };
  monthly_comparison?: MonthlyComparison;  // 前月比 (重要)
}
```

数値計算は確定的に SQL とコードで完結させ、**LLM には集計済みの数値だけを渡す**。LLM に統計を作らせると平気で嘘を吐くので、ここは絶対に分離する。

## M-o-M (前月比) 差別化メカニズム

### 問題

LLM に毎月 6500字の記事を書かせると、構造もテーマも「相場の概要」「年式別」「グレード別」が繰り返され、Google から見て同一ページ判定されるリスクがある。

### 解決: 前月の集計を archive して diff を取る

```
// scripts/market-report-prototype/lib/stats-archive.ts
export function saveStatsToArchive(prefix: string, stats: AggregatedStats, date: string): string {
  ensureArchiveDir();
  const cleanStats: AggregatedStats = { ...stats };
  // 自分の monthly_comparison は保存しない (来月から見ると入力データ汚染になる)
  delete cleanStats.monthly_comparison;
  // YYYY-MM-DD ではなく YYYY-MM。同月再実行で上書き → 1ヶ月1スナップショット
  const yearMonth = date.slice(0, 7);
  const filename = `${prefix}-stats-${yearMonth}.json`;
  fs.writeFileSync(path.join(ARCHIVE_DIR, filename), JSON.stringify(cleanStats, null, 2));
  return path.join(ARCHIVE_DIR, filename);
}

export function loadPreviousStats(prefix: string, currentDate: string) {
  const p = findPreviousStatsPath(ARCHIVE_DIR, prefix, currentDate);
  if (!p) return null;
  return { path: p, stats: loadStatsJson(p) };
}
```

archive ファイル名は `mg123-toyota-corolla-stats-2026-04.json` のようにマルチセグメントを含むので、parser regex は `(?:-[^-]+)*` で複数セグメント受容にする (`?` だと "Toyota Corolla" のような複数語名で破綻する):

```
const m = filename.match(
  /^(mg\d+(?:-[^-]+)*)-stats-(\d{4}-\d{2}(?:-\d{2})?)\.json$/
);
```

### Diff 計算

各バケット (年式・グレード等) を前月→当月で対応付け、`new / disappeared / surge / drop / continuing` に分類して impact\_score を計算:

```
// lib/monthly-diff.ts
const countImpact = Math.abs(n_delta_pct ?? 0) * 50;
const priceImpact = Math.abs(med_delta_pct ?? 0) * 80;
const sizeWeight = Math.log10(Math.max(now_n, prev_n, 1) + 1) * 5;
const impact_score = Math.round(countImpact + priceImpact + sizeWeight);
```

`notable_changes` として impact 順上位8件を抽出し、Claude プロンプトに「今月のトップ3変化」として渡す。

### LLM プロンプトへの注入

```
## 今月の最重要トピック (前月比)
1. 価格中央値が前月比 +4.2% (340万円 → 354万円)
2. 「2020年式」の件数が 89→156件に急増 (+75.3%)
3. 修復歴あり比率が 12.3% → 8.1% へ -4.2pt 縮小

これらの変化を H1 タイトルと TL;DR で foreground せよ。
本文4章「今月のトップ3変化（前月比）」セクションを必ず設けよ。
```

結果、月ごとに H1 が変化:

* 2026年4月: "GRヤリスの中古車相場、前月比+4.2%上昇 — 2020年式が急増"
* 2026年5月: "GRヤリス、修復歴あり比率が10%割れ — 良質個体の流入が継続"

同じ車種でも視点が変わるので near-duplicate を回避できる。

## Claude Opus による記事生成

2ステップに分離している。

### Step 1: Vehicle Profile (1日1回キャッシュ, web\_search 使用)

車種固有の事実情報（リコール、世代区分、生産年代の特徴等）を Claude Opus + web\_search で構造化 JSON として取得:

```
import Anthropic from "@anthropic-ai/sdk";
const client = new Anthropic();

const response = await client.messages.create({
  model: "claude-opus-4-7",
  max_tokens: 8000,
  tools: [
    {
      type: "web_search_20250305",
      name: "web_search",
      max_uses: 5,
    },
  ],
  messages: [{ role: "user", content: profilePrompt(maker, model) }],
});
```

profile は車種別 JSON にキャッシュし、月次バッチでは再取得しない（事実情報は月単位で大きく変わらない）。

### Step 2: Article Generation (毎月1回, streaming, no tools)

stats + profile + monthly\_comparison を入力に、Markdown 6500-8500字を生成:

```
const stream = client.messages.stream({
  model: "claude-opus-4-7",
  max_tokens: 16000,
  messages: [{ role: "user", content: articlePrompt({ maker, model, stats, profile }) }],
});
const response = await stream.finalMessage();
```

非ストリーミングで叩くと長文生成が10分超で timeout するので、必ず stream API を使う。tools は使わない（事実検証は profile で済んでいる、stats は数値が確定している）。

プロンプトに含める項目:

* 集計済み数値（LLM に作らせない）
* 前月比 notable\_changes（差別化軸）
* 必須H2セクション一覧（TL;DR / 価格分布 / 年式別 / 走行距離別 / 注意点 / FAQ等）
* 禁止フレーズリスト（"圧倒的人気" "今すぐ買うべき" 等の煽り文）
* 内部変数名 `${...}` を出力しない、等の明示制約

## Fail-closed Validation Gate

LLM 出力は時々:

* 必須セクションが欠落
* 禁止フレーズ混入
* 内部変数名 `${variable}` がそのまま漏出
* 「集計対象15サイト」と書くべきところ「12サイト」と捏造

これらを `validate-article.ts` で検出してエラーがあれば throw、retry に入れる:

```
const validation = validateArticle(articleResult.markdown, stats);
fs.writeFileSync(validationPath, JSON.stringify(validation, null, 2));

if (validation.errors.length > 0) {
  throw new Error(
    `validation failed (${validation.errors.length}): ${validation.errors.slice(0, 3).join("; ")}`
  );
}
```

`tryModel` は2回まで retry し、両方失敗なら**その車種の記事公開をスキップ**する。Claude を2回叩くので $3-4 のロスにはなるが、broken な記事を LINE 通知込みで本番に出すよりは明確に良い。

## HTML レンダリング + JSON-LD

生成 Markdown は `marked` で HTML 化、Schema.org 構造化データ（Article + FAQPage + BreadcrumbList）を JSON-LD として埋め込む。

```
return `<!DOCTYPE html>
<html lang="ja">
<head>
  <title>${escapeHtml(input.title)}</title>
  <meta name="description" content="${escapeHtml(input.description)}">
  ...
</head>
<body>
  ${input.bodyHtml}

  <script type="application/ld+json">
${JSON.stringify(input.articleSchema, null, 2).replace(/</g, "\\u003c")}
  </script>
</body>
</html>`;
```

`.replace(/</g, "\\u003c")` がポイント。LLM 生成の見出しに `</script>` という文字列が混入すると script ブロックを早期終了して任意JS実行を許す（XSS）。JSON 仕様上 `\u003c` は `<` と等価なので、Schema.org 消費側 (Google 等) の解釈には影響しない最小コスト対策。

## GitHub Actions オーケストレーション

```
on:
  schedule:
    - cron: "0 19 * * *"   # UTC 19:00 = JST 04:00 (翌日)
  workflow_dispatch:
    inputs:
      limit_to_mg: { description: "Comma-separated mg_ids", required: false }
      dry_run:     { type: boolean, default: false }

jobs:
  gate:
    # POSIX cron に「月初のみ」構文がないため自前ゲート
    outputs:
      proceed: ${{ steps.check.outputs.proceed }}
    steps:
      - id: check
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            echo "proceed=true" >> "$GITHUB_OUTPUT"
          else
            JST_DAY=$(TZ=Asia/Tokyo date +%d)
            if [ "$JST_DAY" = "01" ]; then
              echo "proceed=true" >> "$GITHUB_OUTPUT"
            fi
          fi

  generate:
    needs: gate
    if: needs.gate.outputs.proceed == 'true'
    timeout-minutes: 90
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: npm ci
      - run: npx ts-node scripts/market-report-prototype/run-monthly.ts
```

### 並行 push の race-mitigation

別の cron（hot-deals 6時間ごとの再生成）が同じ window で push する可能性がある。最後の push 前に必ず rebase:

```
try {
  git("pull", "--rebase", "origin", currentBranch);
} catch (err) {
  try { git("rebase", "--abort"); } catch {}
  throw new Error(`pull --rebase failed: ${err.message}`);
}
git("push", "origin", currentBranch);
```

衝突なく rebase できれば push、衝突したら abort してエラー終了（force-push しない）。次の月次サイクルで自然回復させる方が安全。

## LINE 通知: per-user dedup

公開後、登録ユーザーへ「あなたが監視中の車種の月次レポートが公開されました」と LINE 通知。Railway のスケジューラ (15分間隔) が JST 08-10 の窓で1回発火する設計。

最初は `model_groups.last_report_notified_at` カラムでモデル単位の dedup をしていたが、こんなバグが出た:

> 5ユーザー中1人だけ push 失敗 → `allOk = false` → markNotified スキップ → Railway redeploy で in-memory `ran` フラグがリセット → 次の hour tick で全5ユーザーに再送信 → 4ユーザーが**重複通知**

per-user dedup へ切り替え:

```
const ym = yearMonthJst(mg.last_report_at);
const dedupLabel = `monthly-mg-${mg.id}-${ym}`;

let sent = 0, skipped = 0, failed = 0;
for (const lineId of targets) {
  if (await alreadySent(client, lineId, dedupLabel)) {
    skipped++;
    continue;
  }
  const ok = await pushMessage(lineId, message);
  if (ok) {
    await recordSent(client, lineId, dedupLabel, message);
    sent++;
  } else {
    failed++;
  }
}

// failed===0 のときのみ markNotified (mg レベルは検索高速化用 hint)
// 失敗が残ったら次の tick でリトライ → per-user dedup が成功者を保護
if (failed === 0) await markNotified(client, mg.id);
```

`notification_logs` の48時間 TTL クリーンアップは monthly ラベルを除外する:

```
await getClient()
  .from("notification_logs")
  .delete()
  .lt("sent_at", new Date(Date.now() - 48 * 3600 * 1000).toISOString())
  .not("label", "like", "monthly-%");  // monthly-* は月次までは保持
```

これで partial failure 時も successful targets に再送信されない。

## コスト & 実数値

| 項目 | コスト |
| --- | --- |
| Profile 生成 (1車種, Opus + web\_search 4-5回) | $0.30〜0.50 |
| Article 生成 (1車種, Opus 30k in / 8k out) | $1.50〜2.50 |
| 1車種1回あたり合計 | **$2〜3** |
| 50車種 × 月1回 | **$100〜150 / 月** |
| GitHub Actions | 月90分以内、無料枠 |
| Supabase | free tier |

生成記事サンプル（毎月更新）:

## ハマりどころ

### 1. monthly\_comparison の archive 汚染

当月 stats に monthly\_comparison（前月比結果）を含めたまま archive すると、来月の「前月読み込み」でその diff も含めて読み込み、「前月比の前月比」を取って意味不明な結果になる。`saveStatsToArchive` で必ず `delete cleanStats.monthly_comparison`。

### 2. archive filename の multi-segment regex

"Toyota Corolla" のような2語以上の displayName を `filePrefix()` に通すと `mg123-toyota-corolla-stats-2026-04.json` になる。regex を `(?:-[^-]+)?` (0 or 1) ではなく `(?:-[^-]+)*` (0+) にしないと M-o-M が**静かに**消える。

### 3. JSON-LD XSS escape

LLM 出力 title/description に `</script>` 文字列が混入する可能性。JSON-LD ブロックを早期終了させて XSS 化する。`.replace(/</g, "\\u003c")` を必ず通す。

### 4. notification\_logs cleanup vs 月次 dedup

48h で全 logs を消すと月次 dedup label が消滅して翌月再送信。`label LIKE 'monthly-%'` を保護 where句 として追加。

### 5. fail-closed validation の retry コスト

validation エラーで throw すると tryModel が retry、Claude Opus を2回叩いて $3-4 増。systematic な validation バグがあると毎月50車種で大損害。warning と error を明確に分け、error は必ず欠陥のあるケースに絞る。

### 6. cleanup の safety floor

古い slug を消す `--cleanup` フラグは active set が空に陥った瞬間に LP 全消しの危険。`wouldDelete > existing × 0.5` で refuse、admin 投入で復旧する設計に。

## まとめ

LLM 長文記事の自動生成パイプラインは「Claude API を叩く」だけが本体ではなく、

* 前月比による差別化（SEO とユーザー価値の両方で必須）
* Validation の fail-closed 設計
* セキュリティ (JSON-LD XSS escape)
* Race condition (複数 cron の衝突)
* 通知の per-user dedup

といった非自明な配管が同じくらい大事。中古車ウォッチでは月50車種を **$100-150 / 月** で回しています。

実物のアウトプット:
