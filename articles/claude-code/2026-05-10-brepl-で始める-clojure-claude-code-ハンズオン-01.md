---
id: "2026-05-10-brepl-で始める-clojure-claude-code-ハンズオン-01"
title: "brepl で始める Clojure × Claude Code ハンズオン"
url: "https://zenn.dev/shinseitaro/articles/brepl-clojure-claude-handson"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "zenn"]
date_published: "2026-05-10"
date_collected: "2026-05-11"
summary_by: "auto-rss"
query: ""
---

Clojure 開発の土台は REPL 駆動です。LLM を使う使わないに関係なく、これが Clojure の楽しさそのもの。

Claude Code のような LLM コーディングアシスタントが加わっても、この土台は変わりません。LLM の提案を即評価して挙動を確かめるために、LLM 側からも REPL に式を投げられる仕組みが必要になります。

ただ、現状 LLM から REPL を使うアプローチには摩擦があります。

* **clojure-mcp** のような MCP サーバー経由は機能豊富だが、出力の改行が `\n` のまま表示されて読みづらいことがある (Clojurians Slack でも繰り返し挙がっている話題)
* 毎回 `clj -X:test` のように JVM を起動するとセットアップは不要だが、プロジェクトの規模によって数秒〜数十秒のもたつきが毎回かかり、累積していく

