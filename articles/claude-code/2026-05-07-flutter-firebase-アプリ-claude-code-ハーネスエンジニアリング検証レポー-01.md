---
id: "2026-05-07-flutter-firebase-アプリ-claude-code-ハーネスエンジニアリング検証レポー-01"
title: "Flutter + Firebase アプリ × Claude Code ハーネスエンジニアリング検証レポート"
url: "https://zenn.dev/never_inc_dev/articles/7909da3ac54885"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

## 1. はじめに

このレポートは、Claude Code を素のまま会話で使うのではなく、**Agents / Skills / Hooks / MCP の 4 層ハーネス** を組んで AI コーディングを「仕組みで縛る」方向に倒した実験のまとめです。

## 2. 背景：AI コーディングのよくある課題

実際に開発を回しながら **自分の手で踏み抜いた順** で書きます。

* 対話型だと **セッションを跨ぐと文脈が消える** → 翌日に「どこまで進んだ？」を再説明するコストが毎回かかります
* AI が自分の実装を自分で「できました」と言う → **採点バイアス**。テストも通っているが本当に動くかは怪しいです
* スプリント間のアーキ判断が **口頭引き継ぎで蒸発**。3 日後に同じ議論を再演します
* ライブラリ最新版・MCP 利用が雑だと **`flutter analyze` を Bash 直叩き** など Tool 誤用が増え、結果がばらつきます
* main 直 commit / 巨大 PR で **レビュー粒度が崩れる**。後から原因切り分け不能

「**プロンプトで頑張る**」のではなく「**仕組みで縛る**」 に倒したのが今回のハーネスです。

## 3. プロジェクト概要

| 項目 | 内容 |
| --- | --- |
| プロダクト | テーマ を入力 → Claude Sonnet 4.6 が章立て・本文・章末問題を生成 → Apple Books 風 Viewer で読む iOS / Android アプリ |
| 技術 | Flutter（Riverpod + Hooks / Feature-First）+ Firebase（Auth / Firestore / Functions / Storage）+ Anthropic SDK |
| 期間 / 規模 | 40h 想定 / Sprint 8 まで定義済 / 現在 Sprint 3 完了 |
| 開発体制 | 開発 1 名 + Claude Code ハーネス |

### 3.1 完成アプリ（iPhone 17 Pro Simulator / Sprint 3 完了時点）

| ホーム（B1） | ライブラリ（B2） | 参考書 Viewer（E1） |
| --- | --- | --- |
| ホーム | ライブラリ | 参考書 |
| テーマ を入力して参考書を生成、最近の参考書を横スクロールで一覧 | 生成済み参考書を 3 列グリッドで管理。検索・並び替え。 | Markdown レンダリング・目次 Drawer・前次章ナビ・読書フォントサイズ 5 段階 |

## 4. ハーネス全体像

人間が触るのは **slash command と PR レビューだけ**。実装・採点・記録は agent / hook / MCP が担う。

**E2E の役割分担**: アプリ内の **Flutter widget は Marionette MCP**（`ValueKey` で確実に特定）、**OS が出すネイティブ dialog（通知許可・share sheet 等）は computer-use**（screenshot + 座標クリック）で操作する **ハイブリッド E2E**。Sprint 3a で実運用パターンを確立済みです。

ポイントは 「対話するのは人間 ⇄ slash command だけです。あとは agent と hook と MCP が動きます」。

## 5. 構成要素一覧

### 5.1 Subagents（9 体）

