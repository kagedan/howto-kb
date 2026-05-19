---
id: "2026-05-18-agentsmd-とシンボリックリンクでjetbrains-ai-の-juniecodexclaud-01"
title: "AGENTS.md とシンボリックリンクで、JetBrains AI の Junie、Codex、Claude Agent をまとめて運用"
url: "https://zenn.dev/nattosystem_jp/articles/e85432144350ef"
source: "zenn"
category: "claude-code"
tags: ["CLAUDE-md", "AI-agent", "OpenAI", "TypeScript", "zenn"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは。ねばねばです。  
私は普段IntelliJ IDEA で、JetBrains AI のコーディングエージェントを切り替えてテストをしています。

JetBrains AI サブスクリプションには、

* **Junie**（JetBrains 自社製、IDE と密に統合されたエージェント）
* **Claude Agent**（Anthropic、Claude Agent SDK 経由で IDE に接続）
* **Codex**（OpenAI、ACP = Agent Client Protocol 経由で接続）

の3つが含まれていて、サブスクリプション外でも **BYOK や ACP 互換エージェント**を追加できる、ベンダー中立な作りになっています。

> **この記事の結論**  
> Junie と Codex は `AGENTS.md` を読む。Claude Agent だけは `CLAUDE.md` を読む。  
> CLAUDE.md を **AGENTS.md へのシンボリックリンク**にすることで、実体ファイル1つで3エージェント全部に同じ指示が行き渡る。

同じ内容を AGENTS.md と CLAUDE.md に二重管理して、片方だけ更新して挙動割れをなくそうの記事です。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--4TgAZjkA--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/5b3c1d38-8b70-4867-86ba-c9bd0a11bd8b.png?_a=BACAGSGT)

## JetBrains IDE と AGENTS.md の相性

「AGENTS.md と JetBrains IDE の相性のよさ」を整理しておきます。**両者がどちらも "ベンダー中立" を志向している**からではないでしょうか。

### JetBrains IDE 側：どのエージェントでも受け入れる設計

JetBrains AI サブスクリプションに含まれる3エージェントは、**それぞれ違う連携方式**で同じ IDE に同居しています。

| エージェント | 連携方式 | 開発元 |
| --- | --- | --- |
| **Junie** | 自社ネイティブ（IDE と最も密に統合） | JetBrains |
| **Claude Agent** | Claude Agent SDK 経由 | Anthropic |
| **Codex** | ACP（Agent Client Protocol、Zed 発のオープン標準）経由 | OpenAI |

「JetBrains 製の Junie + 他社製エージェント2種」が同じ AI Chat の中で切り替えられる状態。さらにサブスクリプション外でも **BYOK / OAuth / ACP 互換エージェント**を後から追加できて、IDE 側は「どのエージェントが来ても受け入れる」スタンスです。

### AGENTS.md 側：どのツールでも読める共通フォーマット

一方の AGENTS.md は、OpenAI Codex・Amp・Google Jules・Cursor・Factory などの協働から生まれた**オープンフォーマット**で、2025年12月には Linux Foundation 配下の Agentic AI Foundation の創設プロジェクトに採用されました。**60,000+ リポジトリ**が既に採用しています。

特定のベンダー製品に紐付かない「AI エージェント向け README」として、ビルド・テスト・規約・禁止事項を1ファイルにまとめる思想です。

### ベンダー中立 × ベンダー中立 = AGENTS.md一本化の希望

IDE は「特定の AI 機能」と密結合していて、別エージェントに乗り換えるとプロジェクト指示も書き直しになりがちです。一方 JetBrains IDE は **複数エージェントが共存する前提**なので、

* 軽い質問は Junie
* 大きめのリファクタは Claude Agent
* コードベース横断の調査は Codex

…のような使い分けが可能です。このとき指示ファイルがエージェントごとに別だと大変なので、**ツール中立な AGENTS.md** をひとつ置いて全員に読ませる、という運用が一番自然になります。

唯一の引っかかりが「Claude Agent だけは CLAUDE.md を読みにいく」点で、これを次のシンボリックリンクで解決します。

## やったこと

### 2.1 AGENTS.md を書く

まずプロジェクトルートに `AGENTS.md` を置きます。書き方はいくつかありますが、Matt Nigh が 2,500+ リポジトリを分析して整理した **6つのコア領域**を参考にしました。

参考: [https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/）](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/%EF%BC%89)

```
# AGENTS.md  
## Commands- 開発サーバ起動: `npm run dev`  
- テスト実行: `npm test`  
- Lint: `npm run lint`  
- ビルド: `npm run build`  
  
## Testing- フレームワーク: Vitest  
- 新規ロジックには必ずユニットテストを追加  
- E2E は `e2e/` 配下  
  
## Project structure- フロント: React 19 + TypeScript 5.6  
- バック: Node 22 + Hono  
- `src/` がアプリ本体、`packages/` が共有ライブラリ  
  
## Code style（コード例を1つ載せる方が説明文より強い）  
  
```ts  
// Good  
export function fetchUser(id: string): Promise<User> { ... }  
```  
  
## Git workflow- Conventional Commits を使用  
- main への直 push 禁止  
  
## Boundaries  
### Always- 変更後は `npm test` を必ず通すこと  
  
### Ask first- マイグレーションファイルの追加・変更  
- 依存ライブラリの追加  
  
### Never- `.env*` を開かない・出力に含めない  
- `node_modules/` を編集しない
```

