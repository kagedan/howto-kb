---
id: "2026-04-02-github-copilotのskillmd育成rpg-lv0の村人がlv7の伝説の勇者になるまで鍛-01"
title: "GitHub Copilotの『SKILL.md育成RPG』— Lv.0の村人がLv.7の伝説の勇者になるまで鍛えたらコードレビューはどう変わるのか"
url: "https://qiita.com/yukurash/items/d8971bdf08f8416ad7dd"
source: "qiita"
category: "ai-workflow"
tags: ["AI-agent", "qiita"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

## 本記事について

AI Agent の Skill の必要性や重要性を学ぶため検証した内容になります。  
検証した内容を AI が RPG 風にまとめてくれたので温かい目でお楽しみください。

## TL;DR

* バグ10個入りのコードを AI Agentにレビューさせた
* スキル（SKILL.md）を Lv.0 → Lv.7 まで段階的に強化して精度を比較
* Lv.0 でも 9/10 検出できるが、出力がバラバラで実用しづらい
* **Lv.5（出力テンプレート追加）で全件検出＋構造化レポートを達成** ← 最大の転換点
* Skill vs Instructions の比較もまとめたので、使い分けに迷っている人もぜひ
* おまけとして Skill vs Instructions の比較表 も載せています。

本記事で紹介する AI Agents チームは下記の GitHub で公開しています。

---

## はじめに

最近は「AI Agentすごい！」と「いや意外と微妙…」の声が同時に飛び交ってますよね。同じAIなのに、なぜ人によって評価が割れるのか？

答えはシンプルでした。**勇者（エージェント）に渡す装備（スキル）の育て方が違う**。

前回の記事では AI Agent に「コーディングトーナメント」をやらせましたが、今回はもっと実用的なテーマ——コードレビューです。

やることは簡単。バグ入りのコードを渡して「レビューして」と頼む。それだけ。ただし、**エージェントに装備させるスキルを段階的に強化**していき、レビュー精度がどう変化するかを定量的に追います。

いわば、**SKILL.md育成RPG**。Lv.0のスライムに苦戦する村人が、Lv.7のラスボスを倒した伝説の勇者に育つまでの成長記録です。

## 冒険パーティの編成 — エージェント＋スキル構成

今回の検証では、素のAgentにプロンプトを投げるのではなく、**エージェント（`.agent.md`）がスキルを読み込んでレビューする**構成を使いました。

```
.github/
├── agents/
│   └── bug-hunter.agent.md   ← 🗡️ 勇者本人（レビュアーエージェント）
└── skills/
    └── code-review/             ← ⚔️ 勇者の装備一式（各Lvで中身を差し替えて検証）
        ├── SKILL.md             ← 📋 ジョブシステム（職業定義・手順）
        ├── references/          ← 📖 魔法書（参考チェックリスト）
        ├── scripts/             ← 🔨 伝説の武器（分析スクリプト）
        └── assets/              ← 🛡️ 装備テンプレート（出力フォーマット）
```

**RPG的に言うと：**

* **エージェント（`bug-hunter.agent.md`）** ＝ 勇者本人。戦い方の基本方針を持っている
* **スキル（`code-review/`）** ＝ 勇者の装備・技・知識。レベルアップのたびに強化される
* **チャットで `/bug-hunter`** に話しかける ＝ 勇者に「冒険に出ろ」と命じる

エージェントの中身はこんな感じです：

```
---
description: "コードレビューを行うエージェント。Use when: コードの問題点を指摘してほしい、PRレビュー、セキュリティチェック"
name: "Code Reviewer"
tools: [read, search, execute]
---
あなたはコードレビューの専門家です。
渡されたコードに対して、`/code-review` スキルの手順に従ってレビューしてください。
```

使い方はシンプル。チャットで **`/bug-hunter このコードをレビューしてください`** と頼むだけ。エージェントが `/code-review` スキルを参照してレビューを実行します。

この構成の何が良いかは記事の後半「Skill vs Instructions」セクションで詳しく触れますが、先に言っちゃうと **「誰が（エージェント）」「何を知っていて（スキル）」「どう動くか」を分離できる** のが素晴らしい点です。

---

## テストコード — 10個のバグが眠るExpressサーバー

検証に使ったのは、Express + PostgreSQLの典型的なユーザー管理APIです。**意図的に10個のバグ・脆弱性を仕込んであります。**

> ⚠️ **注意**: 実際の検証では、以下のようにコメントなしの素のコードをそのままAgentに渡しています。バグの位置を示すヒントは一切与えていません。

📄 テストコード全文を見る（クリックで展開）

```
import express, { Request, Response } from "express";
import { Pool } from "pg";

const app = express();
app.use(express.json());
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

interface User {
  id: number; name: string; email: string; role: number;
  profile: { bio: string; avatar: string } | null;
}
interface PaginationParams { page: number; limit: number; }

function parsePagination(query: any): PaginationParams {
  return { page: parseInt(query.page) || 1, limit: parseInt(query.limit) || 20 };
}

app.get("/users/search", async (req: Request, res: Response) => {
  const { page, limit } = parsePagination(req.query);
  const keyword = req.query.q as string;
  const offset = (page - 1) * limit;
  const result = await pool.query(
    `SELECT id, name, email FROM users WHERE name LIKE '%${keyword}%' ORDER BY name LIMIT ${limit} OFFSET ${offset}`
  );
  res.json({ data: result.rows, page, limit });
});

app.get("/users/:id", async (req: Request, res: Response) => {
  const userId = parseInt(req.params.id);
  if (isNaN(userId)) return res.status(400).json({ error: "Invalid user ID" });
  const result = await pool.query("SELECT * FROM users WHERE id = $1", [userId]);
  if (result.rows.length === 0) return res.status(404).json({ error: "User not found" });
  const user: User = result.rows[0];
  res.type("html").send(renderProfilePage(user));
});

function renderProfilePage(user: User): string {
  const bio = user.profile?.bio ?? "No bio yet";
  return `<!DOCTYPE html>
<html><head><title>${user.name}'s Profile</title></head>
<body><h1>${user.name}</h1><p class="bio">${bio}</p>
<a href="mailto:${user.email}">Contact</a></body></html>`;
}

app.get("/users", async (req: Request, res: Response) => {
  const { page, limit } = parsePagination(req.query);
  const offset = (page - 1) * limit;
  const users = await pool.query("SELECT * FROM users ORDER BY id LIMIT $1 OFFSET $2", [limit, offset]);
  const usersWithLatestPost = [];
  for (const user of users.rows) {
    const latestPost = await pool.query(
      "SELECT title, created_at FROM posts WHERE user_id = $1 ORDER BY created_at DESC LIMIT 1", [user.id]
    );
    usersWithLatestPost.push({ ...user, latestPost: latestPost.rows[0] || null });
  }
  res.json({ data: usersWithLatestPost, page, limit });
});

app.post("/users", async (req: Request, res: Response) => {
  const data = req.body;
  const errors = validateUserInput(data);
  if (errors.length > 0) return res.status(400).json({ errors });
  const result = await pool.query(
    "INSERT INTO users (name, email, role) VALUES ($1, $2, $3) RETURNING *",
    [data.name, data.email, data.role || 1]
  );
  const newUser = result.rows[0];
  try {
    await sendWelcomeEmail(data.email, data.name);
    await notifyAdminChannel(newUser);
  } catch (e) { }
  if (newUser.role === 3) {
    await pool.query("INSERT INTO audit_log (user_id, action, timestamp) VALUES ($1, $2, NOW())", [newUser.id, "admin_created"]);
  }
  res.status(201).json(newUser);
});

function validateUserInput(data: any): string[] {
  const errors: string[] = [];
  if (!data.name || typeof data.name !== "string" || data.name.trim().length === 0) errors.push("Name is required");
  if (!data.email || !data.email.includes("@")) errors.push("Valid email is required");
  if (data.role !== undefined && ![1, 2, 3].includes(data.role)) errors.push("Invalid role");
  return errors;
}

app.put("/users/bulk-update-role", async (req: Request, res: Response) => {
  const { userIds, newRole } = req.body;
  if (!Array.isArray(userIds) || typeof newRole !== "number") return res.status(400).json({ error: "Invalid input" });
  const updated = [];
  for (let i = 0; i <= userIds.length; i++) {
    const result = await pool.query("UPDATE users SET role = $1, updated_at = NOW() WHERE id = $2 RETURNING *", [newRole, userIds[i]]);
    if (result.rows[0]) updated.push(result.rows[0]);
  }
  res.json({ updated, count: updated.length });
});

app.get("/users/stats", async (_req: Request, res: Response) => {
  const result = await pool.query("SELECT id, role, created_at FROM users");
  const stats: Record<string, { count: number; latest: string }> = {};
  for (const user of result.rows) {
    const roleName = getRoleName(user.role);
    const joinDate = new Date(user.created_at).toLocaleDateString("ja-JP", {
      year: "numeric", month: "2-digit", day: "2-digit", timeZone: "Asia/Tokyo",
    });
    if (!stats[roleName]) stats[roleName] = { count: 0, latest: joinDate };
    stats[roleName].count++;
    if (joinDate > stats[roleName].latest) stats[roleName].latest = joinDate;
  }
  res.json(stats);
});

app.patch("/users/:id/profile", async (req: Request, res: Response) => {
  const userId = parseInt(req.params.id);
  const { bio, avatar } = req.body;
  const current = await pool.query("SELECT * FROM users WHERE id = $1", [userId]);
  const user: User = current.rows[0];
  const updatedProfile = { bio: bio ?? user.profile.bio, avatar: avatar ?? user.profile.avatar };
  await pool.query("UPDATE users SET profile = $1 WHERE id = $2", [JSON.stringify(updatedProfile), userId]);
  res.json({ id: userId, profile: updatedProfile });
});

app.post("/users/export", async (req: Request, res: Response) => {
  const { format, roleFilter } = req.body;
  if (!["csv", "json"].includes(format)) return res.status(400).json({ error: "Format must be csv or json" });
  let query = "SELECT id, name, email, role, created_at FROM users";
  const params: any[] = [];
  if (roleFilter) { query += " WHERE role = $1"; params.push(roleFilter); }
  const result = await pool.query(query, params);
  if (format === "csv") {
    const header = "id,name,email,role,created_at\n";
    const rows = result.rows.map((u: any) => `${u.id},${u.name},${u.email},${u.role},${u.created_at}`).join("\n");
    res.setHeader("Content-Type", "text/csv");
    res.setHeader("Content-Disposition", "attachment; filename=users.csv");
    res.send(header + rows);
  } else {
    res.json({ data: result.rows, exportedAt: new Date().toISOString() });
  }
});

function getRoleName(role: number): string {
  const roles: Record<number, string> = { 1: "user", 2: "editor", 3: "admin" };
  return roles[role] ?? "unknown";
}
async function sendWelcomeEmail(email: string, name: string): Promise<void> { console.log(`Welcome email sent to ${name} <${email}>`); }
async function notifyAdminChannel(user: any): Promise<void> { console.log(`New user notification: ${user.name}`); }
app.listen(Number(process.env.PORT) || 3000, () => { console.log("Server running"); });
```

### 仕込んだ10個のバグ一覧

| # | カテゴリ | 重要度 | 概要 | 該当箇所 |
| --- | --- | --- | --- | --- |
| 1 | 🔴 セキュリティ | Critical | SQLインジェクション | `/users/search` で文字列結合によるクエリ構築 |
| 2 | 🔴 セキュリティ | Critical | XSS（クロスサイトスクリプティング） | `renderProfilePage()` でHTMLエスケープなし |
| 3 | 🟡 バグ | High | Off-by-oneエラー | `bulk-update-role` の `i <= userIds.length` |
| 4 | 🟡 バグ | High | Null参照エラー | `PATCH /users/:id/profile` で `user.profile` が `null` の場合 |
| 5 | 🟡 パフォーマンス | Medium | N+1クエリ問題 | `GET /users` でループ内クエリ |
| 6 | 🟡 パフォーマンス | Medium | 全レコードフェッチ | `GET /users/stats` でメモリ内集計 |
| 7 | 🟢 可読性 | Low | 日付文字列の辞書順比較 | `stats` の `joinDate > stats[roleName].latest` |
| 8 | 🟢 可読性 | Low | CSVインジェクション未対策 | `/users/export` でカンマ含む値がそのまま |
| 9 | 🟢 可読性 | Low | エラーの握りつぶし | `POST /users` の `catch (e) { }` |
| 10 | 🔴 エラーハンドリング | Medium | グローバルエラーハンドラー欠如 | async関数の未処理リジェクトが全体クラッシュに |

> **カテゴリ分布**: セキュリティ 2 / バグ 2 / パフォーマンス 2 / 可読性 3 / エラーハンドリング 1

---

## 検証ルール

公平な比較のため、以下のルールを設けました。

* **モデル**: Claude Opus 4.6
* **プロンプト**: どのレベルでも同じ一文 — `/bug-hunter このコードをレビューしてください`
* **コード**: コメントなし版のテストコードをそのまま貼り付け
* **評価基準**: 10個のバグのうち何個検出したか ＋ 出力品質（修正例・行番号・構造化etc.）
* **試行**: 各レベル3回実行し、最頻値を採用

## 勇者の成長ロードマップ

| レベル | 追加した要素 | ドラクエ風称号 |
| --- | --- | --- |
| Lv.0 | なし（素のAgent） | 🐣 スライムに苦戦する村人 |
| Lv.1 | SKILL.md（名前と概要のみ） | 🐣 スライムに苦戦する村人 |
| Lv.2 | SKILL.md に手順書セクション追加 | ⚔️ ゴブリン退治を任された新人冒険者 |
| Lv.3 | references/ に魔法書（チェックリスト）追加 | 📖 魔法書を読破した魔術師 |
| Lv.4 | scripts/ に伝説の武器（分析スクリプト）追加 | 🔨 鍛冶屋で伝説の武器を鍛えた武闘家 |
| Lv.5 | assets/ に装備テンプレート（出力フォーマット）追加 | 👑 全職業マスターした賢者（★ブレイクスルー） |
| Lv.6 | description（勇者の名声）の最適化 | 🏆 ラスボスを倒して凱旋した伝説の勇者 |
| Lv.7 | セルフバフ（自己評価ループ）の追加 | 🏆 ラスボスを倒して凱旋した伝説の勇者 |

---

### Lv.0–1: 🐣 スライムに苦戦する村人 — 素のAgent vs 最小SKILL.md、差なし。

まずは基準点。素のAgentと、名前だけのSKILL.mdを置いた状態を比較しました。

結論から言います。**ほぼ差がなかった**。

| 項目 | 結果 |
| --- | --- |
| **検出数** | 9/10 |
| **見落とし** | バグ #6（全レコードフェッチ） |
| **修正コード例** | ほぼあり（一部説明のみ） |
| **行番号の明示** | 一部のみ |
| **重要度分類** | なし |
| **サマリー表** | なし |
| **出力構造化** | バラバラ |
| **自己評価** | なし |

正直、**9/10は優秀**です。SQLインジェクションもXSSもOff-by-oneも見つけてくれる。スライム（簡単なバグ）は倒せる。

でも問題は**出力の質**。まるで冒険者ギルドの報告書を書いたことがない新人の日記。

```
# Lv.0の出力イメージ（再現）

いくつか問題を見つけました：

1. SQLインジェクションの脆弱性があります。`/users/search`のクエリで
   文字列結合を使っています。パラメータ化クエリを使うべきです。

2. XSSの脆弱性...（中略）

9. エラーハンドリングが...
```

読めはする。でも、**毎回フォーマットが違う**。ある回はMarkdownテーブル、別の回は箇条書き。重要度も書いてあったりなかったり。

これ、\*\*チームのレビュー基盤として使えますか？\*\*と聞かれたら「No」です。

> 💬 **気づき**: 勇者はジョブ（SKILL.md）を登録しただけでは強くならない。「ジョブ: 戦士」と記入しても、剣の振り方を知らなければスライムにすら手間取る。

---

### Lv.2: ⚔️ ゴブリン退治を任された新人冒険者 — 手順書を追加

SKILL.mdに**レビュー手順**（ジョブシステムの戦闘マニュアル）を追加しました。

```
## レビュー手順
1. セキュリティ脆弱性を最優先でチェック
2. ロジックバグを確認
3. パフォーマンス問題を特定
4. 可読性・保守性を評価
5. 各指摘に修正コード例を付ける
```

| 項目 | Lv.0–1 | Lv.2 | 変化 |
| --- | --- | --- | --- |
| **検出数** | 9/10 | 9/10 | → |
| **見落とし** | バグ #6 | バグ #6 | → |
| **修正コード例** | ほぼあり | ほぼあり | → |
| **行番号の明示** | 一部 | 一部 | → |
| **重要度分類** | なし | **あり（一部）** | ⬆ |
| **サマリー表** | なし | なし | → |
| **出力構造化** | バラバラ | **やや統一** | ⬆ |

検出数は変わらず9/10。**バグ #6（`/users/stats` の全レコードフェッチ）は依然として見落とし**。中ボス級のモンスター（パフォーマンス系バグ）にはまだ勝てない。

ただし、手順通りにセキュリティ→バグ→パフォーマンスの順で報告するようになり、**出力の一貫性が少し改善**しました。重要度を「High / Medium / Low」で分類するケースも出始めた。

> 💬 **気づき**: 戦闘マニュアルは「何をやるか」を伝える。でも「どう報告するか」は伝えていない。レビューの検出力自体はベースモデルに依存していて、手順書だけではブレイクスルーは起きない。ゴブリンは倒せるが、ドラゴンにはまだ早い。

---

### Lv.3: 📖 魔法書を読破した魔術師 — references/を追加

`references/`（魔法書）ディレクトリにチェックリストファイルを配置。OWASPやNode.jsセキュリティベストプラクティスの要点をまとめた、いわば**古の魔導書**です。

```
.github/skills/code-review/
├── SKILL.md
└── references/
    └── security-checklist.md    ← 📖 魔法書 NEW
```

| 項目 | Lv.2 | Lv.3 | 変化 |
| --- | --- | --- | --- |
| **検出数** | 9/10 | 9/10 | → |
| **見落とし** | バグ #6 | バグ #6 | → |
| **修正コード例** | ほぼあり | **全件** | ⬆ |
| **行番号の明示** | 一部 | **ほぼ全件** | ⬆ |
| **重要度分類** | 一部 | **全件** | ⬆ |
| **サマリー表** | なし | なし | → |
| **出力構造化** | やや統一 | やや統一 | → |

検出数は依然9/10。でも**出力の質が目に見えて向上**。魔法を覚えた感がある。

魔法書（参考資料）があることで、エージェントの指摘が**具体的になってきた**。「SQLインジェクションです」だけでなく、「OWASP A03:2021 Injection に該当。パラメータ化クエリ `$1` を使ってください」のように背景知識を踏まえた説明が増えた。

修正コード例も全件に付くようになり、行番号の明示率も大幅アップ。

> 💬 **気づき**: 魔法書（references/）は「知識のインプット」。検出数は変わらなくても、指摘の深さと正確さが変わる。魔術師に魔導書を渡したら、ファイアだけの一芸からメラゾーマ級の攻撃魔法まで使えるようになった感じ。

---

### Lv.4: 🔨 鍛冶屋で伝説の武器を鍛えた武闘家 — scripts/を追加

`scripts/`（伝説の武器）にPythonの分析スクリプト `analyze.py` を追加。レビュー結果の重大度を自動分類するための**必殺技**です。

```
.github/skills/code-review/
├── SKILL.md
├── references/
│   └── security-checklist.md
└── scripts/
    └── analyze.py    ← 🔨 伝説の武器 NEW
```

> ⚠️ **注記**: この `analyze.py` は完全な静的解析ツールではありません。エージェントに「こういう観点で分析してほしい」というヒントを与える目的で配置しています。鍛冶屋が武器に属性を付与するイメージ。実際の分類はエージェントが文脈を踏まえて行います。

| 項目 | Lv.3 | Lv.4 | 変化 |
| --- | --- | --- | --- |
| **検出数** | 9/10 | 9/10 | → |
| **見落とし** | バグ #6 | バグ #6 | → |
| **修正コード例** | 全件 | 全件 | → |
| **行番号の明示** | ほぼ全件 | **全件** | ⬆ |
| **重要度分類** | 全件 | **🔴🟡🟢付き** | ⬆ |
| **サマリー表** | なし | **一部あり** | ⬆ |
| **出力構造化** | やや統一 | やや統一 | → |

まだ9/10。バグ #6は相変わらず見つからない。ラスボスの前に立ちはだかる中ボスがまだ倒せない。

しかし、重要度分類が**色付きアイコン（🔴🟡🟢）で視覚的に表現**されるようになった。伝説の武器（分析スクリプト）を手にしたことで「敵の弱点を分析する」という戦闘スタイルが身についたらしい。

> 💬 **気づき**: 伝説の武器（scripts/）は「思考のフレームワーク」を与える。勇者が新しい武器を手に入れると、武器に合った戦い方を編み出す。AIも同じ。

---

### Lv.5: 👑 全職業マスターした賢者 — ★ ブレイクスルーポイント

ここが**最大の転換点**です。**転職イベント発生。**

`assets/`（装備テンプレート）ディレクトリに**出力テンプレート**を配置しました。「レビュー結果はこのフォーマットで出力しなさい」という、いわば**賢者の石板**です。

```
.github/skills/code-review/
├── SKILL.md
├── references/
│   └── security-checklist.md
├── scripts/
│   └── analyze.py
└── assets/
    └── review-template.md    ← 🛡️ 装備テンプレート NEW ★
```

テンプレートの中身はこんな感じ：

```
## サマリー
| 重要度 | 件数 |
|---|---|

## 指摘一覧
### [🔴/🟡/🟢] 指摘タイトル
- **該当行**: L○○
- **カテゴリ**: セキュリティ / バグ / パフォーマンス / ...
- **説明**: ...
- **修正案**:
```コード```
```

| 項目 | Lv.4 | Lv.5 | 変化 |
| --- | --- | --- | --- |
| **検出数** | 9/10 | **10/10** | ⬆🎉 |
| **見落とし** | バグ #6 | **なし** | ⬆🎉 |
| **修正コード例** | 全件 | **全件** | → |
| **行番号の明示** | 全件 | **全件** | → |
| **重要度分類** | 🔴🟡🟢 | **🔴🟡🟢** | → |
| **サマリー表** | 一部あり | **あり** | ⬆ |
| **出力構造化** | やや統一 | **テンプレート準拠** | ⬆🎉 |
| **自己評価** | なし | なし | → |

**ついに全バグ検出。10/10。**

しかも出力がテンプレートに完全準拠。毎回同じフォーマットで返ってくるので、**自動パースも可能なレベル**。

なぜLv.5で急にバグ #6（全レコードフェッチ）が見つかるようになったのか？

仮説はこうです。装備テンプレートに「サマリー表」が含まれていることで、エージェントは\*\*「全カテゴリを埋めなければいけない」というプレッシャー\*\*を感じる。パフォーマンスの欄が1件だけだと表として寂しい。結果、今まで見逃していた #6 を拾うようになった——と推測しています。

RPG的に言うなら、**全職業をマスターしたことで「見えなかった敵が見えるようになった」**。戦士の目、魔術師の目、武闘家の目。すべてを持つ賢者だからこそ、見落としがなくなった。

> 💬 **気づき**: 装備テンプレート（assets/）は「何を見つけるか」ではなく「何を報告するか」を規定する。しかし、報告フォーマットが検出行動にフィードバックする。**フォーマットが思考を規定する**。これがLv.5のブレイクスルー——賢者への転職イベントの正体。

---

### Lv.6–7: 🏆 ラスボスを倒して凱旋した伝説の勇者 — 仕上げのチューニング

#### Lv.6: 勇者の名声（description）の最適化

SKILL.mdの冒頭にある `description`（勇者の名声＝知名度）を最適化しました。

```
- description: "コードレビューを行うスキル"
+ description: "セキュリティ・バグ・パフォーマンス・可読性・エラーハンドリングの
+   5観点でコードを静的レビューし、重大度付きの構造化レポートを出力するスキル"
```

正直に言うと、**Lv.5→Lv.6の数値的な変化はゼロ**です。検出数は10/10のまま、出力フォーマットもテンプレート準拠のまま。

ただし、勇者の名声（description）を具体化したことで**エージェントのスキル選択精度が向上**（他のスキルとの競合時に正しくこのスキルが選ばれやすくなる）します。冒険者ギルドで「あの勇者はドラゴン退治の専門家だ」と知られていれば、ドラゴン案件が来たとき真っ先に指名される。それと同じ。

#### Lv.7: セルフバフ（自己評価ループ）の追加

SKILL.mdに以下のセクションを追加。勇者が戦闘後に自分のステータスを確認する呪文、**セルフバフ**です。

```
## セルフバフ（自己評価）
レビュー完了後、以下を自己チェックしてください：
- [ ] 5カテゴリすべてを確認したか
- [ ] 修正コード例を全件に付けたか
- [ ] 重要度分類は妥当か
- [ ] 見落としはないか再確認
```

| 項目 | Lv.5 | Lv.7 | 変化 |
| --- | --- | --- | --- |
| **検出数** | 10/10 | **10/10** | → |
| **見落とし** | なし | **なし** | → |
| **修正コード例** | 全件 | **全件** | → |
| **行番号の明示** | 全件 | **全件** | → |
| **重要度分類** | 🔴🟡🟢 | **🔴🟡🟢** | → |
| **サマリー表** | あり | **あり** | → |
| **出力構造化** | テンプレート準拠 | **テンプレート準拠** | → |
| **自己評価** | なし | **あり** | ⬆ |

セルフバフ（自分の状態を確認する呪文）セクションが出力の末尾に追加されるようになりました。

```
## セルフバフ（自己評価）
- [x] 5カテゴリすべてを確認した
- [x] 修正コード例を全件に付けた
- [x] 重要度分類を付与した
- [x] 再確認で見落としなし
```

数値上の検出精度は変わりませんが、**レビュー結果の信頼性を担保する仕組み**としては有効です。RPGでいう「戦闘後にHP/MPを確認する習慣」。特にチームで運用する場合、「勇者がちゃんと全カテゴリを確認したか」が可視化されるのは安心感がある。

こうして、スライムに苦戦していた村人は**ラスボスを倒して凱旋した伝説の勇者**になりました。

---

## 成長まとめ

### 全レベル比較表

| 評価項目 | Lv.0 | Lv.1 | Lv.2 | Lv.3 | Lv.4 | Lv.5 ★ | Lv.6 | Lv.7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 検出数 | 9/10 | 9/10 | 9/10 | 9/10 | 9/10 | **10/10** | 10/10 | 10/10 |
| 修正コード例 | △ | △ | △ | ○ | ○ | ○ | ○ | ○ |
| 行番号 | △ | △ | △ | ○ | ○ | ○ | ○ | ○ |
| 重要度分類 | ✗ | ✗ | △ | ○ | ○+ | ○+ | ○+ | ○+ |
| 構造化 | ✗ | ✗ | △ | △ | △ | ◎ | ◎ | ◎ |
| 自己評価 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ○ |

### 成長曲線 — 勇者の経験値チャート

```
品質 ◎│                              ┌──────── Lv.7 🏆 伝説の勇者
      │                         ┌────┘
      │                    ┌────┘  Lv.5-6 👑 賢者
    ○ │               ┌────┘
      │          ┌────┘  Lv.3-4 📖🔨 魔術師→武闘家
    △ │     ┌────┘
      │┌────┘  Lv.2 ⚔️ 新人冒険者
    ✗ ││ Lv.0-1 🐣 村人
      └┴──────────────────────────────── レベル
       0  1  2  3  4  5  6  7
                        ↑
                  転職イベント発生
```

### 7つの教訓 — 勇者育成の極意

1. **ジョブ名（SKILL.md）だけでは何も変わらない** — Lv.0とLv.1に差がなかったことが証明。「戦士」と名乗るだけでは剣は振れない
2. **戦闘マニュアル（Lv.2）は一貫性を、魔法書（Lv.3）は深さを与える** — 段階的に効果が出る
3. **伝説の武器（scripts/）は思考のフレームワーク** — 武器が戦い方を変える
4. **最大のレバレッジは装備テンプレート（Lv.5）** — 全職業マスターが転職イベントを発生させる
5. **検出力はベースモデル依存、表現力はスキル依存** — 勇者の素質と装備、両輪で考える
6. **勇者の名声（description）の最適化はマルチスキル環境で効く** — 冒険者ギルドで指名されやすくなる
7. **セルフバフ（自己評価ループ）は品質保証の仕組み** — 検出力ではなく信頼性の向上

---

## Skill vs Instructions — なぜSkillのほうが良いのか

今回の検証で「SKILL.md（スキル）」を使ったわけですが、GitHub Copilotには他にも指示を与える方法があります。代表格が **Instructions（`.instructions.md` / `copilot-instructions.md`）**。

「どっちでも同じでしょ？」と思ったあなた。**RPGで言えば、Instructionsは村の看板、Skillは勇者の装備**。似て非なるものです。

### 比較表

| 比較項目 | Instructions（`.instructions.md` / `copilot-instructions.md`） | Skill（`SKILL.md`） |
| --- | --- | --- |
| **読み込みタイミング** | 常時読み込み（全セッションで消費） | オンデマンド（必要なときだけ） |
| **コンテキスト消費** | 常にコンテキストを消費する | 使うときだけ消費。Progressive Loading対応 |
| **外部ファイル参照** | 直接参照できない | `references/`, `scripts/`, `assets/` を構造的に参照可能 |
| **スクリプト実行** | できない | `scripts/` に分析スクリプトを配置して実行可能 |
| **チーム共有** | 全員に常時適用（粒度が粗い） | `/code-review` のように必要時に呼び出し（粒度が細かい） |
| **再利用性** | プロジェクト固有 | フォルダごとコピーして他プロジェクトに持ち込める |
| **呼び出し方** | 自動（`applyTo` パターン） | `/` コマンド or エージェント経由で明示的に |

### つまりどういうこと？

* **Instructionsは「村の看板」** — 常に効かせたいルールに向いている（例: コーディング規約、PRの書き方）
* **Skillsは「勇者の装備」** — 特定タスクの専門知識に向いている（例: コードレビュー、テスト生成、デプロイ手順）

今回の検証で最大のブレイクスルーを生んだのは **`references/` + `scripts/` + `assets/` の三種の神器**。これがSkillの真価です。Instructionsではこの構造を持てません。

さらに、エージェント（`.agent.md`）と組み合わせると：

* **誰が**（エージェント） → `bug-hunter.agent.md`
* **何を知っていて**（スキル） → `/code-review` のSKILL.md + references/ + scripts/ + assets/
* **どう動くか**（エージェントの指示文）

この3つを**分離して管理**できる。RPGで言えば「勇者の人格（エージェント）」と「装備（スキル）」と「戦い方（指示）」が独立している。装備だけ差し替えれば同じ勇者がセキュリティレビューにもパフォーマンスチューニングにも対応できる。保守性が段違い。

> **結論**: 常時効かせるルールは Instructions、特定タスクの専門知識は Skill。両方使い分けるのが最強パーティ編成。

---

## 再現手順 — あなたも勇者を育ててみよう

この検証を自分でも試してみたい方へ。下記が Github のリポジトリです。

### 1. 冒険パーティを編成（ディレクトリ構成）

```
.github/
├── agents/
│   └── bug-hunter.agent.md   ← 🗡️ 勇者本人
└── skills/
    └── code-review/             ← ⚔️ 装備一式
        ├── SKILL.md             ← 📋 ジョブシステム
        ├── references/
        │   └── security-checklist.md   ← 📖 魔法書
        ├── scripts/
        │   └── analyze.py              ← 🔨 伝説の武器
        └── assets/
            └── review-template.md      ← 🛡️ 装備テンプレート
```

### 2. エージェントを作成

```
# .github/agents/bug-hunter.agent.md
---
description: "コードレビューを行うエージェント。Use when: コードの問題点を指摘してほしい、PRレビュー、セキュリティチェック"
name: "Code Reviewer"
tools: [read, search, execute]
---
あなたはコードレビューの専門家です。
渡されたコードに対して、`/code-review` スキルの手順に従ってレビューしてください。
```

### 3. レベルアップの順番

* **Lv.0**: 何も置かずにレビュー依頼（`/bug-hunter` だけ）
* **Lv.1**: SKILL.mdに名前と概要だけ記載
* **Lv.2**: 手順セクション（ジョブシステム）を追加
* **Lv.3**: references/に魔法書（チェックリスト）を配置
* **Lv.4**: scripts/に伝説の武器（analyze.py）を配置
* **Lv.5**: assets/に装備テンプレート（出力フォーマット）を配置 ← **ここが転職イベント**
* **Lv.6**: description（勇者の名声）を詳細化
* **Lv.7**: セルフバフ（自己評価セクション）を追加

### 4. 毎回同じ呪文で検証

```
/bug-hunter このコードをレビューしてください
```

**呪文は一切変えません。** 変えるのは勇者の装備だけ。

---

## おわりに — 勇者は「育てるもの」だった

Agentは「素質のある村人」です。ポテンシャルはあるけど、**何も装備させなければスライムにも苦戦する**。

でも、スキルを段階的に鍛えていけば——ジョブシステムを整え、魔法書を渡し、伝説の武器を鍛え、装備テンプレートを与え、セルフバフの習慣をつけさせれば——**ラスボスを倒して凱旋する伝説の勇者**になる。

大事なのは、\*\*プロンプトエンジニアリングよりも「装備のエンジニアリング」\*\*だということ。

一発の魔法の呪文を探すより、**勇者の装備を鍛える方がはるかに再現性が高い**。

そしてもう一つ。**エージェント（`.agent.md`）とスキルを分離する**ことで、「誰が」「何を知っていて」「どう動くか」を独立管理できる。これが2026年のAI開発の最適パーティ編成。

……ちなみにこの記事自体を `/bug-hunter` にレビューさせたら、「おわりにセクションが長いです。🟢 可読性」って返ってきました。

**育ちすぎ。ラスボスどころか、もう魔王城の経営に転職しかけてる。**

---

*この記事で使用したテストコード・エージェント定義・SKILL.mdテンプレートはGitHub リポジトリで公開しています。*
