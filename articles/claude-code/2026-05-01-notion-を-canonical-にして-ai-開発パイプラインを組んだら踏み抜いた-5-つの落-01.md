---
id: "2026-05-01-notion-を-canonical-にして-ai-開発パイプラインを組んだら踏み抜いた-5-つの落-01"
title: "Notion を canonical にして AI 開発パイプラインを組んだら踏み抜いた 5 つの落とし穴"
url: "https://zenn.dev/zoetaka38/articles/84241a9e4d6c25"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

タイムラインで「Issue を Notion に登録 → Claude Code が GitHub MCP 経由で branch 切って実装 → PR 作って差分 Summary を Slack に流す」みたいなフローを組んでいる人を見かけて、自分も近い構成を運用してきたのでハマったポイントを書き残しておく。

うちのケースだと、ビジネス側からの要望は Notion の DB に書かれていて、それを AI が PRD に構造化、開発側がレビューして承認したら下流に流す、という構成になっている。Notion を **canonical source of truth(正本)** に置きつつ、自分たちの DB(Postgres)とは双方向同期する。

一見シンプルなんだけど、実装してみると「Notion を真とする」という設計選択が思っていたより重い。踏み抜いた 5 つの落とし穴を、コードを引きながら共有する。

## 落とし穴 1: 「DB が古い」状態が常に存在する

最初に踏んだのがこれ。Notion を canonical にすると言っても、DB に同期した時点で時間差が生まれる。Notion 側で 1 時間前に編集された内容を反映していない DB の値を AI agent が読むと、agent は **古い前提で PR を作る**。

最初は naive に「PRD を更新したら Notion に push、ページを開いたら pull」だけ実装していたが、ユーザーが Notion 側で本文を直したまま PRD ページを開かずにいると、Slack から起動された別フローが古い DB を読んで動いてしまった。

そこで、PRD エンティティに `notion_synced_at` を別カラムとして持たせ、`updated_at` とは独立させた。

```
# alembic/versions/20260107_add_notion_synced_at_to_prds.py
op.add_column(
    'prds',
    sa.Column('notion_synced_at', sa.DateTime(timezone=True), nullable=True,
              comment='Notion最終同期日時'),
)
```

```
# domain/entities/prd.py 抜粋
def update_notion_synced_at(self) -> None:
    self.notion_synced_at = datetime.now()
    self.updated_at = datetime.now()
```

`updated_at > notion_synced_at` を見るだけで「DB 側に未 push の変更がある」が分かる。逆に Notion の `last_edited_time` を取ってきて `notion_synced_at` と比較すれば「Notion 側に未 pull の変更がある」が分かる。

ページを開いた瞬間に走らせる auto-sync は、これを使って方向を決める。

```
# use_cases/notion/auto_sync_prd_use_case.py 抜粋
def _determine_sync_direction(self, prd, notion_last_edited):
    if not notion_last_edited:
        return None
    # ...timezone を naive UTC に揃える...
    prd_changed = prd_updated > prd_synced if prd_synced else False
    notion_changed = notion_edited > prd_synced if prd_synced else True

    if prd_changed and notion_changed:
        return "both"          # 両方変わってる → pull 優先
    elif notion_changed:
        return "from_notion"
    elif prd_changed:
        return "to_notion"
    return None
```

「両方変わっていたら pull を優先する」と決め切ったのは、**自動 push でデータを失うのが一番怖い** から。pull はローカルが上書きされるだけで Notion 側に履歴が残るが、push は Notion の変更を消しに行くので、ユーザーから見ると「メモがいつの間にか消えた」になる。これは UX 的に致命傷で、信頼を一瞬で失う。

`notion_synced_at` という 1 カラムを足すだけで、その後の同期判定が全部キレイに書けるようになった。入れて良かった、という体感が一番強いカラム。

## 落とし穴 2: Notion 側の手編集と AI 書き戻しの衝突

Canonical を Notion に置くと宣言した時点で、「人間が Notion で編集した内容を AI が上書きしないこと」を守る責任が DB 側に発生する。

最初は last-write-wins(後勝ち)で済ませようとしていた。タイムスタンプを比べて新しい方を採用、それだけ。これは AI 側だけが書き換えるならいいが、人間がページを開いて手で直している所に AI が並行してプロパティを書き戻すと、片方が消える。しかも消えた側は通知も出ない。

