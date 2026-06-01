---
id: "2026-05-31-anthropic-verified-バッジはなぜ取れないのか-審査を通過する8つの設計原則-01"
title: "Anthropic Verified バッジはなぜ取れないのか」— 審査を通過する8つの設計原則"
url: "https://zenn.dev/josh/articles/3b6d6b3d987771"
source: "zenn"
category: "claude-code"
tags: ["MCP", "AI-agent", "zenn"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

# 「Anthropic Verified バッジはなぜ取れないのか」— 審査を通過する8つの設計原則

プラグインをディレクトリに公開したのに、Verified バッジがつかない。

理由はシンプルです。Anthropic の審査は**自動スキャン**と**人間によるレビュー**の2段階あります。自動を通過しても、人間のレビューで落とされるケースが多いのです。公式ドキュメントにはこう明記されています。

> Plugins with an "Anthropic Verified" badge have undergone additional review from a quality and safety perspective. There are no guarantees that any community plugin will become Anthropic Verified.

保証はありません。ただし、**落とされる理由を消すことはできます**。公式ドキュメントから読み解いた8つの設計原則を紹介します。

---

## 原則1：単機能プラグインは作らないこと

Anthropic が明示する「良いプラグイン」の定義がこちらです。([claude.com/docs/plugins/submit](https://claude.com/docs/plugins/submit))

> "The best plugins bundle related capabilities together into a coherent package that solves a specific job function or workflow end-to-end. Rather than exposing a single tool, a good plugin combines skills, connectors, slash commands, and sub-agents so Claude has everything it needs to handle a category of work."

単一ツールの露出では不十分です。たとえば営業プラグインであれば、CRMコネクター＋営業プロセスのスキル＋見込み客リサーチのスラッシュコマンドをセットで束ねます。Claude を「スペシャリスト」にすることが目標です。

---

## 原則2：公式コネクターディレクトリのMCPを使うこと

これは Anthropic が**直接、Verified の可能性を上げると明言**している唯一の施策です。

> "We strongly encourage using connectors that already exist in the Connectors Directory or come from well-known developers. This will increase the likelihood of verification and will reduce the number of warnings shown to users." ([claude.com/docs/plugins/submit](https://claude.com/docs/plugins/submit))

自作MCPを使いたい場合でも、まず公式ディレクトリを確認する習慣をつけておきましょう。

---

## 原則3：オープンソースは必須

クローズドソースのプラグインは**提出すら不可**です。([claude.com/docs/plugins/submit](https://claude.com/docs/plugins/submit))

GitHub リポジトリは public にする必要があります。コードの品質と可読性もレビュー対象と考えておくのが安全です。README、コメント、構造——すべてが「信頼できる開発者か」の判断材料になります。

---

## 原則4：`claude plugin validate` を全クリアしてから提出すること

提出前の必須コマンドがこちらです。

エラーだけでなく、**警告もすべて潰しておく**必要があります。これが自動審査の最低ラインです。ここをクリアしないと人間レビューに到達しません。([claude.com/docs/plugins/submit](https://claude.com/docs/plugins/submit))

---

## 原則5：`SETUP.md` でセットアップを自動化すること

MCPサーバーを含むプラグインには `SETUP.md` スキルを用意します。

> "Plugins can include a SETUP.md skill to guide Claude through configuring and connecting any MCP servers bundled in the plugin. This lets you define step-by-step setup instructions that Claude follows when a user installs or activates your plugin." ([claude.com/docs/plugins/submit](https://claude.com/docs/plugins/submit))

ユーザーが詰まらずにセットアップできることは、Quality の証拠になります。セットアップが不親切なプラグインは審査で不利になる可能性があります。

---

## 原則6：パーミッションは必要最小限に絞ること

Anthropic はユーザーに対して「インストール前にパーミッションを必ず確認せよ」と指示しています。([claude.com/docs/plugins/submit](https://claude.com/docs/plugins/submit))

つまり審査側も**パーミッションの妥当性**を見ています。以下の点に注意が必要です。

* プラグインの目的と関係ないスコープは外す
* 外部サービスへのデータ送信は説明文に明記する
* 不必要に広いアクセス権はそれだけで審査が厳しくなります

GitHub、GitLab、Linear、Asana、Firebase といった既存の Verified パートナーは、いずれも用途が明確で権限スコープが狭くまとまっています。([github.com/anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official))

---

## 原則7：利用規約に違反していないか確認すること

提出前に必読の2ドキュメントがあります。([claude.com/docs/plugins/submit](https://claude.com/docs/plugins/submit))

違反があれば Verified は不可能です。見落としがちなので、必ず一読しておきましょう。

---

## 原則8：完成してから提出すること

見落とされがちな仕様がこちらです。

> "Any changes to your plugin after submission will require re-submitting the form, as each new submission or update is scanned before being shared in the directory." ([claude.com/docs/plugins/submit](https://claude.com/docs/plugins/submit))

「あとで直せばいい」は通用しません。提出＝審査の開始です。レビューキューは混雑しており、サイクルを無駄にしないために**完成度を上げてから一発勝負**で臨むのが得策です。

---

## まとめ

| 原則 | ポイント |
| --- | --- |
| 1. 単機能NG | エンドツーエンドのワークフローを束ねる |
| 2. 公式MCP優先 | Verified 率が上がると明言されています |
| 3. OSS必須 | クローズドは提出不可 |
| 4. validate全クリア | 警告含めすべて解消 |
| 5. SETUP.md | MCP含む場合は必ず用意 |
| 6. 最小権限 | 目的外のスコープは外す |
| 7. 利用規約確認 | 2ドキュメント必読 |
| 8. 完成してから提出 | 更新のたびに審査が走ります |

Verified バッジに近道はありません。ただし、外せる地雷はすべて外せます。この8原則を守ることで、少なくとも「落とされる理由」を消すことができます。

---

**参考リンク**
