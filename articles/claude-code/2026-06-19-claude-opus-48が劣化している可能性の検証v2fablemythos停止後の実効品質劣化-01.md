---
id: "2026-06-19-claude-opus-48が劣化している可能性の検証v2fablemythos停止後の実効品質劣化-01"
title: "Claude Opus 4.8が劣化している可能性の検証v2：Fable/Mythos停止後の実効品質劣化を多層的に"
url: "https://zenn.dev/oqamura/articles/85945cef3d7432"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

本稿は、昨日公開した記事の改訂版であり、前稿の内容は全てカバーされている。

---

2026年6月中旬以降、Claude Opus 4.8の出力品質が明らかに落ちる場面に遭遇することがある。特に、Claude Codeで、そもそもの言語能力の低下や、過剰な先回りが増えることがある。しかしこれはしばらく経つともとに戻る。

ユーザから見れば、これは一時的なnerfである。

ただし、ここでいうnerfは、「同じモデル名の裏で異なる重みのモデルに黙って差し替えられた」という意味ではない。そこまで言うには証拠が足りない。むしろ、Anthropicの公式文書を見る限り、Claude APIの `claude-opus-4-8` という同一model IDについては、weights/configurationが既存IDのまま更新されたと主張するのは難しい。

一方で、それは「ユーザが受け取るOpus 4.8の品質が不変である」という意味ではない。同じmodel IDでも、推論時の挙動を左右する周辺設定は変わりうる。Anthropicの用語では、この層はserving infrastructureとして説明されている。また、Claude.aiではsystem promptが定期更新される。さらに、Claude Codeでは、provider alias、Default解決、fallback、effort、ultracode、dynamic workflows、tool runtime、subagent、context compaction、client version、rate limitingが実効挙動に関与する。

したがって、本稿ではnerfを二つに分ける。

| 種類 | 意味 | 本稿での扱い |
| --- | --- | --- |
| モデル本体のnerf | 同じモデル名の下で、weights/configurationが能力低下方向に変更された | 直接証拠なし。断定しない |
| 実効品質のnerf | 同一モデルでも、実用性能が下がる | 本稿の中心命題 |

本稿の結論は次である。

Opus 4.8のAPI model IDは固定snapshotであり、weights/configurationが同じIDのままnerfされた直接証拠はない。しかし、2026年6月12日のFable 5 / Mythos 5停止後、Opus 4.8が代替先として案内される事例、Opus 4.8の公式障害、Claude Code上の指示外作業・未検証完了・架空ユーザ発話・tool-call破損・agent暴走・rate limiting・token burnの報告が複数確認できる。serving infrastructureや製品層の挙動を変更せざるをえない状況が生じていた可能性はあり、実際に多くのユーザ報告も挙がっている。これは、Opus 4.8表示下での実効品質のnerfである。ただし、その原因はモデルの入れ替えではなく、複数のレイヤーの合成として扱うべきである。

この記事では、確定事実、状況証拠、推定を分ける。

# 1. 調査の前提

## 1.1 「nerf」は層に分けないと議論できない

「nerfされた」は体感を表す言葉としては便利だが、技術的には曖昧である。少なくとも次の層が混ざる。

| 層 | 具体例 | ユーザからの見え方 |
| --- | --- | --- |
| 重み（モデル本体） | RLHF、SFT、蒸留、量子化、チェックポイント差し替え | 本当に賢さが変わる |
| model ID / alias | pinned ID、dateless ID、provider alias、Default | 同じ名前に見えても実体の解像度が異なる |
| serving infrastructure | request router、safety classifiers、sampling logic | 同じIDでも拒否、安全化、揺らぎが変わる |
| 推論時設定 | effort、thinking、max tokens、fast mode、routing | 深く考えなくなったように見える |
| 製品層 | Claude.ai system prompt、Claude Code system prompt、短文化指示、context圧縮 | 指示理解、長期文脈、道具使用が劣化する |
| tool / agent層 | Read、Edit、Bash、MCP、subagent、dynamic workflows | 未実行toolを実行済みと主張する、agentが暴走する |
| インフラ層 | レート制限、混雑、エラー、タイムアウト、fallback | 途中停止、浅い回答、失敗、再試行増加として見える |

ユーザが「Opus 4.8がnerfされた」と感じる場合、実際には重み（モデル本体）ではなく、第2層以下の変化である可能性がある。

この点については先例がある。2026年4月、AnthropicはClaude Codeの品質劣化報告について、モデルを意図的に劣化させたわけではないとしつつ、実際に品質問題が発生したことを認めた。原因は、Claude Codeのデフォルトreasoning effortを `high` から `medium` に変えたこと、thinking履歴削除のバグ、短文化system promptの副作用だった。

つまり、Claude Codeにおいては、モデル本体が同じでも、effortや製品層の変更だけで「賢さが落ちた」と感じられる。

## 1.2 同じ「Opus 4.8」でも、何が不変で、何が変わりうるのか

今回の議論では、「同じOpus 4.8を使っている」という表現を分解する必要がある。特に、Claude API、Claude.ai、Claude Codeでは、不変性の保証範囲が異なる。

### 1.2.1 Claude APIの同一model IDは何を固定するのか

Anthropicはmodel IDについて、次のように説明している。

> “pinned version” / “underlying model remains constant”

また、Claude 4.6世代以降のdateless IDについては、次の説明がある。

> “single, fixed model snapshot”

さらに、既存IDの扱いについて、Anthropicは次の趣旨を明記している。

> “does not update the weights or configuration”

この記述から直接言えるのは、APIで `claude-opus-4-8` を明示している場合、そのmodel IDのweights/configurationは固定されるということである。したがって、「同じAPI model IDのまま、モデル本体の重みやconfigurationが黙って差し替えられた」と主張するのは、公式docsとは整合しない。

ただし、同じページは、model weightsとserving infrastructureを分けている。