| Agent | model | 役割（入力 → 出力） |
| --- | --- | --- |
| planner | opus | 要件 / 技術選定 / DB / API / DESIGN を読んで、**機能リスト・受入条件・スプリント分割をまとめた仕様書（`SPEC.md`）** を作成・更新します。プロダクトオーナー兼プランナーの役割 |
| generator | sonnet | `SPEC.md` と `HANDOFF.md`（前スプリントの引き継ぎ）を読み、**1 スプリント分のコード（Flutter `app/` + Cloud Functions `functions/` + widget / unit / golden test）を実装** し、HANDOFF.md を更新する |
| evaluator | opus | generator の成果物を **iOS Simulator で実機 E2E（Marionette MCP 経由）** + `dart analyze` + `flutter test` で検証し、**4 軸ルーブリック採点**（Func / Code / Arch / UX）を `EVAL_REPORT.md` に出力 |
| flutter-architect | opus | Flutter 側の **Riverpod / Hooks / Feature-First** に関する設計判断を担当。状態管理（`@riverpod` / `keepAlive`）・ディレクトリ構成・Provider 分割の相談先。判断は `DECISIONS.md` に追記される |
| functions-architect | opus | Cloud Functions 側の設計判断を担当。**HTTPS callable / Firestore トリガ / scheduler の使い分け**、Anthropic SDK 呼び出しのリトライ・タイムアウト・コスト制御を相談される |
| designer | sonnet | デザイン全般を担当。デザイントークン（hex / spacing / radius）・コンポーネント命名・画面レイアウトを決定し、**ルールを `DESIGN.md` に**、適用例を **`prototype/screens/*.html`** として書く |
| code-reviewer | opus | PR / ブランチ差分を **CodeRabbit のように精密レビュー**。命名・重複・規約逸脱・テスト不足を `high / medium / low / nit` で指摘。読み専任で書き込みはしない |
| firestore-rules-reviewer | opus | **`firestore.rules` / `storage.rules` 専任**。コレクション横断のアクセスパターン・auth 検証・不変フィールドの保護・rules テストの deny ケース不足など rules 固有のアンチパターンを検出 |
| security-reviewer | opus | **Secrets 漏洩・auth/authz・PII 出力・依存脆弱性・Anthropic キー保護・git 履歴スキャン** を横断的に確認。`firestore-rules-reviewer` と責務分離（こちらは Flutter / Functions / 設定ファイル全般） |

表に出てくるドキュメント（`SPEC.md` / `HANDOFF.md` / `EVAL_REPORT.md` / `DECISIONS.md` / `DESIGN.md` 等）の役割と書き手・読み手は **§5.5 状態ファイル** にまとめてあります。

ステートレス起動: 全 agent は内部メモリを持たず、**`harness-state/` のファイル経由で状態をやり取り** します。だから「次の generator が前回の続きを書ける」「evaluator が generator と独立して採点できる」が成立します。

### 5.2 Skills と Slash Commands

| Slash command | 内部で動くもの | 用途 |
| --- | --- | --- |
| /spec | planner | SPEC 作成・更新 |
| /sprint | sprint-run skill（generator → evaluator → 記録） | 1 スプリント完全実行 |
| /evaluate | evaluator | 採点だけ走らせる |
| /code-review | code-reviewer | 差分の精密レビュー |
| /status | （表示） | SPEC / HANDOFF / EVAL\_REPORT サマリ |
| /metrics | sprints.jsonl 集計 | スプリント実績の定量表示 |

| Skill | 役割 |
| --- | --- |
| sprint-run | 実装 → 評価 → HANDOFF 更新 → sprints.jsonl 追記 |
| sprint-eval-flutter | analyze / test / iOS E2E / golden 更新 |
| flutter-riverpod-arch | Feature-First + Riverpod + Hooks 実装ガイド |
| firebase-functions-arch | Cloud Functions の薄い 2 層実装ガイド |
| firestore-schema | Firestore + rules + indexes の整合管理 |
| firebase-emulator | Emulator 統一起動・停止・テスト |
| harness-init | プロジェクト初期セットアップ |

### 5.3 Hooks（自動品質ゲート）

| イベント | スクリプト | 役割 |
| --- | --- | --- |
| PreToolUse(Bash) | pre-bash-safety | `rm -rf` / `git push --force` / `firebase deploy` 等をブロック |
| PreToolUse(Edit) | pre-protected-files | `analysis_options.yaml` 等の保護対象ファイル改竄をブロック |
| PostToolUse | post-dart-quality | `.dart` を自動 format → `dart analyze` 結果を文脈注入 |
| PostToolUse | post-ts-quality | `functions/` 配下の `.ts` を `eslint --fix` |
| PostToolUse | post-md-format | `.md` を `markdownlint --fix` → `prettier --write` |
| PostToolUse | post-pubspec-sync | `pubspec.yaml` 編集時に `flutter pub get` |
| Stop | stop-flutter-checks | `.dart` を触ったセッションのみ `flutter analyze` + `flutter test`（**センチネル方式**で空ターンは ~0.03 秒で即 exit） |
| Stop | stop-functions-checks | `.ts` を触ったセッションのみ `npm test` |
| UserPromptSubmit | user-prompt-status | `HANDOFF.md` 先頭 25 行 + `EVAL_REPORT.md` 4 軸サマリ（5 行）を毎プロンプト先頭に注入。**それ以外の `harness-state/*` は注入されない**（agent が必要時に Read） |

### 5.4 MCP サーバ

