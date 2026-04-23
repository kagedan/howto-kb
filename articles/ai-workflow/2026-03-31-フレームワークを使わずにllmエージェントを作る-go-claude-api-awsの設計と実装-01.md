---
id: "2026-03-31-フレームワークを使わずにllmエージェントを作る-go-claude-api-awsの設計と実装-01"
title: "フレームワークを使わずにLLMエージェントを作る — Go + Claude API + AWSの設計と実装"
url: "https://zenn.dev/dysksh/articles/27617be34cc336"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

## はじめに

Discordから自然言語でタスクを投げると、LLMがリポジトリを読み、コードを生成し、GitHub PRとして返すエージェント「Nemuri」を作った。PRに限らず、新規リポジトリの作成、S3へのファイルアップロード、Discordへのテキスト返信にも対応している。LangChainやCrewAI等のフレームワークは使わず、Claude APIを直接叩いてGoで実装している。

フレームワークを使わなかった理由は、Nemuriのエージェントループが「1エージェントが2フェーズを順次実行＋レビューループ」というシンプルな構造で、複数エージェントの並列実行や動的ルーティングといったフレームワークが力を発揮する場面がなかったからだ。フレームワークの抽象に合わせるコードが増える一方で、トークン予算制御や質問中断・再開といったドメイン固有のロジックは結局自前で書くことになる。この規模では直接制御する方がシンプルだと考えた。

この記事では、Nemuriの設計判断と実装の勘所について書く。エージェントループの設計、ツール設計、コスト制御、インフラ構成、品質の計測方法を扱う。

リポジトリ: <https://github.com/dysksh/nemuri>

## アーキテクチャ概要

設計原則は「**常時起動するインフラを持たない**」こと。1ジョブ = 1 ECSタスクのワンショット実行で、ジョブがなければAWS費用はほぼゼロになる。

### リクエストの流れ

1. ユーザーがDiscordで `/nemuri <プロンプト>` を実行
2. API Gateway → Ingress Lambda: Ed25519署名検証、DynamoDBにジョブ作成、SQSにエンキュー
3. Discordには「処理中」の仮応答（deferred response）を3秒以内に返す
4. SQS → Runner Lambda → ECS Fargateタスク起動
5. Agent Engineがロック取得 → ジョブ実行 → 結果配信

| カテゴリ | 技術 |
| --- | --- |
| 言語 | Go 1.25 |
| LLM | Claude API 直接呼び出し（実装: claude-sonnet-4-6、レビュー: claude-opus-4-6） |
| インターフェース | Discord スラッシュコマンド |
| コンピュート | ECS Fargate、Lambda |
| データ | DynamoDB、S3、SQS |
| IaC | Terraform（モジュール構成、dev/prod環境分離） |

## なぜ自作したのか

チャットからLLMにコードを書かせてPRを作る仕組みは、GitHub Copilot Coding Agent（IssueやSlackからPR作成）、Cursor Automations（Slack/GitHub等のイベント駆動でクラウド実行）、Devin（クラウド上の自律型エージェント）、Claude Code Scheduled Tasks（クラウドでの定期実行）など、既に複数のサービスが提供している。機能面でこれらに勝る部分はない。

自作した動機は、**LLMエージェントの設計を自分の手で組むこと自体に価値があった**からだ。APIを直接叩いてツール定義・状態管理・コスト制御・ジョブ実行基盤を一から設計することで、既存サービスがブラックボックスにしている部分——エージェントループの制御、トークンコストの最適化、LLMの出力形式の制約、サーバーレスでの非同期ジョブ管理——を自分で判断し実装する経験が得られた。この記事では、その設計判断の中身を書く。

## 2フェーズのエージェントループ

Agent Engineの核心は `internal/agent` パッケージにある。「Gathering（情報収集）」と「Generating（成果物生成）」の2フェーズで動作する。

### なぜ2フェーズに分けるか

情報収集から成果物生成まで会話履歴を引き継ぎながらAPIを繰り返し呼ぶ方式だと、毎回のリクエストに過去の全履歴を含める必要があるため（Claude APIはステートレス）、ツールコール履歴の蓄積でリクエストごとの入力トークンが増大し、コストが膨張する。さらにClaude APIは応答が `max_tokens` に達すると生成を途中で打ち切るため、出力が途切れるリスクもある。Gatheringフェーズでリポジトリを読み込み、テキストサマリと `fileCache` に集約してから、Generatingフェーズで**新しいコンテキスト**に詰め込んで生成することで、不要なツールコール履歴を省いたコンパクトなコンテキストで成果物を生成できる。

