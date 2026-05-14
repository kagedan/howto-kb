---
id: "2026-05-13-claude-codeのskillを改善する-autoresearchとevals-skillsを使-01"
title: "Claude CodeのSkillを改善する — autoresearchとevals-skillsを使った実践ガイド"
url: "https://zenn.dev/salt2/articles/af6b15b68e3fbe"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "LLM", "Python"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

!

**3行まとめ**

* evalを正しく設計してからautoresearchに渡すと、AIエージェントが自律的にSKILL.mdを改善し続けます
* 順序を守らないと、スコアは上がっても実際の品質が下がります
* error-diagnosis Skillをこの手順で改善したところ、パス率が68%から100%まで上がりました

---

## はじめに

はじめまして、SALT2でAIエンジニアをしている岩倉（@KazukiIwakura）です。

自分が日常的に使っているerror-diagnosis Skill（エラーメッセージを入力すると、原因・解決手順・再発防止策を診断するSkill）の出力を眺めていたとき、「なんか壊れてるな」と感じることが増えてきました。ただ、何がどう壊れているのかを言語化できていなかったため、やみくもにSKILL.mdを書き直しても改善した実感がありませんでした。

そこで試したのが、autoresearch-skillとevals-skillsを組み合わせた改善フローです。この記事では、その手順と実際に何が変わったかを紹介します。

**想定読者：** Claude CodeのSkillsを日常的に使っていて、品質改善を体系的にやりたい方。

---

## autoresearchとevals-skillsとは

### autoresearch-skill

AIエージェントが自律的に「変更 → 評価 → keep/revert」のループを繰り返してSKILL.mdを改善し続けるツールです。元はAndrej Karpathyが提唱した手法（MLモデルの学習コードを自律改善するOSS）を、SKILL.mdのプロンプト改善に転用したものです。

変更は1回につき1箇所だけ行い、evalのスコアが上がればkeep、上がらなければrevertします。元のSKILL.mdは自動バックアップされるので、いつでも戻せます。

### evals-skills

evalの設計・検証を支援するSkill群です（Hamel Husainが公開）。チャットで話しかけるツールではなく、コーディングエージェントが手元のトレースファイルやevalコードに対して動作します。実際のトレースデータがある状態で使うものです。

今回使う4つのSkillはこちらです。

| Skill | やること |
| --- | --- |
| `error-analysis` | トレースを読んで失敗パターンを分類する |
| `write-judge-prompt` | evalプロンプトを設計する |
| `validate-evaluator` | evalが人間の判断と一致しているか検証する |
| `generate-synthetic-data` | テスト入力を生成する |

### インストール

**evals-skills**

```
claude mcp add --transport http evals-skills https://...
# または settings.json に手動で追加（詳細はevals-skillsのREADME参照）
```

**autoresearch-skill**

```
curl -o autoresearch-SKILL.md \
  https://raw.githubusercontent.com/olelehmann100kMRR/autoresearch-skill/main/SKILL.md

# グローバルインストール
mkdir -p ~/.claude/skills/autoresearch
mv autoresearch-SKILL.md ~/.claude/skills/autoresearch/SKILL.md
```

配置後はClaude Codeを再起動します。

---

## やってみた — error-diagnosis Skillを改善する

### Step 1：出力を20件読む

まずSkillを繰り返し動かして、出力を20件ほど読みます。この作業は省略できません。ここで失敗パターンを自分の目で把握していないと、後のevalが「想像上の失敗」を測るものになり、autoresearchが的外れな最適化をします。

読むときに意識したこと：

* どんな入力のとき壊れるか
* 壊れたとき出力はどう崩れるか
* 最初に何が失敗しているか（連鎖的な問題の根本）

気づいたことはフリーフォームでメモしておきます。分類は次のステップでやります。入力はバリエーションを意識します（短い/長い、Next.js/Python、明確なエラー/曖昧なエラーなど）。

### Step 2：error-analysisで失敗を分類する

Step 1のメモをもとに、`error-analysis` Skillを使って失敗パターンをカテゴリに整理します。

以下のように話しかけて起動します。

```
/error-analysis

このSkill（error-diagnosis）の出力ログがあります。
失敗パターンを分析して分類してください。
ログファイル：./logs.md
```

エージェントから「パイプラインは何をするか」「懸念点は何か」などを聞かれるので答えます。その後、エージェントはトレースファイルを読み込みながら以下の流れで進めます。

1. 各トレースについてPass/Failと何が問題だったかを確認する
2. 30〜50件読んだ時点で、似た失敗をグループ化する
3. グループ化の結果をあなたと一緒に確認・調整する
4. 全件をカテゴリ別にラベリングする
5. カテゴリ別の失敗率を出して優先順位をつける

自分のケースでは、以下の3カテゴリに整理されました。

**カテゴリA：テンプレート出力の崩れ**  
`【エラーの種類】` などのフォーマット記号の脱落・重複・余分なスペース。規定のセクション（エラーの種類・原因・解決手順・再発防止策）が一部消えているケースも含みます。

