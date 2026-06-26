---
id: "2026-06-26-claude-codeopus-48が無言で止まる問題を-stop-hook-で自動復旧する-01"
title: "Claude Code（Opus 4.8）が無言で止まる問題を Stop hook で自動復旧する"
url: "https://note.com/ai_eng_tech/n/n266bd07443a6"
source: "note"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "Python", "note"]
date_published: "2026-06-26"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

ファイル編集を頼んだのに、Claude Code が「では編集します」と説明しただけで、何も実行されないままターンが終わる。

エラーも出ない。

もう一度promptを送っても、また説明だけして止まる。

この「無言で止まる」現象は、特に Opus 4.8 で目立つ既知のバグです。

原因はツール呼び出しがテキストとして漏れていること。

この記事では、原因と、ルールファイルへの追記や /clear が緩和にとどまる理由、そして Stop hook で自動復旧する実装（誤検知抑制・無限ループ防止・テスト込み）を、そのままコピーして使える形で紹介します。

  

## 症状：ツールが動かないまま、無言でターンが終わる

正常なツール呼び出しは、ハーネスが「構造化された呼び出し（tool\_use）」として受け取り、実際にファイル編集やコマンド実行が走ります。

ところが壊れると、本来は構造化ブロックで届くはずのツール呼び出しが、レガシーな XML 形式の「ただのテキスト」として出力されてしまいます。

イメージはこうです。

```
（正常）ハーネスが tool_use ブロックとして解釈 → ツールが実行される

（壊れ）assistant の本文に、実行されない XML がそのまま流れる：
<function_calls>
<invoke name="Edit">
<parameter name="file_path">...
（ここで実行されず、ターンが終わる）
```

ハーネスはこれをツール呼び出しと解釈できないので、ただのテキストとして扱います。

結果、コマンドは何も走らないままターンが終了します。

「The model's tool call could not be parsed」というエラーが出る場合もあれば、エラーすら出ずに静かに止まる場合もあります。

体感としては、長いセッションや大きめのコンテキストで作業しているときに、ふっと処理が進まなくなる、という出方をします。

## なぜ自動で復旧しないのか

Claude Code は、本物のツールエラーには強いです。

たとえばコマンドが exit 1 で失敗したり、ファイルが見つからなかったりした場合は、その失敗を受け取って自動でリトライ・修正してくれます。

ところが今回のケースは構造がまったく違います。

ツール呼び出しが「テキスト」として出てしまうと、そもそもツール呼び出しとして認識されません。

認識されていないので、リトライすべき対象が存在しません。

だから自動回復のしくみが働かず、無言で止まったまま放置されます。

