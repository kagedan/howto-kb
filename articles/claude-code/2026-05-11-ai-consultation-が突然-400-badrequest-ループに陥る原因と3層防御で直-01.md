---
id: "2026-05-11-ai-consultation-が突然-400-badrequest-ループに陥る原因と3層防御で直-01"
title: "AI consultation が突然 400 BadRequest ループに陥る原因と、3層防御で直した話"
url: "https://zenn.dev/zoetaka38/articles/2328ea1c852dee"
source: "zenn"
category: "claude-code"
tags: ["prompt-engineering", "API", "AI-agent", "OpenAI", "Gemini", "zenn"]
date_published: "2026-05-11"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

ある朝、ユーザーから「AI 相談が壊れてます」という報告が来ました。Codens Green の Consultation 機能、要は Claude と何往復もしながら PRD のネタを詰めていくチャット UI なんですが、特定の 1 ユーザーの 1 会話だけ、新しいメッセージを送るたびに 400 BadRequest が返ってくる、という現象でした。

最初に疑ったのは ANTHROPIC\_API\_KEY です。鍵がローテーションされて環境変数が古いままなんじゃないか、と。でも他のユーザーの consultation は全部問題なく回ってる。じゃあその会話の DB 行が壊れたのか、と消えていない fk を辿って覗いてみたら、見た目は綺麗。`messages` カラムには user / assistant の往復が普通に並んでる。

なのに、新しい user message を 1 行追加してリトライさせると、必ず 400 で落ちる。

## 1 件の空 assistant message が会話を「毒」にしていた

詳しく見たら、`messages` の中に 1 件、`content` が空文字列の assistant message が混ざっていました。10 番目あたりに 1 件だけ、ぽつんと。

Codens Green の consultation は、API call のたびに会話履歴全体を Claude API に投げ直しています。stateless にしているのは別の理由ですが、その結果、過去のメッセージが 1 件でも壊れていると、それ以降の全 call が同じ理由で死に続けるという構造になっていました。

Claude API の Messages 仕様では、各 message の `content` は空であってはいけません。空 string を渡すと `invalid_request_error` で弾かれる。仕様としては当然なんですが、当時のコードは Consultation エンティティの `get_messages_for_ai()` で愚直にこう書いていました。

```
def get_messages_for_ai(self) -> List[Dict[str, str]]:
    """AI API用のメッセージリストを取得"""
    return [
        {"role": msg.role.value, "content": msg.content}
        for msg in self.messages
    ]
```

履歴に空の content が混ざっていたら、そのまま payload に詰めて投げる。Claude API は 400 を返す。次にユーザーがメッセージを足してリトライしても、履歴に同じ空メッセージが残っているから同じ 400。**会話が永遠に詰む**という状態でした。

dashboard で見ると「Claude API への call が intermittent に失敗している」ようにしか見えない。でも本当の原因は「2 日前にこの会話の中で 1 件だけ空 assistant が保存された」という、ログには残らない過去の事件でした。実際 SELECT で当該 row の JSON を覗くまで分からなかった。

> ここで気持ち的にしんどかったのは、CloudWatch の API ログにも Sentry にも「直前の call が空 content を保存した」という痕跡が綺麗には残っていないこと。assistant message が空でも success として書き込まれていた、っていうのは穏やかじゃないですよね。

ちなみに、なぜ「DB の中身を SELECT して気づくまで」時間がかかったかというと、API のレスポンス側のログには `{"status": "ok", "message_id": "..."}` がちゃんと残っていたからです。「保存は成功している」「次の call で死ぬ」、この 2 つが地続きに見えなくて、ぱっと見「Claude API 側のたまの不調か？」というミスリードに引っかかっていました。空 content を弾くガードがないと、自分のコードが自分の未来を破壊しているのに、ログ上は他人事に見える。

## どうして空メッセージが DB に保存されたのか

辿っていくと、原因は `claude_client.py` の `generate_consultation_response()` にありました。

