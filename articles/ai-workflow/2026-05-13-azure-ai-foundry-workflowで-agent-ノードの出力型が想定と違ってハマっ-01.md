---
id: "2026-05-13-azure-ai-foundry-workflowで-agent-ノードの出力型が想定と違ってハマっ-01"
title: "Azure AI Foundry Workflowで Agent ノードの出力型が想定と違ってハマった話"
url: "https://zenn.dev/snboku/articles/6e651c97d7c65c"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "zenn"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

## はじめに

Azure AI Foundry の Workflow 機能を使い始めて約半年、いくつかのプロジェクトで Agent ベースのワークフローを構築してきました。その中で **Agent ノードの出力型** に関する仕様で詰まったポイントがあったので共有します。

公式ドキュメントには明記されていない挙動なので、同じところで止まる方の助けになれば幸いです。

## 発生した問題

ある業務システムの PoC で、こういうワークフローを組みました。

1. ユーザーからの問い合わせを受け取る
2. **Agent ノード** で意図分類 + 必要な情報を抽出
3. 抽出結果を後続の **Function ノード** に渡して DB 検索

期待していたのは、Agent ノードが構造化された JSON(意図カテゴリと抽出フィールドを持つオブジェクト)を返してくれること。

```
// 期待していた出力
{
  "intent": "search_document",
  "keywords": ["契約書", "2024年"]
}
```

しかし実際には、こういう出力が返ってきました。

```
私はあなたの質問を理解しました。
検索したい意図は契約書で、キーワードは2024年です。
```

Agent ノードはデフォルトで **自然言語の応答** を返してきて、後続の Function ノードに渡すと型エラーで停止してしまいました。

## 原因の整理

公式ドキュメントを読み返すと、Agent ノードは LLM ベースなので **「自由形式のテキスト応答」がデフォルト** であることが分かりました。

構造化出力を得たい場合は、以下の3つを **明示的に設定** する必要があります。

| 設定項目 | 内容 |
| --- | --- |
| システムプロンプト | JSON Schema の指示を明記 |
| Response Format | `json_object` に設定 |
| 後続ノード | 型パース処理を別途実装 |

つまり、**「Agent ノードに JSON で返してとプロンプトで書く」だけでは不十分**で、Response Format の設定と、それを受け取る側の Function ノードでの normalize 処理がセットで必要、ということでした。

## 解決策

最終的に以下の3層構造で安定させました。

### 1. システムプロンプトで JSON Schema を明記

```
あなたはユーザーの問い合わせを分析するアシスタントです。

出力は必ず以下のJSON形式のみで返してください:
{
  "intent": "search_document" | "create_ticket" | "other",
  "keywords": ["キーワード1", "キーワード2"]
}

説明文や前置きは一切含めないでください。
```

### 2. Agent ノードの Response Format 設定

Agent ノードの設定画面で **Response Format** を `json_object` に変更します。これを設定しないと、プロンプトで JSON を指示しても自然言語が混ざることがあります。

### 3. Function ノードで normalize 層を挟む

Agent の出力を直接後続に渡さず、**Function ノードでパース・バリデーションを実行** します。

```
import json

def normalize_agent_output(raw_output: str) -> dict:
    try:
        parsed = json.loads(raw_output)
        # 必須フィールドの検証
        if "intent" not in parsed or "keywords" not in parsed:
            raise ValueError("Required fields missing")
        return parsed
    except json.JSONDecodeError:
        # フォールバック: デフォルト値を返す
        return {"intent": "other", "keywords": []}
```

この3層を入れた後、出力の安定性が大幅に向上しました。

## 学び

今回の経験から得た教訓は3つです。

### 1. Agent ノードは便利だが「決定的な動作」を期待してはいけない

Agent は LLM ベースなので、本質的に確率的な挙動をします。「だいたい JSON で返ってくるはず」という前提で設計すると、本番運用で確実に痛い目を見ます。

### 2. Agent の出力を一度 normalize する層を挟むのが安全

「Agent の出力をそのまま使う」設計は PoC では動いても、スケール時に破綻しやすいです。Normalize 層は **コストではなく投資** と考えるべきだと思います。

### 3. LLM ベースのワークフローは「型の境界」を意識的に設計する

従来のシステム設計では「型」は言語処理系が保証してくれましたが、LLM ベースの Workflow では **設計者が明示的に型の境界を作らないと、型は存在しません**。これは発想の転換が必要なポイントでした。

## おわりに

Azure AI Foundry Workflow は強力な反面、まだドキュメントが薄い部分があります。特に Agent ノードは「直感的に動きそうで動かない」典型例なので、同じところで詰まった方の参考になれば嬉しいです。

似たような事例があれば、コメントで教えてください。
