---
id: "2026-06-19-claude-code-codex-obsidian-で半自動ai会議を回す構成-役割分担記憶分離ガ-01"
title: "Claude Code × Codex × Obsidian で「半自動AI会議」を回す構成 — 役割分担・記憶分離・ガードレールまで実装ベースで解説します"
url: "https://qiita.com/TaichiEndoh/items/8286c763c7b58c0d8ad7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "AI-agent", "qiita"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

複数AIエージェント（Claude Code と Codex）を、Obsidian を共有メモリにして連携させる開発体制を実運用しています。

「2体のAIを役割分担させ、議論と決定を Markdown に蓄積し、本番反映だけ人間が承認する」——その**具体的な構成・ファイル・コマンド・ガードレール**を、エンジニア向けに再現可能な粒度でまとめます。

医療と IT のあいだで動きながら発信しています。

---

## 1. 全体構成

```
            ┌─────────────── 人間（最終決定）───────────────┐
            │ 議題を出す / レビュー / 「GO」で本番反映を承認        │
            └───────────────┬───────────────────────────────┘
                            │
        ┌───────────────────┴────────────────────┐
        │                                         │
   Claude Code (Builder)                     Codex (Reviewer + 量産実行)
   - 設計 / 実装 / 文章                       - レビュー / 別案 / 画像生成
   - まとめ / マージゲート                     - drafts への下書き
        │                                         │
        └──────────────┬──────────────────────────┘
                       │ 読み書き（ファイル経由・自動同期なし）
              ┌────────┴─────────┐
              │  Obsidian = docs/ai-collab/  │
              │  議論 / 決定 / レビューの長期記憶 │
              └──────────────────────────────┘
```

ポイントは **AI 同士が直接通信しない**こと。やり取りは **Git 管理された Markdown ファイル**を介し、人間がゲートを握ります。

---

## 2. 役割分担

| 主体 | 役割 | やらないこと |
|---|---|---|
| **Claude Code** | Builder。設計・実装・文章・とりまとめ・**マージゲート（本番反映の一本化）** | — |
| **Codex** | Reviewer ＋ 範囲限定の量産実行。レビュー・別案・**画像生成**・下書き | push / merge / 共有層変更（しない） |
| **Obsidian** | 共有メモリ。議論・決定・レビューを蓄積 | （ただの Markdown 置き場） |
| **人間** | 議題出し・最終決定・本番反映の承認 | — |

> 設計判断: **マージ・push・共有層変更・本番反映は Claude Code（と人間）に一本化**。Codex は「速さ」と「別視点」に専念させ、反映ゲートを通さないと本番に出ない構造にして事故を防ぐ。

---

## 3. 記憶チャンネルの分離

メモの置き場を**役割で分ける**のが肝。混ぜると「どこに書いたか」が崩壊します。

| チャンネル | 用途 | 期間 | Git |
|---|---|---|---|
| `docs/ai-collab/` | AI会議の議論・決定・レビュー | 長期 | ✅ tracked |
| `PORTFOLIO_STATUS.md` | worktree 間の連絡板 | 即時 | git 外 |
| `.agent-memo.md` | 各 worktree の短期 WIP | 短期 | gitignored |
| Notion | 人間向け進捗報告 | 定期 | クラウド |

> `docs/ai-collab/` には **AI会議の記録だけ**を書く。worktree の一時状態は書かない、と決めておくと長期記憶がきれいに育つ。

---

## 4. ディレクトリ構成（Obsidian Vault）

`docs/` 全体を Obsidian Vault として開き、AI が読む正本は `docs/ai-collab/` に限定します。

```
docs/ai-collab/
├── README.md                       # ホーム（読む順 + wikilink）
└── 02_ai-collab/
    ├── PROJECT_CONTEXT.md           # 目的・制約・スタック（めったに変わらない土台）
    ├── AI_ROLES.md                  # 役割定義（性格モデル + 使い分け早見表）
    ├── DECISION_LOG.md              # 決定の履歴（追記のみ・過去を消さない）
    ├── DEBATE_PROTOCOL.md           # 会議の進め方（最大3ラウンド）
    ├── SEMI_AUTO_DEBATE.md          # 半自動化の仕様（後述）
    ├── debates/                     # 1論点1ファイルの議論ログ
    │   └── YYYY-MM-DD-topic.md
    └── drafts/                      # Codex の下書き置き場（本体に直書きしない）
```

> AI が毎回読むのは `docs/ai-collab/` のみ。`docs/` 全体は人間の検索用知識庫（古い docs に個人情報が残るため AI に一括取り込みさせない）。

---

## 5. 半自動会議ループ

```
①人間が議題を出す
②Claude が debate ファイルに Round 1（Builder Proposal）を書く
③Codex が drafts/ に Round 2（レビュー/画像）を下書き        ← ここを自動化
④Claude が drafts をレビュー → 本体 debate に反映 → Round 3（修正版）
⑤人間が決定 → DECISION_LOG に1行 → 本番反映（Claude が実装）
```

### ③の起動コマンド（コピペ不要）

