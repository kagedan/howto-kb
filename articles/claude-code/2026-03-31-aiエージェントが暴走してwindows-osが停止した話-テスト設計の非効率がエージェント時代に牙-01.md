---
id: "2026-03-31-aiエージェントが暴走してwindows-osが停止した話-テスト設計の非効率がエージェント時代に牙-01"
title: "AIエージェントが暴走してWindows OSが停止した話 — テスト設計の非効率がエージェント時代に牙を剥く"
url: "https://zenn.dev/saytooy_arch/articles/09-agent-runaway-test-io"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

## 何が起きたか

Claude Codeのマルチエージェント体制で飲食店向けSaaSを開発中、programmerエージェントがテスト修正を60分間繰り返し、Windows OSのCPU/メモリ/ディスクが枯渇してコマンドを受け付けなくなった。

## 原因: テストコードのI/O非効率パターン

### パターン1: vi.resetModules() + dynamic importの繰り返し

```
// 毎テストでモジュールキャッシュを全削除→ディスクから再読込
beforeEach(() => {
  vi.clearAllMocks();
  vi.resetModules();  // ← モジュールキャッシュ全削除
});

it("テスト", async () => {
  const { fn } = await import("@/services/my-service"); // ← 毎回ディスクから再読込
});
```

**影響**: テスト実行1回あたり24+回のモジュール再読込。エージェントが繰り返しテスト実行すると数千回のディスクI/Oに。

**解決**: static importに変更。createClientモックをplain functionにしてvi.clearAllMocksの影響を排除。

### パターン2: beforeEachでの毎テストユーザー作成/削除

```
// 毎テストでDBにユーザー作成→テスト→削除
test.beforeEach(async ({ page }) => {
  await signUpTestUser(...);  // CREATE USER + INSERT shops
});
test.afterEach(async () => {
  await cleanupUser(userId);  // DELETE user
});
```

**影響**: IT 200+回、ST 166回のDB操作が削減可能だった。

**解決**: beforeAll/afterAllに集約。同一describe内のテストはユーザー共有。

### パターン3: vi.mock競合（同一ファイル内の矛盾するモック）

```
// ファイル前半: 実装をテスト
vi.mock("@supabase/supabase-js", () => ({ createClient: ... }));

// ファイル後半: 実装をモック（← これがhoistされて前半のテストも影響）
vi.mock("@/services/usage-counter-service", () => ({ getLabelMonthCount: vi.fn() }));
```

**影響**: 8件のテストが実装ではなくモックをテストしていた（常にundefined返却）。

**解決**: 競合するモックを別ファイルに分離。

## なぜエージェント時代に危険か

人間がテストを実行する場合、1回のvitest実行で「落ちてるな」と気づいて原因を考える。エージェントは「落ちてる→直す→実行→まだ落ちてる→直す→実行→...」を60分間繰り返す。

テスト1回あたりのI/O非効率が小さくても、エージェントの繰り返し実行で**増幅**される。

## 教訓

1. テスト設計のI/O効率はエージェント時代の新しい品質観点
2. beforeEach→beforeAll集約は「テスト速度改善」ではなく「エージェント暴走時のリソース枯渇防止」
3. エージェントの最大実行時間に上限を設けるべき（今回は60分無制限）
