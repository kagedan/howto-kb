---
id: "2026-06-27-devin-for-terminal-の-hooks-で危ないコマンドを自動で止めるガードレール設計-01"
title: "Devin for Terminal の Hooks で「危ないコマンド」を自動で止める：ガードレール設計"
url: "https://zenn.dev/asix/articles/ef08080dd3b87b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "LLM", "zenn"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-rss"
query: ""
---

:::note info  
🚀 **Devin専門の解説メディア「StartDevin」を運営中！**  
Devinの導入・使い方・最新アップデート・活用事例を、日本語でまとめています。  
👉 **[StartDevin をチェックする（startdevin.jp）](https://startdevin.jp/)**  
:::

## はじめに

AIエージェントに自動承認（前に書いた `dangerous` モードなど）で作業を任せるとき、頭をよぎるのは「**`rm -rf` や `git push --force` を勝手に実行されたらどうしよう**」という不安です。

「信頼できる場面でだけ使う」と言うのは簡単ですが、人間の注意力には限界があります。本当に欲しいのは、**仕組みとして危険な操作を止める**ガードレールです。

Devin for Terminal の **Hooks** は、ツール実行の前後にコマンドやチェックを差し込める仕組みで、まさにこのガードレールに使えます。しかも Claude Code の hooks 形式と互換なので、既存の設定を流用できます。今回はこの Hooks を「安全弁」として設計する話です。

> 内容は公式ドキュメント（Hooks Overview）と `devin 2026.5.x` で確認しています。バージョンによる差は `devin --help` や公式ドキュメントで補ってください。

## Hooks が差し込める7つのタイミング

Hooks は、セッションのライフサイクル上の7つのイベントに反応します。

| イベント | タイミング |
| --- | --- |
| `PreToolUse` | ツールが実行される**前** |
| `PostToolUse` | ツールが完了した**後** |
| `PermissionRequest` | 権限の判断が必要なとき |
| `UserPromptSubmit` | ユーザーがメッセージを送信したとき |
| `Stop` | エージェントが停止しようとするとき |
| `SessionStart` | セッション開始時 |
| `SessionEnd` | セッション終了時 |

ガードレール用途で主役になるのは **`PreToolUse`** です。ツールが動く**前**に割り込んで、内容を検査し、危なければ止められます。

## どこに設定するか

Hooks の設定は、専用ファイルか config に書きます。

| 場所 | 用途 |
| --- | --- |
| `.devin/hooks.v1.json` | 推奨。単独ファイルで、中身全体が hooks オブジェクト |
| `.devin/config.json` の `hooks` キー | config に同居させる場合 |
| `.devin/config.local.json` | 個人用のローカル上書き（git除外） |
| `.claude/settings.json` | Claude Code 形式（後述） |

## 実例：危険なコマンドをブロックする

`PreToolUse` で、シェル実行（`exec`）の前に検査スクリプトを走らせる設定です。`.devin/hooks.v1.json` に書きます。

```
{
  "PreToolUse": [
    {
      "matcher": "exec",
      "hooks": [
        {
          "type": "command",
          "command": "./scripts/check-command.sh"
        }
      ]
    }
  ]
}
```

`matcher` で対象のツール（ここでは `exec`）を絞り、`type: "command"` のフックが検査スクリプトを呼びます。**スクリプトにはイベントデータがJSONで標準入力に渡され、終了コード2を返すとその操作をブロック**できます。

検査スクリプト側の例はこんなイメージです。

```
#!/usr/bin/env bash
# 標準入力から実行されようとしているコマンドを受け取る
payload=$(cat)
if echo "$payload" | grep -E 'rm -rf|push --force|DROP TABLE'; then
  echo "危険なコマンドを検出。ブロックします" >&2
  exit 2   # 終了コード2でツール実行を止める
fi
exit 0
```

これで、`dangerous` モードで自動承認していても、**`rm -rf` 系だけは絶対に通さない**安全弁ができます。私はこの「自動承認 × ピンポイントの拒否リスト」の組み合わせが、いちばん現実的な落としどころだと感じています。

## フックでできること

ブロック以外にも、フックは幅広く使えます。

| やりたいこと | フックの使い方 |
| --- | --- |
| 危険コマンドを止める | `PreToolUse` で終了コード2 → ブロック |
| 編集後に自動整形 | `PostToolUse` で formatter を実行 |
| 文脈を注入 | ツール呼び出し時に指示を追加 |
| 通知・ログ | 副作用としてスクリプト実行 |
| 権限を動的制御 | `decision` に `approve` / `block` を返す |

`type` には、シェルを叩く `command` のほかに、LLMで判断する `prompt` 型もあります。「このコマンドは文脈的に妥当か」をAIに判断させる、といった柔らかい制御も可能です。

## Claude Code の hooks をそのまま使える

Devin for Terminal の hooks は **Claude Code の hooks 形式と互換**です。`read_config_from.claude` が有効（デフォルト）のとき、**`.claude/settings.json` の hooks を自動で読み込みます**。

すでに Claude Code で「`rm -rf` を止めるフック」を書いているなら、Devin 側でも同じガードレールがそのまま効きます。セッション中は **`/hooks`** で、いま読み込まれているフックとその設定元ファイルを一覧できるので、「どこの設定が効いているか」を確認できます。

## おわりに

自動承認は便利ですが、無防備に使うと事故ります。Hooks の `PreToolUse` で危険操作だけを確実に弾く安全弁を1枚かませておくと、「自動で回す」と「事故らない」を両立できます。

しかも Claude Code の hooks 資産はそのまま使える。まずは `rm -rf` と `push --force` を止めるだけの小さなフックから始めて、自動化の安心感を底上げしてみてください。

---

## 参考リンク
