---
id: "2026-06-08-aiに書かせる前提でrusttauriに入門する-01"
title: "AIに書かせる前提でRust/Tauriに入門する"
url: "https://zenn.dev/itdo/articles/d0fd231ed255a6"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "OpenAI", "GPT", "JavaScript", "TypeScript"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

## はじめに

Rust と Tauri に入門するとき、普通は Rust の文法、所有権、Cargo、Tauri のプロジェクト構成、フロントエンドと Rust の連携、権限管理、ビルド、配布までを順に学ぶ必要があります。

しかし、最近ではコーディング自体はAIコーディングエージェントに任せるため、人間が理解しておく内容が変わります。

この記事では、**Rust/Tauri をすべて自分で書けるようになること**ではなく、**AIコーディングエージェントに実装を依頼し、出てきた差分をレビューできるレベルになること**を目標にします。

なお、AIコーディングエージェントとして、今回はCodex CLIを使用します。

## この記事の対象読者

この記事は、次のような人を想定しています。

* Rust はほぼ未経験
* Tauri でデスクトップアプリを作りたい
* TypeScript / JavaScript は多少読める
* 実装の大半はAIコーディングエージェントに依頼したい
* ただし、生成されたコードを検証したい

逆に、この記事では以下を深追いしません。

* 高度な lifetime 設計
* unsafe Rust
* Tauri plugin の自作
* Rust 製フロントエンドフレームワーク
* 署名、配布、自動更新
* 大規模アプリケーション設計

## 基本方針

今回は人間とAIコーディングエージェントの役割を以下のように分けます。

```
AIコーディングエージェント:
- 実装案を出す
- コードを書く
- テストや lint を実行する
- 差分を説明する

人間:
- 要件を決める
- 制約を与える
- 実装計画を確認する
- diff を読む
- 権限追加や依存追加をレビューする
- commit してよいか判断する
```

最初に目指すべきなのは「Rust/Tauri を自在に書く力」ではなく、次の能力とします。

```
[ ] Codex に小さく明確な作業指示を出せる
[ ] Rust 側 command の入出力を読める
[ ] frontend 側 invoke との対応を確認できる
[ ] Tauri の capabilities / permissions の過剰許可を見抜ける
[ ] cargo / npm / tauri build の失敗を大まかに切り分けられる
[ ] git diff を見て、受け入れるか戻すか判断できる
```

## Tauri の構造を最初に理解する

Tauri は、Web frontend と Rust backend を組み合わせてデスクトップアプリを作るフレームワークです。

最初に理解すべき構造はこれです。

```
TypeScript / JavaScript frontend
  ↓ invoke
Tauri IPC
  ↓
Rust command
  ↓
OS / ファイル / DB / API など
```

Tauri では、frontend から Rust 関数を呼ぶために command system を使います。command は引数を受け取り、値を返し、エラーや async にも対応します。

