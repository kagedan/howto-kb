---
id: "2026-04-27-star-3700のaiエージェント自動改善ツールをreadmeだけで動かす前にossコードリーディ-01"
title: "Star 3,700のAIエージェント自動改善ツールを「READMEだけで動かす」前に──OSSコードリーディングで見つけた3つの設計"
url: "https://zenn.dev/bentenweb_fumi/articles/7fzuuupc6dt3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-04-27"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

## はじめに

AIエージェントを別のAIが自律改善し続ける、というコンセプトのOSSフレームワーク（以下、AutoAgent）を見つけました。GitHub Star 3,700超で「自動的にプロンプトとツール構成が進化する」という触れ込みです。

面白そうだったので、自分のマシンで動かす前にソースコードを通読しました。結果として、設計思想として「**安全装置を意図的に外している**」ことが明確に見えたので、評価のフレームワークと併せて共有します。

## 結論

| # | 設計上の選択 | 影響 |
| --- | --- | --- |
| 1 | `permission_mode="bypassPermissions"` がデフォルト | Claude Agent SDKの全権限チェックが無効化される |
| 2 | システムプロンプトに `NEVER STOP` / `Do NOT pause` を明記 | 人間の確認なしに無限ループでコード変更・実行を継続 |
| 3 | API費用の上限値がデフォルト未設定（`None`） | 一晩で数百〜数千ドル請求の可能性 |

3つを組み合わせると「全権限バイパス × 停止困難 × 課金青天井」という構図で、想定外の挙動が起きた時のフェイルセーフが弱い設計になっています。

## 1. `bypassPermissions` モードとは何か

Claude Agent SDK（`@anthropic-ai/claude-agent-sdk`）には、ツール呼び出し時の権限チェックを段階的に緩める設定があります。

| permission\_mode | 挙動 |
| --- | --- |
| `default` | 通常の権限プロンプトに従う |
| `acceptEdits` | ファイル編集系ツールを自動承認 |
| `plan` | 実行せず計画のみ立てる |
| `bypassPermissions` | **全ツール呼び出しを無確認で実行** |

`bypassPermissions` はClaude公式ドキュメントでも「sandbox環境専用」と明記されている設定です。AutoAgentはこれをデフォルト値として `agent_options` に組み込んでいます。

```
# AutoAgent内部の設定（簡略化したイメージ）
agent_options = {
    "permission_mode": "bypassPermissions",
    "system_prompt": META_AGENT_PROMPT,
    "allowed_tools": ["Read", "Write", "Bash", "Edit", ...],
}
```

これがDocker内で完結するなら問題はありません。問題は、**Quickstart の `python run.py` を `docker compose` ではなくホストOSで直接叩く利用者がいる**ことです。

## 2. 「NEVER STOP」プロンプトの何が危険か

メタエージェント（エージェントを改善するエージェント）のシステムプロンプトに以下が含まれます。

```
You MUST continue iterating until the metric improves.
NEVER STOP. Do NOT pause for human confirmation.
If a tool fails, retry with a different approach.
```

このプロンプトが効くと、エージェントは以下のループを回し続けます。

1. 既存エージェントの構成を読む
2. プロンプトやツール構成を「改善」する
3. テスト実行する
4. メトリックが改善しなければ1に戻る

**停止条件が「メトリック改善」しか定義されていない**点が設計上の問題です。

| 期待挙動 | 実挙動 |
| --- | --- |
| メトリック改善で停止 | 改善しなければ無限ループ |
| 致命的エラーで停止 | retry with different approach |
| 人間が割り込み可 | `NEVER STOP` で割り込み拒否 |

LangGraphの `interrupt_before` のような明示的な停止点が無いため、暴走を止めるには Docker コンテナを kill する以外の手段がありません。

## 3. API費用の天井がない

OpenAI / Anthropic のAPIキーを `.env` で渡す方式なのは妥当ですが、**月次・日次の支出上限がコード側で設定されていません**。デフォルト値が `MAX_COST = None` になっています。

