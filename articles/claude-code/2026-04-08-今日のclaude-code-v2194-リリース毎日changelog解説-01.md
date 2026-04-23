---
id: "2026-04-08-今日のclaude-code-v2194-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.94 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/1d5e804cd3bd172b398a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

Bedrock/Vertex/Foundry・チーム・エンタープライズユーザーのデフォルト `effort` レベルが **high** に引き上げられ、Bedrock Mantle対応やセッションタイトルのフック設定など実用的な改善が加わったリリースです。

## 今回の注目ポイント

1. **デフォルト `effort` が high に格上げ** -- API・Bedrock・Vertex・Foundry・Team・Enterpriseユーザーは設定なしで高品質な応答が得られるように
2. **Amazon Bedrock powered by Mantle 対応** -- 環境変数1つで Mantle 経由の Bedrock 呼び出しが可能に
3. **`hookSpecificOutput.sessionTitle` の追加** -- `UserPromptSubmit` フックからセッション名を動的に設定できるように

---

## デフォルト effort が medium から high へ

API キー・Bedrock/Vertex/Foundry・Team・Enterprise プランで Claude Code を使っているすべての方に関係する変更です。

**何が変わったか**: これまでデフォルトで `medium` だった `effort` レベルが、対象ユーザー向けに **high** へ引き上げられました。`/effort` コマンドで任意のレベルに変更できます。

**なぜ嬉しいか**: 設定を触らなくても、より深い思考・長い応答が自動的に得られるようになります。特に複雑なコードレビューやアーキテクチャ設計など、じっくり考えてほしいタスクで効果を感じやすいはずです。

```
# セッション中にeffortを変更したい場合
/effort low    # 軽量・高速な応答
/effort medium # バランス型
/effort high   # デフォルトに戻す（今回から）
```

`effort` レベルを上げるとトークン消費量も増える傾向があります。コスト管理が気になる場合は `/effort medium` や `/effort low` で明示的に下げることもできます。

---

## Amazon Bedrock powered by Mantle に対応

社内基盤として Mantle を利用している AWS 環境で Claude Code を使いたい方向けの新機能です。

**何が変わったか**: 環境変数 `CLAUDE_CODE_USE_MANTLE=1` を設定するだけで、Mantle で動作する Amazon Bedrock 経由の呼び出しが有効になります。

**なぜ嬉しいか**: これまで Mantle ベースの Bedrock 環境では Claude Code を利用できないケースがありましたが、今回の対応で接続の選択肢が広がりました。

```
export CLAUDE_CODE_USE_MANTLE=1
claude
```

また、同時に Bedrock 上の **Sonnet 3.5 v2 の呼び出しバグ**（`us.` inference profile ID を使うべきところが正しく設定されていなかった問題）も修正されています。Bedrock で Sonnet 3.5 v2 が正常に動かなかった方はこのアップデートで解消されます。

---

## フックでセッションタイトルを動的に設定

`UserPromptSubmit` フックを使ってワークフローを自動化している方に便利な追加機能です。

**何が変わったか**: `UserPromptSubmit` フックのレスポンスに `hookSpecificOutput.sessionTitle` フィールドが追加され、フック側からセッションのタイトルを設定できるようになりました。

**なぜ嬉しいか**: セッション一覧を `--resume` で振り返るとき、タイトルが「何をしていたセッションか」を示す重要な手がかりになります。フックを使えば、最初のプロンプト内容を元にタイトルを自動生成するといった運用が可能です。

```
# フックレスポンスの例
hookSpecificOutput:
  sessionTitle: "feat: ユーザー認証APIのリファクタリング"
```

---

## その他の新機能・改善

| カテゴリ | 変更点 | 概要 |
| --- | --- | --- |
| 新機能 | Slack MCP コンパクトヘッダー | `Slacked #channel` 形式でチャンネルへのクリッカブルリンクを表示 |
| 新機能 | `keep-coding-instructions` フロントマター | プラグインの output styles で利用可能なフィールドを追加 |
| 改善 | プラグインスキルの呼び出し名 | `"skills": ["./"]` 宣言時にディレクトリ名ではなくフロントマターの `name` を使用するように変更 |
| 改善 | `--resume` の挙動改善 | 別 worktree のセッションを `cd` コマンド案内なしに直接再開できるように |
| VSCode | 冷起動の高速化 | セッション開始時のサブプロセス処理を削減 |
| VSCode | `settings.json` パースエラー警告 | ファイルのパースに失敗した際に警告バナーを表示するように |

---

バグ修正 16件（クリックで展開）

* **429レートリミット**: `Retry-After` ヘッダーが長い場合にエージェントがフリーズして見える問題を修正。エラーが即座に表示されるように
* **macOS Console ログイン**: ログインキーチェーンがロックされている、またはパスワードが同期されていない場合に「Not logged in」で無音失敗していた問題を修正。`claude doctor` でも診断・修復案内が出るように
* **プラグインスキルフック**: YAMLフロントマターに定義したフックが無視されていた問題を修正
* **`CLAUDE_PLUGIN_ROOT` 未設定時のエラー**: "No such file or directory" で失敗していたフックの問題を修正
* **`${CLAUDE_PLUGIN_ROOT}` の解決**: ローカルマーケットプレイスプラグインの起動時にインストール済みキャッシュではなくマーケットプレイスのソースディレクトリに解決されていた問題を修正
* **長時間セッションのスクロールバック**: 同じ diff が繰り返し表示されたり、空白ページが出る問題を修正
* **マルチライン入力のインデント**: トランスクリプト上で折り返し行が `❯` キャレットの下ではなくテキストの下に揃うように修正
* **Shift+Space の誤動作**: 検索入力欄で `Shift+Space` を押すと "space" という文字列が入力されていた問題を修正
* **ハイパーリンクの二重タブ**: tmux + xterm.js ベースのターミナル（VS Code、Hyper、Tabby）でリンクをクリックすると2つのタブが開く問題を修正
* **alt-screen のゴーストライン**: スクロール中にコンテンツ高さが変わったときに残像が積み重なるレンダリングバグを修正
* **`FORCE_HYPERLINK` 環境変数**: `settings.json` の `env` 経由で設定しても無視されていた問題を修正
* **ネイティブカーソルのタブ追跡**: ダイアログ内でタブ選択時にスクリーンリーダーや拡大鏡がタブ位置を追跡できなかった問題を修正
* **SDK/print モードの中断時履歴**: ストリーム中断時にアシスタントの部分レスポンスが会話履歴に保持されない問題を修正
* **CJK等マルチバイトテキストの文字化け**: stream-json の入出力でチャンクの境界が UTF-8 シーケンスを分断した際に `U+FFFD` で文字化けする問題を修正
* **[VSCode] ドロップダウンの誤選択**: マウスがリスト上にある状態でキー入力や矢印キー操作をすると間違った項目が選択される問題を修正
* **[VSCode] Bedrock Sonnet 3.5 v2**: `us.` inference profile ID を使うことで正常に呼び出せるように修正（新機能欄にも記載）

---

## まとめ

今回のアップデートは、**デフォルト `effort` の high 化**によってほぼすべての有料ユーザーが恩恵を受けるほか、プラグイン・フック周りの修正が多く、Claude Code を業務フローに組み込んでいる方には特に重要なリリースです。Bedrock ユーザーは Mantle 対応と Sonnet 3.5 v2 の修正をぜひ確認してください。まず試すべきことは `/effort` コマンドでデフォルトの挙動を確認し、コストと品質のバランスを自分のユースケースに合わせて調整することです。
