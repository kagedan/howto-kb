---
id: "2026-06-07-antigravity-cliを試してみる-01"
title: "Antigravity-cliを試してみる"
url: "https://zenn.dev/omohikane/articles/endeavour-antigravity-cli"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "Gemini"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

## Gemini-cli は終了してAntigravity-CLIになるらしい

GoogleI/Oでgemini-cliが終了するときいて、後継がどうなのか試してみる。

## インストール

まず何も考えずに`yay` でパッケージ検索してみる。

```
─❯ yay antigravity
14 aur/omarchy-ai-usage-git fdb29ca-1 (+0 0.00)
    AI usage monitoring for Omarchy (Claude, Codex, Gemini, Antigravity) in Waybar
13 aur/kdecodexbar 1.1.0-1 (+0 0.00)
    AI Usage Tracker for KDE Plasma (Codex, Claude, Gemini, Antigravity)
12 aur/cockpit-tools-bin 0.23.11-1 (+1 0.37)
    Universal AI IDE account manager for Antigravity / Codex / GitHub Copilot / Windsurf / Kiro / Cursor / Gemini-cli / CodeBuddy
11 aur/cockpit-tools 0.23.11-1 (+1 0.28)
    Universal AI IDE account manager for Antigravity / Codex / GitHub Copilot / Windsurf / Kiro / Cursor / Gemini-cli / CodeBuddy
10 aur/opencode-antigravity-auth 1.6.0-3 (+1 0.18)
    Google Antigravity OAuth Plugin for opencode
9 aur/uli-git 0.1.0.alpha-1 (+0 0.00)
    Universal Linux Installer co-developed with Antigravity
8 aur/antigravity-manager-git r0.0000000-2 (+0 0.00)
    Professional multi-account manager for Google Gemini & Claude AI (git version)
7 aur/antigravity-manager-bin 0.3.0-5 (+1 0.43) (Out-of-date: 2026-05-12)
    Professional multi-account manager for Google Gemini & Claude AI
6 aur/antigravity-tools-bin 4.1.33-2 (+3 0.62)
    Professional Antigravity Account Manager & Switcher
5 aur/antigravity-cli-bin 1.0.0-1 (+1 1.00)
    Google Antigravity CLI (agy)
4 aur/antigravity-cli 1.0.0_5288553236791296-1 (+1 1.00)
    Google's agentic development platform (CLI companion)
3 aur/antigravity-appimage-bin 2.0.0-1 (+0 0.00)
    An agentic development platform from Google, evolving the IDE into the agent-first era.(AppImage)
2 aur/antigravity-ide 2.0.1-1 (+1 1.00) (Out-of-date: 2026-05-20)
    Antigravity Development IDE
1 aur/antigravity 1.23.2-1 (+73 13.35) (Out-of-date: 2026-05-20) (Installed)
    An agentic development platform from Google, evolving the IDE into the agent-first era.
```

どうやらもうaurに入っているらしい。

```
yay -S aur/antigravity-cli-bin

agy --version
1.0.0

agy

     ▄▀▀▄
    ▀▀▀▀▀▀
   ▀▀▀▀▀▀▀▀
  ▄▀▀    ▀▀▄
 ▄▀▀      ▀▀▄

 Welcome to the Antigravity CLI. You are currently not signed in.

 Select login method:
 > 1. Google OAuth
   2. Use a Google Cloud project

 [Use arrow keys to navigate, Enter to select]

認証を終えたらカラーテーマ選択

Choose your color scheme:        ╭───────────────────────────────────────────────────────╮
                                 │ > you: add a greeting function                        │
  > light                        │                                                       │
    solarized light              │   AGY: Here's the change:                             │
    colorblind-friendly light    │                                                       │
    dark                         │  3   import "fmt"                                     │
    solarized dark               │  4                                                    │
    colorblind-friendly dark     │  5 - func main() {                                    │
    tokyo night                  │  5 + func greet(name string) {                        │
    terminal                     │  6 +     fmt.Printf("Hello, %s!\n", name)             │
                                 │  7   }                                                │
                                 ╰───────────────────────────────────────────────────────╯

    [Next]

  ↑/↓ Navigate · enter Confirm

      [ ] Yes, I agree to help improve Antigravity CLI by allowing
      Google to collect and use my Interactions data,
      subject to the Google Antigravity CLI Terms of Service
      and Google Privacy Policy. I understand I can
      choose to opt out later whenever I want via my
      settings.

      Links:
      - Terms of Service: https://antigravity.google/terms
      - Privacy Policy: https://policies.google.com/privacy

    [Previous]    >  Done

同意をえらんで すすむ

モデルの一覧をみてみる
/model
Switch Model

> Gemini 3.5 Flash (High)      (current)
  Gemini 3.5 Flash (Medium)
  Gemini 3.1 Pro (High)
  Gemini 3.1 Pro (Low)
  Claude Sonnet 4.6 (Thinking)
  Claude Opus 4.6 (Thinking)
  GPT-OSS 120B (Medium)

Keyboard: ↑/↓ Navigate  enter Select  esc Go Back

esc to cancel
```

