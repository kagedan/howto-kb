---
id: "2026-05-19-gpui-testappcontextの全貌-aiエージェント時代のデスクトップアプリ開発テスト戦略-01"
title: "GPUI TestAppContextの全貌 ── AIエージェント時代のデスクトップアプリ開発テスト戦略"
url: "https://zenn.dev/syuya2036/articles/gpui-testing-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "API", "zenn"]
date_published: "2026-05-19"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

## はじめに：デスクトップGUIアプリのテストという壁

Web開発では、AIエージェント（Claude Code、Cursor等）がブラウザを自動操作して動作確認まで行える時代になった。Playwrightでヘッドレスブラウザを立ち上げ、DOMを操作し、スクリーンショットを撮り、アサーションを書く。AIが書いたコードをAIが検証する、そのループが成立している。

一方、デスクトップGUIアプリケーションにはこの等価物がない。OSのウィンドウシステム、GPUレンダリング、プラットフォーム固有の入力処理に依存しており、ヘッドレスでの自動操作は困難だ。DOMツリーのような統一的な構造化表現もなく、UI要素をプログラムから参照・操作する標準手段が存在しない。

この問題に対して、ZedエディタのUIフレームワークであるGPUIは設計レベルで回答を用意している。それが `TestAppContext` を中心としたテストインフラだ。

本記事では、GPUIの `TestAppContext` のアーキテクチャとAPIを網羅的に解説し、AIエージェントを活用したGPUIデスクトップアプリ開発のワークフローを具体的に論じる。

## GPUIテストインフラの全体像

GPUIのテストインフラは、以下の5つのコンポーネントで構成される。

| コンポーネント | ソースファイル | 役割 |
| --- | --- | --- |
| `TestAppContext` | `crates/gpui/src/app/test_context.rs` | アプリケーションコンテキストのテスト版 |
| `VisualTestContext` | 同上 | ウィンドウ付きテストコンテキスト |
| `TestPlatform` | `crates/gpui/src/platform/test/platform.rs` | OS依存なしのプラットフォーム実装 |
| `TestWindow` | `crates/gpui/src/platform/test/window.rs` | レンダリングなしのウィンドウ実装 |
| `TestDispatcher` | `crates/gpui/src/platform/test/dispatcher.rs` | 決定論的な非同期タスクスケジューラ |

核心的な設計思想は「プラットフォーム層の完全な差し替え」だ。本番ではmacOSのMetal、LinuxのVulkanに依存するレンダリングやウィンドウ管理を、テストではすべてインメモリのモック実装に置き換える。GPUもウィンドウシステムも不要。`cargo test`だけで完結する。

```
┌─────────────────────────────────────────┐
│           Application Logic             │
├─────────────────────────────────────────┤
│           GPUI Framework                │
├──────────────────┬──────────────────────┤
│  Production      │  Test                │
│  ┌────────────┐  │  ┌────────────────┐  │
│  │ Platform   │  │  │ TestPlatform   │  │
│  │ (Metal/    │  │  │ (in-memory)    │  │
│  │  Vulkan)   │  │  │                │  │
│  ├────────────┤  │  ├────────────────┤  │
│  │ Window     │  │  │ TestWindow     │  │
│  │ (OS Window)│  │  │ (no rendering) │  │
│  ├────────────┤  │  ├────────────────┤  │
│  │ Dispatcher │  │  │ TestDispatcher │  │
│  │ (OS thread)│  │  │ (deterministic)│  │
│  └────────────┘  │  └────────────────┘  │
└──────────────────┴──────────────────────┘
```

## TestAppContext：テストの心臓部

### 構造

`TestAppContext`は、GPUIの`App`コンテキストのテスト版だ。実際のOS環境を必要とせず、アプリケーション全体の状態管理・イベント処理・非同期タスク実行をシミュレートする。

