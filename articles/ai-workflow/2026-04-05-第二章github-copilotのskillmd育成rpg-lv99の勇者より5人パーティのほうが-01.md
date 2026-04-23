---
id: "2026-04-05-第二章github-copilotのskillmd育成rpg-lv99の勇者より5人パーティのほうが-01"
title: "【第二章】GitHub Copilotの『SKILL.md育成RPG』— Lv.99の勇者より5人パーティのほうが強いのか検証してみた"
url: "https://qiita.com/yukurash/items/e4488807c171b283fca0"
source: "qiita"
category: "ai-workflow"
tags: ["AI-agent", "qiita"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## 本記事について

前回の記事の続編となります。

引き続き、AI Agent の Skill の必要性や重要性を学ぶため検証した内容になります。  
検証した内容を AI が RPG 風にまとめてくれたので温かい目でお楽しみください。

## TL;DR

* 以前は勇者1人で挑んだが、今回は SKILL.md で5人の職業の仲間を作り、以前と同様に同じバグ入りコードに挑ませた。

| 職業 | やったこと |
| --- | --- |
| ⚔️ 戦士 | コードレビュー（バグを正面から斬る） |
| 🛡️ 僧侶 | テスト生成（防御結界を張る） |
| 📜 吟遊詩人 | ドキュメント生成（コードの物語を紡ぐ） |
| ⚗️ 錬金術師 | リファクタリング（コードを練り直す） |
| 🔮 賢者 | セキュリティ監査（闇の脆弱性を見抜く） |

* 1スキル育成型か複数スキル型のどちらが適切かを最後に比較した。
* 本記事で紹介する AI Agents チームは下記の GitHub リポジトリに公開。

## はじめに

[前回の記事](https://qiita.com/yukurash/items/d8971bdf08f8416ad7dd) では、1つのSKILL.mdを育て上げる「職人育成型」のアプローチを紹介した。

いわばRPGでいう「ソロプレイでレベル99まで鍛え上げた戦士」だ。

今回はガラッと方針を変える。

**5つの異なるSKILL.mdを作って、パーティを組む。**

戦士、僧侶、吟遊詩人、錬金術師、賢者。それぞれに専門の武器（参照ファイル）を持たせ、同じダンジョン（バグ入りコード）に挑ませる。

「どの職業が何を得意とするのか？」  
「最強パーティ編成は？」  
「そもそもパーティを組む意味はあるのか？」

全部検証した。

## 冒険パーティの編成 — エージェント＋5つのスキル

今回の構成はこう。パーティリーダー（エージェント）が、5つの職業（スキル）を使い分ける。

```
.github/
├── agents/
│   └── party-leader.agent.md     ← 🗡️ パーティリーダー
└── skills/
    ├── code-review/              ← ⚔️ 戦士
    ├── test-gen/                 ← 🛡️ 僧侶
    ├── doc-gen/                  ← 📜 吟遊詩人
    ├── refactor/                 ← ⚗️ 錬金術師
    └── security-audit/           ← 🔮 賢者
```

RPG的に言うと：

* **エージェント（`party-leader.agent.md`）** ＝ パーティリーダー。どの職業を呼び出すか判断する司令塔
* **スキル（`code-review/` 等）** ＝ 各職業の装備・技・知識。職業ごとに専門の武器（references/、scripts/、assets/）を持つ
* **チャットで `/party-leader`** に話しかける ＝ リーダーに「ダンジョン攻略しろ」と命じる

エージェントの中身はこんな感じ：

```
---
description: "コードの品質を多角的に分析するパーティリーダー。Use when: コードを総合的にチェックしたい、全方位の品質分析がほしい"
name: "Party Leader"
tools: [read, search, execute]
---
あなたはコード品質分析のパーティリーダーです。
渡されたコードに対して、利用可能なスキルを活用して分析してください。
```

使い方はシンプル。チャットで `/party-leader このコードをレビューして` と頼むだけ。リーダーが状況に応じて適切なスキルを参照して分析を実行する。

今回の検証では、各職業の実力を比較するため**1職業ずつソロで挑ませた**。最後にパーティ全員で挑むとどうなるかも検証している。

---

## ダンジョン紹介 — バグ10個が潜むExpressサーバー

前回と同じ、Express + PostgreSQL のユーザー管理API。約155行のTypeScriptコードの中にバグが10個仕込んである。

> ⚠️ 実際の検証では、コメントなしの素のコードをそのままCopilotに渡しています。バグのヒントは一切与えていません。

💀 ダンジョンマップ（テストコード全文）を開く

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

見た目は普通のユーザー管理API。でも中身はトラップだらけだ。

### 仕込んだ10個のバグ一覧

| # | カテゴリ | 概要 |
| --- | --- | --- |
| 1 | セキュリティ | SQLインジェクション（`/users/search`でテンプレートリテラル） |
| 2 | セキュリティ | XSS（`renderProfilePage()`でHTMLエスケープなし） |
| 3 | バグ | Off-by-oneエラー（`bulk-update-role`の `i <= userIds.length`） |
| 4 | バグ | null参照（`PATCH /users/:id/profile`で`user.profile`がnull） |
| 5 | パフォーマンス | N+1クエリ（`GET /users`でループ内クエリ） |
| 6 | パフォーマンス | 不要な再計算（`toLocaleDateString`のIntlロケール解決） |
| 7 | 可読性 | マジックナンバー（`role === 3`等） |
| 8 | 可読性 | 関数の責務過多（`POST /users`のexportエンドポイント等） |
| 9 | 型安全性 | any型乱用（`parsePagination`、`validateUserInput`等） |
| 10 | エラーハンドリング | catch握りつぶし（`POST /users`のtry-catch） |

> **カテゴリ分布**: セキュリティ 2 / バグ 2 / パフォーマンス 2 / 可読性 2 / 型安全性 1 / エラーハンドリング 1

SQLインジェクション、XSS、ロジックバグから可読性まで。本番にデプロイしたら1日で炎上するレベルの「初見殺しダンジョン」である。

## 検証ルール

| 項目 | 内容 |
| --- | --- |
| 対象コード | Express + PostgreSQL ユーザー管理API（約155行・TypeScript） |
| 仕込んだバグ | 10個（セキュリティ、ロジックバグ、パフォーマンス、可読性、型安全性、エラーハンドリング） |
| 検証方法 | 各職業のSKILL.mdを読み込んだ状態で同じプロンプトを投入 |
| 評価基準 | バグ検出数、出力の実用性、他職業との差分 |
| 使用モデル | Claude Opus 4.6 |

各職業には明確に異なるSKILL.mdと、専用の武器（参照ファイル・テンプレート）を装備させている。

## パーティ構成

```
.github/
├── agents/
│   └── party-leader.agent.md   ← パーティリーダー（指揮官）
└── skills/
    ├── code-review/   ← ⚔️ 戦士
    ├── test-gen/      ← 🛡️ 僧侶
    ├── doc-gen/       ← 📜 吟遊詩人
    ├── refactor/      ← ⚗️ 錬金術師
    └── security-audit/ ← 🔮 賢者
```

チャットで `/party-leader` に話しかけると、パーティリーダーが各スキルを順番に呼び出してくれる。個別に試したい場合は `/code-review`、`/test-gen` のように直接呼び出してもいい。

では、1人ずつダンジョンに送り込んでいこう。

---

## ⚔️ 戦士の攻略記録 — `/code-review`

> 「バグがいるなら、正面から斬る。それが戦士だ」

### 装備

| 項目 | 内容 |
| --- | --- |
| SKILL.md | コードレビュー特化 |
| 武器（references/） | バグパターン集（SQLi、XSS、ロジックバグ等） |
| 戦い方 | コードを上から下まで読み、パターンマッチで指摘 |

### 戦闘結果

戦士の出力は圧巻だった。

仕込んだ10個のバグを **すべて検出**。それだけでなく、こちらが意図していなかった問題も２件追加で指摘した。

* **認可チェックの欠落** — 全エンドポイントに認証・認可の仕組みがない
* **CSV出力のエスケープ未対策** — カンマや改行を含む値がそのまま出力される

合計 **12件の指摘**。

ここがポイントだが、追加の2件はバグリストの10個には含まれていない。仕込んだバグではなく、設計レベルの問題だ。つまり戦士は「答え合わせ」を超えて、こちらが想定していなかった穴まで見つけてきた。

出力フォーマットも実用的で、重要度付きサマリー表・修正コード例・行番号がすべて揃っていた。正面突破型の王道スタイル。

### スコアカード

| 指標 | スコア |
| --- | --- |
| バグ検出数 | 12件（仕込んだ10個を全検出 + 設計レベル2件） |
| 出力の実用性 | ⭐⭐⭐⭐⭐ |
| 修正コードの精度 | ⭐⭐⭐⭐ |
| 設計レベルの指摘 | ⭐⭐ |
| 再現性 | ⭐⭐⭐ |

### 気づき

戦士は「目の前の敵を倒す」のが得意。コードの1行1行を見て、既知のパターンと照合する。

設計レベルの指摘も２件出たが、あくまでコードを読む中で「ここにないもの」に気づいた形だ。体系的なセキュリティ監査としてはまだ賢者に軍配が上がる。

---

## 🛡️ 僧侶の攻略記録 — `/test-gen`

> 「バグは斬らない。結界で炙り出す」

### 装備

| 項目 | 内容 |
| --- | --- |
| SKILL.md | テスト生成特化 |
| 武器（references/） | テスト設計パターン（境界値分析、同値クラスなど） |
| 戦い方 | テストコードを生成し、テストが落ちることでバグを暴く |

### 戦闘結果

僧侶はバグを「指摘」しない。代わりに **約50のテストケース** を生成した。

正常系、異常系、境界値の3カテゴリに分類されたテストコード。そしてそのテストを走らせると、**8件が落ちた**。

テストが落ちる＝バグがある。

「ここにバグがあります」とは直接言わないが、テストの失敗メッセージを見れば原因は一目瞭然。しかも **再現性が最も高い**。「テストを実行すればいつでも同じ結果が出る」という安心感は、他の職業にはない強みだ。

### 検出できなかった2件

見落とされたのは **#6（不要な再計算）** と **#7（マジックナンバー）** だ。

* `#6` の `toLocaleDateString` によるIntlロケール解決の再計算は、テストを書いても「正しい結果が返る」ので落ちようがない。パフォーマンス問題はテストの守備範囲外
* `#7` の `role === 3` のようなマジックナンバーは、コードの動作自体は正しい。可読性の問題はテストでは検出できない

これは僧侶の弱点というより、テストという手法の限界だ。

### スコアカード

| 指標 | スコア |
| --- | --- |
| バグ検出数 | 8 / 10（テスト失敗経由で間接検出） |
| 出力の実用性 | ⭐⭐⭐⭐⭐ |
| 修正コードの精度 | —（修正は出さない。テストを出す） |
| 設計レベルの指摘 | ⭐ |
| 再現性 | ⭐⭐⭐⭐⭐ |

### 気づき

僧侶の強みは「証拠を残す」ことだ。

戦士が「ここにSQLインジェクションがある」と指摘するのに対し、僧侶は「`'; DROP TABLE users; --` を入力したらテストが落ちました。はい証拠」と突きつける。

PRレビューで「本当にバグなの？」と疑われたとき、僧侶のテストコードは最強の盾になる。

---

## 📜 吟遊詩人の攻略記録 — `/doc-gen`

> 「コードの真実は、言葉にしたとき初めて見える」

### 装備

| 項目 | 内容 |
| --- | --- |
| SKILL.md | ドキュメント生成特化 |
| 武器（assets/） | APIドキュメントテンプレート |
| 戦い方 | コードを読み解き、仕様書として文書化する |

### 戦闘結果

吟遊詩人は戦わない。歌う。

**8エンドポイント＋関数リファレンス** の完全なAPI仕様書を生成した。パラメータ表、レスポンス表、エラーコード一覧付き。テンプレートに準拠した構造化ドキュメント。

直接的なバグ指摘は少ない。しかし、ドキュメント化の過程で面白いことが起きた。

「`PATCH /users/:id/profile` の `user.profile` が null の場合の動作が仕様上不明」  
「`POST /users` が新規作成・メール送信・監査ログ・条件分岐を1エンドポイントでやっているが、これは意図的か？」  
「`/users/export` のCSV出力フィールドに特殊文字を含む値がある場合のエスケープ仕様が未定義」

これらは **「仕様の曖昧さ」** であり、バグとは微妙に違う。でも、実際のプロダクトでは仕様の曖昧さこそがバグの温床になる。

### スコアカード

| 指標 | スコア |
| --- | --- |
| バグ検出数 | 少ない（直接検出ではなく仕様の曖昧さとして指摘） |
| 出力の実用性 | ⭐⭐⭐⭐ |
| 修正コードの精度 | —（コードは出さない。ドキュメントを出す） |
| 設計レベルの指摘 | ⭐⭐⭐⭐⭐ |
| 再現性 | ⭐⭐ |

### 気づき

吟遊詩人は「バグを見つける職業」ではない。「仕様と実装のギャップを可視化する職業」だ。

他の4職業がコードの「正しさ」を検証するのに対し、吟遊詩人だけが「そもそもこのコードは何をしたいのか？」を問いかける。パーティに1人いると、議論の質がグッと上がる。

ソロで使う場面は少ないが、パーティの一員としては唯一無二の存在。

---

## ⚗️ 錬金術師の攻略記録 — `/refactor`

> 「このコード、もっといい形に練り直せる」

### 装備

| 項目 | 内容 |
| --- | --- |
| SKILL.md | リファクタリング特化 |
| 武器（scripts/） | 複雑度分析スクリプト |
| 武器（references/） | リファクタリングパターン集 |
| 戦い方 | コードの構造を分析し、より良い形に変換する |

### 戦闘結果

錬金術師は **7件のリファクタリング提案** を出した。

すべての提案に **Before/After形式のコード例** が付いていた。

1. パラメータ化クエリへの統一（`/users/search`のSQLi対策を含む）
2. HTMLエスケープ関数の導入（`renderProfilePage`のXSS対策）
3. ループ条件の修正＋`Promise.all`への置換（`bulk-update-role`）
4. Null安全なプロパティアクセス（`PATCH /users/:id/profile`）
5. N+1クエリの解消（JOINクエリへのリライト）
6. バリデーション層の分離と型安全化（`any`型の除去）
7. エラーハンドリングミドルウェアの導入

「SQLインジェクションがあります」ではなく「パラメータ化クエリに変換するとこうなります」という出力。これが錬金術師の流儀だ。

### スコアカード

| 指標 | スコア |
| --- | --- |
| バグ検出数 | 7件（リファクタリング提案経由） |
| 出力の実用性 | ⭐⭐⭐⭐⭐ |
| 修正コードの精度 | ⭐⭐⭐⭐⭐ |
| 設計レベルの指摘 | ⭐⭐⭐⭐ |
| 再現性 | ⭐⭐⭐ |

### 気づき

錬金術師は「見つける」より「直す」に全振りしている。

バグを指摘するだけなら戦士で十分。でも「じゃあどう直すの？」に対して最も実用的な答えを出すのは錬金術師だ。

Before/Afterのコード例はそのままPRに貼れるレベル。実務での時短効果は5職業中No.1かもしれない。

---

## 🔮 賢者の攻略記録 — `/security-audit`

> 「見えないものこそ、最も危険だ」

### 装備

| 項目 | 内容 |
| --- | --- |
| SKILL.md | セキュリティ監査特化 |
| 武器（references/） | OWASPチェックリスト |
| 戦い方 | OWASPベースで脆弱性を体系的に洗い出す |

### 戦闘結果

賢者の最終判定はこうだった。

> **❌ デプロイ不可**

辛辣。でも正しい。

| 重大度 | 件数 | 内容 |
| --- | --- | --- |
| Critical | 3 | SQLインジェクション、XSS、認証・認可の完全欠落 |
| High | 2 | Off-by-oneによるデータ整合性リスク、null参照によるサーバークラッシュ |
| Medium | 2 | レート制限なし（ブルートフォース可能）、catch握りつぶし（障害の検知不能） |

各指摘にはOWASP IDとCVSS風の重大度、そして **攻撃シナリオ** が記載されていた。

「`/users/search?q=' OR 1=1 --` で全ユーザー情報が漏洩。テンプレートリテラルによるクエリ構築がOWASP A03:2021 Injectionに該当……」

注目すべきは、賢者がバグリスト10個の中から重大なものを拾いつつ、リストにない問題も指摘している点だ。

* **認証・認可の完全欠落** — 全エンドポイントが誰でもアクセス可能
* **レート制限なし** — ブルートフォース攻撃やDoSに対して無防備

これらは「コードのバグ」ではなく「設計の欠陥」だ。コードを1行1行見ていても気づけない。

### スコアカード

| 指標 | スコア |
| --- | --- |
| バグ検出数 | 7件（Critical 3 + High 2 + Medium 2） |
| 出力の実用性 | ⭐⭐⭐⭐ |
| 修正コードの精度 | ⭐⭐⭐ |
| 設計レベルの指摘 | ⭐⭐⭐⭐⭐ |
| 再現性 | ⭐⭐⭐⭐ |

### 気づき

賢者は「他の全員が見逃すもの」を見つける。

コードレビュー（戦士）では「この行にバグがある」は分かる。でも「このAPIにはそもそも認証がない」「レート制限がない」は、コードに書かれていないものだから、書かれたコードを読むだけでは見つけられない。

「書かれていないコードのバグを見つける」——これが賢者の真骨頂だ。

---

## パーティ総合成績

5人の冒険者がすべてダンジョンを攻略した。結果を並べてみよう。

| 職業 | バグ検出 | 設計指摘 | 修正コード | 再現性 | 実用性 |
| --- | --- | --- | --- | --- | --- |
| ⚔️ 戦士 | 12件（10個全検出+2） | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 🛡️ 僧侶 | 8/10（テスト経由） | ⭐ | — | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 📜 吟遊詩人 | 少ない（仕様曖昧さ指摘） | ⭐⭐⭐⭐⭐ | — | ⭐⭐ | ⭐⭐⭐⭐ |
| ⚗️ 錬金術師 | 7件（改善提案経由） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 🔮 賢者 | 7件（C3/H2/M2） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### MVP: ⚔️ 戦士

単体での総合力は戦士が最強。仕込んだ10個を漏れなく検出し、さらに設計レベルの問題も2件見つけた。日常のコードレビューなら戦士1人で十分だ。

### 特別賞: 🔮 賢者

「他の全員が見逃したものを見つけた」という点で、パーティへの貢献度は賢者が最も高い。戦士が100点を取った後でも、「❌デプロイ不可」という判定で追加の気づきを叩き出せる。

---

## 最強パーティ編成 — 5人全員で挑んだらどうなるか

ここまでは1人ずつソロで攻略させた。では5人全員で同じダンジョンに挑んだら？

`/party-leader` で5つのスキルを束ね、順番に実行させた結果がこれだ。

### 攻略フロー

```
1. 🔮 賢者が偵察（セキュリティ監査で致命的な罠を発見）
2. ⚔️ 戦士が突入（全バグを検出・指摘）
3. 🛡️ 僧侶が結界（テストコードで証拠を固定）
4. ⚗️ 錬金術師が修復（Before/Afterで修正コードを生成）
5. 📜 吟遊詩人が記録（仕様書を整備して後続チームに引き継ぎ）
```

### パーティ攻略の成果

* 検出した問題: **15件以上**（バグ10件 + 設計レベルの指摘5件以上）
* 出力物: セキュリティ監査レポート、レビュー指摘一覧、テストコード約50件、リファクタリング済みコード、API仕様書
* 所要時間: 約10分（5スキル順次実行）

1人では不可能な **多角的な分析** が、パーティなら10分で完了する。

ただし注意点もある。5スキル分の出力を読んで統合するのは人間の仕事だ。出力量が多いぶん、「で、結局何をすればいいの？」を判断するコストは増える。

---

## 職業図鑑 — どのスキルをいつ使うか

「全部入り」が常にベストとは限らない。場面に応じた使い分けガイドをまとめた。

### 日常のPRレビュー

→ ⚔️ 戦士（`/code-review`）

迷ったらこれ。バグ検出数が最多で、出力も即座に使える。毎日のPRレビューで毎回5スキル回す必要はない。

### テストを書くのがダルい

→ 🛡️ 僧侶（`/test-gen`）

「テスト書いて」と言えば50件出てくる。正常系・異常系・境界値のカテゴリ分けまでやってくれる。既存コードにテストを追加したいときに最適。

### 新メンバーのオンボーディング

→ 📜 吟遊詩人（`/doc-gen`）

「このAPI何してるの？」に対する答えを自動生成。パラメータ表とレスポンス表付きのドキュメントは、READMEの代わりになる。

### 技術的負債の返済

→ ⚗️ 錬金術師（`/refactor`）

「このコード汚いけどどこから手をつければ……」への最適解。影響行数付きのBefore/Afterがあるから、リファクタリングPRがすぐ作れる。

### リリース前のセキュリティチェック

→ 🔮 賢者（`/security-audit`）

本番デプロイの前に必ず通すべきゲート。「デプロイ可/不可」の判定は、チームの意思決定を加速する。

### ボス戦（大規模リリース・監査対応）

→ 🎉 5人全員（`/party-leader`）

四半期リリース、セキュリティ監査対応、レガシーシステムの刷新。ここぞという場面ではフルパーティで挑め。

---

## おまけ: A案 vs B案 — スキル設計のベストプラクティス

前回記事（A案）は「1つのスキルを深く育てる」アプローチだった。今回のB案は「5つの専門スキルを揃える」。

どっちが正解か？　両方だ。

| 比較項目 | A案（1スキル育成型） | B案（複数スキル型） |
| --- | --- | --- |
| コンセプト | 1つのスキルを深く鍛える | 複数の専門スキルを揃える |
| RPGメタファー | 職人を育てる | パーティを編成する |
| 向いている場面 | チームで統一したレビュー基準がほしい | 多角的な分析がほしい |
| メンテナンスコスト | 低（1ファイルを改善し続ける） | 中〜高（複数スキルを管理） |
| 出力の一貫性 | 高（毎回同じフォーマット） | 低（職業ごとに出力形式が異なる） |
| 検出範囲 | 深い（1つの観点を徹底） | 広い（複数の観点を横断） |
| おすすめ | 日常のPRレビュー、CI/CDに組み込む | リリース前の総合チェック、セキュリティ監査 |

結論。

**普段使い＝A案（育成型の戦士1人）、ここぞ＝B案（5人パーティ）。**

RPGでも同じだ。日常のレベル上げはソロ狩りが効率的。でもボス戦ではパーティを組む。それと同じこと。

両方持っておくのが最強の選択肢だ。

---

## 再現手順 — あなたもパーティを組んでみよう

自分のプロジェクトで試したい方向け。下記で公開しています。

### 1. ディレクトリ構造を作る

```
.github/
├── agents/
│   └── party-leader.agent.md   ← パーティリーダー
└── skills/
    ├── code-review/             ← ⚔️ 戦士
    │   ├── SKILL.md
    │   └── references/
    ├── test-gen/                ← 🛡️ 僧侶
    │   ├── SKILL.md
    │   └── references/
    ├── doc-gen/                 ← 📜 吟遊詩人
    │   ├── SKILL.md
    │   └── assets/
    ├── refactor/                ← ⚗️ 錬金術師
    │   ├── SKILL.md
    │   ├── references/
    │   └── scripts/
    └── security-audit/          ← 🔮 賢者
        ├── SKILL.md
        └── references/
```

### 2. 各SKILL.mdを作成

各スキルフォルダに `SKILL.md` を配置する。ポイントは以下の3つ。

1. **役割を1行で定義する** — 「このスキルは○○するためのものです」
2. **参照ファイルを指定する** — `references/` や `assets/` に置いたファイルをSKILL.mdから参照
3. **出力フォーマットを指定する** — テーブル形式、Before/After形式など

### 3. パーティリーダーを作成

`.github/agents/party-leader.agent.md` で5つのスキルを束ねる。実行順序と各スキルへの指示を記述。

### 4. ダンジョンに挑む

VS Code で対象コードを開き、Copilot Chatで `/party-leader` を呼び出す。

```
/party-leader このコードを全職業で分析してください
```

パーティリーダーが賢者→戦士→僧侶→錬金術師→吟遊詩人の順でスキルを自動実行する。

個別に試したい場合は直接呼び出してもOK。

```
/code-review このコードをレビューしてください
/test-gen このコードのテストを生成してください
/doc-gen このコードのAPIドキュメントを生成してください
/refactor このコードのリファクタリング提案をしてください
/security-audit このコードのセキュリティ監査をしてください
```

---

## おわりに

SKILL.mdの真の力は「1つのスキルを磨くこと」だけじゃない。**複数のスキルを組み合わせてパーティを組むこと** で、1人では見えなかった問題が見えるようになる。

今回の検証で分かったこと。

* 戦士は全バグを斬る。しかも仕込んでないバグまで2件見つけてくる
* 僧侶はテストで証拠を固める。ただしマジックナンバーや再計算コストはテストでは捕まえられない
* 吟遊詩人は仕様の曖昧さを炙り出す。バグは直せないが、議論の起点を作れる
* 錬金術師はBefore/Afterで最も実用的に直す。PRに直接貼れるレベル
* 賢者は「❌デプロイ不可」で全員が見逃す設計の穴を暴く

完璧な職業は存在しない。だからパーティを組む。

あなたのプロジェクトにも、まずは戦士を1人。そしてリリース前には `/party-leader` でフルパーティを。

**冒険はここから始まる。**
