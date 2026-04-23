---
id: "2026-04-22-opus47の登場によりclaude-codeの開発者と公式がこれはもうやめろと言い始めた6つのこと-01"
title: "Opus4.7の登場により、Claude Codeの開発者と公式が「これはもうやめろ」と言い始めた6つのこと"
url: "https://qiita.com/ot12/items/06420caf41a34a910c53"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

2026年4月16日、AnthropicがClaude Opus 4.7をリリースしました。

同時に公式ブログ「Best Practices for Using Claude Opus 4.7 with Claude Code」が公開され、Claude Code作者のBoris CherneyもXで「6つの新技」を投下しています。

両方を通してAnthropic公式が言っているのは「これまでのClaude Codeの使い方は、今日でやめろ」です。

4.6までは正解だった作法が、4.7では逆効果になることもあるようです

## 「ペアプロ（細かく指示する）」のはもうやめろ

[![スクリーンショット 2026-04-21 10.22.09.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fdcfedbd5-89ef-49bf-aafc-c53ec977b896.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e53e4a95a2d537a6188523ceecd287bb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fdcfedbd5-89ef-49bf-aafc-c53ec977b896.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e53e4a95a2d537a6188523ceecd287bb)

4.6までの「細かく指示するほど賢く動く」という感覚は、4.7では**逆に性能を下げます**。公式ブログの冒頭で明言されています。

> "Treat Claude more like a capable engineer you're delegating to than a pair programmer you're guiding line by line."  
> （一行ずつ指導するペアプログラマー相手ではなく、任せられるエンジニアとして扱え）

4.6までは、「プロンプトを送る」→「返ってきたコードを見て修正を出す」→「また返ってきたコードを見て…」という**往復型**が標準でした。4.7はこの前提を捨てています。

公式が指示する手順は一つだけ。

> "Specify the task up front, in the first turn."  
> （最初のターンで、タスクを包括的に指定せよ）

初回プロンプトに **Goal（目的）／Constraints（制約）／Acceptance criteria（完了条件）** を全部入れる。そのあと途中介入を減らす方が、4.7は自律実行の性能を発揮します。

### 設計思想の変化

4.6と4.7の違いを、公式は3点で説明しています。

1. ツール呼び出しより **推論を優先する**
2. Subagentの呼び出しに **より慎重になる**（自己完結できるなら呼ばない）
3. **長期自律実行** の性能が向上

ここまで来ると「細かく指示するほど賢く動く」という従来の感覚は逆効果になります。指示が細かいほど、自律判断の余地が減るからです。Claude Codeでの正解プロンプト様式は、4.7を境に**180度逆**になったと言っていいです。

## 「Effort Levelをmaxに常用する」のはもうやめろ

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F6835d47f-d25d-481b-abff-44fa6faac23c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7a6d99fa832f0b927d84aba61d1a2856)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F6835d47f-d25d-481b-abff-44fa6faac23c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7a6d99fa832f0b927d84aba61d1a2856)

「一番上のmaxが一番賢い」は、今日で捨ててください。Claude CodeのEffort Levelは5段階、公式が指定する推奨デフォルトは**maxではなくxhigh**です。

| Level | 公式の使いどころ |
| --- | --- |
| low | 短く、レイテンシ重視、知性不要 |
| medium | コスト重視で知性を多少犠牲にできる |
| high | バランス型（Sonnet推奨） |
| **xhigh** | **Opus 4.7の推奨デフォルト。大半のコーディングで最良** |
| max | 要求の高いタスク用。overthinking傾向あり |

公式の文言はこうです。

> "On Opus 4.7, the default effort is `xhigh` for all plans and providers."  
> （Opus 4.7では、全プラン・全プロバイダでxhighがデフォルト）

注目すべきは **max の扱い**。「上のレベルほど賢い」は正しくありません。公式は max について「overthinking傾向がある」と明記しています。考えすぎで遅くなる、逆に精度が落ちるケースがあるということです。Borisも「ほぼ全タスクで xhigh、最難関でだけ max」と投稿しています。

### 仕様上の重要な変更

