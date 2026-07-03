---
id: "2026-07-03-google-colabでgo言語を学んでみる基本文法編-01"
title: "Google Colabで、Go言語を学んでみる──基本文法編"
url: "https://qiita.com/Inclusive_Solutions_LLC/items/d4413f9b12483af0ea26"
source: "qiita"
category: "ai-workflow"
tags: ["Python", "qiita"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

## はじめに

今回のテーマは、**Google Colabで、Go言語の初歩の初歩を学ぶ**です。

Go言語に限らず、プログラミング言語を新たに学ぶ際、大切なのは、


* 小さくつくて
* その場で試して
* 結果を見ながら、ルール・法則を学ぶ

ことだと思います。最小・高速でPDCAサイクルを回してこそ、効率的に知識が獲得できます。
この点、Google Colab(Jupyter Notebook)は、プログラムの実行環境を意識せずに、プログラムの書き方・実行結果に集中できるので、プログラミング学習には大変便利です。

そこで、本記事では、Google Colabで使用するサンプルコード集とあわせて、Goの基本文法を解説します。


* Goのプログラムはどこから始まるのか
* 変数はどう書くのか
* 関数はどう書くのか
* if文、for文はどう書くのか
* slice、map、structとは何か
* Goのエラー処理はどういう考え方なのか

Go言語の**初歩の初歩**にフォーカスするので、ぜひコードを一つずつ、自分で実行しながら、進めてみてください。



## 対象読者

この記事は、次のような人を対象にしています。

* Google Colabを使ったことがある人
* Pythonなど、何らかのプログラミング言語を少し触ったことがある人
* Go言語に興味がある人
* Goの文法を最初からざっくり眺めたい人
* 学んで終わりでなく、コードを「触りながら」「実行しながら」学びたい人

※本記事は、本格的なGo開発環境の構築ではなく、まずは文法中心に、Google Colab上でGoの雰囲気をつかむことを目的にしています。

なお、「**Google ColabでGoのプログラムを動かすなんてできるの？**」で引っかかってる読者は、まず下記記事で予習してください。

https://qiita.com/Inclusive_Solutions_LLC/items/1a4f40f172352a96e8cb

以後は、Goのコードを `main.go` というファイルに書き出し、それを実行する形で進めます。

# 学習の進め方
## ご自身で進める場合
マジックコマンド(`%%writefile`)で、main.goを作成して、使用してください。
```python
%%writefile main.go
```
作成したmain.goは、下記のコードで実行できます。
```python
!go run main.go
```

main.goの記述を変更しながら、結果を確認してください。

## Google Colab版
すぐに使えるチートシートはこちら。

https://colab.research.google.com/drive/1OGkopVHKr7Xy8TSA3zmZknFD7qywFtst#scrollTo=CfXOzkIM1E1i

※ソースコード・プログラムおよび解説文は、Claudeを用いて作成しています。

# 1. まずは基本形 Goのプログラムは main 関数から始まる

まずは、いちばん小さなGoプログラムです。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

実行すると、次のように表示されます。

```text
Hello, World!
```

それぞれの意味は、ざっくり次のとおりです。

* `package main`
  実行可能なプログラムであることを示します。

* `import "fmt"`
  文字を表示するための `fmt` パッケージを読み込みます。

* `func main()`
  プログラムの入口です。Goのプログラムは、基本的に `main` 関数から始まります。

* `fmt.Println()`
  文字や数値を画面に表示します。



# 2. 関数を作る

Goでは、関数を `func` で定義します。

```python
%%writefile main.go
package main

import "fmt"

func add(a int, b int) int {
    return a + b
}

func main() {
    result := add(2, 3)
    fmt.Println(result)
}
```

実行結果は次のとおりです。

```text
5
```

この部分が関数定義です。

```go
func add(a int, b int) int {
    return a + b
}
```

意味は、

* `add` という名前の関数
* `a int` は、int型の引数 `a`
* `b int` は、int型の引数 `b`
* 最後の `int` は、戻り値の型
* `return a + b` で、足し算の結果を返す

ということです。

Goでは、引数や戻り値の型を基本的に明示します。

同じ型の引数が続く場合は、次のように省略して書くこともできます。

```python
%%writefile main.go
package main

import "fmt"

func add(a, b int) int {
    return a + b
}

func main() {
    result := add(2, 4)
    fmt.Println(result)
}
```

```text
6
```

`a, b int` は、`a` も `b` も `int` という意味です。


# 3. 変数を使う

Goで変数を作るには、いくつかの書き方があります。

まずは、型を明示する書き方です。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    var x int = 10
    fmt.Println(x)
}
```


```text
10
```

`var x int = 10` は、

* `x` という変数を作る
* 型は `int`
* 値は `10`

という意味です。

Goでは、型推論を使って短く書くこともできます。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    y := 20
    fmt.Println(y)
}
```

