---
id: "2026-05-17-opencode-で-claude-code-の-agent-teams-っぽい仕組みを再現しました-02"
title: "opencode で Claude Code の Agent Teams っぽい仕組みを再現しました"
url: "https://zenn.dev/sugi2sugi/articles/18860cb73fa3d8"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "TypeScript", "zenn"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code に **Agent Teams** という機能が登場してから、X（旧Twitter）やYouTube、各種技術ブログでは「すごい」という声が相次いでいます。複数のClaude Agentがチームを組み、それぞれで会話をして、設計・実装・レビューを並列で進める様子はたしかに圧巻です。

一方で、公式ドキュメントには「Agent teams add coordination overhead and **use significantly more tokens** than a single session」と明記されています。つまり、agents-teamはトークンコストが大幅に増加します。そのため、自身みたいにAgents Teamの機能をお金をかけずに使ってみたい・トークンを使用せずに使ってみたい身としては、無料で実装することを考えました。

そこで本記事では、Opencodeの無料モデルである **「MiniMax 2.5 Free」** と **「tmux」** を用いて、同一のプロンプト・同一のベースアプリに対してagents-teamありとなしの2条件でTODOアプリを実装させ、**所要時間・トークン数・成果物の品質**を比較します。

## 背景

もともとは Claude Code の Agent Teams を使いたかったのですが、常用するには費用面の負担がありました。特に複数エージェントを並列で走らせると、コンテキスト量や実行回数が増えやすく、気軽に試しにくいのが悩みでした。

そこで、無料または低コストで使えるオープンな AI コーディングツールを組み合わせれば、同じような開発体験を再現できるのではないかと考えました。

その中で、`tmux`を用いた`agents team`の概要動画を見つけ、Claude を使わなくても Agent Teams を使わなくても、擬似 Agents Teams を実装できそうだと思いました。

<https://www.youtube.com/watch?v=xnVltY6wd-8&t=360s>

今回の方針はシンプルです。

**「Agent Teams の考え方」だけを借りて、実装は opencode + tmux で自作する」** という形です。

## 実験条件

### 共通環境

| 項目 | 内容 |
| --- | --- |
| ベースアプリ | `npx create-next-app@latest`（デフォルト設定） |
| フレームワーク | Next.js（App Router） |
| 言語 | TypeScript |
| スタイリング | Tailwind CSS |
| 追加ライブラリ | なし（禁止） |
| モデル | MiniMax（共通） |

### 実験パターン

| パターン | 説明 |
| --- | --- |
| **A: agents-teamなし** | 単一エージェントにそのままプロンプトを投げる |
| **B: agents-teamあり** | agents-teamを構成した上で同じタスクを依頼する |

### agents-teamの構成と役割

今回のagents-teamは、以下の4つのエージェントで構成しました。

| エージェント | 役割 | 主な出力 |
| --- | --- | --- |
| **architect** | 要件を整理し、コンポーネント設計・ファイル構成・型定義などの設計書を作成する。実装は一切行わない | `docs/architecture.md` |
| **implementer** | architectの設計書をもとに実際のコードを実装する。設計書が届くまで待機する | `app/`以下のソースコード |
| **tester** | implementerの実装をもとにテストケースを作成・実行し、動作を検証する | テストファイル・実行結果 |
| **reviewer** | 全体の実装・テスト結果をレビューし、問題点や改善点をまとめる | レビューコメント |

各エージェントはタスクが完了したら`tmux send-keys`で次のエージェントに通知を送り、バトンを渡していきます。人間が介入するのは最初のarchitectへの指示1回のみです。

### 使用プロンプト

#### agents-teamなし（単一エージェント）

