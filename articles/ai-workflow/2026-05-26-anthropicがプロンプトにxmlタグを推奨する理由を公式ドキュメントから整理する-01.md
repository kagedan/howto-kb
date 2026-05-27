---
id: "2026-05-26-anthropicがプロンプトにxmlタグを推奨する理由を公式ドキュメントから整理する-01"
title: "AnthropicがプロンプトにXMLタグを推奨する理由を公式ドキュメントから整理する"
url: "https://zenn.dev/goki602/articles/2026-05-26-claude-prompt-xml-tags-why"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "zenn"]
date_published: "2026-05-26"
date_collected: "2026-05-27"
summary_by: "auto-rss"
query: ""
---

「Markdownの見出しで整理しているのに、Claudeの応答がどうも安定しない」——そういった経験があるなら、AnthropicがClaude向けに明示的に推奨するXMLタグ構造化を一度試す価値がある。

今週のはてブIT（29 users）でも取り上げられた「なぜAnthropicはプロンプトにXMLタグを推奨するのか」という問いに対し、公式ドキュメントと公開情報をもとに整理してみる。**結論から言うと、ClaudeはXMLフォーマットを大量に学習しており、XMLタグをテキストとしてではなく「構造」として処理できる**のが技術的な背景だ。これを知った上でプロンプトを設計すると、複雑な指示の応答精度が上がりやすい。

## なぜClaudeはXMLタグを「構造」として扱えるのか

Anthropicの公式ドキュメント（[Use XML tags to structure your prompts](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags)）には、「プロンプトに複数のコンポーネント（文脈・指示・例など）が含まれる場合、XMLタグはgame-changerになり得る」と明記されている。

技術的な背景として、Claudeは学習コーパスの中に**ドキュメント・構造化データセット・マークアップ・設定ファイル・Anthropic社内のプロンプト形式**といったXMLフォーマットのデータを大量に含んでいる。その結果、Claudeはこれらを「テキストを読み通す」ではなく「構造言語として内面化」した状態にある。

具体的には、XMLタグを見たClaudeは次の処理を行う：

* **セマンティックな役割の識別** — `<context>` はバックグラウンド情報のシグナル、`<instructions>` は何をすべきかのシグナルとして解釈する
* **アテンション配分の調整** — `<instructions>` 内のテキストは、バックグラウンドテキストとは異なる重みで処理される
* **コンテンツの分離（isolation）** — 複数のセクションが別々のタグで包まれることで、処理中の「情報の混在（bleeding）」が防がれる

対してMarkdownの見出し（`## 見出し`）は、フォーマット表示のために設計されたものだ。Claudeが構造として認識する深度はXMLより浅く、複雑なコンテキストほどこの差が応答品質に現れやすい。これはHacker News上のディスカッション（[Why XML tags are so fundamental to Claude](https://news.ycombinator.com/item?id=47207236)）でも多数のエンジニアが実感として報告していた点だ。

## 実践的な使い方：3つのパターン

### パターン1：指示と入力データの分離

最もシンプルかつ効果が出やすい使い方は、**指示と入力データを別タグで分ける**ことだ。

```
<instructions>
以下の <document> の内容を3点に要約してください。
箇条書きで、各点は50字以内でまとめること。
</instructions>

<document>
{{ユーザーが貼り付けるテキスト}}
</document>
```

タグを参照するときは、プロンプト内で同じタグ名を使って言及するとよい（例：「`<document>` に含まれる情報を使って…」）。公式では、この一貫性が解釈精度に寄与すると述べている。

なお、公式ドキュメントは「**1文だけのプロンプトにXMLタグは不要**」とも明記している。タグが効果を発揮するのは、複数の異なるセクションが存在する場合だ。典型的な構成は3〜5タグ（`<context>`, `<task>`, `<instructions>`, `<output_format>`）とされている。

### パターン2：複数ドキュメントの階層構造

複数のドキュメントを同時に参照させる場合、階層的なタグ構造が有効だ。

```
<documents>
  <document index="1">
    <source>report-2026-q1.pdf</source>
    <document_content>
    {{Q1レポートの内容}}
    </document_content>
  </document>
  <document index="2">
    <source>report-2026-q2.pdf</source>
    <document_content>
    {{Q2レポートの内容}}
    </document_content>
  </document>
</documents>
```

`index` 属性を付けることでClaudeが複数ドキュメントを区別しやすくなる。[Long context prompting tips](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips) では、長いドキュメントをプロンプトの先頭に置き、XMLタグで区切ることを推奨している。ドキュメント数が増えるほどこの構造の効果が上がるとされている。

### パターン3：Chain of Thoughtとの組み合わせ

段階的な推論をClaudeに明示させたい場合、`<thinking>` と `<answer>` タグの組み合わせが有効だ。

```
<task>
以下のビジネス問題を分析してください。
</task>

<instructions>
まず <thinking> タグの中で推論の過程を整理し、
その後 <answer> タグで最終的な提案を出してください。
</instructions>

<context>
{{分析対象の情報}}
</context>
```

公式の[Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) では、「XMLタグとマルチショットプロンプティング、Chain of Thoughtを組み合わせることで、super-structured・high-performanceなプロンプトが作れる」としている。

## 注意点：過剰タグ付けは逆効果

公式ドキュメントは明示的に「**over-tagging（過剰なタグ付け）は避けること**」と述べている。守っておきたいルールをまとめると：

* 1文で完結するセクションにはタグ不要
* タグ名は内容と一致した意味のある名前にする（`<stuff>` や `<misc>` はNG）
* 同じプロンプト内ではタグ名を統一し、参照する際も同じ名前で呼ぶ
* タグの数は3〜5個が目安。それ以上は可読性が落ちる

また、「Claude専用のベストXMLタグ名がある」というわけではない。公式には「Claudeが特定のタグ名でトレーニングされているわけではない」と述べており、**タグ名が内容と一致していることの方が重要**だ。`<context>` でも `<background>` でも、一貫して使えばどちらも機能する。

## まとめ

AnthropicがXMLタグをプロンプトに推奨する技術的な理由は、**Claudeがその学習過程でXMLを構造言語として内面化しており、タグを意味的なシグナルとして処理できる**という点にある。Markdownと見た目が似ているため軽視されやすいが、複数のセクションを持つ複雑なプロンプトでは応答品質への影響が出やすい選択だ。

試すなら `<instructions>` と `<context>` の2タグから始めるのが現実的な入口になる。詳細な使い方のガイドは[公式ドキュメント](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags)に整理されているので、次のプロンプト設計時の参照先にしてほしい。