[brepl](https://github.com/licht1stein/brepl) は「**bash ツールとして使える nREPL クライアント**」というシンプルな割り切りで、この摩擦をかなり減らしてくれます。本記事では、brepl をインストールして Claude Code と一緒に Clojure 開発する基本的なサイクルを、実際に手を動かして体験できるようにまとめます。

最終的には次のループが、編集後のフィードバック (reload + 評価) が **数百ms オーダー** でもらえるようになります。

```
コード編集 → reload → brepl で評価 → 結果を見て次の判断
```

(後半の「速度比較」セクションで実測値を載せます)

## 1. brepl とは何か

brepl は licht1stein 氏が作っている、AI支援 Clojure 開発のためのツールです。

<https://github.com/licht1stein/brepl>

名前は **B**racket-fixing **REPL** の略で、公式 README によれば 3 つのコア機能を備えています。

1. **🔧 括弧の自動修復** — [parmezan](https://github.com/borkdude/parmezan) を使って括弧の不一致や閉じ忘れを自動補正
2. **⚡ シンプルな REPL 評価** — 既存の nREPL に対して式を投げて結果を受け取る
3. **🔄 ファイル編集の自動評価** — 編集された Clojure ファイルを REPL でロードしてエラーを早期検知

このうち 1 と 3 は Claude Code や [ECA](https://eca.dev) のフック機構と統合する形で提供されており、後述するように `brepl hooks install` というワンコマンドでまとめてプロジェクトに導入できます。

加えて、上記とは独立に **薄い CLI nREPL クライアント** としても使えます。既に動いている nREPL に対して、コマンドライン引数や heredoc で Clojure 式を渡すと、評価結果が標準出力で返ってくる、という単純なインターフェースです。本記事のハンズオンでは Claude Code 統合 (Skill + Hook) を入れた上で、この CLI モードを軸にコードを動かしていきます。

CLI モードの実用上のキモは、**Claude Code が bash ツールの出力を加工せずそのまま表示する**点です。改行や日本語、構造化された値が読みやすく出る — これが MCP 経由との一番大きな差になります。

ありがちな誤解を先に潰しておきます。

* ❌ 「brepl は REPL を起動してくれる」 → 違います。**nREPL は別途起動が必要** です
* ❌ 「brepl は LLM 専用ツール」 → 違います。普通の REPL クライアントとしても便利に使えます
* ✅ 「brepl は AI支援 Clojure 開発のためのツール群で、CLI モードと Claude Code/ECA フック統合モードがある」

## 2. セットアップ

### 2.1. brepl 本体

brepl のインストール手順は[公式 README](https://github.com/licht1stein/brepl) を参照してください。インストールできていれば次のように出ます。

```
$ brepl --version
brepl 2.7.1
```

### 2.2. 動作確認用の最小プロジェクト

以下は本記事のハンズオンで使う `deps.edn` です。`:dev` alias で nREPL を起動できるようにしてあります。

deps.edn

```
{:paths ["src" "resources"]
 :deps {org.clojure/clojure {:mvn/version "1.11.4"}}

 :aliases
 {:dev
  {:extra-paths ["dev" "test"]
   :extra-deps {nrepl/nrepl {:mvn/version "1.3.0"}
                cider/cider-nrepl {:mvn/version "0.50.2"}}
   :main-opts ["-m" "nrepl.cmdline"
               "--middleware" "[cider.nrepl/cider-middleware]"
               "--port" "7890"]}

  :test
  {:extra-paths ["test"]
   :extra-deps {io.github.cognitect-labs/test-runner
                {:git/tag "v0.5.1" :git/sha "dfb30dd"}}
   :main-opts ["-m" "cognitect.test-runner"]
   :exec-fn cognitect.test-runner.api/test}}}
```

ポートを `7890` にしているのは、後述する「複数プロジェクトでポートが衝突する」問題を避けるためです。プロジェクトごとに違うポートにしておくと事故が減ります。

### 2.3. ソースファイルとテストを作る

ハンズオンで触る関数とテストを置きます。

src/myapp/core.clj

```
(ns myapp.core
  (:require [clojure.string :as str]))

(defn greet
  "名前を受け取り挨拶文を返す純粋関数。"
  [name]
  (str "Hello, " name "!"))
```

test/myapp/core\_test.clj

```
(ns myapp.core-test
  (:require [clojure.test :refer [deftest is testing]]
            [myapp.core :as core]))

(deftest greet-test
  (testing "正常系"
    (is (= "Hello, Alice!" (core/greet "Alice")))))
```

最終的なディレクトリ構造はこうなります。

```
.
├── deps.edn
├── src
│   └── myapp
│       └── core.clj
└── test
    └── myapp
        └── core_test.clj
```

### 2.4. Claude Code 統合をワンコマンドで入れる

Claude Code と brepl をペアで使う場合、以下のコマンドで **Hook と Skill を一括で導入** できます (公式 README の Quick Start もこの順序)。

実行すると次の 3 つが自動で配置されます。

| 配置されるもの | 役割 |
| --- | --- |
| `.claude/settings.local.json` | Claude Code の Hook 群を登録 (詳細は下) |
| `.claude/skills/brepl/SKILL.md` | brepl の使い方 (heredoc 必須、エラー復旧の作法など) を Claude に教える Skill |
| `.brepl/hooks.edn` | **ユーザーが編集する Stop Hook 設定ファイル** (Claude が停止したときに走らせたいテスト/lint 等を書く場所) |

`.claude/settings.local.json` に登録される Hook は 4 種類で、それぞれ `brepl hook ...` というサブコマンドを呼びます。

| Hook イベント | 走る処理 | 役割 |
| --- | --- | --- |
| `PreToolUse` (Edit/Write/Bash) | `brepl hook validate` | 編集**前**に Clojure 構文を検証 (ブラケット崩れを早期検知) |
| `PostToolUse` | `brepl hook eval` | 編集**後**に変更ファイルを REPL で評価し、ロード時エラーを早期検知 |
| `Stop` | `brepl hook stop` | Claude の応答終了時、`.brepl/hooks.edn` に書かれたチェック (テスト等) を走らせる |
| `SessionEnd` | `brepl hook session-end` | セッション終了時にバックアップファイルを掃除 |

PostToolUse の `brepl hook eval` がいわゆる「Live file synchronization」の正体です。Claude がコードを書き換えた直後に裏で勝手に REPL ロードが走り、構文エラー / 未解決シンボルなどを Claude にフィードバックします。

`.brepl/hooks.edn` の初期値はコメント例だけが入ったテンプレートで、好きなチェックを書き足せます。

.brepl/hooks.edn (抜粋)

```
;; brepl stop hooks configuration

{:stop
 [;; 例: Claude が止まったら nREPL でテストを走らせる
  ;; {:type :repl
  ;;  :code (clojure.test/run-tests)
  ;;  :required? true    ; 失敗したら Claude にリトライさせる
  ;;  :max-retries 10
  ;;  :timeout 120}

  ;; 例: bash で linter を走らせる
  ;; {:type :bash
  ;;  :command "clj-kondo --lint src"
  ;;  :required? false   ; 失敗を伝えるだけでリトライはさせない
  ;;  :timeout 30}
  ]}
```

`:required? true` のフックが落ちると Claude はリトライまでさせられるので、「テスト緑じゃないと止まらない」運用が手軽に組めます。

中身を覗くと SKILL.md の 要点は **「先に SKILL.md を読み込ませる」「heredoc を使う」** という強制ルールを LLM に刷り込むこと。これだけで Claude が brepl の使い方をミスる確率が下がります。

<https://github.com/licht1stein/brepl/blob/master/.claude/skills/brepl/SKILL.md>

このSKILL.mdの更新方法は第８章で説明します。

### 2.5. nREPL を起動

プロジェクトディレクトリでターミナルを開いて

```
$ clj -M:dev
nREPL server started on port 7890 on host localhost - nrepl://localhost:7890
```

このときカレントディレクトリに `.nrepl-port` というファイルが自動的に作られ、中身は `7890` になっています。brepl はこのファイルを見つけて自動的に接続先を決めます。

!

**ポート衝突 (BindException) が出たら**

起動時に `BindException: アドレスは既に使用中です` のようなエラーが出る場合、別のプロセスが既に同じポートを使っています。

```
$ ss -ltn | grep 7890     # 7890 を使っているプロセスを確認
```

不要なプロセスを終了するか、`deps.edn` の `:dev` alias の `--port` を別の番号 (例: `7891`) に変えてください。

!

**nREPL を起動した後にソースファイルを作ると require が通らないことがある**

nREPL を起動した後で `src/` 配下にファイルを追加した場合、`(require '[myapp.core])` が次のような `FileNotFoundException` を返すことがあります。

```
Could not locate myapp/core__init.class, myapp/core.clj or myapp/core.cljc on classpath.
```

これは JVM のクラスローダが起動時の classpath ディレクトリの状態を保持しており、起動後に追加されたファイルを再スキャンしないために起きます。

回避策はシンプルで、**nREPL を一度終了して起動し直す**こと。本記事の手順では `deps.edn` とソースファイルを作ってから nREPL を起動するので通常は遭遇しませんが、後からファイルや名前空間を追加するときには再起動を意識してください。

応急処置として `(load-file "src/myapp/core.clj")` で直接ロードする方法もありますが、`require` 自体を通したいなら再起動が確実です。

### 2.6. 接続テスト

nREPL を起動したターミナルとは別のターミナルを開いて、**プロジェクトのディレクトリ (= `.nrepl-port` ファイルがあるディレクトリ) に `cd` してから** brepl を呼びます。

```
$ cd /path/to/myapp
$ brepl '(+ 1 2 3)'
6
```

`6` が返れば接続成功です。

本記事のような `-e` 引数 / heredoc 経由の評価では、brepl はまず **CWD の `.nrepl-port` を見て接続先を決めます**。`cd` 先がずれると `.nrepl-port` が見つからず「No nREPL port found」エラーになります (実例は次の節で扱います)。

接続先解決の厳密な優先順位 (`-p` 引数 / `BREPL_PORT` 環境変数 / プロセススキャンを含む完全なルール) は後ほど「接続先はどう決まるか」で整理します。

## 3. heredoc パターン: Claude が使うコアテクニック

セットアップで `brepl hooks install` を済ませた時点で、Skill (SKILL.md) を通じて Claude には **「brepl に式を渡すときは必ず heredoc を使う」** というルールが刷り込まれています。

```
brepl <<'EOF'
(require '[clojure.string :as str])
(str/join ", " ["a" "b" "c"])
EOF
```

このパターンの読み書きは人間側もできた方がいいので、簡単に解説します。

[heredoc (ヒアドキュメント)](https://ja.wikipedia.org/wiki/%E3%83%92%E3%82%A2%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88) はシェルで複数行の文字列リテラルを書く仕組みで、`<<'EOF'` から `EOF` までの間がひとかたまりの文字列として扱われます。これを使うと、囲まれた中身は **シェルから一切解釈されず** にそのまま brepl に渡ります。

なぜそれが効くのか。Clojure はシングルクォート `'` (引用) もダブルクォート `"` (文字列) も多用します。シェルで素朴に書こうとすると引用とエスケープが絡み合って混乱しがちですが、heredoc ならその心配がありません。ポイントは `<<'EOF'` の **シングルクォート**。これがあると `$` などのシェル変数展開も無効化されて、Clojure コードを完全にリテラルとして渡せます。

複数式・引用符・日本語が混ざっても素直に書けます。

```
brepl <<'EOF'
(println "String with 'single' and \"double\" quotes")
(str "敬称は " "Mr." " と " "san" " で扱いが違う")
EOF
```

```
String with 'single' and "double" quotes
nil
"敬称は Mr. と san で扱いが違う"
```

このパターンが Skill 経由で Claude に強制されているおかげで、**「クォート地獄でリトライする回数」が劇的に減ります**。Claude が出すシェルコマンドを読むとき、あるいは自分で brepl を直接叩くときに、同じ形でブレなく書けるのが効いてきます。

## 4. ハンズオン: Claude Code と brepl で REPL 駆動サイクルを回す

ここからが記事の中核です。実際のサイクルを順を追って見ていきます。題材はセットアップで作った `greet` 関数 です。

### 4.1. Step 1. 既存挙動を確認

```
brepl <<'EOF'
(require '[myapp.core :as core])
(core/greet "world")
EOF
```

最初の `nil` は `require` の戻り値、2 行目が `greet` の結果です。

### 4.2. Step 2. 要件追加 (敬称オプション)

「名前と敬称を両方受けられるようにしたい」という要件で、Claude にこの関数を書き換えてもらいます。最初の素朴な実装はこんな感じになりがち。

src/myapp/core.clj

```
(defn greet
  "名前と任意の敬称を受け取り挨拶文を返す純粋関数。"
  ([name] (greet name nil))
  ([name title]
   (str "Hello, " (when title (str title " ")) name "!")))
```

### 4.3. Step 3. reload して即動作確認

ファイルを編集したら、REPL を再起動するのではなく `:reload` で名前空間を再読み込みします。

```
brepl <<'EOF'
(require '[myapp.core :as core] :reload)

(core/greet "world")
(core/greet "Yamada" "Mr.")
(core/greet "山田" "さん")
EOF
```

```
nil
"Hello, world!"
"Hello, Mr. Yamada!"
"Hello, さん 山田!"
```

3 番目の出力 `"Hello, さん 山田!"` で違和感に気付きます。**日本語の敬称は名前の後ろ** に付くものです。「さん 山田」では意味が成り立たない。このようなバグを見つけるのに、REPLは非常に有効です。

### 4.4. Step 4. 修正してまた即確認

敬称が末尾にピリオドを持つ前置詞型 (`Mr.`, `Dr.` など) なら名前の前、それ以外 (`さん`, `san`) は名前の後ろに付ける、というルールに直します。

src/myapp/core.clj

```
(defn greet
  "名前と任意の敬称を受け取り挨拶文を返す純粋関数。
   敬称が前置詞型 (Mr. 等の末尾ピリオド) なら名前の前、そうでなければ後ろに付ける。"
  ([name] (greet name nil))
  ([name title]
   (cond
     (nil? title)               (str "Hello, " name "!")
     (str/ends-with? title ".") (str "Hello, " title " " name "!")
     :else                      (str "Hello, " name " " title "!"))))
```

そしてもう一度 brepl で叩く。

```
brepl <<'EOF'
(require '[myapp.core :as core] :reload)

(core/greet "world")
(core/greet "Sawada" "Mr.")
(core/greet "山田" "さん")
(core/greet "Tanaka" "san")
(core/greet "Smith" "Dr.")
EOF
```

```
nil
"Hello, world!"
"Hello, Mr. Sawada!"
"Hello, 山田 さん!"
"Hello, Tanaka san!"
"Hello, Dr. Smith!"
```

意図通り。**編集 → reload → 評価のサイクルを 1 つの brepl 呼び出しで完結** できているのが分かります。

LLM とこのループを回すと、Claude が提案 → brepl で確認 → ダメなら指摘 → 修正、というやり取りが秒単位で回ります。

## 5. 速度比較: なぜ brepl は速いのか

実測してみます。同じテストスイートを 2 つの方法で実行します。

```
time brepl <<'EOF'
(require '[clojure.test :refer [run-tests]])
(require '[myapp.core-test] :reload)
(run-tests 'myapp.core-test)
EOF

real    0m0.137s
user    0m0.087s
sys     0m0.041s
```

```
time clj -X:test
...
Ran 3 tests containing 4 assertions.
0 failures, 0 errors.

real    0m1.723s
user    0m3.286s
sys     0m0.454s
```

| 方式 | 時間 | 内訳 |
| --- | --- | --- |
| **brepl** 経由 | **0.137s** | 既存 JVM に式を投げるだけ |
| `clj -X:test` | 1.723s | JVM 起動 + クラスパス解決 + コンパイル |

**約 12 倍の差**です。1 回 1 秒台のもたつきは「気にならない」と思いがちですが、LLM と一緒に作業するときは数十回〜数百回の評価が積み重なるので、累積でかなり違います。「思いついた瞬間に確認できる」体験が、Clojure 開発の生産性を大きく左右します。

なお、brepl 自体が軽快に動く理由は [README](https://github.com/licht1stein/brepl) に書かれている通りで、

* **Babashka ランタイム** で動いているのでクライアント側の起動コストが小さい
* localhost の nREPL サーバーへの応答は **5ms 未満**
* `.nrepl-port` 等が無い場合のポート自動探索でも 100〜200ms

という設計です。私たちの実測 137ms はこれと整合します。

注意として、初回ロードや依存関係の追加が走るときは普通に時間がかかります。brepl は **既に立ち上がっているプロセスに式を流し込むコストの低さ** を利用しているだけで、JVM 起動時間そのものを消しているわけではありません。

## 6. 接続先はどう決まるか

brepl はどの nREPL に接続するかを次の優先順位で解決します ([README](https://github.com/licht1stein/brepl) 記載)。

1. `-p <port>` コマンドライン引数
2. `.nrepl-port` ファイル
   * `-e` / `-m` / heredoc (本記事の使い方) → **CWD の `.nrepl-port`**
   * `-f` でファイルロード時 → そのファイルのディレクトリから上に向かって探索
3. `BREPL_PORT` 環境変数
4. プロセススキャン: 動いている Java/Clojure/Babashka nREPL の中から CWD と一致するものを探す
5. どれでも見つからなければエラー (`No nREPL port found`)

### 6.1. 接続先を確認する習慣

評価セッションを始める前に、自分が今どこに繋がっているか確認する一行を投げる習慣をつけると事故が減ります。

```
brepl <<'EOF'
{:cwd (System/getProperty "user.dir")
 :ns *ns*
 :clj-version (clojure-version)}
EOF
```

```
{:cwd "/tmp/myapp", :ns #namespace[user], :clj-version "1.11.4"}
```

`:cwd` を見れば「今ロードしているコードはどのディレクトリの REPL のものか」が一目で分かります。LLM とペア作業するときは、各セッションの最初にこれを実行するルールを SKILL.md に書いておくのも有効です。

### 6.2. 起こりやすい事故: stale な `.nrepl-port`

接続先解決のルールは単純な分、次のような事故が起きえます。

* プロジェクト A で nREPL を一度起動 → 終了 (このとき `.nrepl-port` ファイルは自動削除されず残る)
* 別ターミナルでプロジェクト B が **同じポート** で nREPL を起動
* A のディレクトリで brepl を実行 → A の (古い) `.nrepl-port` を読んで **B の REPL に接続**
* たまたま B にも同名の namespace があると、**評価は成功してしまう**

「あれ、なんで自分のコードがこう動くんだ？」と気付くまで時間を食うタイプの事故です。実際この記事を書いている過程でも一度遭遇しました。`(System/getProperty "user.dir")` の出力が自分のいるディレクトリと違って初めて気付いた、という典型例です。

防衛策はシンプルです。

* **プロジェクトごとに固定ポートを変える**: `deps.edn` の `:dev` alias の `--port` を A=7890, B=7891 のように分ける (これが一番効く)
* **セッション開始時に上記の自己診断スニペットを必ず流す**: 接続先がズレていたらこれで気付ける
* 不安なら stale な `.nrepl-port` を手動削除 (`rm .nrepl-port`) してから brepl を呼ぶ

## 7. brepl balance — 構文修復はあくまで「応急処置」

brepl には `balance` というサブコマンドがあって、括弧バランスが崩れた Clojure ファイルを自動修復してくれます。

```
brepl balance src/myapp/core.clj          # in-place 修正
brepl balance src/myapp/core.clj --dry-run # 修正案だけ stdout に
```

便利そうですが、**構文を整えるだけで意味は保証しません**。ここを誤解すると痛い目を見ます。

具体例。次の壊れたファイルがあるとします。

/tmp/broken.clj (修復前)

```
(defn add [a b]
  (+ a b)        ; ← add の閉じ ) が抜けている

(defn mul [a b]
  (* a b))
```

`brepl balance` を実行すると、結果はこうなります。

/tmp/broken.clj (修復後)

```
(defn add [a b]
  (+ a b)

(defn mul [a b]
  (* a b))
)                ; ← 末尾に ) を追加して数だけ合わせた
```

数字上は釣り合っていますが、これを評価すると **`add` の本体に `(defn mul ...)` が取り込まれてしまう** という致命的な意味のズレが残ります。

```
brepl <<'EOF'
(load-file "/tmp/broken.clj")
(add 2 3)
EOF
```

`(add 2 3)` の戻り値は `5` を期待していたはずなのに、`#'user/mul` という Var が返ってきています。`add` を呼ぶたびに `mul` が再定義される、意味不明な関数になっているからです。

`brepl balance` の正しい使いどころは、

* **緊急避難**: REPL がそもそも起動できないほど壊れたファイルを、一旦パースだけ通す応急処置
* **`--dry-run` で機械の修復案を見て、人間/LLM が「意味的に正しいか」判断する材料**

どちらにしても、最終判断は人間 (または LLM の意味理解) 側に残しておくべきです。

## 8. brepl は Skill 層、cljfmt 等は Hook 層 — 役割の分担

Claude Code には大きく 2 つの自動化レイヤーがあります。両者は独立で、呼び出し関係はありません。

![](https://static.zenn.studio/user-upload/deployed-images/8bc45f54a4701c08720fd5ca.png?sha=b3a13db659431edd6d3d16d485a0684759b8d62c)

判断軸はシンプルです。

| 種類 | LLM の判断が必要か | 適した層 |
| --- | --- | --- |
| 評価・テスト・デバッグ | 必要 (どこで何を確認するか文脈依存) | **Skill** (brepl) |
| フォーマット整形 | 不要 (決定論的) | **Hook** (cljfmt 等) |
| 括弧バランス検査 | 不要 (検出だけなら) | **Hook** (警告のみ) |
| 括弧の意味的修正 | **必要** (意味を壊さないため) | **Skill** または人間 |

brepl は Skill 層のツールです — LLM が「ここで評価したい / テストしたい」と判断したときに呼ばれます。一方でフォーマットや単純な検出のような決定論的な処理は Hook 層に任せて、ハーネスが裏で勝手に走らせる。この役割分担ができていると、LLM の判断はビジネスロジックに集中でき、定型処理は気にしなくてよくなります。

セットアップで `brepl hooks install` を実行した時点で、両方の層が一気に整います。

* **Skill 層**: `.claude/skills/brepl/SKILL.md` が配置される — Claude にとっての「brepl の取扱説明書」
* **Hook 層**: `.claude/settings.local.json` に PostToolUse Hook が追加される — ファイル編集後に自動で括弧検証 + REPL 評価が走る

つまり読者は **役割分担を意識しなくても両方の恩恵を受けられる**。これがブレント氏の `brepl hooks install` ワンコマンドに込められた設計上の親切さです。

### 8.1. プロジェクト独自のルールを足したいとき

「セッション開始時に必ず接続先を確認する」「特定の fixture をロードしてからテストする」のようなプロジェクト固有のルールは、brepl の Skill とは別に自分で書いた Skill ファイルを追加することで併用できます。

.claude/skills/myapp-eval/SKILL.md

```
---
name: myapp-eval
description: myapp プロジェクトでの REPL 評価ルール
---

# myapp の評価ルール

## セッション最初に必ず接続先確認

```bash
brepl <<'EOF'
{:cwd (System/getProperty "user.dir")
 :ns *ns*}
EOF
```

`:cwd` が `/path/to/myapp` でなければ作業を中断してユーザーに報告する。

## テスト実行時のお作法

`(require '[myapp.fixtures] :reload)` を必ず先に実行してから個別テストを呼ぶ。
```

このように **brepl の Skill が汎用のベース、プロジェクト固有の作法は別 Skill** という構成にすると、汎用ルールとローカルルールが分離できて保守しやすくなります。

役割分担についてのより詳しい議論は Clojurians Slack `#ai-assist-coding` のスレッドが参考になります。

## 9. まとめ: brepl を使うべきとき・使わないとき

**使うべきとき**

* LLM と一緒に Clojure を書いていて、評価・テスト・リロードを頻繁に繰り返す
* 出力をきれいに見たい (改行・日本語・構造化値)
* セットアップを軽く保ちたい (MCP サーバー管理を増やしたくない)

**他を選んだほうがよいとき**

* チームが既に clojure-mcp で統一されていて運用に乗っている
* nREPL を使わない一発もの (Babashka スクリプト等は普通に `bb` でよい)

brepl は薄くて単純なツールです。**「これだけで何でも解決する銀の弾丸」ではありません**。Hook 層 (フォーマッタ等)、LLM 自身の意味理解、人間のレビュー — それらと組み合わせて初めて、Clojure × LLM の生産性が引き出されます。

逆にいえば、**「LLM のためだけに重厚な仕掛けを足す」必要はない** ということでもあります。bash で評価するだけ、という割り切りで実用上は十分。シンプルなツールが好きな Clojurian の感性ともよく合うと思います。

## 10. 参考リンク
