---
id: "2026-07-04-善性aiエージェントへの道-8-sdkの外へclaude-code-hooksで実行前に止める監査を-01"
title: "善性AIエージェントへの道 #8 ——SDKの外へ——Claude Code hooksで「実行前に止める」監査を配る（agentlens v0.6.0）"
url: "https://note.com/dreamrize/n/n8d4aeec3ec84"
source: "note"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "LLM", "note"]
date_published: "2026-07-04"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

「本ページはプロモーションが含まれています」

## 前回の着地点と、今回の出発点

#7 で agentlens v0.5.0 はホワイトリストを手に入れた。記録する → 危険なら止める → 記録の信頼性を証明する → 誤検知を管理する。次はフィードバックループだと予告した。

今回も予告を裏切る。理由は前回と同じで、もっと手前に向き合うべき現実があったからだ。ただし今回の現実はコードの中ではなく、市場の側にあった。

---

## 実走の記録：数字を直視する

正直に書く。agentlens の現在地は、GitHub Star 0、PyPIダウンロード月233件（ミラー含む）だ。

さらに敌対的に調べてもらった結果、もっと痛い事実が2つ見つかった。

一つ。同名のプロダクトがすでに存在する。しかも「tamper-evident audit trail」という同じ価値提案で、開発は活発、Hacker Newsにも投稿済み。名前空間の戦いは実質的に負けている。

二つ。もっと本質的な問題として、**統合ポイント自体が主流から外れ始めていた**。2026年の今、Claudeでエージェントを動かす人の多くは、素のAnthropic SDKでループを自作していない。Claude CodeやAgent SDKの上で動かしている。公式はhooksとOpenTelemetryを統合点として標準化し、MCPのセマンティック規約も仕様にマージされた。

つまり「anthropic.Anthropic() をラップする」という agentlens の入口は、エージェント開発の主戦場から見ると裏口になりつつある。

---

## 判断：資産はそのまま、置き場所を変える

ここで選択肢は3つあった。現路線の深化、既存エコシステムへの合流、そして統合ポイントの乗り換え。

v0.6.0 が選んだのは乗り換えだ。ハッシュチェーン（#6）もルールエンジン（#3）もホワイトリスト（#7）も、一行も捨てない。変えるのはイベントの受け取り口だけ。Claude Code の PreToolUse / PostToolUse hooks から直接イベントを受け取る。

### 設定は settings.json に2ブロック

```
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "*", "hooks": [
        {"type": "command", "command": "agentlens hook pre --log ~/.agentlens/audit.jsonl --block critical"}
      ]}
    ],
    "PostToolUse": [
      {"matcher": "*", "hooks": [
        {"type": "command", "command": "agentlens hook post --log ~/.agentlens/audit.jsonl"}
      ]}
    ]
  }
}
```

これだけで、Claude Code が実行するすべてのツールコールがハッシュチェーンつきの監査ログに記録され、危険なコマンドは実行前に拒否される。

### 実行前ブロックの実例

```
$ echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | agentlens hook pre --log audit.jsonl
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
 "permissionDecisionReason": "agentlens blocked this tool call: [SHELL_RM_ROOT] ..."}}

$ agentlens verify audit.jsonl
✅ チェーン整合性OK  (1 エントリ)
```

ブロックされた呼び出しも監査ログには残る。「止めたという事実」こそ監査の対象だからだ。

---

## 設計の判断軸

**なぜfail-openにしたか。**監査ロガーのバグがエージェントを止めてはならない。壊れたJSONが来ても、ログ先に書けなくても、hookはexit 0で退く。監査のための部品が可用性のボトルネックになった瞬間、誰も使わなくなる。

**なぜpostは結果だけ記録するか。**preとpostを両方登録する推奨構成では、tool\_useはpreが書く。postも書くと重複する。preを登録しない人のために --standalone を用意した。

**なぜ判定に今回もLLMを使わないか。**#7と同じ答えだ。判定器は決定論的で再現可能であること。「AIが雰囲気で止めた」は監査にならない。

---

## テストと現在地

hooks統合に13本のテストを追加し、全50本通過。ブロック・抑制・ハッシュチェーンの整合性をhooks経由でも確認している。

現在地：行動の記録 ✅ / 危険検知 ✅ / CLIビューア ✅ / 実行前ブロック ✅ / 改ざん検知 ✅ / 誤検知対策 ✅ / **Claude Code hooks統合 ✅ v0.6.0** / フィードバックループ → 設計段階のまま

## 使い始めるには

```
pip install agentlens-io
agentlens hook install   # settings.jsonのスニペットを表示
```

GitHub: https://github.com/agentlens-io/agentlens  
PyPI: https://pypi.org/project/agentlens-io/

---

## 次回 #9 ——今度こそフィードバックループ、かもしれない

2回連続で予告を裏切ったので、もう断言はしない。ログの蓄積からルールを自動改善するフィードバックループは依然として作りたい。一方で、EU AI Act第12条やISO/IEC 42001の監査証跡要件にログをマッピングするエクスポート機能への引力も強い。

次に何を作るかは、今回と同じように市場の側のデータを見て決める。自分のロードマップより、使われる場所に置くこと。今回学んだのはそれだ。

---

## 一次情報・参考リンク

agentlens GitHub: https://github.com/agentlens-io/agentlens  
PyPI: https://pypi.org/project/agentlens-io/  
Claude Code hooks 公式ドキュメント: https://code.claude.com/docs/en/hooks

【広告】以下のリンクはアフィリエイト広告を含みます。  
▶ 「FP陵子の相談室」はこちら  
<https://px.a8.net/svt/ejp?a8mat=4B1HTJ+3R5F3M+5MAS+5ZEMQ>
