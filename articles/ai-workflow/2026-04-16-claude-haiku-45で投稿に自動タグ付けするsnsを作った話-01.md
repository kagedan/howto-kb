---
id: "2026-04-16-claude-haiku-45で投稿に自動タグ付けするsnsを作った話-01"
title: "Claude Haiku 4.5で投稿に自動タグ付けするSNSを作った話"
url: "https://zenn.dev/mukkimuki/articles/38222e692bf8ba"
source: "zenn"
category: "ai-workflow"
tags: ["TypeScript", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

個人開発で「[ailog](https://www.ailoggg.com)」というSNSを作っています。

**「書くだけでいい。整理はAIがやる。」**——投稿するとAIが自動でタグを付け、ナレッジマップとして可視化してくれるサービスです。

この記事では、その中核機能である「AI自動タグ付け」をClaude Haiku 4.5で実装した話を書きます。実際のコード、ハマったポイント、コスト感まで含めて共有します。

## なぜ自動タグ付けが必要だったか

SNSに投稿するとき、「タグを考える」というのは地味に面倒です。Xではハッシュタグを手動で付けますし、NotionやObsidianでは自分で分類する必要があります。

私は「書くだけでいい。整理はAIがやる」というコンセプトのSNSを作りたかったので、**投稿したら裏でAIが勝手にタグを付けてくれる**仕組みが必要でした。

要件はシンプルです：

* 投稿内容から1〜3個のタグを自動生成
* 日本語で、短く一般的な単語
* 応答は1秒以内（UXを壊さない）
* コストは月$10以内に収めたい

この要件に最もフィットしたのがClaude Haiku 4.5でした。

## なぜClaude Haiku 4.5を選んだか

候補は3つありました：

| モデル | 速度 | コスト | 日本語精度 |
| --- | --- | --- | --- |
| GPT-4o-mini | 速い | 安い | 良好 |
| Gemini 2.0 Flash | 速い | 非常に安い | 良好 |
| Claude Haiku 4.5 | 速い | 安い | 優秀 |

最終的にClaude Haikuにした理由：

1. **日本語の文脈理解が優秀** — 「チャッピー」を「ChatGPT」と理解してタグ付けできる
2. **JSON出力の精度が高い** — プロンプトで「JSONで返せ」と指示すると素直に従う
3. **応答速度が速い** — 100トークン程度の出力なら1秒以内
4. **既にAnthropicのSDKを使っていた** — 他のモデルに切り替える必要がなかった

## 実装

### APIエンドポイント

Next.js App Routerの API Route として実装しました。

```
// app/api/ai/tag/route.ts
import Anthropic from '@anthropic-ai/sdk'
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

const anthropic = new Anthropic()

export async function POST(req: Request) {
  try {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { postId, content } = await req.json()
    if (!postId || !content) {
      return NextResponse.json({ error: 'Missing postId or content' }, { status: 400 })
    }

    const message = await anthropic.messages.create({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 100,
      messages: [
        {
          role: 'user',
          content: `以下のSNS投稿に最適なタグを1〜3個、JSON配列で返してください。

ルール:
- タグは日本語で、短く一般的な単語にする
- JSON配列のみを返し、他のテキストは含めない
- 投稿内容が短すぎる場合や意味が不明な場合は空配列 [] を返す

投稿: "${content}"

例: ["AI活用", "プログラミング", "学び"]`,
        },
      ],
    })

    // レスポンスからテキスト抽出
    let text = message.content[0].type === 'text' ? message.content[0].text.trim() : '[]'
    
    // マークダウンのコードフェンスを除去
    text = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim()

    let tags: string[] = []
    try {
      const parsed = JSON.parse(text)
      if (Array.isArray(parsed)) {
        tags = parsed.filter((t): t is string => typeof t === 'string').slice(0, 3)
      }
    } catch {
      console.error('AI tag parse error:', text)
    }

    // Supabaseのpostsテーブルに保存
    const { error: updateError } = await supabase
      .from('posts')
      .update({ ai_tags: tags })
      .eq('id', postId)
      .eq('user_id', user.id)

    if (updateError) {
      return NextResponse.json({ error: 'Failed to update tags' }, { status: 500 })
    }

    return NextResponse.json({ tags })
  } catch (error) {
    console.error('AI tag error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

### クライアント側（PostForm.tsx）

投稿完了後に、**fire-and-forget**でAPIを叩きます。AIタグ付けは投稿成功の必須条件ではないので、失敗しても投稿自体は成立させます。

```
// 投稿をDBにinsertした後
if (data?.id && content.trim()) {
  fetch('/api/ai/tag', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ postId: data.id, content: content.trim() }),
  })
    .then(res => res.json())
    .then(({ tags }) => {
      if (tags?.length > 0) {
        // PostCardのタグをリアルタイム更新
        if (onTagsUpdated) {
          onTagsUpdated(data.id, tags)
        }
        // トースト通知で「整理された」体験を強調
        toast.success(
          `AIがタグを付けました: ${tags.map((t: string) => '#' + t).join(' ')}`,
          { duration: 4000 }
        )
      }
    })
    .catch(() => {})
}
```

この「投稿 → バックグラウンドでタグ付け → トースト通知」の流れで、**「書いたら勝手に整理された」** という体験を作っています。

## ハマったポイント

### 1. JSONレスポンスがマークダウンで返ってくる

「JSON配列のみを返して」と指示しても、Claudeは時々以下のように返します：

```
```json
["AI活用", "プログラミング"]
```