Claude API はごく稀に、`content` ブロックの中の `text` が空、あるいは tool\_use ブロックだけが返ってきて text content が事実上空、という response を返してくることがあります。レアな条件です。長すぎる context、特定の system prompt との組み合わせ、network の中途半端な切断、いろんな要因が考えられるんですが、頻度的には数千 call に 1 件あるかどうか。

そのとき、Codens Green のコードは text\_content をそのまま `.strip()` もせずに

```
ai_response = ai_result["response"]   # ← 空 string が入ってる
consultation.add_assistant_message(ai_response, metadata=...)
```

として add してました。空 string でも、entity 側で「空はダメ」というガードが特にないので、そのまま `messages` 配列に append されて DB に書き込まれる。次の write は普通に往復するので、UI 上は「AI が黙って 1 ターン無視した」ような見え方になります。ユーザーが「あれ、返事こなかったかな」と感じてもう一度送る。すると履歴に空メッセージが残ったまま新しい user message が乗るので、ここからずっと 400 ループに突入する、という流れ。

なので発生条件としては薄いんですが、性質が悪いのは

* 一度起きると **その consultation はもう自力では復旧できない**
* ユーザーから見ると「壊れた」「サポートに連絡」レベルの impact
* ログには成功っぽく見える、404 ではなく 400 なので alert にも引っかかりにくい

という、いやらしい組み合わせでした。

## 3 層防御で直す（ただし「本丸」は 1 層だけ）

直しは PR #315 と #316 に分けて入れました。やったことは大きく 3 つ。layer 1 / layer 2 / layer 3 と呼んでいます。

最初は「layer 1 の inbound filter だけ入れて、空メッセージは AI に投げない」で済ますつもりでした。それだけでループは止まるので。でも書きながら気づいたんですよね、layer 1 だけだと「すでに DB に入ってしまった空メッセージへの絆創膏」にしかならない。**根本原因（=空 response が assistant として保存される）は治っていない**から、レアな条件で再発する。

そこで、本当に効く layer 2 を足しました。layer 1 はあくまで保険、という構成です。

### Layer 1: inbound filter（保険）

`get_messages_for_ai()` の return list から、空 content の message を除外します。SYSTEM role は元々除外していたので、それに条件を足す形。

```
def get_messages_for_ai(self) -> List[Dict[str, str]]:
    return [
        {"role": msg.role.value, "content": msg.content}
        for msg in self.messages
        if msg.role != MessageRole.SYSTEM
        and msg.content
        and msg.content.strip()
    ]
```

これで、過去にすでに保存されてしまった空 assistant message があっても、API へは送られなくなります。既存の壊れた consultation を自動的に救済できる、というのが大きい。

### Layer 2: outbound detection（本丸）

`claude_client.py` の `generate_consultation_response()` で、Claude からの response の text\_content が空だったら **例外を投げる**ようにしました。

```
text_content = "".join(
    block.text for block in response.content if hasattr(block, "text")
)
if not text_content.strip():
    raise ValueError("No text content in Claude API response")
```

ValueError を上で catch して、ユーザーには「AI からの応答の生成中にエラーが発生しました。しばらく待ってから再度お試しください」という汎用 message を返す。**空メッセージは絶対に DB に書き込まれない**、というのがポイントです。

これが本当の fix。layer 1 はあくまで「すでに汚染された会話の救済」のためで、こっちは「そもそも汚染を発生させない」ためのものです。

書いてて思ったのは、API response の validation って軽視されがちなんですよね。「成功 status code が返ってきたんだから success だろう」と扱いがちなんだけど、AI 系の API は「200 だけど content が空」みたいなのが普通にあるので、保存前に必ず 1 段挟まないといけない。これ Claude に限らず、OpenAI でも Gemini でも同じだと思います。

### Layer 3: 履歴を 40 件に切る（別件、ついでに）

これは厳密にはこの bug とは別の話なんですが、同じタイミングで入れました。`AddMessageUseCase` の中で、API に送る前に履歴を直近 40 件（user/assistant 合わせて）に絞っています。

```
MAX_HISTORY = 40
if len(messages) > MAX_HISTORY:
    messages = messages[-MAX_HISTORY:]
    while messages and messages[0]["role"] != "user":
        messages = messages[1:]
```

