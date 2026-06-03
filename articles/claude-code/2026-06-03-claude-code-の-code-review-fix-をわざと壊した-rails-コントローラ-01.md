---
id: "2026-06-03-claude-code-の-code-review-fix-をわざと壊した-rails-コントローラ-01"
title: "Claude Code の /code-review --fix を「わざと壊した Rails コントローラ」で検証する — AI が直す境界と、人が判断すべき境界"
url: "https://qiita.com/jijimama/items/3a9da58cc464cc0be15d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-06-03"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

## なぜこの検証をしたか

Claude Code に `/code-review --fix`（レビューの指摘を作業ツリーに自動適用する）が入った。便利そうだが、コードレビューを **自動修正まで** 任せるとなると、気になるのは精度より **境界** だ。

- どこまでを自動で直してくれるのか
- 逆に、**直さずに残す**（＝人が判断すべき）と AI が判断するのはどこか

「全部それっぽく書き換えてしまう」ツールは、業務の PR では危なくて使えない。
そこで、**わざとアンチパターンを5つ仕込んだ Rails コントローラ** を用意して、`/code-review --fix` に通し、その挙動を観察した記録をまとめる。

結論を先に書くと:

> `/code-review --fix` は「**コードの中だけで閉じる問題は直し、差分の外（マイグレーション等）に及ぶ問題は直さずに指摘で残す**」という振る舞いをした。
> 一番おもしろかったのは、**AI があえて直さなかった1件**（`find_or_create_by` の race condition）。これは DB の UNIQUE 制約が必要で、コントローラのコードをいくらいじっても直らない。

## 検証環境

