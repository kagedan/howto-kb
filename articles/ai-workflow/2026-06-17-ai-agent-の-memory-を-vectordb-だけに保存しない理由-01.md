---
id: "2026-06-17-ai-agent-の-memory-を-vectordb-だけに保存しない理由-01"
title: "AI Agent の memory を VectorDB だけに保存しない理由"
url: "https://zenn.dev/jinenn/articles/mysql-source-of-truth-vectordb-index"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-06-17"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## 1. はじめに

AI Agent の memory を保存するとき、最初は VectorDB を中心に設計したくなる。

あとから semantic search したいなら、memory 本文を embedding に変換してそのまま VectorDB に保存すればよさそうに見える。小さなプロトタイプであれば、この構成でも十分に動く。

ただ、長期的に扱う memory を保存する場合、VectorDB を正本として信頼してよいかは慎重に考えたほうがいい。

ここでいう正本とは、「アプリケーションとして事実として扱うデータ」のことだ。たとえば memory の本文、作成者、作成日時、削除状態、処理状態などは、あとから更新・復元・監査する対象になる。

MySQL のような RDBMS では、こうしたデータを ACID トランザクション・制約・バックアップ・migration と組み合わせて管理しやすい。一方で VectorDB は、意味的に近いデータを検索するための index としての性格が強い。

また、VectorDB に保存される embedding は元の本文そのものではない。embedding model・前処理・chunking・metadata の持たせ方に依存して作られる派生データだ。そのため、あとから embedding model を変えたり VectorDB の index を作り直したりする場合には、元になる memory 本体が別の場所に安定して残っている必要がある。

この記事では、AI Agent Memory Backend の memory 保存を題材に、VectorDB だけに保存しない構成を整理する。

ポイントは、memory 本体をあとから読み直せる形で持ち、VectorDB は semantic search のための検索インデックスとして使うことだ。

検索精度を上げるための chunking や rerank はここでは主題にしない。memory 本体と検索インデックスをどう分けて保存するかが主題だ。

## 2. VectorDB を正本にすると何が困るのか

VectorDB を正本として扱う設計では、memory 本文・metadata・状態を VectorDB の payload に入れ、検索結果をそのまま API レスポンスに使う形になりやすい。

小さなプロトタイプでは、この形はわかりやすい。保存したらすぐ検索でき、VectorDB だけを見れば memory が取れるように見える。

ただ、運用を考えると困る点がいくつか出てくる。

| 困ること | 何が問題になるか |
| --- | --- |
| 更新や削除の正しさを保ちにくい | VectorDB の payload や index に古い内容が残ったとき、何を正しい状態とみなすか曖昧になる |
| embedding model を変えにくい | VectorDB にあるベクトルは特定の model と前処理から作られた派生データなので、元本文がないと作り直せない |
| chunking 方針を変えにくい | chunk 単位を変えたいとき、元の memory 本文から再分割する必要がある |
| 反映失敗を追跡しにくい | API の保存処理と VectorDB 反映が混ざると、memory 保存の成功と検索 index 反映の成功を分けて扱いにくい |
| アプリケーション上の状態を判断しにくい | 削除状態・公開範囲・処理状態などを VectorDB payload だけで信頼すると、古い index が返る可能性がある |
| backup や migration の基準が曖昧になる | 復元や再処理の基準にしたいデータと、検索のための派生データが同じ場所に混ざる |

特に問題になるのは、VectorDB にあるデータが「利用者に返すべき正しい memory」なのか「検索のために作った候補」なのかが曖昧になることだ。

たとえば memory を削除したあとに VectorDB 側の index が一時的に残った場合、その検索結果をそのまま返してよいかを判断しづらい。metadata を更新した場合も同じで、VectorDB payload とアプリケーション上の正しい状態がずれる可能性がある。

また、embedding model や chunking の設計はあとから変わることがある。検索品質を改善したいとき、過去の memory を新しい方針で embedding し直すには、元の memory 本文が安定して残っている必要がある。

VectorDB が不要という話ではない。VectorDB は semantic search には必要だ。ただし、その役割は「正しい memory 本体を持つこと」ではなく「意味的に近い候補を見つけること」に寄せたほうが扱いやすい。

そのためこの記事では、MySQL を正本にし、VectorDB を再生成可能な検索インデックスとして扱う。

