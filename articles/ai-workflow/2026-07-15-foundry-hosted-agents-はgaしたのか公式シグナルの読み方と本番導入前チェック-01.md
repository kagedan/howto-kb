---
id: "2026-07-15-foundry-hosted-agents-はgaしたのか公式シグナルの読み方と本番導入前チェック-01"
title: "Foundry Hosted Agents はGAしたのか？公式シグナルの読み方と本番導入前チェック"
url: "https://zenn.dev/kazu_aiengineer/articles/foundry-hosted-agents-ga-check"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "OpenAI", "Python", "zenn"]
date_published: "2026-07-15"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## 先に結論

* Microsoft Foundry の **Hosted Agents**（自作コードのAIエージェントをコンテナごとMicrosoftマネージドで動かす仕組み）は、公式に「**2026年7月上旬にGA予定**」と予告されていた
* 7/15時点で「GAしました」という単独のアナウンス記事は見当たらないが、**SDKのstable化（7/1）とドキュメントのpreview表記除去（7/13更新）** という2つの公式シグナルからGA到達と判断できる状態
* GA後の確定仕様には**本番コストとアーキテクチャに直結する要素**（セッション単位課金・15分アイドルタイムアウト・Japan East対応など）が含まれる。この記事では導入前チェックリストとして整理した

## Hosted Agents とは何か

Hosted Agents は Foundry Agent Service の機能で、**LangGraph・Microsoft Agent Framework・独自実装など任意のフレームワークで書いたエージェントを、コンテナイメージとしてそのままMicrosoftマネージド基盤にデプロイできる**仕組みです。

ポータル上でプロンプトとツールを設定する「プロンプトベースのエージェント」と違い、コードを持ち込めるのが特徴で、セッションごとにVM分離されたサンドボックス（専用のcompute・メモリ・永続ファイルシステム）が割り当てられます。

「Hosted Agents とは何か」自体は Build 2026（6月）時点の情報で日本語記事がすでに複数あります。なのでこの記事では、**「GAしたのか？」の確認方法**と**GA時点の確定仕様**に絞ります。

## 「GAしたのか」を公式情報から確定する

「GAされました」という切りのいいアナウンスが見つからないとき、私は次の3点を確認しています。今回のHosted Agentsはその良い実例だったので、確認過程ごと共有します。

### シグナル1: 公式ブログの事前予告

Build 2026版の公式ブログ（2026-06-02）に、次の記載があります。

> Hosted agents in Foundry Agent Service, expected to reach general availability by early July 2026

つまり「7月上旬GA」は公式の予告でした。ただしこれは*予定*であり、実際に到達したかは別の証拠が要ります。

### シグナル2: SDKのstable化（これが一番確実）