モデルをgemini以外を選択できるようになっている点がよい。  
以前のgemini-cliではできなかったので、IDE版のに近くなった。

### 基本 記憶テスト

ルール3つを伝えた直後に確認 → 保持できていた。  
ただし、これは1ターン後の確認なので甘いテスト。  
複数ターン挟んだ後の保持は未検証。

## テスト：モデル間のコード品質比較

別途Claude Opus 4.6にテスト用のプロンプトを設計させ、それをAntigravity CLI上で実行した。

```
 ⎿  Model set to Gemini 3.5 Flash (Medium)

────────────────────────────────────────────────────────────
> 以下のルールを覚えて。
  1. 変数名はsnake_case
  2. コメントは日本語
  3. エラーハンドリングは必ずResult型

  では、HTTPリクエストを送ってJSONをパースする関数をRustで書いて。

▸ Thought for 3s, 278 tokens
  Developing the Core Logic

● Bash(mkdir -p /home/r1ppl3/.gemini/antigravity-cli/scratch/rust_h...)
● Bash(cargo add reqwest --features json && cargo add serde --featu...) (ctrl+o to expand)

▸ Thought for 5s, 105 tokens
  Constructing Code Now

● Create(/home/r1ppl3/.gemini/antigra...h/rust_http_json/src/main.rs)
● Bash(cargo check) (ctrl+o to expand)

  manager_task:status{Action:status,TaskId:8606b01f-cf55-4959-82ab-72d3b4c1a835/task-10,toolAction:Checking cargo check status,toolSummary:Task status check}
  ご指定のルールに従い、RustでHTTPリクエストを送信してJSONをパースする関数を作成しました。

  ### 実装のポイント

  1. snake_case: 変数名（ target_url ,  http_client  など）に採用。
  2. 日本語コメント: 処理内容を日本語で記述。
  3. Result型: エラーハンドリングに  Result<T, Box<dyn Error>>  を使用。

  ### ソースコード (main.rs)

    use serde::de::DeserializeOwned;
    use reqwest;
    use std::error::Error;

    /// 指定されたURLにGETリクエストを送信し、レスポンスをJSONとしてパースする関数
    ///
    /// # 引数
    /// * `target_url` - リクエストを送信する先のURL
    ///
    /// # 戻り値
    /// パースに成功した場合は Ok(T)、失敗した場合は Err を返す
    pub async fn fetch_json<T>(target_url: &str) -> Result<T, Box<dyn Error>>
    where
        T: DeserializeOwned,
    {
        // HTTPクライアントを作成
        let http_client = reqwest::Client::new();

        // GETリクエストを送信
        let response = http_client
            .get(target_url)
            .send()
            .await?;

        // レスポンスのステータスを確認
        let response_status = response.status();
        if !response_status.is_success() {
            // エラーハンドリング: 成功以外のステータスコードはエラーとして扱う
            return Err(format!("HTTPリクエストが失敗しました。ステータス: {}", response_status).into());
        }

        // JSONとしてパース
        let parsed_data = response
            .json::<T>()
            .await?;

        Ok(parsed_data)
    }

    #[tokio::main]
    async fn main() -> Result<(), Box<dyn Error>> {
        // 使用例: GitHub APIから情報を取得
        let api_url = "https://api.github.com/repos/rust-lang/rust";

        println!("{} からデータを取得中...", api_url);

        // 実際の運用ではパース先の構造体を定義して呼び出します
        // let data: MyData = fetch_json(api_url).await?;

        Ok(())
    }

  ### 補足

  このプロジェクトは以下のディレクトリに作成しました。作業を続ける場合は、このディレクトリをアクティブなワークスペースとして設定することをお勧めします。
   .gemini/antigravity-cli/scratch/rust_http_json

  依存関係として  reqwest ,  serde ,  serde_json ,  tokio  を  Cargo.toml  に追加済みです。
```