### Phase 1: Gathering

Gatheringフェーズはループで動く。ループ上限は15イテレーション、累積出力トークン上限は32,768。システムプロンプトで「情報が十分になったらツールを呼ばずにテキストでサマリを書け」と指示しており、LLMがテキストのみ（ツールコールなし）で応答した場合、それが分析サマリと判断してフェーズを終了する。

イテレーションが増えると会話履歴が肥大化するため、古いツール結果をトリミングする。

```
const (
    keepRecentIterations = 3     // 直近3イテレーションは完全保持
    trimContentThreshold = 500   // 500バイト以下のツール結果はトリミングしない
    trimPreviewLines     = 20    // トリミング時に先頭20行だけ残す
)
```

読み込んだファイルの完全な内容は `fileCache`（Go側のインメモリマップ `map[string]string`）に保存される。これはLLMのコンテキストウィンドウの外にあるため、会話履歴がトリミングされてもファイル内容は失われない。Generatingフェーズでは、このキャッシュからファイル内容を新しいコンテキストに詰め直す。

### Phase 2: Generating

Gatheringの結果を新しいコンテキストに詰め込み、**単一のLLMコール**で成果物を生成する。GatheringフェーズとはMaxTokensの予算が独立している。

```
const generatingMaxTokens = 32768

func (a *Agent) generatingPhase(ctx context.Context, prompt string, gathering *gatheringResult) (*RunResult, error) {
    contextMsg := buildGeneratingContext(prompt, gathering.summary, gathering.fileCache, gathering.messages)
    messages := []llm.Message{{Role: llm.RoleUser, Content: contextMsg}}

    opts := buildGeneratingSendOptions()          // deliver_result のみ、ToolChoice強制
    opts.MaxTokens = generatingMaxTokens

    resp, err := a.llm.SendMessage(ctx, GeneratingSystemPrompt, messages, opts)
    // ...
}
```

`buildGeneratingContext` は以下の構造でコンテキストを組み立てる。

1. **Original Request**: ユーザーの元のプロンプト
2. **User Clarifications**: Q&Aがあれば追加
3. **Your Analysis**: Gatheringフェーズのテキストサマリ
4. **File Contents**: `fileCache` のファイル内容全体

前述のToolChoice強制（`Type: "tool"`）に加えて `Name: "deliver_result"` を指定することで、LLMは必ずこの特定のツールを呼ぶ。応答のJSONを `AgentResponse` にアンマーシャルして返す。

### Review Loop: モデル分離による品質担保

code/new\_repo（後述のツール設計を参照）の成果物に対して、自動レビュー→修正のサイクルを最大3回実行する。

```
type Agent struct {
    llm       llm.Client   // Gathering + Generating (Sonnet)
    reviewLLM llm.Client   // Review + Rewrite (Opus)
    github    github.API
    owner     string
}
```

