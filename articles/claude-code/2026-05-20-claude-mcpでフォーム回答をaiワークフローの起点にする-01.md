---
id: "2026-05-20-claude-mcpでフォーム回答をaiワークフローの起点にする-01"
title: "Claude MCPでフォーム回答をAIワークフローの起点にする"
url: "https://zenn.dev/lova_man/articles/ee610c12b41bc4"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "GPT", "zenn"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/d9519c5e7642-20260520.png)

Claude MCPでフォームを扱うとき、最初に思いつくのはフォーム作成だと思います。

```
問い合わせフォームを作って
セミナー申込フォームを作って
採用応募フォームを作って
```

これは分かりやすい使い方です。

Claudeでフォーム作成ができれば、白紙から項目を考える時間はかなり短くなります。FORMLOVAのようにMCPサーバーへ接続していれば、文章案だけでなく、実際の非公開下書きやプレビューまで進められます。

ただ、フォーム業務の本体はそこではありません。

本当に重いのは、回答が届いた後です。

この記事では、Claude MCPを「フォームを作るための接続」ではなく、フォーム回答をAIワークフローの起点にする設計として整理します。

## 前提: MCPは外部システムへの接続口

MCPは、Model Context Protocolの略です。

公式ドキュメントでは、AIアプリケーションが外部システムのデータ、ツール、ワークフローへ接続するための標準として説明されています。

Claude Codeの公式ドキュメントでも、MCPサーバーを接続すると、Claude Codeが外部のツール、データベース、APIにアクセスできると説明されています。リモートHTTPサーバーの追加、ローカルstdioサーバー、scopeの分け方なども整理されています。

つまり、Claude MCPは「Claudeに機能を足すプラグイン」ではなく、Claudeから外部システムを扱うための標準化された接続口です。

フォームサービスに置き換えると、こうなります。

```
Claude
  -> FORMLOVA MCP
    -> フォーム作成
    -> フォーム編集
    -> 回答取得
    -> 回答分類
    -> ステータス変更
    -> メール/リマインド/分析
```

ここで大事なのは、`create_form` だけを見ないことです。

## 悪い捉え方: Claudeでフォームを作れたら終わり

フォーム作成だけを見ると、MCPの価値はこう見えます。

```
ユーザー:
  問い合わせフォームを作って

Claude:
  FORMLOVA MCPのcreate_formを呼ぶ
  下書きURLを返す
```

これは便利です。

ただ、この時点ではまだ業務は始まっていません。

フォームは公開され、誰かが送信して、はじめて業務データになります。

公開後には、少なくとも次の状態が出てきます。

```
response.submitted
acknowledgement.sent
intent.classified
owner.assigned
status.in_progress
reply.drafted
reply.sent
status.done
```

Claude MCPでフォームを扱うなら、作成後の状態まで扱えるかを見たほうがいいです。

## フォーム回答はAIワークフローの起点になる

フォーム回答は、AIワークフローの入力として扱いやすいです。

理由は、最初から構造化されているからです。

```
{
  "formId": "contact",
  "responseId": "resp_123",
  "submittedAt": "2026-05-20T06:30:00Z",
  "fields": {
    "name": "山田太郎",
    "email": "taro@example.com",
    "category": "料金相談",
    "message": "有料プランの違いを知りたいです"
  }
}
```

メールやSlackの文章は、毎回かなり揺れます。

一方で、フォーム回答にはフィールド名があります。送信日時もあります。どのフォームから来たのかも分かります。

Claudeが扱う入力として、これはかなり安定しています。

だから、Claude MCPでフォーム回答を扱う場合は、単に「回答を読ませる」だけでなく、次の業務状態へ進める設計にできます。

```
回答を取得する
問い合わせ種別を分類する
営業メールを除外する
担当者候補を出す
返信文を下書きする
ステータスを更新する
週次レポートを作る
```

これが、フォーム回答を起点にしたAIワークフローです。

MCPサーバーを設計するとき、最初はCRUDに寄りがちです。

```
create_form
update_form
list_forms
get_response
update_response
```

もちろん、これらは必要です。

でも、ClaudeのようなAIクライアントから実務を進めるなら、業務単位のtoolも必要になります。

たとえばフォーム回答後なら、こういうtoolのほうがモデルは扱いやすいです。

```
list_new_responses
classify_response_intent
exclude_sales_message
set_response_status
assign_response_owner
draft_reply_email
configure_auto_reply
schedule_reminder
generate_response_summary
```

`update_response` という大きなtoolだけだと、モデルは「何をどう更新すべきか」を毎回考えなければいけません。

一方で、`set_response_status` や `draft_reply_email` のように業務単位に分かれていると、Claudeはユーザーの依頼を分解しやすくなります。

```
ユーザー:
  今週の問い合わせで料金相談っぽいものを見つけて、返信案を作って

Claude:
  1. list_new_responses
  2. classify_response_intent
  3. filter intent = pricing
  4. draft_reply_email
  5. ユーザーへ確認を求める
```

