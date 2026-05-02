---
id: "2026-05-02-claude-code-v21126-リリース毎日changelog解説-01"
title: "Claude Code v2.1.126 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/e3ddb3764b70912ae6c5"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "VSCode"]
date_published: "2026-05-02"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

2026年5月1日にリリースされた v2.1.126 は、新コマンド `claude project purge` とゲートウェイ経由のモデル選択対応が中心。Windows の日本語文字化け修正も静かに入っています。

## 今回の注目ポイント

1. **`claude project purge` で状態を一括削除**: プロジェクト単位で transcripts や設定をまとめて消せる新サブコマンド
2. **`/model` がゲートウェイの `/v1/models` を読む**: `ANTHROPIC_BASE_URL` 経由のプロキシでも実モデル一覧を動的取得
3. **`--dangerously-skip-permissions` の保護対象が縮小**: `.claude/` `.git/` `.vscode/` への書き込みが素通りに
4. **OAuth コードをターミナルへ貼り付けてログイン**: WSL2/SSH/コンテナで詰まっていた認証経路を補完
5. **管理ドメイン許可リストが無視される脆弱性を修正**: `allowManagedDomainsOnly` の効き目が戻る
6. **Windows no-flicker モードの日本語文字化けを修正**: 日本語環境ユーザーに直接効く

---

## `claude project purge` で痕跡をまるごと消す

:::note info
**対象読者**: ローカルに大量のプロジェクト履歴を抱えていて、不要な状態を整理したい人
:::

`~/.claude/projects/` 配下に溜まる transcripts、file history、tasks、設定エントリを、ひとまとめに削除できる新サブコマンドが追加されました。

```bash
# カレントディレクトリのプロジェクト状態を確認だけ
claude project purge --dry-run

# 対話モードで残すかどうか選びつつ削除
claude project purge -i

# 全プロジェクト分まとめて削除（CIから流すとき）
claude project purge --all -y
```

`--dry-run` で消える対象を一覧化、`-y/--yes` で確認なしの強制削除、`-i/--interactive` で対象選択、`--all` で全プロジェクト。これまで `~/.claude/projects/<エンコードされたパス>/` を手で `rm -rf` していた運用が、安全マージン付きの正規コマンドに置き換わります。dotfiles リポにこの呼び出しを書いておけば、新マシンへの移行もクリーンに。

---

## `/model` がゲートウェイのモデル一覧を取りに行く

:::note info
**対象読者**: LiteLLM や Anthropic 互換ゲートウェイを `ANTHROPIC_BASE_URL` で挟んで Claude Code を運用しているチーム
:::

`/v1/models` を返す Anthropic 互換ゲートウェイを `ANTHROPIC_BASE_URL` に向けている場合、`/model` ピッカーがそのエンドポイントを叩いて選択肢を組み立てます。固定リストではなくゲートウェイ側が公開しているモデルがそのまま並ぶ形。

```bash
export ANTHROPIC_BASE_URL=https://my-litellm.example.com
claude
# /model を開くと、my-litellm が公開している model 名が並ぶ
```

社内ゲートウェイで Bedrock 経由 Claude や別プロバイダのモデルを混ぜてホストしているなら、Claude Code 側のリリースを待たずに新しいモデルが選べるようになります。逆にゲートウェイの `/v1/models` が壊れていると `/model` も壊れるので、運用前に curl で叩いて返答を確認しておくと安心。

---

## `--dangerously-skip-permissions` の許可範囲が広がった

:::note info
**対象読者**: CI や Docker 内で `--dangerously-skip-permissions` を常用している人、またはローカルでエイリアスにしている人
:::

v2.1.126 から、`--dangerously-skip-permissions` を付けても確認プロンプトが残っていた `.claude/` `.git/` `.vscode/`、シェル設定ファイル（`.bashrc` `.zshrc` 系）への書き込みもバイパス対象に入りました。

