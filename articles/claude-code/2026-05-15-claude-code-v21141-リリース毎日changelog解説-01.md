---
id: "2026-05-15-claude-code-v21141-リリース毎日changelog解説-01"
title: "Claude Code v2.1.141 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/991c2556a7f9fe035d06"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "VSCode"]
date_published: "2026-05-15"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.141 は hook の `terminalSequence`、Rewind の `Summarize up to here`、`/feedback` の過去セッション同梱が並んだリリース。バグ修正は 40 件超。

### 今回の注目ポイント

1. **hook の `terminalSequence` で通知/ベル/ウィンドウタイトル**: controlling terminal が無くても desktop 通知が出せる
2. **`CLAUDE_CODE_PLUGIN_PREFER_HTTPS` で plugin を HTTPS clone**: GitHub の SSH 鍵が無い環境でも plugin を導入できる
3. **`/feedback` に過去 24 時間 / 7 日のセッション同梱**: 1 セッションに収まらない不具合をまとめて報告できる
4. **Rewind の「Summarize up to here」**: 直近ターンを残しつつ過去だけ要約で圧縮できる
5. **Spinner が 10 秒で amber に変色**: 長考に入ったか固まったかが色で判別できる
6. **`ANTHROPIC_WORKSPACE_ID` で workload identity federation token のスコープ指定**: federation rule が複数 workspace を覆う場合の絞り込み用

## hook で desktop 通知・ベル・ウィンドウタイトルを出せるようになった

:::note info
対象: hook で長時間ジョブの完了を知らせたい人、IDE/ターミナル外で Claude Code を動かしている人
:::

hook の JSON 出力に `terminalSequence` フィールドが追加されました。これに ANSI エスケープシーケンスを入れると、Claude Code が controlling terminal を持たないケースでも desktop 通知やベル音、ウィンドウタイトル変更を発火させられる。

例えば PostToolUse hook で「タスク完了をベルで鳴らす」だけならこう書ける。

```json
{
  "terminalSequence": "\u0007"
}
```

ウィンドウタイトルを書き換えたいなら OSC 0:

```json
{
  "terminalSequence": "\u001b]0;Claude: build finished\u0007"
}
```

今までは hook 側で `printf` などで TTY に直接書き込む必要があり、SDK・headless・background agent のように controlling terminal が無い実行モードでは無視されていた。`terminalSequence` 経由なら Claude Code 本体が代わりに親ターミナルへ送ってくれるので、起動経路に依存しなくなる。(v2.1.141 で追加)

---

## Rewind に「Summarize up to here」が追加された

:::note info
対象: 長いセッションでコンテキストが膨らみがちな人、autocompact 任せでは粒度が荒いと感じている人
:::

Rewind menu (`Esc Esc`) のオプションに `Summarize up to here` が増えました。選んだ位置までの過去を要約に置き換え、それより新しいターンはそのまま残す挙動。autocompact が全体をまとめてしまうのに対し、こちらは「ここから先の文脈は壊したくない」という意図を持って手動で圧縮できる。

調査フェーズが長く続いた後で実装フェーズへ移る時に、調査ログだけ要約へ畳み、直近で固めた仕様や設計判断は原文で残す、という切り分けに向く。(v2.1.141 で追加)

---

## `/feedback` に過去 24 時間 / 7 日のセッションを同梱できる

:::note info
対象: Claude Code に不具合を報告したい人、再現が複数セッションを跨ぐ事象を踏んだ人
:::

`/feedback` 起動時に、現在のセッションだけでなく直近 24 時間または 7 日分のセッションを bundle に含められるようになった。

これまでは `/feedback` がアクティブな 1 セッションのトランスクリプトしか送らず、「昨日のセッションで起きた挙動が今日のセッションで再現せず原因が掴めない」というケースで切り分けが難しかった。範囲を 24 時間 / 7 日に広げれば、横断的なバグ(MCP の認証ループ、permission mode の引き継ぎ、background agent の状態保持など)を一通り回収できる。