ちゃんと衝突を検知して、デフォルトでは **「上書きせず、ユーザーに force=true を要求する」** に変えた。

```
# use_cases/notion/sync_notion_to_prd_use_case.py 抜粋
def _detect_and_resolve_conflict(self, prd, notion_last_edited, force):
    if not prd.notion_synced_at or not notion_last_edited:
        return False, None

    prd_edited_after_sync = prd_updated > prd_synced if prd_synced else False
    notion_edited_after_sync = notion_edited > prd_synced if prd_synced else True

    if prd_edited_after_sync and notion_edited_after_sync:
        if force:
            return True, "forced"
        elif notion_edited > prd_updated:
            return True, "notion_newer"
        else:
            return True, "prd_newer"
    return False, None
```

呼び出し側はこの戻り値を見て、`prd_newer`(=DB 側が新しい)で `force=False` なら **早期 return して同期をスキップ** する。

```
if had_conflict and conflict_resolution == "prd_newer":
    return SyncNotionToPRDOutput(
        prd_id=input.prd_id, synced_at=datetime.now(), changes=[],
        had_conflict=True, conflict_resolution="prd_newer",
        message="Conflict detected: PRD has newer changes. Use force=true to overwrite.",
    )
```

ここで重要なのは、**自動同期では絶対に `force=True` を渡さない** こと。`force=True` を渡せるのは UI で「強制上書き」ボタンを押した人間の操作だけ、という線を引いた。バックグラウンドの cron や AI agent から `force=True` が立つルートが 1 本でもあると、その瞬間に「Notion を canonical にしたはずなのに AI が勝手に上書きする」状態になる。

なお比較は **timezone を一旦 naive UTC に正規化してから** 行う。Notion API は ISO8601 で返るが、Postgres から取り出した値が naive な状況も混ざると平気で比較がぶっ壊れる(`TypeError: can't compare offset-naive and offset-aware datetimes`)。地味だが、衝突判定はすべてこの正規化に乗っかる。

## 落とし穴 3: rate limit と「全 DB を webhook 監視できない」問題

「ページが更新されたら DB に取り込みたい」を webhook で済まそうとして失敗した。

Notion の webhook は対象ページを明示的に subscribe する形なので、ワークスペースに新しい DB やページが **「未来に増える」リソース** をまとめて拾うのに向いていない。結局 polling と組み合わせざるを得ない。

うちでは `last_edited_time` で差分カーソル方式の polling にした。

```
results = notion.databases.query(
    database_id=config.database_id,
    filter={"timestamp": "last_edited_time", "after": last_cursor},
)
for page in results:
    if _matches_task_filter(page, config):
        _enqueue_task_creation(config.project_id, page)
config.last_sync_cursor = datetime.utcnow()
```

これで API 消費は減るが、**「業務開始時刻の 9 時頃に polling が一斉に走って rate limit を撃つ」** 問題が出た。すべてのプロジェクトの cron が同じ秒で起きていると、Notion 側から見ると一瞬でバーストする。

打ち手は地味に 3 つ。

1. Polling cron をプロジェクトごとに ±60 秒のジッター付きで散らす
2. ブロック取得を append 系と同じく **100 件のバッチ + 順次** に強制
3. sync 自体を Celery task 化して、worker 並列度で API レートを上から抑える

3 についてだけコードを引いておく。Notion への push は常に Celery 経由で、worker 並列度がレートを上から抑える。

```
# infrastructure/tasks/notion_sync.py 抜粋
@celery_app.task(bind=True, name="sync_prd_to_notion_task")
def sync_prd_to_notion_task(self, prd_id, database_id, user_id, language="original"):
    self.update_state(
        state="PROCESSING",
        meta={"step": "syncing_to_notion", "progress": 30,
              "message": "Notionに同期しています..."},
    )
    # ... use case を実行 ...
```

同期 API のままだと、ユーザー側のクリックがそのままバーストになる。Celery を挟むだけで「一斉に動く」を「順番に動く」に変換できるので、rate limit 周りはここを変えるだけでもかなり楽になる。

ついでに、ブロック追加 API は **1 リクエスト 100 ブロック上限**。長い PRD を一括で投げると 400 が返る。

```
# infrastructure/external_apis/notion_client.py 抜粋
BATCH_SIZE = 100
for i in range(0, len(children), BATCH_SIZE):
    batch = children[i : i + BATCH_SIZE]
    response = await client.patch(f"/blocks/{page_id}/children", json={"children": batch})
    # ...結果を蓄積...
```