```
#[derive(Clone)]
pub struct TestAppContext {
    #[doc(hidden)] pub app: Rc<AppCell>,
    #[doc(hidden)] pub background_executor: BackgroundExecutor,
    #[doc(hidden)] pub foreground_executor: ForegroundExecutor,
    #[doc(hidden)] pub dispatcher: TestDispatcher,
    test_platform: Rc<TestPlatform>,
    text_system: Arc<TextSystem>,
    fn_name: Option<&'static str>,
    on_quit: Rc<RefCell<Vec<Box<dyn FnOnce() + 'static>>>>,
}
```

通常の`AsyncApp`がアクセスエラー時に`Result`を返すのに対し、`TestAppContext`は存在しないアプリやウィンドウへのアクセスで**パニック**する。テストコードでは失敗は大きな音で伝えるべきだからだ。

### `#[gpui::test]`マクロによる自動注入

テストの入り口は`#[gpui::test]`マクロだ。このマクロが`TestAppContext`の生成、テスト関数の呼び出し、後片付けまでを自動化する。

```
#[gpui::test]
async fn test_something(cx: &mut TestAppContext) {
    // cxは自動的に注入される
}
```

マクロが行うことは以下の通り。

1. `TestDispatcher`をシードから生成
2. `TestAppContext`をディスパッチャから構築
3. テスト関数を呼び出し
4. `run_until_parked()`で残存タスクをフラッシュ
5. パーキングを禁止し、全コンテキストをクリーンアップ

マクロには複数のオプションがある。

```
#[gpui::test]                        // シード0で1回実行
#[gpui::test(iterations = 100)]      // シード0..100で100回実行
#[gpui::test(seed = 42)]             // 特定シードで実行
#[gpui::test(retries = 3)]           // 失敗時3回リトライ
#[gpui::test(on_failure = "dump")]   // 失敗時にカスタム関数呼び出し
```

`iterations`は特に強力だ。`TestDispatcher`はシードベースのスケジューラを使うため、異なるシードで非同期タスクの実行順序が変わる。100回回せばレースコンディションの検出確率が飛躍的に上がる。失敗したシードは出力されるので、`SEED=N cargo test`で再現可能だ。

### 複数クライアントのシミュレーション

関数シグネチャに複数の`TestAppContext`を取ることで、マルチクライアントテストが書ける。

```
#[gpui::test]
async fn test_collaboration(
    cx_a: &mut TestAppContext,
    cx_b: &mut TestAppContext,
) {
    // cx_aとcx_bは同じexecutorを共有し、
    // 非同期タスクが決定論的にインターリーブする
}
```

Zedのリアルタイムコラボレーション機能は、まさにこのパターンで網羅的にテストされている。

## TestAppContextの主要API

### アプリケーション状態へのアクセス

```
// 可変アクセス
cx.update(|app| {
    // &mut App を使った操作
});

// 読み取り専用アクセス
cx.read(|app| {
    // &App を使った操作
});

// Entity（モデル）の読み取り
cx.read_entity(&entity, |model, app| {
    assert_eq!(model.value, 42);
});
```

### ウィンドウの作成

```
// ビューを持つウィンドウを作成
let window_handle = cx.add_window(|window, cx| {
    MyView::new(window, cx)
});

// 空のウィンドウを作成（VisualTestContextが返る）
let vcx = cx.add_empty_window();

// ビューとVisualTestContextを同時に取得（最もよく使うパターン）
let (view, cx) = cx.add_window_view(|window, cx| {
    MyView::new(window, cx)
});
// ここからcxはVisualTestContext（元のTestAppContextをシャドウイング）
```

### 入力シミュレーション

```
// キーストローク（スペース区切りで複数指定可能）
cx.simulate_keystrokes(window, "cmd-shift-p");
cx.simulate_keystrokes(window, "ctrl-c ctrl-v");

// テキスト入力（1文字ずつディスパッチ）
cx.simulate_input(window, "hello world");

// アクションのディスパッチ（フォーカス中のノードに送信）
cx.dispatch_action(window, editor::actions::Save);
```

