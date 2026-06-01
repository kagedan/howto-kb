---
id: "2026-05-31-claude-code-の組み込みツールを実例でplan-mode-と-monitor-01"
title: "Claude Code の組み込みツールを実例で：plan mode と Monitor"
url: "https://qiita.com/0ff00dex7f3a/items/8e1a9862e1de86502fd7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "Python", "qiita"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

## 結論

Claude Code の組み込みツールには [公式リファレンス](https://code.claude.com/docs/en/tools-reference) で一覧化された30種類以上の Tool があります。本記事はその中でも軽量タスクで効果が大きい次の2つを実例で紹介します。

- `EnterPlanMode` / `ExitPlanMode` / `AskUserQuestion`：実装前に暗黙の前提を質問で表に出す
- `Monitor`：長時間スクリプトの出力をストリーミングで監視し、特定行で反応する

## 1. plan mode で暗黙の前提を質問させる

### 題材

次の指示を出しました。

> プランモードで進めて。`~/scratch/` に「今日の日付＋曜日＋天気欄（手入力用）」を出力する Python スクリプトを作って。

![初期プロンプト](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4411569/77da367e-a217-4caf-8bdd-9ff2e449e8e8.png)

数十行で済むシンプルなタスクです。

### 流れ

#### 質問で前提を引き出す

Claude が `AskUserQuestion` で次の2点を聞いてきました。

- 出力フォーマット（Markdown / テキスト）
- 再実行時の挙動（スキップ / 上書き / タイムスタンプ別ファイル）

![質問画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4411569/2adaf9b1-416f-490d-b25a-b35d562b12e7.png)

どちらも初期指示には書いていなかった項目です。

#### 回答を確定

「Markdown（見出しと空欄）」「既存ファイルがあればスキップ」を選択。

![回答レビュー](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4411569/05891474-611c-45b3-b461-e15db3c0b4f8.png)

![回答受領](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4411569/5f546881-bffa-44ac-a419-bcb4d0c0bf22.png)

#### 計画書を承認

回答を踏まえた計画書が提示されます。

![計画書承認](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4411569/a6df35f5-b97d-40f5-bea5-e146f3c81eae.png)

#### 実装

承認後は通常モードに戻って実装が走ります。

![実装完了](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4411569/1eec2cb8-c2c9-4cd1-82ba-01cbae102641.png)

### 出来上がったスクリプト

```python
from datetime import date
from pathlib import Path

WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]


def main() -> None:
    today = date.today()
    wd = WEEKDAYS_JA[today.weekday()]
    out_path = Path(__file__).parent / f"weather_{today:%Y%m%d}.md"

    if out_path.exists():
        print(f"skip (already exists): {out_path}")
        return

    content = f"# {today:%Y-%m-%d}（{wd}）\n\n## 天気\n\n\n\n## メモ\n\n\n"
    out_path.write_text(content, encoding="utf-8")
    print(f"created: {out_path}")


if __name__ == "__main__":
    main()
```

### 効いた点

シンプルな指示ほど依頼者の頭の中に「当然こうあってほしい」が無自覚に存在します。plan mode の質問フェーズで Claude 側から確認することで、その暗黙の前提が初回実装に反映され、手戻りが減ります。

### plan を自分で改造する

「全部お任せ」で使うと plan の構造は Claude 任せになりますが、`~/.claude/CLAUDE.md` に plan 規約を書いたり、`/plan-strict` のようなカスタム slash command で「必須セクション・やらないこと・検証手順」を固定したり、生成後に `Ctrl+G` で直接編集したりすることで、タスクの種類に応じた plan format を選択的に使い分けられます。改造の余地を知っておくと、軽量タスクでも plan mode の活用幅が広がります。

## 2. Monitor で長時間スクリプトを監視させる

### Monitor ツールとは

[公式ドキュメント](https://code.claude.com/docs/en/tools-reference#monitor-tool) では次のように説明されています。

> The Monitor tool lets Claude watch something in the background and react when it changes, without pausing the conversation.

ログの監視・CI ジョブのポーリング・ディレクトリ監視・任意の長時間スクリプトの出力追跡などに使えます。Claude が裏でスクリプトを書いてバックグラウンド実行し、出力1行ごとに反応します。会話自体は止まりません。

### 題材

次の指示を出しました。

> `~/scratch/dummy_etl.py` を作って。10ファイル処理を模したスクリプトで、4秒間隔で「[N/10] OK」を出力、6ファイル目だけ「[6/10] ERROR: KeyError 'purchase_date'」を出力して終了。これを Monitor で流して、ERROR 行を検知したら即停止してエラー内容を要約して。

![指示とスクリプト作成](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4411569/842e5d0c-010e-474e-becc-f4b38e98234d.png)

### 流れ

Claude が `Monitor` ツールを起動し、出力1行ごとに通知が飛んできます。

![Monitorストリームと要約](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4411569/8910eae3-77db-4e55-939e-8d4c1717da2c.png)

1〜5件目は `[N/10] OK` を受けて Claude が「N件目OK」と短く反応。6件目で `[6/10] ERROR: KeyError 'purchase_date'` を受領した瞬間、スクリプトが `sys.exit(1)` で終了し Monitor のストリームも閉じます。Claude はその直後にエラー内容を要約しました。

```
発生箇所: 6/10ファイル目
エラー種別: KeyError
欠落キー: 'purchase_date'
対処案: dict.get('purchase_date') で防御するか、入力スキーマを事前検証する
```

### 効いた点

`Bash` で同じスクリプトを動かすと、完了するまで Claude のターンが止まります。`Monitor` ならストリーミング受信のため、Claude が会話を続けながら逐次反応できます。長時間ジョブやポーリングでは違いが顕著です。

## ツール選択の指針

| 状況 | 使うツール |
|------|-----------|
| 実装前に方針確認したい | `EnterPlanMode` → `AskUserQuestion` → `ExitPlanMode` |
| 長時間ジョブ・ログを監視したい | `Monitor` |
| 一発のコマンド実行 | `Bash` |

公式リファレンスには他にも `Workflow` `Agent` `Skill` などの組み込みツールが定義されています。手元の Claude Code セッションに何がロードされているかは `What tools do you have access to?` と聞けば一覧してくれます。