参考: [フロントエンドから Rust を呼び出す - Tauri](https://v2.tauri.app/ja/develop/calling-rust/)

Rust 側の例です。

src-tauri/src/lib.rs

```
#[tauri::command]
fn greet(name: String) -> String {
    format!("Hello, {name}")
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

TypeScript 側の例です。

src/main.ts

```
import { invoke } from "@tauri-apps/api/core";

const message = await invoke<string>("greet", { name: "Ota" });
console.log(message);
```

レビュー時は、まず以下を確認します。

```
- Rust 側の command 名と frontend 側の invoke 名が一致しているか
- 引数名が一致しているか
- 戻り値が frontend に渡せる型になっているか
- エラーが握りつぶされていないか
- frontend に返してはいけない情報を返していないか
```

## 環境構築

ここではAIコーディングエージェントとしてCodex CLIを使用します。詳細な手順は公式ドキュメントを確認してください。CLI やフレームワークのインストール手順は変わる可能性があるためです。

### Codex CLI

macOS / Linux の例です。

```
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex
```

初回実行時に認証が求められます。

参考: [Codex CLI - OpenAI Developers](https://developers.openai.com/codex/cli)

### Rust

Rust は rustup で入れます。

```
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
```

インストール後、確認します。

```
rustc --version
cargo --version
```

参考: [The Rust Programming Language - Getting Started](https://doc.rust-lang.org/book/ch01-01-installation.html)

### Tauri プロジェクト

最初は Tauri v2 + TypeScript + Vanilla で十分です。

```
npm create tauri-app@latest
```

選択例です。

```
Frontend language: TypeScript / JavaScript
Package manager: npm or pnpm
UI template: Vanilla
UI flavor: TypeScript
```

作成後、起動します。

```
cd tauri-app
npm install
npm run tauri dev
```

参考: [Create a Project - Tauri](https://v2.tauri.app/start/create-project/)

## Codex CLI は最初からフル権限で使わない

Codex CLI はファイル変更やコマンド実行ができます。便利ですが、最初から全自動・全権限で動かすべきではありません。

まずは read-only で調査させます。

```
codex --sandbox read-only --ask-for-approval on-request
```

実装させる場合も、最初は workspace 内の書き込みに限定します。

```
codex --sandbox workspace-write --ask-for-approval on-request
```

Codex CLI の `--ask-for-approval` は、コマンド実行前に人間の承認を求めるタイミングを制御します。`--sandbox` は、モデルが生成した shell command に対する sandbox policy を指定します。

参考: [Command line options - Codex CLI](https://developers.openai.com/codex/cli/reference)

特に以下は避けます。

```
codex --dangerously-bypass-approvals-and-sandbox
```

これは承認と sandbox をバイパスするオプションです。公式ドキュメントでも、外部で堅牢に隔離された環境でのみ使うべきものとして扱われています。

## Git checkpoint を必ず作る

Codex に作業させる前に branch を切ります。

```
git checkout -b feat/app-version
git status
```

作業後は必ず diff を確認します。

```
git status
git diff --stat
git diff
```

最低限、次を確認します。

```
- 依頼していないファイルが変更されていないか
- package.json / Cargo.toml に不要な依存が追加されていないか
- lockfile の変更理由が説明できるか
- build artifact が混入していないか
- capabilities / permissions が広がっていないか
```

要件に合わない差分であれば戻します。

ファイル単位で戻す場合です。

## Codex に最初に依頼するのは「調査だけ」

いきなり「機能を作って」と依頼しません。まずはプロジェクトを読ませます。

```
この Tauri プロジェクトを調査してください。

目的:
- プロジェクト構成を把握したい
- Rust 側 command、frontend 側 invoke、capabilities、package scripts を確認したい

制約:
- まだファイルは変更しない
- 実装はしない
- 調査結果だけを出す

出力:
- ディレクトリ構成
- Tauri/Rust 側の主要ファイル
- frontend 側の主要ファイル
- 開発・テスト・ビルドコマンド
- 注意すべき security/capability 設定
```

この時点で、Codex がリポジトリ構造を正しく理解しているかを見ます。

## Rust は「読める範囲」を絞る

Codex CLI 前提なら、最初から Rust を完璧に書く必要はありません。

最初に読むべき範囲はこれです。

```
- Cargo.toml
- src/main.rs / src/lib.rs
- mod
- struct
- enum
- match
- Result<T, E>
- Option<T>
- ? 演算子
- String / &str
- Vec<T>
- HashMap<K, V>
- serde::{Serialize, Deserialize}
- std::fs
- std::path::PathBuf
```

たとえば、次のコードを見て意味が分かれば十分です。

```
#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct AppSettings {
    theme: String,
    api_base_url: String,
    log_level: String,
}

#[tauri::command]
fn load_settings() -> Result<AppSettings, String> {
    // ...
}
```

レビュー時に見るのは、主に以下です。

```
- frontend に返す型は何か
- エラーは Result で返しているか
- unwrap() / expect() で安易に panic させていないか
- serde で Serialize / Deserialize できるか
- ファイルパスの扱いが危険ではないか
```

所有権や lifetime は重要ですが、最初から深掘りしすぎると進みません。Codex が書いたコードをレビューする目的なら、まずは関数シグネチャ、戻り値、エラー処理、ファイル IO を読めることを優先します。

## Tauri で最も注意するのは capabilities / permissions

Codex CLI に Tauri を書かせる場合、最も危ないのは「動かすために権限を広げすぎる」ことです。

Tauri v2 の capabilities は、どの window / webview にどの permissions を付与するかを定義します。

参考: [Capabilities - Tauri](https://v2.tauri.app/security/capabilities/)

Codex が以下のような変更を入れた場合は、必ず確認します。

```
- filesystem 権限を広く許可している
- shell 実行権限を追加している
- 使っていない plugin を追加している
- capabilities/default.json に広すぎる permission を追加している
- CSP や security 設定を緩めている
```

レビュー対象として、最低限このファイルを見ます。

```
src-tauri/src/lib.rs
src-tauri/Cargo.toml
src-tauri/tauri.conf.json
src-tauri/capabilities/default.json
package.json
```

## AGENTS.md を置く

Codex に毎回同じ制約を伝えるのは無駄です。リポジトリ直下に `AGENTS.md` を置きます。

Codex は作業前に `AGENTS.md` を読みます。グローバルな指示とプロジェクト固有の指示を重ねることで、毎回同じ作業ルールを適用できます。

参考: [Custom instructions with AGENTS.md - Codex](https://developers.openai.com/codex/guides/agents-md)

例です。

AGENTS.md

```
# AGENTS.md