`simulate_keystrokes`と`simulate_input`は内部で自動的に`run_until_parked()`を呼ぶため、呼び出し後すぐにアサーションを書ける。

### プラットフォーム機能のシミュレーション

```
// クリップボード
cx.write_to_clipboard(ClipboardItem::new_string("copied text"));
let item = cx.read_from_clipboard();

// ファイルダイアログ（保存先選択）
cx.simulate_new_path_selection(|_dir| {
    Some(PathBuf::from("/tmp/test.txt"))
});

// アラートダイアログ（「保存しますか？」等）
cx.simulate_prompt_answer("Save");
assert!(cx.has_pending_prompt());

// URLオープン
let url = cx.opened_url();
```

### 非同期処理の同期

```
// 最重要メソッド：保留中の非同期タスクがすべて完了するまで待機
cx.run_until_parked();
```

`run_until_parked()`はGPUIテストにおける同期の要だ。非同期処理をトリガーした後、このメソッドを呼ぶことで、すべてのバックグラウンドタスクが完了（またはブロック状態）になるまで待機する。内部的には`TestDispatcher`の`tick()`をループで回し、実行可能なタスクがなくなるまで処理を進める。

```
model.update(cx, |m, cx| m.start_async_work(cx));
cx.run_until_parked();  // 非同期処理が落ち着くまで待機
// ここでアサーション可能
```

### イベント監視

```
// エンティティの更新通知ストリーム
let notifications = cx.notifications(&entity);

// 型付きイベントの受信
let mut events = cx.events::<MyEvent, MyModel>(&model);

// 条件が真になるまで待機（3秒タイムアウト）
cx.condition(&model, |model, _cx| model.is_loaded).await;

// 次のイベント発火まで待機
let event = model.next_event::<MyEvent>(cx).await;
```

### グローバル状態

```
cx.set_global(AppSettings { dark_mode: true });

cx.read_global::<AppSettings, _>(|settings, _app| {
    assert!(settings.dark_mode);
});

cx.update_global::<AppSettings, _>(|settings, _app| {
    settings.dark_mode = false;
});
```

## VisualTestContext：ウィンドウ操作の簡略化

`VisualTestContext`は`TestAppContext` + `AnyWindowHandle`のラッパーだ。`Deref`で`TestAppContext`のすべてのメソッドにアクセスでき、加えてウィンドウハンドルの指定が不要なAPIを提供する。

```
#[derive(Deref, DerefMut, Clone)]
pub struct VisualTestContext {
    #[deref]
    #[deref_mut]
    pub cx: TestAppContext,
    window: AnyWindowHandle,
}
```

### マウス操作のシミュレーション

```
// クリック（MouseDown + MouseUp）
cx.simulate_click(point(px(100.0), px(50.0)), Modifiers::default());

// マウス移動
cx.simulate_mouse_move(
    point(px(200.0), px(100.0)),
    Some(MouseButton::Left),  // ドラッグ中のボタン
    Modifiers::default(),
);

// マウスダウン・アップの個別制御
cx.simulate_mouse_down(point(px(100.0), px(50.0)), MouseButton::Left, Modifiers::default());
cx.simulate_mouse_up(point(px(100.0), px(50.0)), MouseButton::Left, Modifiers::default());

// 修飾キーの変更
cx.simulate_modifiers_change(Modifiers {
    shift: true,
    ..Default::default()
});
```

### 要素の描画とヒットテスト

マウスイベントをシミュレートする前に、要素ツリーを描画しておく必要がある。描画していない状態でイベントをシミュレートしても、ヒットテスト対象の要素が存在しない。

