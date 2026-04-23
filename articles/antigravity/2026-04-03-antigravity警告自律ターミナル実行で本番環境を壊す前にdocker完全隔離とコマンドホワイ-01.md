---
id: "2026-04-03-antigravity警告自律ターミナル実行で本番環境を壊す前にdocker完全隔離とコマンドホワイ-01"
title: "【Antigravity】警告!!「自律ターミナル実行」で本番環境を壊す前に。Docker完全隔離とコマンド・ホワイトリストの防御設計"
url: "https://note.com/dialogs_develop/n/neb42dee8b094"
source: "note"
category: "antigravity"
tags: ["AI-agent", "antigravity", "note"]
date_published: "2026-04-03"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

こんにちは！高橋です(\*'▽')

最近、Antigravityの「Agent Manager」や「自律ターミナル実行」、使い倒していますか？ 「AIに指示を出すだけで、勝手にターミナルを開いて環境構築からテストまで全部やってくれる！」 本当に魔法のような、Vibe Codingの新時代ですよね♪

ただ、その「全自動」の裏側で、背筋が凍るようなリスクが潜んでいることに気づいていますか？

**「もしAIが、本番環境の認証情報を読み込んだ状態で rm -rf / や drop table を実行してしまったら……？」**

ホストPC（今あなたが触っているパソコンそのもの）のターミナル権限をAIに全権委任するのは、実は非常に危険な行為です。

今回は、そんな悪夢を未然に防ぐための「絶対にやっておくべき防御設計」について、少し真面目にお話しします！ Antigravityのポテンシャルを100%引き出しつつ、インフラを絶対に壊さない「ゼロトラスト・ワークスペース」を一緒に構築していきましょう！

  

---

## 😱 実録：自律エージェントによる「ヒヤリハット」事例

防御策の前に、実際にどんな事故が起こり得るのか知っておきましょう。これ、海外のコミュニティでも結構報告されているんです。

* **事例1：勝手にライブラリを全消し！？** 依存関係のエラー解決をAIに丸投げしたところ、AIが「一度全部クリーンにしよう」と判断。プロジェクトに関係ないローカルの重要なグローバルパッケージまで勝手にアンインストールしてしまい、他のプロジェクトが全滅した……。
* **事例2：プロンプトインジェクションの恐怖** 外部の悪意あるコードをAIが読み込んでしまい、環境変数に設定されていたAWSやFirebaseのAPIキーを、外部の知らないサーバーに向けて curl コマンドで送信しようとした……。

想像するだけで怖いですよね💦 でも大丈夫！ 今から紹介する「3つの壁」を設定すれば、AIの暴走を完全にコントロールできるようになります。

---

## 🧱 防御の第一の壁：DevContainerによる環境の完全隔離

一番確実な方法は、「エージェントを使い捨てのコンテナ（箱）の中に閉じ込める」ことです。 Antigravityは、VS Codeなどでおなじみの「DevContainer（Docker）」に完全対応しています。  
ホストOSではなく、Dockerコンテナの中でAntigravityを動かすことで、万が一AIが暴走してシステムを破壊しても、コンテナを捨てるだけで済みます(\*'▽')b

### Step 1：必要な拡張機能とDockerの準備

1. 事前にPCに **Docker Desktop** をインストールし、起動しておいてください。
2. Antigravityを開き、プロジェクトのルートディレクトリに .devcontainer というフォルダを作成します。

### Step 2：devcontainer.json の作成

作成したフォルダの中に、devcontainer.json というファイルを作成し、以下のコードをコピペします。

JSON

```
{
  "name": "Secure Antigravity Agent",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "customizations": {
    "antigravity": {
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash",
        "agent.allowHostNetworkAccess": false
      }
    }
  },
  "forwardPorts": [3000, 8000],
  "postCreateCommand": "chmod +x .devcontainer/setup.sh && .devcontainer/setup.sh"
}
```

> **💡高橋のポイント** agent.allowHostNetworkAccess: false が超重要です！ これにより、コンテナ内からあなたのローカルネットワーク（社内イントラなど）への不正アクセスを遮断します。