```text
20
```

`:=` は、Goでよく使う短い変数宣言です。

```go
y := 20
```

これは、Goが `20` を見て、「これはint型だな」と自動で判定させる書き方です。

## 注意点

`:=` は、主に関数の中で使います。

```go
func main() {
    y := 20
}
```
まずはこの書き方に慣れるとよいと思います。

# 4. 再代入する

Goでは、一度作った変数に別の値を入れ直すこともできます。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    x := 10
    fmt.Println(x)

    x = 20
    fmt.Println(x)
}
```


```text
10
20
```

最初に `x := 10` で変数を作っています。

その後、`x = 20` で値を入れ直しています。

ここで注意したいのは、

* 新しく変数を作るときは `:=`
* 既存の変数に代入するときは `=`

という違いです。

```go
x := 10 // 新しく作る
x = 20  // 既存の変数に代入する
```

---

# 5. 定数を使う

値を変えたくない場合は、`const` を使います。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    const pi = 3.14
    fmt.Println(pi)
}
```

```python
!go run main.go
```

```text
3.14
```

`const` は定数です。

```go
const pi = 3.14
```

定数は、あとから値を変更できません。

```go
const pi = 3.14
pi = 3.14159 // これはエラー
```

プログラム中で変わらない値に使います。


# 6. 基本的な型

Goには、よく使う基本型があります。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    name := "Alice"
    age := 30
    height := 160.5
    active := true

    fmt.Println(name)
    fmt.Println(age)
    fmt.Println(height)
    fmt.Println(active)
}
```


代表的な型は次のとおりです。

* `string`
  文字列

* `int`
  整数

* `float64`
  小数

* `bool`
  真偽値。`true` または `false`

Goは型に厳しい言語です。

たとえば、int型の変数に文字列を入れることはできません。

```go
x := 10
x = "hello" // エラー
```

Pythonに慣れていると少し面倒に感じますが、Goではこの型の厳しさによって、実行前にミスを見つけやすくなります。

---

# 7. 複数の戻り値

Goの特徴のひとつに、関数が複数の値を返せることがあります。

```python
%%writefile main.go
package main

import "fmt"

func div(a, b int) (int, bool) {
    if b == 0 {
        return 0, false
    }

    return a / b, true
}

func main() {
    result, ok := div(10, 2)
    fmt.Println(result, ok)
}
```

```text
5 true
```

この関数は、2つの値を返しています。

```go
func div(a, b int) (int, bool)
```

戻り値は、

* 割り算の結果
* 割り算できたかどうか

です。

`b == 0` の場合、0で割ることはできないので、`false` を返しています。

Goでは、このように複数の戻り値を使って、処理結果と成功・失敗を一緒に返す書き方がよく出てきます。

---

# 8. if文を書く

条件分岐には `if` を使います。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    x := 3

    if x > 5 {
        fmt.Println("big")
    } else if x < 5 {
        fmt.Println("small")
    } else {
        fmt.Println("equal")
    }
}
```


```text
small
```

Goのif文には、いくつか特徴があります。

* 条件式に `()` は不要
* 処理のまとまりには `{}` が必要
* `else` は前の `}` と同じ行に書く
* Pythonのようなインデントだけのブロックではない

次のように書きます。

```go
if x > 5 {
    fmt.Println("big")
} else {
    fmt.Println("small")
}
```

Pythonのように、

```python
if x > 5:
    print("big")
```

とは書き方が違います。

Goでは `{}` が必須です。

---

# 9. for文を書く

Goでは、繰り返しには基本的に `for` を使います。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    for i := 0; i < 5; i++ {
        fmt.Println(i)
    }
}
```


```text
0
1
2
3
4
```

この部分がfor文です。

```go
for i := 0; i < 5; i++ {
    fmt.Println(i)
}
```

意味は、

* `i := 0`
  最初に `i` を0にする

* `i < 5`
  `i` が5未満の間だけ繰り返す

* `i++`
  1回ごとに `i` を1増やす

ということです。

Goには、`while` というキーワードはありません。

ただし、次のように書くと、while文のように使えます。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    x := 0

    for x < 3 {
        fmt.Println(x)
        x++
    }
}
```

```text
0
1
2
```