```
// 要素を描画
cx.draw(
    point(px(0.0), px(0.0)),
    size(
        AvailableSpace::Definite(px(500.0)),
        AvailableSpace::Definite(px(300.0)),
    ),
    |window, app| view.read(app).render(window, app),
);

// 描画後にクリックをシミュレート
cx.simulate_click(point(px(100.0), px(50.0)), Modifiers::default());

// 名前付き要素のバウンディングボックスを取得
if let Some(bounds) = cx.debug_bounds("my_button") {
    cx.simulate_click(bounds.center(), Modifiers::default());
}
```

### ウィンドウライフサイクル

```
// リサイズ
cx.simulate_resize(size(px(1024.0), px(768.0)));

// 非アクティブ化
cx.deactivate_window();

// 閉じる（戻り値はキャンセルされたかどうか）
let cancelled = cx.simulate_close();
```

## 実践的なテストパターン集

### パターン1：基本的なモデルテスト

UIを介さず、ビジネスロジックの単体テストを書く最もシンプルなパターン。

```
use gpui::{AppContext, TestAppContext};

struct Counter {
    value: i32,
}

#[gpui::test]
async fn test_counter_increment(cx: &mut TestAppContext) {
    let counter = cx.new(|_cx| Counter { value: 0 });

    counter.update(cx, |counter, _cx| {
        counter.value += 1;
    });

    cx.read_entity(&counter, |counter, _app| {
        assert_eq!(counter.value, 1);
    });
}
```

`cx.new()` や `cx.read_entity()` などのメソッドは `AppContext` トレイト経由で提供されているため、トレイトを use する必要がある。

### パターン2：非同期処理のテスト

ファイル読み込みやネットワーク通信など、非同期処理を伴うロジックのテスト。

```
use gpui::{AppContext, Context, TestAppContext};

struct FileLoader {
    content: Option<String>,
}

impl FileLoader {
    fn load(&mut self, cx: &mut Context<Self>) {
        cx.spawn(async move |this, cx| {
            // 非同期でファイル読み込み（テストではモック可能）
            let content = "loaded content".to_string();
            this.update(cx, |this, cx| {
                this.content = Some(content);
                cx.notify();
            }).ok();
        }).detach();
    }
}

#[gpui::test]
async fn test_file_loading(cx: &mut TestAppContext) {
    let loader = cx.new(|_cx| FileLoader { content: None });

    loader.update(cx, |loader, cx| {
        loader.load(cx);
    });

    // 非同期処理の完了を待機
    cx.run_until_parked();

    cx.read_entity(&loader, |loader, _app| {
        assert_eq!(loader.content.as_deref(), Some("loaded content"));
    });
}
```

`cx.spawn` のクロージャは `AsyncFnOnce(WeakEntity<T>, &mut AsyncApp)` を要求するため、`async move |this, cx| { ... }` の AsyncFn 構文で記述する。

### パターン3：ウィンドウとビューのテスト

`VisualTestContext`を使い、ウィンドウ上のビューをテストする。

```
use gpui::{
    div, AppContext, Context, InteractiveElement, IntoElement, ParentElement, Render,
    StatefulInteractiveElement, Styled, TestAppContext, Window,
};

struct ClickCounter {
    clicks: usize,
}

impl Render for ClickCounter {
    fn render(&mut self, _window: &mut Window, cx: &mut Context<Self>) -> impl IntoElement {
        div()
            .id("click-area")
            .size_full()
            .on_click(cx.listener(|this, _event, _window, _cx| {
                this.clicks += 1;
            }))
            .child(format!("Clicks: {}", self.clicks))
    }
}

#[gpui::test]
async fn test_click_counter(cx: &mut TestAppContext) {
    let (view, cx) = cx.add_window_view(|_window, _cx| {
        ClickCounter { clicks: 0 }
    });

    // キーストロークでの操作テスト
    cx.simulate_keystrokes("enter");

    view.update(cx, |counter, _cx| {
        assert_eq!(counter.clicks, 0); // Enterはクリックではない
    });
}
```