```
You are working on a Next.js app created with `npx create-next-app@latest` (App Router, TypeScript, Tailwind CSS).
Please implement the following features:
1. **Navigation Bar**
   - Displayed on all pages
   - Contains the app title "TODO App" and a link to the home page

2. **TODO App** (on the home page `/`)
   - Add a new TODO item (text input + submit button)
   - Delete a TODO item
   - Toggle a TODO item between complete / incomplete
   - Filter TODOs by status: All / Active / Completed
   - Persist TODO data using localStorage so it survives page reloads

Requirements:
- Use TypeScript
- Use Tailwind CSS for styling
- Keep all logic in the App Router structure (no Pages Router)
- Do not install any additional libraries

Please implement all of the above and make sure the app works correctly.
```

#### agents-teamあり（architectへの初期プロンプト）

architectに渡す最初の指示のみをtmuxで送信し、以降はagent同士が`tmux send-keys`でバトンを渡していく形をとります。

```
tmux send-keys -t dev:0.0 '
You are the architect on this project. Your job is DESIGN ONLY — do not write any implementation code.

We are building a TODO app on a Next.js app created with `npx create-next-app@latest` (App Router, TypeScript, Tailwind CSS).

Please design the following features and output the result to `docs/architecture.md`:

1. **Navigation Bar**
   - Displayed on all pages
   - Contains the app title "TODO App" and a link to the home page

2. **TODO App** (on the home page `/`)
   - Add a new TODO item (text input + submit button)
   - Delete a TODO item
   - Toggle a TODO item between complete / incomplete
   - Filter TODOs by status: All / Active / Completed
   - Persist TODO data using localStorage so it survives page reloads

Constraints (for the implementer to follow — document these in architecture.md):
- TypeScript
- Tailwind CSS for styling
- App Router structure only (no Pages Router)
- No additional libraries

Once `docs/architecture.md` is complete, notify the implementer using:
tmux send-keys -t dev:0.1 "The design document at docs/architecture.md is complete. Please start the implementation based on this design." Enter

Do NOT implement anything yourself. Stop after sending the notification.' Enter
```

人間が操作するのはこの1コマンドのみで、以降は各agentが次のagentへ`tmux send-keys`で通知を送りながら自律的に進んでいきます。

### 計測指標

| 指標 | 説明 |
| --- | --- |
| ⏱ 所要時間 | タスク開始〜完了までの実時間 |
| 📤 トークン数 | トークン合計 |
| 🔄 会話ターン数 | エージェント間またはユーザーとの会話回数 |
| ✅ 動作確認 | 実装された機能が要件を満たしているか（手動チェック） |

## 実験結果

### 定量比較

#### 所要時間

| パターン | 所要時間 |
| --- | --- |
| agents-teamなし | 2m 23s |
| agents-teamあり（合計） | 約 7m 35s |

agents-teamありの内訳：

| エージェント | 所要時間 |
| --- | --- |
| architect | 42s |
| implementer | 2m 28s |
| tester | 2m 42s |
| reviewer | 1m 43s |

#### トークン使用量

| パターン | トークン数 |
| --- | --- |
| agents-teamなし | 約 20k（使用率 10%） |
| agents-teamあり（合計） | 約 84k |

agents-teamありの内訳：

| エージェント | トークン数 | 備考 |
| --- | --- | --- |
| architect | 16k | implementerとの会話は1回 |
| implementer | 22k | testerとの会話は1回 |
| tester | 24k | reviewerとの会話は1回。test環境ゼロの状態からtest実装を含むため、本来はより少ない見込み |
| reviewer | 22k | 会話なし。本来はagent間のまとめ役として機能させる予定だが、AGENTS.mdの設定不備によりgit diffで変更全体を読み取る形になってしまった。設定を修正すれば削減できる見込み |

### 定性比較（成果物の品質）

| チェック項目 | agents-teamなし | agents-teamあり |
| --- | --- | --- |
| 動作確認 | ✅ 動作OK | ✅ 動作OK |
| ナビバーの実装 | ✅ | ✅ |
| TODO追加・削除 | ✅ | ✅ |
| 完了/未完了の切り替え | ✅ | ✅ |
| フィルター機能 | ✅ | ✅ |
| localStorage永続化 | ✅ | ✅ |
| テストケースの作成 | ❌ なし | ✅ あり |
| エラー・問題 | ❌ Hydration エラーあり | ⚠️ 入力文字が背景色と被り視認性が低い（デザイン担当なしのため今回の検証対象外） |

