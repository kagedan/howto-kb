---
id: "2026-06-28-flutterとclaude-apiで麻雀のどれを切るクイズアプリを作った話-01"
title: "FlutterとClaude APIで麻雀の「どれを切る？」クイズアプリを作った話"
url: "https://zenn.dev/yuen/articles/7fbb50504ec5d2"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "zenn"]
date_published: "2026-06-28"
date_collected: "2026-06-29"
summary_by: "auto-rss"
query: ""
---

## はじめに

今回はかなり趣味的な開発話です。

麻雀を覚えたばかりの人が「もっと練習したい」と思ったとき、ちょうどいい練習アプリってなかなかないんですよね。  
というわけで、「どれを切ればいいか」を3択で答えるクイズアプリを、FlutterとClaude APIを組み合わせて作ってみました。

### 作ったもの

* 100問出題する「どれを切る？」クイズアプリ
* 固定問題50問（JSONで管理）＋Claude API生成50問の混合方式
* 3択形式で最善の打牌を選ぶと、正誤フィードバックと解説が出る
* 牌はUnicode絵文字（🀇🀈🀉…）で視覚的に表示

---

## 技術スタック

| 用途 | 採用技術 |
| --- | --- |
| フレームワーク | Flutter 3.x |
| 状態管理 | Riverpod |
| API通信 | http |
| APIキー管理 | flutter\_dotenv |
| スコア保存 | shared\_preferences |
| 問題生成AI | Claude API（claude-sonnet-4-6） |

---

## アプリの構成

問題の種類は2つあります。

**固定問題（50問）**：`assets/questions.json`にあらかじめ定義しておいたものです。beginner / intermediate / advanced にバランスよく分けて、麻雀の基本パターンをひととおり網羅するようにしました。

**AI生成問題（50問）**：Claude APIを叩いて起動時に動的生成します。毎回違う問題が出てくるので、繰り返し遊んでも飽きにくいのがポイントです。

```
// questions.json の1問のフォーマット
{
  "id": "fixed_001",
  "title": "基本的なターツ選択",
  "hand": ["1m","2m","3m","4m","5m","1p","2p","3p","7s","8s","9s","南","南","東"],
  "choices": ["4m", "南", "東"],
  "answer": "東",
  "explanation": "南は対子でトイツ候補になる。萬子・筒子はターツや順子として機能している。孤立した東から切るのが基本。",
  "difficulty": "beginner"
}
```

---

## こだわったところ：「場の状況」をどう表現するか

設計で一番頭を使ったのが、**麻雀の「場の状況」をデータとして表現してAIに伝える**部分でした。

麻雀の打牌判断って、手牌だけで決まるわけじゃないんですよね。捨て牌の流れ、ドラ情報、リーチの有無、残り枚数…いろんな要素が絡んできます。それをどうAIプロンプトに落とし込むか、Claude Codeを使いながら実装しました。

### コンテキストをプロンプトに構造化して渡す

場の状況を構造化してプロンプトに渡すことで、問題の質を担保しています。

```
// ai_question_service.dart（抜粋）
String _buildSystemPrompt() {
  return '''
あなたは麻雀の問題作成の専門家です。
「どれを切る？」問題をJSON形式で生成してください。

出力形式（JSON配列）:
[{
  "hand": ["1m","2m",...],  // 14枚の手牌（ツモった状態）
  "choices": ["X","Y","Z"], // 3択（正解を含む）
  "answer": "Z",            // 正解
  "explanation": "..."      // 50字程度の解説
}]

制約:
- 手牌は必ず14枚（ツモった状態）
- choicesは手牌に含まれる牌のみ
- answerはchoicesの中の1つ
- 難易度をmixed（初級・中級・上級）で生成
- 数牌表記: 1m〜9m(萬), 1p〜9p(筒), 1s〜9s(索)
- 字牌表記: 東南西北白發中
''';
}
```

