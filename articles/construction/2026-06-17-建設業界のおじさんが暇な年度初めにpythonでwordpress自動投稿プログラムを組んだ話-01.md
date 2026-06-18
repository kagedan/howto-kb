---
id: "2026-06-17-建設業界のおじさんが暇な年度初めにpythonでwordpress自動投稿プログラムを組んだ話-01"
title: "建設業界のおじさんが、暇な年度初めにPythonでWordPress自動投稿プログラムを組んだ話"
url: "https://qiita.com/ijiDX/items/05ea9973f290b147f2d6"
source: "qiita"
category: "construction"
tags: ["prompt-engineering", "API", "OpenAI", "GPT", "Python", "construction"]
date_published: "2026-06-17"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

![1671830f-9d0b-4e00-b662-80ab80c79370.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/255261/dea9ce58-3bf7-45b2-a961-ac321e909232.png)


ChatGPTで仕様を固め、Claudeに実装させ、OpenAI APIとWordPress REST APIで記事下書きまで自動化した記録です。なお、公開ボタンだけは人間が押します。

---

## はじめに

建設業界は、年度末が地獄です。

成果品、検査、納品、請求、修正、電子納品、なぜか最後に増えるExcel、そして「これ前から言ってましたよね？」みたいなイベントが年度末に集まります。

一方で、年度初めになると急に静かになることがあります。

現場もまだ本格化していない。
発注もまだ動ききっていない。
メールも少ない。
電話も少ない。

つまり、建設業界のおじさんにとっては、まれに訪れる「暇な年度初め」です。

そこで、前から欲しかったものを作りました。

**記事ネタからWordPress下書きまでを自動で作るローカルPythonプログラム**です。

タイトルでは「自動投稿」と書きましたが、実際にはWordPressに**下書き保存**するところまでです。

公開ボタンは人間が押します。

ここは意図的に自動化しませんでした。

---

## 作ったもの

ざっくり言うと、こういう流れのプログラムです。

```text
[人間 / ChatGPT]
  記事ネタ・方針を整理
        ↓
[ローカルPython]
  入力を読み込み、記事生成APIへ渡す
        ↓
[OpenAI API]
  記事タイトル・本文・メタ情報などを生成
        ↓
[WordPress REST API]
  WordPressへ下書き保存
        ↓
[人間]
  管理画面で確認・修正・手動公開
```

やっていること自体は、そこまで複雑ではありません。

* 記事ネタを用意する
* Pythonが記事生成APIを呼ぶ
* 生成結果をWordPress投稿用データにする
* WordPress REST APIで下書き保存する
* アイキャッチ画像があればメディアにアップロードして設定する
* 人間が最後に確認して公開する

実際に作ってみると、難しかったのはコードそのものよりも、**どこまで自動化しないか**でした。

---

## なぜ作ったのか

自分は建設コンサル系の実務をやっています。

道路、橋梁、河川、点検、調書、Excel、Word、GIS、電子納品。
そういう泥臭い実務です。

その一方で、自分のサイトも運営しています。

WordPressに記事を書く。
タイトルを入れる。
本文を入れる。
タグを入れる。
カテゴリを入れる。
アイキャッチを設定する。
メタディスクリプションを確認する。
下書き保存する。

これが地味に面倒でした。

特に、複数サイトを運用し始めると、毎回の投稿作業が微妙に重い。

そこで考えました。

「記事の最終判断は人間がやるとして、下書き作成までは機械にやらせればよくないか？」

というわけで、暇な年度初めに作りました。

---

## 最初に決めたこと

最初に決めたのは、技術ではなく方針です。

```python
POST_STATUS = "draft"
ALLOW_PUBLISH = False
ALLOW_DELETE = False
ALLOW_OVERWRITE_PUBLISHED = False
```

技術的には、WordPress REST APIで `publish` することもできます。

でも今回はやりませんでした。

AIが書いた記事をそのまま公開するのは怖いです。

間違いもあるし、言いすぎもあるし、文脈を外すこともある。

だから、プログラムは**下書き保存まで**にしました。

これは制限ではなく、設計判断です。

---

## ChatGPTとClaudeの分業

今回、コードはClaudeにかなり書いてもらいました。

ただし、丸投げはしていません。

自分の使い分けはこんな感じです。

```text
ChatGPT:
  - やりたいことの整理
  - 処理の流れの整理
  - Claudeに渡す仕様の整理
  - 例外処理方針の整理

Claude:
  - Python実装
  - エラー修正
  - 差分修正
  - リファクタリング

人間:
  - 目的を決める
  - 自動化しない範囲を決める
  - ローカルで動作確認する
  - WordPress下書きを確認する
  - 最終公開する
```