`.id()` は `InteractiveElement`、`.on_click()` は `StatefulInteractiveElement` トレイト経由のメソッドなので、両方をインポートしておく必要がある。`Entity<T>::update` のクロージャは `|this, cx|` の2引数。ウィンドウへのアクセスが必要な場合は `VisualTestContext::update_window_entity(&view, |this, window, cx| { ... })` を使う。

### パターン4：イベント駆動テスト

`EventEmitter`トレイトを実装したモデルのイベントをテストする。

```
use futures::StreamExt;
use gpui::{AppContext, EventEmitter, TestAppContext};

struct Editor {
    content: String,
}

#[derive(Clone)]
enum EditorEvent {
    ContentChanged(String),
    Saved,
}

impl EventEmitter<EditorEvent> for Editor {}

#[gpui::test]
async fn test_editor_events(cx: &mut TestAppContext) {
    let editor = cx.new(|_cx| Editor {
        content: String::new(),
    });

    let mut events = cx.events::<EditorEvent, Editor>(&editor);

    editor.update(cx, |editor, cx| {
        editor.content = "hello".to_string();
        cx.emit(EditorEvent::ContentChanged("hello".to_string()));
    });

    // イベントを受信
    match events.next().await {
        Some(EditorEvent::ContentChanged(text)) => {
            assert_eq!(text, "hello");
        }
        _ => panic!("Expected ContentChanged event"),
    }
}
```

`cx.events::<E, T>(...)` のイベント型は `Clone` 制約を要求するため、Event enum には `#[derive(Clone)]` が必要。

### パターン5：ファイルダイアログのテスト

OS依存のファイルダイアログを、`TestPlatform`の機能でシミュレートする。

```
#[gpui::test]
async fn test_save_as(cx: &mut TestAppContext) {
    let (editor_view, cx) = cx.add_window_view(|window, cx| {
        MyEditor::new(window, cx)
    });

    // ファイルダイアログが開いたら /tmp/test.txt を選択したことにする
    cx.simulate_new_path_selection(|_dir| {
        Some(PathBuf::from("/tmp/test.txt"))
    });

    // Save Asアクションを発火
    cx.dispatch_action(SaveAs);
    cx.run_until_parked();

    // ダイアログが表示されたことを確認
    assert!(cx.did_prompt_for_new_path());
}
```

### パターン6：条件待機テスト

特定の状態になるまで待機するパターン。3秒のタイムアウトが設定されている。

```
#[gpui::test]
async fn test_async_initialization(cx: &mut TestAppContext) {
    let app_state = cx.new(|_cx| AppState {
        initialized: false,
        data: Vec::new(),
    });

    app_state.update(cx, |state, cx| {
        state.begin_initialization(cx);
    });

    // initializedがtrueになるまで待機（最大3秒）
    cx.condition(&app_state, |state, _cx| state.initialized).await;

    cx.read_entity(&app_state, |state, _app| {
        assert!(!state.data.is_empty());
    });
}
```

## Zed実例：Vimテストの多層ラッパーパターン

Zedのコードベースには、`TestAppContext`の上に複数のドメイン特化レイヤーを積み重ねたテストコンテキストが存在する。

```
NeovimBackedTestContext
  └── VimTestContext
        └── EditorLspTestContext
              └── VisualTestContext
                    └── TestAppContext
```

各レイヤーが自身のドメインに特化したヘルパーメソッドを追加している。

```
// Zedの実際のVimテスト
#[gpui::test]
async fn test_visual_star_hash(cx: &mut gpui::TestAppContext) {
    let mut cx = NeovimBackedTestContext::new(cx).await;

    cx.set_shared_state("ˇa.c. abcd a.c. abcd").await;
    cx.simulate_shared_keystrokes("v 3 l *").await;
    cx.shared_state().await.assert_matches();
}
```

`NeovimBackedTestContext`は実際のNeovimプロセスと同じキーストロークを並行して実行し、結果を比較する。このような高度なテストも、根底では`TestAppContext`の入力シミュレーションとアサーション機能に依存している。