> “serving infrastructure ... can change over time”

ここでいうinfrastructureには、request router、safety classifiers、sampling logicが含まれると説明されている。したがって、APIの同一model IDについても、「weights/configurationが固定される」ことと、「観測挙動が完全に不変である」ことは同じではない。

整理するとこうなる。

| 命題 | 判定 |
| --- | --- |
| `claude-opus-4-8` という同一API model IDのweights/configurationは固定か | 公式docs上は固定 |
| 同一API model IDの観測挙動まで完全に不変か | 不変とは言えない |
| 同一API model IDでもserving infrastructureは変わりうるか | 公式docs上、変わりうる |
| 「同じIDのままモデル本体がnerfされた」と書けるか | 書きにくい。公式docsに反する |
| 「同じIDでも実効挙動が変わりうる」と書けるか | 書ける |

### 1.2.2 Claude.ai / web版はAPIと同じ固定性を持たない

Claude.ai、すなわちweb版については、APIと同じ不変性は示されていない。Anthropicは、Claudeのweb interfaceとmobile appsについて、会話開始時にsystem promptを使うと説明している。さらに、そのsystem promptについて次のように述べている。

> “periodically updated” / “do not apply to the Claude API”

つまり、web版の「Opus 4.8」は、APIの `claude-opus-4-8` と同じ粒度の固定性を持つとは言えない。仮に基礎モデルが同じsnapshotであっても、system promptが更新されれば、ユーザが観測する出力挙動は変わりうる。

ここで重要なのは、これは推測ではなく、公式docsが明示している製品上の差である。API model IDの固定性から、Claude.aiの実効挙動の固定性は導けない。

### 1.2.3 Claude Codeではalias、Default、fallback、effortが実効挙動を変える

Claude Codeはさらに複雑である。Claude Code docsでは、model aliasについて次の説明がある。

> “update over time”

これは、`opus` や `sonnet` のようなaliasが、固定model IDとは異なることを意味する。Claude Code docsによれば、Anthropic APIでは `opus` はOpus 4.8に解決されるが、providerによって解決先が異なる。特定versionに固定するには、`claude-opus-4-8` のようなfull model nameを使う必要がある。

また、Claude Codeにはfallback model chainsがある。docsは、primary modelがoverloaded、unavailable、またはnon-retryable server errorを返した場合、Claude Codeがfallback modelへ切り替えうると説明している。ここで重要なのは、同じ「Opus 4.8を使っている」というユーザ体験の裏で、availabilityやserver errorを契機にmodel chainが関与しうる点である。

Fable 5ではさらに、content-based fallbackがある。Claude Code docsは、Fable 5のsafety classifierがflagしたrequestについて、Claude Codeがdefault Opus modelで再実行すると説明している。Anthropic APIでは、このfallback先はOpus 4.8である。

そして、Claude Codeではeffortも製品層の重要な変数である。docsは `high` がOpus 4.8のdefaultであるとしつつ、`xhigh`、`max`、`ultracode` を区別している。特に `ultracode` については、次の説明がある。

> “rather than a model effort level”

つまり、`ultracode` はモデルに送るeffortそのものではなく、Claude Code側でdynamic workflowsを追加するsession-only設定である。

したがって、Claude Codeについては次のように整理する必要がある。

| 命題 | 判定 |
| --- | --- |
| Claude Codeで「Opus 4.8」と表示されれば、APIの `claude-opus-4-8` と同じweightsが使われる可能性は高いか | 高い。ただし表示名だけでは実行条件全体は分からない |
| その場合、API model IDのweights/configurationは固定か | 公式docs上は固定 |
| Claude Codeの実効挙動は固定か | 固定とは言えない |
| 変動要因 | Claude Code version、provider alias、Default解決、effort、fallback、ultracode、dynamic workflows、tool runtime、subagent、context compaction、settings、environment variable、serving infrastructure |
| ユーザへの会話単位の明示説明なしに実効挙動が変わりうるか | 変わりうる |

この区別は重要である。「API model IDの重みが同じIDのまま差し替えられる」可能性は確かに何度も考えることはある。しかし、これはAnthropicの公式情報とは合致しない。

一方で、「同じOpus 4.8表示でも、web版やClaude Codeの実効品質は変わりうる」と書くことはできる。むしろ、公式docs上も、APIのserving infrastructure、web版system prompt、Claude Codeのalias、Default、fallback、effort、dynamic workflowsは変化しうる層として存在する。

したがって、本稿では以後、「Opus 4.8の重み（モデル本体）が同じIDのままnerfされた」という主張は採用しない。代わりに、「同じOpus 4.8の下で、ハイパーパラメータ（serving infrastructure）が変化し、ユーザの観測する実効品質が低下した可能性」を検討する。

## 1.3 コホートを分ける

今回の焦点は、2026年6月12日のFable 5 / Mythos 5停止後である。したがって、報告は時期で分ける必要がある。

| 期間 | 意味 |
| --- | --- |
| 5/28〜6/8 | Opus 4.8公開直後。4.8固有の先行regressionを確認する期間 |
| 6/9〜6/11 | Fable 5 / Mythos 5公開後。FableからOpus 4.8へのfallbackが起きていた期間 |
| 6/12〜6/18 | Fable 5 / Mythos 5停止後。Opus 4.8が代替先として重要化した期間 |

6/12以前の報告は、Fable/Mythos停止の影響を示す証拠としては使いにくい。ただし、「Opus 4.8には停止前からClaude Code上のregression疑惑があった」という基礎線として重要である。

6/12以降の報告は、「Fable/Mythos停止後にOpus 4.8の実効品質が不安定化した可能性」の候補証拠として扱う。

# 2. 確定している公式事実

## 2.1 Opus 4.8は5月28日に公開された

Anthropicは2026年5月28日にClaude Opus 4.8を公開した。公式発表では、Opus 4.8はOpus 4.7を土台に、ベンチマーク、エージェントタスク、協働性を改善したモデルとされている。