これは2026年5月末ごろから目立つようになった既知の回帰バグで、特に Opus 4.8 で踏みやすいことが報告されています（[Qiita: invoke が“ただの文字”で出て止まるバグ【公式既知バグ】](https://qiita.com/sutaminajing40/items/0f07e9c280ad7ed38cd7)、[note: Opus 4.8 が突然止まる「could not be parsed」](https://note.com/kazu_t/n/n4d6d730b1b43)）。

発生しやすい条件もだいぶ絞り込まれています（[Zenn: Opus 4.8 で全ツール呼び出しが壊れる回避策](https://zenn.dev/edhiblemeer/articles/claude-code-opus48-tool-corruption)）。

* 長時間・複数日にまたがるセッション
* 大きなコンテキスト、/compact 直後の状態
* 複数のツールを同時に呼び出すターン
* MCP サーバーを3つ以上つないでいる
* 長い日本語・中国語などの CJK 文字列

どれも、腰を据えて開発しているときほど踏みやすい条件です。

## ルール追記や /clear だけでは足りない

よく紹介される対処は2つあります。

ひとつは Claude のルールファイル（プロジェクト直下に置く指示書）に「英語で思考して日本語で返す」といった一行を足す方法。

もうひとつは、おかしくなったら手動でリトライし、ダメなら /clear や新規セッションで仕切り直す方法です。

どちらも効果はありますが、緩和にとどまります。

ルールファイルはあくまで advisory です。

モデルが読む前提のルールなので、タイミングによっては読み込まれず、設定したのに効かないことがあります。

/clear は確実ですが、人間が「あ、止まってる」と気づいて手を動かす必要があり、しかも積み上げたコンテキストを失います。

欲しいのは、止まったら気づく前に自動で蹴り直してくれる、決定的な仕組みです。

そこで Stop hook の出番になります。

## Stop hook の前提

hook は、特定のイベントで Claude Code が必ず実行する外部スクリプトです。

ルールファイルのようにモデルの気分に左右される advisory ではなく、ハーネスが確実に動かす deterministic な処理です。

ここが今回の肝になります。

hook にはいくつか発火タイミングがあります。

今回使うのは Stop です。

Stop hook は標準入力で **transcript\_path**（会話ログのパス）や **session\_id** を受け取ります。

そして標準出力に次の JSON を返すと、Claude は停止せずに、reason をガイダンスとして会話を続行します（[Claude Code Docs: Hooks](https://code.claude.com/docs/en/hooks)）。

```
{"decision": "block", "reason": "ここに続行の指示を書く"}
```

登録は **settings.json** に書くだけです。

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "python3 ~/.claude/hooks/retry-malformed-toolcall.py" }
        ]
      }
    ]
  }
}
```

つまり「ターンが終わる直前に直前の出力を覗き見て、ツール呼び出しが漏れていたら続行を強制する」というフックが書ければよいわけです。

## フックの中身：検知・誤検知抑制・無限ループ防止

やることは3つです。

漏れたツール呼び出しを検知し、説明用の例示を誤検知せず、無限ループに陥らないようにする。

### 漏れたツール呼び出しを検知する

検知は、漏れたときだけ本文に現れる高精度なシグネチャを部分一致で探します。

```
function_calls>
invoke name=
parameter name=
</invoke>
```

これらは通常の文章にはまず出てきません。

直前の assistant メッセージの本文を transcript から読み取り、このシグネチャが含まれていたら「漏れた」と判定します。

### 説明用の例示を誤検知しない

ここで素朴に実装すると、まさにこの記事のように「ツール構文を説明している文章」まで誤検知してしまいます。

対策はシンプルで、判定の前にコードフェンス（三連バッククォート）とインラインコードを取り除きます。

```
import re

FENCE = "`" * 3  # 三連バッククォート

def strip_code(text):
    text = re.sub(FENCE + r".*?" + FENCE, "", text, flags=re.DOTALL)  # コードフェンス
    text = re.sub(r"`[^`]*`", "", text)                              # インラインコード
    return text
```

実際に漏れたツール呼び出しはコードフェンスに包まれていないので、この前処理で本物の検知漏れはほぼ起きません。

説明・例示だけを綺麗に除外できます。

### 無限ループを防ぐ

block を返し続けると、同じバグが連発したときにフックが暴走します。

そこで、同一セッションでの連続検知回数をカウンタファイルに記録します。

上限（ここでは5回）を超えたら、それ以上は自動続行せず停止を許可します。

ポイントは2つあります。

ひとつは、壊れた痕跡がない通常完了のターンではカウンタをリセットして一切干渉しないこと。

もうひとつは、上限に到達したらカウンタを消さずに保持（ラッチ）すること。

ここで消してしまうと、次の検知でまた0から数え直し、結局ループから抜けられなくなります。

### 完成コード（全文）

以上をまとめたフックの全文です。

標準ライブラリだけで動き、外部依存はありません。

```
#!/usr/bin/env python3
"""Stop hook: 実行されなかった壊れたツール呼び出しを検知し、自動で続行させる。"""
import json
import os
import re
import sys

MAX_RETRIES = 5
FENCE = "`" * 3  # 三連バッククォート

# 漏れたときだけ本文に現れる高精度シグネチャ（部分一致）
SIGNATURES = (
    "function_calls>",
    "invoke name=",
    "parameter name=",
    "</invoke>",
)

def strip_code(text):
    # 説明用のコードブロック/インラインコードを除外してから判定する
    text = re.sub(FENCE + r".*?" + FENCE, "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", "", text)
    return text