| MCP | 用途 | これが無かったら |
| --- | --- | --- |
| dart | analyze / format / test / pub | flutter コマンドを Bash 直叩き |
| marionette | iOS / Android E2E（VM Service attach） | xcodebuild ベースで build 30〜60s × N |
| xcodebuild | release 前のビルド検証のみ | — |
| mobile | OS ダイアログ等のフォールバック | — |
| firebase | emulator / rules / Firestore / Functions ログ | Admin SDK スクリプトを毎回書く |
| context7 | ライブラリ最新ドキュメント | 記憶ベースで API を書く（古い） |
| github | branch / PR / Issue 操作 | gh CLI |
| computer-use | Simulator のネイティブ通知許可等 | 手動操作 |

### 5.5 状態ファイル（`harness-state/`）

agent はステートレスに起動するため、**ファイル経由で次の agent / 次のセッションに状態を引き継ぐ**。`docs/` のような静的ドキュメントと違い、毎スプリント能動的に読み書きされます。

| ファイル | レイヤ | 役割 | 書き手 | 注入 |
| --- | --- | --- | --- | --- |
| HANDOFF.md | 実行 | 現スプリント / 直近完了 / 未達 | generator（毎スプリント上書き） | **先頭 25 行を毎プロンプト自動注入** |
| EVAL\_REPORT.md | 実行 | 1 スプリントの **採点結果 + 検証ログ + 受入条件チェック + 減点根拠 + cleanup 提案** をまとめた評価レポート | evaluator（毎評価で全置換） | **総合判定 + 4 軸サマリのみ自動注入** |
| SPEC.md | 仕様 | 機能リスト / 受入条件 / スプリント分割 | planner | 必要時に agent が Read |
| REQUIREMENTS.md | 設計 | ユーザー要件メモ | 人間 | 必要時に agent が Read |
| TECH\_STACK.md | 設計 | 技術選定とその理由 | 人間 + AI | 必要時に agent が Read |
| DB.md | 設計 | Firestore + Cloud Storage モデル | 人間 + AI | 必要時に agent が Read |
| API.md | 設計 | Functions API 契約（callable / Trigger） | 人間 + AI | 必要時に agent が Read |
| DESIGN.md | 設計 | デザイントークン + 画面ガイド + コンポーネント命名 | designer | 必要時に agent が Read |
| TESTING.md | 設計 | 4 層テスト戦略 + Mock 方針 + コマンド | 人間 + AI | 必要時に agent が Read |
| DECISIONS.md | 蓄積 | アーキ判断ログ（**追記のみ**、過去判断を消さない） | 全 agent | 必要時に agent が Read |
| logs/sprints.jsonl | メトリクス | 全スプリントの 1 行 JSON 履歴（append-only） | sprint-run skill | `/metrics` で集計表示 |
| .metrics/sprint-state.json | メトリクス | スプリント実行中の中間状態（retries 等） | sprint-run skill | skill 内部のみ |

**2 ファイルだけが特別扱い**: HANDOFF.md と EVAL\_REPORT.md だけが UserPromptSubmit hook で毎プロンプト先頭に注入されます（HANDOFF を 200 行超で埋めないようにする理由はここにあります）。

**追記 vs 上書き**: EVAL\_REPORT は毎評価で全置換 / HANDOFF は毎スプリント全置換 / DECISIONS は追記のみ / logs/sprints.jsonl は append-only です。

**関連姉妹**: `prototype/screens/*.html` は DESIGN.md の「適用例」を担う視覚仕様書。generator が UI を書くとき DESIGN.md（ルール）と prototype（適用例）の両方を読みます。

## 6. 開発フロー：`/sprint` の中身

人間が `/sprint` を叩くと、以下が一気通貫で走ります。

### 実際に出てくる PR の見た目

`/sprint` を 1 周回した結果、`sprint-run` skill が自動生成して出してくる PR は、テンプレートに **Sprint メトリクス（Verdict / Avg Score / 4 軸スコア / generator retries / stop hook blocks / tool 誤用 / code-reviewer iterations / ユーザー承認）+ iOS E2E 結果** が埋め込まれた状態で来ます。