## Project

This is a Tauri v2 desktop application with a TypeScript frontend and Rust backend.

## Rules

- Before editing, inspect the relevant files and explain the plan.
- Keep changes small and focused.
- Do not add production dependencies without explicit approval.
- Do not use unwrap() or expect() in production Rust code unless justified.
- Return recoverable errors as Result<T, String> or a structured serializable error.
- Keep Tauri permissions and capabilities minimal.
- Do not grant broad filesystem, shell, or network permissions unless explicitly required.
- Do not modify unrelated formatting or refactor unrelated code.

## Verification

After modifying Rust files, run:

- cargo fmt
- cargo clippy --all-targets --all-features -- -D warnings
- cargo test

After modifying frontend files, run:

- npm run lint, if available
- npm test, if available
- npm run build, if available

Before final response, report:

- files changed
- commands run
- test/build result
- remaining risks
```

## 最初の実装課題は「アプリバージョン表示」

最初の課題として、設定保存やファイル操作は少し重いです。

まずはアプリバージョン表示が適しています。

理由は以下です。

```
- ファイル権限が不要
- command / invoke の対応だけを学べる
- 差分が小さい
- 失敗しても戻しやすい
```

Codex への依頼例です。

```
Tauri v2 + TypeScript の既存プロジェクトに、アプリバージョン表示機能を追加してください。

要件:
- frontend のボタンから Rust 側 command を呼び出す
- Rust 側 command はアプリの version 情報を返す
- frontend は返ってきた version を画面に表示する

制約:
- まず関連ファイルを調査し、実装計画だけ提示してください
- こちらが承認するまで変更しないでください
- 新規依存は追加しないでください
- unwrap()/expect() は使わないでください
- capabilities は必要最小限にしてください
- 関係ない UI リファクタリングは禁止です

完了条件:
- cargo fmt が通る
- cargo clippy --all-targets --all-features -- -D warnings が通る
- cargo test が通る
- npm run lint が存在すれば通る
- npm run tauri build が通る
- 変更ファイル一覧、検証結果、残リスクを報告してください
```

この課題で見るべき diff は以下です。

```
- src-tauri/src/lib.rs に command が追加されたか
- invoke_handler に command が登録されているか
- frontend 側 invoke の command 名が一致しているか
- TypeScript 側の戻り値型が明示されているか
- capabilities が不要に変更されていないか
```

## 次の課題は「設定ファイル読み書き」

次にやるなら、設定ファイル読み書きがよいです。

この課題では、Rust/Tauri の重要要素が一通り出ます。

```
- serde
- Result
- ファイル IO
- PathBuf
- command / invoke
- frontend 側のエラー表示
- capabilities / permissions
```

Codex への依頼例です。

```
Tauri v2 + TypeScript の既存プロジェクトに、設定ファイル読み書き機能を追加したいです。

要件:
- frontend から load_settings / save_settings を呼べる
- Rust 側で JSON 設定ファイルを読み書きする
- 設定内容は theme, apiBaseUrl, logLevel の3項目
- 戻り値とエラーは frontend で扱える形にする
- 設定ファイルの保存場所はまず既存設計を調査して提案する
- Tauri capabilities は必要最小限にする

制約:
- まず関連ファイルを調査し、実装計画だけ出してください
- こちらが承認するまで変更しないでください
- unwrap()/expect() は使わないでください
- 新規依存は追加しないでください。必要な場合は理由を説明してください
- 関係ない UI リファクタリングは禁止です

