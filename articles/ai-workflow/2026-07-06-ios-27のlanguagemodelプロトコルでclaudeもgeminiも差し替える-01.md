---
id: "2026-07-06-ios-27のlanguagemodelプロトコルでclaudeもgeminiも差し替える-01"
title: "iOS 27のLanguageModelプロトコルでClaudeもGeminiも差し替える"
url: "https://zenn.dev/okssusucha/articles/20260703-apple-foundation-models-languagemodel-pro"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Gemini", "zenn"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

iPhoneアプリにAIを組み込むとき、これまでは面倒な二択があった。端末内で完結するAppleのオンデバイスモデルは速くてプライベートだが、サイズが小さく重い推論には向かない。かといってクラウドのClaudeやGeminiを使うと、各社のSDKごとに違うリクエストの形・レスポンスの形を覚え、プロバイダを乗り換えるたびにアプリのロジックを書き直す羽目になる。

WWDC 2026でAppleが入れた `LanguageModel` プロトコルは、この二択を「一つのAPIで両方」に変える。オンデバイスモデルもClaudeもGeminiも、`LanguageModelSession` という同じ入り口の裏に差し込めるようになった。実際に7月に入ってからAnthropicとGoogleの双方が対応パッケージを公開したので、コード付きで中身を追ってみる。

## セッションはそのまま、モデルだけ入れ替わる

要点は、アプリ側が触るコードがモデルを変えてもほぼ動かない、という一点にある。Appleのオンデバイスモデルを使うときの定番はこう書く。

```
import FoundationModels

let model = SystemLanguageModel()
let session = LanguageModelSession(model: model)
let response = try await session.respond(to: "...")
```

Claudeに切り替えたいなら、Anthropicの[ClaudeForFoundationModels](https://github.com/anthropics/ClaudeForFoundationModels)（Apache 2.0、現在0.1.0のベータ）を足して、`model` に渡すインスタンスを差し替えるだけだ。

```
import FoundationModels
import ClaudeForFoundationModels

let model = ClaudeLanguageModel(
  name: .sonnet5,
  auth: .apiKey(ProcessInfo.processInfo.environment["ANTHROPIC_API_KEY"] ?? "")
)
let session = LanguageModelSession(model: model)
let response = try await session.respond(to: "Plan a 4-day trip to Buenos Aires.")
print(response.content)
```

Gemini側もGoogleが[Firebase AI Logic経由の対応](https://firebase.blog/posts/2026/06/apple-foundation-models-gemini/)を出している。パッケージが変わっても、`LanguageModelSession` を作ってから先の書き方は共通だ。

```
import FoundationModels
import FirebaseAILogic

let ai = FirebaseAI.firebaseAI()
let model = ai.geminiLanguageModel(name: "gemini-3.5-flash")
let session = LanguageModelSession(model: model)
```

`respond(to:)` の逐次版 `streamResponse(to:)`、`@Generable` を付けた型で構造化出力を受け取る書き方、`Tool` を実装してデバイス側で関数を呼ばせるツール利用まで、セッション周りの作法はプロバイダを問わず同じになる。つまり「普段はオンデバイス、重い時だけClaudeへ昇格」というエスカレーション方針を、引数一つの分岐で組める。ここが地味に効く。従来はこの昇格のためにコード経路を二本持つ必要があった。

## プロトコルは2層に分かれている

「同じAPIで差し替わる」を成立させている仕組みは、[WWDCのセッション339](https://developer.apple.com/videos/play/wwdc2026/339/)で説明されている。プロバイダが実装するのは実は2つのプロトコルだ。`LanguageModel` は自分が何をできるか（`capabilities`）と、実行器の構成（`executorConfiguration`）を宣言するだけの薄い層。実際の生成は `LanguageModelExecutor` の `respond(to:model:streamingInto:)` が担う。

面白いのはこのExecutorがストリームに流すイベントの順序が決まっていること。まずメタデータ（モデルIDやリクエストID）、次に入力トークン数などの利用量を「生成が始まる前に」報告し、そこからテキストのデルタを流す。フレームワークは `Configuration` をキーにExecutorをキャッシュするので、同じ設定のモデルを複数作っても実体は共有される。アプリ開発者はこの2層を意識せず `LanguageModel` とセッションだけ見ればいい、というのが設計の狙いだ。

## 本番に出せるのはプロキシ経由だけ

見落とすと事故る点がある。`auth: .apiKey(...)` は開発専用だ。Anthropicのドキュメントは明確に警告している。

> A key bundled into an app is extractable from the shipping binary, and anyone who extracts it can make requests billed to your account.

APIキーを埋めたアプリは配布バイナリからキーを抜かれ、あなたの請求で他人に使われる。本番では自前のバックエンドを挟む `.proxied` を使い、キーはサーバ側で付与する。Gemini側もFirebase App Checkでアプリを保護する前提になっている。要するにどちらの経路でも「クライアントに鍵を置かない」が出荷条件になる。

サーバ側ツールの扱いにも差が出る。Claudeでは、Anthropicのインフラ上で1往復のうちに走るWeb検索やコード実行を、セッションではなくモデル側に設定する。

```
let model = ClaudeLanguageModel(
  name: .sonnet5,
  auth: auth,
  serverTools: [.webSearch(maxUses: 5), .codeExecution]
)
```

三者を並べると住み分けはこうなる。

|  | オンデバイス | Claude（Anthropic） | Gemini（Firebase） |
| --- | --- | --- | --- |
| 追加パッケージ | 不要（標準） | ClaudeForFoundationModels | FirebaseAILogic |
| 通信経路 | 端末内 | アプリ→Claude API直（Appleは経由しない） | Firebase AI Logic経由 |
| 課金 | なし | Anthropicアカウント | Firebase/Google側 |
| 得意 | 軽量・オフライン・低遅延 | 大きな文脈・フロンティア推論・サーバツール | Geminiの各モデル |

## まだ0.1.0だが、賭ける方向は正しい

これは要注意の但し書き付きの技術だ。前提となるOS 27はまだベータ、Xcodeもベータ、Claude側パッケージは0.1.0でGAまでAPIが変わりうるうえ、ベータ期間中は外部PRを受け付けていない。プロンプトキャッシュの細かい制御、stop sequence、バッチ処理、トークンカウントといったMessages APIの機能はこのプロトコル越しには出てこないので、重いバックエンド処理を丸ごと載せ替える置き換えではない。あくまでオンデバイスAppのUXを底上げする層だと割り切るのが正しい。

とはいえ、Appleがモデルそのものは外部に明け渡しつつ、`LanguageModelSession` というAPIの表面だけを自分で握った、という構図は巧い。エンジニアから見た本当の価値は「iOSでClaudeが動く」ことではない。API直叩きなら前からできた。そうではなく、トランスクリプト・構造化出力・ツール呼び出しといった抽象がプロバイダをまたいで統一され、モデル選択がアプリ設計の外側の関心事になったことだ。ベンダーロックインを一段外せる。iOS 27が正式に出る頃、この上でどんな「オンデバイス既定＋必要時クラウド」のパターンが定着するかは、いま試しておく価値がある。

<https://github.com/anthropics/ClaudeForFoundationModels>