```
これを `JSON.parse()` すると例外になります。対策として、コードフェンスを除去してからパースします：

```typescript
text = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim()
```

### 2. 空配列の処理

短すぎる投稿（「テスト」「こんにちは」等）には意味のあるタグが付けられません。プロンプトで **「短すぎる場合は空配列 [] を返す」** と明示的に指示することで、Claudeが無理にタグを生成するのを防げます。

### 3. RLS（Row Level Security）との整合性

Supabaseでpostsテーブルに対して`update`ポリシーが必要です。初期マイグレーションでは`insert`と`select`しか許可していなかったため、tag更新が失敗しました。

```
-- supabase/migrations/20260414_002_add_posts_update_policy.sql
CREATE POLICY "Users can update own posts" ON posts
  FOR UPDATE USING (auth.uid() = user_id);
```

### 4. コスト管理

Claude Haiku 4.5の価格は **Input $1 / 1M tokens, Output $5 / 1M tokens**。

1投稿あたりのトークン数は：

* Input: プロンプト（約100トークン）+ 投稿内容（最大300文字 ≈ 200トークン）= 約300トークン
* Output: 最大100トークン

1投稿あたり **$0.0008（約0.12円）** 程度。1万投稿で約1,200円。

個人開発のサービスとしては十分ペイする価格帯です。

## 改善の余地

### 1. タグの正規化

「ChatGPT」「chatgpt」「チャットGPT」が別タグとして生成されることがあります。今後は既存タグとの類似度を見て正規化するロジックを入れたい。

### 2. ユーザーの過去投稿を踏まえたタグ付け

現在は各投稿単体でタグ付けしていますが、そのユーザーが過去に使ったタグを参照すれば、より一貫性のあるタグ付けができます。Embeddingを使えば実装可能。

### 3. バッチ処理

複数投稿を1回のAPI呼び出しでタグ付けすれば、コストを削減できます。ただしリアルタイム性とのトレードオフ。

## Knowledge Mapへの発展

生成したタグは、ユーザーごとに集計して**Knowledge Map**として可視化しています。

Supabaseの`MATERIALIZED VIEW`を使って、ユーザーごとのタグ使用回数を集計：

```
CREATE MATERIALIZED VIEW user_tag_stats AS
SELECT 
  user_id,
  unnest(ai_tags) AS tag,
  COUNT(*) AS count
FROM posts
GROUP BY user_id, unnest(ai_tags);
```

これをタグクラウドとして表示することで、**ユーザーが「どの分野にどれだけ詳しくなったか」を可視化**できます。

単なるタグ付けではなく、「書くほど専門性が見える」体験を作れるのが、この実装の肝です。

## まとめ

Claude Haiku 4.5での自動タグ付けは：

* **実装が簡単**（100行程度のAPIコード）
* **コストが安い**（1投稿あたり0.12円）
* **日本語の精度が良い**
* **応答が速い**（1秒以内）

個人開発で「AIに何かを分類させたい」用途には非常にフィットします。

ailogでは、この自動タグ付けを起点に、Knowledge Map、Weekly Digest、AI Second Brain（過去の投稿にAIで質問できる機能）などを展開しています。

興味があればぜひ[ailog](https://www.ailoggg.com)を触ってみてください。書くだけでAIが整理してくれる体験を味わえます。

フィードバックやアイデアは[X (@mukkimuki343443)](https://x.com/mukkimuki343443)までお気軽にどうぞ。

## 参考