ここで一番大事だったのは、**Claudeに曖昧な状態で丸投げしないこと**でした。

Claudeは実装が速いです。
でも、仕様が曖昧だと普通にブレます。

なので先にChatGPT側で、

* 何をするか
* 何をしないか
* どの状態を成功とするか
* どの状態なら止めるか
* どの処理は人間に残すか

を決めました。

そのうえで、Claudeには「この方針で実装して」と渡しました。

---

## OpenAI APIで記事データを作る

OpenAI API側では、記事の材料を渡して、WordPress投稿用のデータを返してもらいます。

イメージとしてはこうです。

```python
def build_article_prompt(common_rule: str, article_seed: dict) -> str:
    return f"""
あなたは日本語のWordPress記事作成担当です。
以下の共通ルールと記事情報に従って、WordPress下書き用の記事データを作成してください。

# 共通ルール
{common_rule}

# 記事情報
{article_seed}

# 出力してほしい項目
- title
- body_markdown
- slug
- meta_description
- tags
- category
- eyecatch_prompt
"""
```

ここで地味に重要だったのは、**ChatGPT画面のスレッド文脈はAPIに自動では引き継がれない**ということです。

ChatGPTでどれだけ議論していても、APIに渡さなければモデルは知りません。

なので、記事生成時に毎回必要なルールと記事情報を渡す形にしました。

---

## WordPress REST APIで下書きを作る

WordPress側はREST APIを使いました。

下書き作成だけなら、考え方はかなりシンプルです。

```python
import requests
from requests.auth import HTTPBasicAuth

def create_wordpress_draft(
    base_url: str,
    username: str,
    app_password: str,
    title: str,
    content: str,
    slug: str,
    category_ids: list[int],
    tag_ids: list[int],
    featured_media_id: int | None = None,
) -> dict:
    endpoint = f"{base_url.rstrip('/')}/wp-json/wp/v2/posts"

    payload = {
        "title": title,
        "content": content,
        "status": "draft",
        "slug": slug,
        "categories": category_ids,
        "tags": tag_ids,
        "comment_status": "closed",
        "ping_status": "closed",
    }

    if featured_media_id:
        payload["featured_media"] = featured_media_id

    response = requests.post(
        endpoint,
        json=payload,
        auth=HTTPBasicAuth(username, app_password),
        timeout=30,
    )

    response.raise_for_status()
    return response.json()
```

もちろん、実際にはもう少し周辺処理が必要です。

* カテゴリ名からIDを取る
* タグがなければ作る
* 同じslugがないか確認する
* アイキャッチをアップロードする
* エラー時にログを残す
* 処理済みの記事を記録する

ただ、全部を記事に書くと内製ツールの中身を出しすぎるので、ここでは考え方が伝わる程度にします。

---

## WordPress Application Passwordを使う

WordPressの通常ログインパスワードをPythonに持たせるのは嫌だったので、Application Passwordを使いました。

`.env` はこんなイメージです。

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

WP_BASE_URL=https://example.com
WP_USERNAME=example_user
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

MAX_ITEMS_PER_RUN=3
```

実際の値は当然公開しません。

ローカルツールでも、`.env` はGit管理から外します。

```gitignore
.env
logs/
generated/
```

このへんは普通の話ですが、自分用ツールほど雑になりがちなので、最初に分けておく方が安心です。

---

## カテゴリIDを取る

WordPress REST APIで投稿する場合、カテゴリは名前ではなくIDで渡します。

なので、カテゴリ名からIDを引く処理が必要です。

かなり単純化するとこうです。

```python
def get_category_id(base_url: str, auth, category_name: str) -> int:
    endpoint = f"{base_url.rstrip('/')}/wp-json/wp/v2/categories"

    response = requests.get(
        endpoint,
        params={"search": category_name},
        auth=auth,
        timeout=30,
    )
    response.raise_for_status()

    categories = response.json()

    for category in categories:
        if category.get("name") == category_name:
            return category["id"]

    raise ValueError(f"Category not found: {category_name}")
```

カテゴリについては、自動作成せず、WordPress側で先に用意しておく運用にしました。

カテゴリはサイト構造に関わるので、プログラムが勝手に増やすと後で整理が面倒になるからです。

---

## タグは必要に応じて作る

一方で、タグは記事単位で増えてもそこまで致命傷になりにくいので、存在しなければ作る運用にしました。

```python
def get_or_create_tag_id(base_url: str, auth, tag_name: str) -> int:
    endpoint = f"{base_url.rstrip('/')}/wp-json/wp/v2/tags"

    search_response = requests.get(
        endpoint,
        params={"search": tag_name},
        auth=auth,
        timeout=30,
    )
    search_response.raise_for_status()

    for tag in search_response.json():
        if tag.get("name") == tag_name:
            return tag["id"]

    create_response = requests.post(
        endpoint,
        json={"name": tag_name},
        auth=auth,
        timeout=30,
    )
    create_response.raise_for_status()

    return create_response.json()["id"]