自分のプロジェクトでも、この多層パターンを参考にドメイン特化のテストコンテキストを構築できる。

```
// 例：ファイルエクスプローラのテストコンテキスト
struct ExplorerTestContext {
    cx: VisualTestContext,
    explorer: Entity<FileExplorer>,
}

impl ExplorerTestContext {
    async fn new(cx: &mut TestAppContext) -> Self {
        let (explorer, cx) = cx.add_window_view(|window, cx| {
            FileExplorer::new(window, cx)
        });
        Self { cx: cx.clone(), explorer }
    }

    fn navigate_to(&mut self, path: &str) {
        // ドメイン特化のヘルパー
        self.explorer.update(&mut self.cx, |explorer, cx| {
            explorer.navigate(PathBuf::from(path), cx);
        });
        self.cx.run_until_parked();
    }

    fn assert_current_dir(&self, expected: &str) {
        self.cx.read_entity(&self.explorer, |explorer, _app| {
            assert_eq!(explorer.current_dir().to_str().unwrap(), expected);
        });
    }
}
```

## AIエージェント時代のGPUI開発戦略

### 課題の本質

AIエージェント（Claude Code、Cursor等）はターミナル/CLIベースで動作する。Webアプリであれば、PlaywrightやSeleniumを介してブラウザを操作し、テスト結果を取得できる。しかしデスクトップGUIアプリでは、画面に描画された内容をAIが「見る」手段がない。

Scott Logicの実験では、AI エージェントに直接ブラウザ操作でテストを実行させた結果、「スクリプト実行と比較して遅く、コストが高く、非決定的」と結論づけている。Webですらそうなのだから、デスクトップGUIでのAI直接操作は現実的ではない。

### TestAppContextが架ける橋

`TestAppContext`はこの問題に対する解だ。画面レンダリングを必要としない、プログラマティックなテストインフラが、AIエージェントとデスクトップアプリの間のインターフェースとして機能する。

```
AIエージェント (Claude Code / Cursor)
    │
    │ テストコード生成
    ▼
#[gpui::test] テスト関数
    │
    │ TestAppContext経由
    ▼
TestPlatform + TestWindow (OS依存なし、レンダリングなし)
    │
    │ エンティティ操作・入力シミュレーション
    ▼
アプリケーションロジック
    │
    │ アサーション結果
    ▼
cargo test 出力 (pass/fail + エラーメッセージ)
    │
    │ 結果をフィードバック
    ▼
AIエージェント (修正 → 再実行)
```

AIエージェントにとって重要なのは、テスト実行がCLIで完結し、結果がテキストで返ることだ。GPUIのテストインフラはこれを完全に満たしている。

### 実践的なAIエージェント活用ワークフロー

#### 1. 仕様のマークダウン文書化

AIエージェントにコンテキストを与えるため、仕様や設計をリポジトリ内にマークダウンで配置する。

```
project/
├── CLAUDE.md        # AI向けプロジェクト概要
├── docs/
│   ├── tech.md      # 技術選択と制約
│   ├── features.md  # 機能要件
│   └── testing.md   # テスト戦略
├── src/
└── tests/
```

#### 2. テスト駆動のAI開発ループ

GPUIの`TestAppContext`を前提に、以下のループをAIエージェントに回させる。

```
Step 1: AIにテストを先に書かせる
  → #[gpui::test]を使ったテストコード生成

Step 2: cargo test で実行
  → 当然失敗する（実装がないため）

Step 3: AIに実装を書かせる
  → テストが通るように実装コード生成

Step 4: cargo test で再実行
  → 通ればOK、失敗ならStep 3に戻る

Step 5: リファクタリング
  → テストが通る状態を維持しつつコード改善
```

このTDDループの各ステップがCLIで完結するため、AIエージェントが自律的に回せる。

#### 3. テスタビリティを意識したアーキテクチャ

AIエージェントがテストを書きやすいコードを設計するためのガイドライン。