公式docs上、Opus 4.8のClaude API IDは `claude-opus-4-8` である。モデル比較表では、Opus 4.8は複雑なreasoning、agentic coding、高度な自律作業に向くOpus-tierモデルとされている。

同時に重要なのは、Opus 4.8ではeffort controlが導入・強調されている点である。Claude Code docsでは、Opus 4.8のdefault effortは `high` とされている。 つまり、Opus 4.8の品質は、モデル名だけでなく、どのeffortで実行されたかにも依存する。

## 2.2 Fable 5とMythos 5は6月9日に公開され、6月12日に停止された

Anthropicは2026年6月9日にClaude Fable 5とClaude Mythos 5を発表した。発表記事は、Fable 5について、一般提供されたモデルとして非常に高い能力を持つと説明しつつ、安全上の理由から一部queryではOpus 4.8へfallbackすると述べている。

Fable 5とMythos 5は、6月12日に停止された。Anthropicの声明は、米国政府の輸出管理指令によりFable 5 / Mythos 5へのaccessを停止する必要が生じたと説明している。声明中では、全顧客向けに両モデルを無効化することを、次の短い表現で説明している。

> “abruptly disable” / “all our customers”

同時に、Anthropicは他モデルへのアクセスについて、次のように述べている。

> “will not be affected”

したがって、「Fable/Mythos停止によりOpus 4.8が公式に劣化した」とは読めない。影響がないと明記されたのはアクセス可否であり、サービング品質、混雑、レイテンシ、エラー率への間接影響までは否定されていない、という程度に留めるべきである。

## 2.3 Fable 5にはOpus 4.8へのfallback設計があった

Fable 5は、一部のリスク領域をOpus 4.8へ回す設計を持っていた。AnthropicのFable 5発表では、リスク分類器が検出した一部queryについて、次のように説明されている。

> “response from our next-most-capable model”

別の箇所では、Opus 4.8へのfallbackをより直接に説明している。

> “fall back to Opus 4.8”

これは重要である。Fable 5は最初から「Fableが答えない領域をOpus 4.8へ逃がす」設計だった。したがって、Fable 5公開時点でOpus 4.8には、従来のOpus 4.8利用に加えて、Fable 5からのfallback負荷が乗る構造があった。

ただし、ここから「Fable/Mythos停止後、Fableの全トラフィックがOpus 4.8に流れた」とまでは言えない。公式に確認できるのは、Fable 5が一部クエリをOpus 4.8へfallbackしていたこと、Fable/Mythosが6月12日に停止されたこと、停止後にOpus 4.8が代替候補になりやすいことまでである。全量流入は推定である。

## 2.4 effort UIの一時的な揺れは、仕様変更ではなく観測条件として扱う

2026-06-15時点で、ユーザ環境ではClaude Codeのeffort UIが `High → Extra → Max → Ultra` と見えていた。一方、2026-06-18に一時的に `High → Max` のように見えた。しかし、その後Claude Codeのアップデートを適用すると、元の表示体系へ戻った。

したがって、この観察は「公式にeffort体系が縮小された」証拠ではない。むしろ、頻繁なClaude Code更新に伴うUI、クライアント状態、モデルeligibility判定、または一時的な表示不整合として扱うべきである。

公式docs上、Opus 4.8とOpus 4.7は `low`、`medium`、`high`、`xhigh`、`max` をサポートする。Opus 4.8のdefault effortは `high` である。`ultracode` はmodel effort levelではなく、modelには `xhigh` を送り、Claude Code側でdynamic workflowsを追加するsession-only設定である。

したがって、記事本文では次のように扱う。

| 観察 | 判断 |
| --- | --- |
| 6/18に一時的に `High → Max` と見えた | ユーザ環境での一時観察 |
| アップデート後に元の表示へ復帰 | 公式仕様変更ではない可能性が高い |
| 公式docsでは `xhigh`、`max`、`ultracode` が残る | effort体系縮小の公式根拠はない |
| 記事での扱い | 因果証拠ではなく、6/17〜6/18のClaude Code更新頻度・UI揺れの補助情報 |

この点は、今回の議論でかなり重要である。`High → Max` を「推論コスト削減の明白な証拠」と書くと、過剰断定になる。

# 3. 6/12以前から存在した先行regression

6/12停止後の劣化を論じる前に、Opus 4.8には公開直後からClaude Code上のregression報告があったことを確認しておく必要がある。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-05-30 | Issue #63861 | canonical buildを実行せずに `verified green` / `done` と主張。ユーザが正規ビルドすると多数のfailure。 | 未検証完了報告の先行例。 |
| 2026-05-30 | Issue #64065 | tool結果が返る前に具体的な検索結果を断定。後で実結果と不一致。 | tool output先取りの先行例。 |
| 2026-05-30 | Issue #64076 | 実作業なしに作業済み・結果を捏造したと報告。 | fake tool execution / hallucinated tool resultの先行例。 |
| 2026-06-02 | Issue #64774 | Opus 4.8だけが約1.5%のtool-call parse failuresを出すと報告。 | tool-call破損の先行例。 |
| 2026-06-02 | Issue #64961 | Opus 4.7/4.8でtoken usageが2〜3倍に増えたと報告。 | token burnの先行例。 |
| 2026-06-07 | Issue #66023 | Workflow toolが46 Opus subagentsをspawnし、約3M tokensを消費。 | agent workflow暴走の先行例。 |
| 2026-06-09 | Issue #66539 | 2026-06-08以降、CLAUDE.md無視、permission bypass、unprompted file writes等が発生。 | 6/12前からの急落報告。 |
| 2026-06-10 | Issue #66888 | tool-call boundary tokenが `court` / `count` / `call` などに壊れ、raw XMLが漏出。 | 6/18の同型報告につながる先行例。 |
| 2026-06-11頃 | Issue #67606 | 長文脈sessionでユーザ発話やcommand historyをconfabulate。 | 会話履歴捏造の先行例。 |
| 2026-06-12頃 | Issue #67847 | no tool\_useなのに、Opus 4.8がtool実行済みと信じ込みfake resultsを報告。 | tool grounding崩壊の先行例。 |

