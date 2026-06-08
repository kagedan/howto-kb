---
id: "2026-06-07-思考整理アプリを作るllmコスト設計からflutter-custompainterまでの技術全記録-01"
title: "思考整理アプリを作る：LLMコスト設計からFlutter CustomPainterまでの技術全記録"
url: "https://zenn.dev/uray/articles/0e854dacd21744"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "GPT", "Python", "JavaScript"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

## はじめに

「やることが多すぎて寝つけない」

そんな課題を解決するアプリ [BubbleClear](https://bubble-clear.com/) を個人で開発しています。使い方はシンプルで、頭の中にあることを 3〜5 分で全部吐き出す → Claude Haiku 4.5 が各テーマの重みと感情スコアを分析 → バブルマップとして可視化 → 「今一番楽になれる 1 つ」を提案して終わり。

ToDo アプリではなく、**ToDo アプリに何を入れるかを決めるためのツール**です。

この記事は、LLM を組み込んだアプリの原価設計と技術的意思決定のログです。「なぜそれを選んだか」を残すことで、同じ課題に取り組む個人開発者の参考になれば幸いです。

![BubbleClearのマップ画面](https://static.zenn.studio/user-upload/2f211dac713b-20260607.png)*BubbleClearのマップ画面*

## アプリのコアコンセプト

ターゲットは複数プロジェクトを掛け持つナレッジワーカー（30〜45歳）。既存ツールとのアプローチの違いを明確に意識しています。

Day One や Rosebud はジャーナルの記録は得意ですが、「どれが一番重いか」の**定量的な可視化**がありません。Todoist や Things はタスク管理ツールであり、行動を強制します。BubbleClear は行動を強制しません。ただ「今、頭の中で何が一番重いか」を可視化して、1 つだけ選んで手放せるようにします。

その差別化の中心にあるのがバブルマップのUIです。各テーマが重さに応じた大きさの泡として浮かび、タップすると心地よく破裂してクリアになる。このあまり見かけない直感的な操作感を Flutter で実現することを目指しました。

## LLM コスト設計を先に決める理由

機能実装の前に、まず原価モデルを決めました。後から「この価格設定では原価割れする」となると、個人開発では継続が困難になるからです。

### 1 セッションの原価試算

Standard プランの想定価格は ¥380/月。ヘビーユーザーが月 30 セッション使うとして、LLM 原価を先に計算します。

```
入力  1,500 token × $1.00/Mtoken = $0.0015（≒¥0.22）
出力    800 token × $5.00/Mtoken = $0.0040（≒¥0.61）
─────────────────────────────────────────────────────
合計                               ≈ ¥0.82/セッション
ヘビーユーザー月 30 回             ≈ ¥24.6/月
¥380 に占める割合                  ≈  6.5%
```

固定費（ドメイン代 ¥131 + バッファ ¥1,000）と合わせると、有料ユーザー **3〜4 名で月次黒字** になります。この原価率が成立する前提でスタックを選んでいます。

### モデル選定の核心

Claude Sonnet 4 系は Haiku の単価が 5〜15 倍です。同じ試算をすると 1 セッション ¥4〜12。ヘビーユーザーの月次コストが ¥120〜360 になり、**Standard ¥380 の 30〜90% を LLM だけで消費します**。損益モデルが崩壊します。

GPT-4o mini も検討しましたが、2 点で Haiku を選びました。1 つ目はデータ保持ポリシーの要件です。ダンプ原文は心理的にセンシティブな内容を含むため、AI 学習に使われないことをプロバイダーが明示的に保証していることが選定条件でした。2 つ目は `tool_use` の出力安定性で、スキーマ遵守率が高いことは後述のバリデーション設計に直結します。

## Prompt Caching の実装

コスト圧縮の要は Prompt Caching です。システムプロンプト（約 1,200 token）は毎セッション変わらないため、キャッシュ対象にできます。

### なぜ `ephemeral` か

Anthropic の Prompt Caching には `ephemeral`（TTL 5 分の高速キャッシュ）と長時間キャッシュ（TTL 1 時間）があります。長時間キャッシュは書き込みコストが高くなる傾向があるため、利用頻度が予測できないベータ期間ではメリットが薄いと考えました。まずは `ephemeral` で実装し、トラフィックパターンを実測した後に最適化します。

```
# api/app/services/llm/anthropic_client.py
async def _call_full(self, text: str) -> dict:
    response = await self._client.messages.create(
        model=settings.anthropic_model,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,           # ~1,200 token の固定部
                "cache_control": {"type": "ephemeral"},  # ← system レベルのみ
            }
        ],
        tools=[_TOOL_FULL],
        tool_choice={"type": "tool", "name": "analyze_dump"},
        messages=[{"role": "user", "content": text}],
    )
    return self._extract_tool_input(response)
```

**設計方針：System と User の完全な分離**

* `system` ブロック：分類ルール・領域定義・出力フォーマット（固定 → キャッシュ対象）
* `messages[user]`：ユーザーが書き込んだダンプ原文（動的 → キャッシュ対象外）

キャッシュヒット時、入力 1,500 token のうち 1,200 token の課金が省略されます。理論上の効果は **1 セッション ¥0.82 → ¥0.66〜0.73（12〜18% 削減）** です。

ただし、キャッシュは API キー単位で管理されており、TTL 5 分以内に別のリクエストが来た場合にのみヒットします。ユーザーが 1 日 1 セッションしか使わない場合はほぼヒットしません。恩恵が実感できるのは、**複数ユーザーのリクエストが時間的に集中する規模**になってからです。初期段階では「将来のコスト最適化の布石」として実装しておき、β 期間のログでヒット率を計測してから TTL の延長（1 時間）を判断します。

### システムプロンプトの構造

キャッシュ対象にするほど固定部を大きくしたほうがヒット恩恵が増えます。そのため、できる限り多くの定義をシステムプロンプトに詰め込んでいます。

```
システムプロンプト（~1,200 token）— キャッシュ対象
├── アシスタントの役割定義
├── 7 フィールドの詳細定義（weight の意味、domain の enum 説明など）
├── 分類ルール（同一トピックの統合方法、アイテム数の上下限）
└── 出力フォーマット指示

ユーザーターン（毎回変動）— キャッシュ対象外
└── ダンプ原文（100〜1,000 字程度）
```

## Function Calling で構造化出力を強制する

LLM の出力を信頼しないことが設計の基本姿勢です。

`response_format: {"type": "json_object"}` は「JSON を返す」ことを保証しますが、**スキーマを保証しません**。フィールドが欠けたり余分なキーが入ることがあります。

`tool_use` + `tool_choice={"type":"tool","name":"analyze_dump"}` の組み合わせは、指定ツールを必ず呼ぶことを強制します。スキーマ準拠の確率が大幅に上がり、後段のバリデーションが単純になります。

```
# 7 フィールドスキーマ定義（抜粋）
_TOOL_FULL = {
    "name": "analyze_dump",
    "description": "ブレインダンプの分析結果を構造化データとして返す",
    "input_schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "label":        {"type": "string"},
                        "weight":       {"type": "number", "minimum": 0, "maximum": 1},
                        "domain":       {"type": "string",
                                         "enum": ["work","home","health","relationship",
                                                  "money","personal","uncategorized"]},
                        "time_horizon": {"type": "string",
                                         "enum": ["past","now","near","long"]},
                        "urgency":      {"type": "number", "minimum": 0, "maximum": 1},
                        "emotion":      {"type": "number", "minimum": -1.0, "maximum": 1.0},
                        "summary":      {"type": "string"},
                    },
                    "required": ["label","weight","domain","time_horizon",
                                 "urgency","emotion","summary"],
                }
            }
        },
        "required": ["items"],
    },
}
```

`tool_use` が通った後も バックエンド側でさらに Pydantic による再バリデーションを行います。JSON Schema の定義だけでは、実行時における境界値の細かなバリデーションがすり抜ける可能性があるためです。

### 3 段階フォールバック

LLM は確率的な機械です。「必ず動く」を保証するために 3 段階のフォールバックを設けています。

```
async def analyze(self, text: str) -> AnalysisResponse:
    # 1回目（フル 7 フィールドスキーマ）
    raw = await self._call_full(text)
    try:
        items = _parse_tool_input(raw)
        return AnalysisResponse(items=items)
    except (ValidationError, KeyError, TypeError):
        logger.warning("1回目の Pydantic バリデーション失敗。リトライ中…")

    # 2回目（同スキーマで再試行）
    raw = await self._call_full(text)
    try:
        items = _parse_tool_input(raw)
        return AnalysisResponse(items=items)
    except (ValidationError, KeyError, TypeError):
        logger.warning("2回目も失敗。簡易スキーマでフォールバック中…")

    # フォールバック（簡易 2 フィールドスキーマ）
    raw = await self._call_simple(text)
    items = _parse_simple_input(raw)   # label + weight のみ、他はデフォルト値で補完
    return AnalysisResponse(items=items, is_fallback=True)
```

最悪の場合でも、バブルの描画に必要な `label` と `weight` さえ取得できれば、ユーザーの体験を損なわずにバブルマップを描画できます。また、API自体のエラー発生時には、クォータの消費処理を巻き戻す（返金する）仕組みを API router 層に組み込んでいます。

## Flutter CustomPainter で 60fps バブルマップを作る

### なぜ CustomPainter か

React Native などの他フレームワークで同様の描画を行う場合、JavaScript ブリッジを介した描画処理によって 60fps を維持するのが難しい局面があります。Flutter の `CustomPainter` は Skia / Impeller エンジンを直接操作するため、OS の UI ツリーを一切経由せずに描画できます。30〜50 個のバブルを 60fps で動かす要件には、これが最も適した選択肢でした。

### LOD（Level of Detail）パイプライン

ズームアウトして画面上で小さくなったバブルに、グラデーションやテキストを描画するのは無駄です。実効半径（`radius × viewScale`）に応じて描画内容を 4 段階で切り替えています。

```
// app/lib/features/map/presentation/bubble_painter.dart
static const double _lodSkip     = 4.0;   // 実効半径 < 4px → 描画スキップ
static const double _lodGradient = 14.0;  // < 14px → 単色フラット
static const double _lodText     = 24.0;  // < 24px → テキスト非表示

void _drawBubble(Canvas canvas, int i, double scale, {required bool emphasized}) {
  final effectiveR = r * scale;

  if (effectiveR < _lodSkip) return;              // LOD 0: 完全スキップ

  if (effectiveR < _lodGradient) {
    canvas.drawCircle(pos, r, _flatPaints[i]);    // LOD 1: 単色塗りのみ
    return;
  }

  _updateCache(i, r, baseR);                      // LOD 2: inner glow + border
  canvas.drawCircle(Offset.zero, r, cache.body!);
  canvas.drawCircle(Offset(0, -r * 0.18), r * 0.7, cache.innerGlow!);
  canvas.drawCircle(Offset.zero, r, cache.border!);

  if (effectiveR >= _lodText) {                   // LOD 3: テキスト追加
    cache.tp?.paint(canvas, Offset(-tp.width / 2, -tp.height / 2));
  }
}
```

キャッシュ更新（`_updateCache`）は、半径差が 0.5px 以下の場合はスキップします。アニメーション中に毎フレーム `Paint` オブジェクトを再生成するのを避けるためです。

### Deterministic パーティクル（破裂演出）

バブルをタップして破裂させた際、エフェクトが毎回完全に同じだと単調になり、逆に完全なランダムだと意図しない挙動になることがあります。そこで「毎回ランダムに見えて、特定のバブルは常に同じ弾け方をする」という決定論的なアニメーションを設計しました。

```
// sin の小数部を利用した古典的なハッシュ-to-float。整数入力から [0, 1) を生成
double _hash(int n) {
  final x = math.sin(n * 12.9898 + 78.233) * 43758.5453;
  return x - x.floorToDouble();
}

// per-pop seed を畳み込んだ決定論的な疑似乱数
double _rnd(int seed, int k, int salt) =>
    _hash(seed * 2654435761 + k * 40503 + salt * 7919);
```

バブルのデータベースIDや座標値からハッシュのベース（seed）を計算し、粒子インデックス`k` や、用途（角度、初速、サイズ）を分ける`salt` を掛け合わせて疑似乱数を生成します。  
これにより、同じバブルをタップしたときは物理挙動に一貫性を持たせつつ、バブルごとに全く異なる豊かな破裂エフェクトを表現できます。

## アーキテクチャ選定の意思決定（ADR 運用）

各技術選定を Architecture Decision Record（ADR）として `docs/adr/` に記録しています。「何を棄却したか」と「なぜ変えたか」を残すことが目的で、将来の自分や引き継ぎ相手に意思決定の文脈を伝えます。

| 選択項目 | 採用 | 主な棄却候補 | 決め手 |
| --- | --- | --- | --- |
| モバイル | Flutter | React Native / KMP | Skia 60fps 最短経路、iOS/Android 1 コードベース |
| バックエンド | Hono + Cloudflare Workers | Railway / Render | 無料枠 10 万 req/日、V8 isolate でコールドスタートなし |
| LLM | Claude Haiku 4.5 | GPT-4o mini / Sonnet | データ非保持ポリシー、tool\_use 安定性、原価モデル |
| 認証 | Supabase Auth（Magic Link） | Firebase Auth / Auth0 | PostgreSQL 統合、RLS 一体化 |

現行バックエンドは FastAPI（Python）ですが、Cloudflare Workers 移行に備えて LLM 呼び出し層を環境変数 1 行で切り替えられるよう抽象化しています（`LLM_PROVIDER=anthropic|bedrock`）。Haiku の世代更新も `ANTHROPIC_MODEL` の差し替えだけで完結します。

## データプライバシー設計

メンタルヘルス領域では「保管しない」を売ることが差別化になります。

* ダンプ原文は 30〜90 日後に `pg_cron` で自動削除
* 推移グラフに使うのはテーマの **SHA256 ハッシュ値のみ**（原文は不要）
* 退会時は 30 秒以内に全データを物理削除できる設計

ハッシュ値だけを長期保管することで、「3 週連続で同じテーマが出ている」という慢性化検出が原文なしで可能になります。GDPR / APPI のデータ最小化原則とも整合します。

## まとめ

個人開発で LLM を組み込むとき、コスト設計を後回しにすると「機能が完成したが原価モデルが成立しない」という結末になりかねません。

今回の BubbleClear では：

* **Haiku 4.5** で1セッション約¥0.82の原価に抑え、有料会員 3〜4 名で黒字化するモデルを構築
* **Prompt Caching** を活用し、不変のシステムプロンプトをキャッシュすることで最大 15% 前後のランダムコストをさらに削減
* **Function Calling + Pydantic** 、さらに3段階のフォールバックにより「どんな入力でもUIが崩れない」堅牢性を確保
* **Flutter CustomPainter** で LOD や決定論的なエフェクトを工夫し、低負荷かつリッチな 60fps レンダリングを実現
* **ADR（技術意思決定記録）** を残すことで、将来の変更コストを低減

現在 MVP を開発中です。一定の品質基準を満たせば Google Play / App Store でのリリースを目指しています。今後も実装の中で得られた知見を共有していきますので、興味のある方はぜひフォローいただけると励みになります。
