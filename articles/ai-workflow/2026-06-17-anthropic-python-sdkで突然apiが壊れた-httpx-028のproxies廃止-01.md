---
id: "2026-06-17-anthropic-python-sdkで突然apiが壊れた-httpx-028のproxies廃止-01"
title: "Anthropic Python SDKで突然APIが壊れた — httpx 0.28のproxies廃止という地雷"
url: "https://zenn.dev/takano2026/articles/fe33d9d1a3f70b"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Python", "zenn"]
date_published: "2026-06-17"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude APIを使った業務アプリを運用していたら、ある日突然こんなエラーが出ました。

```
Client.__init__() got an unexpected keyword argument 'proxies'
```

コードは一切変更していません。デプロイ環境を再ビルドしただけです。  
原因の特定に少し時間がかかったので、同じ問題に遭遇する方のために記録を残します。

## 何が起きたか

私たちは領収書をスマホで撮影し、Claude Vision（Sonnet 4.6）でOCR→自動仕訳するFlaskアプリを運用しています。Railway上でPython + anthropic SDK（0.39.0固定）で動かしていました。

ある日、Railwayの再ビルドが走った後、OCR機能が完全に停止。エラーログを見ると冒頭のメッセージ。

## 原因：httpx 0.28の破壊的変更

anthropic Python SDK（バージョン0.39.0時点）は、内部でHTTPクライアントとして`httpx`を使っています。`Anthropic()`クライアントを生成する際、`httpx.Client`に`proxies`引数を渡していました。

ところが、**httpx 0.28で`proxies`引数が廃止**されました（`proxy`に一本化）。

```
# httpx 0.27.x まで → OK
httpx.Client(proxies=...)

# httpx 0.28.0 以降 → TypeError
httpx.Client(proxies=...)  # unexpected keyword argument
```

`requirements.txt`で`anthropic==0.39.0`を固定していても、`httpx`のバージョンを固定していなかったため、再ビルド時に最新のhttpx 0.28+がインストールされ、爆発しました。

## 解決策

`requirements.txt`にhttpxのバージョンを明示的に固定します。

```
anthropic==0.39.0
httpx==0.27.2
```

これだけです。

## 教訓：間接依存もピン留めせよ

今回の学びは3つ：

1. **直接依存だけでなく、重要な間接依存もバージョン固定する**。`pip freeze > requirements.txt`で全量を固定するか、少なくともHTTPクライアントのような基盤ライブラリは明示する
2. 2. **再ビルド = 再現性の敵**。コードを変えなくても、依存の解決結果が変わればアプリは壊れる
   3. 3. **同じSDKバージョンを使っている他のアプリも確認する**。実際、同じanthropic 0.39.0を使っていた名刺OCRアプリでも同様の問題が潜伏していたため、横展開で事前修正できました
      4. ## anthropic SDKの最新版では？
   4. 最新のanthropic SDK（0.40.0以降）ではhttpx 0.28対応が入っている可能性があります。SDKを最新に上げるのも選択肢ですが、破壊的変更のリスクを考えると、動いているバージョンを固定する方が運用上は安全です。
3. 特にProduction環境では「動くものを壊さない」が最優先。バージョンアップは検証環境で確認してからにしましょう。

## おわりに

Claude Vision APIは領収書OCRの精度が非常に高く、適格請求書番号（T+13桁）まで正確に読み取ってくれます。ただ、こうした依存関係の地雷は定期的に踏むので、デプロイの再現性には気を配りましょう。

同じ問題に遭遇した方の参考になれば幸いです。

---

*この記事は、一般社団法人日本量子コンピューティング協会（JQCA）の開発チームが業務中に遭遇した問題と解決策を共有するものです。*
