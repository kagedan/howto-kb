---
id: "2025-12-05-日本語環境の-claude-code-opus-48-で-tool-call-が-malformed-01"
title: "日本語環境の Claude Code Opus 4.8 で tool call が malformed になる ― 公式 Issue と回避策まとめ"
url: "https://qiita.com/nomurasan/items/b4ff09cdb3cc2b2d6f17"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "VSCode", "qiita"]
date_published: "2025-12-05"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

# 日本語環境の Claude Code Opus 4.8 で tool call が malformed になる ― 公式 Issue と回避策まとめ

> 本記事は **AI(Claude Code) と並走して書いた** ものを、私(筆者)が **最終レビューして公開** しています。情報源(公式 Issue 5 件・国内ブログ 5 件)の収集とまとめは AI が一次対応し、**「英語思考 1 行」回避策の実機テスト** は私のセッションで実証しました(該当節に結果あり)。事実誤認や URL の正確性は人間が叩いて確認しています。

## TL;DR

- Claude Code (Opus 4.8) でツールコールが malformed になる症状は **既知のモデル本体側バグ**
- **VSCode 拡張のバグではない**(CLI / Desktop でも再現)
- **日本語環境では特に踏みやすい** との独立報告が複数
- 公式の回避策は **Opus 4.7 / Sonnet 4.6 への切り替え**
- 暫定 Tips: CLAUDE.md に `Think in English, interact with the user in Japanese.` の 1 行を入れる
- malformed なターンを含むセッションを **resume しない**(新規セッションで開く)

## 発端

別記事(ZennFes Spring 2026 リアルタイム参戦記)を Claude Code で並走執筆していた最中に、本症状が発生した:

- Opus 4.8 / Effort Max で運用していた
- 章が増えコンテキストが膨れ上がるにつれ、ツールコールの `malformed` エラーが頻発
- `Your tool call was malformed and could not be parsed.` で停止 → リトライしても収束しない
- Opus 4.7 に切り戻したら即解消

「自分の環境固有か?」「VSCode 拡張のバグか?」という疑問が湧いたので、公式 Issue と国内エンジニア記事を横断して調べた結果が本記事。

## 公式 GitHub Issue(`anthropics/claude-code`)

複数の独立した報告が同種の症状を扱っている:

