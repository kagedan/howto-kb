---
id: "2026-03-29-claude-codeでai同士の会話によるブログ自動生成システムを作ってみた-01"
title: "Claude Codeで「AI同士の会話」によるブログ自動生成システムを作ってみた"
url: "https://qiita.com/kenji_harada/items/58b8dbb395199bbe9f1e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "GPT", "qiita"]
date_published: "2026-03-29"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

この記事は自社ブログ([nands.tech](https://nands.tech/posts/claude-code-ai-to-ai-blog-auto-generation-714286))の要約版です

## なぜAI1つじゃダメなのか？

最近Claude Codeで面白いシステムを作った話を書こうと思う。

いきなりだが、AIに記事を1回で完璧に書かせるのは無理ゲーだと思っている。ChatGPTもClaudeも、ワンショットで長文を生成すると「情報てんこ盛りだけど、なんか読む気しない」記事ができあがる。

理由は明確で、AIには「何を削るか」の判断ができないから。全部重要に見えて、結果として誰の心にも刺さらない平坦な文章になってしまう。

じゃあどうするか。人間の編集現場を真似すればいい。

ライターが記事を書く → 編集者が「ここ薄い」「この表現微妙」と指摘 → ライターが修正 → また編集者が見る...

これをAI同士でやらせるのが今回のアプローチだ。

## Claude Code Channelsの威力

2026年3月にリリースされた「Claude Code Channels」が今回のキモ。Discord経由でローカルのClaude Codeにタスクを投げられる機能で、これが想像以上にヤバい。

```
# Claude Codeをバックグラウンドで起動
claude-code --channels discord
```

こうしておくと、Discordから「記事書いて」「コード修正して」「デプロイして」みたいな指示を送れる。しかもMCPサーバー経由でSupabaseやGitHub Actionsとも連携できる。

重要なのは**ローカルで動くからAPI料金がかからない**こと。Claude Codeのサブスク内で完結する。

## システム構成：AI-A vs AI-B

今回のシステムは「2つのAIが役割分担する」設計にした。

### AI-A（司令塔）

* GitHub ActionsのCronで定期起動
* Discordに「トレンド調べろ」「記事書け」「批評しろ」と指示を投げる
* プロジェクト全体の進行管理

### AI-B（Claude Code）

* ローカルマシンで24時間常駐
* 実際の調査・執筆・推敲を担当
* Brave SearchやSupabaseのRAGデータにアクセス

この2者がDiscord上で会話しながら記事をブラッシュアップしていく流れ。

```
# AI-Aから投げられるタスクの例
async def send_task_to_discord(task_type: str, params: dict):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    payload = {
        "content": f"@claude-code {task_type}",
        "embeds": [{
            "title": f"Task: {task_type}",
            "fields": [{"name": k, "value": str(v)} for k, v in params.items()]
        }]
    }
    await httpx.post(webhook_url, json=payload)
```

## 4段階の記事生成プロセス

### 1. トレンド調査（blog\_research）

まずAI-Bが3つのソースから話題を収集する：

```
def collect_trending_topics():
    # RSSフィード監視（OpenAI、Google、Meta等）
    rss_topics = parse_tech_rss_feeds()
    
    # SNSバズ検出
    buzz_topics = analyze_social_engagement()
    
    # 過去トレンド分析
    historical_trends = query_trend_database()
    
    # バズスコア計算
    scored_topics = calculate_buzz_scores(
        rss_topics + buzz_topics + historical_trends
    )
    
    return sorted(scored_topics, key=lambda x: x.score, reverse=True)
```

各トピックに「バズスコア」を付けて、上位候補をBrave Searchで調査。「まだ誰も深く書いてない切り口」があるかチェックする。

### 2. 記事執筆（blog\_draft）

ネタが決まったら、AI-Bがデータ収集から執筆まで一気に進める：

```
async def generate_blog_draft(topic: str):
    # 自社RAG検索（重複回避）
    existing_content = await search_company_rag(topic)
    
    # 創業者の思考ログ検索
    personal_stories = await search_founder_thoughts(topic)
    
    # 外部データ収集
    research_data = await brave_search_research(topic)
    
    # 記事執筆
    draft = await generate_with_context(
        topic=topic,
        context=existing_content + personal_stories + research_data,
        target_length=20000  # 20,000文字目標
    )
    
    return draft
```

この時点ではまだ「下書き」。次の批評フェーズで改善する前提で書く。

### 3. 批評と推敲（blog\_review）

AI-Aが「この記事を批評しろ」とタスクを投げると、AI-Bが5軸で評価する：

```
def review_article(content: str) -> ReviewResult:
    checks = {
        "ai_smell": detect_ai_phrases(content),  # 「パラダイムシフト」等
        "seo_structure": analyze_heading_structure(content),
        "content_depth": measure_section_depth(content),
        "duplicate_rate": check_similarity_with_existing(content),
        "internal_links": count_company_mentions(content)
    }
    
    score = calculate_review_score(checks)
    suggestions = generate_improvement_suggestions(checks)
    
    return ReviewResult(score=score, suggestions=suggestions)
```

批評結果はDiscordに投稿され、AI-Bがそれを見て記事を修正する。

「セクション3が浅い」→ Brave Searchで追加調査  
「AI臭い表現がある」→ 口語調に書き換え  
「内部リンクが足りない」→ 自社サービスの文脈を追加

### 4. 公開とSNS展開（blog\_publish）

推敲完了後、既存のPost-Processingパイプラインに投入：

```
async def publish_article(content: str):
    # Supabaseに保存
    post_id = await save_to_database(content)
    
    # Post-Processing API呼び出し
    await trigger_post_processing(post_id)
    
    # SNS投稿生成
    social_posts = await generate_social_content(content)
    
    # 品質ゲート通過時のみ投稿
    for platform, post in social_posts.items():
        if post.quality_score >= 0.6:
            await publish_to_platform(platform, post)
```

## SNS投稿の自動最適化

記事公開と同時に、3つのプラットフォーム向けに最適化した投稿を生成：

```
def optimize_for_platform(content: str, platform: str):
    if platform == "twitter":
        return {
            "tone": "casual",
            "length": 280,
            "hook_pattern": random.choice(VIRAL_HOOKS),
            "ending": "question_based"
        }
    elif platform == "linkedin":
        return {
            "tone": "professional", 
            "length": 1500,
            "structure": "insight_to_action",
            "hashtags": 2-3
        }
    elif platform == "threads":
        return {
            "tone": "conversational",
            "length": 500,
            "ending": "open_ended"
        }
```

## 運用コスト：なぜほぼゼロなのか

| コンポーネント | コスト |
| --- | --- |
| 記事生成（Claude Code） | **ゼロ**（ローカル、サブスク内） |
| Brave Search API | 微小（記事1本あたり数回のクエリ） |
| OpenAI Embeddings | 微小（ベクトル化のみ） |
| Vercel Post-Processing | 無料枠内 |

従来のCloud Run + 外部LLM APIと比較すると、メインのLLM利用料が完全にゼロになる。

## 2日サイクルの完全自動運用

このシステムは48時間周期で自動実行される：

```
# GitHub Actions (.github/workflows/blog-generation.yml)
name: Auto Blog Generation
on:
  schedule:
    - cron: '0 9 */2 * *'  # 2日おき午前9時

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Research
        run: |
          curl -X POST ${{ secrets.DISCORD_WEBHOOK }} \
            -H "Content-Type: application/json" \
            -d '{"content": "@claude-code blog_research"}'
```

Day 1: トレンド調査 → 執筆 → 批評・推敲  
Day 2: 公開 → SNS展開

月15本の記事が人間の介入なしで生成される。

## 実装で学んだこと

### 1. 批評の具体性が命

AI同士の対話で最重要なのは「具体的な指摘」。

❌ 悪い例：「もっと良くして」  
⭕ 良い例：「セクション3のデータが2024年で古い。2026年3月の最新データに更新しろ」

### 2. 人間性の注入テクニック

AI記事が「AI臭い」理由は構造の均一性。対策として：

```
def humanize_content(text: str):
    # 段落の長さをランダム化
    text = vary_paragraph_lengths(text)
    
    # 独り言や括弧内コメントを挿入
    text = add_casual_comments(text)
    
    # 断定を避ける表現に変換
    text = soften_assertions(text)
    
    return text
```

### 3. 既存インフラの最大活用

新規作成したのは「ループハンドラ4つ」だけ。Post-Processing、RAG、構造化データ生成は全て既存システムを再利用した。

## まとめ

「AIに1発で完璧な記事を書かせる」のをやめて、「2つのAIに段階的に改善させる」アプローチに変えた結果：

* 記事品質が明確に向上（体感2倍以上）
* LLM API料金がゼロに
* 月15本の安定した記事生産
* SNS展開まで完全自動化

Claude Code Channelsの登場で、「AIエージェントが24時間働いてコンテンツを生産し続ける」世界が現実になった。

正直、ここまでできるとは思ってなかった。

詳細な実装手順はこちら → <https://nands.tech/posts/claude-code-ai-to-ai-blog-auto-generation-714286>
