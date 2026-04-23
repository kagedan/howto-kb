---
id: "2026-03-17-codexにいつの間にか入っていたopenai-docs-skillの中身を読み解く-01"
title: "Codexにいつの間にか入っていたopenai-docs skillの中身を読み解く"
url: "https://zenn.dev/purple_matsu1/articles/20260317-codex-openai-docs-skill"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "OpenAI", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

`.codex/skills/.system` にいつの間にか `openai-docs` が入っていたので、中身を調査しました。

Claude Code には以前から `/claude-api` という同様の skill がありましたが、同じ考え方が Codex にも来ていたようです。その中身を読み解きながら「skill とは何をしているのか」を整理してみます。

## openai-docs skill の中身

`openai-docs` skill のディレクトリを開いてみると、OpenAI のドキュメント本体は一切入っていません。

じゃあ何が入っているのか。中身はこの 3 つです。

1. `SKILL.md`: 実行ルール（何を、どの順番で、どう参照するか）
2. `agents/openai.yaml`: UI 定義と MCP サーバーへの依存宣言
3. `references/*.md`: モデル選定やアップグレードの補助資料

つまり skill の正体は、ドキュメントそのものではなく「ドキュメントの調べ方と使い方を定めた運用ポリシー」です。

## `SKILL.md` には何が書いてあるのか

`SKILL.md` の中身を読むと、かなり細かい運用ルールが書かれています。特に重要なのはこのあたりです。

### まず公式 docs を引け

OpenAI 関連の質問が来たとき、Codex がどこから情報を取るかの順番が明確に決まっています。

1. `developers.openai.com` の MCP サーバーで検索・取得
2. `references/` 配下のローカル Markdown
3. `developers.openai.com` / `platform.openai.com` に限定した Web 検索

ふつうの Web 検索を先にやらせない。「OpenAI のことは、まず OpenAI 公式 docs MCP で引け」という強い統制です。

### MCP ツールの使い分けも決まっている

MCP サーバーへのアクセスも、雑に一覧を舐めるのではなく、役割が分かれています。

* `search_openai_docs`: 関連ページを探すための入口
* `fetch_openai_doc`: 必要なページやセクションを正確に取り出す
* `list_openai_docs`: クエリが曖昧で、まずページ一覧を眺めたいときだけ使う

まず検索して、必要箇所だけ fetch する。この流れが skill によって固定されています。

### 補助資料はあくまで補助

`references/` には 3 つのファイルが入っています。

* `latest-model.md`: 最新モデル選定の早見表
* `upgrading-to-gpt-5p4.md`: GPT-5.4 へのアップグレード判断ガイド
* `gpt-5p4-prompting-guide.md`: GPT-5.4 向けのプロンプト移行ガイド

ただし、これらはあくまで「helper context」という扱いです。最新の OpenAI docs と矛盾したら docs が勝つ。ローカルの補助資料は使うけれど、古くなっていても最終回答で誤案内しにくい構造になっています。

## MCP がなくても自己修復する

ちょっと驚いたのが、docs MCP サーバーが入っていない場合の復旧手順まで skill に書かれていることです。

1. まず自分で `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp` を実行する
2. 権限で失敗したら昇格して再実行
3. それでも無理ならユーザーに依頼
4. Codex 再起動を促す
5. 再起動後に docs 検索をやり直す

単なる検索ガイドではなく、「MCP がない環境でも docs-first に戻すための自己修復手順」まで含んでいるんです。

## Claude Code でいうと、どの機能にあたる？

ここが少しややこしいので、図で整理します。

Claude Code には、似たような仕組みが複数のレイヤーに存在しています。

それぞれの対応関係はこんな感じです。

* Built-in docs access: Claude Code は自分自身のドキュメントに常時アクセスできる。これは製品機能として組み込まれている
* `@server:protocol://resource/path`: MCP resource を会話に直接差し込む汎用の参照機構
* `/claude-api` skill: Anthropic / Claude API 向けの専用ポリシー。`openai-docs` に一番近い立ち位置

`openai-docs` は、この `/claude-api` と同じレイヤーにあるものが Codex 側にも来た、ということです。

## `@resource` と skill の違い

ここも混乱しやすいところです。「MCP resource を参照する」のと「skill を使う」のは何が違うのか。

短く言うと、こういう違いです。

* `@resource`: 「このページを読んでから答えて」
* skill: 「OpenAI の件なら、まず公式 docs を検索して、必要箇所だけ確認して、補助資料は補助としてだけ使って答えて」

`@resource` は入力チャネル、skill は運用ポリシー。両者は競合ではなく補完関係です。

使い分けの目安も書いておきます。

* すでに参照したい docs resource が分かっているなら → `@resource`
* 何を参照すべきかまだ曖昧なら → skill
* 公式 docs を source of truth にして調査フローごと固定したいなら → skill
* 既知の 1 ページを会話に注入したいなら → `@resource`

## いつから使えるの？

upstream の `openai/skills` リポジトリでは、`openai-docs` は 2026-03-05 のコミット `80f18ba`（`Add OpenAI Docs skill (#219)`）で追加されています。

`.codex/skills/.system/` 配下の skill はプリインストールされる仕組みなので、この commit を取り込んだ Codex のバージョンから自動的に入ります。少なくとも `codex-cli 0.115.0` には含まれていることを確認しました。

ちなみに Claude Code 側では、`/claude-api` skill がバージョン `2.1.69` で追加、MCP resource reference（`@server:protocol://path` 形式）は 2025-06-18 に導入されています。

## skill の設計思想から学べること

この `openai-docs` skill の本質は、「OpenAI docs を読む機能」ではありません。

本質は 3 つです。

1. 情報源の優先順位を固定する — 公式 docs を最優先にする
2. ローカル補助資料を過信しない — 便利だけど最新 docs と矛盾したら docs が勝つ
3. fallback の範囲を制限する — docs が取れなくても、公式ドメイン以外には広げない

かなり保守的ですが、その分だけ誤案内しにくい設計です。

これは自分で skill を作るときにも参考になる考え方ではないでしょうか。「何ができるか」ではなく「どういう順番で、どこまでを信頼して、どこから先は行かないか」を決める。

## 参考リンク