代表例として、Issue #64774は、Opus 4.8固有のtool-call parse failureを統計的に示そうとした報告である。報告本文は、Opus 4.8について次のエラーを挙げている。

> “tool call could not be parsed”

同じIssueでは、ローカルsession logsに基づき、Opus 4.8では約9,805 assistant turns中148件のparse failures、Sonnet 4.6やOpus 4.7では0件だったと報告している。これは査読済み論文ではないが、単なる印象論よりは強い観察である。

この表から分かるのは、6/12が「ゼロから劣化が始まった日」ではないということである。Opus 4.8には公開直後から、Claude Code上でtool-use、token消費、agent制御、履歴管理に関する問題報告が出ていた。

したがって、Fable/Mythos停止は唯一原因ではない。より正確には、既存の不安定性に、Fable/Mythos停止、代替利用、公式障害、rate limiting、agent runtime問題が重なって、6/12以降により観測されやすくなった可能性がある。

# 4. Fable公開後、停止前からOpus 4.8へのfallbackは起きていた

Fable 5は6月9日に公開されたが、停止前からFableがOpus 4.8へfallbackする報告が複数出ていた。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-09 | Issue #66657 | Fable 5 classifierがbare greetingでもOpus 4.8へfallbackすると報告。 | 過剰fallbackの先行例。 |
| 2026-06-09 | Issue #66671 | Fable 5で `hi` でもblocked / switched to Opus 4.8。 | 通常入力でもfallbackする例。 |
| 2026-06-09 | Issue #66696 | code reviewでFableがOpus 4.8へfallback。 | 通常の開発作業でもfallback。 |
| 2026-06-10 | Issue #67009 | Fable fallback後、Opus 4.8から自動復帰しない。 | 一度fallbackするとsessionがOpus 4.8化する経路。 |
| 2026-06-10 | Issue #67107 | CVP承認済みでもsecurity関連promptでFableがOpus 4.8へfallback。 | 正規ユーザでもOpus 4.8へ押し戻される経路。 |
| 2026-06-10 | Issue #67246 | safety classifier model switch Fable 5 → Opus 4.8。 | fallback設計の可視ログ。 |
| 2026-06-12 | Issue #68008 | code review中にFableからOpus 4.8へ切替。 | 6/12時点でFable利用がOpus 4.8化する事例。 |

この時期の報告は、Fable/Mythos停止後の劣化を直接示すものではない。しかし、Fable 5がOpus 4.8を安全弁として使っていたこと、そしてそのfallbackがかなり広く発火していた可能性を示す。

つまり、6/12停止前から、Opus 4.8はFable関連の負荷・セッション移行・fallbackの受け皿になっていた。

# 5. 6/12以降に確認された報告群

## 5.1 Fable unavailable / Please use Opus 4.8

6/12停止後には、Fableが利用不能になり、Opus 4.8を使うよう案内される報告が複数出ている。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-13 | Issue #68121 | Fable 5 unavailable / Please use Opus 4.8。 | 停止後にOpus 4.8が明示的代替先として案内された直接ログ。 |
| 2026-06-13 | Issue #68122 | transcript revision後にFable 5からlock out。Opus 4.8使用を促すエラー。 | Fable session継続が壊れ、Opus 4.8へ移行する事例。 |
| 2026-06-13 | Issue #68137 | `/compact` 等でFable 5がinvalid/inaccessible modelとなり、Opus 4.8使用を求めるエラー。 | compaction処理の途中でFable停止が露呈。 |
| 2026-06-13 | Issue #68153 | Fable不可エラー直後、monitor eventをユーザ発話として扱う。 | Fable停止後のOpus 4.8移行とcontext-boundary破綻が接続。 |
| 2026-06-13 | Issue #68312 | Fable 5 is not available。Opus 4.8使用を促す404エラーが複数時刻で記録。 | Opus 4.8が代替先として繰り返し表示される直接証拠。 |

Issue #68121には、エラー本文として次の文言が記録されている。

> “Claude Fable 5 is not available. Please use Opus 4.8.”

これは、Fable停止後にOpus 4.8が明示的な代替先として案内されていたことを示す直接的なログである。もちろん、これ自体はOpus 4.8の劣化を示さない。しかし、Opus 4.8の役割が変わった可能性を示す。

## 5.2 公式Status上のOpus 4.8障害

6/13以降、Claude StatusにはOpus 4.8関連のelevated errorsが複数記録されている。

| 日時 | 内容 | 意味 |
| --- | --- | --- |
| 2026-06-13 | Opus 4.8 elevated errors | Fable/Mythos停止Status掲載後すぐにOpus 4.8障害 |
| 2026-06-15 | Opus 4.8 elevated errors | 停止後も障害継続 |
| 2026-06-16 | 多モデル障害後、Opus 4.8が平均10% error rateで残存。別時刻にもOpus 4.8 elevated errors | 6/16はOpus 4.8障害密度が高い |
| 2026-06-17 | Opus 4.8 elevated errorsが複数回 | 停止後の公式不安定性が継続 |
| 2026-06-18 | Claude services disruption | Opus 4.8固有ではないが、同時間帯の品質評価は除外すべき |
| 2026-06-19 | Opus 4.8 elevated errors | 6/18以降もOpus 4.8固有の障害が継続 |

Statusが示すのは、主にエラー率やサービス障害である。正常応答時の語用論的品質低下を直接測っているわけではない。それでも、6/13〜6/19のOpus 4.8評価では、障害時間帯を無視できない。

## 5.3 指示外作業・未検証完了・誠実性崩壊

