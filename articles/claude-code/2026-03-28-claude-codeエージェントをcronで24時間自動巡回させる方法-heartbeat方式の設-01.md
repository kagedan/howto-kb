---
id: "2026-03-28-claude-codeエージェントをcronで24時間自動巡回させる方法-heartbeat方式の設-01"
title: "Claude Codeエージェントをcronで24時間自動巡回させる方法 — heartbeat方式の設計と実装"
url: "https://qiita.com/sentinel_dev/items/160645f49166a7f4cdb7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

## この記事で得られること

* cronとheartbeat方式でAIエージェントを24時間自動巡回させる方法がわかる
* 自動巡回の設計パターンと実装をコピペで動かせる
* 運用時のハマりポイントと監視方法を事前に知れる

**対象読者**: AIエージェントを自動運用したい方 / cronジョブでの定期実行に興味がある方

---

## はじめに — 手動起動の限界

自律AIエージェントを作っても、**起動するのが人間なら、それは自律ではない。**

私は[Claude Code + MAXプランで自律AIエージェント「Sentinel」を自作](https://qiita.com/sentinel_dev/items/e2dd94ec7def5c09c7cb)し、[トークンコストを95%削減](https://qiita.com/sentinel_dev/items/04b6cfed0dabc194cec4)し、[サブエージェントに並列でタスクを委任](https://qiita.com/sentinel_dev/items/fc586285da1de335d8d9)できるようにした。[MEMORY.md](https://qiita.com/sentinel_dev/items/5a24456c8ac3b44a8d75)で記憶を持ち、[SOUL.md](https://qiita.com/sentinel_dev/items/a3d296298d16f921227e)で行動規範を定義した。

エージェントとしては十分に賢い。ただ、毎朝ターミナルを開いて`claude -p "..."`を手動で叩かないと何も始まらない。出先で忘れたらその日のタスクは放置される。

この記事では、cronとpm2を使ってClaude Codeエージェントを**24時間自動巡回**させる方法を解説する。

## heartbeat方式とは

サーバー監視の世界では、定期的に生存確認を送る仕組みを\*\*heartbeat（心拍）\*\*と呼ぶ。同じ発想をAIエージェントに適用する。

30分ごとにエージェントを起動し、3つのことだけをやらせる:

1. **MEMORY.mdとTASKS.mdを読む** — 今の状態を把握する
2. **何をすべきか考える** — Claude APIで分析する
3. **提案をinboxに書く** — 実行はしない

**ポイントは「提案だけ」という制約。** heartbeatは偵察部隊であって、実行部隊ではない。勝手にファイルを書き換えたり投稿したりしない。`inbox/`ディレクトリに提案ファイルを置くだけ。

実行は別のプロセス（`run.sh`やsentinel.js）が担う。この分離が重要だ。heartbeatが暴走しても、提案ファイルが溜まるだけでシステムに副作用がない。

```
heartbeat.sh（偵察）→ inbox/ に提案を書く
run.sh（実行）      → TASKS.md を見てタスクを消化する
```

### なぜ常駐ではなくcron方式か

Claude Codeを常駐させるとリソースを占有し続ける。heartbeat方式なら**30分ごとに数秒だけ動いて消える**。必要なときだけ起動するイベント駆動に近い設計で、MAXプランの制限内でも安定して運用できる。

## heartbeat.shの実装（コアロジック）

実際に運用しているスクリプトのコアロジックを示す。

```
#!/bin/bash
# heartbeat.sh — 30分ごとにcronから呼ばれる定期巡回スクリプト
# 状態を確認し、提案をinboxに書いて終了する

AGENT_DIR="$HOME/agent"
INBOX_DIR="$AGENT_DIR/inbox"
CONFIG_DIR="$AGENT_DIR/config"

mkdir -p "$INBOX_DIR"

# 現在時刻
TIMESTAMP=$(date +"%Y-%m-%d_%H%M")
OUTFILE="$INBOX_DIR/heartbeat_${TIMESTAMP}.md"

# ファイル読み込み
MEMORY=$(cat "$AGENT_DIR/MEMORY.md" 2>/dev/null || echo "(なし)")
TASKS=$(cat "$AGENT_DIR/TASKS.md" 2>/dev/null || echo "(なし)")
TEMPLATE=$(cat "$CONFIG_DIR/heartbeat_prompt.md" 2>/dev/null)

if [ -z "$TEMPLATE" ]; then
  echo "[heartbeat] テンプレートが見つかりません" >&2
  exit 1
fi

# テンプレートの変数を置換
PROMPT="${TEMPLATE//\$\{MEMORY\}/$MEMORY}"
PROMPT="${PROMPT//\$\{TASKS\}/$TASKS}"

# claude -p で実行（使い捨て）
echo "[heartbeat] $TIMESTAMP 実行開始"

CLAUDE_PATH=$(which claude 2>/dev/null || echo "$HOME/.local/bin/claude")

RESULT=$("$CLAUDE_PATH" -p \
  --dangerously-skip-permissions \
  --output-format text \
  <<< "$PROMPT" 2>/dev/null)

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ] && [ -n "$RESULT" ]; then
  {
    echo "## Heartbeat $TIMESTAMP"
    echo ""
    echo "$RESULT"
  } > "$OUTFILE"
  echo "[heartbeat] 完了 → $OUTFILE"
else
  echo "[heartbeat] 失敗 (exit: $EXIT_CODE)" >&2
fi
```

### 設計判断のポイント

**`claude -p`（使い捨てモード）を使う。** 会話履歴を持たず、プロンプトを受け取って結果を返して終了する。heartbeatに前回の文脈は不要。毎回MEMORY.mdとTASKS.mdから「今」を読めばいい。

**inboxパターン。** 出力先を`inbox/heartbeat_2026-03-28_1430.md`のようにタイムスタンプ付きファイルにする。上書きされない、時系列で追える、別プロセスが拾える。シンプルなファイルベースのメッセージキューだ。

**`--dangerously-skip-permissions`。** 自動実行では確認プロンプトに応答できないのでパーミッションチェックをスキップする。名前は怖いが、heartbeatは「提案をファイルに書く」しかしない設計なのでリスクは限定的。

> プロンプトテンプレートの設計詳細（何を見て、何を提案させるか）、run.shとの連携方式、pm2の具体設定など、全体の実装はnote第5回で詳しく解説しています。

## pm2での常駐化の基本

[pm2](https://pm2.keymetrics.io/)はNode.jsのプロセスマネージャだが、シェルスクリプトの定期実行管理にも使える。

```
# pm2でheartbeatを30分間隔で実行
pm2 start heartbeat.sh --name heartbeat --cron-restart="*/30 * * * *" --no-autorestart
```

* `--cron-restart="*/30 * * * *"` — 30分ごとに再実行
* `--no-autorestart` — スクリプト終了後に自動再起動しない（cronで再起動する）

pm2の利点:

* プロセスが落ちたら自動再起動
* `pm2 logs heartbeat` でログを一括確認
* `pm2 list` で全プロセスの状態を一覧表示
* `pm2 save && pm2 startup` でOS起動時に自動復帰

```
$ pm2 list
┌─────────────┬────┬─────────┬──────────┐
│ name        │ id │ mode    │ status   │
├─────────────┼────┼─────────┼──────────┤
│ heartbeat   │ 0  │ fork    │ online   │
└─────────────┴────┴─────────┴──────────┘
```

## 実運用のトラブルシューティング

### 1. PATHが通らない

cronやpm2から起動すると、対話シェルとは環境変数が異なる。`claude`コマンドが見つからないことがある。

```
# 対策: フルパスを明示的に解決する
CLAUDE_PATH=$(which claude 2>/dev/null || echo "$HOME/.local/bin/claude")
```

スクリプト冒頭で`source ~/.bashrc`を入れる手もあるが、副作用が読みにくいのでフルパス指定の方が安全。

### 2. 同時実行の衝突

heartbeat.shの実行が30分以上かかると、次のcronが前の実行と重なる。対策としてロックファイルを使う。

```
LOCKFILE="/tmp/heartbeat.lock"
if [ -f "$LOCKFILE" ]; then
  echo "[heartbeat] 前回の実行がまだ終わっていません。スキップします。" >&2
  exit 0
fi
trap "rm -f $LOCKFILE" EXIT
touch "$LOCKFILE"
```

### 3. Windows環境でのcron

WindowsにはネイティブのcronがないためGit Bash + pm2の組み合わせで解決する。WSL2を使う手もあるが、ファイルシステムの越境でパフォーマンスが落ちるケースがある。

```
# Windows（Git Bash）でpm2を使う場合
pm2 start bash -- -c "/path/to/heartbeat.sh"
```

> 各トラブルの詳細な対処法や、実際に踏んだ地雷の全リストはnote第5回にまとめています。

## まとめ

| 要素 | 役割 |
| --- | --- |
| heartbeat.sh | 30分ごとに状態チェック→提案生成 |
| inbox/ | 提案をファイルとして蓄積（メッセージキュー） |
| run.sh | TASKS.mdを見てタスクを実行 |
| pm2 | プロセスの常駐化・自動再起動・ログ管理 |

heartbeat方式の核心は\*\*「偵察と実行の分離」\*\*。定期巡回で状態を監視し提案を生成するプロセスと、実際にタスクを実行するプロセスを分けることで、安全に24時間稼働できる。

これで「エージェントを起動する」という最後の手動ポイントが消える。MEMORY.mdで記憶し、SOUL.mdで判断し、heartbeatで巡回し、run.shで実行する。人間が寝ている間も、AIエージェントは動き続ける。

## さらに詳しく知りたい方へ

本記事はheartbeat方式の概要とコアロジックを紹介しました。以下の内容はnote第5回で詳しく解説しています:

* heartbeatプロンプトの設計思想（何を見て、何を提案させるか）
* run.shの実装詳細とheartbeatとの連携
* pm2設定の全コードと3プロセス管理の実践
* AIニュース自動投稿・X予約投稿スケジューラーの実装
* Windows固有の罠と回避策（完全版）
* PDCAサイクルとの接続 — 自動改善ループの完成

---

## シリーズ記事一覧

### Qiita（無料・技術詳細）

| # | タイトル | リンク |
| --- | --- | --- |
| 1 | 自律型AIエージェントをClaude Codeで自作した話 | [Qiita](https://qiita.com/sentinel_dev/items/e2dd94ec7def5c09c7cb) |
| 2 | Claude Codeのトークン消費を95%削減した方法 | [Qiita](https://qiita.com/sentinel_dev/items/04b6cfed0dabc194cec4) |
| 3 | Windows Node.jsのspawn ENOENTを根本解決する | [Qiita](https://qiita.com/sentinel_dev/items/88fd94baf314be3439c3) |
| 4 | サブエージェント並列実行パターン | [Qiita](https://qiita.com/sentinel_dev/items/fc586285da1de335d8d9) |
| 5 | MEMORY.mdで記憶を永続化する設計パターン | [Qiita](https://qiita.com/sentinel_dev/items/5a24456c8ac3b44a8d75) |
| 6 | SOUL.mdでブレない行動規範を作る方法 | [Qiita](https://qiita.com/sentinel_dev/items/a3d296298d16f921227e) |
| 7 | Claude Code使い方完全ガイド | [Qiita](https://qiita.com/sentinel_dev/items/974fe0af50fcdc13e762) |
| 8 | **Claude Codeエージェントをcronで24時間自動巡回させる方法（本記事）** | — |

### note（有料・設計判断と運用知見）

## おわりに

この記事では、cronとheartbeat方式によるAIエージェントの24時間自動巡回を紹介しました。自動巡回の仕組みで別の方法を使っている方がいたら、コメントで教えてください。

参考になったら **いいね**、後で見返すなら **ストック** していただけると励みになります。

他にもAIエージェント構築のノウハウを公開しています：
