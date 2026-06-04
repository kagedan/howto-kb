---
id: "2026-06-03-rustのasyncawaitを完全に理解する7つの落とし穴と解決パターン-01"
title: "Rustの`async`/`await`を完全に理解する：7つの落とし穴と解決パターン"
url: "https://qiita.com/locallab/items/70a84285920c68f232b0"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- Rust の async は「ゼロコスト抽象化」だが、**使い方を誤ると意図しないブロッキングが発生する**
- `Future` はポーリングモデルであり、`await` しない限り実行されない
- `Send` 境界・`MutexGuard` のスコープ・タスク分割の 3 点が頻出の躓きポイント
- 本記事では 7 つのよくあるミスと、tokio ベースの解決コードを示す

---

## 背景

Rust の非同期プログラミングは「速くて安全」と謳われますが、初見では挙動が掴みにくい落とし穴が多数あります。

2024〜2026 年にかけて `tokio` は 1.x 系が安定運用フェーズに入り、`async-std` との棲み分けも整理されてきました。今こそ「なぜそう動くのか」を一度体系的に整理するタイミングです。

---

## 前提知識

- Rust 2021 Edition 以降
- `tokio = { version = "1", features = ["full"] }` 使用
- `cargo` ビルドが通る環境

---

## ① `await` を付け忘れる（Future が実行されない）

最も初歩的、かつ最も気づきにくい罠です。

```rust
// ❌ NG: Future を生成しているだけで実行されていない
async fn fetch_data() -> String {
    reqwest::get("https://example.com/api")  // ← await がない
        .unwrap()
        .text()
        .await
        .unwrap()
}
```

Rust は `Future` を**遅延評価**します。`.await` を呼ばなければ一切実行されません。コンパイラは警告を出してくれますが、**チェーンの途中で `await` を忘れると警告が出ないケース**があります。

```rust
// ✅ OK
async fn fetch_data() -> String {
    reqwest::get("https://example.com/api")
        .await           // ← ここ
        .unwrap()
        .text()
        .await
        .unwrap()
}
```

**教訓**: `async fn` を呼んだ直後は必ず `.await` があるか目視確認する。

---

## ② 同期的な重い処理を async ランタイムで直接実行する

`tokio` のデフォルトランタイムはスレッドプールを持ちますが、**1 タスクが CPU をブロックするとスレッドプール全体が詰まります**。

```rust
// ❌ NG: 重い同期処理を async タスク内で直接呼ぶ
#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let result = heavy_cpu_work(); // ← 数秒かかる同期処理
        println!("{}", result);
    });
}

fn heavy_cpu_work() -> u64 {
    // 素数列挙など重い処理
    (2u64..10_000_000).filter(|&n| is_prime(n)).count() as u64
}
```

```rust
// ✅ OK: spawn_blocking でスレッドプールを分離する
#[tokio::main]
async fn main() {
    let result = tokio::task::spawn_blocking(|| {
        heavy_cpu_work()
    })
    .await
    .unwrap();

    println!("{}", result);
}
```

`spawn_blocking` は専用のブロッキングスレッドプールで実行されるため、async ランタイムを詰まらせません。

---

## ③ `std::sync::Mutex` の Guard を `await` をまたいで保持する

これはコンパイルエラーになる場合と、**黙って動くが実はデッドロックを誘発する**場合の両方があります。

```rust
use std::sync::Mutex;

// ❌ NG: MutexGuard が await をまたぐ
async fn update(data: Arc<Mutex<Vec<u32>>>) {
    let mut guard = data.lock().unwrap();
    some_async_fn().await; // ← ここで Guard を持ったまま待機
    guard.push(42);
}
```

`std::sync::MutexGuard` は `Send` を実装していないため、`tokio::spawn` に渡すと**コンパイルエラー**になります。しかしシングルタスク文脈では通ってしまい、デッドロックの原因になります。