## 設計タスク

```
以下の要件でRustのCLIツールを設計・実装して。

要件：
- 複数のログファイル（JSON Lines形式）を並列で読み込む
- 指定した時間範囲でフィルタリング
- 重複するエントリをマージ
- 結果をstdoutにJSON配列として出力

制約：
- メモリ使用量を抑える（1GBのファイルも処理できること）
- エラー時は部分結果を出力して続行

設計判断も含めて説明して。

  ご要望の要件を満たすRustのCLIツールを実装しました。

  ### 設計判断と解説

  #### 1. メモリ使用量の抑制 (1GB超のファイル対応)

  • ストリーミング処理:  BufReader::new(file).lines()  を使用し、ファイルを一行ずつ読み込むことで、巨大なファイルでもメモリ使用量を一定（定数オーダー）に抑えています。
  • 重複排除のメモリ効率:  DashMap<String, LogEntry>  を使用しています。1GBのログに膨大なユニークエントリがある場合、ここがメモリを消費しますが、 LogEntry
  をそのまま保持せず、ID（ハッシュ等）のみを管理するように拡張することで、さらなる節約も可能です。

  #### 2. 並列処理

  • Tokioによる非同期並列実行: 各ファイル読み込みを  tokio::spawn  で個別のタスクとして実行します。これにより、マルチコアを活かした高速なパースとI/Oが可能です。
  • スレッドセーフな共有状態:  Arc<DashMap<...>>  を用いて、複数のスレッドから安全にマージ処理を行えるようにしています。

  #### 3. エラー時の継続性

  • Result型の活用: 各ステップで  Result  を返しつつ、個別の行のパースエラーや読み込みエラーが発生した場合は、 eprintln!  で  stderr  に警告を出力し、次の行や次のファイルへ処理を続行する設計にしています。

  #### 4. JSON配列としての出力

  • ストリーミング出力: 最後に  [  を出力し、イテレータを回しながら一つずつ  serde_json::to_writer  で出力、最後に  ]  を閉じることで、結果をJSON配列として正しく構築して  stdout  へ流します。
  ──────
  ### 実装ファイル (main.rs)

    use anyhow::{Context, Result};
    use chrono::{DateTime, Utc};
    use clap::Parser;
    use dashmap::DashMap;
    use serde::{Deserialize, Serialize};
    use std::fs::File;
    use std::io::{self, BufRead, BufReader, Write};
    use std::path::PathBuf;
    use std::sync::Arc;

    /// ログエントリの構造定義
    #[derive(Debug, Serialize, Deserialize, Clone)]
    struct LogEntry {
        #[serde(default)]
        id: String,
        timestamp: DateTime<Utc>,
        level: String,
        message: String,
        #[serde(flatten)]
        extra: serde_json::Value,
    }

    #[derive(Parser, Debug)]
    #[command(author, version, about, long_about = None)]
    struct Args {
        /// 入力ログファイル（複数指定可能）
        #[arg(short, long, required = true)]
        files: Vec<PathBuf>,

        /// 開始時間（ISO 8601形式）
        #[arg(short, long)]
        start_time: Option<DateTime<Utc>>,

        /// 終了時間（ISO 8601形式）
        #[arg(short, long)]
        end_time: Option<DateTime<Utc>>,
    }

    /// ファイルを読み込み、フィルタリングと重複チェックを行う
    async fn process_log_file(
        file_path: PathBuf,
        start_time: Option<DateTime<Utc>>,
        end_time: Option<DateTime<Utc>>,
        merged_entries: Arc<DashMap<String, LogEntry>>,
    ) -> Result<()> {
        let file = File::open(&file_path)
            .with_context(|| format!("ファイルを開けませんでした: {:?}", file_path))?;
        let reader = BufReader::new(file);

        for line_result in reader.lines() {
            let line = match line_result {
                Ok(l) => l,
                Err(e) => {
                    eprintln!("警告: 行の読み込み中にエラーが発生しました ({:?}): {}", file_path, e);
                    continue;
                }
            };

            if line.trim().is_empty() {
                continue;
            }

            // JSONパース
            let entry: LogEntry = match serde_json::from_str(&line) {
                Ok(e) => e,
                Err(e) => {
                    eprintln!("警告: JSONのパースに失敗しました (ファイル: {:?}, 行: {}): {}", file_path, line, e);
                    continue;
                }
            };

            // 時間範囲でのフィルタリング
            if let Some(start) = start_time {
                if entry.timestamp < start {
                    continue;
                }
            }
            if let Some(end) = end_time {
                if entry.timestamp > end {
                    continue;
                }
            }

            // IDをキーにしてマージ（重複排除）
            let key = if entry.id.is_empty() {
                // IDがない場合は内容からユニークなキーを生成
                format!("{}_{}_{}", entry.timestamp, entry.level, entry.message)
            } else {
                entry.id.clone()
            };

            merged_entries.entry(key).or_insert(entry);
        }

        Ok(())
    }

    #[tokio::main]
    async fn main() -> Result<()> {
        let args = Args::parse();

        // 重複を排除・マージするための共有マップ
        let merged_entries = Arc::new(DashMap::new());
        let mut tasks = Vec::new();

        // 各ファイルを並列に処理
        for file_path in args.files {
            let merged_entries_clone = Arc::clone(&merged_entries);
            let start_time = args.start_time;
            let end_time = args.end_time;

            let task = tokio::spawn(async move {
                if let Err(e) = process_log_file(file_path, start_time, end_time, merged_entries_clone).await {
                    eprintln!("エラー: ファイルの処理中に致命的なエラーが発生しました: {}", e);
                }
            });
            tasks.push(task);
        }

        // 全てのタスクの完了を待機
        for task in tasks {
            let _ = task.await;
        }

        // 結果をJSON配列としてstdoutに出力
        let stdout = io::stdout();
        let mut handle = stdout.lock();

        write!(handle, "[")?;
        let mut first = true;
        for entry in merged_entries.iter() {
            if !first {
                write!(handle, ",")?;
            }
            serde_json::to_writer(&mut handle, &*entry)?;
            first = false;
        }
        writeln!(handle, "]")?;

        Ok(())
    }

  ### プロジェクト情報

  • ディレクトリ: /.gemini/antigravity-cli/scratch/rust_log_tool
  • 実行方法:  cargo run -- --files log1.jsonl log2.jsonl --start-time 2023-01-01T00:00:00Z
```

