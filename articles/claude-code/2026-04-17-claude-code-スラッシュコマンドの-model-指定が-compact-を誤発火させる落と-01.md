---
id: "2026-04-17-claude-code-スラッシュコマンドの-model-指定が-compact-を誤発火させる落と-01"
title: "Claude Code: スラッシュコマンドの `model` 指定が /compact を誤発火させる落とし穴"
url: "https://zenn.dev/genda_jp/articles/9228f64c472e98"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

AIでの並列開発用に、「マージ済み worktree を削除してデフォルトブランチを最新に同期するだけ」の小さなスラッシュコマンドを用意していました。処理自体は数秒で終わる `bash` なので、軽量モデルで十分だろうとフロントマターに `model: haiku` を書いていました。

ところが、長時間動かしている Opus 4.7 (1M) セッションからこのコマンドを呼ぶと、**毎回のように `/compact` プロンプトが出る**という現象に遭遇しました。Opus 基準ではコンテキストはまだ十分余っているはずです。

原因はフロントマターの `model: haiku` その 1 行でした。この問題は Claude Code 2.1.76 で関連修正が入っていますが、Sonnet は別の形の問題（429 エラー）に置き換わり、Haiku は元のまま context-limit の罠が残っているのが実情です。本記事では挙動の根拠を公式ドキュメントから辿りつつ、**モデル別に残る非対称な挙動**を整理します。

---

## 現象

状況はシンプルです。

* セッションはずっと Opus 4.7 (1M) で動かしており、会話履歴は ~160k トークン程度
* 数秒の `bash` 処理を実行するだけの小さなスラッシュコマンドを呼ぶ
* 毎回コンテキストが溢れ、 `/compact` を促すような表示が出る

Opus の 1M ウィンドウ基準では 16% しか使っていないはずで、どう見てもおかしな挙動です。

---

## 原因：`model: haiku` の 1 行

該当コマンドのフロントマターはこのようになっていました（抜粋）。

```
---
description: Clean up merged worktrees
model: haiku
---
```

「軽い定型処理だから Haiku で十分」の意図で入れていた `model: haiku` の 1 行が、Opus セッションで呼んだときに逆に `/compact` を誘発していました。

---

## 公式ドキュメントに基づく問題発生の理由

公式ドキュメントを辿ると、この挙動は仕様の組み合わせで説明がつきます。

### 1. スラッシュコマンドの `model` はターンの間だけモデルを上書きする

[Skills ドキュメント](https://code.claude.com/docs/en/skills) の Frontmatter reference より。

> `model` | Model to use when this skill is active.

"when this skill is active" とあるように、フロントマターの `model` は**そのコマンドが実行されている間だけ**セッションのアクティブモデルを上書きします。省略すればセッションのモデルをそのまま継承します。

### 2. 自動コンパクションはアクティブモデルのウィンドウ基準

[How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works#when-context-fills-up) より。

> Claude Code manages context automatically as you approach the limit. It clears older tool outputs first, then summarizes the conversation if needed.

ここでの "the limit" は固定値ではなく、**現在アクティブなモデルのコンテキストウィンドウ**に対する相対値です。Opus 4.7 と Haiku 4.5 ではウィンドウに 5 倍の差があります。

### 3. 組み合わさると何が起きるか

| アクティブモデル | ウィンドウ | 160k 履歴時の占有率 | コンパクション判定 |
| --- | --- | --- | --- |
| Opus 4.7 (1M) | 1,000k | 16% | 発火せず |
| Haiku 4.5 (200k) | 200k | 80% | **発火条件達成** |

コマンド呼び出しの瞬間に基準ウィンドウが 5 倍縮むため、履歴がそれなりに育ったセッションではほぼ確実にコンパクトの発火条件を満たしてしまいます。

---

## 公式による問題への対応と残る非対称性

この問題は Claude Code チーム側でも認識されており、**2.1.76 の変更ログ**で関連修正が入っています。

> Fixed spurious 'Context limit reached' when invoking a skill with `model:` frontmatter on a 1M-context session.

修正の実装は「スキル側の `model` が 1M 変種を持つモデルなら、自動で `[1m]` 付きに昇格させる」というもの。[Issue #34296](https://github.com/anthropics/claude-code/issues/34296) に該当箇所の逆コンパイル結果が載っています。

```
function Pl6(A, q) {
  if (Cf(A) || !Cf(q)) return A;      // skip if already [1m] OR session not [1m]
  if (gr8(H5(A))) return A + "[1m]";  // promote only if model supports 1m
  return A;
}
```

ポイントは `gr8(H5(A))` の条件、つまり「**1M 変種を持つモデルだけが昇格対象**」という点です。[Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) によると、Sonnet 4.6 は `sonnet[1m]` の 1M 変種を持つ一方、Haiku 4.5 は 200k 固定で 1M 変種が存在しません。したがって Sonnet は昇格され、Haiku は昇格されません。

ただしこの修正は「完全な解消」ではなく、**モデルごとに別々の形で症状が残る**というのが実情です。v2.1.107 時点でコミュニティが確認している挙動が [Issue #42082](https://github.com/anthropics/claude-code/issues/42082) にまとまっています。

> * `model: haiku` → client-side "Context limit reached" (Haiku's 200K cap hits before the API is called when parent session is large)
> * `model: sonnet` → 429 "Extra usage required for 1M context" (promoted to `sonnet[1m]` per #34296)

整理するとこうなります。

| フロントマター | v2.1.76 以降の挙動 |
| --- | --- |
| `model: haiku` | 200k 窓が親セッション履歴を覆えず context-limit 到達 |
| `model: sonnet` | `sonnet[1m]` に自動昇格されるが、1M entitlement が無いと 429 |

`model: sonnet` は一見「自動で 1M に持ち上がって直った」ように見えますが、Max プランなどで 1M entitlement が有効になっていないと 429 に置き換わるだけです。`model: haiku` は昇格の対象外なので、長いセッションで呼ぶと従来通り context-limit にぶつかります。**どちらにせよ、軽量化の意図で `model:` を書くと Opus 1M セッション側を壊しやすい**というのが現状です。

---

## 修正

結局やることは 1 行削除です。

```
 ---
 description: Clean up merged worktrees
-model: haiku
 ---
```

`model` を省略すればコマンドはセッションのアクティブモデルをそのまま継承するので、Opus 1M の余裕の中で動き、コンパクションは誤発火しなくなります。

---

## まとめ

* スラッシュコマンドの `model` はターン単位でセッションのアクティブモデルを上書きし、自動コンパクションが見る基準ウィンドウも連動して縮む
* Claude Code 2.1.76 で Sonnet は `sonnet[1m]` への自動昇格が入ったが、entitlement が無い環境では 429 に置き換わる。Haiku は昇格対象外のため context-limit の罠が継続する
* **Opus 1M セッションで `model:` をフロントマターに書くと、モデルに応じて何らかの形で壊れる**のが現状。軽量化の意図があるならスラッシュコマンドではなく、独立コンテキストで動くサブエージェントに任せるのが筋

## 参考
