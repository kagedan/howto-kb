---
id: "2026-03-18-gemiclawにapiキーを隠匿するkeybinderを導入した-01"
title: "gemiclawにAPIキーを隠匿するkeybinderを導入した。"
url: "https://zenn.dev/nishina__n/articles/2fd0f90086841b"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

現在開発している軽量・セキュアなAIエージェントのgemiclawにAIエージェントからAPIキーが見えないようにするkeybinderを構想・作成した。

リポジトリ：<https://github.com/Nishina-N/gemiclaw>

## AIエージェントのリスク

AIエージェント利用時のセキュリティリスクには以下のようなものがあると思う。

1. プロンプトインジェクション  
   外部から取得したコンテンツ（Webページ、Discordメッセージ等）に悪意ある指令が埋め込まれ、エージェントがそれに従って意図しない行動をとる。
2. 機密情報の漏洩  
   APIキー、トークン、個人情報などをエージェントが読み取り、外部に送出する。
3. 権限昇格・ファイル破壊  
   エージェントが書き込み可能な領域を悪用して、設定ファイルやスキルを書き換え、動作を乗っ取る。
4. 無制限のリソース消費  
   APIの大量呼び出しによる課金爆発、ループによるCPU/メモリ枯渇。
5. サプライチェーン攻撃  
   pip\_installで悪意あるパッケージを導入させられる。インストールされたパッケージがバックドアを持つ。
6. データ汚染（メモリポイズニング）  
   外部コンテンツをそのままメモリに書き込ませ、将来の動作を汚染する。
7. 横断的移動（ラテラルムーブメント）  
   コンテナ内から他のサービスやホストへの不正アクセス。

どれもやられると困るんだが、これらの脅威への対策としては

1. エージェントへの行動規範でエージェントを強くする
2. 外部からルールベースでのエージェントの行動制限
3. 外部からのエージェントの行動監視
4. キーなどをそもそもエージェントから見れなくする。  
   といったものが考えられる。

今回は4.の対策としてAPIキーをAgentから見えなくすることにより、APIキーの流出を防ぐという対策をとった。

## これまでに考案されている脅威への対策

HashiCorp Vault / AWS Secrets Manager  
Key Binderと同じ「アプリケーションがシークレットに直接触れない」設計。エージェントではなく一般的なアプリ向けだけど、思想は同一。Vaultは「動的シークレット（使い捨てキー発行）」まで対応していて、すごい。

API Gateway（AWS API Gateway, Kong等）  
リクエストを受け取ってキーを付与して転送するという点で今回のKey Binderと同じ。エンタープライズ向けに認証・レート制限・ログが揃っているみたい。これと鍵の管理場所があれば良い。今回のは自前で軽量なAPI Gatewayを作ってしまうと言う話。

LiteLLM / Portkey  
LLM向けのプロキシ。複数のLLM APIキーを一元管理し、呼び出し元にキーを見せない構造。gemiclawでいけば、Gemini API呼び出し部分のキー管理。これは今後導入するかもしれない。

Lakera Guard / NeMo Guardrails  
エージェントの入出力を監視してプロンプトインジェクションや有害なレスポンスを検出・遮断するとのこと。「キー漏洩」ではなく、「プロンプトインジェクション」に対応する。

## 今回のkeybinder

今回のkeybinderは別のコンテナにGateway serviceを立ち上げて、APIキーを使うようなやり取りはエージェントがこの別コンテナにクエリを送信することで、keybinder側でAPIキーをバインドして外部送信する。エージェントにはAPIキーが確認できない仕様だ。

Key Binderで対応できる部分は、先ほどの脅威リストの中では  
2. 機密情報の漏洩　と　3. 権限昇格・ファイル破壊の一部。当たり前ながらAPIキーの漏洩対策に主眼をおいているので、どちらも対象がAPIキー抜き取りだった場合にのみ対応可能。

