---
id: "2026-07-12-claude-code-v21207auto-mode-がクラウド3社で-opt-in-不要に毎日c-01"
title: "Claude Code v2.1.207｜Auto mode がクラウド3社で opt-in 不要に｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/0b47d4c62a52b65ea7c0"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "qiita"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

Auto mode が Bedrock・Vertex AI・Foundry で opt-in なしに解禁されました。`CLAUDE_CODE_ENABLE_AUTO_MODE` を仕込まなくても動く代わりに、設定の読み先が `.claude/settings.local.json` から `~/.claude/settings.json` へ移り、旧設定は素通りします。

## 今回の注目ポイント

1. **Auto mode がクラウド3社で opt-in 不要に** - Bedrock・Vertex AI・Foundry で `CLAUDE_CODE_ENABLE_AUTO_MODE` なしに動く。止めるなら `disableAutoMode`
2. **auto mode の設定読み先が変更** - リポジトリ内の `.claude/settings.local.json` にある `autoMode` は無視され、`~/.claude/settings.json` を見るようになった
3. **Bedrock・Vertex・AWS 版のデフォルトが Opus 4.8 に** - モデルを明示していなければ更新後に切り替わる
4. **非対話実行の同意ダイアログ素通りを修正** - `claude -p` や SDK 経由でリモート管理設定が、同意ダイアログを出さないまま「同意済み」として恒久記録されていた
5. **プラグインのシェルインジェクション対策** - shell 形式コマンド内の `${user_config.*}` が拒否されるようになった
6. **`pluginConfigs` をプロジェクト設定から読まなくなった** - 反映されるのは user 設定・`--settings`・managed 設定のみ

## Auto mode、クラウド勢は環境変数なしで動く

:::note info
対象読者: Bedrock / Vertex AI / Foundry 経由で Claude Code を動かしている人
:::

**この3プロバイダでは `CLAUDE_CODE_ENABLE_AUTO_MODE=1` が要らなくなりました。** 起動スクリプトや CI に仕込んでいた環境変数は、そのまま消せます。無効化は設定ファイルの `disableAutoMode` に一本化。

引っかかるのは設定の読み先です。auto mode は `.claude/settings.local.json` の `autoMode` を読まなくなりました。ここに書いていた分は `~/.claude/settings.json` へ移さないと効きません。リポジトリに紛れ込みやすい `.local.json` をプロジェクト上書きに使っていた場合、移設漏れがそのまま挙動差になります。

:::note warn
`.claude/settings.local.json` に `autoMode` を書いている場合、v2.1.207 以降は無視されます。`~/.claude/settings.json` へ移してください。
:::

あわせて Bedrock・Vertex・AWS 上の Claude Platform も、デフォルトが Opus 4.8 になりました。モデルを明示していないパイプラインは、更新後に走るモデルが変わります。

## 非対話実行で同意ダイアログが素通りしていた

`claude -p` や SDK からの実行で、リモート管理設定が同意ダイアログを一度も出さないまま「同意済み」として恒久記録される不具合がありました。v2.1.207 で修正済み。

managed settings をリモート配布している組織では、本来ユーザーの同意を挟むはずのセキュリティ確認が、ヘッドレス実行だと飛ばされていたことになります。CI や自動化パイプラインで `claude -p` を回すほど、同意なしに記録される管理設定が増えます。

:::note alert
非対話実行(`claude -p`・SDK)でリモート管理設定を使っている組織は、v2.1.207 へ更新してください。更新前は同意ダイアログなしで consented 状態が記録されます。
:::

## プラグイン設定の締め付け2件

```
# NG: shell 形式コマンドに ${user_config.*} を直書き → 拒否される
mytool --token "${user_config.token}"

# OK: exec 形式(args 配列)で $CLAUDE_PLUGIN_OPTION_<KEY> を渡す
["mytool", "--token", "$CLAUDE_PLUGIN_OPTION_TOKEN"]
```

shell 形式のコマンド内で `${user_config.*}` を展開する書き方が、シェルインジェクション対策として拒否されるようになりました。hooks は exec 形式(`args` 配列)か `$CLAUDE_PLUGIN_OPTION_<KEY>` を使います。monitors と headersHelper は、値をスクリプト側(設定ファイルかサーバーの `env` ブロック)で読み取ります。

もう1件、プラグインのオプション値(`pluginConfigs`)が、プロジェクト直下の `.claude/settings.json` から読まれなくなりました。反映されるのは user 設定・`--settings`・managed 設定の3経路だけです。プロジェクトに置いた値で他人のプラグイン挙動を差し替える経路が、塞がれました。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.207 | 改善 | 長い出力でのカクつき解消 | 長いリスト・表・段落・コードブロックのストリーミング中に端末が固まる、入力が遅れる問題を修正 |
| v2.1.207 | 修正 | prompt-injection の誤検知 | 良性のシステム生成メッセージで偽の警告が出ていたのを修正 |
| v2.1.207 | 修正 | 自動更新でランチャー上書き | `~/.local/bin/claude` の自作スクリプトやシンボリックリンクを毎回上書きしていた問題を修正。`/doctor` が外部管理ランチャーを報告 |
| v2.1.207 | 修正 | `cd` + `/dev/null` の許可要求 | 出力を `/dev/null` だけにリダイレクトする複合コマンドで許可を求めていたのを修正 |
| v2.1.207 | 修正 | 応答末尾のスクロール飛び | ストリーミング終了時に回答冒頭より上へ飛ぶ問題を修正 |
| v2.1.207 | 修正 | `worktreeConfig` の残留 | 最後の `worktree.sparsePaths` worktree 削除後に `.git/config` から消えず、`tea` など go-git 系ツールを壊していたのを修正 |
| v2.1.207 | 修正 | glob の角括弧崩れ | rules glob・skill パス・`.ignore`・`.worktreeinclude` の壊れた括弧パターンでファイル読み込みが失敗する問題を修正 |
| v2.1.207 | 修正 | agent teams のクラッシュループ | 壊れた mailbox メッセージで毎秒エラーが再発し続けるのを修正 |
| v2.1.207 | 修正 | Windows での無限ハング | AWS 認証解決が固まった際、60秒のストールガードが発火するように |
| v2.1.207 | 修正 | Bedrock の SSO 再取得 | API リクエストごとに IAM Identity Center へ認証情報を要求していたのを修正 |
| v2.1.207 | 修正 | `/usage-credits` の入力検証 | 不正な金額を黙って数字だけ残す挙動を廃止。$1,000 超は打ち込み確認が必須に |
| v2.1.207 | 改善 | agent view の貼り付け/停止表示 | 同一テキスト再貼り付けで `[Pasted text #N]` を展開。停止中セッションは質問を先頭に、`waiting 3m` 形式で経過を表示 |

Remote Control とバックグラウンドセッション周りも複数直っています。ネットワーク断や認証更新のあとにタスク状態が消える問題、デスクトップアプリ主催セッションの進捗がモバイルや Web に出ない問題、worktree に入ったセッションが再開時に空になる問題など。Deep research の Fetch フェーズで全エージェントが「unknown」と表示されていたのも、ホスト名チップが出るように直りました。

## まとめ

v2.1.207 で目立つのは、Bedrock・Vertex・Foundry まわりの変更です。auto mode が3社で環境変数なしに動き、設定の読み先とデフォルトモデルが同時に変わりました。非対話実行の同意素通りとプラグインのシェルインジェクション、2つのセキュリティ修正も入っています。CI や SDK で `claude -p` を回している環境は、更新の優先度が高いです。
