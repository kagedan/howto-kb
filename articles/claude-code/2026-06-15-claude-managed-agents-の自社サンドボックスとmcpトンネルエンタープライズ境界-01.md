---
id: "2026-06-15-claude-managed-agents-の自社サンドボックスとmcpトンネルエンタープライズ境界-01"
title: "Claude Managed Agents の自社サンドボックスとMCPトンネル：エンタープライズ境界内でエージェントを動かす設計判断"
url: "https://qiita.com/YushiYamamoto/items/398b6c20b6b9405607cd"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "TypeScript", "qiita"]
date_published: "2026-06-15"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

2026年5月19日、AnthropicはClaude Managed Agentsに2つの機能を追加した。
**自社サンドボックス（Self-Hosted Sandboxes、パブリックベータ）**と**MCPトンネル（リサーチプレビュー）** だ。

これまでのManaged Agentsは「エージェントループ」も「ツール実行」もAnthropicのクラウド上で動いていた。
今回の変更で**ツール実行だけを自社インフラに移せる**ようになった。コードは自社ネットワーク外に出ない。

ただし「どこで何を動かすか」の設計判断を誤ると、かえって運用が複雑になる。この記事はその判断基準を整理した実務ノートだ。

## 結論：何が変わったのか

| 項目 | 従来のManaged Agents | 自社サンドボックス使用時 |
| --- | --- | --- |
| エージェントループ（オーケストレーション） | Anthropicインフラ | **変わらずAnthropicインフラ** |
| ツール実行（Bash・ファイル操作） | Anthropicクラウドサンドボックス | **自社インフラ（または選択プロバイダ）** |
| 社内ネットワーク接続 | 不可 | MCPトンネル経由で可能（リサーチプレビュー） |
| コンプライアンス対象データ | Anthropicサンドボックスを通る | 自社境界内に留まる |
| ゼロデータリテンション（ZDR）対象 | 非対象（セッション状態が永続化） | 同左（変わらず非対象） |

「エージェントループ（コンテキスト管理・エラーリカバリ）はAnthropicのインフラ上に留まる。ツール実行だけが自社環境に移る」という分離がポイントだ。

セッション履歴やサンドボックス状態はサーバサイドで永続化されるため、ZDRやHIPAA BAAの対象外である点は変わらない。

## 自社サンドボックスを選ぶべきケース

自社サンドボックスが必要になるのは、主に以下の状況だ。

- **コード・ファイルが自社ネットワーク外に出せない**：社内のGitHub EnterpriseやプライベートGitLabからクローンしてテストを回すような用途
- **特定のコンピューティングリソースが必要**：大規模ビルドや画像生成など、デフォルトサンドボックスより多くのCPU・メモリが必要なジョブ
- **既存のネットワークポリシーや監査ログ基盤をそのまま使いたい**：社内に整備済みのセキュリティツールとの統合

逆に「公開APIを叩くだけ」「外部パッケージをダウンロードするだけ」のジョブは、Anthropicのクラウドサンドボックスで足りるケースが多い。インフラ管理コストとのトレードオフをまず確認する。

## サンドボックスプロバイダの選択肢

自社インフラを直接使う以外に、Anthropicが動作確認済みのマネージドプロバイダが4つある。

| プロバイダ | 特徴 | 向いているユース |
| --- | --- | --- |
| **Cloudflare** | microVM＋isolate。ゼロトラスト秘密情報注入、エグレスプロキシ設定可 | 監査・エグレス制御が重要な用途 |
| **Daytona** | フルコンピュータ、長時間ステートフル。SSH接続・一時停止＆復元 | 数時間動き続けるエージェント |
| **Modal** | AI特化クラウド。サブ秒起動、CPU/GPUオンデマンド、大量並列対応 | 大量並列・GPU必要な計算タスク |
| **Vercel** | VMセキュリティ＋VPCピアリング。ネットワーク境界でクレデンシャル注入 | 金融・フィンテックなど厳格なセキュリティ要件 |

選択の最初の分岐は「**長時間ステートフルか、バーストでスケールさせたいか**」だ。数時間動かし続けてSSHで接続したいなら Daytona、大量並列をコールドスタートで回したいなら Modal が起点になる。

