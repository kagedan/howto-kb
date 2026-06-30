---
id: "2026-06-30-claude-code-に-mcp-proxy-for-aws-を触らせたらsessionid-no-01"
title: "Claude Code に mcp-proxy-for-aws を触らせたら「SessionId not found」が出続けた話"
url: "https://qiita.com/charita/items/84785020216699a1d0b9"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "LLM", "qiita"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

# はじめに

最近、AWS リソースの調査はもっぱら Claude Code に頼りっぱなしです。とはいえ、SRE というロールであるが故にどうしても強い権限を持つことになるため、私が使用するクレデンシャルをそのまま渡すのは怖いものです。そこで私の環境では、

- **Claude Code 専用の ReadOnly プロファイル（スイッチロールして使用）を用意**
- **そのプロファイルを Claude Code には毎回明示せず、ディレクトリごとに自動で判別して使わせる**
- **AWS リソースを触るときは必ず `aws-mcp` 経由にする**

という方針で運用を組み立てている最中でした。

その検証の過程で、`aws-mcp` が **「最初の1回だけ成功して、数秒後から延々とエラーになる」** という挙動にハマりました。mcp に接続できていないのかと思ったのですが、 `/mcp` コマンドで確認すると「connected」ステータスになっているので理由が分かりませんでした。
そこで調べてみると、`mcp-proxy-for-aws` の署名処理と assume-role 構成の相性に起因する問題でした。

# 前提：どんな構成で AWS を触らせているか
まず、私が Claude Code に AWS を触らせるために組んでいる構成を簡単に説明します。

## Claude Code 専用プロファイルを作る

既存の `~/.aws/config` / `~/.aws/credentials` をコピーし、プロファイル名の末尾に `-llm` などを付けて被らないようにした `config_llm` / `credentials_llm` を別ファイルとして用意します。Claude Code が使うのはこの ReadOnly 専用ファイルだけ、というように分離しておくと、人間用の設定を汚さずに済みます。
以下は私の環境のイメージです。`aws login` コマンドによって認証情報を取得しています。

```ini
# ~/.aws/credentials_llm（イメージ）
[default]
region = ap-northeast-1

[pj_a-stg-llm]
region = ap-northeast-1
role_arn = arn:aws:iam::xxxxxxxxxxxx:role/readonly
source_profile = default

[pj_b-stg-llm]
region = ap-northeast-1
role_arn = arn:aws:iam::xxxxxxxxxxxx:role/readonly
source_profile = default
```

```ini
# ~/.aws/config_llm（イメージ）
[default]
output = json
credential_process = aws configure export-credentials --profile default
login_session = arn:aws:iam::xxxxxxxxxxxx:user/<user_name>

[pj_a-stg-llm]
output = json

[pj_b-stg-llm]
output = json
```

## ディレクトリごとに使うプロファイルを自動で切り替える

作業ディレクトリに `.aws-profile` というファイルを置き、その中に Claude Code 用プロファイル名（例: `pj_a-stg-llm`）を書いておきます。そして MCP サーバの起動コマンドで、このファイルを読んで `AWS_PROFILE` を組み立てるようにしています。

`~/.claude.json` の該当部分は次のとおりです。


```json
"mcpServers": {
  "aws-mcp": {
    "command": "sh",
    "args": [
      "-c",
      "AWS_PROFILE=$(cat .aws-profile 2>/dev/null || echo 'default') ~/.local/bin/mcp-proxy-for-aws https://aws-mcp.us-east-1.api.aws/mcp --metadata AWS_REGION=ap-northeast-1"
    ],
    "env": {
      "AWS_REGION": "ap-northeast-1",
      "AWS_CONFIG_FILE": "/Users/<user>/.aws/config_llm",
      "AWS_SHARED_CREDENTIALS_FILE": "/Users/<user>/.aws/credentials_llm"
    }
  }
}
```

こうしておくと、ディレクトリを移動するだけで使用するプロファイルを自動で固定できます。プロファイルをプロンプトで毎回指定させずに済むので、指定ミスや権限の取り違えも防げます。
尚、AWS リソースを触る際に直接 AWS CLI を実行されてしまうと意味がないので、グローバル設定の `CLAUDE.md` に必ず `aws-mcp` を使うように指定しています。

## `uvx` ではなくローカルインストールにしている理由

公式のドキュメントでは `uvx mcp-proxy-for-aws@latest ...` のように `uvx` で起動する例が多いのですが、私は `~/.local/bin/mcp-proxy-for-aws` というローカルインストール版を直接叩いています。

これは `uvx` の `@latest` 起動だと**都度ダウンロードが走ってキャッシュが肥大化した**ことがあったためです（あくまで私の環境での話なので、ここは好みで構いません）。

ただしこのやり方は**バージョン固定**になるので、セキュリティ修正やバグ修正を取り込むために**定期的に手動でバージョンアップする運用**が前提になります。あとで触れますが、今回のセッション問題はバージョンを上げても直らない種類のものでした。

# 症状

本題です。上記の構成で `aws-mcp` を使い始めると、こんな挙動になりました。

- **最初のツール呼び出しは成功する**
- ところが**数秒後の2回目以降が、次のエラーで失敗し続ける**

```
The provided SessionId was not found or has expired, please re-initialize your connection.
```

しかも厄介なことに、

- Claude Code の `/mcp` コマンドでは `aws-mcp` が **「✔ connected」** と表示されている
- `aws sts get-caller-identity` 単体は普通に通る（クレデンシャル自体は生きている）
- 一度この状態になると、MCP サーバ（proxy）を再起動するまで全呼び出しが失敗し続ける

という状態で、エラーメッセージ通りの状況ではないように思えました。

# 紛らわしいポイント