![Sprint 3 の PR（merged）](https://static.zenn.studio/user-upload/ea10fd7b3e16-20260507.png)

## 7. 実績

**検証範囲**: 本レポートの数値・E2E 検証は **すべて iOS Simulator（iPhone 17 Pro）での実機確認** に基づく。Functionality / Code Quality / Architecture Fit / UX Quality の 4 軸採点も iOS を基準に行っています。

### 7.1 スプリント実績（`sprints.jsonl` の実値）

#### 評価軸の定義（4 基準・各 10 点 / 全項目 7 点以上で PASS）

| 軸 | 何を見るか | 減点される代表ケース |
| --- | --- | --- |
| **Functionality** | SPEC.md の受入条件をどれだけ満たすか。**ビルド成功 + テスト全パスは前提** | 受入条件未達、サイレントバグ（ラベルと挙動の不一致など）、受入条件に対する widget test の欠落 |
| **Code Quality** | `dart analyze` が warning 含めて 0 か。テストカバレッジ・命名・責務分離・重複 | analyze warning 残存、巨大関数、重複コード、code-reviewer の medium / high 指摘の残存 |
| **Architecture Fit** | Flutter = Feature-First + Riverpod + Hooks（`flutter-riverpod-arch` skill 準拠）/ Functions = 薄い 2 層 Endpoint + Wrapper（`firebase-functions-arch` skill 準拠） | provider 配置ミス、`@Riverpod(keepAlive)` の付け忘れ、新規パッケージ採用時の DECISIONS.md / TECH\_STACK.md 未反映 |
| **UX Quality** | iOS Simulator で実機動作するか。UI 崩れ・タップ反応・ローディング状態。`prototype/` 構造との一致と DESIGN.md トークン経由の表現 | iOS E2E 実機未走行、prototype との視覚乖離、**画面に出る固定色の直書き**（`Colors.white` 等で見た目が固定される箇所） |

加えて、副指標として：

* **retries**: generator が Stop hook（`flutter analyze` + `flutter test`）でブロックされて再実装した回数。**0 が理想**。多いほど初回出力の品質が低いです
* **tool 誤用**: MCP で済む処理を Bash 直叩きした件数（例: `mcp__dart__analyze_files` の代わりに `flutter analyze` を Bash で）。**evaluator が独立検出**

#### スプリント別実績

| Sprint | テーマ | 自動ループ※1 | 人間指示修正 | 合計（実測 + 推定） | Func / Code / Arch / UX | 平均 | retries | tool 誤用 | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 基盤・認証・テーマ | 30 分 | 30 分 | 60 分 | 8 / 7 / 9 / 8 | 8.00 | 3 | 0 | PASS |
| 2 | テーマ → 参考書生成 E2E環境構築 | 51 分 | 120 分（E2Eの環境構築込み） | 171 分 | 9 / 8 / 9 / 8 | 8.50 | 0 | 2 | PASS |
| 3 | Viewer ・ ライブラリ ・ 一覧 | 70 分 | 34 分 | 104 分 | 7 / 7 / 8 / 7 | 7.25 | 0 | 0 | PASS |

**※1 自動ループ**: `/sprint` を叩いてから sprint-run skill が完了するまでの wall-clock time（`sprints.jsonl` の `duration_sec`）。generator 実装 + hook の analyze/test + evaluator 採点 + reviewer 委譲 + リトライをすべて含みます。**人間が席を離れていても進む区間**。

Sprint 1 で retries が 3 回発生 → 2・3 では 0 回に収束。**ハーネスが学習材料（DECISIONS / HANDOFF / 過去 EVAL\_REPORT）を蓄積している** ことの定量シグナルです。

Sprint 2 の tool 誤用 2 件は evaluator が検出して DECISIONS.md に記録 → 以降同じ間違いは起きていません。

Sprint 3 の 4 軸減点内訳（実 EVAL\_REPORT より）:

* **Functionality 7/10**: 「すべて見る」タブ未切替 / `updatedAt` sort のサイレントバグ（ラベルと挙動の不一致）/ 削除・error 経路の widget test 欠落
* **Code Quality 7/10**: code-reviewer medium 指摘 6 件残存 / `_RecentBookItem` と `BookCard` の badge ロジック重複
* **Architecture Fit 8/10**: `bookContentProvider` family の `keepAlive` 漏れ / `flutter_markdown_plus` 採用の DECISIONS.md 未反映
* **UX Quality 7/10**: iOS E2E 実機検証が emulator 未起動で未完 / `Colors.white` `Colors.black` の固定色直書き（前景テキスト等で見た目が決まる箇所）/ 「すべて見る」リンクが動かない UX  
  いずれも cleanup として次スプリントに申し送ります。

### 7.2 効いた瞬間（事例 3 つ）

1. **E2E で本番ブロッカーを 4 件即時検出** — Sprint 3 の Marionette 走行中に Storage rules パス mismatch / manifest フィールド名違い / `keepAlive` 漏れ等を実機検出 → generator が即パッチ。widget test だけでは出なかった種類のバグです。
2. **採点バイアスの排除** — generator (sonnet) と evaluator (opus) を別 agent にしたことで、自分の実装を自分で OK と言わない構造になりました。Sprint 3 では evaluator が UX 7/10 と辛めに採点し、cleanup 6 件が次スプリントの申し送りに積まれました。
3. **Stop hook センチネル方式でコスト削減** — `.dart` を編集したターンだけ `flutter analyze` + `flutter test` を走らせ、ドキュメント編集だけのセッションは ~0.03 秒で抜ける。ハーネスが重くて使えなくなるを回避します。

### 7.3 ナレッジ蓄積：DECISIONS.md（13 件）

* D-001: Feature-First + Riverpod + Hooks
* D-005: `ThemeExtension<AppPalette>` で `isDark` 三項分岐をゼロ化
* D-009: iOS E2E を Marionette MCP + `flutter run` attach 方式へ移行（build 時間 30〜60s → 秒単位）
* D-010: embedding 生成を Sprint 7 に集約（Sprint 2b スコープ超過を防止）
* D-011: Sprint 2b と Sprint 4 の実装順序を入れ替え（UI を先に動かして E2E 足場化）

→ **「過去に何を決めたか」を agent も人間も同じファイルから読む** ので、引き継ぎコストがほぼゼロです。

## 8. 効いた設計判断

実装してみて「これが効いた」と感じたものに絞ります。

* **責務分離**: generator は実装だけ。evaluator は採点だけ。reviewer は指摘だけ。**1 agent = 1 役割** で認知負荷とバイアスを同時に減らします。
* **ステートレス agent + ファイル経由の引き継ぎ**: HANDOFF.md / SPEC.md / DECISIONS.md がすべて。agent は内部メモリを持たない → セッション跨ぎ・複数並列に強いです。
* **Stop hook センチネル方式**: 「やったときだけ走る」を `session_id` 単位で隔離。ハーネスを重くしないコツです。
* **prototype/ と DESIGN.md の二段構造**: DESIGN.md がルール（hex / spacing 値 / 命名規約）、`prototype/` がそれを各画面に適用した HTML 例。generator が UI を書くとき両方読むので、トークン値直書きが構造的に起きにくいです。

## 9. 考察：やってみて思ったこと

実際にハーネス型で 1 スプリントを `/sprint` から PR 作成まで一気通貫で回してみて、想定と違ったことや、運用上の現実解として見えてきたことを紹介します。

### 9.1 一気通貫で回しても、人間レビューは必須

ハーネス型で実装 → 評価 → PR 作成までを自動化できたが、人間レビューはまだ必要だと感じた。

* **設計通りではない実装**: SPEC.md で意図した責務分離と微妙にズレるコードが上がる（agent は「動けばよい」を選択しがち）
* **UI のおかしさ**: AppBar の二重表示、`RenderFlex overflowed by N pixels` の layout overflow、ローディング中のインジケータ位置ズレなど、**widget test も golden test もパスする**のに実機で見ると違和感があります

### 9.2 E2E テストは強力。シームレスな実行環境の整備が肝

最も投資対効果が高かったのは **E2E 環境の整備**。Sprint 3 で 4 件、その後のSprintでも複数の prod-blocker を実機 E2E で早期検出できました。これは widget test や golden test では絶対に出ない種類のバグです（Storage rules パス mismatch / Firestore field 名違い / OS 通知許可の dialog 経路 など）。

E2E をシームレスに回すために最低限必要だと感じた構成：

* **ローカルエミュレータ**: Firebase Emulator（auth / firestore / functions / storage）を `firebase-emulator` skill 経由で統一起動。実 API キーを使わずに E2E が回ります
* **シミュレータ操作 MCP**: Marionette MCP で Flutter widget tree を確実に特定（`ValueKey` ベースで tap / enter\_text）
* **ネイティブ dialog 操作**: computer-use で OS が出す通知許可・share sheet 等を screenshot + 座標クリック

#### この構成に至った経緯（試行錯誤）

最初は **`xcodebuild` MCP（XcodeBuildMCP）** で iOS Simulator のビルド・実行・UI 操作まで一気通貫させたかったが、実運用で詰まった：

* `xcodebuild` MCP は Xcode プロジェクトを `.app` にビルドして Simulator にインストールする経路は強いが、**`flutter run` で起動した debug build に attach して widget tree を操作することは出来ない**（VM Service への接続経路を持っていない）
* かといって `xcodebuild` でビルドした `.app` を `mobile` MCP / `xcodebuild` の UI 自動化で操作しても、**Flutter widget の `ValueKey` で確実に要素特定する手段が無く座標クリックに頼る** ことになり、UI 変更で簡単に壊れます
* ビルド時間も 30〜60 秒かかり、E2E 1 周のターンアラウンドが重いです

結論として **`xcodebuild` MCP を E2E の第一選択肢から外し**、代わりに以下のハイブリッドに切り替えた（DECISIONS.md `D-009` として記録）：

1. `flutter run -d <iOS Simulator> --debug` で起動して **VM Service URI を取得**
2. **Marionette MCP** で VM Service に attach → `ValueKey` ベースで widget tree を tap / enter\_text / scroll
3. OS が出すネイティブ dialog（通知許可・share sheet）だけ **computer-use** で screenshot + 座標クリック
4. `xcodebuild` MCP は **release 前のビルド検証専用**（archive / TestFlight 用 build の確認のみ）に格下げ

このハイブリッド方式は Sprint 3 の Viewer ナビゲーション E2E（13 step）と Sprint 3a の通知許可 dialog E2E で実運用パターンとして確立済みです。**「ビルドツール」と「UI 操作ツール」を分けて、それぞれ最適なものを選ぶ** のがコツでした。

### 9.3 アーキテクチャ skill は陳腐化リスクが高い

導入時は `flutter-riverpod-arch` `firebase-functions-arch` といった **アーキテクチャ skill（実装ガイド）** を整備したが、運用してみると問題が見えた：

* skill 内の記述（Riverpod の書き方・ディレクトリ構成）は **ライブラリのバージョン更新で陳腐化** します
* 文章で書いたガイドより、**実際に動くボイラプレートコード** の方が agent も人間も理解が早いです
* agent が skill を読んでも、結局 **既存コードのパターンを真似** して書くことが多いです

**実装ガイドを skill で書くより、コーディング規約に準拠したボイラプレート（template repository / scaffold）を先に作って、それをハーネス環境に投入する** 方が現実的です。

同じ理由で、**スプリント評価の「Architecture Fit」軸も不要かも**。code-reviewer の規約チェック + 実機 E2E + Functionality 採点で十分。Architecture Fit は「skill との整合度」を見ているだけで、ボイラプレートが正なら計測する意味が薄いです。

### 9.4 導入順序の現実解：hooks + MCP → harness-state → skill / agent

「最低構成からフル構成」と段階を切ったが、**実際にゼロから導入するならもっと薄く始める** のが現実的。

| ステップ | 入れるもの | 得られる価値 |
| --- | --- | --- |
| **1** | Hooks（pre-bash-safety / post-dart-quality / UserPromptSubmit）+ MCP（dart / firebase / marionette / computer-use / github / coderabbit） | **対話型のまま品質ゲートと E2E が手に入る** |
| **2** | `harness-state/` の HANDOFF.md / DECISIONS.md だけ先に作る | セッション跨ぎの文脈維持・判断履歴の蓄積 |
| **3** | sprint-run / sprint-eval-flutter skill を追加 | 評価コマンドの再利用、`/sprint` 一括実行 |
| **4** | planner / generator / evaluator subagent を追加 | 責務分離・採点バイアス排除 |
| **5** | reviewer 系 subagent + designer + フル構成 | 大規模プロジェクト向けの本格運用 |

**最初から subagent を多数仕込むと運用負荷が高い**。まず hooks と MCP で「対話型のまま品質を底上げ」して、慣れてきたら段階的に harness-state → skill → subagent と上に積んでいく方が、チームの学習曲線にも合っています。

### 9.5 ハーネスの定量評価そのものが難しい — 計測値 → 改善ループは今後の課題

今回 `sprints.jsonl` に retries / tool 誤用 / 4 軸スコア / wall-clock time / cleanup 件数といった指標を残したが、**ハーネスのどこを変えれば数値が改善されるか**が直接導けません。Hook を増やす？ DECISIONS.md の参照頻度を上げる？ subagent のプロンプトを書き直す？ どれが効くか事前に分かりません。

**今後やるべきこと（仮説）**:

* **A/B 的な切り替え検証**: 同じスプリントを「subagent あり / なし」「DECISIONS.md 注入あり / なし」で再実行して差分を見ます
* **ベンチマークタスクを定義**: 「決まったお題を Sprint 1 として実行 → スコア / 時間を記録」を、ハーネス改修ごとに繰り返します
* **Claude Agent SDK で独立した計測パイプラインを組む**: Claude Code CLI 固有の組み込み機構（内部 hook / session 管理 / 自動 prompt cache 等）が測定値に混入してしまう問題を切り離すため、**Claude Agent SDK** を直接叩いて agent / skill / hook を SDK レベルで再実装した別パイプラインを用意し、そこに本プロジェクトのハーネスを移植して同じベンチマークを走らせる。**Claude Code に依存しない環境下で計測する** ことで、「Claude Code 自体の進化」と「我々のハーネス設計」の貢献分を切り分けられます

**「ハーネスを作る」より「ハーネスを定量評価して改善する」方が難しい**、というのが Sprint 3 走り終えた段階での率直な感触です。

## 10. 持ち込みハーネス構成（採用チェックリスト）

「採用」列は打ち合わせ用の事前案。**◎ = 必須 / ○ = 推奨 / △ = 任意 / − = 不要 or 動作不可** の 4 段でマーキング。合意したら確定します。

### 10.1 Subagents（9 体）

| Agent | model | 役割 | 採用 |
| --- | --- | --- | --- |
| planner | opus | SPEC.md 作成・更新 | ◎ |
| generator | sonnet | 1 スプリント分の実装 | ◎ |
| evaluator | opus | E2E + 4 軸ルーブリック採点 | ◎ |
| code-reviewer | opus | コーディング規約 / 命名 / 重複の指摘 | ◎ |
| firestore-rules-reviewer | opus | firestore.rules / storage.rules 専任レビュー | ○ |
| security-reviewer | opus | Secrets / auth / 依存脆弱性 / git 履歴スキャン | ○ |
| designer | sonnet | DESIGN.md / prototype/ の更新 | △ |
| flutter-architect | opus | Riverpod / Hooks / Feature-First 設計判断 | △ |
| functions-architect | opus | Cloud Functions 設計判断 | △ |

### 10.2 Skills（7 種）

| Skill | 役割 | 採用 |
| --- | --- | --- |
| sprint-run | 実装 → 評価 → HANDOFF 更新 → sprints.jsonl 追記 | ◎ |
| sprint-eval-flutter | analyze / test / E2E / golden 更新 | ◎ |
| firestore-schema | Firestore + rules + indexes の整合管理 | ○ |
| firebase-emulator | Emulator 統一起動・停止・テスト | ○ |
| flutter-riverpod-arch | Feature-First + Riverpod + Hooks 実装ガイド | △ |
| firebase-functions-arch | Cloud Functions の薄い 2 層実装ガイド | △ |
| harness-init | プロジェクト初期セットアップ | △ |

### 10.3 Slash Commands（6 種）

| Command | 内部で動くもの | 用途 | 採用 |
| --- | --- | --- | --- |
| /spec | planner | SPEC 作成・更新 | ◎ |
| /sprint | sprint-run skill | 1 スプリント完全実行 | ◎ |
| /evaluate | evaluator | 採点だけ走らせる | ◎ |
| /code-review | code-reviewer | 差分の精密レビュー | ◎ |
| /status | （表示） | SPEC / HANDOFF / EVAL\_REPORT 表示 | ○ |
| /metrics | sprints.jsonl 集計 | スプリント実績の定量表示 | △ |

### 10.4 Hooks（9 種）

| イベント | スクリプト | 役割 | 採用 |
| --- | --- | --- | --- |
| UserPromptSubmit | user-prompt-status | `HANDOFF.md` 先頭 25 行 + `EVAL_REPORT.md` 4 軸サマリを毎プロンプト先頭に注入 | ◎ |
| PostToolUse | post-dart-quality | `.dart` 自動 format + analyze 文脈注入 | ◎ |
| Stop | stop-flutter-checks | Dart 触ったセッションのみ analyze + test（センチネル方式） | ○ （時間がかかるようなら外して、ワークフローで担保） |
| PreToolUse(Bash) | pre-bash-safety | `rm -rf` / force push 等をブロック | ◎ |
| PreToolUse(Edit) | pre-protected-files | `analysis_options.yaml` 等の保護 | ○ |
| PostToolUse | post-pubspec-sync | pubspec 編集後 `flutter pub get` | ○ |
| PostToolUse | post-md-format | `.md` を markdownlint + prettier | ◎ |
| PostToolUse | post-ts-quality | `functions/*.ts` に `eslint --fix` | ◎（Functions 採用時のみ） |
| Stop | stop-functions-checks | TS 触ったセッションのみ `npm test` | ○ （Functions 採用時のみ、時間がかかるようなら外して、ワークフローで担保） |

### 10.5 MCP サーバ（9 種）

| MCP | 用途 | 採用 |
| --- | --- | --- |
| dart | analyze / format / test / pub | ◎ |
| github | branch / PR / Issue 操作 | ○ |
| context7 | ライブラリ最新ドキュメント | ◎ |
| marionette | iOS / Android E2E（VM Service attach） | ◎ |
| firebase | emulator / rules / Firestore / Functions ログ | ◎ |
| computer-use | Simulator のネイティブ通知許可等 | ◎ |
| xcodebuild | release 前のビルド検証 | ◎ |
| mobile | OS ダイアログ等のフォールバック | -（起動はしたが設定が不十分だったのか使えなかった） |
| coderabbit | AI コードレビュー（GitHub 連携 / autofix） | ○（自前 code-reviewer subagent の代替・併用候補） |

### 10.6 状態ファイル（`harness-state/` ＋ 姉妹ディレクトリ）

| ファイル | レイヤ | 役割 | 書き手 | 注入 | 採用 |
| --- | --- | --- | --- | --- | --- |
| HANDOFF.md | 実行 | 現スプリント / 直近完了 / 未達 | generator（毎回上書き） | **先頭 25 行を毎プロンプト注入** | ◎ |
| EVAL\_REPORT.md | 実行 | 4 軸採点結果と E2E ログ | evaluator（毎回上書き） | **総合判定 + 4 軸サマリのみ注入** | ◎ |
| SPEC.md | 仕様 | 機能リスト / 受入条件 / スプリント分割 | planner | agent が必要時に Read | ◎ |
| DECISIONS.md | 蓄積 | アーキ判断ログ（**追記のみ**、過去判断を消さない） | 全 agent | agent が必要時に Read | ◎ |
| REQUIREMENTS.md | 設計 | ユーザー要件メモ | 人間 | agent が必要時に Read | ○ |
| TECH\_STACK.md | 設計 | 技術選定とその理由 | 人間 + AI | agent が必要時に Read | ○ |
| DB.md | 設計 | Firestore + Cloud Storage モデル | 人間 + AI | agent が必要時に Read | ○ |
| API.md | 設計 | Functions API 契約（callable / Trigger） | 人間 + AI | agent が必要時に Read | ○ |
| DESIGN.md | 設計 | デザイントークン + 画面ガイド + 命名 | designer | agent が必要時に Read | ○ |
| TESTING.md | 設計 | 4 層テスト戦略 + Mock 方針 + コマンド | 人間 + AI | agent が必要時に Read | ○ |
| prototype/screens/\*.html | 設計（姉妹） | DESIGN.md の各画面適用例（HTML/CSS） | designer | generator が UI 実装時に Read | △ |
| logs/sprints.jsonl | メトリクス | 全スプリントの 1 行 JSON 履歴（append-only） | sprint-run skill | `/metrics` で集計 | △ |
| .metrics/sprint-state.json | メトリクス | スプリント実行中の中間状態（retries 等） | sprint-run skill | skill 内部のみ | △ |

**2 ファイルだけが特別扱い**: HANDOFF と EVAL\_REPORT のみ UserPromptSubmit hook で毎プロンプト注入。残りは agent / 人間が能動的に Read します。

**書き込み規律**: 上書き（HANDOFF / EVAL\_REPORT）/ 追記のみ（DECISIONS）/ append-only（sprints.jsonl）の 3 系統。

**持ち込みのコア**: ◎マークの 4 ファイル（HANDOFF / EVAL\_REPORT / SPEC / DECISIONS）が運用上のコア。これだけでも「セッション跨ぎの文脈維持」と「採点履歴」が成立します。

## 11. まとめ

40h 規模の Flutter / Firebase アプリ開発を「対話型」ではなく「ハーネス型」で 3 スプリント走らせ、評価バイアスを排除しつつ E2E で本番ブロッカーを早期検出し、ナレッジを `DECISIONS.md` に蓄積する流れを確立しました。

ハーネスは初期構築コストがかかる一方、Sprint 2 以降は generator のリトライがゼロに収束するなど、回せば回すほど効果が積み上がる設計だと実感しています。一方で定量評価そのものはまだ未確立で、今後は Claude Agent SDK 等で独立したベンチマーク環境を組み、効果を切り分けて測ることが課題です。

## 参考
