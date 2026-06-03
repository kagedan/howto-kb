---
id: "2026-06-03-claude-code-v21159v21161-リリース毎日changelog解説-01"
title: "Claude Code v2.1.159〜v2.1.161 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/1c20a1401487b278ecc9"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "VSCode", "qiita"]
date_published: "2026-06-03"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.159〜v2.1.161 の計 3 本を 1 本にまとめて解説します。2.1.159 は内部改善のみで、ユーザー向けの変更は 2.1.160 と 2.1.161 に集中しています。

今回の注目ポイント:

1. **シェル起動ファイルへの書き込みは確認を挟む** - `.zshenv` などへの意図しないコマンド実行を防ぐガードを追加(2.1.160)
2. **acceptEdits でもビルドツール設定は素通りさせない** - `.npmrc` や `bunfig.toml` などは書き込み前に確認(2.1.160)
3. **`claude mcp` がシークレットを端末に出さない** - `${VAR}` を非展開にし、認証ヘッダと URL 内の秘密情報を伏字化(2.1.161)
4. **並列ツール呼び出しが互いに独立** - 失敗した Bash が同じバッチの他コールを巻き込まなくなった(2.1.161)
5. **grep で見たファイルは Read なしで Edit できる** - 単一ファイルの grep が read-before-edit 判定を満たす(2.1.160)
6. **`workflow` キーワードが `ultracode` に改名** - 「workflow」という単語では起動しなくなった(2.1.160)

## 並列ツール呼び出しが1つの失敗で全滅しなくなった

:::note info
対象読者: 1ターンで複数の Bash やツールを並列実行させている人
:::

Claude Code は1ターンで複数のツールを並列に投げることがあります。テストと lint を同時に走らせる、といった場面。2.1.160 以前は、このバッチ内の Bash が1つでも失敗すると、同じバッチの他の呼び出しがまとめてキャンセルされていました。

2.1.161 は各ツールを独立させました。バッチ内の1つが落ちても、他はそのまま結果を返します。

```text
# 同一バッチで並列実行
- npm test    -> 失敗(テストが落ちた)
- git status  -> 2.1.160 以前: 巻き添えでキャンセル
              -> 2.1.161:      ちゃんと結果が返る
```

テストの失敗ログと git status を1ターンで両方拾えるので、取り直しの追加ターンが要りません。落ちた箇所を確認しながら、並列で走らせた別コマンドの結果をそのまま次の判断に使えます。

---

## grep で開いたファイルは Read を挟まず Edit できる

:::note info
対象読者: grep でアタリをつけてから直接編集する人
:::

read-before-edit のガードがゆるみました。2.1.160 から、単一ファイルに対する `grep` / `egrep` / `fgrep` は Read と同等に扱われます。

```bash
# 2.1.160 以前
grep -n "deprecated" src/api.ts   # 場所を確認
# -> Edit する前にもう一度 Read が必要だった

# 2.1.160 以降
grep -n "deprecated" src/api.ts   # これだけで Edit に進める
```

grep で行番号まで見ているのに、もう一度ファイル全体を Read させられる二度手間が消えます。ただし複数ファイルをまとめて grep した場合は対象外。あくまで単一ファイルの grep だけが判定を満たします。

---

## 設定ファイルへの書き込みにガードを追加

:::note info
対象読者: acceptEdits や自動承認でエージェントを回している人
:::

コード実行につながる設定ファイルへの書き込みに、確認プロンプトが入りました。どちらも 2.1.160。

シェル起動ファイルが対象の1つ。`.zshenv` `.zlogin` `.bash_login` や `~/.config/git/` への書き込み前に確認が入ります。これらは次回シェル起動時に実行されるので、書き換えられると意図しないコマンド実行につながる。

ビルドツール設定も対象。`acceptEdits` モードでも、`.npmrc` `.yarnrc*` `bunfig.toml` `.bazelrc` `.pre-commit-config.yaml` `.devcontainer/` といったコード実行を許す設定は、書き込み前に確認するようになりました。