**カテゴリC：技術前提の陳腐化**  
Pages Router / CommonJSなど旧来の前提で診断が書かれており、現代の主流（App Router / ESM）が後回しになっている。Next.js関連エラーでApp Routerの解決策が末尾の一行だけになっていたり、`__dirname` を推奨しているがESM代替（`import.meta.url`）への言及がないケースが典型です。

**カテゴリD：エッジケースへの言及漏れ**  
推奨は技術的に正しいが、よく知られた罠・例外への言及がなくそのまま使うとハマる。`isdigit()` を推奨しているが `'²'.isdigit()` が `True` になる問題に触れていないケースや、修正手順に破壊的変更が伴うのに警告がないケースが見つかりました。

評価カテゴリは3〜6個が適切です。多すぎるとSkillがチェックリストを暗記するだけになります。

### Step 3：evalを設計して検証する

#### evalプロンプトを設計する

`write-judge-prompt` Skillを使います。Step 2の評価カテゴリをもとに、Pass/Fail形式のevalプロンプトを設計します。

設計前に用意するもの：

* Step 2で整理したカテゴリとチェック項目
* ラベリング済みのトレース（各カテゴリでPass/Failの典型例を3件以上）

起動例：

```
/write-judge-prompt

失敗カテゴリがAとBの2つあります。
各カテゴリのPass/Fail判定をするevalプロンプトを設計してください。

カテゴリA：〇〇という失敗
カテゴリB：〇〇という失敗

Pass例：（実際のPass出力を貼る）
Fail例（カテゴリA）：（失敗した出力を貼る）
Fail例（カテゴリB）：（失敗した出力を貼る）
```

evalプロンプトには以下の4要素が必要です。

1. **タスクと評価基準** — ジャッジが何を評価するかを1文で
2. **Pass/Failの定義** — 具体的に、厳密に
3. **Few-shotの例** — ラベル済みトレースから（clear Pass / clear Fail / ボーダーラインの3種）
4. **構造化出力フォーマット** — `{"critique": "...", "result": "Pass または Fail"}`

`critique` を先に書かせること（判定の前に根拠を述べさせること）でジャッジの精度が上がります。

#### evalを検証する

`validate-evaluator` Skillで、設計したevalが人間の判断と一致しているか検証します。

必要なデータ：

* 人間がラベリングしたトレース約20件（PassとFailを半々）
* これをtrain（10〜20%）/ dev（40〜45%）/ test（40〜45%）に分割

検証の流れ：

1. ジャッジをdev setで実行してTPRとTNRを計算する
2. 不一致のケースを確認してevalプロンプトを修正する
3. TPRとTNRがどちらも90%以上になるまで繰り返す
4. 最後にtest setで1回だけ実行して最終スコアを記録する

```
from sklearn.metrics import confusion_matrix

tn, fp, fn, tp = confusion_matrix(human_labels, evaluator_labels,
                                   labels=['Fail', 'Pass']).ravel()
tpr = tp / (tp + fn)  # 人間がPassのとき、ジャッジもPassと言う率
tnr = tn / (tn + fp)  # 人間がFailのとき、ジャッジもFailと言う率
```

**目標：TPR > 90% かつ TNR > 90%**（最低ラインはどちらも80%）

この検証を省略すると、evalの判定ミスに合わせてSkillが最適化されます。スコアは上がっても実際の品質は下がります。

### Step 4：テスト入力を生成する

`generate-synthetic-data` Skillでautoresearchに渡すテスト入力を作ります。

「テストケースを20件生成して」とだけ頼むとLLMは似たようなケースを繰り返します。このSkillは「次元ベースのタプル生成」というアプローチで、バリエーションの軸をあらかじめ定義してから組み合わせを作ります。

今回定義した次元：

```
Dimension 1：言語/フレームワーク
- next-js-api / node-fs / python-numeric / node-module

Dimension 2：失敗誘発パターン
- 旧パターンを誘うケース / クリーンケース（Pass生成用）

Dimension 3：エラーの明確さ
- 明確 / 曖昧 / 混在
```

起動例：

```
/generate-synthetic-data

Skillは〇〇（Skillの説明）です。
以下の失敗パターンを誘発しやすいテスト入力を生成してください。

失敗パターン：
- 〇〇なエラーメッセージでフォーマットが崩れやすい
- 〇〇なエラーでは出力が欠落しやすい
```

次元を定義するとエージェントが20タプルのドラフトを提案します。確認・調整したあと、各タプルを実際のエラーメッセージ（スタックトレース付き）に変換します。autoresearchに渡すのは**3〜5件**に絞ります。

### Step 5：autoresearchを実行する

準備が整ったら起動します。**autoresearchのループは長時間動くため、別のターミナルウィンドウで実行することを推奨します。**

```
# 別ターミナルで
cd /your-project && claude
```

起動したら以下の形式で貼り付けます。

```
/autosearch-skill

Target skill: ~/.claude/skills/error-diagnosis/SKILL.md

Test inputs:
1. （Step 4で生成したT1のエラーメッセージ）
2. （T2のエラーメッセージ）
3. （T3のエラーメッセージ）

Eval criteria:
EVAL 1: ...（Step 3で設計したevalプロンプト）
EVAL 2: ...

Runs per experiment: 5
Budget cap: なし（手動停止）
```