100 ブロックの PRD なんて稀だろう、と思いきや、リスト + 画像 + コードブロック + サブセクションで簡単に超える。実運用 1 週間ほどで 500 ブロック超の PRD が現れて落ちた。

## 落とし穴 4: コメントスレッドのミラーは flat に倒すしかなかった

「Notion 上のコメントを DB にも保持して、PR や Slack に流したい」が要件。最初はスレッド構造をそのまま再現しようとした(parent comment を持つ tree)が諦めた。

理由は 2 つ。Notion のコメント API は **スレッド構造を最初から flat に持っている** こと、そして **「インラインコメント(本文の選択範囲に紐づく)」「ページコメント」「スレッド返信」** の 3 軸を同時に DB に表現するとテーブルが膨らみすぎることだ。

最終的にスキーマはこうした。`parent_comment_id` は元々あるので、そこに Notion 同期用フィールドを追加するだけ。

```
# alembic/versions/20260107_add_inline_comment_and_notion_sync_to_prd_comments.py
op.add_column('prd_comments',
    sa.Column('selected_text', sa.Text(), nullable=True))
op.add_column('prd_comments',
    sa.Column('text_start_offset', sa.Integer(), nullable=True))
op.add_column('prd_comments',
    sa.Column('text_end_offset', sa.Integer(), nullable=True))
op.add_column('prd_comments',
    sa.Column('notion_comment_id', sa.String(255), nullable=True))
op.add_column('prd_comments',
    sa.Column('notion_synced_at', sa.DateTime(timezone=True), nullable=True))
op.create_index('ix_prd_comments_notion_comment_id',
    'prd_comments', ['notion_comment_id'], unique=False)
```

**Notion 側のスレッド構造はそのままミラーしない**。代わりに、コメント本文に「どのセクションのどの選択範囲に対するコメントか」を埋め込む形でメタを保存する。

```
# use_cases/notion/sync_prd_comments_use_case.py 抜粋
def _format_comment_for_notion(self, comment: PRDComment) -> str:
    parts = []
    if comment.section_key:
        parts.append(f"[{comment.section_key}]")
    if comment.selected_text:
        parts.append(f'> "{comment.selected_text}"')
        parts.append("")
    parts.append(comment.content)
    return "\n".join(parts) if len(parts) > 1 else comment.content
```

「Notion 上では 1 つの flat なテキストコメント、DB では構造化フィールドにバラす」という非対称な持ち方。Notion のコメントが 100% 自分たちのドメインモデルと噛み合わないことを認めて、**round-trip しない情報は一方通行と割り切る**。pull 側は `notion_comment_id` で「取り込み済みか」だけ見て、冪等性を保つ。

ハマったのは権限まわりで、Notion 統合に「コメント読み取り」が無効だと API は 404 を返す。エラー文だけだと原因が分からないので、ユーザー向けに翻訳して返している。

```
try:
    notion_comments = await client.get_all_comments(prd.notion_page_id)
except Exception as e:
    if "object_not_found" in str(e) or "404" in str(e):
        raise ValueError(
            "Notion統合に「コメント読み取り」権限がありません。"
            "統合ダッシュボードで「Read comments」を有効にして再連携してください。"
        ) from e
    raise
```

これがないと、サポートに「同期できません」だけ来てひたすら原因切り分けに時間が溶ける。

## 落とし穴 5: 「人間が触る列」と「AI が触る列」の境界が曖昧だと事故る

5 つ目が一番悩んだ。Notion の DB はプロパティを自由に増やせるので、「ステータスは AI と人間の両方が触る」「タイトルは原則人間」「Owner は人間しか触らない」「最終承認者は AI が読むけど書かない」みたいに列ごとにルールが混ざる。

これを **コードで強制せず convention で済ませる** と確実に事故る。AI agent は文字列で命令された権限境界を尊重しないし、別タスクで似たコードを書くとコピペで境界を越える。

うちでは `NotionDatabaseConfig` というプロジェクト設定エンティティで、**AI / コードが書き込む列だけを enum 化された設定として持たせる** 設計にした。