def read_last_assistant_text(transcript_path):
    try:
        with open(transcript_path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return None
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = ev.get("message") if isinstance(ev.get("message"), dict) else ev
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                c.get("text", "")
                for c in content
                if isinstance(c, dict) and c.get("type") == "text"
            )
        return ""
    return None

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    transcript_path = data.get("transcript_path")
    session_id = data.get("session_id") or "default"
    if not transcript_path:
        sys.exit(0)

    counter_file = os.path.expanduser(f"~/.claude/tmp/malformed-retry-{session_id}.count")
    text = read_last_assistant_text(transcript_path)
    if text is None:
        sys.exit(0)

    malformed = any(sig in strip_code(text) for sig in SIGNATURES)

    if not malformed:
        # 通常完了 → カウンタをリセットして干渉しない
        try:
            os.remove(counter_file)
        except OSError:
            pass
        sys.exit(0)

    try:
        with open(counter_file) as f:
            count = int(f.read().strip() or "0")
    except (OSError, ValueError):
        count = 0

    if count >= MAX_RETRIES:
        # 上限到達 → 停止を許可（カウンタは保持してラッチ）
        sys.exit(0)

    os.makedirs(os.path.dirname(counter_file), exist_ok=True)
    try:
        with open(counter_file, "w") as f:
            f.write(str(count + 1))
    except OSError:
        pass

    reason = (
        "前回の出力に、システムが実行できなかった壊れたツール呼び出しが含まれており、"
        "ツールは実行されていません。タスクは未完了です。"
        "直前に行おうとしたツール操作を、正しいツール呼び出し形式で今すぐ出し直して続行してください。"
        "説明文を繰り返すのではなく、ツール呼び出しそのものを実行すること。"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

保存したら実行権限を付けておきます。

```
chmod +x ~/.claude/hooks/retry-malformed-toolcall.py
```

なお、Stop hook の無限ループ対策として、入力 JSON の **stop\_hook\_active** を見て早期 return する方法もあります。

今回はセッション横断で確実にラッチさせたかったので、カウンタファイル方式を採りました。

似たアプローチの先行事例もあります（[Zenn: ツール呼び出しが生テキストで表示されるときの Stop hook 対策](https://zenn.dev/ultimatile/articles/claude-code-leaked-tool-call-stop-hook)）。

## 単体テストで検証する

hook は「確実に動く」ことが価値なので、入れる前にテストで挙動を固定します。

確認したいのは3つの分岐です。

* 通常完了の出力 → 何もせず素通り（exit 0、stdout なし）
* 壊れたツール呼び出しを含む出力 → decision:block を返す
* 連続検知が上限に達したあと → 停止を許可（block しない）

標準入力をモックして、フックを起動し、標準出力を検証するだけです。

```
import json, subprocess, sys

def run_hook(stdin_obj):
    p = subprocess.run(
        [sys.executable, "retry-malformed-toolcall.py"],
        input=json.dumps(stdin_obj), capture_output=True, text=True,
    )
    return p.stdout.strip()

# 壊れた出力を含む transcript を用意して渡すと decision:block が返る
out = run_hook({"transcript_path": "fixtures/malformed.jsonl", "session_id": "t1"})
assert json.loads(out)["decision"] == "block"

# 通常完了の transcript なら stdout は空
out = run_hook({"transcript_path": "fixtures/normal.jsonl", "session_id": "t2"})
assert out == ""
```

これで「動くらしい」から「動くと言える」に変わります。

カウンタファイルはテストごとに HOME を一時ディレクトリへ差し替えると隔離できます。

## それでも救えないときは、潔く仕切り直す

このフックは緩和策であって、根本解決ではありません。

モデルが出力形式を崩さなければ、そもそも発火しません。

そして上限に到達したということは、同じバグが連発している状態です。

そのときは粘らず、新規セッションや /clear で仕切り直すのが結局いちばん速いです。

あわせて、発生条件（長時間セッション・巨大コンテキスト・MCP の多重接続）を踏みにくいセッション運用を意識すると、発火頻度そのものが下がります。

それでも、人間が張り付いて監視しなくても、止まったら自動で蹴り直してくれる安全網があるのは大きいです。

「無言で止まる」を「勝手に立ち直る」に変える。

advisory なルールではなく、ハーネスが必ず実行する deterministic な hook だからこそ、モデルの気まぐれに依存せずに効きます。

同じ現象でターンが溶けている人は、まず Stop hook を一枚かませてみてください。

仕組みをもう一段深く知りたい場合は、公式の [Claude Code Docs: Hooks](https://code.claude.com/docs/en/hooks) が出発点として確実です。
