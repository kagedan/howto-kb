---
id: "2026-05-06-あなたの-mcp-server実は-glama-listing-で3週間止まる-5つの罠と解決策-01"
title: "あなたの MCP server、実は Glama listing で3週間止まる (5つの罠と解決策)"
url: "https://zenn.dev/kanseilink/articles/linksee-memory-mcp-publish-glama-traps-20260506"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "GPT", "Python", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

2026年4月17日に Linksee Memory を npm publish した。同日に Glama listing 申請 + [awesome-mcp-servers PR #4999](https://github.com/punkpeye/awesome-mcp-servers/pull/4999) も出した。

3週間後の今 (5/6)、awesome-mcp-servers PR は **まだ merge されていない**。Glama Score は **A · A · B** で止まっている。

何が悪かったか?

公式 docs に書かれていない罠が5つあった。しかもどれも、**新規に MCP server を publish する全員が踏む構造的な問題** だった。

この記事は、その5つの罠と解決策を data 込みで残す。次に MCP server を出す人が、私と同じ3週間を溶かさないために。

## Linksee Memory って何?

知らない人向けに簡潔に。

Linksee Memory は Claude Code / Cursor / ChatGPT の **session 跨ぎ記憶喪失** を解決する local-first MCP server だ。6-layer 構造化メモリ (goal / context / emotion / implementation / caveat / learning) と、file diff cache による 50%+ の token 節約を提供する。

## 罠1: Glama は repo の Dockerfile を **使わない**

### 何が起きたか

Glama に repo を submit すると build test が走る。私の Dockerfile は丁寧に書いた `node:20-slim` ベースのマルチステージ build だった。なのに失敗。

ログを開いて愕然とした。Glama 側が動かしていた build は私の Dockerfile と **何の関係もなかった**。

### 真実

Glama は repo の Dockerfile を完全に無視する。代わりに自前の build spec で動かす。

```
{
  "baseImage": "debian:trixie-slim",
  "buildSteps": ["pnpm install", "pnpm run build"],
  "nodeVersion": "24"
}
```

しかもこの build spec は **時期によって変わる**。4月時点では `npm + Node 20` だったのが、5月には `pnpm + Node 24` になっていた。私が書いた Dockerfile への投資はゼロ評価された。

### 解

* Dockerfile は飾り。`package.json` の scripts と dependencies が完備されているかだけが効く
* README で「Dockerfile を見て」と書いても、Glama 経由のユーザーには届かない
* 自分の手元で `node:24-bookworm` の Docker container 内で `pnpm install && pnpm run build` を試すのが現実的な動作確認

## 罠2: better-sqlite3 v11 は Node 24 で死ぬ

### 何が起きたか

build は通る。でも server を起動した瞬間に落ちる。

```
Error: Could not locate the bindings file. Tried:
 → /app/node_modules/.pnpm/better-sqlite3@11.x/.../better_sqlite3.node
 ...(13 個の path を試して全滅)
```

### 真実

better-sqlite3 v11.x の prebuild は **Node 22 (NODE\_MODULE\_VERSION 127) まで**しか同梱されていない。Node 24 (137) には binding が存在しない。

local 環境では node-pre-gyp が動的に native compile してくれるが、Glama の build container には gcc と Python の dev tools が揃っていない。compile 失敗 → binding なし → server 即死。

### 解

`package.json` で v12+ にバンプする。

```
{
  "dependencies": {
    "better-sqlite3": "^12.9.0"
  }
}
```

v12 から Node 24 (NODE\_MODULE\_VERSION 137) prebuild が同梱されている。Native dep を持つ MCP server は、**最新 Node の prebuild が出ているかを依存ライブラリ毎に常時確認する**運用が必要だ。

## 罠3: pnpm 10 はデフォルトで postinstall scripts を切ってる

### 何が起きたか

better-sqlite3 を v12 にした。再 build。また同じ "Could not locate the bindings file" で落ちる。

私は最初、binding が破損しているのかと疑った。npm install を全部やり直しても変わらない。

### 真実

ログを精読すると、build の途中に小さく warning が出ていた。

```
╭ Warning ──────────────────────────────────────────────────╮
│ Ignored build scripts: better-sqlite3, esbuild.           │
│ Run "pnpm approve-builds" to pick which dependencies      │
│ should be allowed to run scripts.                         │
╰───────────────────────────────────────────────────────────╯
```

**pnpm 10 はセキュリティ強化として、すべてのパッケージの postinstall scripts をデフォルトで OFF にしている**。better-sqlite3 の native binding は postinstall (`node-pre-gyp install`) で取得される。silently skip → binding が存在しないまま install 完了 → server 起動時に発覚。

これは MCP server 文脈ではほぼ議論されていない。GitHub Issues / Stack Overflow にも該当議論が少ない。

### 解

`package.json` で明示的に許可する。

```
{
  "pnpm": {
    "onlyBuiltDependencies": ["better-sqlite3"]
  }
}
```

Glama / Smithery のような pnpm-default registry を使う場合、native dep を持つ全てのパッケージで **必須**。

## 罠4: 想定外の transitive XSS (`ip-address`)

### 何が起きたか

罠1〜3を全部解いた。Glama build pass。release 0.2.1 自動生成。やっと終わったと思って Score を見たら、**Maintenance が C 評価**だった。

### 真実

`npm audit` を回したら出てきた。

```
ip-address  <=10.1.0
Severity: moderate
ip-address has XSS in Address6 HTML-emitting methods
GHSA-v2v4-37r5-5v8g

  express-rate-limit  >=8.0.1
  Depends on vulnerable versions of ip-address
    @modelcontextprotocol/sdk  >=1.26.0
    Depends on vulnerable versions of express-rate-limit
```

**MCP SDK 1.29.0 (latest) が express-rate-limit 経由で 脆弱版 ip-address を pull していた**。`npm audit fix` では治らない。peer dep 制約で SDK を downgrade できない。

### 解

`package.json` で transitive dep を強制 override する。

```
{
  "overrides": {
    "ip-address": "^10.2.0"
  },
  "pnpm": {
    "overrides": {
      "ip-address": "^10.2.0"
    }
  }
}
```

両方書く必要があるのは、MCP SDK の register が npm / pnpm 両方で動くことを担保するため。確認:

```
$ pnpm audit
No known vulnerabilities found
```

これは `@modelcontextprotocol/sdk` 上流が express-rate-limit を bump するまで続く回避策だ。

## 罠5: Glama Maintenance Score の "6ヶ月" 縛り

### 何が起きたか

罠1〜4を全部解いた。再評価を待った。**Maintenance は B のまま**だった。

### 真実

Score 内訳を expand したら、これだった。

```
✓ Last stable release on 2026-04-20
✓ No critical vulnerability alerts
✓ No high-severity vulnerability alerts
✓ No code scanning findings
✓ CI is passing
○ No issues in the last 6 months
○ No commit activity data available
```

5項目 ✓ / 2項目 ○ で B 評価。残り2つの ○ を解読すると:

* **No issues in the last 6 months** → repo が3週間しか存在しない。6ヶ月の history を持っていない
* **No commit activity data available** → GitHub の `/repos/{}/stats/commit_activity` API は新 repo に対して async populate に時間がかかり、しばらく空 array を返す

つまり **新規 repo は構造的に Maintenance A になれない**。アルゴリズムが repo age を考慮していない。

### 解

3つの選択肢がある。

1. **6ヶ月待つ** — repo が熟成すれば自動的に解消する
2. **CI 追加** — `CI is passing` ✓ を確実に取る (これは即効性あり、私もやった)
3. **maintainer に直接交渉** — punkpeye (awesome-mcp-servers maintainer) に「A/A/B でも入れてくれませんか」と PR 上で聞く

私は今 (3) を試している。返答待ち。

## 5つの罠を1分で確認

公開予定の MCP server を持っているなら、以下を確認する。

1. **Dockerfile に頼らない** → `package.json` で完結する
2. **better-sqlite3 v12+** → Node 24 prebuild 必須
3. **`pnpm.onlyBuiltDependencies`** で native dep の postinstall 許可
4. **`overrides` で `ip-address` を ^10.2.0** に強制 (SDK 上流 fix まで)
5. **Maintenance B を覚悟** → 6ヶ月後に A、それまでは交渉 or 待機

## Linksee Memory を試す

```
npm install -g linksee-memory
```

Claude Code に登録:

```
// .claude/settings.json
{
  "mcpServers": {
    "linksee-memory": {
      "command": "npx",
      "args": ["linksee-memory"]
    }
  }
}
```

repo: <https://github.com/michielinksee/linksee-memory>

GitHub star をもらえると Maintenance Score が上がるので嬉しいです 🙏  
(現在 3 stars / 1,903 DL — DL の割に star 比率が低い構造的問題があり、それも別記事で書く予定です)

## 次に書く予定

このシリーズの続編候補:

* **Mem0 / Letta / Zep / Linksee Memory どれを選ぶか** (memory MCP の比較記事)
* **Claude Code の "本当の" memory leak — Linksee Memory で気づいた話**
* **Glama Score を A/A/A まで持っていく方法 (6ヶ月後の続報)**

---

書き手: [Michie Yamaguchi](https://x.com/ELLECraftsinga1) (Synapse Arrows PTE. LTD. / Singapore)  
シンガポールで一人 indie OSS 開発をしています。Synapse Arrows の他のプロダクトは [synapsearrows.com](https://synapsearrows.com) にあります。
