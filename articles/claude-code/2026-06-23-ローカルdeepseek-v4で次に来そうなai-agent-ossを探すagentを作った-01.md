---
id: "2026-06-23-ローカルdeepseek-v4で次に来そうなai-agent-ossを探すagentを作った-01"
title: "ローカルDeepSeek V4で「次に来そうなAI Agent OSS」を探すAgentを作った"
url: "https://zenn.dev/kamo78/articles/ds4-local-agent-discovery"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-06-23"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

## この記事でやること

ローカルLLMの評価は、単発チャットの速度だけでは足りません。

実際にAgentとして使うなら、以下が必要になります。

* 外部情報を探す
* APIや外部処理を何度も呼ぶ
* 候補をフィルタする
* JSONなどの構造化出力を守る
* 長い文脈から根拠を拾う
* READMEの宣伝文句を鵜呑みにせず、source-backedに検証する
* 途中で失敗したら処理を分割する

そこで今回は、ローカルで動く DeepSeek V4 Flash に **「まだ有名ではないが伸び始めているAI Agent関連OSS」を探させるAgent** を作りました。

さらに、候補を見つけるだけではREADME要約で終わってしまうので、上位候補を `git clone` し、docs / examples / source / tests / CI まで読む **Source Inspection Agent** も作りました。

## 検証環境

| 項目 | 値 |
| --- | --- |
| マシン | MacBook Pro M5 Max / 128GB |
| LLM | DeepSeek V4 Flash |
| 推論サーバ | DS4 / OpenAI互換API |
| API | `/v1/chat/completions` |
| モデル名 | `deepseek-v4-flash` |
| 検証日 | 2026-06-14 |
| Agent実装 | Python stdlibのみ |

今回のAgentは、LangChainやCrewAIなどのフレームワークを使わず、OpenAI互換Chat Completions APIを直接叩く小さなPythonスクリプトとして実装しました。

理由は、モデルそのものとharness設計の挙動を見たかったからです。

ここは誤解しやすいので明確にしておきます。

今回のAgent本体では、OpenAI APIの `tools` / `tool_calls`、つまりモデル自身に

を出させる **model-driven tool calling** は使っていません。

使っているのは、Python harness側で制御する **program-driven pipeline agent** です。

| 種類 | 今回の扱い |
| --- | --- |
| OpenAI `tools` / `tool_calls` | Agent本体では未使用 |
| GitHub Search API | harness側が呼ぶ |
| repo metadata / README / issue / PR取得 | harness側が呼ぶ |
| `git clone` / `git ls-files` | harness側が実行 |
| ファイル選定 / chunk分割 | harness側で実装 |
| 候補評価 / source-backed評価 | DS4が担当 |
| JSON validation / retry | harness側で実装 |

DS4のOpenAI互換 `tool_calls` 自体は、別途疎通確認で動作確認済みです。

ただし今回の目的は「安定した技術発掘Agentを組めるか」だったため、どのAPIをいつ呼ぶかはharness側で決め、モデルには **取得済みevidenceを評価する役割** を持たせました。

これは自律性を少し抑える代わりに、再現性とログの追いやすさを優先した設計です。今後の発展としては、検索クエリ生成や追加調査判断をmodel-driven tool callingに寄せる余地があります。

## 全体フロー

今回作ったAgentは2段構成です。

### Discovery Agent

最初のAgentは、GitHub Search APIで候補を探します。

検索キーワードは以下のようなAI Agent関連語です。

* `ai-agent`
* `llm-agent`
* `mcp`
* `tool-calling`
* `agent-workflow`
* `agent-evaluation`
* `local-llm`
* `computer-use`
* `agent-observability`

有名OSSを再調査しても面白くないので、AutoGPT / LangGraph / CrewAI / Dify などは比較基準・除外リストとして扱いました。

評価軸はstar数だけではありません。