なお bundle 内の redaction も同時に改善されており、セッション ID のような引用符付き値が JSON として valid な形で出るようになった(これも v2.1.141)。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.141 | 新機能 | `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` | GitHub の plugin を SSH ではなく HTTPS で clone |
| v2.1.141 | 新機能 | `ANTHROPIC_WORKSPACE_ID` | workload identity federation の token を特定 workspace にスコープ |
| v2.1.141 | 新機能 | `claude agents --cwd <path>` | session 一覧を指定ディレクトリ配下に絞る |
| v2.1.141 | 改善 | Auto mode permission dialog | `permissions.ask` ルールが原因のとき理由を併記 |
| v2.1.141 | 改善 | file-edit permission の IDE diff | IDE 接続時に「view diff in your IDE」が復活 |
| v2.1.141 | 改善 | Background agents の permission mode 保持 | `/bg` や `←←` 経由でも default にリセットされない |
| v2.1.141 | 改善 | `claude agents` の Completed 判定 | 作業完了済みで background shell だけ残るエージェントを Completed 扱い |
| v2.1.141 | 改善 | Spinner amber 化 | 10 秒経過で警告色になり、長考か停止かを目視判別 |
| v2.1.141 | 改善 | Plugin menu navigation | `→`/Tab でタブ切替、fullscreen でタブヘッダ・検索ボックスがクリック可 |

<details><summary>バグ修正一覧 (v2.1.141)</summary>

