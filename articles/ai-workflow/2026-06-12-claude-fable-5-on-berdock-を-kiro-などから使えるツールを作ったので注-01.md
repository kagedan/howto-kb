---
id: "2026-06-12-claude-fable-5-on-berdock-を-kiro-などから使えるツールを作ったので注-01"
title: "Claude Fable 5 on Berdock を Kiro などから使えるツールを作ったので、注意点をまとめた"
url: "https://zenn.dev/g2/articles/a178f3b651140f"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "Python", "zenn"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

## bedrock-fable-mcp

Amazon Bedrock に Claude Fable 5 が来たので、普段使っているモデルとは別系統の「第二の分析役」として使えるようにするちょっとしたツールを作りました。

<https://github.com/0V/bedrock-fable-mcp>

コードや設計のレビュー、粗探し、難所のデバッグ、自分の結論への反証出しなどに使えます。

この記事では、Claude Fable 5 を使う前に必ず注意すべきデータ保持の制約や、実運用で分かったちょっとしたコツを書いています。Bedrock 経由で Fable 5（および Mythos 5）を使う際の参考にしてください。

## データの扱いは要注意

このリポジトリでは `DATA_RETENTION.md` というファイルの中にデータの取り扱いについて事細かに書いています。このファイル自体は人と AI の両方が読むことを想定したファイルで、このリポジトリを作ったのは、ほぼこのファイルのためと言っても過言ではありません。まずはこのファイルに書かれている内容をざっくりと解説します。

Fable 5（と Mythos 5）は、Bedrock のデータ保持モードを `provider_data_share` にしないと使えません。このモードでは入力と出力が最大30日間保持され、**モデルプロバイダである Anthropic に共有され**ます（AWS 公式 [data-retention.html](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)）。他の Anthropic モデルとは異なり、データは AWS 内に留まらないため要注意です。

データの保持モードは、プロジェクト単位とアカウント単位の2か所で設定でき、加えてモデル自身の既定値があります（この3つはスコープと呼ばれます）。モードは default / provider\_data\_share / none / inherit の4つです。

* **default**: AWS が安全対策や不正防止のために保持することはありますが、モデルプロバイダには渡しません。実際にどれだけ保持するかはモデルごとに違います。
* **provider\_data\_share**: 入力と出力をプロバイダの要件に従って保持・共有します。Fable 5 や Mythos 5 を呼ぶにはこれが必須です。
* **none**: ゼロ保持。AWS も永続ストレージに書かず、プロバイダにも共有しません。代わりに、保持を要求するモデルは使えなくなります。
* **inherit**: このスコープでは値を決めず、ひとつ上（プロジェクトならアカウント）の設定に従います。新しく作ったアカウントやプロジェクトは最初がこの `inherit` で、自分で別のモードを設定するまでは広いスコープ任せのままです。

モードは「プロジェクト → アカウント → モデル既定」の順に見て、最初に `inherit` でない値が採用されます。Fable を呼ぶには、この実効モードを `provider_data_share` にしておく必要があります。

こういった理由により、会社の方針として Anthropic にデータを共有して良いという整理になっているかが重要です。今回公開したツールでは、入れて良いのは公開データか合成されたデータだけとして、PII、専有コード、シークレット、生ログ、アカウント ID や ARN などは入れないようREADMEで書いています。このあたりは扱うデータの要件にあわせてご調整ください。

もし、よりきちんとフィルタリングをかけるのであればBedrock Guardrails などのガードレールをご活用いただけると良いかと思います。

## 使い方

AWS アカウントへのクレデンシャルを設定したら、あとは準備は二つです。保持モードを `provider_data_share` にすることと、リージョンを指定しましょう。

```
# Fable を使える状態にする
python3 set_data_retention.py set provider_data_share
# 未設定ならエラーで止まる
export FABLE_AWS_REGION=us-west-2
```

