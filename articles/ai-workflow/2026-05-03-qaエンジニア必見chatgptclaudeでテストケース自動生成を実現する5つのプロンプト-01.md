---
id: "2026-05-03-qaエンジニア必見chatgptclaudeでテストケース自動生成を実現する5つのプロンプト-01"
title: "QAエンジニア必見｜ChatGPT/Claudeで「テストケース自動生成」を実現する5つのプロンプト"
url: "https://qiita.com/aipapalog/items/25c03a629f807d35f5ca"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-05-03"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

QAエンジニアとして、毎日こんな作業に時間を取られていませんか？

- 要件書を読んでテストケースを一から手動で書く
- カバレッジが足りているか手動でレビューする
- バグレポートの書き直しが何度も発生する

ChatGPT / Claude を正しいプロンプトで使えば、これらの作業を**数分に短縮**できます。
本記事では、現役SQAエンジニアが実務で使っている5つのプロンプトを公開します。

---

## プロンプト1 テストケース自動生成

```
You are a senior QA engineer. Generate a comprehensive test case suite for the following feature requirement.

Feature: [要件をここに貼り付ける]

For each test case, provide:
- Test Case ID (TC-001, TC-002...)
- Title
- Preconditions
- Test Steps (numbered)
- Expected Result
- Priority (High / Medium / Low)
- Test Type (Functional / Boundary / Negative / Edge Case)

Include at least:
- 3 positive (happy path) test cases
- 3 negative test cases
- 2 boundary value test cases
- 1 edge case

Format as a table followed by detailed steps for each.
```

**使い方:** `[要件をここに貼り付ける]` を実際の要件定義書やUser Storyに置き換えるだけ。GPT-4o または Claude 3.5 Sonnet 以上推奨。

**出力イメージ:**

| TC-ID | タイトル | 優先度 | 種別 |
|-------|---------|--------|------|
| TC-001 | 正常ログイン | High | Functional |
| TC-002 | 誤パスワードでのログイン | High | Negative |
| TC-003 | パスワード最大長（72文字）でのログイン | Medium | Boundary |

---

## プロンプト2 カバレッジギャップ検出

```
You are a QA test coverage expert. Review the following test cases and identify missing coverage.

Requirements:
[要件を貼り付け]

Existing test cases:
[既存テストケースを貼り付けまたはサマリー]

Identify:
1. Untested scenarios or user flows
2. Missing negative/error test cases
3. Missing boundary conditions
4. Integration points not covered
5. Non-functional aspects overlooked (performance, security, accessibility)

For each gap, suggest a specific test case title and its priority.
```

レビューで指摘を受ける前に自己チェックできます。

---

## プロンプト3 バグレポート品質向上

```
You are a QA engineer. Improve the following bug report to make it clear, reproducible, and developer-friendly.

Original bug report:
[あなたのバグレポートを貼り付け]

Rewrite it with:
- Clear title (format: [Component] Action causes unexpected Result)
- Environment details
- Exact reproduction steps (numbered)
- Expected vs Actual behavior
- Severity and Priority
- Suggested root cause (if obvious)
```

Before: `ログインできない`
After: `[Auth] 誤パスワード5回後、正しいパスワードでもログイン不可（High/P1）`

---

## プロンプト4 リスクベーステスト優先度付け

```
You are a QA risk analyst. Given the following features/changes in this release, prioritize test areas by risk.

Changes in this release:
[変更内容のリスト]

For each area, provide:
- Risk Level (High/Medium/Low)
- Reason for risk rating
- Recommended test depth (Smoke/Sanity/Full Regression)
- Specific test focus areas
```

スプリント終盤の時間不足時に、どこから手をつけるか即座に判断できます。

---

## プロンプト5 回帰テスト範囲の自動決定

```
You are a QA lead. Based on the following code changes, determine the regression test scope.

Code changes summary:
[差分サマリーまたはPRの説明を貼り付け]

Identify:
1. Directly affected features requiring full testing
2. Potentially impacted features requiring sanity testing
3. Unaffected areas where smoke testing is sufficient
4. Specific test cases to prioritize from the existing suite
```

---

## まとめ

| プロンプト | 削減できる作業 | 体感削減率 |
|-----------|--------------|----------|
| 1 テストケース自動生成 | 設計時間 | 約70% |
| 2 カバレッジギャップ検出 | レビュー工数 | 約50% |
| 3 バグレポート改善 | 手戻り | 約60% |
| 4 リスク優先度付け | 判断時間 | 約80% |
| 5 回帰範囲決定 | 分析時間 | 約65% |

これらを含む **35本のQA特化プロンプト集** をGumroadで公開中です（英語版・$10）。
https://isaacson68.gumroad.com/l/awuand

日本語解説付きプロンプト集はnoteで公開しています（¥500）。
https://note.com/isa5/n/n2e704e60b058

---

*役に立ったら LGTM・ストックお願いします。*