以下は [Anthropic公式API Docs「What's new in Claude Opus 4.7」](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7) の "Breaking changes" 節に明記されています。Messages API限定で、Claude Managed Agents使用時は非該当です。

* fixed thinking budget モードは非サポート（`thinking: {type: "enabled", budget_tokens: N}` は400エラー）
* adaptive thinking は **デフォルトOFF**。`thinking: {type: "adaptive"}` を明示する必要あり
* `temperature` / `top_p` / `top_k` の非デフォルト値も400エラーになる（プロンプトで挙動制御する方針）
* トークナイザー刷新：同じテキストで**1.0〜1.35倍**のトークン数になり得る。`max_tokens` にヘッドルームを持たせる
* 思考内容（thinking content）はデフォルトで省略。必要なら `display: "summarized"` で戻す

調整手段は `effort`（Claude Codeなら `/effort`）と `task_budget`（beta）の2系統に集約されています。

Claude Codeのバージョン要件も変わりました。**v2.1.111 以降**でなければ Opus 4.7 を呼び出せません。古いバージョンのままでは新モデルの恩恵を受けられないので、まず更新を確認してください。

```
claude --version
# 2.1.110 以下なら更新
```

## 「`--dangerously-skip-permissions`」を常用するのはもうやめろ

`--dangerously-skip-permissions` を常用する運用は、2026年4月時点で**時代遅れ**です。Borisが同日Xで出した「6つの新技」のうち、権限プロンプト撲滅系が2つ、これを安全に置き換えます。

### Auto Mode

[![スクリーンショット 2026-04-22 9.26.13.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fa72529d2-6e7d-4087-b2b4-cfd4ac65a27d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d0e9f660e80f907e4b3208e3de9d0c2a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fa72529d2-6e7d-4087-b2b4-cfd4ac65a27d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d0e9f660e80f907e4b3208e3de9d0c2a)

Claude Codeを使っていて誰もが経験する、「Allow?」の連打問題。これを解決するのが Auto Mode です。公式の説明はこうです。

> "A classifier model reviews commands and blocks only what looks risky: scope escalation, unknown infrastructure, or hostile-content-driven actions."  
> （分類モデルがコマンドを精査し、リスクあるもの（スコープ拡大、未知のインフラ、敵対的内容由来の操作）だけをブロック）

起動は単純です。

```
claude --permission-mode auto -p "fix all lint errors"
```

Max / Team / Enterprise プラン限定の Research Preview 機能ですが、**`--dangerously-skip-permissions` の正しい代替**として位置づけられています。

### `/fewer-permission-prompts`

[![スクリーンショット 2026-04-22 9.26.27.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F342c33d4-6966-4fec-a567-a283c45c981b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bd063f531827897ccaea4bd0aff061d8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F342c33d4-6966-4fec-a567-a283c45c981b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=bd063f531827897ccaea4bd0aff061d8)

同時に追加された新しいSkillです。

* セッション履歴を分析し、**許可リストの追加候補を提案**
* 何度も同じコマンドを承認している状態を検知
* 提案を受け入れると、次から自動通過

`/permissions` で手動ホワイトリスト化していた作業を、**半自動化**してくれる機能です。Auto Modeが使えない Pro プランでも利用できます。

### プラン別の可用性

| 機能 | Pro | Max | Team | Enterprise |
| --- | --- | --- | --- | --- |
| Auto Mode | × | ○ | ○ | ○ |
| `/fewer-permission-prompts` | ○ | ○ | ○ | ○ |
| `/permissions` | ○ | ○ | ○ | ○ |

上記の通り、Auto Mode が安全かつ同等の体験を提供します。

## 「長時間セッションを横で見守り続ける」のはもうやめろ

4.7は自律実行が長くなります。横で1行ずつ見守り続ける運用はやめて、**結果だけ受け取る**体制に切り替えてください。Boris本人がXで紹介したUI側の2つがこれを支援します。

### Focus Mode（`/focus`）

[![スクリーンショット 2026-04-22 9.27.27.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fe9c414b2-c549-4258-b75c-50f50e6a332b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d6ae0568299f2054ce9079eedf35194c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fe9c414b2-c549-4258-b75c-50f50e6a332b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d6ae0568299f2054ce9079eedf35194c)

最終結果のみを表示し、途中の思考・ツール使用ログを隠すモードです。`/focus off` で元に戻せます。委譲モデルと相性がよく、「任せたら結果だけ見る」という使い方を支えます。

### Recaps

[![スクリーンショット 2026-04-22 9.26.57.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F9eb26a38-8900-485d-84b8-ff161c69e9d7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=80108d514e2ab70276e10fdaf80047a3)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F9eb26a38-8900-485d-84b8-ff161c69e9d7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=80108d514e2ab70276e10fdaf80047a3)

長時間セッションから復帰したとき、**サマリーを自動表示**する機能です。Borisは「エージェントが何をしたか、次は何をするかを準備する」UIとして紹介しています。`/loop` で何時間も回していたタスクに戻っても、「何をどこまでやったか」を即座に把握できます。

この2つは **4.7の長期自律実行が前提になったUI**です。Anthropicは「見守る必要がない」ことを可視化で支援する、というスタンスを取っています。

## 「Subagentを毎回呼ぶ」のはもうやめろ

[![スクリーンショット 2026-04-22 9.22.26.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F474018d7-0857-4b00-9743-56eb50ce9d30.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7d91a8f942ab290e6fdd7f19e1ba0761)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F474018d7-0857-4b00-9743-56eb50ce9d30.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7d91a8f942ab290e6fdd7f19e1ba0761)

4.6までの「積極的にsubagentを切れ」は**捨ててください**。4.7の公式ブログは真逆のことを書いています。

> "More judicious about when to delegate work to subagents."  
> （サブエージェントへの委譲タイミングには、より慎重になること）

### いつ明示的に呼ぶか

公式が明示している基準は2つだけです。

* **fanning out across files**（複数ファイルへの並列作業）
* **independent items**（独立した複数タスク）

それ以外は Claude 自身が判断します。従来のように「subagent使って」と毎回指示を入れると、**逆に性能が下がるケース**が出てきます。4.7は自分で判断する前提で訓練されているからです。

## 「検証機構なしで任せる」のはもうやめろ

[![スクリーンショット 2026-04-22 9.28.05.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F3261e3e1-46f7-4398-8755-37af9b76e0ce.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=afbbe0308237ae1e109fdae235cb2c82)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F3261e3e1-46f7-4398-8755-37af9b76e0ce.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=afbbe0308237ae1e109fdae235cb2c82)

6つの「やめろ」の最後、そして公式が**最も効果の高い施策**と明記しているのがこれです。

> "Include tests, screenshots, or expected outputs so Claude can check itself. This is the single highest-leverage thing you can do."  
> （テスト・スクリーンショット・期待出力を与えてClaude自身が検証できるようにせよ。これが最も効果の高い施策）

モデルが賢くなっても、**検証機構を渡さない限り品質は上がりません**。

### 実装パターン

**バックエンド**：テストスイートを Stop Hook に繋ぐ。`npm test` が通るまで Claude が自動でもう1周する構成です。`.claude/settings.json` にこう書きます。

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [{ "type": "command", "command": "npm test" }]
      }
    ]
  }
}
```

**フロントエンド**：Playwright / Puppeteer で E2E、またはChrome拡張。Boris本人はChrome拡張を「毎回使う」と発言しています。

### 4.7固有の事情

4.7は自律実行が長くなるので、**途中で誰も見ていない時間が増えます**。検証機構がなければ、誤った方向で走り続けるリスクも比例して上がります。

推奨される組み合わせは、**xhigh × 長期自律 × 検証機構**の3点セット。品質が上がるかどうかは、モデルの差ではなく**検証機構を渡しているかどうか**で決まります。

## 今日やる実務設定チェックリスト

ここまでの同日公開内容を、設定項目に落とし込みます。

**1. Claude Code を v2.1.111 以上に更新**

**2. モデルを Opus 4.7、Effort を xhigh に**

```
/model opus
/effort xhigh
```

**3. 初回プロンプトの型を整える**

```
Goal: <達成したいこと>
Constraints: <守るべき制約>
Acceptance criteria: <完了の判定基準>
```

**4. Verification Loop を組む**

* バックエンド：テストを Stop Hook に
* フロントエンド：Playwright か Chrome拡張

**5. Auto Mode を試す（Max以上）**

```
claude --permission-mode auto
```

チェックボックスで整理するとこうなります。

## 同日登場の他の見逃せない新機能

Opus 4.7 リリースと同時に入った、ベストプラクティス記事の本筋ではないものの実務で効く新機能を3つ。

### `/ultrareview` コマンド（Claude Code）

4.7 にあわせて Claude Code に追加されたレビュー用コマンド。複数視点でコードを厳しめに点検するモードで、PR前の最終チェックに向きます。

### Task budgets（beta）

エージェントループ全体のトークン予算をモデルに **目安として** 伝えられる新機能です。`max_tokens` が単発リクエストの上限を設ける仕組みなのに対し、task budget は**エージェントが自分でペース配分する**ための助言的上限です。

```
response = client.beta.messages.create(
    model="claude-opus-4-7",
    output_config={
        "effort": "high",
        "task_budget": {"type": "tokens", "total": 128000},
    },
    betas=["task-budgets-2026-03-13"],
    ...
)
```

最低値は20k、品質重視の探索タスクでは設定しない方が無難です。

### 高解像度画像サポート

画像の最大解像度が **2576px / 3.75MP** に拡張されました（従来は1568px / 1.15MP）。スクリーンショット解析・ドキュメント理解・computer useでの改善が期待できます。加えて、モデルの座標系と実ピクセルが1:1に揃ったので、座標変換の計算が不要になっています。

## まとめ

2026年4月16日に Anthropic が公式ブログで出したベストプラクティスと、Claude Code 作者 Boris Cherny が同日にXで投下した6つの新技は、合わせて**これまでのClaude Codeの使い方は今日で卒業しろ**の一点に収束します。

ペアプロ、max常用、`--dangerously-skip-permissions`、Subagent毎回呼び出し、検証機構なしの自律実行、長時間セッションの横付き見守り。4.6までは正解だった6つが、4.7では全部「やめろ」に変わりました。

4.7の真価は、**途中で介入しないこと**で初めて出てきます。6つの旧作法をやめて、任せる前提で設定を整えてみてください。

## 参考