| Issue | 内容 |
|---|---|
| [#63604](https://github.com/anthropics/claude-code/issues/63604) | Opus 4.8 が malformed な tool_use ブロックを繰り返し出力、レスポンス全体が破棄される (4.7 は正常) |
| [#64658](https://github.com/anthropics/claude-code/issues/64658) | Desktop app(Code タブ)1.9659.4 で「tool call could not be parsed (retry also failed)」が継続的に再現 |
| [#65230](https://github.com/anthropics/claude-code/issues/65230) | Opus 4.8 がツールコールを実行せず**コードフェンスとして出力**する |
| [#64129](https://github.com/anthropics/claude-code/issues/64129) | ツール使用後にレスポンスが表示されない(クォータは消費される) |
| [#62123](https://github.com/anthropics/claude-code/issues/62123) | API エラー「Model's tool call could not be parsed (retry also failed)」 |

### 症状の典型

- 約 **5〜10 ターン経過**で malformed tool_use が頻発し始める
- 元の tool_use ブロックではなく、**レガシーな XML テキスト形式**で吐かれることがある(パーサが解釈不能)
- リトライしても同じコンテキストを再生するだけで**収束しない**
- ツールコールがマークダウンコードフェンスとして出力される(=実行されない)

### 公式が示すワークアラウンド

- **Opus 4.7 または Sonnet 4.6 への切り替え**
- これだけで即座に解消する報告が多数

## 日本語エンジニアブログでの報告

国内でも複数の独立した記事が同じ症状を扱っている。**日本語環境ではさらに踏みやすい**という重要な追加情報あり:

| 出典 | 記事の核 |
|---|---|
| [Zenn / edhiblemeer 氏](https://zenn.dev/edhiblemeer/articles/claude-code-opus48-tool-corruption) | **「日本語環境で踏みやすい未修正バグ」** とタイトルで明示。長時間運用で全ツール呼び出しが壊れる症状の再現と回避策 |
| [note / kazu 氏](https://note.com/kazu_t/n/n4d6d730b1b43) | CLAUDE.md に **1 行追加するだけで落ち着いた** 報告(後述) |
| [SIOS Tech Lab](https://tech-lab.sios.jp/archives/52853) | 法人テックブログで「Opus 4.8 で `The model's tool call could not be parsed` が頻発している件」 |
| [wentz-design (2026-06)](https://wentz-design.com/post/claude-code-opus48-tool-call-2026-jun/) | 2026 年 6 月時点の不具合状況と回避策のまとめ |
| [Threads / hataraku_writer 氏](https://www.threads.com/@hataraku_writer/post/DZCdnhfEvgt/) | 「精度は高いんですがエラー多発でストレス」 SNS での実感共有 |

## 誘発条件 ― なぜ日本語で踏みやすいのか

複数の報告を突き合わせて分かった条件:

- **長い CJK(中日韓)引数** × **大きいコンテキスト** × **長考(Effort 高)**
- 長文編集・大量ツールコール・日本語のやり取りが重なる場面ほど発症率が上がる

つまり典型的な日本語ヘビーユーザー(長文 markdown を Edit ツール経由でガンガン直す、コンテキストに大量の日本語が乗る等)ほど踏みやすい。本記事の発端となった「リアルタイム並走執筆」も、まさにこの条件に合致していた。

## 追加で出ている症状パターン

- `stop_reason: tool_use` なのに **tool_use ブロックが無い**(矛盾した応答が返る)
- 構造化されるべきツール呼び出しが **`<invoke>` 形式のテキスト**として漏れ出す(本来 JSON で来るはずのものが XML テキストで漏れる)
- malformed なターンを含むセッションを **resume すると再発する**(=新規セッションで開き直すのが定石)

## 回避策まとめ

### 1. モデルを切り替える(根本対策)

最も確実。`/model` で即切り替え:

- **Opus 4.7** に戻す
- **Sonnet 4.6** に下げる(深い推論より速度・安定性が必要なとき)

### 2. CLAUDE.md に 1 行追加する(暫定 Tips)

note / kazu 氏の報告で頻発エラーが大幅改善した1行:

```
Think in English, interact with the user in Japanese.
```

「内部思考は英語、応答は日本語」という単純な指示。**なぜ効くかの推測**:

- バグの誘発条件が「**長い CJK 引数** × ツールコール生成」だった
- 内部思考(=ツールコールを組み立てる中間表現)を **英語に寄せる**ことで、CJK 引数の生成タイミングを **応答出力時のみ** に限定できる
- 結果として、ツールコール JSON のシリアライズ段階で日本語が混入する量が減り、malformed が起きにくくなる

公式パッチが来るまでの暫定回避策として、検証する価値がある Tips。

### 3. malformed セッションは resume しない

一度 malformed が出たセッションを resume すると、同じ壊れたコンテキストを再ロードして再発する。**新規セッション**で開き直すこと。

### 4. Effort を下げる

`Max` を使っていたら `High` 以下に下げる。`Ultra` で同様のバグが既知だったので、長文 × 高 Effort の組み合わせは避ける。

### 5. settings.json でモデルをピン留めする

`/model` の選択ピッカーで誤って 4.8 を選んでしまう事故を防ぐため、`~/.claude/settings.json` の `model` キーを `"claude-opus-4-7"` に固定する運用も有効。

## 自分の運用にどう組み込むか

筆者の運用は以下のように改修した:

- `~/.claude/settings.json` で `model: "claude-opus-4-7"` をピン留め
- `/model` で意図せず 4.8 に切り替わったら復旧スクリプトで戻す
- 長文編集を伴うセッションでは Opus 4.7 を**事実上のデフォルト**として扱う
- 新しい Opus が出ても、**実証されるまで本番運用には乗せない**

「最新 ≠ 安定」という当たり前の原則が、フロンティアモデルの世界でも依然として効くという話。BCP / レジリエンス観点からは、**動いている枯れた構成**を維持する判断のほうが正解になる場面がある。

## まとめ

| 質問 | 答え |
|---|---|
| 同じ状態の人いる? | **大勢いる**(公式 Issue 5 件 + 国内記事 5 件以上) |
| VSCode 拡張側のバグ? | **NO**(CLI / Desktop でも再現) |
| 日本語環境特有? | **特に踏みやすい**(独立報告複数) |
| 公式の回避策は? | **Opus 4.7 / Sonnet 4.6 へ切替** |
| 暫定 Tips は? | CLAUDE.md に英語思考 1 行 |
| いつ直る? | 2026-06 時点で未修正(本記事執筆時点) |

「自分だけが踏んでいるバグ」と感じたら、まずググる前に**英語と日本語の両方で同種の症状を検索する**こと。一次ソースを取りに行く習慣が、不要な不安を分解してくれる。

## 実証ログ ― 「英語思考 1 行」を自分で試してみた結果

本記事執筆中、回避策「2. CLAUDE.md に 1 行追加する」をその場で自分で検証した。

### 検証条件

- **日時**: 2026-06-20
- **モデル**: Opus 4.8 (`/model` で切り替え)
- **CLAUDE.md**: `Think in English, interact with the user in Japanese.` を先頭に追加
- **タスク**: 長文 markdown を Edit ツールで連続編集する場面(別記事の執筆を継続)
- **コンテキスト状態**: 既にかなり長いセッションを継続中(=最も malformed が出やすい条件)

### 結果

> やってみたけど駄目だったね。4.7 に戻した

**malformed エラーは出た**。1 行追加だけでは、長文 × 大量ツールコール × 累積コンテキストの組み合わせを防ぎきれなかった。

### この結果の解釈

**「効かない」と断定はできない**(あくまで n=1 の自己実験)。考えられる解釈:

- **誘発条件が強すぎた**: 既に長く膨れたコンテキストで試したため、最初から症状が出る寸前の状態だった可能性
- **症状の発症閾値を下げる効果はあったかも**: 完全予防ではなく「踏みづらくする」程度の効果なら、今回のような厳しい条件では破れる
- **CLAUDE.md の読み込みタイミング**: モデル切り替え時に CLAUDE.md を再読込しているかは要確認(=反映前のセッションでテストしていた可能性)
- **環境依存**: kazu 氏の環境では効いたが、別の使い方をする筆者環境では効かない、ということもあり得る

### 結論(暫定)

- **「効くこともあるが、長文 × ツールコール多発の本番運用では頼れない」** 程度に受け止めるのが安全
- **公式パッチが来るまでの**、根本対策はやはり **Opus 4.7 / Sonnet 4.6 への切り替え**
- 「英語思考 1 行」は試す価値はあるが、**過剰に期待しない**
- ただし **「このセッションで効かなかった ≠ 他セッションでも効かない」**。新規セッション・短いコンテキスト・別の使い方では効く可能性があるため、CLAUDE.md には**残置して継続検証**することにした

### 教訓

「ブログで 1 行で直った」報告は**鵜呑みにせず実測する**べき、というファクトチェックの基本が再確認できた。同じ条件で再現するとは限らない、という当たり前の事実。

「他者が報告した回避策が、自分の環境で同じく効くとは限らない」は、ソフトウェアエンジニアリングの全領域で繰り返し検証される普遍原理。本記事を読んでくれた方も、**自分の環境で実測する**ことを推奨する。

## 関連記事

- 本バグに気付いた経緯 → **メタ記事 / [ZennFes 2026 を聞きながら AI と一緒に記事を書くという体験](https://qiita.com/nomurasan/private/221f4ff6b9e168046ec3)**
- バグに遭遇したイベント全体のレポート → **本編 / [ZennFes Spring 2026 リアルタイム参戦記](https://qiita.com/nomurasan/private/7923ac6916a9664b8886)**