## 評価（Claude Opus 4.6による）

Gemini3.5-Flashが出したコードをClaude Opus 4.6に評価させた。以下評価ポイント。

### ✅ 合格点

* **BufReader + lines()** → ストリーム読み込みは正しい
* **エラー処理** → eprintln + continue で続行。要件通り
* **設計説明がある** → コード貼るだけじゃない

---

### ❌ 穴①：メモリ制約を実は満たしていない

Rust

let merged\_entries = Arc::new(DashMap::new());

**全ユニークエントリがDashMapに載る**。1GBのログにユニークエントリが数百万件あったら、普通にOOMする。

本人も「ここがメモリを消費します」と書いてるが、**対策を「拡張可能」で逃げてる**。要件は「1GBのファイルも処理できること」なのに、実装が満たしていない。

正解は：ソート済みストリームのk-way mergeか、外部ソート。

---

### ❌ 穴②：tokio::spawnでブロッキングI/O

Rust

let task = tokio::spawn(async move {

// File::open + BufReader::lines() ← これは同期I/O

});

`std::fs::File` + `BufReader::lines()` は**ブロッキング**。tokioのランタイムスレッドを詰まらせる。

正しくは `tokio::task::spawn_blocking` か `tokio::fs` を使うべき。

---

### ❌ 穴③：「ストリーミング出力」と言いつつ全件バッファ