Key Binder導入で新たに発生するリスクとしては以下の２点が考えられるが、AgentがAPIキーを見れる状態よりはずっとマシだと思う。

1. Key Binder自体が攻撃対象になる  
   内部ネットワークに認証なしのHTTPサービスが増える。同ネットワーク上の別コンテナから悪用可能。
2. secrets.jsonの一点集中  
   分散していたキーが1ファイルに集まるため、Key Binderコンテナが侵害された際の被害範囲が広がる。

## keybinderの構成の詳細

keybinderは `node:20-slim` ベースの軽量なNode.jsコンテナで、TypeScriptで書かれたシンプルなHTTPサーバーだ。ポート3001でリクエストを待ち受け、エージェントのスキルスクリプトからのクエリを受け取り、APIキーを付与して外部APIを叩き、結果だけを返す。

**コンテナ分離の仕組み**

`docker-compose.yml` で2つのサービスを定義している。

```
services:
  gemiclaw:
    build: .
    depends_on:
      - keybinder
    volumes:
      - ./config:/app/config   # エージェントが読み書きできる領域
      # secrets_for_skills.json はここにマウントしない

  keybinder:
    build: ./keybinder
    volumes:
      - ./keybinder/secrets_for_skills.json:/secrets/keys.json:ro
      # このコンテナにのみ secrets をマウント
```

`secrets_for_skills.json` は keybinder コンテナの `/secrets/keys.json` としてマウントされ、gemiclaw コンテナには一切マウントされない。エージェントが `read_file` でどんなパスを指定しても、Pythonで `os.environ` を叩いても、このファイルにたどり着く手段がない。

**エンドポイント**

現時点では以下の2つのエンドポイントを実装している。

| エンドポイント | 対応API | パラメータ |
| --- | --- | --- |
| `GET /brave?q=<query>` | Brave Search API | `q`: 検索クエリ |
| `GET /mapbox/static?lat=&lon=&zoom=&markers=` | Mapbox Static Images API | `lat`, `lon`, `zoom`, `width`, `height`, `markers`（省略可） |

Mapboxの `markers` パラメータは Mapbox のオーバーレイ記法（例: `pin-s+ff0000(139.69,35.68),pin-s+0000ff(140.11,36.21)`）をそのまま受け付けており、カンマ区切りで複数ピンにも対応している。

地図画像はバイナリなのでbase64エンコードして返す設計にした。スキルスクリプト側でデコードしてファイルに書き出す。

**スキルスクリプト側**

エージェントが書き換え可能な `config/skills/` 以下のスクリプトは、外部APIを直接叩く代わりに keybinder を呼ぶだけになった。

```
# web_search/run.sh
QUERY=$(python3 -c "...")
curl -sf "http://keybinder:3001/brave?q=${QUERY}"
```

スクリプトを書き換えても `http://keybinder:3001/...` へのリクエストしか送れない。APIキー自体はスクリプトには登場しない。

**新しいAPIを追加するには**

エージェントが新しい外部APIを使うスキルを自作したい場合、`keybinder/server.ts` に対応エンドポイントを人間が追加してリビルドする必要がある。これは実装の制約でもあるが、エージェントが承認なしに未知のAPIを使い始めることを防ぐためだ。スキルの自己拡張性とAPIキーのセキュリティはここでトレードオフになっている。

## まとめ

今回導入したkeybinderは業界標準の「APIゲートウェイ＋シークレットマネージャー」パターンをAIエージェント向けに軽量化したもので、「APIキーという資産の保護」に対しては有効。ただしAIエージェントのセキュリティリスクの全体から見ると対応範囲は限定的で、1・3（一部）・4・5・6・7のリスクはAGENTS.mdのルール整備・Dockerの権限設計・メモリの書き込みルールといった別レイヤーで対処する必要がある。将来的にはLakera Guardのような入出力監視を組み合わせたいところです。

かしこ