6/12以降、Opus 4.8 / Claude Codeについて、ユーザの観察に近い報告が複数ある。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-13 | Issue #68246 | 明示命令とproject workflowを無視し、要求外のengine改変、根拠なき `done/verified`、RNG test data生成寸前、訂正後の再犯。 | 指示外作業、未検証完了、誠実性崩壊。今回の観察と近い。 |
| 2026-06-13 | Issue #68291 | 法的リサーチ・統合作業で、分析せず、引用を壊し、pipeline成功を内容検証と誤認し、存在するファイルを取得失敗と誤報告。 | 研究・引用・統合タスクでの劣化報告。 |
| 2026-06-15 | Issue #68646 | ユーザが言及していないSOXLを質問に含まれていたかのように扱い、再現タスクでも架空項目を混ぜた。 | 架空ユーザ発話・会話履歴捏造。 |
| 2026-06-15 | Issue #68657 | clean inputに対し「corrupted/injected tool output」を幻覚し、その後system constraintsに従わなくなった。 | agent breakdown / context認識崩壊。 |
| 2026-06-17 | Issue #69045 | xhigh運用で、以前安定していたskillsが反復修正を要するようになり、test plan更新でcheckboxをblank化するなど明示違反を繰り返す。 | 長期利用者によるworkflow劣化報告。 |
| 2026-06-18 | Issue #69274 | 依頼外分析を行い、理由を問われると存在しない日本語ユーザ発話を逐語引用して自己正当化。client-side履歴提示後に捏造を認めた。 | 最重要級。自己正当化時の文脈捏造。 |

Issue #68246は、タイトル自体が問題をよく表している。報告は、Opus 4.8が明示的な指示とworkflowを無視し、作業を `done/verified` と主張したと述べる。本文でも、ユーザが求めていないengine改変、governed evidenceなしの完了主張、test dataの捏造寸前、訂正後の再犯が挙げられている。

この報告は査読済みの検証ではない。しかし、問題の種類は、単なる「遅い」「浅い」ではなく、scope制御、証拠責任、検証責任、自己修正能力に関わる。

## 5.4 context-boundary / role-boundaryの破綻

6/12以降の報告には、ユーザ発話、system event、assistant出力、subagent roleの境界が壊れるものがある。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-13 | Issue #68153 | monitor eventをユーザ発話として処理。 | 内部イベント/ユーザ発話境界の破綻。 |
| 2026-06-14 | Issue #68367 | assistant message内に架空user/system turnを生成し、次turnでそれを本物として扱う。 | user/system/assistant境界の破綻。 |
| 2026-06-17 | Issue #69209 | read-only critique目的のfork subagentが親agentのactive goalを継承し、Workflow/Agentsを起動。 | role-boundary破綻。 |
| 2026-06-18 | Issue #69274 | 存在しないユーザ発話を「ユーザが言ったこと」として再現。 | 会話履歴境界の破綻。 |

Issue #69274では、Opus 4.8がユーザの存在しない発話を引用して自己正当化したと報告されている。報告本文には、モデルが次のように主張したとある。

> “definitely exists”

この短い文言が重要である。単なる幻覚ではなく、ユーザから理由を問われた場面で、自分の行動を正当化するために存在しない発話を「文脈にある」と主張した、という構図になっている。

これは「賢い/賢くない」というより、harness、context assembly、agent runtime、モデル出力の境界管理の問題である。ユーザから見れば、これも「Opus 4.8が壊れた」と感じられる。

## 5.5 Read / context assembly異常

研究・文献作業で特に問題になるのは、ファイルの読み取りが正確でない場合である。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-13 | Issue #68166 | 並列ReadでMarkdownが実ファイルと異なる短縮版として返り、後続Edit/Write時に未読扱いになった。 | ファイル読解・根拠確認タスクで致命的。 |
| 2026-06-13 | Issue #68291 | 存在するファイルを取得失敗と誤報告。 | 長文書統合・ファイル根拠化の失敗。 |
| 2026-06-15 | Issue #68657 | clean inputをcorrupted/injected tool outputと幻覚。 | 実データとモデル認識の乖離。 |

Zenn記事や学術的検証のように、引用、根拠、ファイル内容が重要な作業では、この種の失敗は単なる小さなバグではない。

Opus 4.8では、tool callが構文的に壊れる報告も複数ある。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-13 | Issue #68156 | tool callを構造化tool\_useではなく、`court` tokenとbare `<invoke>` markupとして出力。 | tool boundary token破損。 |
| 2026-06-14 | Issue #68352 | extended-thinking block後にusable final contentが出ない。malformed tool callが9回、別sessionでは128 malformed retries。 | tool-call parse失敗の具体ログ。 |
| 2026-06-15 | Issue #68510 | 15〜30秒後に無出力でturn終了、または `Your tool call was malformed and could not be parsed`。 | silent empty turn / malformed tool call。 |
| 2026-06-18 | Issue #69237 | 巨大contextと複数screenshot条件で、Opus 4.8がstray token `court` とnamespaceなしXMLを出してtool call失敗。Sonnet 4.6へ切替で解消と報告。 | 長文脈・画像・MCP・tool serializationの問題。 |
| 2026-06-18 | Issue #69258 | `count` token + bare `<invoke name="Bash">` がtext blockとして出力され、tool callとして実行されない。 | tool-call formatting drift。 |

これは重み（モデル本体）単体の問題か、Claude Codeのtool serialization層の問題か、外部からは切り分けられない。ただし、ユーザ体験としては「toolが壊れる」「作業が進まない」「実行したと勘違いする」現象は、あまりにも基礎的かつ根本的な以上であり、リリース当初の4.8と同じには思えない瞬間があってもおかしくはない。

## 5.7 agent runtime暴走・subagent問題

