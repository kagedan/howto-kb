---
id: "2026-05-20-自分の-wikiobsidian-なしで開ける-記憶が勝手に賢くなる-kioku-v010-01"
title: "自分の wiki、Obsidian なしで開ける? 記憶が勝手に賢くなる? — KIOKU v0.10"
url: "https://zenn.dev/megaphone_tokyo/articles/10b40b01447f5b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/60d37f9e6b81-20260520.png)

## はじめに

Claude Code / Desktop / Codex CLI / Gemini CLI の記憶 OSS「KIOKU」を作っています。直近の流れ:

* **v0.7.0 (4/28)**: マルチエージェント対応の記憶共有 (Claude / Codex / Gemini が同じ session-logs/ に書き込む)
* **v0.7.5 (5/8)**: 「自分の KIOKU は動いてる?」「Wiki は腐ってない?」の 2 つの自己診断ツール (`kioku doctor` / `kioku_health`)
* **v0.8 (5/12)**: Visualizer β — Wiki の git 履歴を時間軸の HTML で見る最初のビュー

ここまでで「動く / 健康 / 過去が見える」が揃いました。が、自分で日常的に KIOKU を使っていると、今度は **「使う側の体験」に 5 つの不満** が残っていることに気付きました。

1. **「Obsidian を起動せずに、ブラウザで自分の Wiki を一望したい」** — Visualizer β は時間軸ビューだけで、ダッシュボード (今アクティブな概念 / 直近の判断 / 取り込み待ち) は Obsidian の Bases plugin がないと見えない
2. **「Wiki の中で keyword を探したい、足りなければ Claude にもっと深掘りしてほしい」** — 検索は MCP tool 経由でしか叩けず、ブラウザ上で「とりあえず 5 秒で当たり付け」ができない
3. **「移動中にスマホで Wiki を読みたい、続きは Claude モバイルアプリに渡したい」** — HTML ビューは PC ブラウザ前提で、iPhone Safari で開くと文字が小さくタブも横スクロール
4. **「クラウド同期が静かに失敗する不安をなくしたい」** — Git push が失敗しても次回起動時に何も告知されず、気付いたら Mac mini と MacBook で内容がズレている
5. **「記憶の取り込みが裏で失敗していても気付けない、検索候補がいつまでも固定で賢くならない」** — 素材の取り込みが落ちても無言、ブラウザ検索の候補は固定計算で「自分が実際に何を調べているか」が反映されない

<https://github.com/megaphone-tokyo/kioku>

## 1. 「Obsidian を開かずに、ブラウザで Wiki を一望したい」

Sprint 3 の Visualizer β (5/12) で、Wiki の git 履歴から時間軸ビューを生成する `kioku_generate_viz` MCP tool が land しました。**ページがいつ生まれて、どのページがどのページに繋がったか** が時系列で見える HTML です。

ただ、Visualizer β だけでは「Wiki を眺めるブラウザ体験」は半分しか完成していませんでした。残り半分が「**ダッシュボード**」 — 今アクティブな概念 / 直近の判断 / hot キャッシュの状態、といった「今の Wiki の現在地」を見せる入口です。これまでは Obsidian で `wiki/meta/dashboard.base` を開かないと見えませんでした。

Sprint 4 Phase 1 で **Web UI shell + Bases dashboard renderer** を内製し、`kioku_generate_viz` に `mode: 'shell'` を追加しました。Claude Code セッション内で `kioku_generate_viz` MCP tool を `mode='shell'` で 1 回呼んでもらうだけで、`$VAULT/.cache/viz/wiki-graph.html` に **8 タブ構成のシェル HTML** が出力されます:

```
[Dashboard] [Overview] [Timeline] [Diff] [Lineage]
  + (placeholder で先出し): [Search] [Navigation] [Wikilink]
```

Dashboard タブには **Obsidian の Bases plugin が普段見せている view が、Obsidian なしで再現** されます (Hot Cache / Active Projects / Concepts / Decisions など)。`.base` ファイルの YAML を Node 標準ライブラリだけで parse して renderer 側で描画するので、Obsidian も外部 plugin も要りません。