```

このへんは地味ですが、実際に自動投稿っぽいことをしようとすると避けて通れません。

記事本文だけ作れても、カテゴリやタグで止まると面倒です。

---

## アイキャッチ画像をアップロードする

アイキャッチ画像は、Pythonで生成するのではなく、人間がAI画像生成などで用意します。

Python側では、画像ファイルがあればWordPressのメディアライブラリへアップロードして、投稿の `featured_media` に設定します。

```python
from pathlib import Path

def upload_media(
    base_url: str,
    auth,
    image_path: Path,
) -> int:
    endpoint = f"{base_url.rstrip('/')}/wp-json/wp/v2/media"

    headers = {
        "Content-Disposition": f'attachment; filename="{image_path.name}"',
        "Content-Type": "image/png",
    }

    with image_path.open("rb") as f:
        response = requests.post(
            endpoint,
            headers=headers,
            data=f,
            auth=auth,
            timeout=60,
        )

    response.raise_for_status()
    return response.json()["id"]
```

これで返ってきた `media_id` を、投稿作成時の `featured_media` に渡します。

```python
media_id = upload_media(base_url, auth, image_path)

post = create_wordpress_draft(
    base_url=base_url,
    username=username,
    app_password=app_password,
    title=title,
    content=content,
    slug=slug,
    category_ids=category_ids,
    tag_ids=tag_ids,
    featured_media_id=media_id,
)
```

これで、WordPress管理画面上ではアイキャッチつきの下書きとして確認できます。

---

## 複数サイト対応

複数のWordPressサイトを扱いたかったので、投稿先サイトを切り替えられるようにしました。

考え方は単純です。

```python
def get_site_config(site_key: str, env: dict) -> dict:
    prefix = site_key.upper()

    return {
        "base_url": env[f"{prefix}_WP_BASE_URL"],
        "username": env[f"{prefix}_WP_USERNAME"],
        "app_password": env[f"{prefix}_WP_APP_PASSWORD"],
    }
```

`.env` 側はこういうイメージです。

```env
SITE_A_WP_BASE_URL=https://site-a.example.com
SITE_A_WP_USERNAME=user_a
SITE_A_WP_APP_PASSWORD=xxxx xxxx xxxx xxxx

SITE_B_WP_BASE_URL=https://site-b.example.com
SITE_B_WP_USERNAME=user_b
SITE_B_WP_APP_PASSWORD=yyyy yyyy yyyy yyyy
```

実際には、記事ごとにどのサイトへ投げるかを持たせています。

ここも具体的な管理方法まで書くと長くなるので、今回は概念だけにします。

---

## 処理件数を制御する

一度に何十件も投げると、確認が大変です。

そこで、1回の実行件数を `.env` で制御できるようにしました。

```python
def get_max_items_per_run(env: dict, default: int = 1) -> int:
    value = env.get("MAX_ITEMS_PER_RUN", str(default))

    try:
        max_items = int(value)
    except ValueError:
        return default

    return max(1, max_items)
```

使う側はこうです。

```python
max_items = get_max_items_per_run(env, default=1)

for article in pending_articles[:max_items]:
    process_article(article)
```

最初から10件、20件と走らせるより、まずは1件、次に3件くらいで試す方が安全です。

自動化は、成功するとつい件数を増やしたくなります。
でも、WordPressの下書きが大量にできても、最後に読むのは人間です。

ここは地味に大事です。

---

## エラーは止めずにログへ逃がす

こういう自動化で一番イヤなのは、1件失敗しただけで全部止まることです。

なので、基本方針はこうしました。

```python
def run_batch(articles: list[dict]) -> None:
    for article in articles:
        try:
            process_article(article)
            write_log(article, result="success")
        except RecoverableArticleError as e:
            write_log(article, result="failed", message=str(e))
            continue
        except FatalEnvironmentError:
            raise
```

全部完璧に止めるより、どこで何が起きたか残して、後で直せるようにする。

この考え方は建設コンサルの実務にも近いです。

成果品でも、エラーが出た瞬間に全体を破壊するより、どこが不整合なのか記録して潰していく方が現実的です。

---

## 重複投稿は避ける

自動化で怖いのは、同じ記事を何度も作ってしまうことです。

なので、投稿前にslugの重複を確認します。

```python
def wordpress_slug_exists(base_url: str, auth, slug: str) -> bool:
    endpoint = f"{base_url.rstrip('/')}/wp-json/wp/v2/posts"

    response = requests.get(
        endpoint,
        params={"slug": slug, "status": "any"},
        auth=auth,
        timeout=30,
    )
    response.raise_for_status()

    return len(response.json()) > 0