ポイントは **Boundaries を Always / Ask first / Never の3層**で書くこと。  
次はシンボリックリンクについて見ていきましょう。

### 2.2 シンボリックリンクとは

> **シンボリックリンクとは**  
> ファイルやディレクトリへの「ショートカット」のこと。  
> 実体は1つだけなので、どちらのパスから開いても**常に同じ内容**が読み書きされる。  
> `ln -s 実体 リンク名` で作れる。

イメージとしては、

```
[実体] AGENTS.md  ←──┐  
                     │ "中身を見せて" と聞かれたら同じ実体に転送  
[リンク] CLAUDE.md ──┘
```

CLAUDE.md を開いても、Finder/エクスプローラからは普通のファイルに見えますが、OS が裏で「これはリンクだから AGENTS.md の内容を返すね」と処理してくれます。**コピーではない**ので、AGENTS.md を編集すれば CLAUDE.md 側からも即座に新しい内容が読めます。

### 2.3 CLAUDE.md → AGENTS.md のリンクを張る

#### macOS

```
# プロジェクトルートで  
ln -s AGENTS.md CLAUDE.md
```

`ls -la` で確認するとリンク矢印が見えます:

```
$ ls -la CLAUDE.mdlrwxr-xr-x  1 user  staff  10  5 15 14:22 CLAUDE.md -> AGENTS.md```  
  
#### Windows（PowerShell）  
  
```powershell  
# プロジェクトルートで  
New-Item -ItemType SymbolicLink -Path CLAUDE.md -Target AGENTS.md
```

または cmd で:

```
mklink CLAUDE.md AGENTS.md
```

ただし Windows でシンボリックリンクを作るには **開発者モードを ON** にするか **管理者として実行**する必要があります。

## 検証

3エージェント全部に同じ質問を投げて、AGENTS.md の内容がちゃんと反映されるかを確かめます。

質問は揃えて：

> 「このプロジェクトでテストを走らせるコマンドと、触ってはいけないファイルを教えて」

期待する答えは AGENTS.md の Commands と Boundaries → `npm test` と `.env*` / `node_modules/`。

### 3.1 Junie が AGENTS.md を読んでいることを確認

IntelliJ IDEA の AI Chat でエージェントを Junie に切り替えて質問。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--hkqX2KmJ--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/e2105206-52b2-4524-923b-17e5604bbeb6.png?_a=BACAGSGT)

Junie はセッション開始時に AGENTS.md をガイドラインとして読み込む仕様なので、期待通り `npm test` と `.env*` / `node_modules/` を返してくれました。

### 3.2 Codex が AGENTS.md を読んでいることを確認

エージェントを Codex に切り替えて同じ質問。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--lD6o3RgN--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/862103e4-82bf-48d1-8118-c95e8a3f12f8.png?_a=BACAGSGT)

Codex も AGENTS.md 対応しているので、同じ答えが返ります。

### 3.3 Claude Agent がシンボリックリンク経由で AGENTS.md を見ていることを確認

エージェントを Claude Agent に切り替えて同じ質問。Claude Agent は本来 `CLAUDE.md` を見にいく仕様ですが、CLAUDE.md の実体が AGENTS.md なので**同じ内容**が読まれます。

![image.png](https://res.cloudinary.com/zenn/image/fetch/s--hwli31T_--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3978583/589b0f64-b39b-4306-ae0b-25a50a958038.png?_a=BACAGSGT)

確認のために、Claude Agent に「いま読んでいる指示ファイルのパスとサイズを教えて」と聞くと、`CLAUDE.md` を読んでいると答えますが、OS 側で AGENTS.md にリダイレクトされているので**中身はAGENTS.mdから供給**されています。

## まとめ

JetBrains AI で複数エージェントを使い分けるなら、

1. プロジェクトルートに **AGENTS.md** を設置
2. **`ln -s AGENTS.md CLAUDE.md`**（Windows なら `mklink` or `New-Item -ItemType SymbolicLink`）でリンクを張る
3. これで Junie / Codex / Claude Agent の3エージェント全部に同じ指示が届く

という運用が、いまのところ気持ちいいです。

ぜひ試してみてください！

## ナットウシステムからのお知らせ

弊社は JetBrains 製品に関するご質問、ご相談等を受け付けております。弊社の[X](https://x.com/nattosystem?s=20)または[メール](mailto:sales@nattosystem.com)でご連絡ください。

## 参考資料

### AGENTS.md（オープン標準）

### Junie（JetBrains 自社エージェント）

### ACP（Agent Client Protocol）と Codex / Claude Agent の同居

### Claude Agent / CLAUDE.md