なぜ 8 タブ全部を最初に出したか — 「あとで増えるかもしれない」を匂わせるためではなく、**Phase 2 (Search) / Phase 3 (Navigation) / Phase 4 (Wikilink) で実装される未来のタブ位置を、Phase 1 時点で固定** するためです。タブの並びが後から変わると、ユーザーがブックマークした URL の `#tab=...` が壊れる。先に枠だけ用意して、placeholder には「Phase 2 で実装予定」のラベルを付ける。Phase 2 公開時に `Search` タブが置き換わって、ユーザーから見ると「タブが変わった」ではなく「**鍵が外れた**」体験になります。

### 設計の境界 — 「ブラウザで開けるけど、ブラウザでは編集しない」

Phase 1 で重要だったのは「**何を作らないか**」を明示したことです。具体的には:

* **エディタは作らない** (Monaco / CodeMirror / ProseMirror / TipTap / Lexical 全部 forbidden keyword に登録)
* **新規ページ作成 UI は作らない** (Web UI から `wiki/` 配下に書き込む手段なし)
* **外部 CDN / fetch / WebSocket は作らない** (シェル HTML は完全 self-contained、`<script src>` / `<link href>` 0 件)
* **Canvas alternative は作らない** (Obsidian Canvas 相当の draw board は範囲外)

この境界を **「Path C+β」** という内部呼称で 4 phase ずっと維持しています。Wiki を**書く**ためのツールは Obsidian や VS Code に任せて、KIOKU は **Markdown 解析プラットフォーム** に徹する、という分業です。Obsidian と KIOKU の両立、claude-obsidian (先行 OSS) との棲み分け、競合より「使う場所」で勝つ、というポジションが Phase 1 で具体的な HTML として現れた、という意味で大きい release でした。

## 2. 「ブラウザで keyword 検索、足りなければ Claude で深掘り」

Phase 1 で `Search` タブの **枠だけ** 出した翌日、Phase 2 で中身を入れました。

ここで設計判断が 1 つありました。「ブラウザの Search タブ」を作るときに、自然に出てくる選択肢が 2 つある:

* **案 A**: ビルド時に「よく検索されそうな keyword の Top-N」を裏で先に検索しておいて、結果を HTML に inline JSON で埋め込む。ユーザーが入力した文字に対して **JS でクライアントサイド filter** だけで結果を絞る (= offline-first、サーバ不要)
* **案 B**: localhost に HTTP サーバを立てて、ブラウザの Search タブから `fetch(localhost:NNNN/search?q=...)` を叩く。任意の keyword にライブで答えられる (= ライブ、HTTP サーバが追加の攻撃面になる)

