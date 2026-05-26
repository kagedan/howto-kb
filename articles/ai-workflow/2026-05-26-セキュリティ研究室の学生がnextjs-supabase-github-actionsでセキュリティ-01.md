---
id: "2026-05-26-セキュリティ研究室の学生がnextjs-supabase-github-actionsでセキュリティ-01"
title: "セキュリティ研究室の学生がNext.js + Supabase + GitHub Actionsでセキュリティニュースサイトをゼロから作った話"
url: "https://qiita.com/kyukssb/items/d09e720cb8182a2bb0a1"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Gemini", "Python", "TypeScript", "qiita"]
date_published: "2026-05-26"
date_collected: "2026-05-26"
summary_by: "auto-rss"
query: ""
---

## はじめに

サイバーセキュリティの研究室で勉強している学生です。
就活のポートフォリオとして、**セキュリティニュースを自動収集・表示するWebサービス「SecDash」** を作りました。

👉 **https://secdash.vercel.app**

「作ってみた」だけでなく、実際に毎日自動でデータが更新されている**稼働中のサービス**です。

---

## 作ったもの

### SecDash — セキュリティニュースまとめ

![スクリーンショット 2026-05-26 8.48.17.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4438186/426990e5-ff80-4d9d-9559-bec44ba5c1aa.png)


**主な機能**

- NVD・CISA・Hacker Newsから毎日自動でセキュリティニュースを収集
- CVSSスコアで深刻度（Critical / High / Medium）を色分け表示
- フィルター・ページネーション機能
- 脆弱性解説・マルウェア解説・攻撃手法解説ページ（計25ページ）

---

## 技術スタック

| 役割 | 技術 |
|------|------|
| フロントエンド | Next.js 14 / TypeScript |
| データベース | Supabase（PostgreSQL） |
| 自動収集 | Python + GitHub Actions |
| ホスティング | Vercel |
| データソース | NVD API / CISA API / Hacker News API |

---

## システム構成

```
GitHub Actions（毎日JST10時に自動実行）
　　↓
collector.py
　　├── NVD API（最新CVE）
　　├── CISA API（悪用確認済み脆弱性）
　　└── Hacker News API（セキュリティニュース）
　　↓
Supabase（PostgreSQL）
　　↓
Next.js（Vercel）← ユーザーがアクセス
```

---

## 実装のポイント

### 1. NVD APIからCVEを自動収集

```python
def fetch_nvd_cves(days_back: int = 1) -> list[dict]:
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%S.000")
    end   = now.strftime("%Y-%m-%dT%H:%M:%S.000")

    url = (
        "https://services.nvd.nist.gov/rest/json/cves/2.0"
        f"?pubStartDate={start}&pubEndDate={end}&resultsPerPage=20"
    )
    resp = httpx.get(url, timeout=30)
    items = resp.json().get("vulnerabilities", [])
    # CVSSスコアから深刻度を判定
    severity = (
        "critical" if score >= 9.0 else
        "high"     if score >= 7.0 else
        "medium"   if score >= 4.0 else
        "info"
    )
```

### 2. Supabaseへの重複なし保存

```python
def upsert_items(items: list[dict]) -> int:
    for item in items:
        # source_idで重複チェック
        existing = supabase.table("news").select("id").eq("source_id", item["source_id"]).execute()
        if existing.data:
            continue  # 既存データはスキップ
        supabase.table("news").insert(item).execute()
```

### 3. GitHub Actionsで毎日自動実行

```yaml
on:
  schedule:
    - cron: "0 1 * * *"   # 毎日 JST 10:00
  workflow_dispatch:        # 手動実行も可能
```

### 4. Next.jsでSupabaseからリアルタイム表示

```typescript
const { data, error } = await supabase
  .from("news")
  .select("*")
  .order("published_at", { ascending: false })
  .limit(200);
```

---

## コスト

| サービス | 費用 |
|----------|------|
| Supabase | 無料（500MBまで） |
| Vercel | 無料 |
| GitHub Actions | 無料（月2000分） |
| **合計** | **月0円** |

APIコストもゼロで運用できています。

---

## 工夫した点

### セキュリティ解説ページの充実
単なるニュースまとめだけでなく、有名な脆弱性・マルウェア・攻撃手法の解説ページを作りました。

- **脆弱性解説**：Log4Shell・WannaCry・Heartbleed・EternalBlue・ShellShock・Spectre/Meltdown
- **マルウェア解説**：Emotet・Mirai・Stuxnet・NotPetya・Pegasus
- **攻撃手法解説**：SQLインジェクション・XSS・フィッシング・CSRF・DDoSなど8種類

各ページは「このページ1つで価値がある」レベルを目指して、仕組み・被害事例・対策を詳しく解説しています。

---

## 苦労した点

### Gemini APIの無料枠問題
当初はGemini APIでニュースをAI要約する機能を実装しようとしましたが、無料枠の上限（limit: 0）に何度もはまりました。現在はAI要約なしで運用しています。将来的にはAnthropicのAPIで実装予定です。

### GitHub Actionsのエラー対応
環境変数の設定漏れ・依存関係の競合など、ローカルでは動くのにCIで失敗するケースが多く、デバッグに時間がかかりました。

---

## 今後の予定

- [ ] AI要約機能の追加（Claude API）
- [ ] 英語対応（海外ユーザーへのリーチ）
- [ ] Google AdSense収益化（審査中）
- [ ] セキュリティ用語集ページの追加

---

## おわりに

セキュリティの勉強をしながら、実際に動くサービスを作ることができました。
フロントエンド・バックエンド・インフラ・自動化まで一通り経験できたので、
就活でも自信を持ってアピールできる内容になったと思います。

GitHubのコードも公開しています。
👉 **https://github.com/kairi12510/secdash**

フィードバック・スターをいただけると励みになります！
