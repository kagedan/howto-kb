---
id: "2026-06-19-claude-code-をハブにしてdbt-の仕事だけ-dbt-wizard-に任せてみた-01"
title: "Claude Code をハブにして、dbt の仕事だけ dbt Wizard に任せてみた"
url: "https://zenn.dev/usen_ict/articles/12bd61ad5ab606"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

!

dbt Labs の **dbt Wizard CLI**（Beta）を、Claude Code の「乗り換え先」ではなく **Claude Code から呼び出す専門エージェント**として触ってみた話です。

実際にローカルで動かすところまでやったら、`headless 実行` も `Claude Code → dbt Wizard のルーティング` もすんなり繋がりました。  
ハマりどころ（BYOK 認証まわり）も含めてメモします。

![Claude Code をハブに、dbt のタスクだけ dbt Wizard に委譲するイメージ](https://static.zenn.studio/user-upload/88da040b6c5a-20260619.png)

## dbt Wizard、出ましたね

dbt Labs から **dbt Wizard CLI**（現在 Beta）が出ました。みなさんもう触りました？

公式ドキュメントの説明はこう。

> The dbt Wizard CLI helps teams ship higher-quality dbt changes faster and with less risk. Built for governed data development in dbt, it understands your project, routes to the right dbt tools, validates changes, and shows how logic evolves from your local machine.
>
> — [About dbt Wizard CLI（dbt Docs）](https://docs.getdbt.com/docs/dbt-ai/about-dbt-wizard-cli)

ざっくり訳すと「**dbt の変更を、より速く・低リスク・高品質に出すための CLI。プロジェクトを理解して適切な dbt ツールに振り分け、変更を検証し、ロジックの変化をローカルで見せてくれる**」。

つまり **dbt 専用の AI エージェント CLI** です。普通のコーディング AI と違って **dbt のメタデータ（lineage / tests / contracts / semantic）をネイティブに理解した上で**、モデルの調査・リファクタ・失敗ランのデバッグ・PR レビューをやってくれます。  
BYOK（自分の API キー持ち込み）で Anthropic / OpenAI / Snowflake Cortex など好きなモデルを裏に置けます。

![wizard を起動するとこの TUI。/model でモデル切替、/status で承認設定や使用量を確認できる](https://static.zenn.studio/user-upload/b6aa605f353f-20260619.png)

で、こう思った人も多いはず。

> 「Codex でいいじゃん」「Claude（Code）でいいじゃん」

でも、**dbt のことは dbt 専用エージェントが一番詳しい**のだろうなとも思います。  
なので乗り換えるんじゃなくて、

> **Claude Code をハブにして、dbt のときだけ dbt Wizard に投げる（＝専門エージェントとしてルーティングする）**

ほうがいいんじゃないか、と思って試してみました。

実はこの構図、Snowflake が `snowflake-cortex-code` プラグインで先にやっています（Claude Code → Cortex Code に自動で振り分ける）。同じことを dbt Wizard でやりたい、という今回の話。発想の元はこの記事です。

<https://dev.classmethod.jp/articles/snowflake-cortex-code-plugin-claude-code/>

ということで、まず**触ってみる**ところから。

## 触ってみる

インストールは公式どおり。`wizard` と `dbt-wizard` の両方のコマンドが入ります。

```
curl -fsSL https://public.cdn.getdbt.com/dbt-wizard/install/install-wizard.sh | sh
wizard --version    # dbt-wizard 0.1.1-beta.69
```

`wizard exec --help` を見ると、Usage が **`codex exec`** になっていて、サブコマンドやフラグ構成も Codex とほぼ一致していました。少なくとも**現行実装は Codex CLI 系のコードベースを利用しているように見えます**（ラッパーなのか fork なのかまでは未確認）。これが後半で効いてきます。

非対話で使うサブコマンドはこの2つ。

* `wizard exec [PROMPT]` … エージェントを headless 実行
* `wizard review` … PR / 差分レビュー専用（`--uncommitted` / `--base` など）

## ハマった：頭脳（LLM）どうする問題

dbt Wizard は AI エージェントなので、頭脳の LLM が要ります。

まず `wizard login`（dbt Platform 経由）でマネージドのモデルを使おうとしたら、**私の環境では** hosted gateway が使えず 403（組織のメールドメインが未認可）。

```
ERROR: 403 Forbidden: Account email domain is not authorized for this gateway
```

この 403 は Beta の参加状況・組織設定・dbt Platform の権限などに依存しそうで、`login` だけで使える環境も多いはずです。私の環境では使えなかったので **BYOK（自分の API キー持ち込み）** に切り替えました。

```
export ANTHROPIC_API_KEY="sk-ant-..."
wizard providers enable anthropic
```

使うモデルは `~/.dbt/wizard/config.toml` で指定します。

```
# ~/.dbt/wizard/config.toml
model = "anthropic/claude-sonnet-4-6"
```

!

**`model` に書く値は任意の文字列ではなく、`<provider>/<モデルID>` 形式**です（例: `anthropic/claude-sonnet-4-6`）。  
使えるIDは dbt Wizard 側のモデルカタログ（ローカル LiteLLM の定義）に載っているものだけなので、**自分の環境で確認してから書く**のが確実です。

```
# 有効なモデルIDを確認する
wizard providers show anthropic   # その provider の "id" 一覧
wizard debug models               # 全モデルカタログ（slug 一覧）
```

たとえば手元の `providers show anthropic` ではこう出ました（執筆時点 v0.1.1-beta.69）。

```
anthropic/claude-sonnet-4-6
anthropic/claude-opus-4-7
anthropic/claude-haiku-4-5
```

provider を変えれば prefix も変わります（`snowflake/claude-sonnet-4-6`、`bedrock/...` など）。Beta なのでモデル名は更新される前提で、ハードコードせず `show` / `debug models` で都度確認するのがおすすめです。

ただこれだけだと `wizard exec` がまだ hosted ゲートウェイを見にいって繋がらない。

headless だと**ローカルの LiteLLM サイドカーに切り替わらない**のが原因で、環境変数で起こします。

```
DBT_WIZARD_START_LOCAL_LITELLM=1 wizard exec --sandbox read-only "..."
```

これで `127.0.0.1` のローカル LiteLLM 経由になって BYOK が効きました。

## 動いた

```
$ echo "「1+1」の答えだけ返して" \
    | DBT_WIZARD_START_LOCAL_LITELLM=1 wizard exec --sandbox read-only -
user  「1+1」の答えだけ返して
wizard  2          ← ちゃんと返ってきた
```

dbt プロジェクトに対して read-only で動かすと、エージェントが自分で `find` を打ってリポジトリを探索しはじめます（`models/staging` が無いと気づいて `models/` を見直す、みたいな agentic な動き）。  
`--sandbox read-only` なので読み取りはできても書き込みは弾かれる。**安全境界がネイティブで効く**のが良いところ。

## dbt らしい仕事をさせてみる

「1+1」だけだと "ただの CLI ラッパー" に見えるので、もう少し dbt らしいお題を。  
read-only のまま「marts のモデルを1つ incremental 化するならどう変える？（**ファイルは編集しない**）」と聞いてみます。

```
# 検証済み 2026-06-19（read-only / 編集なし。-c dbt_target=dev は環境に合わせて）
wizard exec --sandbox read-only --no-validation -c dbt_target=dev \
  "models/marts のモデルを1つ incremental に書き換えるなら？ config と is_incremental() の要点を、ファイルは編集せず提案して"
```

エージェントは `models/marts` を覗いてモデルを1つ選び、こんな提案を返しました（**モデル名・カラム名は一般化しています**）。

```
-- (1) config を incremental に
{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

-- (2) is_incremental() で増分だけ取る
SELECT order_id, customer_id, order_amount, updated_at
FROM {{ ref('stg_orders') }}
WHERE 1=1
{% if is_incremental() %}
  AND updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

`unique_key` の指定、`is_incremental()` の中で `{{ this }}` の最大 `updated_at` を見て増分だけ取る、初回はフルリフレッシュ——と、**dbt の incremental の定石を押さえた提案**でした。

### ただの grep じゃなく、dbt メタデータエンジンを持っている

別のお題（「影響範囲の大きいモデルは？」）を投げたときが面白くて、エージェントは `ref()` を grep するのではなく **`dbt_index` という専用ツール（dbt メタデータの検索）** を呼びにいきました。さらに**起動時にプロジェクトを compile** しようとし、それが `target 'prod' not found in profile 'snowflake'`（デフォルト target 未設定）で失敗すると、**「compile が落ちたから dbt\_index が空なんだ。`dbt_project.yml` と `profiles.yml` を見よう」と自分で dbt 文脈のデバッグを始めました**。

汎用コーディング AI との差はここで、**dbt のメタデータ・compile・設定を前提に動く**のが実地で見えます。

## ついでに：Claude Code からルーティングする

ここまでで「dbt Wizard を headless で呼べる」のは確認できたので、本題の **Claude Code → dbt Wizard 振り分け**。`snowflake-cortex-code` の仕組みをほぼそのまま真似ます。

### ① どっちに投げるか判定する

プロンプトに dbt っぽい語があれば Wizard、無ければ Claude Code、という素朴なスコアリング。

```
DBT_INDICATORS_STRONG = ["dbt", "marts", "staging", "ref(", "state:modified", ...]
CLAUDE_CODE_INDICATORS = ["github pr", "terraform", "edit file", "cortex", ...]

def route(prompt):
    p = prompt.lower()
    w = sum(3 if i == "dbt" else 2 for i in DBT_INDICATORS_STRONG if i in p)
    c = sum(2 for i in CLAUDE_CODE_INDICATORS if i in p)
    if w + c == 0:
        return "claude"            # 迷ったら安全側
    return "wizard" if w > c else "claude"
```

実際に投げた結果：

| プロンプト | 判定 |
| --- | --- |
| 「marts のフィルタを直して」 | **wizard** |
| 「state:modified+ だけ build して」 | **wizard** |
| 「Terraform plan が変」 | claude |
| 「この PR レビューして」 | claude（dbt 文脈語が無いと wizard に行かない＝境界ケース） |

最後の境界ケースが地味に大事で、`wizard review` を確実に呼びたいなら「dbt の PR をレビュー」のように一言添える運用が無難でした。

### ② envelope は `--sandbox` に乗せるだけ

`snowflake-cortex-code` では権限制御を自前で書いていましたが、dbt Wizard は Codex ベースなので**ネイティブの `--sandbox`** がそのまま envelope になります。

| envelope | `--sandbox` |
| --- | --- |
| RO（探索・レビュー） | `read-only` |
| RW（dev / CI） | `workspace-write` |
| PROD（本番・要確認） | `danger-full-access` |

なので Wizard を呼ぶラッパーはこれだけ：

```
ENVELOPE_TO_SANDBOX = {"RO": "read-only", "RW": "workspace-write", "PROD": "danger-full-access"}

def build(prompt, envelope, cwd):
    return ["wizard", "exec", "--sandbox", ENVELOPE_TO_SANDBOX[envelope], "-C", cwd, prompt]
```

あとは Claude Code の `UserPromptSubmit` hook に「判定 → Wizard 実行」を仕込めば、いつもどおり Claude Code に話しかけるだけで裏で振り分ける、という流れになります（`snowflake-cortex-code` と同じやり方）。

## 触ってて気づいた小ネタ

* **`~/.claude/skills/` を読みにきた**：手元では dbt Wizard が Claude Code の skill ディレクトリを読み込もうとしました（Codex 系の skill 探索に含まれるようです）。資産を共有できて便利な反面、`SKILL.md` の frontmatter にコロンがあると YAML パーサが弾いてエラーログが出ます（実行は続行）。クォートで回避。
* **`wizard mcp-server`**：Wizard を MCP サーバ化して Claude Code から直結する道もあります。router で shell 経由 dispatch する以外の選択肢。
* **Snowflake Cortex を BYOK provider にすると、頭脳が本物の Claude**（`snowflake/claude-sonnet-4-6` 等）。データを社内に留めたまま Claude を使えます。ただし Snowflake の PAT は**ネットワークポリシー必須**なので、そこは別途整える必要あり。

## まとめ

* **dbt Wizard は "dbt を分かっている" エージェント**。dbt メタデータエンジン（`dbt_index`）を内蔵し、プロジェクトを compile してから動き、incremental の定石もきちんと押さえてくる。汎用 AI とは一線を画す dbt 特化ぶりが頼もしい
* 中身が Codex CLI ベースなので **envelope はネイティブ `--sandbox`** に乗せられて実装が軽い。`wizard review` で CI のレビューまで一気通貫なのも嬉しい
* 認証まわりだけ少しコツが要る（組織ドメインで 403 のときは BYOK、headless BYOK は `DBT_WIZARD_START_LOCAL_LITELLM=1`）。Beta なのでこの辺りは今後どんどん磨かれていくはず
* Claude Code からのルーティングは `snowflake-cortex-code` のミラーで最短。3つ目以降の専門エージェントも同じパターンで足せる

Beta の段階でも、dbt のメタデータや compile を前提に動く様子はかなり印象的でした。そのうえで **「Claude Code + dbt Wizard」という組み合わせ**には確かな手応えを感じました。dbt に閉じた仕事は dbt 専用エージェントに、それ以外は Claude Code に——と自然に分担が決まるのがいいところです。

「1つの最強エージェントが全部やる」より、**Claude Code をハブにして専門エージェントを足していく**。dbt Wizard はその最初の相棒として、これからの伸びが楽しみです。

## 参考リンク