| 観点 | 見る内容 |
| --- | --- |
| 成長性 | star / fork / 最近のpush / release / issue / PR |
| 実用性 | 何を解決するか、導入しやすいか |
| 技術的新規性 | 状態管理、MCP、tool calling対応、workflow、memory、traceなどの工夫 |
| 技術的参考度 | API設計、plugin構造、schema validation、retry、loggingなど |
| ローカルLLM適性 | OpenAI互換API、Ollama、LM Studio、MLX等との相性 |
| 信頼性 | tests / CI / license / maintainer activity |

### Source Inspection Agent

Discovery Agentだけだと、READMEの宣伝文句に引っ張られるリスクがあります。

そこで上位5件は `git clone` して、ローカルで以下を読ませました。

* README
* docs
* examples
* source code
* tests
* `.github/workflows`
* package定義

GitHub APIを細かく叩くと負荷やrate limitが気になるため、深掘りはclone後のローカル解析に寄せました。

cloneした外部repo本体は保存対象にせず、解析結果だけを保存しています。

## Discovery Agentの結果

10件規模の検証結果です。

| 指標 | 値 |
| --- | --- |
| 発見repo | 72 |
| フィルタ通過 | 66 |
| 深掘り評価 | 10 |
| GitHub API calls | 49 |
| GitHub API合計時間 | 22.80 sec |
| LLM calls | 11 |
| LLM合計時間 | 504.68 sec |
| LLM平均時間 | 45.88 sec |
| LLM最大時間 | 145.43 sec |
| LLM総token | 51,518 |
| validation errors | 0 |

構造化JSONのvalidation errorが0だったのは良い結果でした。

一方で、10件をまとめて最終Markdownに統合するLLM callが最大145秒かかっています。候補単位の評価は安定している一方、全体統合は重いです。

### 発掘された10件

この時点でも記事としては面白いのですが、README要約に寄っている可能性があります。

そこでSource Inspection Agentを追加しました。

## Source Inspection Agentの結果

上位5件をcloneして、ローカルファイルを読ませました。

| 指標 | 値 |
| --- | --- |
| 対象repo | 5 |
| chunk inspections | 20 |
| LLM calls | 25 |
| LLM合計時間 | 913.15 sec |
| LLM平均時間 | 36.53 sec |
| LLM最大時間 | 53.18 sec |
| LLM総token | 134,148 |
| validation errors | 0 |
| git clone | 3 |
| clone合計時間 | 179.09 sec |

Discovery AgentよりLLM call数とtoken数は増えましたが、各callの最大時間は抑えられています。

これは後述する **chunk分割** の効果です。

### source-backed評価

| Repo | 分類 | confidence | Source Inspectionの要点 |
| --- | --- | --- | --- |
| `awesome-agentic-ai-zh` | curated\_resource | medium | 教材・ロードマップ。ローカルLLMやAgentic AIの構成はよく整理されているが、tool本体ではない。 |
| `clawpanel` | software\_tool | medium | Tauri desktop app。agent CRUD、memory管理、config schema validation、Docker helper、tests/CIが確認できた。 |
| `agentfield` | software\_tool | medium | SDK/examples/CIは確認。core frameworkやbenchmark主張の一部はREADME依存が残る。 |
| `Rapid-MLX` | software\_tool | medium | Apple Silicon向けinference server。pipeline architecture、tool parser、eval/harness/testsがsource-backedで確認できた。 |
| `AssetOpsBench` | software\_tool | medium | MCP server定義、agent runner、offline evaluation pipelineを確認。CI/testsは弱め。 |

ここで重要なのは、Discovery Agent時点の「すごそう」という評価が、Source Inspectionでかなり補正されたことです。

例えば `awesome-agentic-ai-zh` は有用ですが、分類としてはsoftware toolではなくcurated resourceです。`AgentField` も魅力的な主張は多いものの、source inspectionでは一部がREADME-onlyとして扱われました。

一方で `Rapid-MLX` は、M5 Max / local LLM文脈との相性がかなり良い候補でした。Apple Silicon向けのlocal inference serverで、pipeline architectureやtool parser、evaluation harnessがsource-backedで確認できています。

