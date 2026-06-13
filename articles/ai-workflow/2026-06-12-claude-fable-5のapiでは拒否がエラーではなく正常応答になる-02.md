---
id: "2026-06-12-claude-fable-5のapiでは拒否がエラーではなく正常応答になる-02"
title: "Claude Fable 5のAPIでは「拒否」がエラーではなく正常応答になる"
url: "https://qiita.com/okssusucha/items/584b549f01d36baf7524"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "Python", "qiita"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

`stop_reason: "refusal"`。エラーではなくHTTP 200の正常応答として、モデルが回答を断ってくる。Anthropicが6月9日にリリースしたClaude Fable 5のAPIドキュメントを読んでいて、最初に手が止まったのがこの仕様だった。

今回のリリースは「1つのモデルを2つの製品として出す」という珍しい構成になっている。一般提供されるClaude Fable 5と、限定提供のClaude Mythos 5は同一のモデルで、違いは安全分類器(safety classifier)の有無だけ。Mythos 5は米政府と連携するProject Glasswing経由で、サイバー防御や重要インフラの事業者にのみ提供される。価格はどちらも入力$10/M、出力$50/Mトークンで、コンテキストは1Mトークン、最大出力は128kトークン。公式発表は https://www.anthropic.com/news/claude-fable-5-mythos-5 にある。

性能面の主張(ほぼ全ベンチマークでSoTA、Stripeでの大規模コードベース移行事例など)はベンダー発表なので割り引いて読むとして、エンジニアとして無視できないのはAPI統合の作り方が変わる点のほうだ。以下、APIドキュメント( https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5 )を基に整理する。

## 分類器が発動するとOpus 4.8が代わりに答える

Fable 5の分類器が反応するのは、サイバー攻撃・生物化学・蒸留(モデル能力の抽出)に関わるリクエストで、Anthropicによれば発動はセッション全体の5%未満。発動した場合、リクエストはエラーにならず、次点のモデルであるClaude Opus 4.8が代わりに応答する設計になっている。

課金もこの挙動に合わせて作り込まれている。出力前に拒否されたリクエストには課金されない。AWSのブログ( https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/ )によると、ストリーミングの途中でブロックされた場合は、そこまでがFable料金、以降がOpus料金という按分になる。フォールバック時のレスポンスはOpus価格で請求されるので、「高いモデルに投げたのに安いモデルが答えたぶんまで高く払う」ことはない。地味だが、従量課金の監視をしている側としてはありがたい配慮だと思う。

## 統合側で必要になる3つの変更

ドキュメント自身が「統合には3つの変更を計画せよ」と明言している。refusalのレスポンスハンドリング、別モデルへのリトライ、新しい課金ルールの3つだ。

冒頭に書いた通り、拒否はHTTP 200で返る。つまり既存の例外ハンドラやリトライミドルウェアには一切引っかからない。`stop_reason`を見ていないコードは、拒否応答をそのまま正常な結果として下流に流してしまう。最低限のクライアント側ハンドリングはこうなる。

```python
import anthropic

client = anthropic.Anthropic()

resp = client.messages.create(
    model="claude-fable-5",
    max_tokens=2048,
    messages=[{"role": "user", "content": prompt}],
)

if resp.stop_reason == "refusal":
    # 分類器による拒否。例外は飛ばないので自前で分岐する
    resp = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
```

手動リトライのほかに、APIに`fallbacks`パラメータを渡してサーバー側でリトライさせる方法(Claude APIとClaude Platform on AWSでベータ提供)と、各言語SDKのミドルウェアで吸収する方法が用意されている。リトライ時にはfallback creditという仕組みでプロンプトキャッシュの構築コストが返金され、モデル切り替えでキャッシュ代を二重払いしなくて済む。フォールバックを前提にした製品設計を、課金レベルまで含めてAPIに組み込んできたのは初めて見る形だ。

評価系への影響も考えておきたい。同じmodel IDを指定していても、応答したのがFable 5なのかOpus 4.8なのかでアウトプットの質は変わる。レスポンスにはどの分類器が拒否したかが含まれるので、評価パイプラインやログ基盤ではこのメタデータを必ず保存して、refusal経由の応答を分離集計できるようにしておくべきだ。そうしないと回帰テストの数字が静かに濁る。

## adaptive thinking固定で、生のCoTは返らない

Messages APIの挙動にもFable/Mythos固有の変更がある。thinkingはadaptive thinkingのみで、`thinking: {"type": "disabled"}`は指定できない。思考の深さは`effort`パラメータで制御する。さらに、生のchain of thoughtは一切返らず、`thinking.display`を`"summarized"`にすると要約が、デフォルトの`"omitted"`では空のthinkingブロックが返る。蒸留対策の分類器と合わせて、モデルの内部挙動を外に出さない方針が徹底されている。CoTをデバッグ材料にしてきたチームは、要約ベースでの観測に切り替える必要がある。

もう1点、見落とすと痛いのがデータ保持だ。Fable 5とMythos 5はCovered Modelsに指定され、全トラフィックが30日保持となり、zero data retention(ZDR)の対象外になる。学習や安全目的以外には使わないとされているが、ZDRを契約条件にしている規制業界では、現時点でFable 5を選べないケースが出るはずだ。Opus 4.8に留まるか、保持ポリシーの緩和を待つかの判断材料になる。

「能力はそのままに、安全装置の有無で製品を分割し、塞いだ穴は別モデルへのフォールバックで埋める」という今回の構成は、フロンティアモデルの提供形態として一つの型になりそうに見える。デュアルユース能力が上がるほど、この種のAPIレベルの作り込みは増えるだろう。refusalハンドリングは、これから書くLLM統合コードの標準装備として考えておいたほうがいい。