#### agents-teamなしで発生したエラー

```
Uncaught Error: Hydration failed because the server rendered HTML didn't match the client.
As a result this tree will be regenerated on the client.
This can happen if a SSR-ed Client Component used:
```

localStorage を直接参照するコンポーネントがサーバーサイドレンダリング時に実行されたことによる、SSR/CSR の不一致が原因と考えられます。単一エージェントではこの種のSSR考慮漏れが発生しやすい傾向がありました。

## 考察

### トークン数について

agents-teamなしが約20kだったのに対し、agents-teamありは合計約84kと、**約4.2倍**のトークンを消費しました。ただし、この数字にはいくつかの改善余地があります。

* **tester**はtest環境がゼロの状態からの構築を含んでいるため、環境が整っていれば消費量は減る見込み
* **reviewer**はAGENTS.mdの設定不備により、変更全体をgit diffで読み込む形になってしまった。本来は各agentのまとめを受け取る役割にすれば大幅に削減できる

つまり、**現状のトークン数は設定の最適化余地を含んだ上限値**であり、AGENTS.mdを整備すれば差は縮まると考えられます。

### 所要時間について

agents-teamなしの2m23sに対し、agents-teamありの合計は約7m16sと**約3倍**の時間がかかりました。ただし、今回のagents-teamはコーディングだけに対しての検証であり、使用定義から実装・デザイン・もしくは資料作成などの並列実行が可能なタスクの場合は、かなり時間削減で作業が進められると思います。

### 品質について

最も顕著な差は**テストケースの有無**です。agents-teamなしではテストが生成されませんでしたが、agents-teamありではtesterエージェントがテストケースを作成しました。また、agents-teamなしではlocalStorageのSSR考慮漏れによるHydrationエラーが発生しましたが、agents-teamありでは同様のエラーは見られませんでした。reviewerがコードをチェックする工程が入ったことで、この種のミスが防がれた可能性があります。

### 総評

| 観点 | 結論 |
| --- | --- |
| コスト（トークン） | agents-teamありが約4倍。ただし設定次第で削減余地あり |
| 速度 | agents-teamありが約3倍の時間。並列化で改善余地あり |
| 品質 | agents-teamありが優位。テスト生成・エラー検出の面で差が出た |

シンプルなTODOアプリ程度の規模では、コスト・速度の面でagents-teamのオーバーヘッドは大きいです。一方で、**テスト自動生成やレビュー工程の組み込み**という点では、agents-teamの恩恵は明確に現れました。より大規模・複雑なタスクになるほど、この差は広がると予想されます。

---

## まとめ

今回は opencode + tmux を使い、Claude Code の Agent Teams を参考にした擬似マルチエージェント環境を自作し、TODOアプリの実装を通じてagents-teamありとなしを比較しました。

結果をまとめると：

* **トークン数**はagents-teamありが約4倍（改善余地あり）
* **所要時間**はagents-teamありが約3倍（並列化で改善余地あり）
* **品質面**では、テスト自動生成・Hydrationエラーの回避などagents-teamありが優位

「コスト・速度」vs「品質・堅牢性」のトレードオフであり、プロジェクトの規模や重要度に応じて使い分けるのが現実的な結論です。また、AGENTS.mdやエージェントのプロンプト設計を磨くことで、コスト面のデメリットはまだ改善できる余地があります。

今後は実装してみて理解できたAgents-teamを、実際の開発に組み込んで質を上げる実装ができるようにしていこうと思います。

## 成果物

agents-teamありで作成したTODOアプリは以下で公開しています。

デプロイ済みアプリ: <https://agents-team-5jyl.vercel.app/>  
GitHubリポジトリ: <https://github.com/sugityan/agents-team>

## 参考
