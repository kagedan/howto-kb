---
id: "2026-03-31-過去の-session-をほしい時に参照する方針で-claude-mem-のトークン消費を激減させた-01"
title: "過去の session をほしい時に参照する方針で claude-mem のトークン消費を激減させた話"
url: "https://qiita.com/nishiken1118/items/6b16557fcabf784c861e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

[claude-mem](https://github.com/thedotmack/claude-mem) は Claude Code にセッション間の永続メモリを与える便利なツールですが、観測記録が蓄積されるにつれてセッション開始時の自動注入でトークン消費が膨らんでいきます。

この記事では、トークン消費を抑えつつ claude-mem の恩恵を最大限に受けるための設定を、実際の運用をもとに解説します。

---

## 推奨設定の全体像

### 設定の方針

**「事前の自動注入を極限まで絞り、必要な情報は都度取得する」** という方針です。  
claude-mem が持つセッション開始時のコンテクスト注入を極限まで絞る代わりに、こちらの指示で明示的に過去の詳細な情報をとってくるようにします。

### settings.json

設定ファイルは `~/.claude-mem/settings.json` にあります。以下が実際に使っている設定です。  
まずは設定項目の概要と設定値の説明をします。

```
{
  // データディレクトリの場所。claude-mem が観測記録や DB ファイルを保存するパス
  // デフォルト: "~/.claude-mem" | 値: 任意のディレクトリパス
  "CLAUDE_MEM_DATA_DIR": "~/.claude-mem",

  // メモリ処理（観測記録の生成や要約）に使用する AI モデル
  // デフォルト: "sonnet" | 値: "haiku" / "sonnet" / "opus"（フルネーム "claude-sonnet-4-5" 等でも可）
  // 上位モデルほど要約の品質は上がるが、メモリ処理自体の API コストが増える
  "CLAUDE_MEM_MODEL": "sonnet",

  // 認証方法。"cli" は Claude Code の認証をそのまま使う
  // デフォルト: "cli" | 値: "cli" / "api-key"
  "CLAUDE_MEM_CLAUDE_AUTH_METHOD": "cli",

  // インデックスに含める観測記録の件数
  // デフォルト: 50 | 最小: 0
  // セッション開始時にインデックス（タイトル + ID + トークン数）として自動注入される
  // 1 件あたり約 50〜100 トークンを消費する（公式 README に記載）
  // 大きくすると: カバー範囲が広がり古い作業の記録もインデックスに含まれるが、トークン消費が増加する
  // 小さくすると: トークン消費は減るが、直近の作業しかインデックスに載らなくなる
  "CLAUDE_MEM_CONTEXT_OBSERVATIONS": "1",

  // 全文展開する観測記録の件数
  // デフォルト: 0 | 最小: 0
  // narrative フィールド（詳細な文脈情報）を全文展開する件数を指定する
  // 1 件あたり 500〜1,000 トークンが追加される（公式 README に記載）
  // 大きくすると: エージェントが最初から詳細な文脈を把握できるが、トークン消費が急増する（10 件で 5,000〜10,000 トークン追加）
  // 0 にすると: インデックスのみの超軽量モード。詳細は毎回 get_observations で取得する
  "CLAUDE_MEM_CONTEXT_FULL_COUNT": "0",

  // Context Index に含める直近のセッション数
  // デフォルト: 10 | 最小: 0
  // 大きくすると: より過去のセッション情報もカバーするが、トークン消費が増加する
  // 小さくすると: 直近のセッションのみになるが、トークンは節約できる
  "CLAUDE_MEM_CONTEXT_SESSION_COUNT": "1",

  // 全文展開時に使うフィールド
  // デフォルト: "narrative" | 値: "narrative" / "facts"
  //   "narrative" — 観測記録を文章形式で要約したもの。文脈を理解しやすく、Claude が自然言語として扱いやすい
  //   "facts"     — 事実を箇条書きの JSON 配列で列挙したもの。コンパクトだが前後の文脈が失われ判断材料として不十分なことがある
  "CLAUDE_MEM_CONTEXT_FULL_FIELD": "narrative",

  // ワーカープロセスのポート番号
  // デフォルト: "37777" | 値: 任意のポート番号
  "CLAUDE_MEM_WORKER_PORT": "37777",

  // PostToolUse フックで観測記録の対象から除外するツールのリスト
  // デフォルト: ""（空＝すべてのツールを記録） | 値: ツール名のカンマ区切り
  // 除外すると対象ツールの入出力が記録されなくなり、観測記録のノイズが減る
  // 特に Read/Glob/Grep は 1 セッションで数十〜数百回発火するが、読んだだけでは何も変わっていない
  // 除外しすぎると Edit や Bash の前後文脈が欠落するため、変更を伴わないツールに絞るのが安全
  // 除外対象:
  //   Read               — ファイル読み取り。1 セッションで大量発火し、状態を変更しない
  //   Glob               — ファイル検索。同上
  //   Grep               — テキスト検索。同上
  //   ListMcpResourcesTool — MCP リソース一覧取得。メタ操作であり記録する価値が低い
  //   SlashCommand        — スラッシュコマンド実行。内部的な操作
  //   Skill              — スキル呼び出し。同上
  //   TodoWrite          — TODO リスト更新。一時的な情報
  //   AskUserQuestion    — ユーザーへの質問。対話の中間状態
  "CLAUDE_MEM_SKIP_TOOLS": "ListMcpResourcesTool,SlashCommand,Skill,TodoWrite,AskUserQuestion,Read,Glob,Grep",

  // Context Index に表示する観測タイプのフィルタ
  // デフォルト: 全種類 | 値: bugfix / feature / refactor / discovery / decision / change のカンマ区切り、または空文字
  // ※ これは「表示時フィルタ」であり、DB への記録には影響しない（ソースコード context-generator.cjs で確認）
  // どの値を設定しても全タイプの観測記録が DB に保存され、search で全件検索できる
  // 空文字にすると Context Index にタイプ条件で表示される記録がゼロになる
  "CLAUDE_MEM_CONTEXT_OBSERVATION_TYPES": "",

  // 観測記録に付与されるコンセプトタグのフィルタ
  // デフォルト: 全種類 | 値: how-it-works / why-it-exists / what-changed / problem-solution / gotcha / pattern / trade-off のカンマ区切り、または空文字
  // ※ OBSERVATION_TYPES と同様「表示時フィルタ」。DB には全コンセプトの記録が残り、search で取得可能
  // 空文字にすると Context Index にコンセプト条件で表示される記録がゼロになる
  "CLAUDE_MEM_CONTEXT_OBSERVATION_CONCEPTS": "",

  // 直前セッションの要約を Context Index に含めるか
  // デフォルト: "true" | 値: "true" / "false"
  // true にすると前回セッションの要約が自動注入されるが、その分トークンを消費する
  "CLAUDE_MEM_CONTEXT_SHOW_LAST_SUMMARY": "false",

  // 直前セッションの最後のメッセージを Context Index に含めるか
  // デフォルト: "true" | 値: "true" / "false"
  // true にすると前回の最終メッセージが自動注入されるが、その分トークンを消費する
  "CLAUDE_MEM_CONTEXT_SHOW_LAST_MESSAGE": "false",

  // フォルダごとの CLAUDE.md 自動注入を有効にするか
  // デフォルト: "true" | 値: "true" / "false"
  // true にすると claude-mem がフォルダ単位で CLAUDE.md を生成・注入するが、Claude Code 本体の CLAUDE.md と重複する
  "CLAUDE_MEM_FOLDER_CLAUDEMD_ENABLED": "false",

  // --- トークン消費の可視化設定 ---
  // デフォルト: 全て "false" | 値: "true" / "false"
  // 全て true にすると、各設定変更がどれだけトークン消費に影響するかを数値で確認できる
  // チューニングが完了したら false にして表示自体のノイズも減らせる
  "CLAUDE_MEM_CONTEXT_SHOW_READ_TOKENS": "false",    // 読み込んだトークン数を表示する
  "CLAUDE_MEM_CONTEXT_SHOW_WORK_TOKENS": "false",    // 作業に使ったトークン数を表示する
  "CLAUDE_MEM_CONTEXT_SHOW_SAVINGS_AMOUNT": "false",  // 節約できたトークン数を表示する
  "CLAUDE_MEM_CONTEXT_SHOW_SAVINGS_PERCENT": "false"  // 節約率（パーセント表示）を表示する
}
```

---

## この設定にした理由

### 事前注入をほぼゼロにする

#### CONTEXT\_OBSERVATIONS=1、CONTEXT\_FULL\_COUNT=0、CONTEXT\_SESSION\_COUNT=1

claude-mem の真価は `search` → `get_observations` による都度取得にあります。セッション開始時に大量のインデックスや全文を注入しても、そのセッションで実際に使うのはごく一部です。使わない情報に毎回トークンを払い続けるのは無駄なので、事前注入はほぼゼロにしました。

* `CONTEXT_OBSERVATIONS=1`: インデックスに載せるのは直近 1 件のみ。過去の記録が必要になったら `search` で検索する
* `CONTEXT_FULL_COUNT=0`: 全文展開ゼロ。全ての詳細は `get_observations` で都度取得する
* `CONTEXT_SESSION_COUNT=1`: 直近 1 セッションの文脈だけ保持。古いセッションの情報は `search` で引ける

デフォルト設定（OBSERVATIONS=50、SESSION\_COUNT=10）と比較すると、セッション開始時のトークン消費を大幅に削減できます。それでいて、`search` と `get_observations` が使える限り、過去の情報へのアクセスは一切失われません。

### 記録のノイズを減らす

#### SKIP\_TOOLS=Read,Glob,Grep ほか 5 ツール

`Read`、`Glob`、`Grep` の 3 つは 1 セッションで数十〜数百回発火するルーティン操作です。これらが全件記録されると、観測記録がノイズだらけになり、本質的な変更（`Edit`、`Write`、`Bash` など）の記録が埋もれてしまいます。この設定を入れた結果、観測記録のノイズが目に見えて減少し、`search` で検索したときの精度も向上しました。

### 表示フィルタを空にする

#### OBSERVATION\_TYPES=""、OBSERVATION\_CONCEPTS=""

ソースコード（`context-generator.cjs`）を AI に確認させたところ、これらの設定は **表示時フィルタ** であり、DB への記録には一切影響しないことがわかりました。どの値を設定しても、全タイプ・全コンセプトの観測記録が DB に保存されます。`search` で全件検索できるため、Context Index に自動表示する必要がありません。

事前注入をほぼゼロにする方針と合わせて、両方とも空文字にしています。必要な記録は `search` → `get_observations` で都度引けば十分です。

### 不要な自動注入を無効化する

#### SHOW\_LAST\_SUMMARY=false、SHOW\_LAST\_MESSAGE=false

直前セッションの要約と最終メッセージの自動注入を無効化しています。これらは前回の作業をすぐに再開したい場合に便利ですが、別の作業を始めるセッションでは不要なトークン消費になります。前回の文脈が必要な場合は `search` で明示的に引く方が効率的です。

#### FOLDER\_CLAUDEMD\_ENABLED=false

claude-mem がフォルダ単位で CLAUDE.md を生成・注入する機能を無効化しています。Claude Code 本体が CLAUDE.md を読み込む仕組みを持っているため、claude-mem 側でも注入すると内容が重複し、トークンの無駄になります。

### モデルとフィールドの選択

#### CONTEXT\_FULL\_FIELD=narrative（デフォルトのまま）

Claude がコンテクストを読み取って次のアクションを判断する際、narrative の方が文章として読みやすいため採用しています。もう一方の `facts`（事実を箇条書きの JSON 配列で列挙）はコンパクトですが前後の文脈が失われます。情報の詳細度合いについては妥協したくなかったのでこのままにしました。

#### CLAUDE\_MEM\_MODEL=sonnet

メモリ処理は要約や分類が中心なので、最上位モデルを使う必要はなく、sonnet クラスで十分な品質が得られます。デフォルトがこれなので問題ないという判断です。

### トークン消費の可視化

#### SHOW\_\*=全 false

筆者自身はこの可視化機能を使っていませんが、claude-mem には `SHOW_*` 系の設定を `true` にすることで、各設定変更がどれだけトークン消費に影響するかを数値で確認できる機能があります。設定のチューニング中はこれらを全て `true` にしておくと、どの項目がどれだけトークンを消費しているかが一目でわかるため、効率的にチューニングを進められます。チューニングが完了したら全て `false` に戻すことで、可視化表示自体のノイズも排除できます。

---

## おわりに

本記事では **「事前の自動注入を極限まで絞り、必要な情報は都度取得する」** という方針で、実際に運用している claude-mem の設定を共有しました。

これにより `search` と `get_observations` で都度好きなコンテクストに遡れるようにしました。それでいて DB には全記録が残るため、自動注入を最小化しても情報は一切失われません。とても快適です！