ポイントは「制約を明示的に書く」こと。特に「choicesは手牌に含まれる牌のみ」というルールを入れておかないと、手牌にない牌が選択肢に混入するバグが普通に発生しました。AIといえども雑に扱うとちゃんとズレてきますね。

### バリデーションは必須です

AIのレスポンスが必ずしも正しいJSONになるとは限らないので、パースエラーや手牌が13枚でないケースに備えたバリデーションを入れています。

```
List<Question> _validateAndParse(String jsonStr) {
  final List<dynamic> raw = jsonDecode(jsonStr);
  return raw
    .where((q) => (q['hand'] as List).length == 14)
    .where((q) => (q['choices'] as List).length == 3)
    .where((q) => (q['choices'] as List).contains(q['answer']))
    .map((q) => Question.fromJson(q))
    .toList();
}
```

API失敗時は固定問題からランダムに補完するようにしているので、クラッシュはしません。

---

## 牌のUnicode表現

牌の表示はUnicode絵文字（U+1F000番台）を使っています。

```
// utils/tile_emoji.dart
const Map<String, String> tileEmojiMap = {
  '1m': '🀇', '2m': '🀈', '3m': '🀉', '4m': '🀊', '5m': '🀋',
  '6m': '🀌', '7m': '🀍', '8m': '🀎', '9m': '🀏',
  '1p': '🀙', '2p': '🀚', '3p': '🀛', '4p': '🀜', '5p': '🀝',
  '6p': '🀞', '7p': '🀟', '8p': '🀠', '9p': '🀡',
  // 字牌...
};
```

ただ、端末やフォントによって表示が崩れることがあるんですよね。なのでテキストフォールバック（「一萬」「二筒」など）も一緒に実装しておきました。Android実機でテストしたら絵文字が豆腐になったことがあって、このフォールバックに助けられました。

---

## 状態管理：Riverpodで問題フローを管理

クイズの進行状態はRiverpodで一元管理しています。

```
// providers/quiz_provider.dart（抜粋）
class QuizState {
  final List<Question> questions;
  final int currentIndex;
  final int score;
  final String? selectedAnswer;
  final bool isAnswered;
  final QuizPhase phase; // loading / playing / feedback / completed
}
```

`QuizPhase`で画面の状態を明確に区別したことで、UIのちらつきや二重回答のバグを防げました。「フィードバック表示中」と「次の問題に移行中」の間のボタン操作まわりが特にスッキリしたと感じています。

---

## スコアとランク

100問終了後にスコアとランクを表示します。

| スコア | ランク |
| --- | --- |
| 90〜100 | SS（雀聖） |
| 80〜89 | S（雀士） |
| 70〜79 | A（上級者） |
| 50〜69 | B（中級者） |
| 〜49 | C（初心者） |

スコアは`shared_preferences`でベストスコアを保存して、ホーム画面にも表示しています。

---

## 振り返り

### うまくいったこと

* **Claude APIの問題生成**は想定以上に品質が高くて、プロンプトをちゃんと書けばほぼ正しい麻雀問題が生成できました
* **Riverpodによる状態管理**は、クイズのような「フェーズ遷移が多いUI」にとても相性がよかったです
* **固定問題＋AI生成のハイブリッド方式**は、初回起動時のローディングを最小限にしつつ問題の多様性も確保できて、バランスがよかったと思います

### 次やるなら変えたいこと

* **問題のキャッシュ**をローカルに持てるようにして、オフラインでも遊べるようにしたいです
* **難易度選択**をユーザー側で選べるようにすると、初心者から上級者まで幅広く使ってもらえそうだなと思っています

---

## おわりに

FlutterとClaude APIを組み合わせることで、問題コンテンツの生成をAIに任せながらクイズアプリを作ることができました。「AIに問題を作らせる」というアプローチは、麻雀のような専門知識が必要なドメインでも十分使えると感じています。

同じように「専門知識系クイズアプリ」を作ってみたい方の参考になれば嬉しいです！