### Step 3：コンテナでプロジェクトを開き直す

Antigravityの画面左下にある「><」のようなリモートウィンドウアイコンをクリックし、「Reopen in Container（コンテナで再度開く）」を選択します。 これで、AIは完全に隔離された安全な部屋（コンテナ）の中だけで作業するようになります！

---

## 🛡️ 防御の第二の壁：コマンド・ホワイトリストの導入

コンテナに閉じ込めたとはいえ、コンテナ内のデータも勝手に消されたら困りますよね。 次は、AIがターミナルで実行できるコマンドを「私たちが許可したものだけ（ホワイトリスト）」に制限します。

### Step 1：ラッパースクリプト（検閲官）の作成

.devcontainer フォルダの中に、safe\_bash.sh というファイルを作成し、以下を記述します。

Bash

```
#!/bin/bash

# 許可するコマンドのリスト（ホワイトリスト）
ALLOWED_COMMANDS=("ls" "pwd" "cat" "echo" "npm run" "npm install" "pytest" "git status")

# AIが実行しようとしたコマンドを取得
CMD="$*"

# コマンドが許可リストに含まれているかチェック
IS_ALLOWED=0
for ALLOWED in "${ALLOWED_COMMANDS[@]}"; do
  if [[ "$CMD" == "$ALLOWED"* ]]; then
    IS_ALLOWED=1
    break
  fi
done

if [ "$IS_ALLOWED" -eq 1 ]; then
  # 許可されていればそのまま実行
  eval "$CMD"
else
  # 許可されていなければエラーを返してAIに警告する
  echo "[SECURITY ERROR] Command not allowed: $CMD"
  echo "許可されていないコマンドです。破壊的アクションの可能性があるため実行をブロックしました。"
  exit 1
fi
```

### Step 2：Antigravityに検閲官を通させる設定

先ほどの devcontainer.json の設定（settingsの中）に、以下を追記します。

JSON

```
"agent.terminalExecutionCommand": "/bin/bash .devcontainer/safe_bash.sh"
```

これで、AIが rm -rf などを実行しようとしても、このスクリプトが弾いて「エラー」としてAIに返してくれます。AIは「あ、このコマンドはダメなんだな」と学習し、別のアプローチを考えてくれるようになります！

---

## 🚨 防御の第三の壁：Agent Managerの「キルスイッチ」

最後の壁は、人間による監視です。   
Antigravityの Agent Permissions（エージェント権限設定）を見直しましょう。

### 手順：破壊的アクションの承認制（Human-in-the-loop）

1. Antigravityの設定画面（Settings）から Agent Permissions を検索します。
2. **Terminal Execution（ターミナル実行）** の項目を Always Allow（常に許可） から **Ask for Confirmation on Destructive Commands（破壊的コマンドは確認を求める）** に変更します。

これを設定しておくと、もしホワイトリストをすり抜けるような複雑なコマンド（例えばスクリプトファイルを通じた実行など）を行おうとした際、Antigravityの画面上に「このコマンドを実行してもいいですか？ [Approve] / [Reject]」というポップアップが出ます。

私たちが「承認」ボタンを押さない限り、AIは勝手に手を動かせません。まさに最強のセーフティネット（キルスイッチ）ですね！

---

## 🎁 おわりに：制限は「AIを信頼するため」の土台

「こんなに制限ガチガチにしたら、AIの便利さが半減するのでは？」と思う方もいるかもしれません。

でも、逆なんです。  
**「絶対に致命的な事故が起きない安全な土台」があるからこそ、私たちは安心してAIに大規模なリファクタリングや複雑なデバッグを丸投げして、夜ぐっすり眠ることができるんです。**

フェイルセーフは、AIの邪魔をするものではなく、人間がAIを信頼して任せるためのパートナーシップの証拠です(\*'▽')

まずは手元のプロジェクトで、DevContainerの導入から試してみてくださいね！   
それでは今回はここまで(\*'▽')ﾉｼ