**UIとロジックの厳密な分離**

```
// Bad: ロジックがRenderに埋め込まれている
impl Render for FileExplorer {
    fn render(&mut self, window: &mut Window, cx: &mut Context<Self>) -> impl IntoElement {
        let entries = std::fs::read_dir(&self.path).unwrap(); // テスト不可能
        // ...
    }
}

// Good: ロジックはモデルメソッドに分離
impl FileExplorer {
    fn refresh(&mut self, cx: &mut Context<Self>) {
        cx.spawn(|this, mut cx| async move {
            let entries = tokio::fs::read_dir(&this.read(&cx, |t, _| t.path))
                .await.unwrap();
            // ...
        }).detach();
    }
}
```

**コンテキストベースの依存性注入**

GPUIの`AppContext`パターンを活用し、プラットフォーム依存の操作をコンテキスト経由にする。テスト時に`TestAppContext`が自動的にモック版に差し替わる。

```
// プラットフォームのファイルダイアログを直接呼ばず、
// コンテキスト経由でアクセスする
fn save_file(&mut self, window: &mut Window, cx: &mut Context<Self>) {
    let path = window.prompt_for_new_path(cx);
    // TestPlatformが自動的にシミュレーション結果を返す
}
```

**型システムによる不正状態の排除**

Rustの型システムを活用して不正な状態を型レベルで排除すれば、AIが生成するコードの信頼性が上がる。コンパイルエラーはAIにとって最良のフィードバックだ。

```
// 状態遷移を型で表現
enum FileState {
    Unloaded,
    Loading(Task<()>),
    Loaded(FileContent),
    Error(String),
}

// 不正な状態遷移はコンパイルエラーになる設計
```

#### 4. Claude Codeでの具体的な開発フロー

Claude Codeは以下の特性を持つ。

* ターミナルファーストで、`cargo test`とネイティブに統合
* テスト生成時にコードベース全体のパターンを推論
* 失敗テストのエラーメッセージを解析して修正を提案

実際の開発では、以下のようなプロンプトでClaude Codeを活用できる。

```
# テストの生成
「FileExplorerのnavigateメソッドについて、
 TestAppContextを使ったテストを書いて。
 ディレクトリ移動、存在しないパスへの移動、
 親ディレクトリへの移動のケースをカバーして。」

# 実装の生成
「上記のテストが通るようにnavigateメソッドを実装して。」

# テスト実行と修正
「cargo testを実行して、失敗しているテストがあれば修正して。」
```

## gpui-ceでの利用

ZedのGPUIはgpui-ceとしてコミュニティ版がcrates.ioで公開されている。自分のプロジェクトでテスト機能を利用するには、`test-support`フィーチャーフラグを有効化する。

```
[dependencies]
gpui = { package = "gpui-ce", version = "0.3" }

[dev-dependencies]
gpui = { package = "gpui-ce", version = "0.3", features = ["test-support"] }
```

これで`#[gpui::test]`マクロと`TestAppContext`が使えるようになる。

## まとめ

GPUIの`TestAppContext`は、デスクトップGUIアプリケーションのテストを「プラットフォーム非依存」「ヘッドレス」「決定論的」に行うためのインフラだ。

その設計の核心は、プラットフォーム層の完全な差し替えにある。`TestPlatform`、`TestWindow`、`TestDispatcher`が本番のOS環境を完全にシミュレートし、`cargo test`だけでアプリケーション全体の振る舞いを検証可能にする。

AIエージェント時代において、このアプローチの価値はさらに高まる。CLIで完結するテストインフラは、AIがコードを書き、テストし、修正するフィードバックループの基盤となる。Webのブラウザ自動化に相当する「プログラマティックテスト」が、デスクトップアプリ開発においてもAI活用を可能にする鍵だ。

GPUIの`TestAppContext`を活用すれば、AIエージェントと協働するデスクトップアプリ開発のワークフローを今すぐ構築できる。

## 参考資料