- Bedrock/Vertex/Foundry/gateway で `ANTHROPIC_SMALL_FAST_MODEL` 未設定時に background side-query が存在しない Haiku ID を投げていた問題を main-loop model にフォールバックして修正
- Windows で `claude daemon status` / `/doctor` が daemon pipe key file をロック/読めない時に opaque な失敗で落ちていた問題を、エラー内容表示に変更
- ラッパー経由で flag が付与されると `claude agents` が dashboard ではなく agent-type 一覧を出していた問題を修正
- `claude agents` で crash したセッションを開く際、working directory が削除済みだと重複 dispatch していた問題を修正
- カスタム `ANTHROPIC_BASE_URL` gateway 下で background job が auto-name されない問題を main model 利用に切り替えて修正
- 1 セッションで `/model` を切り替えると並行セッションの autocompact 閾値が無音で変わっていた問題を修正
- tool-permission prompt 表示中に permission mode を変えて新設定で許可された場合に prompt が自動で閉じない問題を修正
- permission/dialog prompt 表示中に Enter を押すと input box にも送信されてしまう問題を修正
- `EnterWorktree` で working directory が切り替わった後の hook が存在しない `transcript_path` を受け取る問題を修正
- セル折返しのある markdown table が縦並び key-value に fallback していた問題を修正 (v2.1.136 のリグレッション)
- Up-arrow 履歴: 自動復元されたキャンセル済みプロンプトが履歴から消える問題、応答前にキャンセルされたプロンプトが履歴から落ちる問題を修正
- vim INSERT/VISUAL モード中に Ctrl+C が turn を中断しない問題を修正
- `enter` を `chat:newline` に rebind したとき `meta+enter` / `ctrl+enter` 等の `chat:submit` キーバインドが効かない問題を修正
- output style 設定時に prompt suggestions が無音で無効化される問題を修正
- `spinnerVerbs` 設定が turn 完了メッセージで反映されない問題を修正
- AskUserQuestion ポップアップが直前のチャット最終行を覆い隠す問題を修正
- Web Search のエラー時ステータスが「Did 0 searches」になっていた問題を修正
- multi-line statusline が端末幅を超える行を含むと行が欠落/破損する問題を修正
- light-ansi テーマで diff 文脈行が白(不可視)になっていた問題を黒に修正
- error overlay が minified バンドルのソースを吐いて元エラーが埋もれる問題を修正
- フィードバック評価の数字を打った直後の Enter が rating 送信ではなくチャット送信になる問題を修正
- agent panel で選択中のサブエージェントに `x` を打つと prompt 側に文字が入っていた問題を修正
- ユーザー最初のプロンプト前に plugin monitor 通知からセッションタイトルが派生していた問題を修正
- 「Allowed by PermissionRequest hook」が collapsed read/search 群で tool 呼び出しごとに重複表示される問題を修正
- `/tui` が稼働中の background shell / subagent を無音で落としていた問題を、終了待ちを促すよう修正
- Bedrock / Vertex / Foundry など third-party provider のセッションで welcome banner が「API Usage Billing」と表示される問題をプロバイダ名表示に修正
- 短い端末の fullscreen で `/mcp` server 一覧がフォーカス中サーバを表示外に押し出す問題を修正
- `/feedback` バンドルの redaction が session ID 等の引用符付き値で invalid JSON を出していた問題を修正
- desktop / third-party provider セッションが host managed-settings の `apiKeyHelper` / `ANTHROPIC_AUTH_TOKEN` を継承してしまう問題を修正
- logger 初期化前の analytics イベントが silently drop される問題を修正
- `claude plugin install` で marketplace の `ref` が upstream で消えていて `sha` がピン止めされている場合に失敗する問題を修正
- `.mcp.json` で MCP サーバを宣言している plugin の details pane が 0 件表示になる問題を修正
- plugin MCP サーバの config 変数未設定時に generic な接続失敗を出していた問題を「config issue」+ ヒント表示に修正、また malformed な `.mcp.json` エントリが他の MCP サーバを巻き込んで落とさないよう修正
- MCP サーバ config の POSIX shell パラメータ展開 (`${var%pattern}` 等) が env 変数未設定と誤検知される問題を修正
- MCP HTTP/SSE サーバが接続で 403 を返したとき「failed」ではなく「needs auth」と表示するよう修正
- リモート MCP サーバが optional な server-events stream の再接続失敗で本体まで切断していた問題を修正 (tool 呼び出しは POST 経由で継続)
- worker session token が途中でローテートされた際に Remote Control MCP コネクタが全て 401 になる問題を修正
- Remote Control が stale token 拒否時に trusted device を `/login` ループせず自動 re-enroll するよう修正
- SDK / headless で beta tracing 有効時に初期 OTel span が silently drop される race を修正
- `voice:pushToTalk` のカスタムキーバインドと `"space": null` 解除が無視されていた問題を修正
- Windows の Alt+V 画像ペーストでスクリーンショットが「no image found」になる問題を修正
- glibc / musl 両方の platform package がある Linux で SDK が「native binary not found」になる問題を修正
- Bedrock: `awsCredentialExport` が ambient AWS credentials 解決時にスキップされていた問題を常時実行に修正 (cross-account access の認証)
- [VSCode] in-chat mic が無音入力時に何も出さない問題を「No audio detected」表示に修正
- [VSCode] voice mode の WSL エラーが WSLg 利用者向けに `sox libsox-fmt-pulse` インストールを案内するよう修正
- `claude agents`: 起動時に pre-warmed background worker が unhealthy だとセッションが落ちる問題を fresh launch にフォールバックして修正
- `claude agents`: REPL を background 化した直後に残る空のプレースホルダーセッションを非表示化、`←` 経由で他にエージェントが無い場合に onboarding 文言を出すよう修正
- `←` で残った空の idle background セッションを daemon が 5 分後に自動撤収するよう修正

</details>

## まとめ

v2.1.141 は hook の通知経路、Rewind の部分要約、`/feedback` の範囲拡張と、長時間・複数セッションを跨ぐユースケースの取りこぼしを埋める変更が中心。autocompact が全体を一括で要約に置き換えるのに対し、Rewind の `Summarize up to here` は残したいターンを指定して圧縮できる、という違いを押さえて使い分けると効く。