引き換えに、コンテナの外で本フラグを使う際の事故リスクは確実に増えます。たとえば Claude が `.zshrc` に `eval` 行を仕込むケースや、リポジトリ直下の `.git/hooks/pre-commit` を書き換えるケースが、無確認で通る、ということ。`rm -rf /` のような破滅的削除コマンドだけは引き続きセーフティネットでプロンプトが出ますが、ファイル書き込みについては実質ノーガードです。

運用は使い捨て Docker やサンドボックス VM に閉じるのが前提。ローカルマシンに `--dangerously-skip-permissions` のシェルエイリアスを置いていたなら、この機会に外しておきたいところ。

## その他の変更

| カテゴリ | 変更点 | 概要 |
|---|---|---|
| 認証 | OAuth コードのターミナル貼り付け対応 | WSL2/SSH/コンテナでブラウザコールバックが localhost に届かないとき、画面に表示されたコードを手入力できる |
| Telemetry | `claude_code.skill_activated` に `invocation_trigger` 属性 | `user-slash` / `claude-proactive` / `nested-skill` でスキル発火経路を判別可能 |
| Telemetry | Host-managed デプロイの analytics 自動無効化を撤廃 | `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` 配下の Bedrock/Vertex/Foundry でも有効化される |
| UI | Auto mode のスピナーが赤くなる | 権限チェック待ちのときに、ツール実行中と区別がつくよう色分け |
| Windows | PowerShell 7 の検出経路を拡張 | Microsoft Store 版・PATH なし MSI・.NET global tool もOK |
| Windows | PowerShell tool 有効時は PowerShell が一次シェル | Bash 優先からの転換 |
| Read tool | malware-assessment リマインダーを削除 | 旧モデルが「これはマルウェアではない」と過剰コメントするのを抑制 |
| Security | `allowManagedDomainsOnly` / `allowManagedReadPathsOnly` の無視を修正 | 上位 managed-settings に `sandbox` ブロックがないと無視される問題を解消 |

### バグ修正

<details>
<summary>v2.1.126 で修正されたバグ一覧</summary>

- 2000px 超の画像貼り付けでセッションが壊れる問題（自動縮小と履歴からの除去で対応）
- `OAuth not allowed for organization` で login 画面に飛ばす挙動を、管理者連絡を促すメッセージに変更
- 低速・プロキシ越し・IPv6-only devcontainer での OAuth login タイムアウト
- 同時 credential 書き込みで有効な refresh token がクリアされる稀なレース
- API リトライのカウントダウンが `0s` で固まる
- Mac スリープ復帰直後のリクエストで `Stream idle timeout` が出る
- バックグラウンド/リモートセッションでの長い思考中の `Stream idle timeout` 誤検知
- 空ターン連発のあと、思考は終わっているのに出力が出ないハング
- Cursor / VS Code 1.92〜1.104 のターミナルでトラックパッドスクロールが速すぎる
- claude.ai MCP connectors が、needs-auth 状態の手動サーバに抑制される
- Windows no-flicker モードで日本語/韓国語/中国語が文字化け
- `Ctrl+L` でプロンプト入力が消える（readline 同様、画面再描画のみに）
- `context: fork` のスキルや一部 subagent で初回ターンに WebSearch/WebFetch が使えない
- `--channels` 起動時の対話セッションで plan-mode ツールが使えない
- `/plugin` Uninstall が結果に `Enabled` と表示
- linter が大量のファイルに触れたときの file-modified リマインダーをサイズで打ち切り
- `/remote-control` リトライ表示が `connecting…` のまま固まる
- Remote Control 初回接続失敗時にエラー理由が出ない
- Windows: clipboard write を EDR/SIEM テレメトリから隠蔽し、22KB 超選択もコピー可能に
- PowerShell tool で `git diff -- file` の `--` が `--%`（停止トークン）と誤認される
- Agent SDK が並列ツール呼び出し中に malformed なツール名でハングする

</details>

## まとめ

`claude project purge` で日常運用がだいぶ楽になり、ゲートウェイ派には `/model` の動的解決が刺さります。`--dangerously-skip-permissions` の保護範囲縮小は逆方向の変更なので、ローカル常用していた人は一度設定の棚卸しを。
