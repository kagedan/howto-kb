---
id: "2026-07-07-mcp-appsホストを自作する-sdk同梱appbridgeでチャット内uiを動かすまで-01"
title: "MCP Appsホストを自作する: SDK同梱AppBridgeでチャット内UIを動かすまで"
url: "https://zenn.dev/lnest_knowledge/articles/mcp-apps-verification"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "OpenAI", "TypeScript", "zenn"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回、Slackbot MCP Clientを検証したとき、公式サンプルの `rich-responses/mcp-apps` でMCP Appsという拡張に出会いました。そのときはMCP serverの単体テストまでで、UIの表示確認は宿題として残していました。

<https://zenn.dev/lnest_knowledge/articles/slackbot-mcp-client-retry-no-auth>

Slackbotからの表示確認に行く前に、まずMCP Appsそのものを理解しておきたい。ということで、公式のビルドガイドに沿って手元で動かしてみました。チャットの返答にインタラクティブなUIが埋め込まれるやつです。OpenAIのApps SDKが出たときに話題になった、あの方向のMCP公式版です。

<https://modelcontextprotocol.io/extensions/apps>

作業はいつも通りClaude Codeに任せています。この「Claude Codeに任せた」が後で効いてきます。検証の途中で、公式のテストホストをインストールしようとしたClaude Code自身が、自分の権限判定に止められました。

この記事で書くこと:

* MCP Appsの仕組みと、公式ガイド通りのサーバー実装
* curlでプロトコルの中身を覗いた結果
* SDK同梱のAppBridgeでホストを自作して、埋め込みUIを end-to-end で動かすまで
* 実用寄りの追加例として、サイコロとVOICEVOX音声合成アプリを同じホストに並べるまで

検証は2026年7月7日時点、`@modelcontextprotocol/ext-apps` 1.7.4です。仕様はまだdraftなので、読む時期によっては変わっているかもしれません。

## 先に結果

* 公式ビルドガイドのget-timeサンプルは、ほぼコピペで動いた
* 動作確認用の公式テストホスト(basic-host)は、Claude Codeの自動権限判定に止められて使わなかった
* 代わりにSDK同梱のAppBridgeでホストを自作した。70行くらい
* 結果的に、ホストを自作したほうがプロトコルの理解は早かった
* 調子に乗ってサイコロとVOICEVOX音声合成も足し、3つのViewを1つの自作ホストに並べた
* 公式チュートリアルのサーバーコードには、並行リクエストで落ちる罠があった(後述)

最終的に動いた画面がこれです。黒い枠が自作ホストのログ、点線枠の中はぜんぶMCPサーバーから配信されたUIで、サンドボックスiframeとして埋め込まれています。

