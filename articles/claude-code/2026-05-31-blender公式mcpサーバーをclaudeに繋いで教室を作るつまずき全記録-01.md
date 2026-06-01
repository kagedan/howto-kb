---
id: "2026-05-31-blender公式mcpサーバーをclaudeに繋いで教室を作るつまずき全記録-01"
title: "Blender公式MCPサーバーをClaudeに繋いで教室を作る（つまずき全記録）"
url: "https://zenn.dev/shintama/articles/blender-official-mcp-claude"
source: "zenn"
category: "claude-code"
tags: ["MCP", "LLM", "zenn"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

## はじめに

Blender に公式の MCP サーバーが出た。これを使えば Claude から自然言語で Blender を操作できるはずだ。試してみたかった ── 結論から言うと、動いた。Claude に「日本の教室を作って」と頼んだら、黒板も教卓も生徒机もある、それらしいシーンが出来上がった。

![完成した日本の教室のシーン（冒頭・完成形）](https://static.zenn.studio/user-upload/deployed-images/3cb8918c1394a64835f97b45.png?sha=aaabe62f08c61acf2f5a261db4c7d7272d91ac40)

ただし、公式の手順どおりにアドオンを入れようとして3か所で詰まった。同じところで止まる人は少なくないはずなので、**つまずきと、最終的に効いた回避策をそのまま記録する**。エラーメッセージ・バージョン番号・パスは検索で来た人がそのまま照合できるよう、実物のまま載せる。

**対象バージョン**: Blender 5.1.2（Windows / x64）  
**検証日**: 2026年5月31日

**対象環境**

* Blender 5.1.2（Windows / x64）
  + 5.1 系は 2026-03-17 リリース、5.1.2 は 2026-05-19 のバグ修正版。執筆時点の安定版。
* 入れたもの: 公式 Blender Lab の MCP サーバー（`https://www.blender.org/lab/mcp-server/`）
  + プロジェクト: `https://projects.blender.org/lab/blender_mcp`
* 接続先 LLM: Claude（Claude アプリ側の MCP 接続）

**TL;DR（ハマりどころ早見表）**

* `The extension dropped was not found in the remote repository` → リポジトリのインデックス未取得。同期 or 再起動。直らなければ次へ。
* `remote data unavailable, sync with the remote repository` → ネット/SSL の遮断を疑う（ウイルス対策・ファイアウォール・VPN）。System Console でエラー確認。
* 結局つながらない時 → **ZIP をディスクからインストールが最短**。自動更新は諦める。
* 公式（blender.org/lab）と第三者製 `blender-mcp` は別物。

## そもそも何を入れるのか ── 部品は2つ

公式 MCP は「2つの部品が連携する」と整理すると分かりやすい。ここを最初に押さえておくと、どこで詰まっているのかの切り分けが楽になる。

* **(A) Blender アドオン（エクステンション）**: Blender の中で動き、リクエストを受けて実行する。TCP で待ち受ける（今回の設定: Host `localhost` / Port `9876`）。**これが入って動いていないと何も始まらない**。
* **(B) MCP サーバー本体（別プロセス）**: Claude などの LLM クライアントから起動され、(A) に中継する。

今回スクショで確認できた (A) のアドオン情報:

| 項目 | 値 |
| --- | --- |
| 名称 | MCP |
| 説明 | "MCP server add-on for LLM interaction." |
| メンテナー | Blender Lab |
| バージョン | 1.0.0 |
| タイプ | エクステンション |
| 設定 | Host `localhost` / Port `9876` / Auto Start オン |
| 状態 | Server is running |

この記事のつまずきは、ほぼ全部 **(A) を入れる段階** で起きた。

## つまずき① ── ドラッグ&ドロップは「2回」必要だった

公式手順では、アドオンを Blender にドラッグ&ドロップして入れる。これが実は2段階になっている。

1. **1回目**: 「Blender Lab リポジトリ（`lab.blender.org`）」を追加する
2. **2回目**: アドオン本体をインストールする

1回目は成功した（`Repository found: "lab.blender.org"`）。ところが2回目で次のメッセージが出る。

```
エクステンションをインストール
Repository found: "lab.blender.org"
The extension dropped was not found in the remote repository.
Check this is part of the repository and compatible with:
Blender version 5.1.2 on "windows-x64".
```

![つまずき①: アドオンが見つからないエラーダイアログ](https://static.zenn.studio/user-upload/deployed-images/b06fa110f76a937183c9801f.png?sha=98509dccb309e118ed91f289ee43fbaf74ce239a)

リポジトリは追加できたのに、落としたアドオンが「リポジトリの中に無い」と判定されている。

原因は、**リポジトリは登録できたが、その中身（インデックス）をまだ取得できていない** こと。「起動時に更新チェック」は文字どおり“起動時”しか同期しないので、リポジトリを追加した直後の同じセッションでは中身が空のまま。だから落としたアドオンが一覧に見つからない、と判定される。

……というのが最初に立てた仮説だった。ならば再起動すれば同期されるはず ── と思ったが、後述するように **これは再起動だけでは直らなかった**。同期そのものが失敗していたのだが、この時点ではまだ気づいていない。

## つまずき② ── 一覧に MCP が出てこない

ならばと、プリファレンス >「エクステンションを入手」で `mcp` を検索した。**ヒットなし**。

リポジトリ一覧を見ると `lab.blender.org` は追加済み・有効・URL `https://lab.blender.org/`・「起動時に更新チェック」オン、という状態。登録自体は問題なさそうに見える。

![つまずき②: リポジトリは追加済みだが検索に出てこない](https://static.zenn.studio/user-upload/deployed-images/6ff13d4eb44d7ced3ae94d1e.png?sha=1ea29253e0ccaabfd09bdcef7dedd79a65919d19)

つまずき①と同じ「中身が空」の症状だろうと考え、手動同期（リフレッシュ）と再起動を試した。

## つまずき③ ── リポジトリ同期そのものが失敗していた

再起動後、エクステンション入手画面で今度はこの警告が出た。

```
リポジトリ警告:
Repository: "lab.blender.org" remote data unavailable, sync with the remote repository.
```

![つまずき③: リモートデータが取得できないという警告](https://static.zenn.studio/user-upload/deployed-images/63429b289f12e6eb66de2bac.png?sha=18ff86f0440d2e0d5e401be980f0dedb62586539)

これは **Blender がリポジトリ一覧データをネット越しに取得できていない** 状態。落としたファイルや MCP 固有の問題ではなく、Blender 界隈では `extensions.blender.org` でも頻出する有名なエラーだ。MCP に限らず「エクステンションが同期できない」全般で出る。

よくある原因と対処を、自分が確認した範囲で整理しておく。

* **ウイルス対策ソフト / ファイアウォール / VPN が Blender の通信（SSL）を遮断している**。ブラウザでサイトが見えても、Blender の通信だけ止められていることがある（ここが盲点）。
* Windows の場合、**Microsoft Visual C++ 再頒布可能パッケージの入れ直し** で直った報告がある。
* キャッシュ破損時は、`extensions.cache` 内の `compat.dat` を退避して再起動すると解消した例がある。

切り分けの定石は、`Window > Toggle System Console` でシステムコンソールを開いた状態で「Refresh Remote」を実行し、**SSL エラーなのか接続拒否なのか** を確認すること。

ただ、正直に書くと、自分はここで原因の特定まではしなかった。目的は MCP を動かすことであって、リポジトリ同期を直すこと自体ではない。同期の不具合を深追いするより、次に書く **ZIP の直接インストール** に切り替えた方が早いと判断した。だからこの記事では「同期失敗の原因はこれだった」という結論は出していない。同じ警告で困っている人は、上の候補を当たりつつ、直らなければ回避策に進むのが現実的だと思う。

## 解決 ── ZIP を「ディスクからインストール」する

リモート同期を直すより手っ取り早い回避策がある。**アドオンの ZIP を直接インストールする** ことだ。リポジトリ経由をすっ飛ばす。

ZIP は公式 Lab ページから入手できる。

* 入手元: `https://www.blender.org/lab/mcp-server/`

手順:

1. 上記ページからアドオンの ZIP をダウンロードしておく
2. Blender のエクステンション入手画面の右上 **▼ メニュー** を開く
3. **「ディスクからインストール」** を選ぶ
4. ダウンロードした ZIP を選択

結果、アドオン「**MCP（Blender Lab / v1.0.0）**」が有効化され、`Server is running` の表示まで到達した。インストール先はここだった。

```
C:\Users\<user>\AppData\Roaming\Blender Foundation\Blender\5.1\extensions\lab_blender_org\mcp\__init__.py
```

![解決: MCPアドオン（Blender Lab / v1.0.0）が有効化され、Host localhost / Port 9876 で Server is running まで到達](https://static.zenn.studio/user-upload/deployed-images/9eafece6258174df4bd0be94.png?sha=af0d37410c54b7e94f7a1bec1fda1ff88d7b02a7)

## Claude との接続

Blender 側のアドオンが `localhost:9876` で稼働していれば（Auto Start オン）、あとは Claude 側の MCP 接続を通すだけだ。

自分は Claude アプリのコネクタ機能から繋いだ。手順はこう。

1. **設定 → コネクタ** を開く
2. **「カスタマイズ」** へ進む
3. **「コネクタを追加」（＋ボタン）** を押す
4. 検索欄に **`Ble`** と入れると、**Blender 公式のコネクタ** が出てくるので、それを追加する

接続できると、Claude から `execute_blender_code` などのツールが呼べる状態になる。

## 実際に作ってみた ── 日本の教室

接続できたので、さっそく頼んでみた。

> プランモードから始めて、Blender を操作して日本の教室を作って

結果が冒頭の画像だ。黒板・教卓・整列した生徒机・壁掛け時計・窓のある、日本の教室らしいシーンが生成された。右のアウトライナーを見ると `Desks` コレクションに多数の机オブジェクトが並んでいるのが分かる。

ただし、近づいて別角度から見ると粗が見える。**椅子は生成されているのだが、配置が崩れて机にめり込んでいる**。机と椅子それぞれは作れても、「椅子は机の下に正しく収める」という空間的な整合まではきれいに取れていない。

![別角度。椅子が机にめり込んでいる（初回生成の粗）](https://static.zenn.studio/user-upload/deployed-images/06da9f198fc2e21beb081671.png?sha=c1facc248cb46cfb68db4247d962e5455baf6e73)

正直に書くと、こうした詰まりは途中でもあった。AI によるモデリングは一発で完璧にはならず、崩れた箇所を指摘して **反復と指示の微調整** を重ねていく作業になる。それでも、ここまでそれらしいシーンが対話だけで立ち上がるのは素直に面白い。

## まとめ

公式 Blender MCP を Claude に繋ぐところまでで踏んだ罠と、効いた対処を改めて。

* **つまずき①**（`The extension dropped was not found in the remote repository`）: リポジトリは追加できてもインデックス未取得。同期 or 再起動。
* **つまずき②**（検索しても MCP が出ない）: 同じく中身が空。同期で解決を試みる。
* **つまずき③**（`remote data unavailable, sync with the remote repository`）: ネット/SSL の遮断を疑う。System Console でエラーを確認。
* **解決**: 直せない時は **ZIP をディスクからインストール** が最短。自動更新は諦める。
* 公式（blender.org/lab）と第三者製 `blender-mcp` は別物。

同じエラーで検索して来た人が、ここで止まらずに先へ進めれば書いた甲斐がある。

## 参考