DashMapに全部溜めてから最後にイテレートしてるだけ。これはストリーミングじゃない。本当のストリーミングなら、channel経由で処理しながら出力する設計になる。

---

## 採点

| 観点 | 判定 |
| --- | --- |
| メモリ制約 | ❌ 実質未達 |
| 並列処理 | △ 動くが設計ミス |
| 重複マージ | △ 力技 |
| エラー処理 | ✅ |
| 設計説明 | △ 浅い。トレードオフの言語化が弱い |

---

## 総評

**「動くコードを速く出す」能力は十分ある。  
「設計判断の深さ」が足りない。**

これがGemini 3.5 Flash (Medium)の天井。同じプロンプトをClaude Opus 4.6 (Thinking)に投げたら、穴①②③を自分から指摘した上で設計を組む可能性が高い。

試してみる価値はある。

## Claude Opusに変えてやってみる

```
> 以下の要件でRustのCLIツールを設計・実装して。

  要件：
  - 複数のログファイル（JSON Lines形式）を並列で読み込む
  - 指定した時間範囲でフィルタリング
  - 重複するエントリをマージ
  - 結果をstdoutにJSON配列として出力

  制約：
  - メモリ使用量を抑える（1GBのファイルも処理できること）
  - エラー時は部分結果を出力して続行

  設計判断も含めて説明して。 ふぁいるめいはopusでつくったとわかるようにしてつくってみて。

▸ Thought for 6s
  The user is repeating the same request. Let me look at what happened - I started...
  了解。前回途中だったので、最初からきちんと作り直します。

  設計を改善し、チャネルベースのストリーミング方式で実装します。ファイル名は  opus_  プレフィックスで統一します。

● Bash(cd /home/r1ppl3/.gemini/antigravity-cli/scratch/opus_log_mer...) (ctrl+o to expand)

  依存関係が入ったので、ソースファイルを作っていきます。

● Create(/home/r1ppl3/.gemini/antigra...log_merger/src/opus_entry.rs)
● Create(/home/r1ppl3/.gemini/antigra...og_merger/src/opus_reader.rs)
● Create(/home/r1ppl3/.gemini/antigra...og_merger/src/opus_writer.rs)
● Create(/home/r1ppl3/.gemini/antigra.../opus_log_merger/src/main.rs)
● Bash(cargo check 2>&1) (ctrl+o to expand)

   StdoutLock が Send でないためasyncタスク内で .await をまたげない問題ですね。修正します。

● Create(/home/r1ppl3/.gemini/antigra...og_merger/src/opus_writer.rs)
● Bash(cargo check 2>&1) (ctrl+o to expand)

  コンパイル通りました。テスト用のダミーログファイルで動作確認します。

● Bash(mkdir -p /home/r1ppl3/.gemini/antigravity-cli/scratch/opus_l...)
● Bash(cargo run -- testdata/log_a.jsonl testdata/log_b.jsonl --sta...) (ctrl+o to expand)

  全て動作確認できました。結果を整理します。
  ──────
  ## 設計解説

  ### プロジェクト構成

    opus_log_merger/
    ├── src/
    │   ├── main.rs          -- エントリポイント、CLI引数定義
    │   ├── opus_entry.rs    -- ログエントリ構造体、重複判定キー生成、時間フィルタ
    │   ├── opus_reader.rs   -- ファイル並列読み込み、ストリーミングパース
    │   └── opus_writer.rs   -- 重複排除 + ストリーミングJSON出力
    └── testdata/
        ├── log_a.jsonl
        └── log_b.jsonl

  ### 設計判断

  #### 1. メモリ効率: チャネルベース・ストリーミング

  前回の実装（ DashMap 方式）はエントリ全体をメモリに保持していたが、今回は根本的に異なるアプローチを取った。

    [ファイルA] --BufReader行単位--> [spawn_blocking] --mpsc channel--> [writer: 即stdout出力]
    [ファイルB] --BufReader行単位--> [spawn_blocking] ------↗

  • エントリ本体はメモリに溜めず、チャネルを通過したら即stdoutに書き出す
  • 重複判定は HashSet<String> にキー文字列のみを保持（エントリ本体は捨てる）
  • 1GBのファイルでも、メモリ上に残るのはユニークなdedup keyだけ

  #### 2. 並列処理:  spawn_blocking

  ファイルI/Oは本質的にブロッキング操作なので、 tokio::spawn （非同期タスク）ではなく tokio::task::spawn_blocking を使用。これによりtokioのワーカースレッドを占有しない。

  #### 3. エラー耐性: 行単位の続行

  • JSONパースエラー → stderrに警告を出し、次の行へ  continue
  • ファイルオープン失敗 → stderrに警告を出し、他のファイルの処理を続行
  • 不正な行があっても、正常な行は全て出力される

  #### 4.  StdoutLock とasyncの相性問題

   StdoutLock は Send を実装していないため、 .await をまたいで保持できない。各書き込み操作で stdout().lock() を取得・解放することで解決。パフォーマンスへの影響は軽微（lock/unlockは極めて高速）。

  ### テスト結果

    入力: log_a.jsonl (5行, うち1行は不正JSON) + log_b.jsonl (3行, うち1件は重複)
    フィルタ: 2024-06-01 ~ 2024-06-30

  •  evt-004 （7月のエントリ）→ 時間フィルタで除外 ✓
  •  evt-002 （両ファイルに存在）→ 重複排除で1件に ✓
  • 不正JSON行 → stderrに警告、処理続行 ✓
  • IDなしエントリ → ハッシュベースのキーで正常処理 ✓

  ### 使い方

    cargo run -- file1.jsonl file2.jsonl --start-time 2024-01-01T00:00:00Z --end-time 2024-12-31T23:59:59Z

  ソースは  .gemini/antigravity-cli/scratch/opus_log_merger  にあります。
```