なぜここに入れたか。Consultation は長い人だと 50 〜 70 ターンを超えてくることがあって、毎 call で全履歴を投げると context window と料金の両方が痛い。あと、Claude API は messages 配列の先頭が `user` role である必要があります。truncate しただけだと、運悪く先頭が assistant になることがあるので、user が出てくるまで頭から削る、というガードを足しています。

これも 400 BadRequest を引き起こす別経路だったので、ユーザー視点では「長い会話で API call が落ちる」という同じ症状に集約されます。だから同じ PR 群でまとめて出す判断にしました。fix そのものは互いに独立ですが、release notes 的には「長い consultation での failure を 3 種類まとめて潰した」と書いた方がユーザーに伝わるので。

なので 3 層と言いつつ、内訳は

| 層 | 役割 | このバグへの貢献 |
| --- | --- | --- |
| Layer 1 (inbound) | 履歴の空 message を AI に投げない | 既存汚染会話の救済 |
| Layer 2 (outbound) | 空 response を保存させない | 根本 fix |
| Layer 3 (truncation) | 履歴を 40 件に切る + 先頭 user 保証 | 別件、ついで |

こんな配分です。Layer 2 だけで bug としては閉じてます。

## 副産物：既に壊れていた会話の救出

既に DB に空メッセージが居座っている consultation が現時点で何件あるのか。これは別途調査しました。サポートに連絡してきたのが 1 件、ログを掘って当該 row を確認できたのが数件、というレベル感。

ここで選択肢が 2 つあって、

1. data migration を書いて、空 content の message row を DB から削除する
2. 何もしない。layer 1 が AI に送るときに弾くので、新しい往復は普通に通る

迷ったけど、2 にしました。理由は、

* migration を書くと、user 側から見えていた「履歴に空ターンが 1 個あった」という事実そのものは消える。これは UX 的にはむしろ違和感が出る可能性がある（「あれ、前回送ったやつ消えた？」）
* layer 1 で吸収できているなら、新しい会話は普通に進む。古い空ターンは UI 上「(空)」として表示されるだけで、機能的には害がない
* そもそも数が少ない

要は「過去の歴史は書き換えない、未来の挙動だけ直す」という方針。Migration は壮大に書くと壮大に壊れるので、本当に必要なときだけにしたい、というのもありました。

## 学び：AI agent の health = 会話履歴の health

今回のバグ、しんどかったポイントは「壊れている根拠が DB の 1 セルにしかない」というところでした。ログを掘っても出てこないし、コードを読んでも一見何も悪く見えない。Claude API の error message も「invalid messages」みたいな割と汎用なやつなので、ピンポイントには指さない。

一般化すると、stateful っぽく見える AI 会話 UI って、実態は「履歴を毎回 stateless に投げ直す」設計になっていることが多いです。その瞬間、過去の入力が 1 件でも壊れていると、未来の全 call が連鎖的に壊れる。これは普通の REST API では起きにくい failure mode で、AI 系ならではです。

なので、入出力の境界で「空 / 不正な data は通さない」を二重にやる必要がある。

* 入口（送る前）に filter があるか
* 出口（保存する前）に validation があるか

このどちらか片方しかないと、今回のように **過去の事故が未来を呪う**事態が起きる。両方あって初めて、「過去がもし汚染されていても新しい往復は健全」「これから新たな汚染は発生しない」という二重の保証になる、というのが今回の学びでした。

それと、release を急ぐと layer 1 だけで満足してしまいたくなる衝動がある。「とりあえずループは止まったし」って。でも layer 1 は症状を隠す薬で、layer 2 を入れないと病気は治っていない。書きながらこの判断を間違えそうになったので、ここは自戒として残しておきます。

Codens Green は「ビジネスサイドの自由記述を AI が PRD に構造化する」プロダクトで、こういう Consultation 系のエラーモードに毎週のように遭遇しながら直しています。興味があれば [Codens](https://www.codens.ai/) を覗いてみてください。
