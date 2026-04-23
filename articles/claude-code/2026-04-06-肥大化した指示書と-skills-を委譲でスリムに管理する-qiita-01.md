---
id: "2026-04-06-肥大化した指示書と-skills-を委譲でスリムに管理する-qiita-01"
title: "肥大化した指示書と skills を委譲でスリムに管理する - Qiita"
url: "https://qiita.com/ymatsukawa/items/502adfab4d0fa09c9f8b"
source: "qiita"
category: "claude-code"
tags: ["qiita"]
date_published: "2026-04-06"
date_collected: "2026-04-06"
summary_by: "auto-rss"
query: ""
---

```
@{指示書までのパス}.md に記載されたワークフローを実行せよ。/coding-standard-skill に従え
```

こんなプロンプトを何度も実行してきた。

その中で、大抵こんなことが起きる

* 指示書やスキルが、神クラスみたいに太る
* 大きい時は800行
* 管理しきれない

ここでいう「管理」とは、

* 無思考にAIへ丸投げせず
* 人間が意味を理解できるように、運用保全できる

という意味だ。

どうやれば、管理可能にできるのか？

この記事にはその手法を示している。

**対象読者**

* claude code にて、簡易的にでもカスタムスキルを構築したことがある人
* 指示書およびカスタムスキルの整理方法を探している人

## 構築の大きな流れ

* 人間の作業
  + 構築原則の確認
  + `{指示書}.md` を構築
  + `.claude/skills` を構築
  + `.claude/skills/xxx-skill/references` を構築
* AIと人間の作業
  + `AskUserQuestionTool` を使ってレビュー
* 最終確認

## 構築原則の確認

* `.md` はシンプルにする
* 専門知識は `.claude/skills` へ
* 具体例やコードは `.claude/skills/xxx-skill/references` へ

**オブジェクト指向で言えば `.md` はクラスである。**

詰め込みすぎれば「神クラス」へ変貌し、分かりづらくなる。

従って、クラス単位(.md 単位)で、委譲をすべきである。

## `{指示書}.md` を構築

以下様式に従った md を構築する。

構築時は内容に粗があっても問題ない。

```
# {プロジェクト名}
## ゴール
(プロジェクトで達成したいことを記述する)

## 実施理由
(なぜ、プロジェクトゴールが存在するかを記述する)

## ワークフロー
* [ ] `/xxx-skill` を使って xxx をする
* [ ] `/yyy-skill` を使って yyy をする
* [ ] `/zzz-skill` を使って zzz をする

## 禁則事項
* [ ] ... すること
* [ ] ... すること
```

`{指示書}.md` に置くのは上記四項目のみ。それ以外は以下二つに分離する。

* `.claude/skills`: やってほしいこと
* `.claude/skills/xxx-skill/references`: 具体的な例

<構築例>

```
# 単体テスト構築サブプロジェクト
## ゴール
技術負債を安全に解消し、1ヶ月に1回のリリースサイクルを2週間に1回へ短縮する。

## 実施理由
直下のソース群は、1年前にリリースした。しかし、コードが全体的に複雑化している。
そのため、以下の問題が発生している。

* 設計見通しが悪く、改修見積もりに想定の1.5倍以上かかる
* 影響範囲を特定しづらい
* 総じて、バグが生まれやすい

これらの問題を解消するため

* (1) 単体テスト構築
* (2) リファクター

の段取りをしたい。まずは、足がかりに (1) 単体テスト構築を実施したい。

## ワークフロー
* [ ] `/overview-skill` より、対象および関連コードの設計調査をする
* [ ] `/planning-unit-test-skill` より、単体テスト計画を立てる
* [ ] `/make-unit-test-skill` より、単体テストの構築と検証する
  * [ ] テスト失敗時は、同スキルの指示に従うこと

## 禁則事項
* [ ] `src/**/*` の実装ファイルを編集すること
* [ ] `env.example` を編集すること
```

## `.claude/skills` を構築

スキルも同様に次の様式に従って書く。

```
---
name: xxx-skill
description: (1. 何をするスキルか 2. いつ呼ばれるべきか を記述)
---

# XXX Skill
(一文で、何をするスキルかを記述)

## ゴール
(スキルのゴールを記述)

## 3つの原則
(スキル実施に従ってほしい原則を記述)
* [ ] xxx であること
* [ ] yyy であること
* [ ] zzz であること

## ワークフロー
* [ ] `/xxx-skill` を使って yyy をする
* [ ] `/yyy-skill` を使って xxx をする
* [ ] `/zzz-skill` を使って zzz をする

## 禁則事項
* [ ] xxx をすること
* [ ] yyy をすること

## 例
`.claude/skills/xxx-skill/references/xxx-example.md` を参照する
```

**補足**  
「3つの原則」が「スキルの外せない軸」になる。

配置するなら 2 から 5個の範囲内を推奨。

1個だけだとそれに引っ張られ、8個や10個にすると軸不定になりがちである。

**make-unit-test-skill の場合**

