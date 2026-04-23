---
id: "2026-04-02-llmの構造化出力まだjsonスキーマですか-by-anthropic-academy-01"
title: "LLMの構造化出力「まだJSONスキーマですか？」 by Anthropic Academy"
url: "https://note.com/unique_auklet272/n/n31f9d7089c5e"
source: "note"
category: "ai-workflow"
tags: ["LLM", "note"]
date_published: "2026-04-02"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

## 結論

Claude、OpenAI、Geminiはそれぞれ「構造化された出力だけを取り出す」ための仕組みを持っていますが、設計思想がそれぞれで異なります。  
 AIアプリを作るなら、使うSDKやフレームワークごとの違いを知っておかないとうまくいかないよねっていう話しです👍

## 前提：構造化出力ってなんで必要なの？

前提として、構造化出力ってなんで必要なのかをまず解説します。  
例えば、Claudeに「JSONを生成して」と頼むと、こうなりがち：

![](https://assets.st-note.com/img/1775027250-W3KeQ7DspUmlSiAIPau2tbxF.png?width=1200)

**余計な文字が混在したアウトプット**

欲しいのはJSONだけなのに、前後に余計な説明文が入ってしまい邪魔です。

では、どうすればいいか。

## Claudeの構造化出力は大きく2つの方法がある

Claudeの構造化出力は大きく2つのやり方があります。  
  
一つ目は、output\_config.formatを使う（いわゆるJSONスキーマです）  
二つ目は、プリフィル + stop\_sequencesを使う

今回は意外とあまり知られてない**「プリフィル + stop\_sequences」**を中心に解説します。

### ① Claudeの構造化出力：output\_config.format

まず一つ目、Claude のJSONスキーマ指定による構造化出力について簡単に解説します。output\_config.formatにjson\_schemaを指定すると、Claudeはスキーマに準拠したJSONだけを返すことが保証されます。

```
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "このメールから情報を抽出して: 田中太郎(tanaka@example.com)がEnterpriseプランに興味あり"}
    ],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "plan_interest": {"type": "string"},
                },
                "required": ["name", "email", "plan_interest"],
                "additionalProperties": False,
            },
        }
    },
)
```

JSONだけではなく、他にもPython、TypeScript、Javaなどに限定して出力させることが可能なようです。[（公式ドキュメント）](https://platform.claude.com/docs/ja/build-with-claude/structured-outputs)

ただし、CSVやRegexといった記法には対応していないようです。

そこで、登場するのが、  
二つ目の構造化出力を制御する**「プリフィル + stop\_sequences」**です！

### ② Claudeの構造化出力：プリフィル + stop\_sequences

JSONスキーマを使わずにClaudeは以下の2つのテクニックを組み合わせて出力を制御する。

**プリフィル（Prefill）**  
アシスタントの返答の書き出しを、こちらが事前に埋めておくテクニック。

```
add_assistant_message(messages, "```json")
```

これでClaudeは「自分はもうコードブロックを開始した」と思い込み、余計な説明文なしでいきなりJSONの中身を書き始める。 プリフィルの文はもう出力済みとして扱われるので、出力に含まれなくなる。いいね👍

**stop\_sequences**特定の文字列が出てきたら強制的に生成を止める。例えば以下 ``` の部分

```
text = chat(messages, stop_sequences=["```"])
```

閉じの ``` が来たら即停止。JSONの中身だけが取得できる。

![](https://assets.st-note.com/img/1775089313-MsXzOlgabDU8mAdfrVn0v7ET.png?width=1200)

[**Anthropic Academy『Structured data 』**](https://anthropic.skilljar.com/claude-with-the-anthropic-api/287732)

**応用：プリフィルにアシスタント指示を埋め込む**以下の Here are all three commands without any comments: のところがそう  
「余計なこと書くなよ？」と指示してあげる。

これはシステムプロンプトではなくて、**プリフィル専用のアシスタント指示**です。

```
add_assistant_message(messages, "Here are all three commands without any comments:\n```bash")
```

こうすることで、Claudeは「自分がそう宣言した」と認識するので、コメントを付けずに出力する。 自分で言ったことに矛盾しないように振る舞う、というClaudeの性質を利用したテクニック。

![](https://assets.st-note.com/img/1775027239-TIxwFulXCkv28f3dSNDPgHWc.png?width=1200)

**コマンドのみ出力を制御したアウトプット**

## 各LLMの出力制御方法の比較表

![](https://assets.st-note.com/img/1775090681-IOdWklF2ULRbfor5GEqQ31NK.png?width=1200)

* **プリフィルはClaude独自**の機能。OpenAI・Geminiには同等の機能がない
* OpenAI・Geminiは代わりに**JSONモードや構造化出力**をAPIパラメータとして用意（スキーマを渡せばその通りに出力される）
* LangChainはフレームワークとして各LLMの機能をラップしつつ、**Output Parsers**で後処理として構造化する仕組みも持つ
* ストップシーケンスは**3社とも対応**している共通テクニック

## 設計思想の違い

* **Claude**: プリフィル+stop\_sequencesの組み合わせで柔軟に制御。JSON以外（bash、Python、CSVなど）にも同じテクニックで対応できる
* **OpenAI**: JSONモード・スキーマ指定に加え、GPT-5ではFree-Form Function CallingやCFGも追加。生コードの受け渡しから構文レベルの厳密制御まで、用途別に専用の仕組みが用意されている
* **Gemini**: JSONモード・スキーマ指定で構造化出力に対応

Claudeは汎用的なテクニック1つで幅広く対応するアプローチ。OpenAIは用途ごとに専用機能を増やしていくアプローチ。方向性が対照的です。実践での使いどころ

Webアプリでユーザーがボタンを押したら、コピペできるきれいなJSONだけ返したい。 そんなとき、プロンプトで「JSONだけ返して」と頼むのではなく、APIの仕組みで強制的に出力の開始地点と終了地点をコントロールする。

```
# プリフィルで開始地点を固定
add_assistant_message(messages, "```json")

# ストップシーケンスで終了地点を強制
text = chat(messages, stop_sequences=["```"])

# 取得したJSON文字列をPython辞書に変換
clean_json = json.loads(text.strip())
```

## 必見： ```codeプリフィルであらゆるフォーマットに対応可能

なんとプリフィルを ```json ではなく ```code にすると、Python・JSON・Regexのどれが来ても対応できる。 評価パイプラインのように、出力フォーマットが事前に確定しないケースで特に有効。

```
add_assistant_message(messages, "```code")
```

こんな感じ  
全体はこう👇

```
def run_prompt(test_case):
    prompt = f"""
Please solve the following task:

{test_case["task"]}

* Respond only with Python, JSON, or a plain Regex
* Do not add any comments or commentary or explanation
"""

    messages = []
    add_user_message(messages, prompt)
    # "```code" → フォーマットを限定せずコードだけ返させる
    add_assistant_message(messages, "```code")
    output = chat(messages, stop_sequences=["```"])
    return output
```

**実際の出力例（3種類のフォーマットが混在）**

![](https://assets.st-note.com/img/1775027075-AqQjoMehSKzWFZsk1XEHirdY.png?width=1200)

**プリフィル"""codeで3種類のフォーマット出力が可能**

"```code" という汎用的なプリフィルひとつで、3種類すべてが説明文なし・コードだけで返ってきている。 "```json" や "```python" のように個別指定しなくても、プロンプト側で「Respond only with Python, JSON, or a plain Regex」と伝えれば、Claudeが適切なフォーマットを選んで出力する。

output\_config.formatでもPythonとかに限定した出力制御は可能ですが、**RegexやCSVに限定したアウトプットはプリフィルだけです。**[（公式ドキュメント）](https://platform.claude.com/docs/ja/build-with-claude/structured-outputs)

## まとめ

Claudeはプリフィルという独自機能があり、```codeでJSON・Python・bashなど何でも同じやり方で対応できる柔軟さが強み。構造化出力の方でもある程度できますが、対応フォーマットにCSV等がないようです。[（公式ドキュメント）](https://platform.claude.com/docs/ja/build-with-claude/structured-outputs)

OpenAI・GeminiはJSONモードやスキーマ指定があり、JSON出力は手軽。GPT-5ではさらにFree-Form Function CallingとCFGが加わり、生コードの受け渡しや構文レベルの厳密制御まで可能になりました。stop\_sequencesは各社共通で使えます。

AIエージェントを作るなら、それぞれの出力制御の仕組みを把握しておくことが大事です。