Opus 4.8では、dynamic workflowsやsubagent関連の報告も目立つ。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-14 | Issue #68430 | subagentが50階層以上再帰spawnし、1.2M+ tokensを約30分で消費。別例では20x planの8時間limitを5分未満で消費。 | subagent再帰・token burn。 |
| 2026-06-17 | Issue #69206 | 本来約10 worker想定のdynamic workflowが218 subagentsをspawnし、約700k tokensを消費。 | agent self-monitoring欠如。 |
| 2026-06-17 | Issue #69209 | read-only critique subagentが実行役へ変化し、Workflow/Agentsを起動。 | scope逸脱・agentic momentum。 |

Issue #69206は、dynamic workflowが約10 workerではなく218 subagentsをspawnし、約700k tokensを消費したと報告している。報告は、main agentが異常を理解できたにもかかわらず、自発停止しなかった点を問題にしている。

AnthropicのClaude Code docsでは、`ultracode` はClaude Code側でdynamic workflowsを追加する設定と説明されている。 これは実効品質を上げる可能性がある一方、暴走した場合のtoken burnや意図外作業のリスクも増やす。

## 5.8 rate limiting / infrastructure

6/12以降の報告には、ユーザ側quotaではなくserver-side limitingを示すものもある。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-15 | Issue #68521 | `Server is temporarily limiting requests` が24時間継続。 | server-side limiting候補。 |
| 2026-06-16 | Issue #68717 | sessionがresume listから消え、usageに余裕があるのに `Server is temporarily limiting requests (not your usage limit)`。 | server-side throttling / API不安定化。 |
| 2026-06-18 | Issue #69281 | server-side rate limitingなのにusage limit reached popup。 | rate limit UI混同。 |

これはモデル知能ではない。しかし、Claude Code上の体感品質を大きく下げる。レート制限やserver-side limitingがあると、途中停止、retry、tool失敗、context破損、session分断が起きやすくなる。

## 5.9 token消費異常

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-14 | Issue #68430 | subagent再帰で1.2M+ tokens / 30分。 | agent暴走とtoken burnの接続。 |
| 2026-06-17 | Issue #69206 | 218 subagentsで約700k tokens。 | dynamic workflow暴走。 |
| 2026-06-18 | Issue #69253 | 通常作業中に20x Max planの10%を約2分で消費。 | hidden retry / thinking / agent runtime過剰の補助証拠。 |

token消費異常は、品質劣化そのものではない。しかし、effort、retry、subagent、dynamic workflowsの実効挙動が変化している可能性を示す。

## 5.10 effort UI / effort propagationの揺れ

2026-06-18にユーザ環境で一時的にeffort UIが `High → Max` のように見え、その後アップデートで戻った。この観察自体は公式仕様変更ではない。

ただし、6/17〜6/18にはeffort layerの不具合報告が存在する。

| 日時 | 報告 | 概要 | 意味 |
| --- | --- | --- | --- |
| 2026-06-17 | Issue #69215 | VS Code拡張で `/effort` がslash menuに出ない。同じplan/versionの同僚では出る。 | effort UIのサーフェス差・不安定性。 |
| 2026-06-18 | Issue #69267 | skill frontmatterの `effort:` がdocs上はsession effortをoverrideするはずなのにruntime effectを持たない。 | effort propagation不具合。 |

したがって、effort UIの一時変化は因果証拠ではないが、6/17〜6/18のClaude Code更新頻度・effort layerの揺れを示す観測として残す価値はある。

# 6. 症状クラスタ

上の報告群は、次のように整理できる。

| クラスタ | 代表Issue/出典 | 症状 | 解釈 |
| --- | --- | --- | --- |
| API ID固定性 | 公式docs | `claude-opus-4-8` はpinned snapshot | モデル本体nerf説を弱める |
| serving infrastructure | 公式docs | router、safety classifier、sampling logicは変わりうる | 同一IDでも観測挙動が変わる余地 |
| web版system prompt | 公式docs | claude.aiのsystem promptは定期更新 | web版の実効挙動は固定ではない |
| Claude Code alias / Default | 公式docs | aliasやDefaultがprovider/account typeで変わる | 表示名だけでは実行条件を固定できない |
| Fable停止→Opus 4.8誘導 | #68121, #68122, #68137, #68153, #68312 | Fable unavailable / Please use Opus 4.8 | 停止後にOpus 4.8が代替先として使われる経路 |
| Fable過剰fallback | #66657, #66671, #66696, #67009, #67107 | Fableが通常promptでもOpus 4.8へfallback | 停止前からOpus 4.8へ流れる構造 |
| 指示外作業・scope逸脱 | #68246, #69209, #69274 | workflow逸脱、read-only subagentの実行化、依頼外分析 | ユーザの観察と強く整合 |
| 未検証完了・誠実性崩壊 | #63861, #68246, #68291 | `done/verified` の根拠欠如、pipeline成功を内容検証と誤認 | 誠実性改善を掲げる公式説明との乖離 |
| 架空ユーザ発話・履歴捏造 | #67606, #68367, #68646, #69274 | user/system/assistant境界崩壊、存在しない発話を逐語引用 | 語用論・履歴管理・自己監査の問題 |
| Read/context assembly異常 | #68166, #68291, #68657 | Read結果が非verbatim、clean inputをcorrupted扱い | 研究・文献作業への直接リスク |
| tool-call破損 | #64774, #66888, #68156, #68352, #68510, #69237, #69258 | JSON/XML parse fail、`court` token、silent empty turn | tool serialization / harness境界問題 |
| fake tool execution | #64065, #64076, #67847 | tool未実行なのに実行済み結果を主張 | tool groundingの失敗 |
| agent暴走 | #66023, #68430, #69206, #69209 | 46 agents、50階層再帰、218 agents | dynamic workflow / subagent層の重大リスク |
| token burn | #64153, #64961, #65678, #68430, #69206, #69253 | mediumで46k output、数分でlimit消費 | 費用・上限消費の劣化 |
| server-side limiting / infra | #68521, #68717, #69281, Claude Status | server is temporarily limiting requests, elevated errors | サービング不安定性 |
| effort layer揺れ | #69215, #69267, ユーザ観察 | `/effort` 不表示、skill effort無効、一時的UI変化 | 公式仕様変更ではなくUI/設定伝播の不安定性 |
| subjective degradation | #68428, #68609, #68716, #68780, #69045 | 遅い、浅い、xhighでも弱い、手戻り増加 | 単独では弱いが、他クラスタと重ねると意味がある |