`FABLE_AWS_REGION` にデフォルトリージョンを置いていないのは、データが処理・保持される場所を意図的に選ぶためです。

このツールは次の３つの方法で利用できます。

### CLI

```
export FABLE_AWS_REGION=us-west-2
python3 fable_call.py "このアルゴリズムの計算量を分析して"
python3 fable_call.py --system "あなたは厳格なレビュアー" --max-tokens 6000 "..."
echo "長いプロンプト" | python3 fable_call.py -
```

### 任意の MCP クライアント

`fable_mcp.py` を stdio の MCP サーバとして登録します。env でプロファイルとリージョンを渡します。

```
{
  "command": "python3",
  "args": ["/path/to/fable_mcp.py"],
  "env": {
    "FABLE_AWS_PROFILE": "sandbox",
    "FABLE_AWS_REGION": "us-west-2"
  }
}
```

### Kiro

Kiro の Skills としても利用できます。

```
cp -r . ~/.kiro/skills/fable
FABLE_AWS_REGION=us-west-2 ~/.kiro/skills/fable/install-kiro.sh
```

### 終わったら戻す

使い終えたら保持モードを戻すこともできます。

```
python3 set_data_retention.py set default  # 通常の Bedrock 保持（プロバイダ非共有）に戻す
```

`set default` で Fable は unavailable となり、Anthropic への共有も止まります。AWS にも一切保持させたくないなら `set none`（ゼロ保持）にできますが、AWS 上での保持を要求する他のモデルも使えなくなるために注意してください。

## 使ってみて分かったコツ

**max\_tokens はある程度大きな値にする。**  
Fable 5 は推論モデルで、内部の推論が出力トークンを食います。900 のような低い値にしたところ、推論の途中で打ち切られ、本文が空のまま `stop=max_tokens` で返ってきました。これは私の肌感覚ですが、6000以上程度にしておくと程よいという印象でした。

**1リクエストにつき1タスクにする。**  
独立した論点を一度に詰め込むと品質が崩れ、またトークン消費も激しいため `stop=max_tokens` で本文が空になることがありました。論点ごとに分けて投げる方が安定します。

**コストは出力が支配的だと考えておく。**  
[Bedrock の料金](https://aws.amazon.com/bedrock/pricing/)では Anthropic モデルの出力単価が入力の数倍なので、推論モデルの Fable 5 では出力がコストの大半を占めます。読まない長文を生成させないよう、出力の形式と長さを先に指定しておくと良いです。ツールはフッターに入力・出力のトークン数を毎回出します（キャッシュを使った呼び出しではキャッシュ別の数も出ます）。そこで実コストを確かめられます。

**stop\_reason を確認する。**  
`end_turn` なら完了、`max_tokens` なら途中で切れています。プロンプトには「何を達成したいか・制約・判断基準」を書いて、解き方はモデルに任せると安定する印象です。

## Fable 5 にこのツールをレビューさせてみた

このツール自体を、このツールを使って Fable 5 にレビューさせてみたところ、以下のようなバグやよろしくない実装が見つかりました。指摘は的確で、レビュー力がなかなか強力になっているなという印象でした。

* Bedrock クライアントにタイムアウトを設定しておらず、既定の60秒で推論が死ぬ（レビュー中に実際1度タイムアウトしました）
* コスト計算に dead code がある
* `--cache` は system が無いと効かないが、README の例として書かれている
* `set_data_retention.py` が失敗しても exit 0 を返す
* アカウント全体に影響する設定変更なのに、事前の検証や確認が無い（これはバグではないものの、良い指摘）

## はじめの一歩

公開されているコードや文章などを対象に CLI でレビューを1本流してみましょう。まずは小さく試します。出力、および`stop_reason` やトークンフッターを見て良い感じに使えてるなと思えたら、あとは普段のワークフローに混ぜるだけです（Anthropic に共有して良いデータだけを入れるようにすることを忘れずに）。

Claude Fable 5 ライフ、楽しんでみてください。
