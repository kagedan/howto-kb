---
id: "2026-06-05-claude-code-effort-ultracode-と-codex-goal-を医療ai開発で-01"
title: "Claude Code /effort ultracode と Codex /goal を医療AI開発で使い分ける"
url: "https://zenn.dev/taichiendoh/articles/ccb221b551703a"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "zenn"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

## この記事について

[前回記事](https://zenn.dev/taichiendoh/articles/ab5b0f005c447a)では医療現場で生成AIを使うときの法律と技術を整理しました。

今回はその続編として、**実際に医療AIを開発するときに、どのAIコーディングツールをどう使い分けるか**を整理します。特に2026年5月公開の **`/effort ultracode`** に踏み込みます。

## 役割分担の全体像

| ツール | 役割 |
| --- | --- |
| **Claude Code workflow** | 大規模調査・分解・並列処理する **設計係** |
| **Codex /goal** | 完成条件に向けた実装・修正・テストの **実装係** |
| **Claude Code /effort ultracode** | 設計+実装を自動オーケストレーションする **自走モード** |

医療AI開発のように「設計を慎重に考えるべき」領域では、**段階的な workflow → /goal** のほうが安定します。

## `/effort ultracode` とは

ultracode は2つの機能を組み合わせたセッション設定：

1. **xhigh effort**：推論深度を最大近くまで上げる
2. **Dynamic Workflows orchestration**：Claude が自動で workflow を組む

```
# セッション全体に適用
/effort ultracode

# 通常作業に戻す（コスト爆発防止）
/effort high
```

**必要バージョン**：Claude Code v2.1.154 以上

```
npm install -g @anthropic-ai/claude-code@latest
```

### effort レベルの使い分け

| レベル | 用途 |
| --- | --- |
| medium | 軽い編集・Q&A |
| high | 通常のコーディング |
| xhigh | 難しいデバッグ・設計 |
| ultracode | 大規模・複数フェーズ・自律進行 |

**ultracode はトークン消費が大きい**ので、大仕事だけにオンにして、終わったら必ず `/effort high` に戻す運用が必須です。

## workflow / /goal 以外のおすすめコマンド

### Claude Code（特に使うもの10個）

| コマンド | 用途 |
| --- | --- |
| `/init` | プロジェクト初期化（CLAUDE.md 生成） |
| `/memory` | CLAUDE.md 編集（プロジェクト方針を記憶） |
| `/clear` | 会話履歴をリセット |
| `/compact` | 会話を圧縮（コンテキスト80%超えたら） |
| `/cost` | トークン消費の確認（ultracode 時必須） |
| `/review` | コードレビュー |
| `/permissions` | 権限管理 |
| `/effort` | 推論深度切替 |
| `@パス` | ファイル参照（Tab補完OK） |
| `! コマンド` | シェル直接実行 |

### Codex（特に使うもの5個）

| コマンド | 用途 |
| --- | --- |
| `/plan` | 計画モード（/goal の前段） |
| `/goal` | ゴール設定（完了条件付き作業指示） |
| `/diff` | 差分確認 |
| `/review` | コードレビュー |
| `/permissions` | 権限設定（**`danger-full-access`は厳禁**） |

## 医療AI開発の推奨フロー

### 1. CLAUDE.md に医療AI制約を書く

```
# Medical AI Development Constraints
- 患者情報を含むデータは絶対に外部APIに送らない
- 仮名化と匿名化を区別すること
- DBスキーマを勝手に変えない
- 認証ロジックを勝手に変えない
- ログに患者識別情報を出力しない
```

### 2. 調査フェーズ（Claude Code）

```
/effort xhigh

Run a workflow to analyze this medical AI codebase.

Scope:
- src/dicom/**
- src/api/**

Output:
- Files handling patient information
- Risk points for 3省2GL compliance
- SPEC.md draft
- GOAL.md draft

Do not modify any files
```

最後の **`Do not modify any files`** が安全装置です。

### 3. GOAL.md を作成

```
## Goal
DICOM画像の自動分類機能を追加する

## Scope
Modify only:
- src/dicom/classifier/**
- src/api/dicom/classify/**

## Constraints
- 患者識別情報をログに出力しない
- 既存の認証フローを変更しない
- 新しい外部依存を追加しない

## Done when
- DICOM ファイルから画像分類ができる
- npm test passes (coverage 80%以上)
- ログに患者識別情報が含まれていないテストが通る
```

### 4. Codex /goal で実装

```
/goal Implement the feature described in GOAL.md.

Before finishing, run:
- npm test
- npm run lint

Stop only when all Done when conditions are satisfied.
```

### 5. 人間がレビュー

必ず以下を確認：

* PHI（保護対象保健情報）の漏えいがないか
* 関係ないファイルが変更されていないか
* 認証・権限まわりを壊していないか
* 新しい依存パッケージが追加されていないか

## ハマる5つの落とし穴

1. **個人プランのAIに患者情報を送る** → 企Q-26 違反。業務契約+ZDR必須
2. **いきなり編集させる** → `Do not modify any files` で調査だけにする
3. **スコープを絞らない** → 「アプリ全体」はNG、ディレクトリ単位で限定
4. **完了条件を書かない** → `Done when:` を必ず明示
5. **レビューを省く** → 医療AI開発では人間の最終レビュー必須

## まとめ

```
Claude Code workflow = 設計係
Codex /goal = 実装係
/effort ultracode = 両方を兼ねる自走モード
```

**医療AI開発では「AIに丸投げ」は厳禁**。要配慮個人情報・SaMD・3省2ガイドラインの観点で、人間のレビューを必ず入れる設計にしてください。

AIに任せる前の整理が雑だと、AI開発は破綻します。`workflow` で整理して、`SPEC.md` と `GOAL.md` を作って、`/goal` に渡す。あるいは `/effort ultracode` で自律オーケストレーションを使う。

人間が「目的を決め、制約を与え、最後にレビューする」構造は揺るがない。これが、医療AI開発における現実的なAIエージェント活用です。

## 参考リンク

## 免責

* AI開発ツールは進化が速いので、必ず公式ドキュメントを参照してください
* 医療AI業務利用は、情報セキュリティ部門・顧問弁護士と相談したうえで導入してください
* 筆者は本記事の内容を業務利用したことに起因するいかなる損害も負いません

## 著者プロフィール

臨床工学技士 × AIエンジニア / 11年間、病院の医療機器の現場に立ち続けてきました。  
いまはAIエンジニアとしても活動しながら、酪農学園大学の研究生として論文博士の取得を目指しています。  
研究テーマの主軸は遺伝子医療の未来。そのうえで、医療現場と地続きにある病院のIT・サイバーセキュリティ・医療AI導入についても、現場で起きている課題と一次情報を突き合わせながら調べ続けています。

質問・誤りの指摘・「うちのチームではこう使っている」という事例の共有、いつでも歓迎します。

X：[@endoh\_taichi](https://x.com/endoh_taichi)  
Qiita：[@TaichiEndoh](https://qiita.com/TaichiEndoh)