ハマった原因の半分は、ここの勘違いにありました。

まず「`connected` と表示されているのに失敗する」のは、`/mcp` コマンドが見せているのが **Claude ↔ proxy 間のローカル stdio 接続**だからです。この接続は生きています。しかし実際に壊れているのは、その奥にある **proxy ↔ AWS バックエンド間の MCP セッション**（HTTP ヘッダの `Mcp-Session-Id`）のほうでした。

つまり「接続は2層あって、`connected` が意味しているのは手前の層だけ」という構造を理解していないと、「`connected` なのになぜ？」とずっと悩むことになります。

そしてもう一つ。これは**単純なクレデンシャル失効・トークン切れではありません**。もしそうなら最初の1回目から失敗するはずですが、実際には「初回だけ成功する」という状況でした。この「初回だけ成功する」という事実が、原因を特定する大きなヒントになりました。

# 原因

結論から言うと、原因は以下の2つの掛け算でした。

1. `mcp-proxy-for-aws` が **HTTP リクエストごとに新しい boto3 Session を生成する**
2. 利用プロファイルが **assume-role 構成かつ `role_session_name` 未指定**

順に見ていきます。

## (1) リクエストごとに boto3 Session を作り直している

`mcp-proxy-for-aws` のリクエスト署名処理（`sigv4_helper.py` の `_sign_request_hook`）は、リクエストのたびにディスクからクレデンシャルを読み直して新しい Session を作っています。

https://github.com/aws/mcp-proxy-for-aws/blob/main/mcp_proxy_for_aws/sigv4_helper.py#L281-L284

コメントにあるとおり、「アカウント切り替えやクレデンシャル更新を即座に反映するため、毎回ディスクから読む」という**意図的な実装**です。プロファイルを動的に切り替える使い方を想定すると理にかなっています。

## (2) assume-role + `role_session_name` 未指定だと、セッション名が毎回変わる

問題は、これが assume-role プロファイルと組み合わさったときです。

`role_arn` + `source_profile` の構成で `role_session_name` を指定していないと、botocore は AssumeRole のたびにロールセッション名を **`botocore-session-<Unix秒>`** という形で自動生成します。リクエストごとに Session を作り直す → 毎回 AssumeRole が走る → そのたびにセッション名の末尾の秒数が変わる、というわけです。

そして AWS の MCP バックエンドは、`Mcp-Session-Id` を**呼び出し元のプリンシパル ARN（ロールセッション名込み）に紐付けて**管理しています。

連鎖を整理すると、こうなります。

1. リクエストごとに新しい Session → 毎回 AssumeRole → ロールセッション名が時刻依存で変わる
2. バックエンドは `Mcp-Session-Id` を「ロールセッション名込みのプリンシパル ARN」に紐付けている
3. 次のリクエストでロールセッション名が変わる → バックエンドは「別人からのアクセス」と判定 → 紐付いたセッションが見つからず `SessionId not found`

`initialize` 直後の即時呼び出しだけが成功するのは、署名が `initialize` と**同じ秒**に収まって、たまたまロールセッション名が一致するためです。数秒経つと秒数がずれて、そこから先は全滅します。「初回だけ成功する」の正体がこれでした。

# 対処：`role_session_name` を固定する

やることは単純で、プロファイルに**固定の `role_session_name`** を与え、ロールセッション名が揺れないようにするだけです。これで通常のツール呼び出しがそのまま安定して使えるようになります。

`role_arn` を持つプロファイルに1行追加します。

```ini
[pj_a-stg-llm]
region = ap-northeast-1
role_arn = arn:aws:iam::xxxxxxxxxxxx:role/readonly
source_profile = default
role_session_name = pj_a-stg-llm-<user_name>   # ← この1行を追加
```

セッション名の付け方ですが、私は `<プロファイル名>-<用途や担当者がわかる識別子>` というルールにしました。固定するだけなら任意の文字列で構いませんが、**CloudTrail やアクセス分析で「誰の（何の）セッションか」がひと目で分かる**ようにしておくと、後から監査するときに楽です。AI 用なら `-claude` や `-llm`、個人で使うなら名前を入れる、といった具合です。

設定を変えたら、**`aws-mcp` の MCP サーバを再接続**します（Claude Code の CLI なら `/mcp` で reconnect、デスクトップアプリなら再起動）。proxy は毎回ディスクからクレデンシャルを読み直すので、再 `initialize` の時点で固定名にバインドし直り、以降は安定します。

# まとめ

`aws-mcp`（`mcp-proxy-for-aws`）で `SessionId not found` が出続けたときの話でした。要点を振り返ります。

- **症状**: 初回だけ成功し、数秒後から `The provided SessionId was not found or has expired` が連発する。`/mcp` は connected 表示で、`sts get-caller-identity` も通る
- **原因**: proxy がリクエスト毎に boto3 Session を作り直す × assume-role で `role_session_name` 未指定 → ロールセッション名が `botocore-session-<秒>` で毎回変わり、バックエンドが別プリンシパルと判定してセッションを見失う
- **対処**: プロファイルに固定の `role_session_name` を付ける。設定後は MCP サーバを再接続する
- **注意**: 最新版に上げても再発する（直すべきはバージョンではなくセッション名）

これで安全かつ簡単に Claude Code 専用の ReadOnly 権限で AWS 環境を触らせることができるようになりました。とはいえまだ運用を始めて間もないので、もっと良いやり方があれば教えていただけると嬉しいです。

# 参考

- Issue: https://github.com/aws/mcp-proxy-for-aws/issues/117
- PR: https://github.com/aws/mcp-proxy-for-aws/pull/122
- 該当コード: `mcp_proxy_for_aws/sigv4_helper.py` の `_sign_request_hook` / `create_aws_session`