acceptEdits を「全部自動でいい」と思って使っていると、ここだけは止まる。逆に言えば、この2カテゴリ以外は今まで通り素通りします。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| 2.1.161 | 可観測性 | OTEL_RESOURCE_ATTRIBUTES | 値がメトリックのラベルに付与され、team や repo など独自の軸で使用量を切り分けられる |
| 2.1.161 | UI | claude agents | ファンアウト時に done/total を詳細の前に表示。peek は最長実行中の項目を出す |
| 2.1.161 | MCP | /mcp | 一度もサインインしていない claude.ai コネクタを「Show unused connectors」行に折りたたむ |
| 2.1.161 | Linux | クリップボード | フルスクリーンで wl-copy/xclip/xsel を使用。PRIMARY セレクションにもコピーし中クリック貼り付けに対応 |
| 2.1.161 | セキュリティ | claude mcp | list/get/add が `${VAR}` を非展開にし、認証ヘッダと URL の秘密情報を伏字化 |
| 2.1.161 | パフォーマンス | レンダリング | レイアウトエンジンの JIT プロファイル安定化と、大きなファイル書き込みの描画を改善 |
| 2.1.160 | キーワード | ultracode | 動的ワークフローのトリガーを `workflow` から `ultracode` に改名。プロンプト入力で violet にハイライト |
| 2.1.160 | 環境変数 | フラグ削除 | `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE` を削除し no-op 化 |
| 2.1.160 | 起動 | JetBrains | 起動時の JetBrains プラグイン導入の案内を削除 |
| 2.1.159 | 内部 | インフラ | 内部インフラ改善のみ。ユーザー向けの変更なし |

バグ修正は数が多いので折りたたみます。

<details>

<summary>バグ修正一覧(2.1.160 / 2.1.161)</summary>

2.1.161:
- `forceLoginOrgUUID`/`forceLoginMethod` が Bedrock/Vertex/Foundry/Mantle のサードパーティセッションをブロックしていた問題(2.1.146 のリグレッション)
- バックグラウンドサブエージェントの出力が `claude -p` の stdout(`--output-format text`/`json`)を壊す問題
- `/usage-credits` が Team/Enterprise 管理者に再ログインを始めてしまう問題
- `/autofix-pr` が git worktree や別リポジトリ内で「default branch では実行できない」と誤報する問題
- `--resume` ピッカーが git worktree でないディレクトリ(jj workspaces 等)のセッションを表示しない問題
- Windows で bash を明示起動するフック(`/usr/bin/bash script.sh`)が失敗する問題
- OpenTelemetry のログイベントが初期化完了前に黙って捨てられる問題
- `isolation: "worktree"` のワークフローエージェントが自身の worktree 内のファイル編集をブロックされる問題
- バックグラウンドセッションが settings.json ではなく古いモデルで起動する問題
- セッション再開後に Write の結果描画でクラッシュしうる問題
- 完了したサブエージェントが running 表示のまま固まる問題
- `CLAUDE_CODE_TMPDIR` が深いパスのとき `$TMPDIR` 配下の Unix ソケットで `EADDRINUSE` が出る問題
- `/effort` ダイアログやワークフローアニメーションが「Reduce motion」設定を無視していた問題
- [VSCode] 文字化け対策にターミナル GPU アクセラレーション無効化を案内するヒントを追加

2.1.160:
- WSL でコピー時に Windows クリップボードへ書けない問題(OSC 52 から PowerShell interop に変更)
- `claude agents` から完了セッションを復元すると履歴が消え元のプロンプトを再実行する問題
- 夜間リタイア後に再アタッチしたバックグラウンドセッションが会話を失う問題
- `claude --bg` がデーモンのコールドスタート時に「socket missing」で失敗する問題
- Windows で背景セッション起動ディレクトリが `claude rm` 後も削除できない問題
- `claude agents` がセッション一覧に戻る際に数秒フリーズする問題
- Windows で背景セッション接続中にキー入力が無反応になる問題
- Apple Terminal/tmux に sync-output マーカーを送って描画が乱れる問題
- `claude agents` 表示で CJK IME の変換中文字が画面左下に出る問題
- `file:///C:/...` リンクが Windows で壊れたパスに書き換えられる問題
- プロジェクトディレクトリやブランチ名に非 ASCII が含まれると音声モードが接続失敗する問題
- auto モード非対応メッセージが原因を誤ってモデルのせいにする問題
- ブリーフモードのセッション再開で過去の返信がスクロールバックから消える問題
- vim モードの `p` が `v$` でヤンクした際カーソル下行に貼り付ける問題

</details>

## まとめ

2.1.160 はセキュリティガードが中心。シェル起動ファイルとビルドツール設定への書き込みで確認が増えるので、acceptEdits を自動承認で回している人ほど止まる回数が増えます。2.1.161 の並列ツール独立化は、1ターンに複数コマンドを並列実行する人が片方の失敗で全部を取りこぼさなくなる変更。`workflow` から `ultracode` への改名は、過去の手順書やスニペットを使っている場合は読み替えが要ります。
