---
id: "2026-05-07-aiエージェントを統制する4つの柱langgraph-interrupt-と-firecracker-01"
title: "AIエージェントを統制する4つの柱——LangGraph interrupt と Firecracker で作る2026年版"
url: "https://zenn.dev/ukiajp/articles/ai-agent-governance-pillars-2026"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

## 0. はじめに

AIエージェントが「自分でツールを呼び、パッケージをインストールし、処理を進める」時代になりました。

LangChain や LangGraph のようなフレームワークを使えば、自然言語の指示だけでコードを書いて実行し、外部APIを叩き、必要なライブラリを取ってくるエージェントを数時間で組めます。

便利です。本当に便利です。

しかし、**人間のレビューが介在しない分だけ、リスクも高速で顕在化します。**

「AIに任せたら知らないパッケージが入っていた」「自動実行スクリプトが外部に通信していた」——そうした事態が現実になる前に、ガバナンスの基盤を整えておく必要があります。

本記事では、RPAエンジニアとして「自動化の統制」と向き合ってきた経験を踏まえながら、2026年時点のAIエージェント・ガバナンス設計を整理します。結論を先に書くと、設計すべき柱は**Whitelist・Policy-as-Code・承認ゲート・サンドボックス**の4つです。

---

## 1. 2026年に何が起きているか——「もう古い問題」ではない

「サプライチェーン攻撃って2018年の event-stream とか2024年の xz utils の話でしょう？」と思っている方に、まず2026年の現状を共有させてください。

**dYdX phantom packages（2026年1月）**  
npm 上に dYdX を装った128個の偽パッケージが投入され、半年間で12万ダウンロードを超えました。一部は週3,900回以上ダウンロードされていました。注目すべきは、これらの多くが「未登録の名前」を狙ったケースで、npm の typosquatting 検知を**そもそも対象外にしてすり抜けていた**点です。

**Axios RAT 混入（2026年3月）**  
週1億ダウンロードを超える `axios` のバージョン1.14.1と0.30.4に、クロスプラットフォームのリモートアクセス・トロイの木馬が仕込まれました。検知・削除までわずか3時間。「広く使われた実績あるパッケージなら安全」という前提は、もう成り立ちません。

**TeamPCP（2026年3月）**  
コンテナ・セキュリティスキャナの Trivy を皮切りに、自己増殖型の npm ワームが40以上のパッケージへ拡散。さらに Checkmarx KICS、OpenVSX 拡張、最後は PyPI の `LiteLLM` と `Telnyx` のリリースまで汚染した、**ツール業界横断**の多段攻撃でした。

**xz utils（2024年）の教訓も忘れてはなりません。** 2年がかりで信頼を積み上げた攻撃者がバックドアを仕込み、発見されたのは Postgres の挙動を不審に思った1人のエンジニアの偶然でした。

これらが示しているのは、**人間が手動でパッケージを選ぶときの「あれ？」という違和感が、エージェントの自律実行では発火しない**という事実です。AIエージェントは知らないパッケージを淡々とインストールします。攻撃の速度と規模が上がる構造的な理由は、ここにあります。

---

## 2. 任天堂の「枯れた技術の水平展開」をガバナンスに持ち込む

ここで一度、技術選定の哲学に立ち返らせてください。

ゲームボーイは1989年に発売され、2003年まで生産され続けました。戦場に落とされても動いたという逸話があります。なぜそれほど頑丈だったか。

答えは「枯れた技術の水平思考」にあります。任天堂の横井軍平氏が体系化したこの哲学は、**最新技術を追うのではなく、実績ある技術を組み合わせて新しい価値を生む**というものです。新しい部品は未知のリスクを抱えています。枯れた部品は、すでに多くの失敗と修正を経て洗礼を受けています。

私はこの原則がAIエージェントのガバナンス設計に直結すると考えています。

**ガバナンス基盤にこそ、枯れた技術を使うべきです。**

アプリケーション層では新しいフレームワークを試してもよい。しかしセキュリティポリシーの実行基盤・ライブラリの管理・承認フロー・実行隔離を支える仕組みには、実績があり・監査されており・コミュニティが広く理解している技術を選ぶべきです。

ガバナンスが壊れたとき、守るべきものがすべて崩れる。だからこそ、ガバナンス層は壊れにくくなければなりません。

---

## 3. 4つの柱——具体的な設計

2026年現在、AIエージェント・ガバナンスの構成要素として国内外で収斂しつつあるのが次の4つです。Microsoft が2026年4月に公開した [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) も、OWASP Agentic Top 10 に対応するためにこの4層を中心に据えています。

### 3-1. ライブラリWhitelist——「入れていいもの」を宣言する

エージェントが触れていいパッケージを、事前に宣言しておきます。

```
# allowed_packages.txt
requests==2.31.0
pydantic==2.5.0
langchain==0.1.0
openai==1.10.0
```

これだけのことで「知らないパッケージが入る」リスクを大幅に下げられます。