この設計のほうが、AIワークフローとして安定します。

## read / suggest / write を分ける

Claude MCPでフォーム運用を扱う場合、特に重要なのは副作用の境界です。

フォーム回答を読むだけなら、比較的安全です。

返信文を下書きするだけなら、まだ安全です。

でも、実際にメールを送る、ステータスを変更する、公開中フォームを書き換える、回答を削除する、となると話が変わります。

私は、フォーム運用MCPでは操作を3段階に分けるのがよいと思っています。

| 段階 | 例 | 方針 |
| --- | --- | --- |
| read | 回答取得、フォーム一覧、集計 | 実行しやすい |
| suggest | 分類候補、担当者候補、返信文下書き | 結果を人間に見せる |
| write | ステータス変更、メール送信、公開フォーム変更 | 明示確認を挟む |

たとえば、Claudeが返信文を作るところまでは自動でよいです。

でも、送信は別です。

この確認境界がないと、AIワークフローは実務に入れにくくなります。

MCPで外部システムへつながるほど、できることは増えます。同時に、止める場所も設計しないといけません。

## Claude Desktop と Claude Code で役割が違う

Claude MCPといっても、使う場所で向き不向きがあります。

Claude Desktopは、フォーム運用を会話で進めるのに向いています。

```
問い合わせフォームを作って
プレビューを見せて
自動返信文をもう少し丁寧にして
昨日の回答を分類して
料金相談だけ返信案を作って
```

一方でClaude Codeは、開発・設定・リポジトリ文脈に寄せやすいです。

```
このプロジェクトにFORMLOVA MCPを追加して
フォーム送信後のSlack通知設計を確認して
公開前レビューの結果をもとに修正して
```

FORMLOVA側では、Claude Desktop向けの接続ガイドとClaude Code向けの接続ガイドを分けています。

同じMCPサーバーでも、ユーザーの作業場所が違うからです。

フォームを作る、回答を見る、返信案を作るならClaude Desktopが分かりやすい。

プロジェクトにMCP設定を入れる、開発作業と一緒にフォームを扱うならClaude Codeが向いている。

この使い分けは、Claude MCPの記事を書くときにも混ぜないほうがいいと思っています。

## ChatGPTとの違いは「思想」よりも接続面

ChatGPTでもフォーム作成はできます。

ChatGPTでフォーム作成をする場合も、フォーム項目案を作るだけなら十分できます。MCPや外部アプリ連携が使える環境なら、実際のフォームサービスへつなぐこともできます。

Claudeでフォーム作成をする場合も、本質は同じです。

違いは「どちらのモデルが賢いか」だけではありません。

実務上は、どのクライアントで、どのMCPサーバーを、どのscopeで、どの権限で接続するかが効きます。

フォーム運用の設計としては、ChatGPTかClaudeかよりも、次の点が重要です。

```
作成後の回答を読めるか
回答を分類できるか
状態を戻って確認できるか
副作用のある操作で確認できるか
別サービスのMCPと横断できるか
```

Claude MCPの記事では、Claudeの接続手順だけに寄せるより、この運用面まで見たほうが実務に近くなります。

## 実装イメージ: 返信案まで作る

たとえば、問い合わせフォームの回答に対して返信案を作る流れを考えます。

```
ユーザー:
  昨日来た問い合わせのうち、料金相談だけ返信案を作って
```

MCP tool側は、次のように分かれていると扱いやすいです。

```
type ListResponsesInput = {
  formId: string;
  submittedAfter?: string;
  status?: "new" | "in_progress" | "done" | "excluded";
};

type ClassifyResponseInput = {
  responseId: string;
  labels: Array<"pricing" | "support" | "recruiting" | "sales_pitch">;
};

type DraftReplyInput = {
  responseId: string;
  tone: "polite" | "friendly" | "concise";
  purpose: "answer_question" | "request_more_info" | "schedule_meeting";
};
```

Claudeはまず回答を取り、分類し、対象を絞り、返信案を作ります。

ここまではsuggestです。

その後に送信するなら、別のwrite toolにします。

```
type SendReplyInput = {
  responseId: string;
  draftId: string;
  confirmationToken: string;
};
```

返信案を作るtoolと送信するtoolを分けることで、Claudeは作業を進められますが、外部への副作用は人間の確認で止められます。

## まとめ

Claude MCPでフォームを扱うなら、フォーム作成だけで終わらせないほうがいいです。

`Claudeでフォーム作成` は入口として大事です。

ただ、フォーム業務の価値は、回答が届いた後に出ます。

```
フォームを作る
回答が届く
分類する
担当者を決める
返信案を作る
ステータスを変える
集計する
改善する
```

この流れをClaudeから扱えるようにするのが、フォーム領域でのMCPの面白いところです。

MCP対応フォームサービスを見るときは、「Claudeからフォームを作れるか」だけでなく、「Claudeからフォーム回答後の仕事まで扱えるか」を見たほうがいいと思います。

## 関連リンク
