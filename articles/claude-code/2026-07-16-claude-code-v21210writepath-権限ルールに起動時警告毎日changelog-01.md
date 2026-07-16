---
id: "2026-07-16-claude-code-v21210writepath-権限ルールに起動時警告毎日changelog-01"
title: "Claude Code v2.1.210｜Write(path) 権限ルールに起動時警告｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/2b9faf5b4ab771d4496a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "qiita"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

`Write(path)` 形式の権限ルールを settings.json に書いていると、v2.1.210 から起動時に警告が出ます。案内される置き換え先は `Edit(path)` と `Read(path)`。permission を細かく書き込んでいる設定ほど、影響を受けます。

## 今回の注目ポイント

1. **Write(path) 系の権限ルールに起動時警告** — `Write(path)` / `NotebookEdit(path)` / `Glob(path)` は `Edit(path)` / `Read(path)` へ寄せる案内 (v2.1.210)
2. **worktree 分離のサブエージェントがメインリポジトリを触れていた** — git を変更するコマンドが自分の worktree の外に届いていた (v2.1.210)
3. **ultracode の opt-in が webhook でも成立していた** — 人間由来でない入力でキーワードが発火 (v2.1.210)
4. **フックのタイムアウトがユーザー拒否として報告されていた** — 無人セッションが止まって待つ原因 (v2.1.210)
5. **折りたたみツール行に経過時間カウンタ** — 長時間のツール呼び出しが停止して見える問題への対処 (v2.1.210)
6. **auto モードの権限分類器が外部セッションで Sonnet 5 既定に** — セッション最初のリクエストで検証し、以降は固定 (v2.1.210)

## Write(path) と NotebookEdit(path) と Glob(path) が警告対象になった

:::note info
対象読者: settings.json の `permissions` に、ツール名 + パスの形でルールを書き込んでいる人
:::

**`Edit(path)` と `Read(path)` に寄せろ、というのが警告の中身です。** 代替は changelog が名指し。

> Added a startup warning for `Write(path)`, `NotebookEdit(path)`, and `Glob(path)` permission rules — use `Edit(path)` or `Read(path)` instead

書き換えの方向はシンプルで、ファイルを書く系は `Edit(path)` へ、ファイルを読む・探す系は `Read(path)` へ寄せます。

```json
{
  "permissions": {
    "allow": [
      "Write(src/**)",
      "NotebookEdit(notebooks/**)",
      "Glob(src/**)"
    ]
  }
}
```

これを次の形へ。`Write` と `NotebookEdit` は `Edit` に、`Glob` は `Read` に寄ります。

```json
{
  "permissions": {
    "allow": [
      "Edit(src/**)",
      "Edit(notebooks/**)",
      "Read(src/**)"
    ]
  }
}
```

:::note warn
settings.json をチームで共有しているなら、全員の起動時に同じ警告が出ます。書き換えは早いほうが手戻りが少ない。置き換えた後は、意図した範囲で許可と拒否が効いているかを一度確認してください。
:::

## worktree 分離のサブエージェントが、自分の worktree の外に git を打てていた

`isolation: 'worktree'` を指定したサブエージェントが、git を変更するコマンドをメインリポジトリのチェックアウトに対して実行できていました。分離のために worktree を切っているのに、その分離を跨いで元のリポジトリを触れる状態。v2.1.210 で修正され、git 操作は自分の worktree に閉じます。

worktree を切る目的そのものが、並列実行でファイルを衝突させないこと。その前提が破れていました。同じ回で、停止したバックグラウンドセッションが `git worktree lock` を残したままになる件も直っています。所有プロセスが消えたロックは、定期スイープが解放するようになりました。

## ultracode が webhook 経由の入力でも発火していた

`ultracode` のキーワード opt-in が、webhook のペイロードや中継された PR コメントのような、人間が打っていない入力でも成立していました。中継された PR コメントの本文に `ultracode` と書いてあるだけで、opt-in が通る経路。