Goでは、これも `for` です。

---

# 10. sliceを使う

Goで複数の値を並べて扱うとき、よく使うのが `slice` です。

Pythonのリストに近いものだと考えると、最初は理解しやすいです。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    nums := []int{1, 2, 3}

    fmt.Println(nums)
}
```

```text
[1 2 3]
```

`[]int{1, 2, 3}` は、int型の値を並べたsliceです。

値を追加するには、`append` を使います。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    nums := []int{1, 2, 3}

    nums = append(nums, 4)

    fmt.Println(nums)
}
```

```text
[1 2 3 4]
```

Goの `append` は、戻り値を受け取る必要があります。

```go
nums = append(nums, 4)
```

Pythonのように、

```python
nums.append(4)
```

と書くのとは少し違います。

---

# 11. rangeでループする

sliceの中身を順番に取り出すには、`range` を使います。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    nums := []int{1, 2, 3}

    for i, v := range nums {
        fmt.Println(i, v)
    }
}
```

```python
!go run main.go
```

```text
0 1
1 2
2 3
```

`range` を使うと、2つの値が取れます。

```go
for i, v := range nums
```

* `i` はインデックス
* `v` は値

です。

値だけ使いたい場合は、インデックスを `_` で捨てます。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    nums := []int{1, 2, 3}

    for _, v := range nums {
        fmt.Println(v)
    }
}
```

```python
!go run main.go
```

```text
1
2
3
```

`_` は、「この値は使わない」という意味です。

Goでは、使っていない変数があるとエラーになるため、不要な値は `_` で受けます。

---

# 12. mapを使う

Goの `map` は、Pythonの辞書に近いものです。

キーと値のペアでデータを持ちます。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    prices := map[string]int{
        "apple":  100,
        "banana": 200,
    }

    fmt.Println(prices)
}
```


```text
map[apple:100 banana:200]
```

`map[string]int` は、

* キーが `string`
* 値が `int`

という意味です。

つまり、次のような対応関係を持っています。

```text
apple  -> 100
banana -> 200
```

値を取り出すには、次のように書きます。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    prices := map[string]int{
        "apple":  100,
        "banana": 200,
    }

    v := prices["apple"]
    fmt.Println(v)
}
```

```text
100
```

---

# 13. mapにキーが存在するか確認する

Goのmapでは、存在しないキーを指定しても、エラーにはなりません。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    prices := map[string]int{
        "apple":  100,
        "banana": 200,
    }

    v := prices["orange"]
    fmt.Println(v)
}
```


```text
0
```

存在しないキーの場合、値の型に応じたゼロ値が返ります。

intの場合は `0` です。

ただし、これだと、

* 本当に値が0なのか
* キーが存在しなかったのか

がわかりません。

そこで、Goでは次の書き方をよく使います。

```python
%%writefile main.go
package main

import "fmt"

func main() {
    prices := map[string]int{
        "apple":  100,
        "banana": 200,
    }

    v, ok := prices["apple"]
    fmt.Println(v, ok)

    v, ok = prices["orange"]
    fmt.Println(v, ok)
}
```

```python
!go run main.go
```

```text
100 true
0 false
```

`ok` が `true` ならキーが存在します。
`false` ならキーが存在しません。

この書き方は、Goで非常によく出てきます。

```go
v, ok := prices["apple"]
```

---

# 14. structを使う

Goには、PythonやJavaのようなclassはありません。

そのかわり、データの形を表すために `struct` を使います。

```python
%%writefile main.go
package main

import "fmt"

type User struct {
    Name   string
    Age    int
    Gender string
}

func main() {
    u := User{Name: "Alice", Age: 30, Gender: "F"}

    fmt.Println(u)
    fmt.Println(u.Name)
}
```

```python
!go run main.go
```

```text
{Alice 30 F}
Alice
```

この部分がstructの定義です。

```go
type User struct {
    Name   string
    Age    int
    Gender string
}
```

これは、`User` というデータ型を作っています。

`User` は、

* `Name` というstring型の項目
* `Age` というint型の項目
* `Gender` というstring型の項目

を持ちます。

値を作るときは、次のように書きます。

```go
u := User{Name: "Alice", Age: 30, Gender: "F"}
```

項目にアクセスするときは、`.` を使います。

```go
u.Name
```

---

# 15. メソッドを使う

Goにはclassはありませんが、structにメソッドを紐づけることができます。

```python
%%writefile main.go
package main

import "fmt"

type User struct {
    Name   string
    Age    int
    Gender string
}

