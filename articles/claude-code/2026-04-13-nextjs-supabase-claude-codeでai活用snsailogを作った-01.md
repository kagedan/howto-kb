---
id: "2026-04-13-nextjs-supabase-claude-codeでai活用snsailogを作った-01"
title: "Next.js + Supabase + Claude CodeでAI活用SNS「ailog」を作った"
url: "https://zenn.dev/mukkimuki/articles/5283ad6efa2737"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

## 作ったもの

AI活用の記録をシェアできるSNS「ailog」を作りました。

<https://www.ailoggg.com>

ChatGPTやClaudeを使ってみた記録、AI副業の実践ログ、AIでアプリを作った話など、AIに関する「やってみた」を投稿できるサービスです。

## 技術スタック

* **フロントエンド**: Next.js 15 (App Router)
* **バックエンド/DB**: Supabase (PostgreSQL + Auth + Storage)
* **ホスティング**: Vercel
* **開発支援**: Claude Code
* **ドメイン**: XServer Domain

## なぜこの構成にしたか

個人開発で速く出すことを優先しました。

**Next.js (App Router)** はSSRとAPI Routeが1プロジェクトで完結するので、フロントとバックエンドを分ける必要がない。

**Supabase** は認証・DB・Storageが一つのダッシュボードで管理できて、PostgreSQLのRLS（Row Level Security）でセキュリティもDB層で制御できる。個人開発の無料枠としても十分。

**Claude Code** は開発の工程で大活躍。

## 主な機能と実装

### 認証（Supabase Auth + Google OAuth）

Supabase AuthのGoogle OAuthを使用。`@supabase/ssr` でサーバーサイドのセッション管理をしています。

認証後のコールバックで `public.users` テーブルにユーザーレコードを作成するトリガーを設定しています。

### 投稿（300文字 + 画像2枚）

投稿テキストは300文字以内。画像は最大2枚まで添付可能。

`posts` テーブルに `image_urls text[]` カラムを持たせて、画像の公開URLを配列で保存する設計にしました。

### OGPリンクプレビュー

投稿内のURLを検出して、OGP情報（タイトル・説明・サムネイル）をカード表示する機能。

実装はNext.jsのAPI Route (`/api/ogp`) でサーバーサイドからOGPを取得。CORSの問題を回避しつつ、取得結果は `ogp_cache` テーブルにキャッシュして7日間再利用しています。

### 他コンテンツ

3つの質問に答えるだけで、用途に合ったAIツールを提案するフローチャート形式の診断機能やらAIチャットボットと話すだけで要件定義まとめてくれるツールやらを置いてます。基本的に便利になるツールを作っておいておきたいなって思ってます。

## Claude Codeでの開発

今回の開発ではClaude Codeをかなり使い込みました。

やったこととしては：

* 機能要件をプロンプトにまとめてClaude Codeに渡し、実装してもらう
* DB設計（テーブル構造、RLSポリシー）もプロンプトに含める
* Supabaseの既存構造を調べてプロンプトに記載し、整合性を保つ

うまくいったポイント：

* **既存の構造を正確に伝える**ことが重要。テーブル定義、既存の環境変数、使っているライブラリのバージョンなどをプロンプトに含めると、整合性のあるコードが出てくる
* **1機能1プロンプト**で依頼する。複数機能を一度に頼むと抜け漏れが出やすい
* **完成イメージを具体的に書く**。UIの挙動やエラーハンドリングまでプロンプトに書くと、手戻りが減る

## 今後やりたいこと

* プロンプトテンプレート集ページの追加
* AI活用チャレンジ（デイリーお題）機能
* Google Analytics導入
* SEO強化（ブログ機能の追加）
* コンテンツ追加etc

## まとめ

Next.js + Supabase + Claude Codeの構成は、個人開発でSNS的なサービスを作るには十分すぎる組み合わせでした。特にSupabaseのRLSとStorageの組み合わせは、セキュリティを気にしつつも開発速度を落とさないので便利です。

興味があれば使ってみてください。

<https://www.ailoggg.com>