## 3. 今回の基本構成

今回の最小構成は、FastAPI・MySQL・Outbox Worker・Embedding・VectorDB で作る。

![MySQLを正本、VectorDBを検索インデックスにする全体構成](https://static.zenn.studio/user-upload/deployed-images/84abb1ac45207640bcd0640b.png?sha=0914832a7821963621bc7540b4b7c2723a25625a)

この図で見たいポイントは次の通りだ。

* Client からの書き込みリクエストは、まず FastAPI が受ける
* FastAPI は MySQL のトランザクション内で memory 本体と後続処理の記録を保存する
* Worker は MySQL の `outbox_events` を polling し、未処理の event を取得する
* Worker は MySQL から memory 本体を読み、embedding を生成して VectorDB に反映する
* VectorDB は memory 本体の保存先ではなく、semantic search 用の検索インデックスとして扱う
* 検索時は VectorDB で候補を見つけたあと、返却する本文や状態は MySQL から取得する

各コンポーネントの責務は以下のように分ける。

| コンポーネント | 役割 | この記事での扱い |
| --- | --- | --- |
| FastAPI | API リクエストを受け、MySQL に memory と outbox event を保存する | 同期処理の入口 |
| MySQL | memory 本体・処理状態・後続処理の記録を保存する | 正本 |
| outbox\_events | Worker に渡すべき後続処理を MySQL 上に残す | 非同期処理の状態管理 |
| Worker | outbox event を処理し、embedding 生成と VectorDB 反映を行う | 非同期処理の実行役 |
| Embedding | memory 本文から検索用ベクトルを生成する | 派生データの生成 |
| VectorDB | ベクトル検索に必要な index を保存する | 検索インデックス |
| Docker Compose | API・Worker・MySQL・VectorDB をローカルで再現する | 検証環境 |

ここで大事なのは、MySQL と VectorDB を同じ種類の保存先として見ないことだ。

MySQL は、あとから復元・再処理・状態確認するための正本を持つ。VectorDB は、MySQL にある memory を意味検索しやすくするための index を持つ。したがって VectorDB に保存する payload は検索に必要な最小限の情報に寄せ、API が利用者に返す本文や状態は MySQL 側から組み立てる。

初期実装では Redis Queue は入れず、MySQL の `outbox_events` を Worker が polling する。ここでまず確認したいのは、**正本を MySQL に置き、VectorDB 反映を後続処理として扱えるか** だ。Redis Queue は、event 数や遅延・Worker 数が問題になってから追加する。

## 4. MySQL を正本にする

この設計では、memory に関する事実は MySQL に保存する。

ここでいう事実とは、あとからアプリケーションが信頼して読み直す必要がある情報だ。memory の本文・会話との関連・作成日時・削除状態・処理状態などが該当する。

| データ | MySQL に置く理由 |
| --- | --- |
| memory 本文 | 利用者に返す内容そのものだから |
| conversation\_id / role | memory の文脈や発話者を判断するために必要だから |
| metadata | 検索条件・表示・再処理の判断に使う可能性があるから |
| outbox\_events | 後続処理の状態を追跡し、失敗時に再実行するため |
| retry\_count / last\_error | 障害時に何が起きたかを確認するため |
| created\_at / updated\_at | 並び順・監査・再処理対象の判断に使うため |

MySQL を正本にすると、memory を作成する API の責務を明確にできる。

```
API が同期的に保証すること:
memory 本体と後続処理の記録を MySQL に保存する

API が同期的には保証しないこと:
embedding が生成され、VectorDB に反映され、検索可能になっていること
```

この分け方により、API は「memory を受け付けた」ことを返せる。VectorDB 反映の完了は Worker が後続で処理する。

memory 作成時の流れを図にすると次のようになる。

![memory作成時の流れ](https://static.zenn.studio/user-upload/deployed-images/38432e08f02437f9eb1638bf.png?sha=72c3b488a002f7ef22fb6a2b3f0667ce28e073f0)

図2では、API が MySQL への保存までを担当し、VectorDB 反映を Worker に渡している。

* `POST /memories` の中では、memory 本体と outbox event を MySQL に保存する
* API は VectorDB への反映完了を待たずに、受付結果を返す
* Worker は `outbox_events` から処理対象を取得する
* Worker は MySQL から memory 本体を読み、embedding を生成して VectorDB に反映する
* VectorDB 反映が終わったら、Worker が outbox event を完了状態にする

ここで重要なのは、MySQL に memory を保存する処理と後続処理の記録を残す処理を、同じトランザクションに入れることだ。

コードでは `Memory` と `OutboxEvent` を同じ session で追加し、最後にまとめて `commit` している。

```
memory = Memory(
    conversation_id=request.conversation_id,
    role=request.role,
    content=request.content,
    metadata_json=request.metadata,
)
session.add(memory)
session.flush()

event = OutboxEvent(
    event_type=OutboxEventType.MEMORY_CREATED.value,
    aggregate_type="memory",
    aggregate_id=memory.id,
    payload={"memory_id": memory.id},
)
session.add(event)
session.commit()
```

こうしておくと、memory だけ保存されて後続処理の記録がない状態や、後続処理の記録だけあって対象の memory がない状態を避けやすい。

Worker 側では outbox event から対象の memory を読み、embedding を生成して VectorDB に反映する。

```
memory = session.get(Memory, event.aggregate_id)
if memory is None:
    raise ValueError(f"memory not found: {event.aggregate_id}")

vector = embed_text(memory.content, settings.embedding_dimensions)
index.upsert_memory(memory, vector)
mark_outbox_completed(session, event)
```

Worker は VectorDB に保存するための材料を MySQL から取得している。VectorDB 側を見て memory 本体を復元するのではなく、MySQL の正本から検索インデックスを作る、という向きだ。

MySQL を正本にしておけば、VectorDB 反映に失敗しても memory 本体は失われない。検索インデックスが壊れたり作り直しが必要になったりしても、MySQL に残っている memory から再生成できる。

## 5. VectorDB を検索インデックスとして扱う理由

VectorDB は memory 本体を永続化する場所ではなく、意味的に近い memory を見つけるための検索インデックスとして扱う。

理由は、VectorDB に保存するベクトルが元データそのものではなく、検索のために作られた派生データだからだ。

| 要素 | VectorDB 側のデータに影響するもの |
| --- | --- |
| embedding model | 同じ本文でも model が変わるとベクトルが変わる |
| 前処理 | 正規化・不要文字の除去・言語ごとの処理で結果が変わる |
| chunking | どの単位で分割するかによって検索粒度が変わる |
| metadata | filter や payload の設計によって検索結果が変わる |
| distance / index 設定 | 距離関数や index 設定によって検索特性が変わる |

つまり VectorDB にあるデータは **その時点の検索設計を反映した index** であり、memory 本体とは性質が違う。検索のための投影として見るほうが適切だ。

同じ memory 本文でも embedding model を変えればベクトルは変わる。chunking 方針を変えれば、1 つの memory から作られる index の単位も変わる。metadata の持たせ方を変えれば、filter の効き方や検索後の扱いも変わる。

VectorDB の index は検索設計に合わせて作り直す対象であり、長期的に信頼する memory 本体とは別の寿命を持つ。

一方、MySQL に memory 本体が残っていれば VectorDB は作り直せる。

```
MySQL
  memory の正本
  更新・削除・状態管理・再処理の基準

VectorDB
  semantic search 用の index
  MySQL のデータから再生成できる派生データ
```

検索時もこの考え方に合わせる。VectorDB は query に意味的に近い候補を返すために使い、利用者へ返す本文・role・metadata・削除状態などは MySQL から取得する。

コード上でも、VectorDB の検索結果だけでレスポンスを組み立てず、候補 ID を使って MySQL を引き直している。

```
hits = QdrantMemoryIndex().search(vector, limit)
ids = [hit.memory_id for hit in hits]

memories = session.execute(
    select(Memory).where(Memory.id.in_(ids))
).scalars().all()
memory_by_id = {memory.id: memory for memory in memories}

results = []
for hit in hits:
    memory = memory_by_id.get(hit.memory_id)
    if memory is None:
        continue
    results.append(
        SearchResult(
            memory_id=memory.id,
            content=memory.content,
            conversation_id=memory.conversation_id,
            role=memory.role,
            metadata=memory.metadata_json,
            score=hit.score,
            created_at=memory.created_at,
        )
    )
```

VectorDB は候補を見つけるために使い、API レスポンスの本文や metadata は MySQL から作る。

こうしておくと、VectorDB に古い index が一時的に残っていても、MySQL 側の状態を見て返却対象から外せる。VectorDB の役割を「候補を見つけること」に限定し、正しいデータを返す責務は MySQL 側に寄せられる。

## 6. VectorDB 反映に失敗しても memory 本体は残る

MySQL を正本にし VectorDB 反映を Worker に分けると、VectorDB 側で障害が起きても memory 本体を失わずに済む。

実際に Qdrant を停止した状態で `POST /memories` を実行し、Worker が VectorDB 反映に失敗する状態を作ってみた。

再現時は、Compose 環境を起動したあと Qdrant だけを停止して memory 作成 API を呼び出した。

再現に使ったコマンドと出力

```
docker compose up -d --build
docker compose stop qdrant

$body = @{
  content = 'VectorDB failure reproduction: Qdrant is stopped before worker upsert'
  role = 'user'
  metadata = @{ scenario = 'vectordb_failure_log' }
} | ConvertTo-Json -Depth 5

$response = Invoke-RestMethod `
  -Method Post `
  -Uri 'http://localhost:8000/memories' `
  -ContentType 'application/json' `
  -Body $body
```

作成された memory と task は以下だ。

```
memory_id=fbf34687-e1ef-4a4c-a6d7-67a060ae125f
task_id=1329be6b-99c2-4a24-bc8f-3c7dc1b53b3f
initial_status=pending
```

この時点で API は memory 本体と outbox event を MySQL に保存している。まだ VectorDB には反映されていない。

Qdrant を停止しているため Worker は VectorDB に接続できず、次のように失敗する。

```
worker-1  | 2026-06-17 16:37:45,889 ERROR __main__ failed outbox event 1329be6b-99c2-4a24-bc8f-3c7dc1b53b3f
worker-1  |   File "/app/app/worker.py", line 35, in process_once
worker-1  |   File "/app/app/vectordb.py", line 37, in upsert_memory
worker-1  |   File "/app/app/vectordb.py", line 25, in ensure_collection
worker-1  | qdrant_client.http.exceptions.ResponseHandlingException: [Errno -5] No address associated with hostname
```

Worker は失敗した event をすぐには捨てず retry する。今回の設定では最大 3 回まで試行し、最終的に `failed` になった。

```
task_status=failed
retry_count=3
max_retries=3
last_error=[Errno -2] Name or service not known
```

ここで重要なのは、VectorDB 反映に失敗しても memory 本体は MySQL に残っていることだ。

MySQL を確認すると `memories` には本文が残っている。

```
id                                      role  content
fbf34687-e1ef-4a4c-a6d7-67a060ae125f    user  VectorDB failure reproduction: Qdrant is stopped before worker upsert
```

一方 `outbox_events` には後続処理が失敗したことが残っている。

```
id                                      aggregate_id                            status  retry_count  max_retries  last_error
1329be6b-99c2-4a24-bc8f-3c7dc1b53b3f    fbf34687-e1ef-4a4c-a6d7-67a060ae125f  failed  3            3            [Errno -2] Name or service not known
```

この状態は、検索インデックスへの反映には失敗しているが、memory の保存には成功している状態だ。

もし API の中で MySQL 保存と VectorDB 反映をまとめて同期実行していた場合、どこまで成功したのかを API 側で扱う必要が出てくる。MySQL には保存できたが VectorDB には反映できなかったのか、VectorDB には反映できたがレスポンスに失敗したのか、といった境界が API の責務に入り込む。

今回の構成では API の責務は MySQL への保存までだ。VectorDB 反映の失敗は `outbox_events` の状態として残る。そのため、次のような運用を後から組める。

* `failed` の outbox event を確認する
* 原因をログや `last_error` から調べる
* Qdrant 復旧後に failed event を再実行する
* 必要であれば MySQL の memory から VectorDB index を再構築する

VectorDB 反映に失敗しても、正本である memory 本体は失われない。失敗は検索インデックス側の反映失敗として扱い、MySQL に残っている正本から再処理できる。

## 7. 検索時も最終的な memory 本体は MySQL から取得する

検索時も、VectorDB を正本として扱わない。

VectorDB は query に近い候補を見つけるために使い、最終的に返す memory 本体は MySQL から取得する。

![検索時の流れ](https://static.zenn.studio/user-upload/deployed-images/38fafb4adc5a9ed28ba009f7.png?sha=451d9228b77067c2ef26d20d48c734c2642ce552)

流れはこうなる。

* API が検索 query を受け取る
* query から embedding を生成する
* VectorDB で意味的に近い候補を検索する
* VectorDB から得た候補を使って MySQL を引き直す
* MySQL にある本文・metadata・作成日時・状態を使ってレスポンスを作る

こうすると VectorDB は「候補を見つける場所」になる。利用者に返すデータの正しさは MySQL 側で判断する。

実装でも、VectorDB の検索結果だけでレスポンスを作らない。

```
hits = QdrantMemoryIndex().search(vector, limit)
ids = [hit.memory_id for hit in hits]

memories = session.execute(
    select(Memory).where(Memory.id.in_(ids))
).scalars().all()
memory_by_id = {memory.id: memory for memory in memories}
```

`hits` は VectorDB が返した検索候補だ。API はその候補を使って MySQL から `Memory` を取得する。

レスポンスに入れる本文や metadata は MySQL から取得した `Memory` の値を使う。

```
for hit in hits:
    memory = memory_by_id.get(hit.memory_id)
    if memory is None:
        continue
    results.append(
        SearchResult(
            memory_id=memory.id,
            content=memory.content,
            conversation_id=memory.conversation_id,
            role=memory.role,
            metadata=memory.metadata_json,
            score=hit.score,
            created_at=memory.created_at,
        )
    )
```

`if memory is None: continue` も重要だ。VectorDB 側に古い index が残っていても、MySQL に正本がなければ返さない、という判断ができる。

今後 memory に削除状態や公開範囲を追加した場合も同じで、VectorDB の候補に含まれていても、MySQL 側で「返してよい memory か」を判断できる。

検索 API は VectorDB に依存しているが、VectorDB の payload を正本として信頼しているわけではない。VectorDB は検索候補を返し、MySQL が最終的な返却内容を決める。

## 8. この設計でできること

MySQL を正本にし VectorDB を検索インデックスとして扱うと、障害時や設計変更時に取り得る手段が増える。

| できること | 理由 |
| --- | --- |
| VectorDB 反映に失敗した memory を確認できる | `outbox_events` に status・retry\_count・last\_error が残るため |
| 失敗した処理を再実行できる | memory 本体が MySQL に残っているため |
| VectorDB の index を再構築できる | MySQL の memory から embedding を作り直せるため |
| embedding model を変更しやすい | 元本文を MySQL から読み直して再生成できるため |
| 検索結果の本文を正本から返せる | VectorDB の payload ではなく MySQL の row を使うため |
| 古い index を返却前に落とせる | MySQL 側に存在しない memory をレスポンスから除外できるため |

特に大きいのは、失敗を「データ消失」ではなく「検索インデックス反映の未完了」として扱える点だ。

VectorDB への反映に失敗しても memory 本体は MySQL にある。そのため復旧後に `failed` の outbox event を再実行したり、特定期間の memory を対象に index を作り直したりできる。

検索品質を改善したくなった場合にも、この構成は扱いやすい。embedding model・chunking・metadata の設計を変えると VectorDB 側の index は作り直しになるが、MySQL に元の memory が残っていれば過去データも含めて再生成できる。

この設計の目的は VectorDB を軽視することではない。VectorDB は semantic search に必要な重要なコンポーネントだ。ただし責務は「正本を持つこと」ではなく「検索しやすい index を持つこと」に限定する。

## 9. 結論

AI Agent Memory Backend では、memory 本体の正本を MySQL に置き、VectorDB は semantic search 用の検索インデックスとして扱う。

API は MySQL に memory 本体と後続処理の記録を保存する。Worker はその記録を処理し、embedding を生成して VectorDB に反映する。検索時は VectorDB で候補を見つけ、最終的に返す本文や状態は MySQL から取得する。

こうすることで、VectorDB 反映に失敗しても memory 本体は残る。embedding model や index 設計を変えたい場合も、MySQL にある正本から再生成できる。

VectorDB は便利な保存先ではなく、再生成可能な検索インデックスとして扱う。更新・削除・失敗時の復旧・index 再構築を考えると、この分け方のほうが扱いやすい。