### 所感

Flashの出力をチャットベースのOpusにいれた指摘事項を全て潰した上で、StdoutLockのSend問題まで自力で解決している。  
テストデータの自動生成・検証まで含めて、設計判断の深さに明確な差が出ている。  
複雑な設計など思考の深さが必要な場面ではやはりopusの方が優れている。

## Antigravity CLIの現実的な使いみち

テストの結果、モデル品質にはっきり差が出た。  
ではAntigravity CLIをどう使うべきか。まず選べるモデルの性能差を確認する。

### Gemini 3.5 Flash vs 3.1 Pro（ベンチマーク比較）

| ベンチマーク | 3.5 Flash | 3.1 Pro | 勝者 |
| --- | --- | --- | --- |
| Terminal-Bench 2.1（コーディング） | 76.2% | 70.3% | Flash |
| GDPval-AA（エージェント） | 1656 Elo | 1314 Elo | Flash |
| MCP Atlas（ツール使用） | 83.6% | 78.2% | Flash |
| ARC-AGI v2（推論） | 72.1% | 77.1% | Pro |
| 速度 | 284 t/s | 109 t/s | Flash |
| レイテンシ | 803ms | 12,985ms | Flash |

コーディング・エージェント用途では3.5 Flashが完全に上位互換。3.1 Proが勝つのは一部の純粋推論ベンチのみで、速度差は約16倍。CLI用途で3.1 Proを選ぶ理由はほぼない。

### 無料枠の比較

|  | Antigravity CLI | Aider + Gemini API |
| --- | --- | --- |
| Flash無料枠 | 1,000 req/日 | 250 req/日 |
| モデル自由度 | △（選択肢固定） | ◎（任意） |
| ローカルLLM接続 | 不可 | 可 |
| 制限超過時 | ロックアウト | 従量課金で継続 |

### 結論

Antigravity CLIの唯一の優位点は「Gemini 3.5 Flashの無料枠が1日1,000リクエスト」であること。Aiderの無料枠（250 req/日）の4倍にあたる。

ただしClaude Opusはレートリミットと出力トークン制限により実用性が低く、ローカルLLM接続もできない。運用の自由度ではAiderが上。

実戦的な使い方としては：

* Antigravity CLI：Flashで雑用・コード生成・スキャフォールドを無料で大量に回す
* Aider or Claude Code：設計判断・レビュー・複雑なデバッグなど品質が要る場面に使う

「無料でFlashを大量に回すツール」として割り切るなら、Antigravity CLIを残す価値はある。
