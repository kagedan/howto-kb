---
id: "2026-05-23-claude-opus-47とgpt-55-instantを併用する三層レビューワークフローを装して-01"
title: "Claude Opus 4.7とGPT-5.5 Instantを併用する「三層レビュー」ワークフローを装してみた"
url: "https://zenn.dev/kairosai/articles/0137becdcb8239"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "OpenAI", "Gemini", "GPT", "Python"]
date_published: "2026-05-23"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

---

## title: "Claude Opus 4.7とGPT-5.5 Instantを併用する三層レビューワークフロー" emoji: "🤖" type: "tech" topics: ["ai", "claude", "openai", "gemini", "python"] published: true

## TL;DR

* 2026年5月にClaude Opus 4.7とGPT-5.5 Instantが相次いでリリース
* | モデル | 強み |
* |---|---|
* | GPT-5.5 Instant | 高速・低ハルシネーション・Memory連携 |
* | Claude Opus 4.7 | 長文の論理整合性・難問処理・コーディング |
* | Gemini 3.5 Flash | 速度と汎用性のバランス |  
  そこで、それぞれを「初稿→監修→要約」に割り当てるパイプラインを書いてみます。

## 構成

```
[入力プロンプト]
   ↓
   GPT-5.5 Instant (初稿生成)
      ↓
      Claude Opus 4.7 (論理レビュー & 修正)
         ↓
         Gemini 3.5 Flash (3行要約)
            ↓
            [最終出力]
            ```

            ## 実装

            ```python
            import os
            from anthropic import Anthropic
            from openai import OpenAI
            import google.generativeai as genai

            oai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            ant = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            gem = genai.GenerativeModel("gemini-3.5-flash")

            def draft(prompt: str) -> str:
                res = oai.chat.completions.create(
                        model="gpt-5.5-instant",
                                messages=[{"role": "user", "content": prompt}],
                                    )
                                        return res.choices[0].message.content

                                        def review(text: str) -> str:
                                            res = ant.messages.create(
                                                    model="claude-opus-4-7",
                                                            max_tokens=4096,
                                                                    messages=[{
                                                                                "role": "user",
                                                                                            "content": f"次の文章を、事実誤りや論理破綻の観点でレビューして修正版を返してください。\n\n---\n{text}\n---"
                                                                                                    }],
                                                                                                        )
                                                                                                            return res.content[0].text
                                                                                                            
                                                                                                            def summarize(text: str) -> str:
                                                                                                                res = gem.generate_content(f"次を3行で要約:\n\n{text}")
                                                                                                                    return res.text
                                                                                                                    
                                                                                                                    def pipeline(prompt: str) -> dict:
                                                                                                                        d = draft(prompt)
                                                                                                                            r = review(d)
                                                                                                                                s = summarize(r)
                                                                                                                                    return {"draft": d, "reviewed": r, "summary": s}
                                                                                                                                    
                                                                                                                                    if __name__ == "__main__":
                                                                                                                                        out = pipeline("2026年の生成AI業界の主要トピックを3つ挙げて解説して")
                                                                                                                                            print(out["summary"])
                                                                                                                                            ```
                                                                                                                                            
                                                                                                                                            ## ハマりどころ
                                                                                                                                            
                                                                                                                                            - Claude Opus 4.7のmax_tokensはデフォルトでは小さめなので、長文レビューには明示的に4096〜8192を指定する。
                                                                                                                                            - GPT-5.5 InstantはMemory sourcesが有効だと前回の文脈を引っ張るので、A/B検証する時はMemoryをオフに。
                                                                                                                                            - Gemini 3.5 Flashは速度優先のため、3行要約には最適だが「長文構造化」には不向き。
                                                                                                                                            
                                                                                                                                            ## まとめ
                                                                                                                                            
                                                                                                                                            役割分担を徹底することで、1モデル単独で書かせるよりも品質が安定します。副業や受託業務の納品工程に組み込むと体感で2〜3割の時短になります。
                                                                                                                                            
                                                                                                                                            次回はこれをClaude Skillsとしてパッケージする手順を書きます。
```