ポイントは**バージョンまで固定する**こと。同じパッケージ名でも、バージョンアップによって依存関係が変わり、悪意あるコードが紛れ込む経路が生まれます。Axios の事例（1.14.1のみが汚染）は、まさに「同じ名前・違うバージョン」で攻撃が成立することを示しています。

### 3-2. Policy-as-Code——ルールをコードで実行する

ルールをコードとして記述し、CIパイプラインで自動検査します。

手作業のチェックは漏れます。人間は疲れるし、急いでいるときは飛ばします。ルールがコードであれば、毎回・漏れなく・機械的に実行できます。

```
# .github/workflows/policy-check.yml
- name: Check vulnerabilities
  run: |
    pip install pip-audit
    pip-audit --requirement requirements.txt
- name: Static analysis
  run: |
    pip install bandit
    bandit -r src/
```

`pip-audit` は Python Packaging Authority（PyPA）公式のツールで、2026年現在もアクティブにメンテナンスされています。Bandit と組み合わせれば、依存関係の脆弱性とコード上のセキュリティ・アンチパターンを両面でチェックできます。

より複雑なポリシーには [OPA（Open Policy Agent）](https://www.openpolicyagent.org/) や Rego が有効です。「本番環境には特定のパッケージしか入れられない」「ライセンスがMIT以外のパッケージは要確認」といったルールも、すべてコードで表現・自動化できます。

### 3-3. 承認ゲート——LangGraph `interrupt()` で人間の判断を挟む

AIエージェントが自律的に進めていい範囲と、人間の確認を要する範囲を明示的に設計します。

LangGraph では2026年の標準パターンとして、`HumanInTheLoopMiddleware` でツール呼び出しごとに承認・却下・修正を要求できます。

```
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[write_file, execute_sql, read_data],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_file": True,
                "execute_sql": {"allowed_decisions": ["approve", "reject"]},
                "read_data": False,  # 読み取りは自動承認
            },
            description_prefix="ツール実行の承認待ち",
        ),
    ],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "conversation_1"}}

# 1回目：interrupt まで実行して停止
result = agent.invoke(
    {"messages": [{"role": "user", "content": "古い顧客データを削除して"}]},
    config=config,
    version="v2",
)
print(result.interrupts)  # 承認待ちの内容を確認

# 人間の判断を渡して再開
agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
    version="v2",
)
```

ポイントは **checkpointer が必須**である点です。`interrupt()` は `GraphInterrupt` 例外を投げてグラフ実行を停止し、状態を checkpointer にスナップショット保存します。`Command(resume=...)` で同じ `thread_id` に対して再開すると、保存された状態から続きが走ります。

開発時は `InMemorySaver` で十分ですが、**本番では `AsyncPostgresSaver` 等の永続チェックポインタが要件**になります。プロセスが落ちても状態が消えないことが、承認ゲートを「インフラ」として成立させる前提です。

### 3-4. サンドボックス——実行を物理的に隔離する

ここが2026年版で最も重要な追加です。

Whitelist・Policy-as-Code・承認ゲートをすり抜けた処理が、それでも本番システムを破壊しないように、**実行環境そのものを隔離**します。

OWASP Agentic Top 10 の「ASI05: Unexpected Code Execution」は、サンドボックスを推奨ではなく**コントロール要件**として定義しています。2026年現在の選択肢は次の3つに収斂しています。

| 技術 | 強度 | ユースケース |
| --- | --- | --- |
| **Firecracker microVMs** | 最強（カーネル分離） | 規制対象データ・金融・医療 |
| **gVisor** | 強（syscallレベル） | コンピュート集約型のマルチテナント |
| **V8 Isolates** | 軽量（JS限定） | レイテンシ重視の軽量タスク |

Microsoft Agent Governance Toolkit と NVIDIA のサンドボックス・ガイダンスは、**4つの強制レイヤー**で揃いつつあります。

1. **Network egress**：外部通信先のホワイトリスト
2. **Filesystem boundaries**：書き込み可能なパスを限定
3. **Secrets scoping**：API キー等のスコープを最小化
4. **Configuration file protection**：設定ファイルへの書き込みを禁止

Firecracker は AWS Lambda の実行基盤として実績があり、まさに「枯れた技術」の典型です。最新の何かに飛びつくのではなく、すでに大規模本番で揉まれた仕組みをガバナンス層に持ち込む。これが2章の哲学の具体化です。

---

## 4. RPAエンジニアの視点から

UiPath でRPAを設計していたとき、似たような問題と向き合っていました。

UiPath には「アクティビティ」と呼ばれる処理ブロックがありますが、組織によっては「使っていいアクティビティ」を管理者が制限していました。野良ロボットが業務システムを壊すことへの対策です。これはまさに**Whitelist的な発想**でした。

ロボットの実行環境も、本番サーバ上で直接動かすのではなく、専用の実行ホストに隔離する設計が標準でした。今思えば、**サンドボックスの思想を別の言葉で実装していた**わけです。

AIエージェントの時代に変わっても、問題の本質は同じです。

* 自動化の範囲を定義する
* 逸脱を検知する仕組みを作る
* 人間が介在すべきポイントを設計する
* 暴走しても被害が拡がらないように隔離する

RPAで学んだ「自動化の統制」は、AIエージェントのガバナンス設計に直接応用できます。ツールが変わっても、考え方は枯れません。

---

## 5. なぜ「いま」整えるのか——規制のタイミング

2026年は、AIガバナンスが「推奨」から「義務」に変わる年です。

* **EU AI Act 高リスクAI規制**：2026年8月施行
* **Colorado AI Act**：2026年6月施行

EU AI Act の高リスクカテゴリに該当するシステムには、リスク管理・データガバナンス・トレーサビリティ・人間による監督が**法的要件**として課されます。今回紹介した4つの柱は、そのまま規制対応の土台になります。

「いずれやればいい」が「もう待てない」に変わったタイミングで、本記事を書いています。

---

## 6. 実装してみた——9件の警告とどう向き合ったか

理論だけ書いて終わるわけにもいかないので、実際に自分のリポジトリ [meeting-to-doc](https://github.com/ukiajp/meeting-to-doc)（会議録画を文字起こし＋スクショ抽出で議事録化するツール）に Whitelist と Policy-as-Code を導入してみました。

### 導入した内容

* `requirements.txt` をバージョン固定（`whisperx==3.8.5`、`google-genai==1.75.0` 等）
* `requirements.lock.txt` に `pip freeze` 全体を保存
* `.github/workflows/policy-check.yml` で `pip-audit` と `bandit` を CI 実行

### 初回実行で出た9件

`pip-audit` が4パッケージで9件の脆弱性を検知しました。

| パッケージ | 件数 | 概要 |
| --- | --- | --- |
| Pillow 12.1.1 | 4 | FITS/PSD/PDF 解析やフォント処理での DoS・メモリ破壊 |
| mako 1.3.10 | 1 | Windows パストラバーサル |
| setuptools 70.2.0 | 1 | `easy_install` 経由のパストラバーサル |
| transformers 4.57.6 | 1 | `Trainer._load_rng_state()` での任意コード実行 |

`bandit` も Medium 1件（`urllib.request.urlopen` の使用）を指摘してきました。

### 「警告ゼロ」を目指さなかった理由

全部対応してしまうのは簡単ですが、**実害ベースで判断する**ほうがセキュリティ運用としては正しいと考えました。今回の判断はこうです。

* **Pillow**：直接依存・コスト低 → アップグレード
* **mako**：本プロジェクトでは使っていない（pyannote-audio の孫依存） → 放置
* **setuptools**：廃止された API 経由の問題 → 放置
* **transformers**：本プロジェクトは推論のみで `Trainer` を使わない → 放置
* **bandit B310**：URL は固定の `localhost:11434`（Ollama）。ユーザー入力を URL に混ぜていない → `# nosec B310` で抑制

判断記録は [SECURITY\_NOTES.md](https://github.com/ukiajp/meeting-to-doc/blob/main/SECURITY_NOTES.md) として残しています。

### 学び

* **CI が出した警告を読むこと自体に価値がある。** 知らないうちに脆弱性のあるパッケージが入っている、という事実を知ることが第一歩
* **「Trainer を使わない」のような利用文脈の判断は、人間にしかできない。** AI エージェントに「全部直して」と頼むと、不要な依存アップデートで別の不具合を呼ぶリスクがある
* **判断記録を残すこと**が、未来の自分とレビュアーへの最大の親切。「なぜ放置したか」が説明できれば、警告は資産になる

CI を最初から「fail させる」厳格モードにしなかったのも意図的です。`continue-on-error: true` で警告として運用し、慣れてきたら段階的に厳格化する。Policy-as-Code は**入れて終わり**ではなく、**運用の温度**を選べることが大事です。

---

## 7. まとめ

AIエージェントの自律性を上げるほど、制約設計の質が問われます。2026年版のチェックリストとして整理します。これは私自身が個人プロジェクトに導入する際の手順そのものでもあります。

| 柱 | 目的 | 主な技術 |
| --- | --- | --- |
| Whitelist | 入れていいものを宣言 | requirements 固定・承認済リスト |
| Policy-as-Code | ルールをCIで自動執行 | pip-audit、Bandit、OPA/Rego |
| 承認ゲート | 人間の判断を挟む | LangGraph `interrupt()` + Postgres checkpointer |
| サンドボックス | 実行を物理隔離 | Firecracker、gVisor、V8 Isolates |

そしてその全体に、2つの哲学を通します。

* **ガバナンス基盤にこそ枯れた技術を使う**（任天堂の水平展開）
* **設計は人間、実装はAI、レビューは敵対的視点で**（同じモデルを並べてもセカンドオピニオンにはならない）

エージェントに任せることと、エージェントを制御することは矛盾しません。**「任せる前に整える」のがエンジニアの責任です。**

---

## 参考資料