func (u User) Greet() {
    fmt.Println("Hello,", u.Name)
}

func main() {
    user := User{Name: "Alice", Age: 30, Gender: "F"}

    user.Greet()
}
```

```text
Hello, Alice
```

この部分がメソッドです。

```go
func (u User) Greet() {
    fmt.Println("Hello,", u.Name)
}
```

`func` のあとに `(u User)` がついています。

これは、`User` 型に `Greet` というメソッドを持たせる、という意味です。

そのため、次のように呼び出せます。

```go
user.Greet()
```

Goはclassを持たない言語ですが、structとメソッドを使うことで、データと処理を結びつけることができます。

---

# 16. Goのエラー処理

Goには、Pythonの `try / except` のような例外処理は基本的にありません。

そのかわり、関数の戻り値として `error` を返し、それを呼び出し側で確認します。

```python
%%writefile main.go
package main

import (
    "fmt"
    "errors"
)

func div(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }

    return a / b, nil
}

func main() {
    result, err := div(10, 0)

    if err != nil {
        fmt.Println("error:", err)
        return
    }

    fmt.Println("result:", result)
}
```


```text
error: division by zero
```

この関数は、2つの値を返します。

```go
func div(a, b int) (int, error)
```

* 計算結果
* エラー

です。

エラーがない場合は、`nil` を返します。

```go
return a / b, nil
```

エラーがある場合は、`error` を返します。

```go
return 0, errors.New("division by zero")
```

呼び出し側では、次のように確認します。

```go
if err != nil {
    fmt.Println("error:", err)
    return
}
```

Goでは、`if err != nil` は非常によく出てくる定番の書き方です。

---

# 17. 文字列を数値に変換する

Goでは、標準ライブラリを使って文字列を数値に変換できます。

代表的なのが `strconv.Atoi` です。

```python
%%writefile main.go
package main

import (
    "fmt"
    "strconv"
)

func main() {
    n, err := strconv.Atoi("123")

    if err != nil {
        fmt.Println("error:", err)
        return
    }

    fmt.Println("number:", n)
}
```

```text
number: 123
```

`strconv.Atoi("123")` は、文字列 `"123"` を整数に変換します。

ただし、変換できない文字列を渡すとエラーになります。

```python
%%writefile main.go
package main

import (
    "fmt"
    "strconv"
)

func main() {
    n, err := strconv.Atoi("あああ")

    if err != nil {
        fmt.Println("error:", err)
        return
    }

    fmt.Println("number:", n)
}
```

実行すると、次のようなエラーが表示されます。

```text
error: strconv.Atoi: parsing "あああ": invalid syntax
```

Goでは、このように「失敗するかもしれない処理」は、戻り値の `error` を確認しながら進めます。

---

# 18. ループとエラー処理を組み合わせる

複数の文字列を数値に変換してみます。

```python
%%writefile main.go
package main

import (
    "fmt"
    "strconv"
)

func main() {
    nums := []string{"10", "20", "a", "30"}

    for _, s := range nums {
        n, err := strconv.Atoi(s)

        if err != nil {
            fmt.Println("skip:", s)
            continue
        }

        fmt.Println("number:", n)
    }
}
```

```python
!go run main.go
```

```text
number: 10
number: 20
skip: a
number: 30
```

このコードでは、`"a"` は数値に変換できません。

そのため、エラーになった場合は、

```go
continue
```

でその回の処理をスキップしています。

Goでは、こういう形で、

* 1件ずつ処理する
* エラーがあればその場で確認する
* スキップするか、終了するかを決める

という書き方がよく出てきます。

---

# 19. エラーを上の層に返す

エラーが起きたとき、その場で処理するのではなく、呼び出し元に返すこともあります。

```python
%%writefile main.go
package main

import (
    "fmt"
    "strconv"
)

func parseInt(s string) (int, error) {
    n, err := strconv.Atoi(s)

    if err != nil {
        return 0, err
    }

    return n, nil
}

func main() {
    n, err := parseInt("123あ")

    if err != nil {
        fmt.Println("error:", err)
        return
    }

    fmt.Println(n)
}
```

```text
error: strconv.Atoi: parsing "123あ": invalid syntax
```

`parseInt` 関数では、エラーが起きたらそのまま返しています。

```go
if err != nil {
    return 0, err
}
```

そして、`main` 関数側でエラーを表示しています。

このように、

* 下の関数ではエラーを返す
* 上の関数でどう対応するか決める

という分け方ができます。

---

# 20. 1件でも失敗したら終了する

先ほどは、エラーが出たデータだけスキップしました。

今度は、1件でもエラーが出たら処理全体を終了します。

```python
%%writefile main.go
package main