エージェントはまずベースライン（experiment #0）を計測してスコアを報告します。続行確認が来たら「yes」と答えるとループが始まります。

エージェントは以下の6項目を順番に確認してから実験を開始します。

| 確認項目 | 答え方 |
| --- | --- |
| 対象skill | SKILL.mdのパスを伝える |
| テスト入力 | Step 4で生成した3〜5件を貼り付ける |
| evalチェックリスト | Step 3で検証済みのevalプロンプトを貼り付ける |
| 1実験あたりの実行回数 | デフォルトは5（多いほど信頼性が上がるが時間とコストが増える） |
| 実験サイクルの間隔 | デフォルトは2分 |
| バジェットキャップ | 上限を決めたい場合は回数を指定、なければ「なし」 |

ループが始まると以下のファイルが生成されます。

```
autoresearch-error-diagnosis/
├── dashboard.html       # スコア推移のライブダッシュボード
├── results.tsv          # 全実験のスコアログ
├── changelog.md         # 各変更の詳細記録
└── SKILL.md.baseline    # 改善前のバックアップ
```

3回連続でパス率95%以上を記録するか、バジェットキャップに達すると自動停止します。

---

## 結果

![](https://static.zenn.studio/user-upload/c33da8830069-20260325.png)

### スコアの変化

|  | パス率 |
| --- | --- |
| ベースライン（改善前） | 68% |
| 改善後 | 100% |

実験は4回で、すべてkeepでした。

| 実験 | スコア | パス率 | 結果 |
| --- | --- | --- | --- |
| 0b（baseline） | 17/25 | 68% | baseline |
| 1 | 21/25 | 84% | keep |
| 2 | 23/25 | 92% | keep |
| 3 | 24/25 | 96% | keep |
| 4 | 25/25 | 100% | keep ✅ |

### autoresearchがkeepした変更

最終的にkeepされた変更は4点でした。

**変更1：バッククォートをMarkdown禁止記号リストに明示追加（+16%）**

```
# 変更前
出力はプレーンテキストのみ。Markdownの記号（#、**、---など）は一切使わない

# 変更後
出力はプレーンテキストのみ。Markdownの記号（#、**、`、---など）は一切使わない
コード例を示す場合はそのまま記載する（コードブロック記号（```）もインラインコード記号（`）も使わない）
```

backtickが暗黙的に「許容されている」とモデルが判断していたため、禁止を明示したことで大幅改善。

**変更2：識別子専用のバッククォート禁止ルールを追加（+8%）**

```
# 追加
関数名・変数名・フィールド名・クラス名などのコード識別子もバッククォートで囲まずそのまま書く
（例：email フィールド、UserCreate クラス、findUnique() メソッドはすべて装飾なしで記載）
```

T4（Pydantic エラー）で `email` フィールドや `UserCreate` クラスへのバッククォートが残っていた原因に対応。

**変更3：再発防止策の上限を明示ルール化（+4%）**

```
# 追加
再発防止策は最大2項目に収める（3項目以上は書かない）
```

スキル定義の「1〜2個」という制約が守られないケースが散発していたため、ルールセクションに明示。

**変更4：識別子ルールの負例テキストを除去（+4%）**

```
# 変更前（変更2で追加した版）
（正：email フィールド　誤：`email`フィールド）という形で負例を併記していた

# 変更後
正例のみに変更（負例から削除）
```

禁止例の中にバッククォート文字を含めていたため、モデルがそれを「許容パターン」として学習してしまっていた。正例のみで書き直したことで解消。

### 改善しなかったもの

今回の4実験はすべてkeepとなり、廃棄された変更はありませんでした。

ただし、実験の過程で一つ誤った設計をしていたことが判明しました。変更2で「禁止事項の例示にその禁止文字を含めてしまった」ケースです（変更4で修正）。これはautoresearchが1変更ずつ試すループだったため問題を切り分けられましたが、複数の変更を一度にまとめていたら見逃していたと思います。

元のSKILL.mdに戻したい場合はバックアップから復元できます。

```
cp ~/.claude/skills/error-diagnosis/autoresearch-error-diagnosis/SKILL.md.baseline \
   ~/.claude/skills/error-diagnosis/SKILL.md
```

---

## まとめ

この手順で大事なのは順序です。

```
出力を自分で読む（20件）
    ↓
error-analysisで失敗を分類する
    ↓
evalを設計 → validate-evaluatorで検証する（TPR/TNR 90%以上）
    ↓
generate-synthetic-dataでテスト入力を生成する
    ↓
autoresearchでループを実行する
```

最初の「出力を自分で読む」を省略すると、後の全工程が無駄になります。Hamelのevals講座には「定期的にデータを手動で確認する意欲がなければ、evalに時間を使っても無駄だ」とあります。地味ですが、ここが全ての起点です。

Skillの出力を読んでいて「なんか壊れてるな」と感じたことがある方は、まず出力を20件読むところから始めてみてください。

---

## 参考文献