```rust
// ✅ OK 案① スコープを限定する
async fn update(data: Arc<Mutex<Vec<u32>>>) {
    {
        let mut guard = data.lock().unwrap();
        guard.push(42);
    } // ← Guard をここで drop
    some_async_fn().await;
}

// ✅ OK 案② tokio::sync::Mutex を使う
use tokio::sync::Mutex;

async fn update(data: Arc<Mutex<Vec<u32>>>) {
    let mut guard = data.lock().await; // ← async-aware なロック
    some_async_fn().await;
    guard.push(42);
}
```

`tokio::sync::Mutex` は `await` をまたいでも安全です。ただし、**ロック時間が短いなら案① の方が効率的**です。

---

## ④ `tokio::spawn` に `Send` でない型を渡す

```rust
// ❌ NG: Rc は Send ではない
use std::rc::Rc;

#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let x = Rc::new(42); // コンパイルエラー
        println!("{}", x);
    });
}
```

エラーメッセージ:
```
error[E0277]: `Rc<i32>` cannot be sent between threads safely
```

`tokio::spawn` はタスクをスレッド間で移動できるよう、`Future: Send` を要求します。

```rust
// ✅ OK: Arc を使う
use std::sync::Arc;

#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let x = Arc::new(42);
        println!("{}", x);
    });
}
```

シングルスレッドランタイムを使う場合は `tokio::task::LocalSet` + `spawn_local` で `!Send` な型も扱えます。

```rust
// ✅ OK: シングルスレッド専用
#[tokio::main(flavor = "current_thread")]
async fn main() {
    let local = tokio::task::LocalSet::new();
    local.run_until(async {
        tokio::task::spawn_local(async {
            let x = std::rc::Rc::new(42);
            println!("{}", x);
        }).await.unwrap();
    }).await;
}
```

---

## ⑤ `async fn` を trait に定義しようとする（2024 以前の罠）

Rust 1.75 以前では、trait 内で `async fn` を直接宣言できませんでした。

```rust
// ❌ NG (Rust 1.74 以前)
trait Fetcher {
    async fn fetch(&self) -> String;
}
```

**Rust 1.75 (2023-12-28 stable)** から trait 内 `async fn` が安定化されました。ただし、**オブジェクト安全性** (`dyn Trait`) との組み合わせにはまだ制限があります。

```rust
// ✅ OK: Rust 1.75+ での直接記述
trait Fetcher {
    async fn fetch(&self) -> String;
}

// ✅ OK: dyn が必要なら async-trait クレートを併用 (Rust 1.75 以前も含め安全)
use async_trait::async_trait;

#[async_trait]
trait Fetcher {
    async fn fetch(&self) -> String;
}
```

`async-trait` クレートは内部で `Pin<Box<dyn Future>>` に脱糖するため、`dyn Fetcher` が使えます。Rust 1.75+ でもオブジェクトセーフな trait が必要な場合は `async-trait` が現実解です。

---

## ⑥ 無限ループ内で `await` せずビジーループになる

```rust
// ❌ NG: yield ポイントがなく他タスクが飢餓状態になる
async fn polling_loop(flag: Arc<AtomicBool>) {
    loop {
        if flag.load(Ordering::Relaxed) {
            println!("flag set!");
            break;
        }
        // await がないため tokio は他タスクに切り替えられない
    }
}
```

`tokio` のコーオペラティブスケジューリングでは、**`await` が yield ポイント**になります。`await` のないループはランタイムを独占します。

```rust
// ✅ OK: tokio::task::yield_now() で明示的に yield
async fn polling_loop(flag: Arc<AtomicBool>) {
    loop {
        if flag.load(Ordering::Relaxed) {
            println!("flag set!");
            break;
        }
        tokio::task::yield_now().await; // ← 他タスクに実行権を渡す
    }
}

// ✅ より実用的: 短いインターバルを挟む
async fn polling_loop(flag: Arc<AtomicBool>) {
    loop {
        if flag.load(Ordering::Relaxed) {
            break;
        }
        tokio::time::sleep(Duration::from_millis(10)).await;
    }
}
```