```
---
name: make-unit-test-skill
description: Golangの単体テスト(正常系/異常系)を構築し全件パスを確認する。planning-unit-test-skillの計画完了後に使用する。
---

# Make Unit Test Skill

## ゴール
Golang の単体テスト(正常系/異常系)を構築する。テスト構築後はテスト全件成功を確認する。

**重要事項**
スキル実行前に `/planning-unit-test-skill` が行われていること。
もしこのスキルが単体で行われた場合は、次の手順を踏むこと。
* [ ] "/planning-unit-test-skill の実行後に実施してください" という旨のエラーを出力
* [ ] ワークフローを停止

## 3つの原則
* [ ] テストケースはシンプルであること
* [ ] テストケースは機能網羅的であること
* [ ] テストケースが品質過剰ではないこと

**留意事項**
品質過剰とは、開発本位のテストであり、それ自体が開発者やユーザーへ価値を生まないことを指す

## ワークフロー
* [ ] (1) `/planning-unit-test-skill` から計画を受け取り、全容を把握する
* [ ] (2) テスト対象の、正常系を構築する
* [ ] (3) テスト対象の、異常系を構築する
* [ ] (4) `go test ./...` の全件パスを確認する
  * [ ] もし失敗した場合、テスト構築誤りを検証し、再構築する

## 禁則事項
* [ ] サフィックス `_test.go` がついていない、機能実装を修正すること

## 例
* テストに関するプラクティス例: `.claude/skills/make-unit-test-skill/references/unit-test-example.md`
* 過剰品質に関する例: `.claude/skills/make-unit-test-skill/references/over-testing-example.md`
```

## `.claude/skills/xxx-skill/references` を構築

例やコードを掲載する。  
OK/NG パターンの「比較」を記述すると、LLM 側の判断精度が高くなりやすい。

```
# {総称タイトル}

## パターン1: {パターン1 のタイトル}
**OK**:
(コードもしくは内容)

**NG**:
(コードもしくは内容)

## パターン2: {パターン2 のタイトル}

**OK**:
(コードもしくは内容)

**NG**:
(コードもしくは内容)
```

**テストプラクティスの場合: `.claude/skills/make-unit-test-skill/references/unit-test-example.md`**

```
# 単体テスト構築時のプラクティス

## パターン1: テストの待ち処理
待ち処理が必要な場合「同期」ではなく、go func の非同期待ち処理を設ける。

**NG**:
go startServer()
time.Sleep(100 * time.Millisecond)
// 検証をここで行う

**OK**:
serverReady := make(chan struct{})
go func() {
    startServer()
    close(serverReady)
}()

select {
case <-serverReady:
    // server is ready
case <-time.After(5 * time.Second):
    t.Fatal("server failed to start")
}
```

**過剰品質の場合: `.claude/skills/make-unit-test-skill/references/over-testing-example.md`**

```
# 品質過剰なテスト例
品質過剰とは、開発本位のテストであり、それ自体が開発者やユーザーへ価値を生まないことを指す。

## パターン1: コンストラクタ代入しただけの検証
引数をフィールドに代入しただけの関数を、全フィールド突合わせで検証する。

**NG**:
func NewUser(name string, age int) *User {
    return &User{Name: name, Age: age}
}

func TestNewUser(t *testing.T) {
    u := NewUser("Alice", 30)
    assert.Equal(t, "Alice", u.Name)
    assert.Equal(t, 30, u.Age)
}

**OK**:
// コンストラクタにバリデーションやデフォルト値設定がある場合のみテストする
func NewUser(name string, age int) (*User, error) {
    if name == "" {
        return nil, errors.New("name is required")
    }
    return &User{Name: name, Age: age, CreatedAt: time.Now()}, nil
}

func TestNewUser_EmptyName(t *testing.T) {
    _, err := NewUser("", 30)
    assert.Error(t, err)
}
```

ここまで「人の手と目」で構築したものを、claude code にレビューさせる。

* plan モードに切替。即時実行をやめさせる為
* 以下プロンプトを `{指示書}.md`、各スキルの SKILL.md に対して実行する

```
@{対象ファイルパス} にて、修正追加すべき箇所はあるかレビューをせよ。
精度を高めるため、質問事項がある場合は AskUserQuestion を行うこと。
```

質疑後、AI側に修正を行わせる。

## 最終確認

意図通りに動くかをテストする。

```
@{指示書}.md のワークフローに従って、@src/path/to/sample.go の単体テストを構築せよ
```

主に確認すべき観点は以下

* ワークフロー通りに動いているか
* 原則・禁則事項を守っているか
* references の例に沿っているか

意図通りでない場合、修正を重ねる。一発で動くことを期待しない。

# 全体補足

**`hooks` や `.claude/skills` の assets / scripts は配置しないのか？**  
本記事では最低限の構成に絞った為あえて詳述しなかった。  
ただし設計方針として以下の通り。

* hooks はワークフロー横断の関心事なのでスキルの外 (`.claude/hooks`)
* scripts / assets はスキル従属なので、各スキル配下へ (`.claude/skills/xxx-skill/` )

# 参考文献

[A complete guide to building skills for Claude](https://claude.com/blog/complete-guide-to-building-skills-for-claude) (skills の知見を深めたい場合は必読)