同じ方向の変更として、Agent ツールがサブエージェントの読んだ内容を経由する間接プロンプトインジェクションに対して強化されています。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.210 | UI | 経過時間カウンタ | 折りたたまれたツール要約行で時間が刻まれ、長時間の呼び出しが停止して見えなくなる |
| v2.1.210 | フック | タイムアウトの誤報告を修正 | コールバックのタイムアウトがユーザー拒否としてモデルに伝わり、無人セッションが待ち状態に入っていた |
| v2.1.210 | Bash | 自動バックグラウンド化の通知を改善 | タイムアウトで自動的に background へ回した場合と、明示的な background 指定を、モデルが区別できる |
| v2.1.210 | Bash | `cd` の扱いを修正 | コマンドが background へ回された後、`cd` が効いたとモデルが誤認していた。作業ディレクトリが変わらない旨をツール結果に明記 |
| v2.1.210 | auto モード | 権限分類器の既定を Sonnet 5 に | 外部セッション向け。最初のリクエストで検証し、そのセッション中は固定 |
| v2.1.210 | プラン | 承認ラベルの誤りを修正 | 編集なしの承認が「(edited by user)」と表示され、古いスナップショットでプランファイルを上書きしていた |
| v2.1.210 | スキル | `$1` / `$2` の消失を修正 | 未対応の位置プレースホルダが黙って削除されていた。今後はそのまま保持 |
| v2.1.210 | MCP | プラグイン提供サーバの巻き添え停止を修正 | セッション途中の MCP 再同期で、プラグイン由来のサーバが落とされていた |
| v2.1.210 | MCP | SDK サーバの接続開始を修正 | `initialize` 制御リクエスト経由で登録したサーバが、次のターンまで接続を待っていた |
| v2.1.210 | CLI | `claude attach` の失敗を修正 | セッション遷移中の「job not found」「agent is still starting」。デーモンの安定を待ち、遅延中のリサイズも完了後に適用 |
| v2.1.210 | エージェント | `--effort ultracode` の消失を修正 | `claude agents --effort ultracode` の値が dispatch 先セッションに届かず、黙って捨てられていた |
| v2.1.210 | Grep | ページング末尾の誤表示を修正 | content モードで結果の終端を越えると「No matches found」と返していた |
| v2.1.210 | メモリ | 無言の切り詰めを廃止 | MEMORY.md が読み取り上限を超える書き込みは、明示的なエラーになる |
| v2.1.210 | サンドボックス | 遅延シンボリックリンクの取り込み | 後から現れた `.claude/*` のシンボリックリンクが deny-write リストに反映されていなかった |
| v2.1.210 | 安定性 | 各種クラッシュ修正 | bigint やプレーンテキストを返すツール結果レンダラ、スタイル付きテキスト外のコンテンツ、バックグラウンドワーカーの接続リセット時のクラッシュループ |
| v2.1.210 | エディタ | ペーストマーカーの漏れを修正 | 外部エディタで貼り付けテキストの前後に È / É が混入していた |
| v2.1.210 | エージェント表示 | ビュー往復の不具合を修正 | ← で agents ビューを開くとタスクトラッカーが消える、`CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` でゴーストフレームが重なる、削除済みセッションの下書き画像が残る |
| v2.1.210 | アクセシビリティ | スクリーンリーダー対応 | Shift+Tab の権限モード切り替えを読み上げる |
| v2.1.210 | dataviz | 色検証の精度向上 | 知覚的な OKLab 色差と、再調整した色覚多様性のしきい値を採用 |
| v2.1.210 | Fable | advisor で一時的に選択不可 | Fable advisor の失敗を引き起こすサーバ側の問題を修正するまでの措置 |

## まとめ

v2.1.210 は、起動時の警告が 1 件増えただけの回に見えて、settings.json の書き方そのものに踏み込んでいます。`Write(path)` を書いていたなら、そこは書き換え対象ということ。worktree 分離と `ultracode` の修正も、自動化を回している環境ほど効きます。