```

使う側はこうです。

```python
if wordpress_slug_exists(base_url, auth, slug):
    raise RecoverableArticleError(f"Slug already exists: {slug}")
```

自動投稿系は、うまくいった時より、失敗した時の後始末が面倒です。

重複下書きが増えると、人間が確認するコストが上がります。

なので、ここは最初から入れました。

---

## 実際に動かしてみた

一通りの処理フローを組み上げて、ローカル環境で動作確認を行いました。

流れとしては、以下まで通っています。

```text
記事データ生成
↓
ローカル保存
↓
WordPressカテゴリ解決
↓
WordPressタグ作成
↓
アイキャッチ画像アップロード
↓
WordPress下書き作成
↓
投稿ID取得
↓
処理結果を記録
```

WordPress管理画面に、アイキャッチつきの下書きが作成されたのを確認しました。

この瞬間は普通にうれしかったです。

建設業界のおじさん、年度初めにPythonで記事作成の内製ラインを立ち上げました。

---

## 一般公開しない理由

ここまで作ると、少し考えます。

「これ、公開したら誰か使うのでは？」

ただ、すぐにやめました。

理由は明確です。

```text
公開すると、たぶんサポートが本体になる
```

想定される詰まりどころはいくらでもあります。

* OpenAI APIキー取得
* WordPress Application Password
* WordPress REST APIの権限
* サーバー設定
* SSL
* カテゴリ・タグ
* 画像アップロード権限
* テーマやプラグイン差分
* API仕様変更
* 生成結果の品質確認

自分用ローカルツールなら強いです。

でも一般公開すると、たぶん「使い方がわかりません」「APIキーって何ですか」「WordPressに投稿できません」が大量に来ます。

やるならWebアプリ化やSaaS化が必要です。

しかし、それはまた別の事業です。

なので今回は、公開ツールではなく、**内製ライン**として使うことにしました。

---

## コードを書くより、境界線を決める方が大事だった

今回やって思ったのは、AI時代の開発では、コードを書く力よりも、

**どこまで機械にやらせるかを決める力**

の方が大事だということです。

Claudeはかなり実装してくれます。

ただし、仕様が曖昧だと普通に迷います。

逆に、方針が固まっていると速いです。

今回効いたのはこの順番でした。

```text
1. ChatGPTでやりたいことを整理する
2. 自動化する範囲としない範囲を決める
3. Claudeに実装させる
4. ローカルで動かす
5. エラーだけClaudeに返す
6. 差分修正する
```

AIに丸投げするのではなく、AIに投げる前の境界線を決める。

これが一番効きました。

---

## 自動化できることを、あえて自動化しない

今回の一番のポイントは、ここだと思っています。

* 記事生成は自動化する
* WordPress下書き保存も自動化する
* アイキャッチ設定も自動化する
* でも公開は自動化しない
* 公開済み記事の上書きもしない
* 削除もしない

この線引きが大事でした。

全部自動化できるから全部やる、ではありません。

自動化すると危ないところは、人間に残す。

この設計にしたことで、実務で使える安心感がかなり上がりました。

---

## まとめ

暇な年度初めに、PythonでWordPress自動投稿プログラムを組みました。

正確には、WordPressに**下書き投稿**するプログラムです。

作ってみて感じたことは以下です。

* OpenAI APIとWordPress REST APIをつなぐこと自体は難しくない
* 難しいのは運用設計
* 自動公開しない判断はかなり大事
* ChatGPTは方針整理、Claudeは実装に向いている
* 作れることと、一般公開できることは違う
* 自分用ローカルツールとしてはかなり強い
* 建設業界のおじさんでも、年度初めの空白時間とAIがあれば内製ラインは組める

ただし、公開ボタンだけは人間が押す。

ここは、今後もしばらく譲らないと思います。


Python、OpenAI API、WordPress REST APIを使って、WordPress下書きをローカル環境から自動作成する仕組みを作りました。

全体の背景や運用方針はこちらにまとめています。
https://ijidx.jp/2026/06/17/python%e3%81%a7wordpress%e4%b8%8b%e6%9b%b8%e3%81%8d%e3%82%92%e8%87%aa%e5%8b%95%e4%bd%9c%e6%88%90%e3%81%99%e3%82%8b%e4%bb%95%e7%b5%84%e3%81%bf%e3%82%92%e4%bd%9c%e3%81%a3%e3%81%9f%e8%a9%b1%ef%bd%9copena/

この記事では、実装寄りのポイントだけを整理します。