---

## ⑦ エラー伝搬で `?` を使うと型が合わない

```rust
// ❌ NG: tokio::spawn のクロージャ内で ? を使うと戻り値型が合わない
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tokio::spawn(async {
        let text = reqwest::get("https://example.com")
            .await?       // ← ここで型不一致
            .text()
            .await?;
        println!("{}", text);
        Ok(())
    });
    Ok(())
}
```

`tokio::spawn` が返す `JoinHandle<T>` の `T` は `Result<(), E>` でも良いですが、`?` を使うには**クロージャの戻り値型を明示する**必要があります。

```rust
// ✅ OK: 戻り値型を明示し、JoinHandle を await する
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let handle = tokio::spawn(async {
        let text = reqwest::get("https://example.com")
            .await
            .map_err(|e| e.to_string())?
            .text()
            .await
            .map_err(|e| e.to_string())?;
        println!("{}", text);
        Ok::<(), String>(())
    });

    handle.await??; // JoinError と内部 Error の二重 ? に注意
    Ok(())
}
```

`handle.await` は `Result<Result<(), E>, JoinError>` を返すため、`??` で二重に unwrap が必要です。anyhow クレートを使うと大幅にシンプルになります。

```rust
// ✅ anyhow を使う場合
use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    let handle = tokio::spawn(async {
        let text = reqwest::get("https://example.com")
            .await?
            .text()
            .await?;
        println!("{}", text);
        anyhow::Ok(())
    });

    handle.await??;
    Ok(())
}
```

---

## まとめ

| # | 罠 | 解決策 |
|---|---|---|
| ① | `await` 忘れ | チェーン全体を目視確認 |
| ② | 重い同期処理のブロッキング | `spawn_blocking` で分離 |
| ③ | `MutexGuard` を `await` またぎ保持 | スコープ分離 or `tokio::sync::Mutex` |
| ④ | `!Send` 型を `spawn` に渡す | `Arc` に変換 or `spawn_local` |
| ⑤ | trait 内 `async fn` | Rust 1.75+ 直書き or `async-trait` |
| ⑥ | `await` なし無限ループ | `yield_now` or スリープ挿入 |
| ⑦ | `?` の型不一致 | 戻り値型明示 or `anyhow` |

Rust の async は「魔法」ではなく、**ポーリングベースの協調スケジューリング**という明確なモデルで動いています。モデルを理解していれば、エラーメッセージも「そりゃそうだ」と読めるようになります。

公式ドキュメントの [Asynchronous Programming in Rust](https://rust-lang.github.io/async-book/) と tokio の [tutorial](https://tokio.rs/tokio/tutorial) は特に充実しているので、深掘りしたい方はぜひ参照してください。

---

## 参考リンク

- [The Rust Programming Language — async/await](https://doc.rust-lang.org/book/)
- [Asynchronous Programming in Rust (async-book)](https://rust-lang.github.io/async-book/)
- [tokio 公式ドキュメント](https://docs.rs/tokio/latest/tokio/)
- [async-trait クレート](https://docs.rs/async-trait/latest/async_trait/)
- [anyhow クレート](https://docs.rs/anyhow/latest/anyhow/)
- [Rust 1.75 リリースノート (async fn in traits)](https://blog.rust-lang.org/2023/12/28/Rust-1.75.0.html)

---

✍️ 本記事の著者: **合同会社ジモラボ**

ジモラボは、八王子を拠点に AI を活用した SaaS を多数開発しています。本記事の技術検証もそうした開発過程の副産物です。

- 🌐 公式サイト: https://locallab.jp
- 🔍 AI SEO 最適化 SaaS: [lookupai.jp](https://lookupai.jp)
- 📺 YouTube: [@locallab_llc](https://www.youtube.com/@locallab_llc)
- ✉️ お問い合わせ: info@locallab.jp

> 興味を持っていただけたら、ぜひ各 SNS のフォローもお願いします!
