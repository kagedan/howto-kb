---
id: "2026-06-12-claude-fable-5が黙って性能を下げる仕様anthropicが2日で撤回-01"
title: "Claude Fable 5が黙って性能を下げる仕様、Anthropicが2日で撤回"
url: "https://zenn.dev/okssusucha/articles/20260612-claude-fable5-invisible-safeguards-revers"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "zenn"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

# Claude Fable 5が黙って性能を下げる仕様、Anthropicが2日で撤回

モデルのシステムカードを隅まで読む人は少ない。でも今回ばかりは、読んだ人が勝った。

6月9日にリリースされたAnthropicの新フラッグシップ [Claude Fable 5](https://www.anthropic.com/news/claude-fable-5-mythos-5) について、開発者のJonathan Ready氏が[システムカード](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf)の中に妙な記述を見つけた。フロンティアLLM開発に関するリクエスト、具体的には事前学習パイプラインの構築、分散学習インフラ、MLアクセラレータ設計などを検知した場合、モデルが「ユーザーに見えない形で」回答の質を落とす、と書いてあったのだ。

> these safeguards will not be visible to the user. Fable 5 will not fall back to a different model. Instead, the safeguards will limit effectiveness through methods such as prompt modification, steering vectors, or parameter-efficient fine-tuning

エラーを返すのでも、拒否するのでもない。プロンプト改変やステアリングベクトルで、Fable 5のまま黙って出力を劣化させる。Ready氏はこれを「Claudeがあなたのアプリを妨害してもあなたは気づけない」と表現した。発見の経緯は本人のポストに詳しい。

<https://jonready.com/blog/posts/claude-fable5-is-allowed-to-sabotage-your-app-if-youre-a-competitor.html>

## 🙈 「見えない劣化」が一番まずい理由

正直なところ、フロンティアモデルの蒸留や複製を防ぎたいというAnthropicの動機自体は理解できる。問題は実装の選び方だ。

サイバーセキュリティや生物兵器関連のリクエストに対して、AnthropicはもともとOpus 4.8への「見える」フォールバックを使っていた。検知されればユーザーに通知が出る。ところがフロンティアLLM開発だけは不可視方式が選ばれた。Anthropicの推計では影響はトラフィックの約0.03%。数字だけ見れば誤差だが、この0.03%は「分散学習を組む人」「アクセラレータ向けにカーネルを最適化する人」に集中する。そして2026年の今、その作業はフロンティアラボの専売ではない。普通のスタートアップがvLLMを改造し、自社データで継続事前学習を回す時代に、「フロンティアLLM開発」と「ただの仕事」の境界は分類器が引けるほど明確ではない。

エンジニアとして一番嫌なのは、デバッグ不能になることだ。モデルの回答が悪いとき、それがモデルの限界なのか、プロンプトのせいなのか、それとも見えない介入なのか、区別する手段がない。LLMを開発ツールチェーンの一部として使うというのは、コンパイラを信頼するのと同じ種類の信頼をベンダーに預けることで、「特定の入力でコンパイラが黙って最適化を弱める」仕様はその信頼を根本から壊す。

## 48時間後の方針転換

批判は速かった。Wiredが[6月11日に調査記事](https://www.wired.com/story/anthropic-responds-to-backlash-on-claudes-secret-sabotage-on-ai-research/)を出し、[Simon Willison氏](https://simonwillison.net/2026/Jun/11/anthropic-walks-back-policy/)ら開発者コミュニティの著名人が問題を整理した。同日、Anthropicは[@ClaudeDevsの公式声明](https://twitter.com/claudedevs/status/2064949876463645026)で方針を撤回する。

> We made the wrong tradeoff and we apologize for not getting the balance right.

声明によれば、不可視方式を選んだ理由は「狭くターゲットでき、誤検知をほぼゼロにしたまますぐ出荷できる。見えるセーフガードは探られて(probed)ジェイルブレイク耐性を固める時間が必要になる」というものだった。リリース速度のために透明性を捨てた、と自分で認めた形だ。修正後の挙動はこうなる。

|  | 修正前(6/9〜) | 修正後(6/11発表) |
| --- | --- | --- |
| 検知時の挙動 | Fable 5のまま出力品質を低下 | Opus 4.8へフォールバック |
| ユーザー通知 | なし | あり(cyber/bioと同方式) |
| APIレスポンス | 通常応答と区別不可 | 拒否・フォールバック理由を返す |
| 誤検知 | 非常に少ない(狭い網) | 短期的に増える見込み |

ロールアウトはサーバーサイドで数日かけて行われるとしている。

## タダでは直らない

注目すべきは、Anthropic自身が告知している副作用だ。セーフガードを可視化すると、どこで発動するかを攻撃側が試行錯誤できるため、分類器の網を広げざるを得ない。結果として、正当なML研究のリクエストが誤ってOpus 4.8に落とされるケースが短期的に増える。[Decryptの記事](https://decrypt.co/370831/anthropic-apologizes-claude-fable-5-secret-censorship)はここを「修正にはcatchがある」と指摘していて、実際、これから数週間はFable 5で学習インフラ系の質問をしていて急にOpus 4.8に切り替わる経験をする人が出るはずだ。少なくとも今度は「切り替わった」と分かる。それが本質的な前進だと思う。

実務側で取れる対策は地味だが明確で、ベンダー製LLMをパイプラインに組み込むなら自前の回帰evalを持つこと。モデルバージョン固定だけでは不十分だというのが今回の教訓で、同じモデルIDでもサーバーサイドの介入で挙動は変わり得る。出力品質の定点観測があれば、不可視の介入もノイズからの逸脱として検出できる可能性が上がる。

最後にひとつ引っかかりを残しておくと、今回「見える」ようになったのは、Anthropicが見せると決めた介入だけだ。システムカードに書かれていたからこそ発見され、撤回までつながった。逆に言えば、ドキュメントに書かれない介入を外部から検証する手段を、私たちはまだ持っていない。モデルカードを最後まで読む習慣は、当面やめないほうがいい。