## 重要だった失敗: 大文脈一括投入はtimeoutした

最初、Source Inspection Agentでは「ローカルLLMだからトークンコストは気にしなくてよい」と考え、1repoあたり最大22万字のsource evidenceを1回で渡しました。

結果はtimeoutでした。

次に6万字まで下げても、やはりtimeoutしました。

ここで分かったのは、**ローカルLLMはトークン課金を気にしなくてよいが、応答時間とtimeoutは無視できない**ということです。

最終的には以下のように分割しました。

この構成では、5repoすべて完走しました。

| 方式 | 結果 |
| --- | --- |
| source evidenceを1回で投入 | timeout |
| 量を減らして1回で投入 | timeout |
| chunk inspection + repo統合 | 完走 |

Agent harness設計としては、これはかなり重要です。

ローカルLLMの強みは「何度も呼んでも課金が増えない」ことなので、巨大な1リクエストに詰めるより、**小さめのリクエストを複数回投げて段階統合する**方が実用的でした。

## DS4はAgentの頭脳として使えるか

今回の検証では、DS4 / DeepSeek V4 Flashは以下をこなせました。

* GitHub Search APIで候補探索
* 候補フィルタリング
* README / metadataベースの技術評価
* JSON schemaに沿った構造化出力
* validation error時のretry
* clone済みrepoのsource-backed inspection
* chunkごとの要約
* repo単位の統合評価
* Markdownレポート生成

特に、Discovery AgentとSource Inspection Agentのどちらでも、最終的なschema validation errorは0でした。

これはかなり実用的です。

ただし、弱点もあります。

* 大文脈を一括投入するとtimeoutする
* 最終統合や長文生成は遅い
* READMEの宣伝文句には引っ張られる
* source-backedにするにはharness側のファイル選定とchunkingが重要
* GitHub APIを多用しすぎない設計が必要

つまり、モデル単体というより **Agent harness設計込みなら実用的** という評価です。

## 特に深掘りしたいAI Agent関連リポジトリ

個人的に深掘り候補として面白いのは以下です。

M5 Max / Apple Silicon / local LLMという文脈に直結します。

Source Inspectionでも、pipeline architecture、tool parser、eval/harness/testsが確認できました。DS4記事の読者にもかなり近いテーマです。

今回の上位5件source inspectionには入れていませんが、Discovery Agentの10件候補ではかなり面白いです。

AI coding agentのAPI trafficやtool callをローカルでtraceするツールで、Agent harnessのobservabilityという観点で価値があります。

こちらも上位5件source inspectionには入れていませんが、AI coding agentを再現可能な開発workflowにする方向で、実務に近いです。

次に別記事や続編を作るなら、[Rapid-MLX](https://github.com/raullenchai/Rapid-MLX), [claude-tap](https://github.com/liaohch3/claude-tap), [ai-devkit](https://github.com/codeaholicguy/ai-devkit) あたりを個別に試すのがよさそうです。

## まとめ

今回の結論です。

* ローカルDeepSeek V4でも、技術発掘Agentは実用的に動く
* 単発ベンチより、Agent loopで見る方が実用性が分かる
* Discovery AgentだけではREADME要約に寄りやすい
* cloneベースのSource Inspection Agentを入れると、source-backedに評価できる
* GitHub API連打を避けるには、探索はAPI、深掘りはclone後ローカル解析がよい
* 大文脈一括投入はtimeoutする
* chunk分割 + 段階統合がローカルLLM Agent harnessの重要設計になる

ローカルLLMは「無料で無限に巨大文脈を投げられる魔法」ではありません。

しかし、課金を気にせず複数回呼べるので、処理を細かく分けて、検証・統合を繰り返すAgentにはかなり向いています。

今回の実験では、DS4 / DeepSeek V4 Flashは **AI Agent関連OSSを発掘し、source-backedに技術評価するAgentの頭脳として使える** という感触でした。

次は、このAgent自身をもう少し磨いて、発掘した候補を個別に試すところまで進めたいです。