完了条件:
- cargo fmt が通る
- cargo clippy --all-targets --all-features -- -D warnings が通る
- cargo test が通る
- npm run lint が存在すれば通る
- npm run tauri build が通る
- 変更ファイル一覧、検証結果、残リスクを報告してください
```

## 差分レビューのチェックリスト

### Rust 側

```
[ ] unwrap()/expect() が雑に使われていない
[ ] recoverable error が Result で返されている
[ ] frontend に返してよいエラーだけ返している
[ ] serde Serialize / Deserialize が適切
[ ] PathBuf の扱いが危険ではない
[ ] ファイル読み書き対象が想定範囲内
[ ] command の引数と戻り値が frontend と一致している
```

### Tauri 設定

```
[ ] capabilities が最小権限
[ ] 不要な plugin が追加されていない
[ ] shell 権限が追加されていない
[ ] filesystem scope が広すぎない
[ ] tauri.conf.json の identifier / productName / build 設定が壊れていない
[ ] security 設定が緩められていない
```

### Frontend 側

```
[ ] invoke の command 名が Rust 側と一致している
[ ] invoke の引数名が Rust 側と一致している
[ ] 戻り値型が明示されている
[ ] loading 状態がある
[ ] エラー表示がある
[ ] Rust 側の失敗を握りつぶしていない
```

### Git 差分

```
[ ] 依頼していないファイルが変更されていない
[ ] lockfile の変更理由が説明できる
[ ] build artifact が含まれていない
[ ] package.json / Cargo.toml の依存追加が妥当
[ ] テストや検証結果が説明されている
```

## Codex にレビューだけさせるプロンプト

実装後は、Codex に自分自身の差分をレビューさせるのも有効です。ただし、最終判断は人間が行います。

```
現在の未コミット差分をレビューしてください。

観点:
- Rust のエラー処理
- Tauri command / invoke の整合性
- permissions / capabilities の過剰許可
- frontend 側の型安全性
- 不要な依存追加
- テスト不足
- build 不能リスク

制約:
- まだ修正しない
- 指摘は severity: critical / high / medium / low で分類
- 修正案は具体的に書く
```

## 学習順序

### 1週目: Codex CLI と Git

```
- codex 起動
- read-only で調査
- workspace-write で小さい変更
- git diff
- git restore
- git checkout -b
- git commit
```

ゴールです。

```
Codex が何を変更したかを把握し、不要なら戻せる。
```

### 2週目: Rust の読み方

見る範囲です。

```
- struct
- enum
- Result
- Option
- ?
- serde
- std::fs
- PathBuf
```

ゴールです。

```
Rust 側 command の入力、出力、エラー処理を読める。
```

### 3週目: Tauri の境界理解

見る範囲です。

```
- #[tauri::command]
- invoke
- tauri.conf.json
- capabilities/default.json
- package scripts
```

ゴールです。

```
frontend から Rust command を呼ぶ流れを説明できる。
capabilities / permissions の変更が妥当か判断できる。
```

### 4週目: 小さい機能を Codex に任せる

課題例です。

```
- アプリバージョン表示
- 設定ファイル読み込み
- 設定ファイル保存
- ログファイル選択
- ログ検索
```

ゴールです。

```
Codex に実装させ、差分確認、テスト確認、commit 判断までできる。
```

## 最終的な到達ライン

この入門の到達ラインは、次の質問に答えられることです。

```
- Codex はどのファイルを変更したか
- その変更は要件に対応しているか
- 余計な依存を追加していないか
- 余計な Tauri permission を追加していないか
- Rust 側 command と frontend 側 invoke は一致しているか
- エラー処理は妥当か
- cargo fmt / clippy / test / tauri build は通ったか
- この差分を commit してよいか
```

ここまでできれば、Rust/Tauri をすべて自力で書けなくても、Codex CLI を使って小さな Tauri アプリを安全に育てられます。

## まとめ

Codex CLI 前提の Rust/Tauri 入門では、学習範囲を絞るべきです。

最初に必要なのは、Rust を完全に書けることではありません。

必要なのは次の能力です。

```
- Codex に小さく明確な指示を出す
- 実装前に計画を出させる
- 差分を見る
- Rust command の入出力とエラー処理を見る
- frontend invoke との整合性を見る
- Tauri capabilities / permissions の過剰許可を見抜く
- テスト・lint・build の結果を見る
```

Tauri は Web frontend と Rust backend の境界がはっきりしているため、Codex CLI に実装を任せる構成と相性がよいです。

ただし、Tauri は OS 機能やファイルシステムに触れます。permissions / capabilities の確認は必須です。

**Codex に書かせる。人間は設計、制約、レビュー、リスク判断を担当する。**

この分担で始めるのが、現実的な Rust/Tauri 入門になります。

## 参考資料