## MCPトンネルの仕組みと制約

MCPトンネルは「社内ネットワーク上にあるMCPサーバをエージェントから呼べるようにする」機能だ。

仕組みはシンプルだ：自社側に軽量ゲートウェイをデプロイし、そこから**外向き1接続だけ**Anthropicのインフラに張る。インバウンドのファイアウォール解放は不要で、通信はエンドツーエンドで暗号化される。
エージェントから見ると、社内DB・プライベートAPI・ナレッジベース・チケットシステムが「ツールとして呼べるMCPサーバ」として見える。

設定はClaude ConsoleのWorkspace settingsから組織管理者が行う。現状リサーチプレビューのため、利用には事前申請が必要だ。

## 実装チェックリスト

### 事前確認

- [ ] Claude PlatformのAPIキーを取得している
- [ ] すべてのManaged AgentsリクエストにBetaヘッダ `managed-agents-2026-04-01` を付与している
- [ ] 自社サンドボックスが本当に必要か、クラウドサンドボックスで足りるかを確認した
- [ ] MCPトンネルが必要な場合、アクセス申請を済ませた（`claude.com/form/claude-managed-agents`）

### サンドボックス設定

- [ ] サンドボックスプロバイダを選定した（Cloudflare / Daytona / Modal / Vercel / 自社インフラ）
- [ ] サンドボックス内のネットワークポリシーを自社標準に合わせた
- [ ] 機密ファイルやシークレットの扱いを定義した（サンドボックスに持ち込む vs MCPトンネル経由で参照する）
- [ ] セッション削除ポリシーを決めた（セッションはAPIで手動削除可能）

### MCPトンネル設定（申請済みの場合）

- [ ] 軽量ゲートウェイを社内ネットワーク上にデプロイした
- [ ] ゲートウェイからの外向き接続のみ許可（インバウンド解放は不要）
- [ ] ConsoleのWorkspace settingsでトンネルを設定した（Organization Admin権限が必要）
- [ ] エージェントから呼び出すMCPサーバのツール一覧を確認した

## 失敗パターン

**「全部自社サンドボックスに移せばいい」と考える**  
エージェントループはAnthropicのインフラに残る。
自社サンドボックスはツール実行だけだ。「コンプライアンス上クラウドに出せないデータのみ自社に置く」が基本で、全部移そうとするとインフラ管理コストが増えるだけになる。

**MCPトンネルを汎用プロキシ代わりに使おうとする**  
MCPトンネルはMCPサーバへの接続専用だ。
任意のHTTPリクエストをトンネリングする汎用プロキシではない。社内DBを直接叩きたい場合は、DBの前にMCPサーバを立てる構成が必要になる。

**ZDR・HIPAA BAAが必要な用途に使う**  
現時点でManaged Agentsはセッション状態が永続化されるため、ZDR・HIPAA BAAの対象外だ。
規制上これらが必須の場合は、Messages APIで自前のエージェントループを実装する構成を選ぶ必要がある。

**事前申請なしにMCPトンネルを利用しようとする**  
MCPトンネルはリサーチプレビューで、デフォルトでは有効になっていない。APIが `403` や `feature not enabled` 系のエラーを返す場合は申請が通っていない可能性が高い。

## 参考リンク

- [New in Claude Managed Agents: self-hosted sandboxes and MCP tunnels（Anthropic公式ブログ、2026-05-19）](https://claude.com/blog/claude-managed-agents-updates)
- [Claude Managed Agents overview（公式ドキュメント）](https://platform.claude.com/docs/en/managed-agents/overview)
- [Self-hosted sandboxes ドキュメント](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes)
- [Claude Managed Agents クックブック（GitHub）](https://github.com/anthropics/claude-cookbooks/tree/main/managed_agents/self_hosted_sandboxes)

---

:::note
**この記事を書いた人✏️@YushiYamamoto**
ITPRODX.com代表 / AIアーキテクト
Next.js / TypeScript / n8nを活用した自律型アーキテクチャ設計を専門としています。
日々の自動化の検証結果や、ビジネス側の視点（ROI等）に関するより深い考察は、以下の公式サイトおよびnoteで発信しています。
:::

https://itprodx.com

https://note.com/prodouga