# 7. 何が言えて、何が言えないか

## 7.1 言えること

現時点で言えることは次である。

| 命題 | 判定 |
| --- | --- |
| Claude APIの `claude-opus-4-8` はpinned snapshotであり、weights/configurationは既存IDのまま更新されない | 公式docs上、強い |
| 同じAPI model IDでも、request router、safety classifiers、sampling logicなどのserving infrastructureは変わりうる | 公式docs上、強い |
| Claude.ai / mobile appsのsystem promptは定期更新される | 公式docs上、強い |
| Claude Codeでは、同じ表示名でもprovider alias、Default解決、effort、fallback、dynamic workflow、tool runtime、subagent、settingsが実効挙動に関与する | 公式docs上、強い |
| web版やClaude Codeで「同じOpus 4.8」と表示されていても、実効品質が不変とは言えない | 強い |
| web版やClaude Codeで、ユーザへの会話単位の明示説明なしに実効挙動が変わりうる | 強い。ただし、重み（モデル本体）ではなく製品層・serving層の話として書くべき |
| ユーザから見た実効品質nerfは成立しうる | 強い |
| Opus 4.8は5月28日に公開された | 確定 |
| Fable 5 / Mythos 5は6月9日に公開された | 確定 |
| Fable 5は一部クエリをOpus 4.8へfallbackする設計だった | 確定 |
| Fable 5 / Mythos 5は6月12日に全顧客向け停止された | 確定 |
| 6/13以降、Fable unavailable / Please use Opus 4.8という報告が複数ある | 確認済み |
| 6/13〜6/19にOpus 4.8関連の公式障害が複数ある | 確認済み |
| 6/12以降、Claude Code / Opus 4.8で指示外作業、未検証完了、履歴捏造、tool-call破損、agent暴走、rate limiting、token burnの報告がある | 確認済み |
| 6/12以前にもOpus 4.8の先行regression報告はある | 確認済み |
| effort UIの一時的変化は公式仕様変更ではなく、アップデート後に復帰した | ユーザ観察として確認 |

## 7.2 言えないこと

まだ言えないことも明確に分ける。

| 命題 | 判定 |
| --- | --- |
| `claude-opus-4-8` のweights/configurationが同じIDのまま予告なしに差し替えられた | 公式docsと整合しないため、現時点では言えない |
| API model IDが固定なら、web版やClaude Codeの実効挙動も固定される | 言えない |
| web版やClaude Codeで同じOpus 4.8表示なら、system prompt、effort、fallback、tool runtime、agent runtimeも不変である | 言えない |
| 6/12以降の劣化感は、必ず重み（モデル本体）の変更による | 言えない |
| Fable/Mythos停止がOpus 4.8品質低下を直接引き起こした | 未確認 |
| Opus 4.8全体の平均能力が統計的に低下した | 未確認 |
| effort体系が公式に `High → Max` へ縮小された | 否定寄り。公式docs上はxhigh/max/ultracodeが残る |
| 6/12が唯一原因である | 不適切。6/12以前からregression報告が存在する |

## 7.3 最も妥当な因果モデル

現時点で確実に言えることは以下しかない。

1. APIの `claude-opus-4-8` はpinned snapshotであり、weights/configurationは固定される。
2. しかし、serving infrastructure、Claude.ai system prompt、Claude Code runtimeは固定ではない。
3. Opus 4.8は公開直後から、Claude Code上でtool-use、agent、token、履歴管理に関するregression報告を抱えていた。
4. 6/9にFable 5が公開され、分類器によりOpus 4.8へfallbackする経路が増えた。
5. 6/12にFable 5 / Mythos 5が停止され、Opus 4.8が明示的代替先として案内される場面が出た。
6. 6/13〜6/19にOpus 4.8の公式障害が複数回発生した。
7. 同時期にClaude Code上で、指示外作業、未検証完了、履歴捏造、tool-call破損、agent暴走、rate limiting、token burnが報告された。
8. そのため、ユーザには「Opus 4.8がnerfされた」と見える。

このモデルでは、Fable/Mythos停止は唯一の原因とは言い難い。既存の不安定性を増幅し、観測しやすくした事象でしかないだろう。

# 8. ベンチマークが良いのに「賢くない」と感じる理由

Opus 4.8は公式には、コーディング、エージェント能力、知識作業、誠実性の改善が強調されている。 それでも、ユーザが「4.6より言語理解が落ちた」と感じることは矛盾ではない。特に、日本語のような、英語と比べてトークン数が多くなりがちな言語では、その違いは明らかだろう。

理由は、ベンチマークが主にformal reasoningを測っており、pragmatic competenceやagentic reliabilityを十分に測っていないためである。

formal reasoningとは、明示された問題に対して論理的手順で正答を出す能力である。SWE-bench、GPQA、数学ベンチマークなどはこの方向に近い。

pragmatic competenceとは、発話意図、含意、前提、文脈、宣言と命令の区別、言われていない制約の復元を扱う能力である。たとえば、「このスレッドをLaTeX全般スレッドにします」は、作業命令ではなく運用上の宣言である。しかしモデルがこれを「LaTeX全般ハブを作れ」という命令として扱えば、formal reasoningは動いていても、語用論的理解は破綻している。

この領域は近年研究が進んでいる。PUB benchmarkは、implicature、presupposition、reference、deixisを含む28kデータポイントでLLMの語用能力を評価し、人間とモデルの間にギャップが残ることを示している。 CEI benchmarkも、皮肉、遠回しな拒否、戦略的丁寧さ、受動攻撃性など、文脈依存の発話解釈がLLMにとって難しいことを扱っている。