組み合わせると以下のシナリオが現実的に起こり得ます。

```
21:00 動かして寝る
21:05 メタエージェントがプロンプトを書き換える（GPT-5 で $0.5）
21:10 テスト実行（GPT-5 で $1.2）
21:15 メトリックが改善しないので別アプローチに切り替え（$0.8）
...
07:00 起床、ダッシュボードで $480 の請求を発見
```

OpenAI の Dashboard で日次予算アラートを設定していても、アラート発火後の自動停止までは数十分のラグがあります。**OSS側で支出上限を持つ**のがベターです。

## OSSを評価するときの実用フレームワーク

AIエージェント系OSSは「便利そう」と「安全そう」のギャップが大きいので、READMEだけで判断しないチェックリストを共有します。

### 必読ファイル

1. `package.json` / `pyproject.toml` / `requirements.txt` ── 依存ライブラリの中に望まないものが無いか
2. エントリーポイント（`main.py` `index.ts` など） ── 起動時に何が呼ばれるか
3. システムプロンプト（`prompts/` 配下や定数文字列） ── エージェントの行動原理
4. SDK初期化部分 ── permission\_mode / allowed\_tools / sandbox 設定
5. APIキー管理 ── 環境変数 / Keychain / ハードコード

### 評価軸

| 観点 | 良い設計 | 危険サイン |
| --- | --- | --- |
| 権限 | 最小権限・明示的に拡張 | デフォルトで全権限バイパス |
| 停止条件 | 明示的なinterrupt point / max\_iterations | NEVER STOP / 無限ループ |
| 支出上限 | コード側で MAX\_COST デフォルト設定 | None / 未設定 |
| 隔離 | Docker / sandbox 強制 | ホスト直接実行可 |
| 監査ログ | 全ツール呼び出しを記録 | console.log のみ |

### 自分が使う前の3問チェック

* このOSSを暴走させた場合、**いくらまでなら許容できるか**？ その上限はOSS側に設定可能か？
* 暴走を**何分以内に検知して停止**できるか？ その手順は事前に試したか？
* このOSSが書き換える可能性がある**ファイル/インフラの範囲**は限定されているか？

3問とも即答できないなら、まだ自分のホストでは動かさない方が安全です。

## OSS批判ではなく、利用文脈の話

繰り返しになりますが、AutoAgent自体はマルウェアではありません。

* ✅ コードに難読化や隠し動作は無し
* ✅ Docker Compose 設定がリポジトリに含まれる
* ✅ 研究目的の論文・ベンチマークが付随している
* ❌ READMEのトップに「ホスト直接実行は危険」と書かれていない
* ❌ デフォルト設定が `bypassPermissions` × `NEVER STOP` × `MAX_COST=None`

つまり「研究者が自分のラボで使う前提」の設計が、Star 3,700の話題性で「個人開発者が週末に試す」文脈に流れていることが本質的なリスクです。

## まとめ

* AIエージェント系OSSは「Star数 × 話題性」と「個人で動かしたときの安全性」が直結しない
* 評価する際は **permission\_mode / 停止条件 / 支出上限 / 隔離方式** の4点を必ず読む
* READMEだけで動かすのは、自宅のサーバーに**赤の他人が書いた su スクリプトを実行する**のと近い感覚で見たほうがよい

AIエージェント時代のOSSは、コード自体が悪意を持っていなくても、設計思想と利用文脈のギャップが事故を生みます。皆さんはOSSを動かす前、どこまで読みますか？

#AIエージェント #セキュリティ #OSS

---

## この記事を書いた人

**BENTEN Web Works** — 業務自動化・AI活用・システム開発のフリーランスエンジニアです。

Claude Code / GAS / Python を活用した開発や、AI導入のご相談を承っています。

👉 **[情シス代行サービス](https://bentenweb.com/services/it-outsourcing/)** — 詳細・お問い合わせはこちら  
🐦 **[X（旧Twitter）](https://x.com/Fumi_BENTENweb)** — 日々の知見を発信中