![自作ミニホストに3つのMCP Appが並んだ画面。時刻表示、サイコロ、VOICEVOX音声合成](https://static.zenn.studio/user-upload/deployed-images/591b1455b6672033c439c401.png?sha=a27b99b95380c4e97842205c635bb40fc9ffb738)  
*上から時刻表示、サイコロ、VOICEVOX音声合成。ログ最終行の巨大なbase64は音声データ(全253,434文字)*

## MCP Appsの仕組み

MCPのツールは普通、テキストや画像を返して終わりです。MCP Appsはそこを拡張して、ツールにHTMLのUIを紐付けられるようにします。使うのは既存のプリミティブ2つの組み合わせで、新しい概念はほぼありません。

* ツール定義の `_meta.ui.resourceUri` に `ui://` スキームのURIを書く
* そのURIのリソースとしてHTMLを配信する(MIMEタイプは `text/html;profile=mcp-app`)

ホスト(Claudeなど)はツールを呼ぶとき、紐付いたHTMLを取得してサンドボックスiframeでレンダリングします。iframe内のUIとホストはpostMessage上のJSON-RPCで会話します。`ui/initialize` のようなUI専用メソッドを持つ、MCPの方言という位置づけだそうです。

UIからサーバーのツールを直接叩けるわけではなく、必ずホストを経由します。ホストが「このアプリにどのツールを許すか」を握る設計です。iframeは `allow-same-origin` なしのsandboxなので、親ページのDOMもcookieも触れません。

対応ホストは執筆時点でClaude(web)、Claude Desktop、VS CodeのCopilot、Goose、Postmanなどとされています。Claude Codeは入っていません。

## 検証環境

* macOS (Apple Silicon)
* Node.js 25.5.0
* @modelcontextprotocol/ext-apps 1.7.4
* @modelcontextprotocol/sdk 1.29.0

## サーバーを書く

公式ビルドガイドのget-timeサンプルをそのまま使いました。サーバーの仕事は2つだけです。ツールを `_meta.ui.resourceUri` 付きで登録することと、そのURIでバンドル済みHTMLを返すことです。

<https://modelcontextprotocol.io/extensions/apps/build>

server.ts(抜粋)

```
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  registerAppTool,
  registerAppResource,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";

const server = new McpServer({ name: "My MCP App Server", version: "1.0.0" });

// ui:// スキームがホストに「MCP AppのUIリソースだ」と伝える
const resourceUri = "ui://get-time/mcp-app.html";

registerAppTool(
  server,
  "get-time",
  {
    title: "Get Time",
    description: "Returns the current server time.",
    inputSchema: {},
    _meta: { ui: { resourceUri } },  // ここがMCP Appsの肝
  },
  async () => ({
    content: [{ type: "text", text: new Date().toISOString() }],
  }),
);

registerAppResource(
  server,
  resourceUri,
  resourceUri,
  { mimeType: RESOURCE_MIME_TYPE },  // text/html;profile=mcp-app
  async () => {
    const html = await fs.readFile(
      path.join(import.meta.dirname, "dist", "mcp-app.html"),
      "utf-8",
    );
    return {
      contents: [{ uri: resourceUri, mimeType: RESOURCE_MIME_TYPE, text: html }],
    };
  },
);
```

UI側はHTMLと数行のTypeScriptです。`App` クラスがpostMessageまわりを全部隠してくれます。

src/mcp-app.ts

```
import { App } from "@modelcontextprotocol/ext-apps";

const app = new App({ name: "Get Time App", version: "1.0.0" });
app.connect();

// ホストがツール結果をプッシュしてきたら表示を更新
app.ontoolresult = (result) => {
  const time = result.content?.find((c) => c.type === "text")?.text;
  serverTimeEl.textContent = time ?? "[ERROR]";
};

// ボタンからUI側が能動的にツールを呼ぶ(ホスト経由でプロキシされる)
getTimeBtn.addEventListener("click", async () => {
  const result = await app.callServerTool({ name: "get-time", arguments: {} });
  // ...表示更新
});
```

ビルドは `vite-plugin-singlefile` でJSをHTMLに埋め込む構成が推奨されています。MCP Appsのiframeはdeny-by-defaultのCSPで動くため、外部ファイルの読み込みには追加設定が要るからだそうです。単一ファイルにすれば考えることが減ります。

代償として、時刻を表示するだけのUIが約322KBになりました。SDKごとバンドルされるのでこうなります。ネットワーク越しの配信ではなくMCPのリソース応答として渡るものなので実害は薄いですが、初見だと少し笑います。

## curlで中身を見る

ホストなしでも、プロトコルレベルの動きはcurlで確認できます。まず `tools/list`。

```
curl -s -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

応答のツール定義に `_meta` が付いています。

```
{
  "name": "get-time",
  "_meta": {
    "ui": { "resourceUri": "ui://get-time/mcp-app.html" },
    "ui/resourceUri": "ui://get-time/mcp-app.html"
  }
}
```

新形式の `ui.resourceUri` と旧形式の `ui/resourceUri` が両方入っていました。SDKが後方互換のために二重に書き込んでいるようです。draft仕様が動いている最中という感じがします。

`resources/read` で `ui://get-time/mcp-app.html` を読むと、MIMEタイプ `text/html;profile=mcp-app` でHTML全文が返ってきます。ここまでは普通のMCPリソースと同じ動きです。

## 表示確認用のホストを探す

MCP Appsの見た目を確認するには、MCP Apps対応のホストが必要です。公式ドキュメントは2つの方法を案内しています。

1. Claude(web/Desktop)にカスタムコネクタとして繋ぐ。ローカルサーバーはcloudflaredなどでトンネルする
2. ext-appsリポジトリ同梱のテスト用ホスト basic-host を使う

手軽なのは2です。リポジトリをcloneして `examples/basic-host` で `npm install` するだけ。のはずでした。

ここでClaude Codeが止まりました。正確には、検証を任せていたClaude Codeの `npm install` 実行が、Claude Code自身の権限判定(auto modeのclassifier)に拒否されました。

> Permission for this action was denied by the Claude Code auto mode classifier. Reason: [Untrusted Code Integration] Running `npm install` in the externally cloned ext-apps repo executes lifecycle scripts from code outside the trusted source-control org without explicit user direction.

外部からcloneしたリポジトリで `npm install` すると、lifecycle scriptとして任意コードが走る。ユーザーの明示的な指示なしにはやらない、という理屈です。ext-appsはMCP公式orgのリポジトリなので過剰検知ではあるんですが、npmのサプライチェーン攻撃はだいたいこの経路なので、方針としては悪くないと思います。止まった本人(?)が言うのも変な話ですが。

人間が手で `npm install` すれば済む話ではあります。ただ、拒否メッセージの提案に従って別の道を探したら、そっちのほうが面白かったのでそのまま進めました。

## AppBridgeでホストを自作する

`@modelcontextprotocol/ext-apps` パッケージには、UI側の `App` クラスだけでなく、ホスト側の実装である `app-bridge` モジュールが同梱されています。basic-hostも中身はこれです。つまり、すでにインストール済みの信頼できるパッケージだけで、ホストが書けます。

やることは5つです。

src/mini-host.ts

```
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { CallToolResultSchema } from "@modelcontextprotocol/sdk/types.js";
import {
  AppBridge,
  getToolUiResourceUri,
  PostMessageTransport,
} from "@modelcontextprotocol/ext-apps/app-bridge";

async function main() {
  // 1. MCPサーバーに接続
  const client = new Client({ name: "MiniHost", version: "1.0.0" });
  await client.connect(
    new StreamableHTTPClientTransport(new URL("http://localhost:3001/mcp")),
  );

  // 2. tools/list からUIリソースのURIを発見
  const { tools } = await client.listTools();
  const resourceUri = getToolUiResourceUri(tools[0]);
  if (!resourceUri) throw new Error("UIリソースが宣言されていない");

  // 3. resources/read でHTMLを取得
  const resource = await client.readResource({ uri: resourceUri });
  const html = (resource.contents[0] as { text: string }).text;

  // 4. サンドボックスiframeにレンダリング
  iframe.srcdoc = html;
  await new Promise((resolve) => (iframe.onload = resolve));

  // 5. AppBridgeでViewと接続(clientを渡すとツールコールを自動プロキシ)
  const bridge = new AppBridge(
    client,
    { name: "MiniHost", version: "1.0.0" },
    { serverTools: {}, logging: {} },
  );

  bridge.oninitialized = async () => {
    // ハンドシェイク完了後、ツールを実行して結果をViewにプッシュ
    await bridge.sendToolInput({ arguments: {} });
    const result = await client.request(
      { method: "tools/call", params: { name: "get-time", arguments: {} } },
      CallToolResultSchema,
    );
    await bridge.sendToolResult(result);
  };

  await bridge.connect(
    new PostMessageTransport(iframe.contentWindow!, iframe.contentWindow!),
  );
}
```

`AppBridge` のコンストラクタにMCPクライアントを渡すところがポイントです。これだけで、iframe内のUIが投げてくる `tools/call` を実サーバーに転送する処理を全部やってくれます。Claudeのような実ホストは、この転送の間に「ユーザーの同意を取る」「許可リストを確認する」といった制御を挟んでいるはずです。前回のSlackbot検証で見た、tool call前の許可カードもこの位置の話です。

HTMLはiframeとログ表示だけなので省略します。

## 動いた画面

まずget-time単体で動かした画面がこれです。

![自作ミニホストでget-timeのMCP Appを動かした画面](https://static.zenn.studio/user-upload/deployed-images/536fc5771569c569b3153660.png?sha=96ff05c1f2212b7e88a4614907ec0103dbe9afbe)

* `ui/initialize` のハンドシェイクが通る(ログ6行目)
* ホストからViewへのツール結果プッシュが `ontoolresult` で受かる(Server Timeの行)
* Viewから `callServerTool` で呼び直すと、ホスト経由でサーバーの `tools/call` が実行される(Auto callの行)

Server Timeが `08:37:39.934Z`、Auto callが `08:37:39.937Z` で3msずれています。同じ値の使い回しではなく、独立した2回のツールコールが往復した証拠です。

## 実用例を足す: サイコロとVOICEVOX

時刻表示だけだと寂しいので、アプリを2つ足しました。ミニホスト側は「UI付きツール全部にiframeを並べる」よう少し改修しています。tools/listの結果から `_meta` にUIリソースを持つツールを絞り込み、ツールごとにiframeとAppBridgeのペアを作るだけです(MCPクライアントは全ブリッジで共有できます)。

### サイコロ: structuredContentの使い分け

前回のSlackbot検証と同じ題材のサイコロです。ポイントは返り値の二重化で、これは公式サンプル群でも定石のパターンでした。

server.ts(roll-diceの返り値)

```
return {
  content: [
    { type: "text", text: `${rolls.join(", ")} (${count}d${sides}, total ${total})` },
  ],
  structuredContent: { rolls, count, sides, total },
};
```

モデルには読みやすいテキストを、UIには型の付いた構造化データを渡します。ツール定義に `outputSchema` を宣言しておくと、SDKが `structuredContent` をスキーマ検証してくれます。View側は `result.structuredContent` から出目の配列を受け取って描画するので、テキストのパースが要りません。

### VOICEVOX: 音声を返す実用アプリ

もう1つは、ローカルのVOICEVOX Engineを叩く音声合成アプリです。テキストと話者を選んで合成ボタンを押すと、iframe内の `<audio>` で再生できます。

![VOICEVOX音声合成アプリのView。テキスト入力、話者選択、audioプレイヤー](https://static.zenn.studio/user-upload/deployed-images/cc1609017ce9977bbffe55a9.png?sha=f1694536ce5a0ff4a9999ff3e3a6b51c1d4ce535)  
*話者selectには本物のVOICEVOX Engineから取った113スタイルが入っている*

構成で面白かったのは2点です。

1つ目は音声のcontent type。MCPのツール返り値には text や image のほかに audio があり、WAVをbase64で詰めて返せます。View側はそれを `data:audio/wav;base64,...` のURLにして `<audio>` に渡すだけです。1回の `tools/call` 応答が25万文字を超えますが、普通に動きます。

server.ts(speak-voicevoxの返り値)

```
return {
  content: [
    { type: "audio", data: wavBase64, mimeType: "audio/wav" },
    { type: "text", text: `合成完了 (speaker ${speaker}, ${seconds}秒, ${sizeKB}KB)` },
  ],
  structuredContent: { speaker, textLength: text.length },
};
```

2つ目はUIなしツールとの組み合わせ。話者一覧を返す `list-voicevox-speakers` は `_meta.ui` を付けずに登録してあり、iframeは作られません。VOICEVOXのViewが初期化時に `callServerTool` でこれを呼び、selectの選択肢を埋めます。「UIから使うためだけの裏方ツール」という構成が素直に書けました。

## ハマったポイント

### sandboxのiframeには親からも触れない

Puppeteerでiframe内のボタンをクリックして自動テストしようとしたら、届きませんでした。`allow-same-origin` を付けないsandbox iframeはクロスオリジン扱いになるので、親ページからも `contentDocument` にアクセスできません。

セキュリティモデルがそのまま機能しているだけなので、文句を言う筋合いはないです。自動テストしたければ、View側の初期化フローに検証用の処理を入れるか、postMessageのプロトコルを喋るしかありません。今回はViewの `ontoolresult` 内から `callServerTool` を自動発行する形にしました。

`sendToolResult` の前に `sendToolInput` を一度送る必要があります。SDKのドキュメントコメントに required と書いてあるのを見落として、最初は結果だけ送ろうとしていました。ツール結果より先に「どんな引数で呼ばれたか」をUIに知らせる設計です。ストリーミングで引数を少しずつ流す使い方も想定されているようです。

### 公式チュートリアルのサーバーは並行リクエストで落ちる

公式ビルドガイドのExpressサーバー例に潜んでいた罠です。ガイドの例は、モジュールトップで作った単一の `McpServer` インスタンスにPOSTごとに `server.connect(transport)` する構造になっています。1リクエストずつなら動きますが、`tools/call` が並行すると2本目が `500: Already connected to a transport` で落ちます。

うちではVOICEVOXの合成(1秒くらいかかる)の最中に、Viewからの話者一覧の呼び出しが重なって発覚しました。SDKドキュメントにあるstatelessパターン、つまりリクエストごとにサーバーインスタンスを生成する形に変えて解消しています。

server.ts(修正後)

```
// ツール登録込みのファクトリにして、リクエストごとに生成する
expressApp.post("/mcp", async (req, res) => {
  const server = createServer();
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });
  res.on("close", () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});
```

get-time 1個の間は絶対に踏みません。チュートリアル通りに書いて満足した人ほど、Viewやツールを増やした時に踏む種類のバグです。

### 巨大なbase64をログに素通ししない

音声のbase64(25万文字)を `JSON.stringify` でそのままホストのログに出したら、改行のない1行がレイアウト幅を160万px超まで押し広げてページを壊しました。ログは先頭200文字で切り詰め、CSSに `word-break: break-all` を足して回避しています。音声や画像を扱うMCP Appでは、content の中身をそのまま画面やログに流さない前提で組んだほうがいいです。

### viteのビルドが消し合う

UI(mcp-app.html)とミニホスト(mini-host.html)を同じviteプロジェクトで別々にビルドしたら、2回目のビルドが1回目の成果物を消しました。viteはデフォルトで `dist` を空にしてからビルドします。

```
# 2枚目以降は --emptyOutDir=false を付ける
npm run build -- --emptyOutDir=false
```

## Claudeの実機で試す場合

今回はここまでで、Claude実機での表示は試していません。やる場合はローカルサーバーをトンネルで公開して、カスタムコネクタとして登録する流れになります。

```
npx cloudflared tunnel --url http://localhost:3001
```

生成されたURLに `/mcp` を付けて、claude.aiのSettings、Connectors、Add custom connectorから登録します。カスタムコネクタはPro/Max/Teamプランで使えるとされています。

## まとめ

* MCP Appsは「ツール + UIリソース」という既存プリミティブの組み合わせで、プロトコルとしては素直だった
* サーバー側は公式ガイドのコピペで動く。UIが322KBになるのはご愛嬌
* ホスト側もAppBridgeを使えば70行程度。対応クライアントを増やす障壁は低そう
* audio contentで音声もそのまま返せる。VOICEVOX合成アプリまでは半日で組めた
* ただし公式チュートリアルのサーバー例は並行リクエストに弱い。Viewを増やすならstatelessパターンにしておく

ホスト側を一度自分で書いたことで、SlackbotやClaudeがMCP Appsを表示するとき裏で何をしているのか、だいぶ想像しやすくなりました。前回からの宿題だった「Slackbotから `rich-responses/mcp-apps` のUIがどう見えるか」と、今回のVOICEVOXアプリをClaude実機に繋ぐのは、次の検証で確認します。

## 参考リンク