PyPI の [azure-ai-projects](https://pypi.org/project/azure-ai-projects/) を見ると、**2.3.0（stable・非beta）が2026-07-01にリリース**され、hosted agent関連のメソッド群（セッション・ファイル操作・agent code系）が`.beta`サブクライアントから正式なoperationsに昇格しています。

Microsoft系サービスでは、**プレビュー機能はSDKでもbeta扱いのまま**なのが通例です。逆に言えば、SDKでstableに昇格した機能は、サービス側がGA品質に達したという強いシグナルになります。

### シグナル3: Learnドキュメントのpreviewラベル

Learn の [Hosted agents コンセプトページ](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents)（2026-07-13更新版）を見ると:

* **5月時点のアーカイブではタイトルが "Hosted agents in Foundry Agent Service (preview)" だった**のに対し、現行版では **(preview) が外れ、"Limitations during preview" 節も消えている**
* 一方で、同ページ内の **A2Aプロトコルには "(preview)" が明記**されたまま

previewのものにはラベルが残り、Hosted Agents本体からは除去された。この書き分けは編集上の意図と読めます。なお7/7付の公式ブログ時点ではまだ「GA is close」（もうすぐ）という表現だったので、**決め手はこの7/13のドキュメント更新**です。

**結論**: 3つのシグナルが揃っており、7/15時点でHosted AgentsはGAに到達していると判断できます。ただし後述の通り、**周辺機能にはpreviewが残っている**ので「全部GA」ではありません。

## GA時点の確定仕様 — 本番導入前チェックリスト

以下はすべて Learn の公式ドキュメント（2026-07-13更新版）の記載に基づきます。

### ① 課金モデル: 「セッション単位」を理解しないとコストが読めない

Hosted Agents は**レプリカ数の設定が存在しません**。セッションごとにサンドボックスが立ち上がり、**課金はアクティブな全セッションで消費したCPU+メモリの合計**です。

公式ドキュメントに重要な注意があります:

> Billing is based on cpu + memory consumed across all active sessions, so oversizing multiplies cost by your concurrency.

つまり、**サンドボックスのサイズ超過見積もりは同時セッション数の分だけ掛け算でコストに跳ねます**。1セッションあたりのサイズは次の3択です。

| CPU | メモリ |
| --- | --- |
| 0.5 vCPU | 1 GiB |
| 1 vCPU | 2 GiB |
| 2 vCPU | 4 GiB |

右サイジングの公式推奨手順は「代表的なワークロードを流し、自動連携されるApplication Insightsで実測ピークを見て、**割り当ての70%を超えるなら上げ、大きく下回るなら下げる**」。バージョンはイミュータブルなので、変更のたびに新バージョン作成→再テストになります。

### ② セッションのライフサイクル: 15分と30日を設計に織り込む

* **アイドル15分**でcomputeが解放される（scale-to-zero）。`$HOME`と`/files`の中身は永続化され、再開時に復元される
* **30日間非アクティブでセッションは完全削除**
* ディスクは**1 vCPU以上で最大20 GiB/セッション**。ただし**約20%はシステム予約**で、残りをコンテナイメージ・`$HOME`等で分け合う

アイドル復帰時のコールドスタートについて公式は「予測可能（predictable cold starts）」と表現しており（具体的な秒数は非公表）、状態は復元されます。常駐前提のアーキテクチャから発想を変える必要がありますが、逆に言えば**待機中のcomputeコストがゼロ**になるのはエージェントワークロードと相性が良い部分です。

### ③ リージョン: Japan East が初期リストに入っている

GA時点の提供リージョンは20リージョンで、**Japan East が含まれています**。東日本で完結させたい国内案件にとってはここが一番の朗報かもしれません（リストは今後拡大予定と明記あり）。

### ④ ネットワーク・セキュリティの落とし穴

* **2026-06-25より後に作成したFoundryプロジェクト**は、エージェントイメージ用のprivate（network-secured）Azure Container Registryをサポート。**それ以前に作成した既存プロジェクトはACRのパブリックエンドポイント到達性が必要**なまま。ネットワーク分離要件がある場合、プロジェクトの作り直しを検討する価値があります
* 公式ドキュメントが明言: **シークレットをコンテナイメージや環境変数に入れない**（managed identity＋Key Vault接続を使う）。環境変数はバージョン作成時にイミュータブルなので、うっかり入れると履歴に残り続けます
* デプロイごとに**専用のEntra ID（agent identity）が自動発行**され、モデル呼び出しや下流サービスへのアクセスはこのIDで行う。外部リソース（自前のStorageなど）へはこのIDにRBACを手動で付与する方式

### ⑤ プロトコル選択: 迷ったらResponses

エージェントのエンドポイントは複数プロトコルを同時に持てます。公式の使い分け指針を要約すると:

| ユースケース | プロトコル |
| --- | --- |
| チャットボット・RAG・バックグラウンド処理 | **Responses**（OpenAI互換。会話履歴・ストリーミングをプラットフォームが管理） |
| Webhook受信・非会話型処理・独自ペイロード | **Invocations**（任意JSONの入出力。セッション管理は自前） |
| リアルタイム音声 | **Invocations (WebSocket)** |
| Teams / Microsoft 365 公開 | Responses + Activity（ブリッジは自動） |
| エージェント間連携 | A2A（**これはまだpreview**） |

### ⑥ まだpreviewのもの（「全部GA」ではない）

周辺には2026-06-02（Build 2026）発表のpreview機能群が多数あります。導入検討時に混同しないよう注意してください。

* A2Aプロトコル、Memory、Agent Optimizer、Toolboxes拡張（Tool Search / Work IQ / Fabric IQ）、Routines など → **preview**
* 言語サポートは **PythonとC#**（プロトコルライブラリはフレームワーク非依存）

## どこから始めるか

公式サンプル（Microsoft Agent Framework / LangGraph / 素のPython）が [foundry-samples リポジトリ](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents) にまとまっています。`azd`（Azure Developer CLI）の `azure.yaml` に `azure.ai.agent` サービスを定義するか、SDK（`azure-ai-projects` 2.3.0以降）でバージョン定義を書くのが入口です。

実際のデプロイから課金の実測までは、別途手を動かして検証記事にする予定です。

## 参考リンク（一次ソース）