```
# domain/entities/notion_database_config.py 抜粋
class NotionDatabaseConfig:
    def __init__(
        self, project_id, database_id, database_name,
        title_property_name=None,
        status_property_name=None,
        status_property_type=None,         # "status" or "select"
        status_mapping=None,
        creator_property_name=None,
    ):
        self.title_property_name = title_property_name
        self.status_property_name = status_property_name
        self.status_property_type = status_property_type
        self.status_mapping = status_mapping or []
        self.creator_property_name = creator_property_name
```

書き込みロジックは、プロパティ辞書を組むときにこの設定を必ず参照する形にした。

```
# use_cases/notion/sync_prd_to_notion_use_case.py 抜粋
def _prd_to_notion_properties(self, title, status, database_config=None, ...):
    title_property_name = "Name"
    if database_config and database_config.title_property_name:
        title_property_name = database_config.title_property_name
    properties = {title_property_name: NotionClient.build_title_property(title)}

    if database_config and database_config.status_property_name:
        status_property_name = database_config.status_property_name
        notion_status = self._get_notion_status(status, database_config)
        if notion_status:
            if database_config.status_property_type == "select":
                properties[status_property_name] = NotionClient.build_select_property(notion_status)
            else:
                properties[status_property_name] = NotionClient.build_status_property(notion_status)

    if database_config and database_config.creator_property_name:
        # ... people 型 or rich_text 型で書き込み ...
    return properties
```

**設定にない列には絶対に値を入れない**。`properties` 辞書には `title_property_name` / `status_property_name` / `creator_property_name` の 3 種しか key が入らないのが見れば分かる。AI agent が「他のプロパティも書いた方が便利そう」と判断しても、ここを通る限り書き込み先は設定済みの 3 列に閉じる。

`status_mapping` も同じ思想で、Notion 側の status 名と内部 PRDStatus の対応を **DB に明示的に持つ**。

```
def _get_notion_status(self, prd_status, database_config=None):
    if database_config and database_config.status_mapping:
        for mapping in database_config.status_mapping:
            if mapping.get("internal_status") == prd_status.value:
                return mapping.get("notion_status")
        # マッピング外は status を書き換えないために None を返す
        return None
```

`status_mapping` に存在しない PRDStatus は **None を返して書き込みをスキップ**。これで、Notion 側で独自カラム値を運用しているチームに対して、AI が勝手に「Done」みたいな値を書き戻すルートを塞げる。

書き込み境界をエンティティで持つと、unit test で「この設定下では status は書かれない」「creator が people 型で Notion ユーザーが見つからなければ creator 列は空のまま」が押さえられる。文字列 prompt や CLAUDE.md に「○○には書かないこと」と書く方式は、テストできない時点で本番で守れる気がしなかった。

## 学び: Canonical = Notion でも、DB は「同期状態」を持つ場所になる

5 つ振り返って共通する反省は 1 つ。**「canonical を Notion に置く」と決めた瞬間、DB 側の責務は『Notion のコピー』ではなく『Notion との同期状態を管理する場所』に変わる**、というところを最初は見誤っていた。

* 同期メタ(`notion_synced_at`)を **DB の値とは別カラム** で持つ(落とし穴 1, 2)
* rate limit は webhook では解決せず、**polling + queue + jitter** で抑え込む(落とし穴 3)
* Notion 側のモデル(コメントスレッド、自由なプロパティ)と DB モデルが一致しない部分は、**round-trip しないと決め切る**(落とし穴 4)
* AI / コードの書き込み範囲は **設定エンティティで明示的に閉じる**。convention や prompt では守れない(落とし穴 5)

特に 5 つ目は、AI を入れるパイプラインを組んでいる人がよくハマる気がする。LLM を信じて自由度を上げるとデータ事故が起きるし、絞り過ぎると AI が機能しない。設定エンティティとして持って UI から触れる形に倒すと、両方の自由度が上がる。

## おわりに

書きながら振り返ると、踏んだ罠の 8 割は **同期メタ・タイムゾーン正規化・書き込み境界** の 3 つに集約されていた。Notion を canonical にするのはビジネス側との接点として強力だが、DB 側の同期実装の重さは最初に見積もり切れていなかった。

似たような構成を組んでる人で、自分が踏んでない別の罠があれば聞いてみたい。特に「formula プロパティの扱い」「複数ワークスペースに跨る同期」「Notion 側 DB スキーマ変更の検知」は、自分の中でまだ綺麗な答えが出ていないので、誰かのやり方を真似したい。
