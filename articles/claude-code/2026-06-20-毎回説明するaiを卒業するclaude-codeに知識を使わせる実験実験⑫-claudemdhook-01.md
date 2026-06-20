---
id: "2026-06-20-毎回説明するaiを卒業するclaude-codeに知識を使わせる実験実験⑫-claudemdhook-01"
title: "毎回説明するAIを卒業する。Claude Codeに知識を使わせる実験【実験⑫】 〜CLAUDE.md＋hooksで「言わなくても動く」状態を作った記録～"
url: "https://note.com/w53jbs/n/n8e2e94dfb89e"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "Python", "note"]
date_published: "2026-06-20"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

---

**【実験⑫】｜Claude Code×Obsidian自動化｜はたらくAI社**

---

→ 前回：[【実験⑪】毎回](https://note.com/w53jbs/n/n6c9fef685c4b)[AI](https://note.com/w53jbs/n/n6c9fef685c4b)[に同じことを説明してた。](https://note.com/w53jbs/n/n6c9fef685c4b)[Obsidian](https://note.com/w53jbs/n/n6c9fef685c4b)[で『](https://note.com/w53jbs/n/n6c9fef685c4b)[AI](https://note.com/w53jbs/n/n6c9fef685c4b)[の記憶庫』を作ってみた](https://note.com/w53jbs/n/n6c9fef685c4b)

---

## はじめに

Claude Codeは「読んでください」と言わなければ読まない。「記録してください」と言わなければ書かない。

AIは便利ですが、「何を覚えておくか」は人間が設計する必要があります。

接続しただけでは、手間は何も変わらない。そのことに気づきました。

前回の実験⑪でObsidianの導入・Vault設定・MCP接続まで完了しました。でも毎回指示が必要なら、「AIが記憶を持った」とは言えない。

**「言わなくても自動で動く」状態にする。**

それが今回の実験⑫です。

---

## やったこと

### ① CLAUDE.mdに自動参照ルールを追加

Claude Codeが作業を始める前に、Obsidianの知識OSを自動で読みに行くルールをCLAUDE.mdに書きました。

```
【常時読む（毎回必須）】
  → 知識OS\MEMORY.md

【作業別に読む】
  X投稿・note作成  → identity_aitaro.md
  アイケン審査     → identity_aiken.md
  戦略確認・企画   → project_hatarakuAI.md
  つくるAI社連携   → project_tsukuruAI.md

【作業後に書く】
  X投稿作成後  → X投稿記録\YYYY-MM-DD.md に追記
  実験完了後   → 実験ロードマップ.md を更新
  重要な決定   → MEMORY.md に追記
```

CLAUDE.mdに書くだけ。コードは不要です。

### ② Stop hookで日次ログを自動生成

Claude Codeのセッションが終わるたびにPythonスクリプトを自動実行する設定を追加しました。

**編集するファイルは2つだけです。**

settings.json に以下を追記：

```
"hooks": {
  "Stop": [{
    "matcher": "",
    "hooks": [{
      "type": "command",
      "command": "python D:\\はたらくAI社\\tools\\log_to_obsidian.py"
    }]
  }]
}
```

スクリプトの中身はシンプルです。

```
# 今日のログファイルがなければ作成、あればスキップ
today = datetime.date.today().strftime("%Y-%m-%d")
log_file = VAULT / "X投稿記録" / f"{today}.md"

if not log_file.exists():
    log_file.write_text(テンプレート)  # 日次ログを自動作成
```

朝に作業を始めると、前日のセッション終了時に今日のログファイルが既に出来上がっています。

![](https://assets.st-note.com/img/1781661899-TRquXEt8CyfsmvibJU04zN9k.png?width=1200)

![](https://assets.st-note.com/img/1781661904-obTd7RXMGBU0xAgqrVnilshO.png?width=1200)

---

## 結果

一番変わったのは、AIの性能ではありませんでした。「記録する」という行動が、意識しなくても残るようになったことです。

**「毎回おさらい」がなくなりました。**

設定前：セッション開始 → キャラ設定を説明 → 戦略を共有 → 本題へ（推定5〜10分）

設定後：セッション開始 → 自動でMEMORY.mdを読む → すぐ本題へ

1回5〜10分の短縮。1ヶ月30セッションで計算すると**150〜300分の削減**になる計算です。

日次ログは1週間で7件が自動蓄積されました。「記録しよう」と意識しなくてもObsidianに積み上がっていく状態です。手動で管理していたときは週2〜3件程度だったため、記録量は約2〜3倍になりました。

---

## 気づき

**設定コストは30分でした。**

CLAUDE.mdへの追記が15分。settings.jsonの編集とスクリプト作成が15分。技術的な難しさはほぼなく、「何を自動化するか決める」のが一番時間がかかりました。

もう一つ気づいたこと。**知識OSの中身が整っていないと自動参照しても意味がない。**

Claude Codeが読みに行くファイルの質が、そのまま出力の質になります。ObsidianはAIへの「説明書」を整理する場所でもある、ということです。

---

## 今日からできること

技術に詳しくなくても、最初の一歩はここまでできます。

1. **CLAUDE.mdにルールを書く**（コード不要）
2. **設定や判断基準を1ファイルにまとめてObsidianに置く**
3. **慣れたらhooksで自動化する**

①②だけでも体感が変わります。hooksは慣れてから挑戦で十分です。

---

## 次の実験

実験⑪でObsidianを導入し、実験⑫で自動化しました。

「第二の脳を作った」というより、「第二の脳を育て始めた」段階だと思っています。

次は実験⑬として、「Obsidianに蓄積されたデータをClaude Codeが定期的に分析し、次の投稿戦略を自動提案する」仕組みを作ってみます。

記録するだけでなく、記録を活かす。そこまで育てば、本当の意味で「自分専用のAI」になる気がします。

まだ答えは出ていませんが、やってみます。

![](https://assets.st-note.com/img/1781662028-bH6ks0tS5UyEY7f8RFhrl9DL.png?width=1200)
