---
id: "2026-06-06-claude-codeでツール呼び出しinvokeがただの文字で出て止まるバグの原因と直し方公式既知-01"
title: "Claude Codeでツール呼び出し(invoke)が“ただの文字”で出て止まるバグの原因と直し方【公式既知バグ】"
url: "https://qiita.com/sutaminajing40/items/0f07e9c280ad7ed38cd7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "qiita"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

# Claude Codeでツール呼び出し(invoke)が“ただの文字”で出て止まるバグの原因と直し方【公式既知バグ】

> 「Claude Code で作業してたら、急にツール呼び出しが実行されず、`<invoke ...>` みたいなタグが**そのまま文字として出力されて止まる**」——これ、あなたの設定ミスでもプロンプトのせいでもありません。**公式リポジトリに複数 issue が立っている既知バグ**です。原因と、確実に復帰する手順、再発を減らす予防策をまとめます。

![messageImage_1780744176355.jpg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3674840/af5a8e91-531f-4687-ba89-66ec2f246c3b.jpeg)


## TL;DR（先に結論）

- **症状**：ツール呼び出しが実行されず、`<invoke ...>` のXMLが生テキストで出てターンが止まる。
- **原因**：モデルがツール呼び出しを「構造化データ」ではなく「古い形式のXML文字列」として出力してしまう回帰バグ（2026年5月末〜）。一度壊れると履歴に残り、**壊れ方をコピーし続ける**（few-shot self-poisoning）。
- **❌ やってはいけない**：リトライ／「気をつけて」と再指示。→ 壊れたテンプレを増殖させて**悪化**します。
- **✅ 直し方**：`Esc` 2回 or `/rewind` で壊れる直前に戻す → ダメなら `/clear`（確実）。
- **✅ 予防**：区切りで `/clear`・`/compact`、巨大でXMLだらけの skill を途中で読み込まない、1Mコンテキストを切る。

## こんな症状で困っていませんか？

ツール（Bash、MCPツール、ブラウザ操作など）を呼ぼうとした瞬間、実行されずに次のようなテキストがそのまま画面に出て、**ターンが終わってしまう**：

```text
court
<invoke name="mcp__Claude_in_Chrome__computer">
<parameter name="action">scroll</parameter>
<parameter name="coordinate">[1000, 500]</parameter>
...
</invoke>
```

注目すべき特徴は3つ：

1. 先頭に `court` のような**意味不明な余計なトークン**が付く
2. 本来あるはずの `antml:` プレフィックスが**落ちている**
3. 全体を囲む `<function_calls>` ラッパーが**無い**、裸の `<invoke>`

この3点セットが、後述する公式 issue の説明と**完全に一致**します。

## これは自分のミスじゃない（公式の既知バグ）

`anthropics/claude-code` に同種の issue が複数立っています（[#64235](https://github.com/anthropics/claude-code/issues/64235), [#62344](https://github.com/anthropics/claude-code/issues/62344), [#64658](https://github.com/anthropics/claude-code/issues/64658) ほか）。Opus 4.8 でも再発報告があり、執筆時点で**完全修正には至っていません**（部分修正は出荷済み）。

## 原因

### ① 本体：tool_use が「テキスト」に化ける回帰バグ

本来、ツール呼び出しは `stop_reason: tool_use` の**構造化ブロック**として返るべきところ、モデルがそれを**レガシーな `<invoke>` XML“文字列”として直列化**してしまう。クライアント側は「ただのテキスト」と解釈するので、ツールは実行されずにターンが終わる＝**すぐ止まる**。2026年5月末頃から目立つようになった回帰バグです。

### ② 悪化メカニズム：few-shot self-poisoning（自己汚染）

ここが重要。**一度壊れたツール呼び出しが会話履歴に残ると、自己回帰生成で以後も同じ壊れ方をコピーし続けます。**

> だから **リトライや「気をつけて」「1個ずつ呼んで」という再指示は最悪手**。壊れたテンプレを履歴に増やし、セッション内では自力回復できなくなります。

報告では「4回連続リトライしても全部同じ壊れ方をした」「特定の文脈（連続するツール呼び出し・失敗後のリトライ）で安定的に再発した」とされています。

### 踏みやすい条件

- 長時間まわしている**長いセッション**
- **連続したツール呼び出し**
- **大きなファイル／ページ**をたくさん読み込んでいる
- `<result>` ブロックやヒアドキュメントなど**XML/マークアップ密度が高い skill** を読み込んだ
- 「**1Mコンテキスト + 強い思考**」の組み合わせ

> 💡 **ブラウザ自動操作（Claude in Chrome 等）は要注意。** 連続スクロール＋巨大なページテキスト読み込みで、上の条件をほぼ全部満たすため特に踏みやすいです。

## 直し方（詰まったときのリカバリー）

| 手順 | やること | 補足 |
|---|---|---|
| ① | **リトライしない** | 汚染を増やすだけ |
| ② | `Esc` を2回 or `/rewind` | 壊れる直前のチェックポイントに戻して続行 |
| ③ | `/clear` | 確実に効く唯一の復帰策。文脈を残したいなら先に `/compact` |

ポイントは「**壊れたターンを履歴から消してから続ける**」こと。②で直前に戻すだけで直ることが多く、ダメなら③でセッションをリセットします。

## 予防（再発を減らす）

- **タスクの区切りで `/clear` か `/compact` をこまめに。** セッションを肥大化させない。
- **巨大でXMLだらけの skill ファイルをセッション途中で読み込まない。**
- **1Mコンテキストを使っているなら200Kに戻す**のも有効：

```bash
# 1Mコンテキストを無効化（200Kに戻す）
export CLAUDE_CODE_DISABLE_1M_CONTEXT=1
```

> ※ 環境変数名は将来変わる可能性があります。最新の正確な名前は[公式ドキュメント](https://code.claude.com/docs/en/errors)で確認してください。

- 不要な場面は `/effort` を下げる（部分的な緩和）。
- **Claude Code を最新版に更新**（部分修正が入っています）。

### 諸説あり：日本語マルチバイト密度の影響（確証は弱め）

「日本語などマルチバイト文字の密度が高いと崩れやすい」という説もあり、緩和として `CLAUDE.md` に次を足す方法が出回っています。

```text
Think in English, respond in Japanese.
```

ただしこれは一次ソースの根本原因（回帰バグ／self-poisoning）ほど確証はありません。**まずは上のリカバリー＋予防を徹底**し、これは保険程度に試すのがおすすめです。

## まとめ

- ツール呼び出しが生テキストで出て止まるのは、**あなたのせいではなく公式の既知バグ**。
- **リトライは厳禁**。`Esc`2回 / `/rewind` → ダメなら `/clear`。
- 長いセッション・XML密な文脈・1M+強思考で踏みやすい。**こまめにリセット**が効く。

同じ症状でハマっている人の助けになれば幸いです。

## 出典

- [anthropics/claude-code #64235 — Regression: tool_use block absent / legacy `<invoke>` XML text](https://github.com/anthropics/claude-code/issues/64235)
- [anthropics/claude-code #62344 — Malformed tool calls due to in-context few-shot poisoning](https://github.com/anthropics/claude-code/issues/62344)
- [anthropics/claude-code #64658 — Opus 4.8 でも再発](https://github.com/anthropics/claude-code/issues/64658)
- [anthropics/claude-code #63875 — Recurring "could not be parsed" interrupts sessions](https://github.com/anthropics/claude-code/issues/63875)
- [Claude Code Error reference（/rewind・Esc・/clear）](https://code.claude.com/docs/en/errors)
