---
id: "2026-06-24-codexを2週間使ったらssdに37tb書かれてanthropicはid確認を要求してきた-01"
title: "Codexを2週間使ったらSSDに37TB書かれて、AnthropicはID確認を要求してきた"
url: "https://qiita.com/lhjjjk4/items/0449e2ff8dc6319ac5c0"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "OpenAI", "Gemini"]
date_published: "2026-06-24"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

# Codexを2週間使ったらSSDに37TB書かれて、AnthropicはID確認を要求してきた

![Cover](https://files.catbox.moe/ifxfek.png)

> SSDキラーから身分証明書ウォールまで——AIコーディングツールに第三の道はあるのか？ある。OpenCodeという選択肢。

先週の木曜日の午後、MacBookのシステム情報を開いて、SSDの寿命健康度を3分間見つめていた。

先月の96%から91%に落ちていた。

3ヶ月で5%。これは正常じゃない。

ターミナルを開いてディスク書き込み量を確認した。`diskutil info disk0`。結果が出た瞬間、固まった。**総書き込み量37.2TB**。Macを買って半年も経っていない。

犯人は毎日使っている**OpenAI Codex CLI**——あの「AIプログラミングアシスタント」を謳うターミナルツール。

正直な反応：これコード書くのを手伝ってくれるやつでしょ？なんで俺のディスクを先に書き潰してんの？

> ⚠️ **これは個別事例ではない。** GitHub Issue #28224に詳細が記録されている：Codex CLIは年間約**640TB**のデータをSSDに書き込む。640TBだ。エンタープライズサーバー1台分の年間書き込み量が、MacBookの上で静かに走っている。 — Source

---

## 【技術コア】

### Codex CLIがやったこと

Codex CLIはAIとの各会話をローカルのSQLiteデータベースに保存する。これ自体は問題ない。問題はその保存方法にある。

💡 **例えて言うなら：** 日記帳があるとしよう。1行書きたいたびに、まず日記帳全体を新しいノートに書き写して、それからその1行を加える。書き写し終わった後、古いノートは机の上に積み上げたまま。1文字書くたびに、机の上の紙が1インチ高くなる。

技術的には、SQLiteの**WAL（Write-Ahead Logging）モード**と**TRACEレベルのログ**の組み合わせ。メッセージを送るたびに、Codexは：

1. 会話全体をWALファイルに書き込む
2. 挿入・クリーンサイクルをトリガー
3. WALファイルが数GBに膨れ上がる
4. メインデータベースにマージ
5. 同時に生WebSocket/SSEデータを**平文**で `~/.codex/` に書き出す

すべてのステップが狂ったように書き込む。しかもTRACEレベルログは**ハードコード**——`RUST_LOG=warn`を設定？無駄。読んでない。

| 指標 | 値 |
|------|-----|
| 21日間の実際の書き込み量 | **37TB** |
| 年間推定書き込み量 | **640TB** |
| 持続書き込み速度 | **5-16 MiB/s** |

### 何が起きるか

MacBook Pro M4ユーザーなら——SSDはマザーボードに半田付け。交換費用は**5-8万円**。640TB/年で、ディスクは2-3年持てば良い方。その後、新しいマザーボードをお迎えください。

さらに不安なのが**プライバシー問題**。Codexは生API通信データ（コードスニペット、会話内容を含む）を**平文**でディスクに書き出す。誰かがPCにアクセスすれば、`~/.codex/` を開いてすべて見られる。 — Source

### OpenAIの対応

> 「フィードバックを受け取りました。ご報告ありがとうございます。」

このIssueはGitHubで**stale**タグがついている。stale＝「期限切れ、対応しません」。10ヶ月経って、修正なし。回避策なし。公式声明なし。「確認中」のコメントすらない。

月額$20のChatGPT Plusを払って、CLIツールを使ったら、ツールがこっそりディスクを殺していて、運営は認めない。

どう計算しても合わない。

— — — *よし、ツールを換えよう* — — —

---

## 🔒 Claude Codeに逃げたら、KYCの壁にぶつかった

OK、Codexは信頼できない。Claude Codeに換えよう。对吧？

Claude Codeは確かに良い。AnthropicのフラグシップターミナルAIアシスタント。SWE-benchテストスコア72.7%（現時点最高）、マルチエージェント協調、深いGit統合、そしてヨダレが出るextended thinkingモード。

技術的に、現時点で最強のAIコーディングエージェントかもしれない。認める。

**だが。**

2026年4月14日、Anthropicは新ポリシーを発表：**全ユーザーが完全機能アクセスのためにID確認（KYC）を完了しなければならない**。7月8日から強制適用。

KYC。Know Your Customer。

💡 **イメージしてほしい：** 近所のスターバックスでコーヒーを頼む。店員が笑顔で「こんにちは、まず身分証明書を見せていただけますか？それからカメラに向かって笑っていただけますか。そのあとラテをお作りします。」呆れる。コーヒーだぞ？でもAnthropicの世界では、まさにそうだ。

### 確認フロー

AnthropicはID確認を**Persona**というサードパーティにアウトソース。必要なもの：

- **政府発行の物理的証明書**（パスポート、運転免許証、IDカード）——スクショでもスキャンでもなく、実物写真
- **リアルタイムセルフィー**——その場にいるか検出、写真の再撮は拒否
- **海外携帯電話番号**——+86（中国）はサポートリストにない
- **Visa/Mastercardクレジットカード**——Alipay、WeChat Payは不可

つまり、中国本土以外のパスポート、海外の電話番号、国際クレジットカードを持ち、カメラに向かってセルフィーを撮り、証明書と顔認証データをPersonaという米国企業に渡す必要がある。

それで完了。

> ⚠️ **中国本土ユーザー向け：** 中国本土、中国香港、中国マカオはすべてPersonaのサポート対象外。確認を提出する資格すらない。VPNで登録に成功しても、確認ステップで詰む。

---

## 🧱 中国の開発者にとって、その壁は特に高い

「プロキシを使えばいいじゃん、IP換えれば」

そう簡単ではない。**三重の罠**がある：

| 罠 | 状況 | 結果 |
|-----|------|------|
| **第一層：登録ブロック** | 中国IPで「Service not available in your region」 | 登録ページすら開けない |
| **第二層：確認＝BAN** | プロキシで登録 → 中国IDを提出 → Personaが未対応地域を検出 | アカウント即無効化。$20-200のサブスク返金なし |
| **第三層：事後処刑** | どうにか確認通過しても、ランダムな「整合性チェック」 | いつでもBAN可能。コードはクラウドにロック |

第二層が一番ヤバい。あるユーザーが体験を共有していた：丸一晩かけて全部の準備、顔スキャン通過、パスポート写真を提出。翌朝PCを開いたら——アカウントが消えていた。メールに一文：「Your account has been disabled due to policy violations」

説明なし。異議申し立て先なし。返金なし。

証明書も、顔データも、お金も渡した。そして「お前は対象外」と言われた。

> 💰 **計算してみよう：** Claude Pro $20/月、Claude Max $100-200/月。BANされたら年間最大$2,400の損失。さらに重要なのは、提出した生体データ——顔スキャン、ID写真——はすでにPersonaのサーバーにある。取り返せない。

正直、Claude Codeの技術は本当に素晴らしい。でもこの「まずIDを出せ」アプローチは、中国の開発者に対してこう言っているのと同じ：

**「お前は歓迎しない。」**

— — — *じゃあどうする？* — — —

---

## 🚀 【なぜ注目すべきか】OpenCode——どこから来たかを聞かない、何のモデルを使うかだけ

**OpenCode** というプロジェクトを紹介したい。

一言で：**MITライセンス、完全オープンソース、無料、ID不要、75以上のAIモデルプロバイダー対応**。

GitHubで**178K stars**。毎週200以上のコミット。コミュニティの活発さは当時のVS Codeに匹敵。

### OpenCodeとは

TypeScript + Goで書かれたターミナルAIコーディングエージェント。「Codex CLI + Claude Codeのオープンソースハイブリッド」と考えてほしい。独自のターミナルUI、コードの読み書き、コマンド実行、Git操作、そしてどのAIベンダーにも縛られない。

使いたいモデルは自分で選ぶ：

| プロバイダー | 利用可能モデル | アクセス方法 |
|------------|-------------|-------------|
| OpenAI | GPT-5.5, GPT-5, o3/o4-mini | APIキーまたは**ChatGPT Plus OAuth** |
| Anthropic | Claude 4.5 Sonnet/Opus | APIキーまたは**Claude Pro OAuth** |
| Google | Gemini 2.5 Pro/Flash | APIキー |
| ローカルモデル | Qwen3, DeepSeek, Llama | Ollama / LM Studio / llama.cpp |
| その他70以上 | OpenAI互換サービス各種 | カスタムエンドポイント + キー |

> 🔑 **キラー機能：OAuthルーティング。** OpenCodeの最も賢い設計——ChatGPT Plus（$20/月）またはClaude Pro（$20/月）の既存サブスクをそのままOpenCode経由で使える。**追加のAPI購入不要。** 毎月払っている$20がそのまま使える。しかもOpenCodeはミドルウェアとして、Codexのようにディスクを荒らしません。 — Source

### 2つの問題への解決策

| 問題 | Codex CLI | Claude Code | OpenCode |
|------|-----------|-------------|----------|
| **SSD書き込み** | 640TB/年 💀 | 正常 ✅ | 制御可能 ✅ |
| **ID確認** | 不要 ✅ | 強制KYC 💀 | 不要 ✅ |
| **中国で利用可能** | プロキシ必要 ⚠️ | ほぼ不可 💀 | 完全に可能 ✅ |
| **オープンソース** | Yes (Rust) ✅ | No 💀 | Yes (MIT) ✅ |
| **月額** | $20+ | $20-200 | **$0（ソフト自体）** |
| **モデル選択** | GPT-5.xのみ | Claudeのみ | **75以上** |
| **IDE統合** | なし | VS Code | VS Code + JetBrains |
| **プライバシー** | 平文保存 💀 | クラウド処理 ⚠️ | ローカル優先 + 暗号化 ✅ |

### コスト比較

| 方案 | 年間費用 | ディスクリスク | BANリスク |
|------|---------|-------------|----------|
| Codex Plus ($20/月) | $240 | 極大 | 低い |
| Claude Pro ($20/月) | $240 | なし | 極大（中国ユーザー） |
| **OpenCode + 既存サブスク** | **$0** | 制御可能 | なし |
| OpenCode + API従量課金 | ~$50-100 | 制御可能 | なし |
| OpenCode + ローカルモデル | **$0** | 制御可能 | なし |

既存のChatGPT PlusまたはClaude Proがあれば、OpenCode自体は**完全無料**。1円も追加不要。

— — — *移行ガイド* — — —

---

## 🛠️ 15分でできる移行ガイド

説得できた？換え方。簡単。15分で終わる。

**Step 1：OpenCodeインストール** ⏱ 2分

macOS：
```bash
brew install opencode-ai/tap/opencode
```

Linux：
```bash
curl -fsSL https://opencode.ai/install | bash
```

Windows：
```bash
npm install -g opencode-ai
```

ターミナルで`opencode`と入力してウェルカム画面が出れば成功。

**Step 2：AIサブスクを接続** ⏱ 5分

OpenCode内で`/connect`と入力：

```
$ opencode
Welcome to OpenCode!
> /connect

? Select provider:
  ❯ OpenAI (ChatGPT Plus/Pro)
    Anthropic (Claude Pro/Max)
    Google (Gemini)
    GitHub Copilot
    Custom Provider
```

OpenAIを選ぶとブラウザがChatGPTログインページを開く。認証後ターミナルに戻れば使える。

**そう、これだけ。** APIキーの生成も、コピペも不要。ログイン1回で完了。

**Step 3：ワークフローを移行** ⏱ 8分

Claude Codeからの場合、`CLAUDE.md`をコピーして`AGENTS.md`にリネーム。90%互換。

Codex CLIからの場合、`codex.json`を`opencode.json`に移行：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": { "openai": { "npm": "@opencode-ai/provider-openai" } },
  "model": "openai/gpt-5.5",
  "tools": { "bash": true, "edit": true, "read": true }
}
```

コマンド対応表：

| 機能 | Codex CLI | Claude Code | OpenCode |
|------|-----------|-------------|----------|
| プロジェクト初期化 | `codex init` | `/init` | `/init` |
| モデル切替 | 非対応 | `/model` | `/model` |
| サブスク接続 | 自動 | 自動 | `/connect` |
| コード実行 | `codex "..."` | `claude "..."` | `opencode "..."` |
| 対話モード | `codex` | `claude` | `opencode` |

> 🎁 **Pro Tips：**
> - プロジェクトルートに`AGENTS.md`を作成すると自動読み込み
> - `/model`でいつでもモデル切替（同一セッション内でも可）
> - 複数サブスクがあればマルチプロバイダールーティング設定可能
> - ローカルモデル（Ollama）も接続可能。オフラインでも使える

---

## 🏁 まとめ

この2週間を振り返ると、3つの段階を経た：

1. **衝撃**：Codexがディスクを静かに殺している。OpenAIは放置。
2. **怒り**：Claude CodeがID確認を要求。Anthropicは中国ユーザーを歓迎しない。
3. **安堵**：OpenCodeが現れた——無料、オープンソース、どこから来たかを問わない。

OpenCodeが完璧とは言わない。バグもあるし、足りない機能もある。UIもClaude Codeほど洗練されていない。でも最も重要な品質がある：**それはあなたのものだ**。

ID不要。BANリスクなし。ディスクを壊されない。MITライセンスのOSS、コードはGitHubに公開されていて、全行自分で監査できる。

AIツールがどんどん「囲い込みガーデン」になっていく時代に、OpenCodeは清風だ。良いツールは**人のために奉仕すべき**で、ツールを使うために「資格」を証明させるべきではない。

> 🔗 **関連リンク：**
> - [OpenCode GitHub](https://github.com/anomalyco/opencode) — Source
> - [OpenCode公式サイト](https://opencode.ai) — Source
> - [Codex SSD Bug: Issue #28224](https://github.com/openai/codex/issues/28224) — Source

Codex CLIを使っているなら——今日、SSD書き込み量を確認しよう。
Claude Codeを中国で使っているなら——Plan Bの準備を始めよう。
AIコーディングツールをまだ使っていないなら——おめでとう、すべての坑を飛び越えてOpenCodeから始めればいい。

*あなたのSSDも、あなたの身元も、AIツールを使うための代価であってはならない。*

---

📝 約4,500字 · 読了目安12分 · CodexからOpenCodeに移行中の開発者による記事