**実装にはSonnet、レビューにはOpus**を使う。LLMが自身の生成物を評価する際に自己選好バイアスがかかることが指摘されており（[Panickssery et al., 2024 "LLM Evaluators Recognize and Favor Their Own Generations"](https://arxiv.org/abs/2404.13076)）、同じモデルが5段階評価で自身の出力を0.5〜1.0ポイント高く評価する傾向が報告されている。ただしこれらの研究は主に自然言語評価が対象で、コードレビューに特化した検証は少ない。SonnetとOpusは同じClaude系列内のモデルではあるが、異なるモデル、特により高性能なモデルでレビューすることで、生成モデルの系統的な盲点を補完できる可能性を考慮してこの構成にしている。

レビューは4軸でスコアリングし、平均7.0以上で合格としている。

```
type ReviewScores struct {
    Correctness     float64 `json:"correctness"`     // 正確性
    Security        float64 `json:"security"`        // セキュリティ
    Maintainability float64 `json:"maintainability"` // 保守性
    Completeness    float64 `json:"completeness"`    // 完全性
}
```

Rewriteにはminorを除いたissueのみを渡す。「指摘された問題だけを修正せよ、無関係な変更をするな」とプロンプトで明示している。

収束しない場合の打ち切り条件は以下の5つ。

1. スコア閾値到達（avg >= 7.0）
2. スコア改善の停滞（2ラウンドで0.1未満の改善）
3. 同一指摘の繰り返し（同じ `issue.Message` が3回出現）
4. minorのみ残存（合格扱い）
5. アクション可能な指摘なし（スコアは低いが具体的なissueがない → Rewriteスキップ）

同一指摘の検出は `issue.Message` の完全一致で判定している。LLMが同じ問題を異なる文言で指摘した場合は検出できないが、実用上は許容している。

## ツール設計: LLMに何を渡すか

APIを直接叩いてエージェントを作る場合、LLMに渡すツールは自分で定義する。フェーズごとにLLMに渡すツールを切り替え、各フェーズで実行可能な操作を最小限にしている。

Claude APIの `tool_choice` パラメータで、LLMのツール使用を制御できる。`auto` ではLLMがツールを呼ぶかテキストで応答するかを自発的に選ぶ。`tool` では指定したツールの呼び出しが強制され、LLMはテキスト応答を返せず必ずそのツールのJSON引数を生成する。

| フェーズ | 利用可能ツール | ToolChoice | MaxTokens |
| --- | --- | --- | --- |
| Gathering | `list_repo_files`, `read_repo_file`, `ask_user_question` | auto | min(出力トークン予算の残量, 16384) |
| Generating | `deliver_result` | tool（強制） | 32768 |
| Review | `submit_review` | tool（強制） | 8192 |
| Rewrite | `deliver_result` | tool（強制） | 16384 |

Gatheringフェーズでは**読み取りのみ**。Generatingフェーズでは**成果物の宣言のみ**。

LLMの出力は「**何を作るか**」の宣言（JSON）であり、実際の書き込みはAgent Engineが制御する。Generatingフェーズで `deliver_result` を呼ぶと、LLMは以下の構造体に相当するJSONを返す。

```
type AgentResponse struct {
    Type            string       `json:"type"`              // "text", "code", "new_repo", "file"
    Content         string       `json:"content,omitempty"` // text用
    Repo            string       `json:"repo,omitempty"`
    RepoDescription string       `json:"repo_description,omitempty"` // new_repo用
    Title           string       `json:"title,omitempty"`   // PR title
    Description     string       `json:"description,omitempty"` // PR description
    Files           []OutputFile `json:"files,omitempty"`
}
```

Agent Engine側のExecutorは、この `type` に応じて配信先を振り分ける。

* `code`: 既存リポジトリにブランチを作成し、GitHub PR を作成
* `new_repo`: 新規リポジトリを作成した上で PR を作成
* `file`: S3にアップロードし、署名付きURL（24時間有効）をDiscordに送信
* `text`: Discordにテキストメッセージを送信

LLMは `type` の選択と `files` の内容を通じて「何を作るか」を決められる。しかし、書き込みの実行方法（GitHub APIの認証、ブランチ名の命名規則、S3のパス構造、署名付きURLの生成等）はAgent Engineが制御する。LLMが触れるのはスキーマの入力側だけであり、認証情報やインフラへの直接アクセスは持たない。

## コスト制御: 4層のトークン最適化

エージェントはループでAPIを何度も呼ぶため、コスト管理が重要になる。出力品質を定量測定する評価フレームワーク（後述）での計測中にレート制限エラーが頻発し、Gatheringフェーズのトークン消費が課題であることが明らかになった。原因はすでにキャッシュしたファイルの重複取得、関連のないファイルの大量読み込み、十分な情報が集まっても収集を続ける傾向の3つである。

### Layer 1: 重複ファイル読み取りの防止

`fileCache` でGathering中に読んだファイルを追跡し、同じファイルへの再取得をブロックする。

```
if tc.Name == "read_repo_file" {
    cacheKey := fileCacheKey(tc.InputJSON)
    if cacheKey != "" {
        if _, already := fileCache[cacheKey]; already {
            toolResults = append(toolResults, llm.ToolResultBlock{
                ToolUseID: tc.ID,
                Content:   fmt.Sprintf("[Already read] %s — this file has already been read and its full content is cached. ...", cacheKey),
            })
            continue
        }
    }
}
```

重複取得が発生する原因は `trimConversation` にある。古いイテレーションのツール結果を先頭20行にトリミングするため、LLMはファイルの全文がなくなったと判断して同じファイルを再度取得しようとする。合成メッセージで「キャッシュ済み、Generatingフェーズで利用可能」と明示することでこれを防ぐ。ゼロコストの最適化で、品質への影響はない。

### Layer 2: 動的入力トークン予算

Gatheringフェーズに入力トークン予算（80,000トークン）を設定し、超過時にサマリ生成を強制する。

```
const maxGatheringInputTokens = 80000

// ループ内で
if totalInput >= maxGatheringInputTokens {
    slog.Warn("gathering input token budget exceeded, forcing summary",
        "total_input", totalInput, "limit", maxGatheringInputTokens)
    break
}
```

イテレーション数のハードリミットではなく入力トークン予算にした理由は、タスクの複雑さに適応するためである。少数のファイルを読む単純タスクは少ないイテレーションで終了し、多数のファイルを読む複雑タスクはイテレーション数に制約されない。コスト（≒トークン数）を直接制約する方がイテレーション数という代理指標よりも効果的である。

### Layer 3: ファイルツリーの事前フィルタリング

`list_repo_files` の結果が返った直後に、短い応答だけを求めるLLMコール（MaxTokens: 1024。Generatingフェーズの32,768と比べて約1/30）でタスクに関連するファイルを選出し、ソフトサジェスチョンとして追記する。

```
func (a *Agent) preFilterFiles(ctx context.Context, prompt, fileTree string) string {
    // fileTree → pathList, pathsJSON の構築は省略
    userMsg := fmt.Sprintf("Task: %s\n\nRepository files:\n%s", prompt, string(pathsJSON))
    messages := []llm.Message{{Role: llm.RoleUser, Content: userMsg}}
    opts := &llm.SendOptions{MaxTokens: preFilterMaxTokens}

    resp, err := a.llm.SendMessage(ctx, PreFilterSystemPromptWith(len(pathList)), messages, opts)
    // レスポンスはJSON配列のファイルパスリスト
}
```

サジェスチョン数はリポジトリ規模に連動する（下限 `max(3, totalFiles/10)`、上限 `min(totalFiles/3, 15)`）。厳密なフィルタリング（選出外を読めなくする）ではなく、エージェントは任意のファイルを読む自由を持つ。事前フィルタが重要なファイルを見落とすリスクを回避するためである。Layer 3の定量的なトークン削減効果は計測していない。定性的には、エージェントが無関係なファイルを大量に読み込む傾向が軽減されることを確認している。

### Layer 4: 選択的プロンプトキャッシング

Anthropicのプロンプトキャッシング（`cache_control: {"type": "ephemeral"}`）は、通常の入力トークンコストに対してキャッシュ作成時が1.25倍、キャッシュ読み取り時が0.1倍になる。**同一プレフィックスを持つ後続コールがある場合にのみ有効**なので、無条件に適用するとキャッシュ作成コストだけが積み上がる。

キャッシュを有効にするかどうかは、後続コールでキャッシュが読まれる見込みがあるかで判断する。

| フェーズ | DisableCache | 理由 |
| --- | --- | --- |
| Gathering 1回目 | true | トークン量が少なく1.25倍コストに見合わない。後続でメッセージ構造が変わるためヒットもしない |
| Gathering 2回目以降 | false | 前回のプレフィックスがキャッシュヒットする。ここがキャッシュの主な恩恵 |
| Gathering 予算80%以降 | true | 次のコールは強制サマリで異なるメッセージになる可能性が高い |
| Generating / Review / Rewrite | true | 単発コール。後続リクエストなし |

評価での計測結果（12ケース）では、無条件キャッシュから選択的キャッシュへの変更で**キャッシュ作成トークンが392Kから127Kに減少**し、実質的なトークン節約量が5倍に改善した。品質（pass\_rate 1.0）は維持されている。

## ほぼゼロコスト待機のインフラ構成

個人開発でLLMエージェントを動かすインフラの最大の問題は、**ジョブがない時間帯にもコストがかかること**。Nemuriは常時稼働するリソースを一切持たない。

| コンポーネント | コスト特性 |
| --- | --- |
| ECS Fargate | ジョブ実行時間に比例（0.25 vCPU / 512 MiB） |
| Lambda（Ingress / Runner） | 128MB、呼び出し回数に比例 |
| DynamoDB | PAY\_PER\_REQUEST、TTLで自動削除 |
| S3 | ライフサイクルルールで自動削除 |
| SQS | 標準キュー + DLQ |

### なぜSQS + Runner Lambdaが必要か

Discordのインタラクション応答期限は3秒。Ingress Lambda内で署名検証、DynamoDB書き込み、さらに `RunTask` のAPI呼び出しまで行うと、3秒を超えるリスクがある。SQS `SendMessage` は同一リージョンで数十ms程度で完了するため、`RunTask` をSQS経由で後段のLambdaに委譲することで、この時間的制約を安全にクリアできる。

「Discordへの応答だけ先に返して、goroutineで `RunTask` を呼べばSQSもRunner Lambdaも不要では？」と思うかもしれない。しかし、**Lambdaはハンドラが `return` した時点で実行環境がフリーズ（一時停止）される**ため、バックグラウンドのgoroutineは中断され、再開される保証もない（実行環境自体が破棄される可能性もある）。これはGoに限らずどのランタイムでも同じで、Lambdaの「リクエスト→レスポンス」同期モデルに起因する制約である。

SQSを挟むことでこの制約を回避しつつ、リトライ（visibility timeout後の再配信）やDLQによるジョブ消失防止も得られる。また、Ingress LambdaはSQSにメッセージを投げるだけで、後段がECSかLambdaかを知る必要がない。

SQSメッセージのライフサイクルはRunner Lambdaの成否に連動する。AWSのSQS-Lambda統合（イベントソースマッピング）では、Lambdaが正常終了するとSQSメッセージを自動削除する仕組みになっている。つまり**ECSタスクが起動した時点でSQSメッセージは既に削除されている**。ECSタスク内部のエラーではSQS経由の自動リトライは発生しない。LLM APIコストが1ジョブあたり数百円かかることがあるため、失敗原因を確認せずにリトライするとコストだけが積み上がるリスクがあるからである。ECSタスクがエラーで終了した場合、DynamoDB上のジョブ状態をFAILEDに遷移させ、エラーメッセージを保存した上で、Discordを通じてユーザーに通知する。FAILED状態からの自動リトライは行わない。

### 1ジョブ = 1 ECSタスク

ECS Serviceとして常駐させてキューをポーリングする方式も考えたが、ワンショット実行を選択した。ジョブがない時間帯のコストがゼロになる、タスク間でメモリリークが蓄積しない、SQSキュー深度による自然なスケーリングが得られる。デメリットのコールドスタート（数十秒）は、ジョブ実行時間が数分単位のため許容範囲。

### DynamoDB vs RDS

RDSは最小構成でも常時稼働が必要で、「常時起動するインフラを持たない」原則に反する。Aurora Serverless v2でもスケールダウンの下限がある。DynamoDBはPAY\_PER\_REQUESTでゼロリクエスト時のコストがほぼゼロで、条件付き書き込みで分散ロックも実現できる。ジョブ間のリレーションが不要な単純なキーバリュー構造なので、RDBのメリットも薄い。

### 状態管理: DynamoDBの条件付き書き込み

ジョブの状態遷移は6状態・固定遷移で管理する:

ロック取得はDynamoDBの条件付き書き込みで実現する。

```
func (s *Store) AcquireLock(ctx context.Context, jobID, workerID string) error {
    now := time.Now().Unix()
    expired := now - int64(HeartbeatExpiry.Seconds()) // HeartbeatExpiry = 10分

    _, err := s.client.UpdateItem(ctx, &dynamodb.UpdateItemInput{
        Key: map[string]types.AttributeValue{
            "job_id": &types.AttributeValueMemberS{Value: jobID},
        },
        UpdateExpression: aws.String(
            "SET #state = :running, worker_id = :wid, heartbeat_at = :now, " +
            "updated_at = :now, version = version + :one"),
        ConditionExpression: aws.String(
            "(#state IN (:init, :waiting)) AND " +
            "(attribute_not_exists(worker_id) OR worker_id = :empty OR heartbeat_at < :expired)"),
    })
    return err
}
```

条件は2つのAND: (1) stateがINITまたはWAITING\_USER\_INPUT、(2) worker\_idが未設定、空、またはheartbeat\_atが10分以上前。ハートビートは3分間隔で `heartbeat_at` のみ更新し、`version` はインクリメントしない。`version` を状態遷移時のみインクリメントする理由は、楽観的ロック（「更新時に `version` が変わっていたら競合とみなして失敗させる」排他制御）の競合をハートビートで引き起こさないためである。

### Discordスラッシュコマンド vs @メンション監視

@メンションベースのメッセージ監視はDiscord Gateway（WebSocket常時接続）が必要で、常時稼働するBotプロセスが必要になる。スラッシュコマンドはHTTPエンドポイント（API Gateway + Lambda）で受けられるため、サーバーレスアーキテクチャと整合する。

## 品質を計測する仕組み

プロンプト調整やトークン最適化が品質に影響しないことを確認するため、評価フレームワークを構築した。Agent Engineをローカルで実行し、実際のClaude APIとモックされたGitHub APIで出力品質を定量測定する。GitHub APIをモックするのは、固定されたリポジトリスナップショットに対してテストを実行し、結果を再現可能にするためである。Claude APIは実際に呼び出し、モデルの実際の出力品質とトークン消費量を計測する。

```
type TestCase struct {
    ID               string            `json:"id"`
    Prompt           string            `json:"prompt"`
    Category         Category          `json:"category"`
    Fixture          Fixture           `json:"fixture"`
    QuestionHandling *QuestionHandling `json:"question_handling,omitempty"`
    Expectations     []Expectation     `json:"expectations"`
    Rubric           []RubricItem      `json:"rubric"`
}
```

品質測定は2層構造:

* **pass\_rate**: 各トライアルの全expectationが通ればpass。バイナリ判定でリグレッション検出に使う
* **quality\_score**: 重み付きルーブリックで0.0〜1.0のスコアを算出。品質改善の計測に使う

expectationは意図的に緩くしており、現行システムではほぼすべて通過する（pass\_rate ≈ 1.0）。pass\_rateが1.0のままでは改善を計測できないため、ルーブリックによる連続的なスコアで漸進的な進歩を追跡する。

テストケースのプロンプトと期待値は作成後は不変（immutable）とし、追加のみ許可する。変更すると過去のベースラインとの比較が不可能になるためである。12ケースのゴールデンテストセットで、変更前後のpass\_rateとquality\_scoreを比較できる。計測なしの最適化は方向感を失う。

## まとめ

フレームワークを使わず、Claude APIを直接叩いてDiscordからGitHub PRを返すエージェントシステムをGo + AWSで実装した。設計判断をまとめる。

* **2フェーズのエージェントループ**: Gathering（情報収集）→ Generating（成果物生成）でコンテキストをリセットし、ツールコール履歴の蓄積によるコスト膨張を回避
* **ツール設計**: フェーズごとに渡すツールとToolChoiceを切り替え、LLMの出力を「宣言」に閉じ込める。実際の書き込みはAgent Engineが制御
* **レビューループ**: 実装（Sonnet）とレビュー（Opus）でモデルを分離し、5つの打ち切り条件で収束を制御
* **4層のトークン最適化**: 重複取得防止、動的入力トークン予算、ファイルツリー事前フィルタリング、選択的プロンプトキャッシング
* **ゼロコスト待機のインフラ**: 1ジョブ=1 ECSタスクのワンショット実行、SQSによる非同期連携、DynamoDB条件付き書き込みによる排他制御
* **評価フレームワーク**: 12ケースのゴールデンテストセットでpass\_rateとquality\_scoreを定量測定

実装の全詳細（会話コンテキストの永続化と質問→回答フロー、LLMクライアントのリトライ/レート制限戦略、Ingress Lambdaの分岐ロジック、ECSタスク定義とTerraformモジュール構成、評価フレームワークの設計と計測結果等）は[個人ブログの詳細版](https://dysksh.github.io/blog/posts/nemuri/)に書いている。

リポジトリ: <https://github.com/dysksh/nemuri>
