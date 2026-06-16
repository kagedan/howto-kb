# 月次棚卸し手順書

毎月、howto-kb 全カテゴリの蓄積を「vault 救い上げ」「archive 退避」「Supabase 整合」で整理する。

棚卸しは Step 0 → 9 を月初〜月中に通しで実行する。score=3 予備プールは Step 5.5 (方法D) で Sonnet 二分化まで含めて毎月処理する。

## 目的

- vault (`D:\Obsidian\kagedan-work\sources\web\`) に有益記事を救い上げる
- 役目を終えた記事を `archive/`（git管理外）にローカル退避し、`articles/` を軽量化
- `index.json` を再ビルドし、Supabase を同期

## 採点軸（記憶しておく）

「**大阪市の公共工事（土木）に携わる非エンジニアが、業務にAIを活用するための howto として vault に保存する価値があるか**」で 5段階採点。

| score | 内容 | 判定 |
|---:|---|---|
| 5 | 実装直結ノウハウ（プロンプト具体例、Skill設計、ワークフロー手順） | ⭕ 採用 |
| 4 | AI活用の汎用ノウハウ（モデル特性、エージェント設計、CLAUDE.md/Tips） | ⭕ 採用 |
| 3 | AI活用事例・業界動向（参考になる事例紹介、新サービス・トレンド） | △ 予備プール |
| 2 | 製品宣伝・概論・本文薄い・有料記事の無料部分・純技術記事 | ❌ 除外 |
| 1 | スパム・無関係・宣伝のみ | ❌ 除外 |

採用範囲は「**書類作成・事務処理にAIを使う具体ノウハウ**」＋「**AI使い方全般**」（Claude/MCP/Skill/エージェント/CLAUDE.md/プロンプト/Hook/Subagent/Handover/Context管理など）。

詳細は memory: `~/.claude/projects/.../memory/feedback_vault_value_criteria.md`

## フロー（5カテゴリ共通）

### Step 0. 候補抽出（全カテゴリ共通、1回だけ）

```bash
python scripts/inventory_select.py
```

出力: `scripts/_inventory/candidates-YYYY-MM-DD.json`

vault 既存URL を除外 + スパム除外（X限定）した残り全件が候補。

### Step 1. カテゴリごとに 1次採点（要約スニペット）

```bash
# バッチ準備（カテゴリ別）
python scripts/inventory_prep_batches.py --category {tag} --batch-size 40 --snippet 1500

# Workflow で採点（Claude側で Workflow ツール起動。Haiku low + 並列）
#  → 結果を workflow_scores-{tag}.json として保存

# ショートリスト生成（score 4-5 のみ）
python scripts/inventory_shortlist.py --scores scripts/_inventory/workflow_scores-{tag}.json --tag {tag} --min 4
```

出力:
- `scripts/_inventory/scores-{tag}-YYYY-MM-DD.json`（採点結果永続化）
- `scripts/_inventory/shortlist-{tag}-YYYY-MM-DD.md`（精選用 md）

### Step 2. 精選（人 or 自動）

`shortlist-{tag}-YYYY-MM-DD.md` の `[ ]` を `[x]` に変えて保存。

- **規模が小さい (~100件)**: かげだんが手動で精選
- **規模が大きい (数百〜数千件)**: 全採用 (`[ ] -> [x]` 一括置換)

```bash
# 一括 [x] 化（規模が大きい場合）
python -c "from pathlib import Path; p=Path('scripts/_inventory/shortlist-{tag}-2026-06-16.md'); p.write_text(p.read_text(encoding='utf-8').replace('- [ ] **', '- [x] **'), encoding='utf-8')"
```

### Step 3. 本文取得 + 採点バッチ生成

```bash
python scripts/inventory_fetch.py \
    --md scripts/_inventory/shortlist-{tag}-2026-06-16.md \
    --scores scripts/_inventory/scores-{tag}-2026-06-16.json \
    --tag {tag}
```

- web 記事 (source != x): readability で本文取得
- X 投稿 (source == x): KB本文の t.co を解決 → リンク先記事 fetch、リンクなし/SNS のみ/取得失敗 → ツイート本文使用
- 出力: `fetched-{tag}-YYYY-MM-DD.json` + `review_batches/{tag}/batch_NNN.json`

### Step 4. 本文採点（Workflow）

Claude 側で Workflow を起動して `review_batches/{tag}/batch_NNN.json` を Haiku 並列採点。
プロンプトは「実本文を読んで採点軸 1-5 で評価」。

結果 → `workflow_review_scores-{tag}.json` に保存。

### Step 5. 採点マージ

```bash
python scripts/inventory_review.py \
    --fetched scripts/_inventory/fetched-{tag}-2026-06-16.json \
    --scores scripts/_inventory/workflow_review_scores-{tag}.json \
    --tag {tag}
```

- score 4-5: vault 取り込み確定
- score 3: 予備プール → `pending-review-{tag}-YYYY-MM-DD.md` に分離
- score 1-2 / 取得失敗: 除外

出力: `reviewed-{tag}-YYYY-MM-DD.json`

### Step 5.5. 方法D：score=3 予備プールの最終判定（Sonnet 厳しめ二分化）【毎月必須】

score=3 は Haiku 1次採点でボーダーラインに残った「業界事例・トレンド寄り」記事。
**毎月の棚卸しでは Step 5 で出た pending_review を全カテゴリまとめて Sonnet で adopt/skip 二分化する**（規模に関わらず実施）。

```bash
# 1. 全カテゴリの pending_review を集約してバッチ化
python scripts/inventory_method_d_prep.py
#  -> scripts/_inventory/method_d_batches/batch_NNN.json （5件 / batch）

# 2. Claude 側で Workflow を起動：
#  - script: .claude/workflows/inventory-method-d.js（保存済み、/inventory-method-d で起動可）
#  - 採点基準: 厳しめ。具体ノウハウ＋業務への応用可能性の双方を満たすもののみ adopt
#  - schema: {id, decision:'adopt'|'skip', confidence, reason}
#  - model: claude-sonnet-4-6（並列最大16、5件×130バッチ ≒ 4〜5分）

# 3. Workflow 結果を decisions.json に保存後、未判定/phantom ID を補正
#  -> scripts/_inventory/method_d_decisions.json

# 4. adopt 分を inventory_import.py 用 json に整形
python scripts/inventory_method_d_build_import.py
#  -> scripts/_inventory/reviewed-method-d-YYYY-MM-DD.json （reviewed_for_import 配列）

# 5. user 確認用 shortlist md を出力（カテゴリ別、confidence 順）
python scripts/inventory_method_d_shortlist.py
#  -> scripts/_inventory/method_d_adopt-YYYY-MM-DD.md

# 6. dry-run → apply で vault 取り込み（Step 6 に合流）
python scripts/inventory_import.py --reviewed scripts/_inventory/reviewed-method-d-YYYY-MM-DD.json
python scripts/inventory_import.py --reviewed scripts/_inventory/reviewed-method-d-YYYY-MM-DD.json --apply
```

注意点:
- Workflow の Sonnet 出力で稀に「phantom ID」（バッチに無い id を勝手に生成）が出るので、pending_review と突合して除外する
- 同様に未判定 id が数件出ることがある。補完 agent で個別判定して decisions に追記
- 中間生成物は使い終わったら `_progress/method_d_YYYY-MM-DD/` に退避し、`method_d_batches/` は削除

### Step 6. vault 取り込み

```bash
# dry-run（件数確認）
python scripts/inventory_import.py --reviewed scripts/_inventory/reviewed-{tag}-2026-06-16.json

# apply
python scripts/inventory_import.py --reviewed scripts/_inventory/reviewed-{tag}-2026-06-16.json --apply
```

vault `D:\Obsidian\kagedan-work\clippings\` にフロントマター付き md を書き出す。
その後 vault 側で `clippings-to-sources` スキルで `sources/web/` に振り分け。

### Step 7. archive 退避（容量整理）

```bash
# dry-run
python scripts/inventory_archive.py \
    --md scripts/_inventory/shortlist-{tag}-2026-06-16.md \
    --scores scripts/_inventory/scores-{tag}-2026-06-16.json \
    --tag {tag}

# apply
python scripts/inventory_archive.py --md ... --scores ... --tag {tag} --apply
```

`[x]` を付けた全件（vault 取り込み成否に関わらず）を `articles/{tag}/{file}.md` → `archive/{tag}/{file}.md` に移動。

archive は `.gitignore` で除外（git管理外＝ローカル退避）。

### Step 8. index 再ビルド + Supabase 整合

```bash
# index.json 再ビルド（articles/ のみ対象なので archive を自動除外）
python scripts/build_index.py

# Supabase 同期（差分）
python scripts/sync_supabase.py

# Supabase の orphan（index.json に無い行）を削除
python scripts/cleanup_supabase.py --orphan --force
```

### Step 9. git commit

archive 移動した分は `articles/` から消えるので、git 上は削除として反映される。
新規スクリプトや改修分とまとめて 1 コミットで OK。

```bash
git add -A
git commit -m "session: 月次棚卸し YYYY-MM 実行（...内訳...）"
# push は別途確認
```

## カテゴリ別の所要

| カテゴリ | 件数目安 | shortlist | fetch | review | 合計 |
|---|---:|---:|---:|---:|---|
| antigravity | 〜100 | 即生成 | 2-5分 | 1-2分 | 約10分 |
| cowork | 〜500 | 即生成 | 10-15分 | 2-5分 | 約30分 |
| construction | 〜1500 | 即生成 | 5-10分 | 3-5分 | 約20分 |
| claude-code | 〜5000 | 即生成 | 60-90分 | 10-20分 | 約2時間 |
| ai-workflow | 〜5000 | 即生成 | 60-90分 | 10-20分 | 約2時間 |
| **全体** | | | | | **約5時間** |

並列起動すれば短縮可能（fetch を 4 並列で同時実行など）。

## 注意点

- **採点ワークフロー漏れ**: Haiku の出力で id が抜けることがある（数件〜100件規模）。`inventory_review.py` が「⚠ 未採点 id」を報告するので、補完 agent で別途採点して `workflow_*scores-{tag}.json` に追記してから再 review する
- **重複出力**: id ベースで自動 dedup されるので件数のズレは無視可能
- **Supabase orphan**: 月数モード (`cleanup_supabase.py -m N`) と orphan モード (`--orphan`) は補完的。archive 移動した分は orphan モードで消す
- **vault 振り分け**: `clippings/` への書き出し後、kagedan-work 側の Claude Code で `clippings-to-sources` 等を実行する必要あり
- **採点軸の調整**: 採点結果がズレるなら memory `feedback_vault_value_criteria.md` を更新して再採点

## 初回実行記録 (2026-06)

| カテゴリ | 候補 | shortlist [x] | fetch ok | review 採用 | vault取込 | archive |
|---|---:|---:|---:|---:|---:|---:|
| construction | 1,013 | 77 | 76 | 35 | 35 | 77 |
| antigravity | 68 | 27 | 26 | 15 | 15 | 27 |
| cowork | 338 | 173 | 167 | 102 | 102 | 173 |
| ai-workflow | 4,123 | 1,730 | 1,672 | 1,039 | 1,039 | 1,729 |
| claude-code | 4,075 | 2,312 | 2,260 | 1,578 | 1,578 | 2,311 |
| **合計** | **9,617** | **4,319** | | | **2,769** | **4,317** |

副次効果:
- articles 残: 5,840件（45%削減）
- index.json: 6.6MB → 3.7MB（44%削減）
- Supabase orphan 4,378件削除 → index.json と完全一致

## 方法D 実行ログ

毎月の実施結果を新しい順に追記する。

### 2026-06-16

score=3 予備プール 658件を Sonnet で再判定 (Workflow 並列、約4.5分)。

| カテゴリ | pending_review | adopt | skip |
|---|---:|---:|---:|
| antigravity | 9 | 0 | 9 |
| construction | 17 | 0 | 17 |
| cowork | 32 | 4 | 28 |
| ai-workflow | 305 | 12 | 293 |
| claude-code | 295 | 54 | 241 |
| **合計** | **658** | **70** | **588** |

vault 取込: 70件 (vault `clippings/` 経由 → `clippings-to-sources` で `sources/web/` へ振り分け)。
中間生成物・判定履歴は `_progress/method_d_2026-06-16/` に退避。