Codex CLI を Claude Code 側のシェルから直接叩きます。

ラッパースクリプト（`needs-codex-round: true` の debate を自動検出）:

```bash
./scripts/codex-round.sh                 # 自動検出して Codex 実行（drafts に下書き）
./scripts/codex-round.sh --read-only     # 書かず下見だけ
./scripts/codex-round.sh --prompt-only   # 実行せずプロンプトをクリップボードへ
```

中身は Codex CLI の `exec` をスコープ付きで呼ぶだけ:

```bash
/Applications/Codex.app/Contents/Resources/codex exec \
  -C /path/to/repo \
  -s workspace-write \
  "SEMI_AUTO_DEBATE.md のルールに従い、対象 debate を読み、
   Round 2 の下書きを drafts/<同名>.md に書く。この1ファイルのみ。
   commit/push/merge は禁止。完了後に読/書/次の論点を報告。"
```

> `-s read-only` / `-s workspace-write` で権限を絞れる。下書き段階は drafts のみ書込にしておくと安全。

---

## 6. マーカーと drafts staging

debate ファイル冒頭の `## Status` にマーカーを置き、Codex はこれを見て動きます。

```markdown
## Status
- needs-codex-round: true       # Codex の番（自分の Round が空なら動く）
- needs-imagegen: true          # 画像生成OK（最大3案）
- draft-target: drafts/2026-06-17-ideas-hero-visual.md
```

- **drafts staging**: Codex は本体 debate に直書きせず `drafts/` に下書き → Claude/人間がレビューして本体へ反映。**レビュー前の混入を防ぐ**。
- `Final Decision` が埋まっていたら Codex は停止。**最大3ラウンド**で打ち切り（決まらなければ「小さく作って試す」へ）。

---

## 7. ガードレール（安全設計）

Codex に渡す不変のルール:

- push / merge / rebase 禁止（**マージゲートは Claude Code/人間に一本化**）
- 編集してよいのは `debates/*.md` か `drafts/*.md` のみ
- 1回の実行で触る debate は1ファイル
- 自分の担当ラウンド（Round 2 / 4）だけ書く
- `src/` `public/` 設定ファイルは自動編集しない
- 画像生成は `needs-imagegen: true` のときだけ・最大3案
- 実行後に「読/書/次に Claude が見る点」を報告

> 加えて運用モデルとして「**お金がかからず・やり直せる作業は自動 / 本番反映・OS設定・不可逆操作・課金は人間の承認**」を CLAUDE.md に明文化。AI は本番直前に必ず判断材料を提示して止まる。

---

## 8. 動いた実例：ヒーロー画像の刷新

この構成で、サイトのトップ背景画像を更新しました。

1. Claude が3方向を提案（debate Round 1）
2. `codex-round.sh` 起動 → **Codex が3案を画像生成**し比較・推奨（drafts に Round 2）
3. Claude がレビュー＋実装案を Round 3、人間が1案決定
4. 決定を DECISION_LOG に記録 → Claude が `hero-bg-v2.webp`（40KB）を実装 → 本番反映

人間がやったのは「方向を承認し、画像を1枚選ぶ」だけ。**生成・レビュー・実装はAIチームが分担**しました。

---

## 9. コスト設計（おまけ）

- 本番デプロイは Ignored Build Step で「docs/`*.md` だけの変更はビルドをスキップ」。**会議ログや記事の更新は無料**。
- 重い処理（画像生成等）は範囲限定＋人間承認で歯止め。
- 検証はローカル（無料）→ 本番反映は最後の1回だけ。

> だから「**Obsidian に議論を貯めまくっても課金は増えない**」。外部脳は書くほど育ち、コストは増えない設計。

---

## まとめ

要点はこの4つです。

- **役割分担**: Claude=作る/まとめる/マージゲート、Codex=レビュー+量産、人間=決定
- **記憶分離**: 長期(ai-collab) / 連絡(STATUS) / 短期(memo) / 報告(Notion)
- **半自動ループ**: マーカー＋drafts staging ＋ `codex exec` でコピペ排除、3ラウンド上限
- **ガードレール**: 本番反映・push・共有層は人間/Claude に一本化

AI 同士を直接つなぐのではなく、**Git 管理の Markdown を共有黒板にして、人間がゲートを握る**。これが事故らずスケールする現実解だと感じています。

全部いきなり作らなくて大丈夫です。まずは「議論を1ファイルに書いて決定ログを残す」——そこから始めれば十分回り始めます。

---

## 参考資料

- Claude Code スキル公式: https://code.claude.com/docs/en/skills.md
- 公開 Qiita: https://qiita.com/TaichiEndoh/items/f4087c3129b2d017cf3f （医療機関インフラ再構築）

## 著者について

臨床工学技士 × AI エンジニア。教育関係の仕事もしています。
医療と IT のあいだで動きながら、現場目線で発信中です。

- note: https://note.com/taichi_endoh
- Qiita: https://qiita.com/TaichiEndoh
- X: https://x.com/endoh_taichi

質問・情報提供・コラボ提案、いつでも歓迎です。