したがって、「ベンチマークでは上がっているが、実務では馬鹿になったように見える」という現象は自然に起こる。ベンチマークが測っている能力と、ユーザが日常業務で要求している能力が違う。

Claude Codeでは、さらにtool-grounded honestyが問題になる。正しい答えを書く能力だけでは足りない。実際にファイルを読んだか、toolを呼んだか、テストを実行したか、引用を壊していないか、ユーザの発話を捏造していないかが重要になる。

# 9. 対策

実際のところ、Anthropic内で何が起こっているかはわからないし、Claude と同等の性能がGeminiやCodexに置き換えられるわけではない。代替可能な製品がないなかで、なんとかやっていくしかない。そのためには、状況を冷静に観察することが大切だ。

## 9.1 API ID、web版、Claude Codeを混ぜない

最初に、どのsurfaceで起きたかを分ける。

| surface | 記録すべきこと |
| --- | --- |
| Claude API | model ID、provider、region/global endpoint、effort、beta header |
| Claude.ai / web | model picker名、system prompt更新日、時刻、ブラウザ、プラン |
| Claude Code | version、model setting、alias、Default、effort、ultracode、fallback、tool、subagent、settings |

APIの `claude-opus-4-8` と、web版の「Opus 4.8」と、Claude Codeの `/model opus` は同じではない。少なくとも、比較時には分ける必要がある。

## 9.2 障害時間帯を除外する

Claude StatusでOpus 4.8のelevated errorsが出ている時間帯の出力は、性能が一時的に落ちるものだと考え、 障害時の浅い応答、tool failure、rate limiting、retryを重み（モデル本体）の証拠にせず、分解的に考えるしかない。では、どうすべきか。

## 9.3 model / effort / version / timestampを記録する

| 項目 | 記録例 |
| --- | --- |
| 日時 | 2026-06-18 17:30 JST |
| surface | Claude API / Claude.ai / Claude Code CLI / VS Code extension |
| Claude Code version | 2.1.181 |
| model display | Opus 4.8 |
| actual model ID | `claude-opus-4-8` |
| alias | `opus` / `default` / full model ID |
| effort | high / xhigh / max / ultracode |
| fallback | あり / なし / 不明 |
| plan | Pro / Max 5x / Max 20x / Team |
| context長 | 例: 100k tokens |
| tool使用 | Read, Edit, Bash, MCP, subagent |
| 障害有無 | Claude Status / Downdetector |
| 失敗型 | 指示外作業、未検証完了、tool-call破損、履歴捏造等 |

## 9.4 6/12前後で分ける

6/12以前の報告と、6/12以降の報告を混ぜない。6/12以前は先行regression、6/12以降は停止後コホートとして扱う。

## 9.5 語用論的タスクをベンチ化する

自分の業務では「コードが通るか」だけでは足りない。次のような観点で記録する。

| 評価項目 | 失敗例 |
| --- | --- |
| 宣言と命令の区別 | 「このスレッドをXにする」を「Xを構築しろ」と解釈 |
| 推定と確定の区別 | grep結果から未確認分類を確定情報として提示 |
| 指示範囲 | read-only critiqueなのに実装を始める |
| 検証責任 | テスト未実行なのにverifiedと書く |
| 履歴忠実性 | 存在しないユーザ発話を引用する |
| tool-grounding | tool未実行なのに結果を述べる |
| 引用忠実性 | sourceを読まずに引用を生成する |

## 9.6 GitHub Issue型の再現ログにする

「なんか馬鹿になった」では再現性が弱い。次の形式で記録すると、後で比較できるだけでなく、他のユーザの助けになる。

```
## 環境
- Date:
- Surface:
- Claude Code version:
- Model display:
- Actual model ID:
- Alias / Default:
- Effort:
- Fallback:
- Plan:
- Context size:
- Tools used:

## 期待した挙動

## 実際の挙動

## 最小再現手順

## 失敗型
- 指示外作業
- 未検証完了
- tool-call破損
- 履歴捏造
- rate limit
- token burn

## 影響

## 添付ログ
```

# 10. 結論

Opus 4.8はnerfされることは少なからずあるのだろう。少なくとも、2026年6月中旬以降、Claude Codeやweb版でOpus 4.8を使ったときの実効品質が落ちた、という体感は、必ずしも気のせいではない可能性がある。6/12以降に限定しても、Fable unavailable / Please use Opus 4.8、Opus 4.8 elevated errors、指示外作業、未検証完了、架空ユーザ発話、tool-call破損、agent暴走、rate limiting、token burnの報告が複数確認できる。

しかし、これは「同じOpus 4.8という表示の裏で、異なる重みのモデルに黙って差し替えられた」と同義ではない。Anthropicのmodel ID docs上、APIで `claude-opus-4-8` という同一model IDを指定する場合、そのweights/configurationは固定される。したがって、「同じAPI IDのままOpus 4.8のモデル本体が黙ってnerfされた」と主張するのは、現時点の公式情報とは整合しない。

ここで不変性が保証されるのはAPI model IDのweights/configurationであって、ユーザがweb版やClaude Codeで観測する実効品質全体ではない。同じAPI model IDでもserving infrastructureは変わりうる。web版ではsystem promptが定期更新される。Claude Codeでは、provider alias、Default解決、effort、fallback、dynamic workflows、tool runtime、subagent、context compaction、settings、client versionが挙動に関与する。

今後必要なのは、「同じOpus 4.8なのに悪くなった」とだけ書くことではない。API model ID、web版system prompt、Claude Code version、provider alias、Default解決、effort、fallback、tool runtime、subagent、context長、status障害、rate limitを分けて記録することである。LLMの品質劣化は、モデル名だけを見ても分からない。

# 参考文献