import (
    "fmt"
    "strconv"
)

func run() error {
    nums := []string{"10", "20", "a", "30"}

    for _, s := range nums {
        n, err := strconv.Atoi(s)

        if err != nil {
            return err
        }

        fmt.Println("number:", n)
    }

    return nil
}

func main() {
    if err := run(); err != nil {
        fmt.Println("error:", err)
        return
    }
}
```

```text
number: 10
number: 20
error: strconv.Atoi: parsing "a": invalid syntax
```

`"a"` のところでエラーになり、そこで処理が終了します。

このように、Goではエラーが起きたときに、

* スキップして続ける
* 即終了する
* 上の関数に返す

といった方針を、自分で明示的に書きます。

---

# 21. ファイルを開く

Goでは、ファイル操作も標準ライブラリで行えます。

```python
%%writefile main.go
package main

import (
    "fmt"
    "os"
)

func main() {
    f, err := os.Open("sample.txt")

    if err != nil {
        fmt.Println("error:", err)
        return
    }

    defer f.Close()

    fmt.Println("file opened")
}
```


もし `sample.txt` が存在しなければ、次のようなエラーになります。

```text
error: open sample.txt: no such file or directory
```

`os.Open` も、結果とエラーを返します。

```go
f, err := os.Open("sample.txt")
```

ファイルを開けた場合は、最後に閉じる必要があります。

```go
defer f.Close()
```

`defer` は、その関数が終了するときに実行される処理を予約するものです。

ファイルを開いたあとに閉じ忘れないようにするため、Goではよく使われます。

---

# 22. GoからPythonを呼び出す

少し応用ですが、GoからPythonを呼び出すこともできます。

まず、Pythonファイルを作ります。

```python
%%writefile script.py
print("hello python from go")
```

次に、GoからこのPythonスクリプトを実行します。

```python
%%writefile main.go
package main

import (
    "fmt"
    "os/exec"
)

func main() {
    cmd := exec.Command("python3", "script.py")

    out, err := cmd.CombinedOutput()

    if err != nil {
        fmt.Println("error:", err)
        fmt.Println(string(out))
        return
    }

    fmt.Println("output:", string(out))
}
```


```text
output: hello python from go
```

これは、Goのプログラムから外部コマンドとしてPythonを実行している例です。

```go
cmd := exec.Command("python3", "script.py")
```

実行結果は、`CombinedOutput()` で受け取っています。

```go
out, err := cmd.CombinedOutput()
```

このように、GoからPythonを呼び出すこともできます。

実務では、Goで前処理や制御を行い、Pythonで分析処理を行う、といった組み合わせも考えられます。


## AIと一緒に学ぶときの聞き方

Goを学ぶときは、AIに次のように聞くと理解しやすくなります。

```text
このGoコードを1行ずつ説明してください。
Python経験者にもわかるように説明してください。
```

```text
このGoコードで使われている型をすべて説明してください。
```

```text
このGoコードをPythonで書くとどうなりますか。
Go版とPython版の違いも説明してください。
```

```text
このGoコードに初心者向けの練習問題を3つ追加してください。
```

```text
このエラーメッセージの意味を説明し、修正方法を教えてください。
```

AIに丸投げするのではなく、コードを動かして、少し変えて、エラーを出して、その意味をAIに聞くのが、プログラミング学習ではかなり効果的だと思います。

## さいごに

Google Colabは、Pythonや機械学習だけの環境ではありません。

Linuxコマンドを実行できるため、Goの学習環境としても使えます。

本格的な開発環境を作る前に、

* まずGoの文法を触る
* 小さなコードを動かす
* Pythonとの違いを見る
* AIに説明させる
* エラーを読んで修正する

という学習には、Google Colabはかなり便利です。

PythonだけでなくGoも少し触ってみることで、プログラミング言語を見る視野が広がると思います。

## 弊社について

本記事を書いている 合同会社インクルーシブソリューションズ は、データ基盤構築・分析基盤設計・システム改善支援を中心に活動している小規模IT法人です。

主な領域は、

* データマート設計・データパイプライン構築
* SQL / Python を用いたデータ処理設計
* BI導入支援・分析基盤の整備
* 既存システムの運用改善・可視化支援

といった、「データを使える状態にする」ための活動です。

弊社の企業活動に興味がある方は、ぜひ公式サイトも覗いてみてください。

https://inclu-sol.versus.jp/wordpress/