- Claude Code v2.1.161（`/code-review --fix` 自体は **v2.1.152** で追加された機能）
  - 出典: [Claude Code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
    > `/code-review --fix` applies findings to working tree
- 題材: ローカルに作った検証用 git リポジトリ（リモートなし・完全にローカル完結）
- 言語/FW: Ruby on Rails（コントローラ1ファイル）

`/code-review` は **git の差分** をレビュー対象にする。
そこで「きれいな状態を baseline コミット → わざと壊した変更を加える」ことで、
**壊した差分だけ** をレビューさせた。

## 題材: わざと壊した Rails コントローラ

baseline（きれいな状態）はこれ:

```ruby
class TagsController < ApplicationController
  def index
    @tags = Tag.order(:name)
    render json: @tags
  end
end
```

ここに、決済・管理系の Rails でありがちな問題を **5つ** 意図的に足した差分を作る:

```ruby
class TagsController < ApplicationController
  def index
    @tags = Tag.order(:name)
    render json: @tags
  end

  def search
    # 1. SQL インジェクション: パラメータを文字列展開している
    @tags = Tag.where("name LIKE '%#{params[:q]}%'")

    # 2. N+1 クエリ: 各 tag の posts をループ内で都度参照
    @result = @tags.map do |tag|
      { name: tag.name, post_count: tag.posts.count, author: tag.posts.first.user.name }
    end

    render json: @result
  end

  def create
    # 3. UNIQUE 制約に依存しない find_or_create_by（race condition）
    tag = Tag.find_or_create_by(name: params[:name])

    # 4. 例外を握りつぶしている（原因が追えない）
    begin
      tag.update(description: params[:description])
    rescue => e
      nil
    end

    # 5. マスアサインメント: params をそのまま渡している
    Tag.create(params[:tag])

    render json: tag
  end
end
```

仕込んだ問題:

| # | 種類 | 危険度 |
|---|---|---|
| 1 | SQL インジェクション | 致命的（任意条件の注入） |
| 2 | N+1 クエリ + nil 参照クラッシュ | 高 |
| 3 | `find_or_create_by` の race condition | 高（重複データ） |
| 4 | 例外の握りつぶし | 中（原因追跡不能） |
| 5 | マスアサインメント | 高（不正な属性書き換え） |

## `/code-review --fix` が出した指摘

`/code-review --fix` を実行した結果、**5件すべてを検出**した。指摘の要約:

| # | file:line | 指摘 | 失敗シナリオ |
|---|---|---|---|
| 1 | `tags_controller.rb:9` | SQL インジェクション | `q=%' OR 1=1 --` で全件取得・任意条件注入 |
| 2 | `tags_controller.rb:13` | `tag.posts.first.user.name` が nil 参照でクラッシュ | posts が空の tag で `.first`→nil→NoMethodError |
| 3 | `tags_controller.rb:13` | N+1: ループ内で `posts.count` / `posts.first` を都度クエリ | tag が N 件なら 2N+ 回の追加クエリ |
| 4 | `tags_controller.rb:24` | 例外の握りつぶし + `update` の失敗無視 | 検証失敗や例外が無言で消え追跡不能 |
| 5 | `tags_controller.rb:29` | マスアサインメント（戻り値も未使用） | 許可しない属性を外部から書き換え可能 |

注目したいのは、**N+1 の指摘に「nil 参照クラッシュ」が分離して入っている**こと。
`tag.posts.first.user.name` は N+1 であると同時に、posts が空なら `.first` が nil になり`NoMethodError` で落ちる。**1行に2つの異なる障害が同居している** のを、別々の指摘として挙げてきた。

## 自動修正の中身を、公式根拠つきで1つずつ読む

`--fix` 適用後のコード:

```ruby
class TagsController < ApplicationController
  def index
    @tags = Tag.order(:name)
    render json: @tags
  end

  def search
    # バインド変数で渡し、LIKE のメタ文字(%, _)もエスケープする
    pattern = "%#{Tag.sanitize_sql_like(params[:q])}%"
    # posts と user を事前ロードして N+1 を避ける
    @tags = Tag.where("name LIKE ?", pattern).includes(posts: :user)

    @result = @tags.map do |tag|
      first_post = tag.posts.first
      {
        name: tag.name,
        post_count: tag.posts.size,      # ロード済み association を使い追加クエリを出さない
        author: first_post&.user&.name   # posts や user が無くても nil で安全
      }
    end

    render json: @result
  end

  def create
    tag = Tag.find_or_create_by(name: params[:name])

    # 失敗を握りつぶさず、検証エラーは例外として呼び出し元へ伝える
    tag.update!(description: params[:description])

    render json: tag
  end
end
```

修正の各論を、Rails 公式の根拠と一緒に確認する。

### 1. SQL インジェクション → バインド変数 + `sanitize_sql_like`

```ruby
# before
Tag.where("name LIKE '%#{params[:q]}%'")
# after
pattern = "%#{Tag.sanitize_sql_like(params[:q])}%"
Tag.where("name LIKE ?", pattern)
```

`?` のプレースホルダで値を **バインド変数** として渡すのが第一。
加えて、LIKE の場合は値自体に含まれる `%` `_` がワイルドカードとして悪用されうるので、`sanitize_sql_like` でエスケープしている。ここまでやるのは丁寧で、評価できる。

> Sanitizes the given LIKE pattern by escaping the `_` (underscore) and `%` (percent) characters.
> — [ActiveRecord::Sanitization::ClassMethods#sanitize_sql_like](https://api.rubyonrails.org/classes/ActiveRecord/Sanitization/ClassMethods.html#method-i-sanitize_sql_like)

### 2. マスアサインメント → 行ごと削除

```ruby
# before
Tag.create(params[:tag])   # ← 削除された
```

`params` を直接 `create` に渡すのは Strong Parameters 違反。
ここで AI は「**修正して残す**」ではなく **行ごと削除** した。
理由は、この行が **戻り値も使われておらず、tag を二重生成するだけの無意味なコード** だったから。「直す」より「消す」が正しいケースを見分けている。

> Action Controller parameters are forbidden to be used in Active Model mass assignments
> until they have been permitted.
> — [Rails Guides — Strong Parameters](https://guides.rubyonrails.org/action_controller_overview.html#strong-parameters)

（もし「正しく permit して残す」べきコードなら`params.require(:tag).permit(:name, ...)` になる。今回は不要な行だったため削除が妥当だった。）

### 3. nil 参照クラッシュ → ぼっち演算子

```ruby
# before
author: tag.posts.first.user.name
# after
first_post = tag.posts.first
author: first_post&.user&.name
```

posts が空、または post に user が無いケースで `&.`（safe navigation operator）によりnil を返して落ちないようにしている。

### 4. N+1 → `includes` + ロード済み association の利用

```ruby
# before
@tags = Tag.where(...)              # posts/user は都度クエリ
post_count: tag.posts.count         # 毎回 COUNT クエリ
# after
@tags = Tag.where(...).includes(posts: :user)   # 事前ロード
post_count: tag.posts.size          # ロード済みなら追加クエリなし
```

`includes` で eager load する定番の N+1 対策。
さらに `.count`（常に SQL を撃つ）を `.size`（association がロード済みなら Ruby 側で数える）に変えているのが細かい。

> To eager load associated records when they are accessed, use the `includes` method.
> — [Rails Guides — Eager Loading Associations](https://guides.rubyonrails.org/active_record_querying.html#eager-loading-associations)

### 5. 例外握りつぶし → `update!`

```ruby
# before
begin
  tag.update(description: params[:description])
rescue => e
  nil   # ← 失敗が無言で消える
end
# after
tag.update!(description: params[:description])
```

`update`（失敗時 false を返すだけ）+ 例外握りつぶしを、`update!`（失敗時に例外を送出）に変更。
検証失敗を **無言で握りつぶさず呼び出し元へ伝える** 方向に倒している。

> update! ... Raises a `RecordInvalid` error if validations fail.
> — [ActiveRecord::Persistence#update!](https://api.rubyonrails.org/classes/ActiveRecord/Persistence.html#method-i-update-21)

## 一番の収穫: AI が「あえて直さなかった」1件

5つ仕込んだうち **4つは自動修正された**。残る1つ、`find_or_create_by` の race condition は **直さずに指摘だけ残した**。

これが今回の検証で一番価値のある挙動だった。

```ruby
# このまま残された
tag = Tag.find_or_create_by(name: params[:name])
```

なぜ直さなかったのか。`find_or_create_by` は内部で SELECT → なければ INSERT を行うが、これは **アトミックではない**。

> Please note this method is **not atomic**, it runs first a SELECT,
> and if there are no results an INSERT is attempted.
> — [Rails API — find_or_create_by](https://api.rubyonrails.org/classes/ActiveRecord/Relation.html)

同時リクエストが「両方とも SELECT で見つからない」と判断すると、**両方が INSERT して重複行ができる**。
そして **これを本当に防ぐのはアプリのコードではなく、DB の UNIQUE 制約** だ。制約があって初めて、二重 INSERT を DB が弾き、Rails 側の `rescue RecordNotUnique` が機能する。

つまりこの問題の正しい修正は:

```ruby
# マイグレーション（= レビュー中のコントローラ差分の「外」）
add_index :tags, :name, unique: true
```

であって、**コントローラのコードをいくら書き換えても直らない**。
`/code-review --fix` は、これを **差分の範囲外に及ぶ修正** と判断して手を出さず、指摘として残した。これは「AI に自動修正させる」上で、むしろ **信頼できる挙動** だ。
全部を機械的に書き換えるのではなく、**コードの中で閉じない問題は人に判断を委ねる**。

## この検証から決めた自分の運用ルール

`/code-review --fix` を業務の PR で使うときに、現在の自分が守ること:

1. **PR を作る前のブランチで回す**。差分（未コミットの作業ツリー変更も含む）に対して走るので、コミット前のレビューに向く。
2. **自動修正を鵜呑みにせず、必ず `git diff` で人間が確認する**。
   `--fix` は「直せるものだけ直し、範囲外/挙動変更は指摘で残す」挙動だが、採否の最終判断は人がやる。
3. **「直されなかった指摘」こそ精読する**。今回の race condition のように、**コードの外（マイグレーション・インフラ・設計）に原因がある問題** が残されている可能性が高い。そこが一番効くレビューになる。

要するに、`/code-review --fix` は **一次レビュアー** として優秀だが、**最終レビュアーは人間**、という線引きで使う。


## まとめ

| 仕込んだ問題 | `/code-review --fix` の対応 |
|---|---|
| SQL インジェクション | 自動修正（バインド変数 + `sanitize_sql_like`） |
| nil 参照クラッシュ | 自動修正（`&.`） |
| N+1 | 自動修正（`includes` + `.size`） |
| 例外握りつぶし | 自動修正（`update!`） |
| マスアサインメント | 自動修正（無意味な行を削除） |
| **`find_or_create_by` の race** | **直さず指摘で残す（DB 制約=差分外のため）** |

`/code-review --fix` の価値は「自動で直してくれること」だけではなく、**直せる境界と直せない境界を分けてくれること** にある。
コードの中で閉じる問題は直し、設計・DB に及ぶ問題は人に渡す。
この境界が信頼できるからこそ、業務の一次レビューに組み込める。


## 参考

- [Claude Code CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) — `/code-review --fix` は v2.1.152 で追加
- [ActiveRecord::Sanitization::ClassMethods#sanitize_sql_like](https://api.rubyonrails.org/classes/ActiveRecord/Sanitization/ClassMethods.html#method-i-sanitize_sql_like)
- [Rails Guides — Strong Parameters](https://guides.rubyonrails.org/action_controller_overview.html#strong-parameters)
- [Rails Guides — Eager Loading Associations](https://guides.rubyonrails.org/active_record_querying.html#eager-loading-associations)
- [ActiveRecord::Persistence#update!](https://api.rubyonrails.org/classes/ActiveRecord/Persistence.html#method-i-update-21)
- [Rails API — find_or_create_by](https://api.rubyonrails.org/classes/ActiveRecord/Relation.html)

## 再現手順（実際に叩いたコマンド）

```bash
# 1. 検証用リポジトリを用意（リモートなし・ローカル完結）
mkdir -p code-review-fix/app/controllers && cd code-review-fix
git init
git config user.email "lab@example.com"
git config user.name  "lab"

# 2. きれいな baseline をコミット
cat > app/controllers/tags_controller.rb <<'RUBY'
class TagsController < ApplicationController
  def index
    @tags = Tag.order(:name)
    render json: @tags
  end
end
RUBY
git add -A && git commit -m "baseline: TagsController#index"

# 3. わざとアンチパターンを仕込んだ差分を作る（本文の「壊したコード」に差し替え）
#    → これで git diff に5つの問題が乗る

# 4. Claude Code でレビュー＋自動修正
#    /code-review --fix

# 5. 自動修正の結果を人間が確認
git diff HEAD
```