6 名のロールエージェント (PM / CTO / 戦略 / マーケ / セキュリティ / UX) で慎重に議論した結果、**案 A を意図的に採用** することにしました ([meeting 26051403](https://github.com/megaphone-tokyo/kioku/blob/main/plan/claude/26051403_meeting_phase2-architectural-decision-option-c.md))。理由は 4 つ:

1. **「Hardened LLM Wiki」というポジションと整合** — HTTP サーバを立てない時点で、CSRF / localhost rebinding / port 衝突 / CORS / CSP の追加の攻撃面が全部消える
2. **規模が小さい** — 16-20 時間で land、追加サーバ実装の 22-30 時間を回避
3. **Phase 3 (Mobile) との合流が綺麗** — offline-first の precomputed JSON ならスマホでもそのまま動く
4. **「ブラウザで 5 秒の当たり付け → Claude で深掘り」の 2 段検索** という UX が、KIOKU の差別化点になる

この **「offline-first + Claude-augmented」の 2 段検索** が、v0.9.0 のキャッチコピー **「Claude-augmented Search」** の正体です。具体的にはこう動きます:

**Tier 1 (シェル HTML 単独で完結、5 秒で結果)**:

```
ユーザー: ブラウザで Search タブを開いて「pgvector」と入力

ブラウザ: ビルド時に事前計算した Top-N popular queries の中から
        「pgvector」を含む結果を JS でフィルタ
        → 5 秒以内に「pgvector に関係する Wiki ページ 8 件」を表示
        (タイトル + 抜粋 + 関連度スコア)
```

**Tier 2 (Claude conversation でドリル、LLM-augmented)**:

```
ユーザー: 結果の下にある「Claude で深掘り検索」ボタンをクリック

ブラウザ: クリップボードに kioku_search MCP tool 呼び出し prompt をコピー
        + Claude Desktop / Code を開くプロンプトを表示

Claude:  ユーザーが prompt を Claude に貼り付けると、
        kioku_search が任意の keyword で full search → 自然言語で結果整理
        → 「pgvector の RAG パイプラインで Supabase だけで完結するパターンは
          concepts/pgvector-rag-pipeline.md の 〜」のように回答
```

**「ブラウザは速い当たり付け、Claude は深い理解」の役割分担** が、ユーザー体験として 2 段で繋がっています。Tier 1 だけだとマイナーな keyword で 0 hit になるので、その時の自然な逃げ道が Tier 2、という設計。

技術的には、shell HTML の `<input>` イベントから DOM への描画まで **すべて textContent + createElement のみ** で組んでいます。`innerHTML =` は forbidden keyword で全 file 0 hit、XSS surface 増分ゼロを保証 (Phase 1 で確立した contract をそのまま継承)。検索結果に `<script>` や `<img onerror>` が混じっていても、textContent はそれを文字列としてしか描画しないので無害化されます。

## 3. 「移動中にスマホで Wiki を読みたい、続きは Claude mobile に渡したい」

Phase 1+2 の HTML は PC ブラウザ前提でした。実際 iPhone Safari で開いてみると:

* 8 タブが横スクロール (タブを切り替えるのに横スワイプ + tap が必要)
* フォントが 12px で小さすぎ、入力欄が 14px なので Safari が auto-zoom 発動
* Visualizer β の SVG グラフはスマホ画面に収まりきらず、フィット表示すると nodes が見えない
* 「Claude で深掘り検索」ボタンを押しても desktop の MCP tool 想定で、モバイルでは何も起こらない

Phase 3 で 4 軸まとめて Mobile 対応しました:

### a. レスポンシブ CSS + ハンバーガーメニュー

`< 768px` を breakpoint にして、CSS media query で 8 タブの横並びを **ハンバーガーメニュー + 縦スタック** に切り替え。tap target は **iOS HIG 推奨の 44pt 以上** を全 interactive 要素に強制。input は **16px** にして Safari の auto-zoom を無効化、virtual keyboard 出現時の自動 scroll も実装。

### b. Visualizer β の Mobile simplified view

スマホ画面では SVG グラフを諦めて、**ページ一覧の text list** に切り替え。タブレット以上では従来通り SVG。「視覚的に弱くなる」のではなく、**「スマホでは情報密度が高い text のほうが速く読める」** という UX 判断 ([meeting 26051404](https://github.com/megaphone-tokyo/kioku/blob/main/plan/claude/26051404_meeting_phase2-retrospect-and-phase3-judgment.md))。

### c. Tier 2 deep-link を Mobile 対応 (`claude://` URI scheme)

「Claude で深掘り検索」ボタンに **URI scheme detection** を追加:

* **デスクトップ**: 既存の MCP tool prompt クリップボード copy
* **モバイル**: `claude://` URI scheme を attempt → 1.5 秒待って起動しなければ `claude.ai` web に fallback

iOS / Android の Claude モバイルアプリがインストールされていれば、ボタン 1 回で **Claude モバイルアプリの会話画面に検索 prompt が prefill された状態で開く** という動線が完成します。インストールしていなければ、ブラウザで `claude.ai` が開いて web 版で続けられる。**「Hardened な navigation 契約」** として、CSP `navigate-to` policy + JS-side whitelist の 2 段防御で、攻撃者が任意の URI scheme を突き刺せない設計にしています。

### d. パフォーマンス予算 461KB → 300KB

Mobile 4G 想定で **シェル HTML の初期 render < 1 秒** を目標に、JS minification + tree-shake で 461KB → 300KB に圧縮。self-contained を維持したまま (外部 CDN 禁止) で達成、というのが Phase 3 の地味な裏方の工夫でした。

実機 dogfood も Phase 3 acceptance gate に組み込み、PM の Vault を iPhone Safari + Android Chrome の両方で開いて 9/9 acceptance criteria を満たしてからの land。**KIOKU の Mobile 対応は「desktop の縮小版」ではなく、「移動中 5 分の wiki チェック → 続きを Claude mobile に渡す」** が一連の動線として組まれています。

## 4. 「クラウド同期が静かに失敗する不安をなくしたい」

ここまで 3 phase で「**使うため**」の改善を積みましたが、ずっと残っていた地味な問題が **「Git 同期が静かに失敗する」** こと。

KIOKU は SessionStart Hook で `git pull --rebase --quiet`、SessionEnd Hook で `git add + commit + push` を回しています。WiFi が切れていたり、別の Mac で先に push されていたり、credential が切れていたりすると、これが **silent fail** します。気付くのは「あれ? Mac mini で書いた wiki が MacBook に来てない」と数日後に気付く時。

Phase 4 で 4 軸の Sync polish を入れました:

### a. retry queue (`.kioku-sync-retry.json`)

git push が失敗したら、エラーの種類 (network / non-fast-forward / auth) を分類して **`$OBSIDIAN_VAULT/.kioku-sync-retry.json`** に記録します:

```
{
  "errorType": "network",
  "timestamp": "2026-05-15T10:23:00Z",
  "retryCount": 0
}
```

次回 SessionStart で retry queue があれば、`git pull --rebase` 後に push を再試行。成功したら queue ファイルを削除、失敗したら `retryCount` を +1 して記録を更新。**ユーザー操作なしに、次回起動時に勝手に再同期** されます。

資格情報系 (GitHub Personal Access Token、SSH key literal) は **エラーメッセージの中でもマスク** してから retry queue に書き込む、というのが地味だが重要な点。LEARN#13 + `scan-secrets` パターンと整合。

### b. ユーザーへの通知文

UX の観点で、エラーの伝え方も丁寧に再設計:

* ❌ `Git push failed` (技術的、ユーザー混乱)
* ✅ `クラウド同期できませんでした。次回 Claude 起動時に再同期されます (詳細: network unreachable)` (action 不要であることを明示)

### c. `kioku doctor` の sync state diagnostic

`bash scripts/doctor.sh` の出力末尾に **`Sync state`** セクションを追加:

```
Sync state: ✅ healthy (last push: 2026-05-15 10:23、network: reachable)
```

retry queue が pending なら ⚠ 表示、network が unreachable なら情報併記、最後に成功した push の timestamp も表示。**「自分の KIOKU は今健康?」 と「自分の同期は今動いてる?」** を 1 コマンドで確認できる状態になりました。

### d. テスト基盤 (sync mock)

`mockGitPushFailure(errorType)` ヘルパーを `tests/fixtures/test-helpers.mjs` に追加。network / reject / auth の 3 mode で git push 失敗を模擬できるようになり、retry queue / sync state の自動テストが可能に。**Phase 4 の地味な土台** ですが、今後 Sprint 5 で Sync 周りを触る時の安全網になります。

これで KIOKU の同期の仕組みは **「失敗をユーザーに告げて、次回自動で再試行」** に変わりました。「Hardened」のピースがここまでで揃った、というのが v0.9.0 の意味です。

## 5. 「記憶の取り込みが裏で失敗しても気付けない、検索候補がずっと固定で賢くならない」をなくしたい

ここまでの 4 つは v0.9.0 (5/13-16) で揃えた「使いたい体験」でした。**v0.10.0 (5/17-19) は方向が少し違って、「KIOKU の記憶パイプライン自身が、信頼性と賢さを自分で育てる」** という自己進化の軸です。

§4 で「Git 同期の silent fail を retry queue でなくした」話を書きました。実は同じ問題がもう 1 箇所、**記憶の取り込み (auto-ingest)** にも残っていました。

### a. 取り込みの silent fail をなくす (Sprint 5、v0.10.0 axis A)

KIOKU は `raw-sources/` に置いた素材を `auto-ingest.sh` で extract → Claude で要約 → `wiki/summaries/` に書く、というパイプラインを定期実行しています。ここで extract が失敗したり、要約が途中で落ちたりしても、§4 の Git 同期と同じく **silent fail** していました。

Sprint 5 で、§4 の sync retry queue と **完全に同じパターン** を取り込み側にも適用:

* extract / 要約の失敗を種類分類 (`extract_failed` / `llm_failed` / `fs_error` / `sha256_drift`) して `.kioku-auto-ingest-retry.json` に記録
* 次の定期実行で自動 retry、3 回失敗したものは **手動 review queue** に回す (無限 retry を避ける)
* 資格情報は `scripts/lib/masking.mjs` の SSOT 経由でマスクしてから記録 (§4 と同じプライバシー担保)
* `bash scripts/doctor.sh` に **auto-ingest state** セクションを追加 →「取り込みは今健康?」が 1 コマンドで分かる

§4 の「Sync polished」が、記憶を**取り込む**パイプラインまで延長された、という意味で「Hardened」の総仕上げのピースでした。

### b. 検索が、使うほど賢くなる (Sprint 5.5、v0.10.0 axis B)

§2 の「ブラウザ検索 → Claude で深掘り」で、ブラウザ側の Tier 1 はビルド時に「よく検索されそうな keyword の Top-N」を事前計算する、と書きました。この「よく検索されそう」の推定は、これまで **7 つの固定 source** (Wiki のタグ参照 / index の wikilink / git commit subject など) からの静的計算でした。固定なので、**ユーザーが実際に何を検索しているかは反映されない**。

Sprint 5.5 で 8 番目の source を追加 — **ユーザーの実利用ログ** です:

* `session-logs/` をスキャンして、実際に検索された query を抽出し、最高 weight (2.8) で候補に加算
* 累積ファイル (`.kioku-discoverqueries-usage.json`) で **時間をかけて学習** → 使うほどブラウザ検索の当たりが良くなる
* **プライバシー契約**: `masking.mjs` SSOT で PII / 機微情報をサニタイズ、容量上限 64KB、`.kioku-discoverqueries-opt-out` ファイルを置けば学習を完全に無効化
* `doctor.sh` に discoverqueries state セクション追加 (使用ログのサイズ / opt-out 状態)

「検索インデックスが固定」から「**使うほど賢くなる**」へ。これが v0.10.0 のキャッチコピーに加わった **「reliability/intelligence の自己進化」** の中身です。

> v0.9.0 で「使いたい時に使える」を揃え、v0.10.0 で「**記憶パイプライン自身が信頼性と賢さを自分で育てる**」を足した。この 2 つを 1 本にまとめたのが本記事の理由です。

## 6. (副次) 全 phase 通底の Hardened 契約 — なぜ「offline-first / textContent only」を貫いたか

ここからは engineer 向けの副次トピックです。「v0.9.0〜v0.10.0 = Hardened LLM Wiki for Professionals + Claude-augmented Search + Mobile + Sync polished + reliability/intelligence の自己進化」という長いキャッチコピーの「**Hardened**」の中身。

Sprint 4 の 4 phase + v0.10.0 の Sprint 5/5.5 はそれぞれ範囲が違いましたが (data renderer / search / responsive UI / sync infra / 取り込み reliability / 検索学習)、全 phase で **同じ契約を継承** していました。特に §5 の Sprint 5/5.5 は、§4 で作った retry queue / credential masking の `masking.mjs` SSOT をそのまま再利用 — **契約は機能追加のたびに作り直すのではなく、一度作って継承する** という設計の実例です:

| 契約項目 | 内容 | 全 phase で grep verify |
| --- | --- | --- |
| **self-contained** | snapshot mode の HTML は外部依存 0 (`<script src>` / `<link href>` / `fetch` / `XMLHttpRequest` / `WebSocket` 全 0) | ✅ |
| **textContent only** | 検索結果 / Visualizer node / Dashboard view 全部が DOM 経由で render、`innerHTML =` は forbidden keyword で 0 hit | ✅ |
| **Path C+β 境界** | エディタ / 新規ページ作成 UI / Plugin loader / Cloud connector / Electron / Canvas alternative は全部 forbidden keyword | ✅ |
| **credential masking** | retry queue / error log / session log すべてで GH\_TOKEN / GITHUB\_TOKEN / SSH key literal を mask | ✅ |

各 PR の完了報告 mandatory step に **「forbidden keyword self-grep」** を入れています。たとえば Phase 2 では:

```
grep -rnE "(\bnew\s+Function\b|\beval\(|\.innerHTML\s*=|\.outerHTML\s*=)" \
  tools/claude-brain/mcp/lib/qmd-search-index.mjs \
  tools/claude-brain/mcp/templates/shell-template.html \
  tools/claude-brain/mcp/tools/search.mjs
# Expected: empty (0 hits)

grep -rnE "(\bfetch\(|XMLHttpRequest|sendBeacon|WebSocket)" \
  tools/claude-brain/mcp/templates/shell-template.html
# Expected: empty (snapshot mode self-contained 維持)
```

「forbidden な API が混入していない」を **PR ごとに機械的に証明** する。コードレビューで人間が「`innerHTML` 見落としてないか」を目視するのではなく、`grep -rnE` 1 行で 0 hit を確認する。**Hardened は文化ではなくテストで担保** する、というのが Sprint 4 全体の通底原則でした。

副次的な恩恵として、v0.9.0〜v0.10.0 の全 phase 通じて **新規の攻撃面増加 0 件** を達成。Mobile responsive は CSS と JS feature detection だけ、Tier 2 deep-link は CSP `navigate-to` ポリシー + whitelist で追加防御、Sync retry / auto-ingest retry / discoverQueries 学習は同じ credential masking SSOT で漏洩防止 (Sprint 5.5 の検索学習は加えて PII サニタイズ + opt-out + 容量上限のプライバシー契約)。**「機能を増やしながら、攻撃面は増やさない」** という、地味だが OSS としての信頼につながる設計を維持しました。

### multi-Claude セッションの分業 (前作の続き)

[v0.7.2-v0.7.5 retrospect](https://zenn.dev/megaphone_tokyo) で書いた「PM Claude / 制作 Claude / マーケ Claude の分業」がそのまま使えました。Sprint 4 の 4 phase + Sprint 5/5.5 という cadence は、subagent-driven cycle が **収束した安定状態** に到達したことを意味します:

* Phase 1: 1 日 (4 sub-PR、N=17-20 of 4 cycle)
* Phase 2: 1 日 (4 sub-PR、N=21-24 of 4 cycle)
* Phase 3: 1 日 (4 sub-PR、N=21-24 of 4 cycle)
* Phase 4: 半日 (3 sub-PR、N=25-27 of 3 cycle 簡略形)
* Sprint 5 (v0.10.0 axis A): 当日完走 (3 sub-PR、N=3 cycle 簡略形)
* Sprint 5.5 (v0.10.0 axis B): 当日完走 (3 sub-PR、Sprint 5 パターン完全再利用)

「plan canonical の成熟」「依存順序の明確化」「前 phase contract の継承」 — この 3 つの要点を `.claude/rules/workflow.md` に LEARN convention として明文化したことで、**1 phase あたりの cycle cost が安定状態に収束** しました。1 サイクル目で 9 日かかっていた Sprint 1 と比べて、Sprint 4 以降は 1 phase あたり 1 日。Sprint 5/5.5 は Sprint 4 Phase 4 の retry queue パターンをそのまま再利用して当日完走、という再現性を示せました。

## 試し方

```
# Plugin marketplace (推奨、Mode C = Full memory)
claude plugin marketplace add megaphone-tokyo/kioku
claude plugin install kioku@megaphone-tokyo

# 軽量モード (Mode A = MCP-only) で試す場合
bash scripts/install-mcp-client.sh --apply

# 「自分の Wiki を Obsidian なしで開きたい」 — シェル HTML 生成
# Claude Code セッションで以下を依頼:
#   「kioku_generate_viz を mode='shell' で呼んでください」
# → MCP tool が $OBSIDIAN_VAULT/.cache/viz/wiki-graph.html を出力
open "$OBSIDIAN_VAULT/.cache/viz/wiki-graph.html"
# → 8 タブ構成の Web UI shell が開く

# 「ブラウザで keyword 検索、Claude で深掘り」 — Search タブ動作確認
# (シェル HTML を開いた状態で Search タブをクリック → keyword 入力)

# 「スマホで Wiki を見たい」 — シェル HTML を iPhone Safari / Android Chrome で開く
# (ハンバーガーメニュー + 縦スタック レイアウトに切り替わる)

# 「クラウド同期が今健康?」 — doctor の sync state diagnostic
bash scripts/doctor.sh | grep -A3 'Sync state'

# 「記憶の取り込みは今健康? 検索学習は動いてる?」 — v0.10.0 の自己診断
bash scripts/doctor.sh | grep -A3 'Auto-ingest state'
bash scripts/doctor.sh | grep -A3 'DiscoverQueries'
```

`kioku_generate_viz mode='shell'` は **読み取りのみ** で完結します (Wiki には何も書きません、`.cache/viz/` 配下に HTML を出力するだけ)。Claude Code セッション内で MCP tool として呼べるので、気軽に試してみて、4 タブ + 4 placeholder タブの構成と Dashboard view を眺めてください。

## 次の Sprint と結び

v0.10.0 で「使いたい体験」+「記憶パイプラインの自己進化」が揃いました。この先 (Phase 6+) の方向性は release 反応を観察してから確定しますが、現時点の候補:

* **Tier 3 (将来)** — served mode / Mobile native app の再評価。現状 YAGNI で defer 中、ニーズ次第で復活
* **plugin marketplace / monetization 系** — release の反応を見てから検討する候補
* **検索学習の発展** — Sprint 5.5 で入れた利用ログ学習を、複数マシン横断や精度改善に広げる方向

Sprint 1+2 (5 月上旬) + Sprint 3 (5/12) + Sprint 4 (5/13-16、v0.9.0) + Sprint 5/5.5 (5/17-19、v0.10.0) で、**「動く / 健康 / 過去が見える / 使いたい / 記憶が自分で賢くなる」 の 5 軸が揃った v0.9.0〜v0.10.0** が完成しました。**「Hardened LLM Wiki for Professionals + Claude-augmented Search + Mobile responsive + Sync polished + reliability/intelligence の自己進化」** が 1 行 narrative。

OSS は release で終わりではなく、**振り返りで初めて「何ができるようになったか」が言葉になる** と毎回感じます。v0.9.0 + v0.10.0 を別々に見ると「シェル + 検索 + モバイル + 同期 + 取り込み reliability + 検索学習」の 6 機能の集合ですが、振り返りで束ねると **「ユーザーが使いたい時に使えて、記憶パイプライン自身が信頼性と賢さを育てる状態にした 1 週間」** という 1 文に圧縮できる。

KIOKU を試してみる方は、まず Claude Code セッション内で `kioku_generate_viz` MCP tool を `mode='shell'` で呼んでシェル HTML を生成して、ブラウザで開いてみてください。Dashboard / Overview / Timeline / Lineage の 4 タブを巡るだけで、「自分の Wiki がどんな状態か」が 1 分で見えます。

<https://github.com/megaphone-tokyo/kioku>

## 他のプロダクト

季節の写真を集めたギャラリーサイトです。作者が撮影した四季折々の写真を眺められるだけでなく、**自分の画像と季節の写真を AI で合成する** 機能もあります。

写真が好きで、AI で遊ぶのも好き、という個人的な興味から作りました。

---

**作者**: [@megaphone\_tokyo](https://x.com/megaphone_tokyo)  
コードと AI で何かつくる人 / フリーランスエンジニア 10 年目 / 東京
