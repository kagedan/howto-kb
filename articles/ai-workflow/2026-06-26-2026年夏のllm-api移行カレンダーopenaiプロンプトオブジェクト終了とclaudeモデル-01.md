---
id: "2026-06-26-2026年夏のllm-api移行カレンダーopenaiプロンプトオブジェクト終了とclaudeモデル-01"
title: "2026年夏のLLM API移行カレンダー：OpenAIプロンプトオブジェクト終了とClaudeモデル廃止に本番をどう備えるか"
url: "https://qiita.com/YushiYamamoto/items/8374b35d81f06b86066f"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-06-26"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

![LLM API migration calendar 2026 summer](https://raw.githubusercontent.com/YushiYamamoto/YushiYamamoto/main/assets/llm-api-migration-calendar-2026-06-eyecatch.png)

2026年6月、OpenAIとAnthropicが相次いで「廃止（deprecation）・終了（shutdown）」の予定を公式に告知した。OpenAIは6月3日に再利用可能なプロンプトオブジェクト（`v1/prompts`）の終了を、Anthropicは6月15日にClaude Sonnet 4 / Opus 4の即時リタイアを発表している。いずれも本番のLLM連携を静かに壊しうる変更で、しかも多くは「告知済み・将来の固定日に消える」タイプだ。つまり今は、慌てずに移行計画を引けるボーナス期間にある。

この記事は、6月に確定した主要なAPI廃止・モデルリタイアを一次情報で整理し、本番を止めないための移行カレンダーとチェックリストに落とし込む。対象は、OpenAI / Claudeのどちらか（または両方）を本番のアプリ・エージェント・自動化に組み込んでいるエンジニアと技術意思決定者。

## 結論

| 確認項目 | ニュースの含意 | 直すこと |
|---|---|---|
| OpenAI `v1/prompts`・再利用可能プロンプト | 2026/11/30 に終了。ダッシュボードで組んだプロンプトはAPIから消える | プロンプトをアプリ側のコードへ移し、`Responses API`の`input`/`instructions`で渡す |
| OpenAI Evals Platform / Agent Builder | 同じく 2026/11/30 に終了 | 評価・エージェント定義を自前コードまたは別基盤へ移植 |
| OpenAI GPT Imageモデル | 2026/12/1 にAPIから削除（`gpt-image-2`へ） | 画像生成の`model`指定を棚卸しして差し替え |
| OpenAI GPT-5 / o3系 | 2026/12/11 にリタイア（`gpt-5.5`等へ） | 固定スナップショット名のハードコードを更新 |
| Claude Sonnet 4 / Opus 4 | 2026/6/15 に**リタイア済み**。リクエストはエラーを返す | 即時に Sonnet 4.6 / Opus 4.8 へ。固定モデル名の参照を全削除 |
| Claude Opus 4.1 | 2026/8/5 にリタイア予定 | Opus 4.8 へ移行。8月までに切替を完了 |

ポイントは2つ。第一に、**OpenAI側は固定の将来日（11月〜12月）に消える**ので、今は計画的に移せる。第二に、**Claude側のモデルリタイアは一部すでに発生している**（Sonnet 4 / Opus 4は6/15で終了済み）。後者を放置すると、リクエストは即エラーになる。

## OpenAI：再利用可能プロンプトと周辺基盤の終了（2026/11/30）

### 確認できる事実

OpenAIの公式Deprecationsページによると、再利用可能プロンプトオブジェクトと`v1/prompts`は2026年6月3日に告知され、2026年11月30日に終了予定。同日に **Evals Platform** と **Agent Builder** も終了予定として記載されている。

原文: "The `v1/prompts` API and reusable prompt objects are scheduled to shut down."
日本語訳: 「`v1/prompts` APIと再利用可能プロンプトオブジェクトは終了予定」（OpenAI Deprecationsページ）

移行の推奨は、プロンプト内容をアプリケーションコード側へ移すこと。各本番プロンプトをバージョン管理されたヘルパーに置き、変数を型付き引数や検証済み入力に置き換え、生成したメッセージを`Responses API`の`input`と`instructions`で直接渡す形が公式の案内に沿う。

### 実務解釈

ダッシュボードのGUIでプロンプトを組み、IDで呼び出す運用をしているチームは、その参照が11/30で切れる。やることは「プロンプトをGUIからGitへ引っ越す」ことに尽きる。

```python
# Before: ダッシュボードのプロンプトIDに依存（11/30で終了）
resp = client.responses.create(
    prompt={"id": "pmpt_123", "version": "3"},
    # variables=...
)

# After: プロンプトをコード側で管理し、input/instructions で渡す
SYSTEM_PROMPT = "あなたは契約書レビューの補助を行う。..."  # 版管理はGitで

def build_messages(contract_text: str) -> list[dict]:
    return [{"role": "user", "content": contract_text}]

resp = client.responses.create(
    model="gpt-5.5",
    instructions=SYSTEM_PROMPT,
    input=build_messages(contract_text),
)
```

副次的な利点として、プロンプトがコードレビューとCIの対象になり、差分・ロールバック・A/BがGit上で完結する。GUIの便利さより、本番のプロンプトは「コードとして」持つほうが事故が減る。Evals Platform / Agent Builderを使っている場合は、評価セットとエージェント定義のエクスポート可否を11月までに必ず確認しておく。

## Claude：モデルのリタイアと課金挙動の変化（2026/6）

### 確認できる事実

Anthropicの公式リリースノートによると、2026年6月15日に **Claude Sonnet 4（`claude-sonnet-4-20250514`）と Claude Opus 4（`claude-opus-4-20250514`）をリタイア**した。

原文: "We've retired the Claude Sonnet 4 model (`claude-sonnet-4-20250514`) and the Claude Opus 4 model (`claude-opus-4-20250514`). All requests to these models will now return an error."
日本語訳: 「Claude Sonnet 4とClaude Opus 4をリタイアした。これらのモデルへの全リクエストはエラーを返す」（Claude Platformリリースノート）

推奨移行先はそれぞれ Sonnet 4.6 / Opus 4.8。さらに6月5日には **Claude Opus 4.1（`claude-opus-4-1-20250805`）の廃止**が告知され、Claude APIでのリタイアは2026年8月5日予定。移行先はOpus 4.8とされている。

課金面では2026年6月2日から、出力が生成される前に`stop_reason: "refusal"`で拒否されたリクエストは課金されなくなった。6月9日のFable 5 / Mythos 5投入時には、拒否されたリクエストを別モデルで再実行するオプトインの`fallbacks`パラメータ（ベータ）も追加されている。

### 実務解釈

固定スナップショット名（`claude-sonnet-4-20250514`等）をコードや環境変数にハードコードしているプロジェクトは、6/15時点ですでにエラーを踏んでいる可能性がある。対処は機械的で、(1) リポジトリ全体をモデル名で全文検索し、(2) 4.6 / 4.8系へ置換、(3) フォールバックや旧バージョン参照が残っていないかを確認する。

```bash
# 廃止・リタイア済みモデル名がコードに残っていないか棚卸し
grep -rEn "claude-(sonnet-4-20250514|opus-4-20250514|opus-4-1-20250805)" . \
  --include='*.ts' --include='*.py' --include='*.js' --include='*.env*'
```

課金挙動の変化は地味だが効く。拒否が無料化されたことで「安全分類器に弾かれた呼び出しを課金対象として監視していた」コスト計上ロジックがズレる。`stop_reason`を見て成功・拒否・エラーを分けて集計しているなら、拒否を「失敗かつ無課金」として扱う前提に合わせて見直す。`fallbacks`はベータかつ別モデル料金での再実行なので、コスト影響を理解した上でオプトインする。

## 実装チェックリスト

**OpenAI（11/30・12/1・12/11に向けて）**
- [ ] ダッシュボードで作成した再利用可能プロンプト（`prompt.id`参照）を棚卸しする
- [ ] プロンプト本文をアプリのコードへ移し、`instructions`/`input`で渡す形に書き換える
- [ ] Evals Platform / Agent Builderの利用有無を確認し、エクスポート計画を立てる
- [ ] `gpt-image-1-mini` / `gpt-image-1.5` / `chatgpt-image-latest` の参照を`gpt-image-2`へ
- [ ] `gpt-5-2025-08-07` / `o3-2025-04-16`等の固定スナップショット名を後継へ更新

**Claude（即時・8/5に向けて）**
- [ ] `claude-sonnet-4-20250514` / `claude-opus-4-20250514` の参照をコード・環境変数から全削除し、4.6 / 4.8へ
- [ ] `claude-opus-4-1-20250805` を8/5までにOpus 4.8へ移行
- [ ] `stop_reason: "refusal"`（無課金）を成功・エラーと分けて集計するよう監視を更新
- [ ] `fallbacks`を使うなら、再実行が別モデル料金で課金される点をコスト試算に反映

**共通**
- [ ] モデル名・プロンプトIDのハードコードを1か所（設定/定数）に集約し、次の廃止に備える
- [ ] 公式Deprecations / リリースノートの定期確認をスプリントのルーティンに組み込む

## 失敗パターン

**パターン1：固定スナップショット名をハードコードしたまま放置** → 対策：モデル名は設定値として一元管理し、`grep`で残存参照を定期棚卸しする。Claudeはすでにリタイア済みのモデルがあるため「将来の話」ではない。

**パターン2：GUIで作ったプロンプト/評価/エージェント定義を移行直前まで放置** → 対策：終了日（11/30）から逆算し、エクスポート可否の確認だけでも今やる。GUI資産はコード資産より移行コストが見えにくい。

**パターン3：廃止告知を「すぐ消えるわけではない」と読んで先送り** → 対策：固定日が切られた廃止は、その日に確実に壊れる。猶予期間は移行のための時間であって、放置のための時間ではない。

**パターン4：課金挙動の変更を見落とす** → 対策：Claudeの拒否無料化のように、エラー扱い・コスト集計の前提が変わる変更は、機能の廃止と同じ重みで監視ロジックに反映する。

## 参考リンク

- [Deprecations | OpenAI API](https://developers.openai.com/api/docs/deprecations)
- [Migrate from prompt objects | OpenAI API](https://developers.openai.com/api/docs/guides/prompting/migrate-from-prompt-object)
- [Claude Platform release notes | Claude Docs](https://platform.claude.com/docs/en/release-notes/overview)
- [Model deprecations | Claude Docs](https://platform.claude.com/docs/en/about-claude/model-deprecations)

:::note
**この記事を書いた人✏️@YushiYamamoto**
ITPRODX.com代表 / AIアーキテクト
Next.js / TypeScript / n8nを活用した自律型アーキテクチャ設計を専門としています。
日々の自動化の検証結果や、ビジネス側の視点（ROI等）に関するより深い考察は、以下の公式サイトおよびnoteで発信しています。
:::

https://itprodx.com

https://note.com/note_knowledge
