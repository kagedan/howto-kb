---
id: "2026-05-10-nextjsからqwikへ丸ごと移行してみた-個人開発webアプリのリアーキテクチャ実録-01"
title: "Next.jsからQwikへ丸ごと移行してみた - 個人開発Webアプリのリアーキテクチャ実録"
url: "https://zenn.dev/connect0459/articles/rearchitect-from-next-to-qwik"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "JavaScript", "TypeScript"]
date_published: "2026-05-10"
date_collected: "2026-05-11"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* 対象
  + Next.jsの経験がある方
  + Qwikに興味がある方
  + フレームワーク移行を検討している方
* 内容
  + Next.js App Router v15.4からQwik v1.19へ移行し、自サイトのファーストパーティJS転送サイズを2〜4割削減
  + 移行戦略とQwikのPros/Consを評価

## 背景

学生時代に所属していたコミュニティ向けに、Next.js App RouterでWebアプリを個人で開発・運用していました。しかし、デプロイアダプターの非推奨化を契機に、前々から気になっていたQwikへの移行を試してみました。

移行にあたって意識したことや、実際に移行してみて感じたNext.jsやQwikが持つそれぞれの優位性と課題をまとめます。

### Webアプリの概要

移行対象は、商品・サービスの予約購入フローを持つ小規模なWebアプリです。構成は次の通りです。

| 項目 | 値 | 備考 |
| --- | --- | --- |
| ページ数 | 11 | `/`、`/search/` など |
| ソースファイル数 | 約130 | テスト除く |
| ソースコード行数 | 約8,000 | テスト除く |
| ビジネスドメイン数 | 10 | 商品管理、カートなど |

バックエンドはPHPでHTTP APIを提供していますが、詳細は割愛します。移行期間は約6ヶ月（2025年10月〜2026年3月）で、手が空いたときに少しずつ実装を進めていました。

### なぜ移行したのか

団体を離れても上記Webアプリの運用保守には関わっており、インフラ構成にお金をかけない方針で運用していました。フロントエンドはCloudflare Pagesの無料枠、バックエンドはLaravelでRESTful APIを構築してレンタルサーバーでホストする構成です。

ところが、デプロイに使っていたNext.jsアプリをCloudflare Pages向けにビルドするアダプター [next-on-pages](https://github.com/cloudflare/next-on-pages) が非推奨になり、 [opennextjs-cloudflare](https://github.com/opennextjs/opennextjs-cloudflare) への移行が必要になりました。さらに追い打ちをかけるように、Next.js本体のマイナーバージョンを上げた際、Server Actionsが動かなくなるなどの不具合にも遭遇し、Next.jsで保守することの大変さを感じていました。

そのような経緯があり、ホスト先や技術スタックを改めて見直した際、前々から気になっていたQwikへの移行を試してみることにしました。QwikはResumabilityをコアコンセプトとするJSフレームワークで、「ページを開いた瞬間にJavaScriptがほぼゼロ」であることを掲げています。

<https://qwik.dev/>

QwikはCloudflare Pages向けのデプロイアダプターが整備されており、設定周りの変更は軽微で済みそうだと感じました。Resumabilityによるパフォーマンス優位性に以前から興味があり、小規模なアプリでの移行は良い実験の機会でもありました。

## アーキテクチャの差異 - HydrationとResumability

移行の話をする前に、Qwikが優れているとされる点を整理します。

### Next.js App RouterにおけるHydration

Next.js App Routerでは、Server Componentsで生成されたHTMLに加えて、Client Componentsに対して **Hydration** が発生します。サーバーが生成したHTMLをもとに、クライアントサイドでClient ComponentsのJavaScriptを実行してStateを再構築し、イベントリスナーを登録します。

React 18以降では、Suspense境界単位で処理されるSelective Hydrationにより、Client Componentsは優先度に応じて段階的にHydrationされます。それでも、Hydrationのコスト自体はなくなりません。

```
サーバーサイド
　　　＿人人人人人人人人人＿
　　　＞　THE WORLD！！　＜
　　　＞　時よ止まれ！！　 ＜
　　　￣Y^Y^Y^Y^Y^Y^Y^Y^￣
　　　　　　　　||
　　┌───────────────────┐
　　│ State: {count: 5} │
　　└───────────────────┘
　　　　　　　　|| HTML送信
　　　　　　　　\/

クライアントサイド
　　　＿人人人人人人人人人＿
　　　＞　時は動き出す！　＜
　　　￣^Y^Y^Y^Y^Y^Y^Y^￣
　　　　　　　　|| 必要なJSチャンクをダウンロード
　　　　　　　　|| 全コンポーネントを再実行
　　　　　　　　\/
　　　　　(ﾟдﾟ)ｳﾞｫｫｫ
　　　「仮想DOMを再構築...」
　　　「Stateを再計算...」
　　　「イベントリスナーを登録...」

　　┌───────────────────┐
　　│ State: {count: 5} │ ← もう一度作り直し
　　└───────────────────┘
```

サーバーで計算した状態をクライアントサイドでもう一度計算し直す処理が発生します。

### QwikのResumabilityの哲学

一方、Qwikの **Resumability** は全く異なるアプローチを取ります。サーバーで計算された状態はJSON形式でHTMLに焼き付けられます。インタラクションが発生すると、 `qwik/json` の内容が解釈され、状態がメモリに復元されます。その後、QRLと呼ばれる遅延参照を解決してJSチャンクをオンデマンドに読み込みます。

<https://qwik.dev/docs/advanced/qrl/>

```
サーバーサイド
　　　＿人人人人人人人人人＿
　　　＞　THE WORLD！！　＜
　　　＞　時よ止まれ！！　 ＜
　　　￣Y^Y^Y^Y^Y^Y^Y^Y^￣
　　　　　　　　||
　　┌───────────────────────────┐
　　│ State: {count: 5}         │
　　│ ↓ シリアライズ              │
　　│ <script type="qwik/json"> │
　　│ {"count": 5}              │
　　│ </script>                 │
　　└───────────────────────────┘
　　　　　　　　|| HTML送信
　　　　　　　　\/

クライアントサイド
　　　　  　　 ∧_∧
　　　　　　 (　･ω･)
　　「まだまだ止めていられるぞ...」
　　　　　　　　|| カウントボタンをクリック
　　　　　　　　\/
　　　＿人人人人人人人人人＿
　　　＞　時は動き出す！　＜
　　　￣^Y^Y^Y^Y^Y^Y^Y^￣
　　　　　　　　|| qwik/jsonをパース
  　┌───────────────────┐
  　│ State: {count: 5} │ ← メモリに復元
  　└───────────────────┘
　　　　　　　　|| QRLを解決してチャンク読み込み
　　　　　　　　\/
  　　　　　　(ﾟдﾟ)ｷﾀｰ
  　　「必要なコードだけ起動！」
  　　「count.value++を実行」
```

重要なのは、 **「クライアントサイドで状態を再計算する必要がない」** という点です。これが実際のパフォーマンスにどう影響するのかは、移行結果のセクションで詳しく見ていきましょう。

## 移行戦略

QwikにはReactコンポーネントをそのまま動かす [Qwik React](https://qwik.dev/docs/integrations/react/) というブリッジが存在しますが、今回は使用せず、すべてのコンポーネントをQwikネイティブな記法に書き換えました。ブリッジを使う選択肢もあるなかで全書き換えにした理由は、Resumabilityのメリットを最大限に活かしたかったからです。

<https://qwik.dev/docs/integrations/react/>

まずはReact/Next.jsに依存する箇所とピュアなTypeScriptのロジックを分離し、移行に伴うコーディングコストを最小化することから始めました。

### フレームワーク依存の機能を局所化

メタフレームワークはHTTPリクエストやCookieアクセスなどを、フレームワーク固有の方法で提供しています。そのため、移行の前後で書き方に違いが出ることがあります。

このアプリはSSRが主体であるため、サーバーサイドフェッチを前提として話しますが、 `fetch()` APIはNext.jsとQwikで利用方法が異なります。Next.jsが `cache` 、 `next` オプションを追加して独自に拡張していることは、Next.jsを使ったことのある方にはおなじみかと思います。他方でQwikでは、ルーティング・SSR層を担うQwik Cityが `routeLoader$` などの関数を提供しており、キャッシュ制御はその関数のコンテキストで行う方式です。

<https://qwik.dev/docs/qwikcity/>

このようなフレームワーク間の差がどこに集中しているかを確認するため、各フレームワーク固有の実装を整理しました。

fetch APIに関しては幸いなことに、Next.jsの時点で `ApiClient` のようなHTTP Requesterを切り出してバックエンドAPIと通信させる設計にしていました。フレームワーク固有の設定は `request()` 内で `fetch()` に渡す `RequestInit` を組み立てる箇所に集中していたため、変更はその箇所に絞るだけで済みました。

```
// 移行前後でAPIの使い方（getメソッドなど）はほぼ共通
class ApiClient {
  private async request<T>(
    method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
    path: string,
    config?: RequestConfig, // 独自定義のconfig型
    body?: unknown,
  ): Promise<T> {
    const headers = this.getHeaders(config);
    const endpoint = this.buildEndpoint(path, config);

    // 移行前（Next.js版）: next オプションでISRキャッシュを設定
    // const requestInit: RequestInit = {
    //   method,
    //   headers,
    //   cache: config?.cache,
    //   next: config?.next, // Next.js固有: ISRキャッシュ・再検証設定
    //   body: body ? JSON.stringify(body) : undefined,
    // };

    // 移行後（Qwik版）: next オプションを除去するだけ
    const requestInit: RequestInit = {
      method,
      headers,
      cache: config?.cache,
      body: body ? JSON.stringify(body) : undefined,
    };

    const response = await fetch(endpoint, requestInit);
    if (!response.ok) throw new ApiError(response.status, response.statusText);
    return response.json();
  }

  public async get<T>(path: string, config?: RequestConfig): Promise<T> {
    return this.request<T>("GET", path, config);
  }
  // ...
}
```

fetch APIと同様に、Cookie処理に関してもフレームワーク間でアクセス方法が異なります。Next.jsでは `cookies()` で関数ベースのアクセスが可能ですが、Qwik Cityでは `routeLoader$` など、各関数の `requestEvent` パラメータから `.cookie` を取り出す設計になっています。

`ApiClient` のようにフレームワーク横断のラッパーで吸収できるケースもありました。ただし、Cookieへのアクセスはフレームワーク固有のコンテキストへの結合度が高いため、Qwik版ではラッパーを設けずに各コンテキスト内で直接アクセスする形にしました。

```
// 移行前（Next.js版）: cookies()で関数ベースのアクセス
const cookieStore = await cookies();
const cartValue = cookieStore.get("cart")?.value;

// 移行後（Qwik版）: requestEvent.cookieからアクセス
const cartValue = requestEvent.cookie.get("cart")?.value;
```

### テスト環境の整備

エンタープライズで運用されているような大規模サイトではなかったので、基本は整備済みのUnitテストで動作を担保していました。ただし、状態管理や実際のユーザーフローを網羅するE2Eテストは整っていなかったため、手動確認がメインでした。

ただ、手動で確認するのも手間がかかるので、この際自動で検査できる箇所はテストを整備して楽をしたいと思っていました。そうして移行作業を進める中で、Playwright Test Agentsが登場しました。

<https://playwright.dev/docs/test-agents>

Playwright Test Agentsは自然言語の指示からE2Eテストを自律生成・実行する機能で、複数のAIエージェントが分業してテスト計画から実装・修正までを自動で回してくれます。

これが登場したとき、「これを使えば比較的楽にE2Eテストを導入できそうだ」と思い、実験を兼ねて導入することにしました。カート追加・購入手続きなど主要フローの正常系・準正常系・異常系について、まずNext.js版をベースラインとしてE2Eテストを整備しました。同じテストスイートをQwik版にも適用することで、移行後のリグレッションをほぼ手動確認なしで検知できる状態にしました。

### ClaudeにQwikを「教える」

普段の開発ではClaude Codeを使っており、Qwik固有の知識・制約を事前に与えて活用すれば、未知のフレームワークでも学習コストを抑えて移行できると考え実施しました。ただ、Qwikは広く使われているフレームワークではないので、Claude Codeに聞くだけでは以下のようなハルシネーションが発生することがありました。

```
<!-- 例1: ResumabilityをHydrationと混同した診断ミス -->
(claude) < 初期表示が遅いのはHydrationによるものと考えられます。
(me) < Resumabilityの設計により、Hydrationはほぼ起きないはずでは？
(me) < サーバーサイドの非同期フェッチがレンダリングをブロックしているのが根本原因なので、 `<Resource />` を使ってStreaming UIを表示しましょう。

<!-- 例2: computed signalのシリアライズ制約の理解不足 -->
(claude) < カート数量が更新されない現象を修正しました。 `useResource$` 内で `currentCart` を追跡しています。
(me) < `Serializing dirty task`という警告が出ています。
(me) < Qwikは派生値であるcomputed signalの依存をシリアライズできない場合があるので、元のbase signalである `cart` を直接追跡するように修正してください。
```

そこで、プロジェクト配下の `CLAUDE.md` に以下の指示を追加しました。

* Qwikの公式ドキュメントを参照して実装する
* 不明な点は `QwikDev/qwik` リポジトリのコードを検索する
* ReactのコードをQwikの正しい記法に直す

さらに、移行中に実際に踏んだバグから以下のような制約を `CLAUDE.md` に追記しました。

CLAUDE.mdに書いた実装Tipsの簡略例

## 実装Tips

### computed signalではなくbase signalを追跡する

`useResource$` や `useTask$` 内の `track()` には、computed signalではなく、元となるbase signalを直接渡す必要がある。computed signalを渡すと `Serializing dirty task` 警告が発生する。

```
// NG: computed signalを追跡するとシリアライズ警告が発生
useResource$(({ track }) => {
  track(() => branchCart.value); // branchCart は computed signal
});

// OK: 元のbase signalを直接追跡する
useResource$(({ track }) => {
  track(() => cartStore.cart.value); // cartStore.cart はbase signal
});
```

### `useResource$` と `useTask$` を使い分ける

`useResource$` `<Resource>` はSSR時のStreaming表示に最適化されている。カート削除のように「クライアントサイドの状態変化を即時にUIへ反映させたい」場面では期待どおりに動作しない。クライアント状態の変化をトリガーにUIを更新するなら `useTask$` を使うこと。

### オブジェクトを `track()` に渡すには `JSON.stringify` が必要

`searchQuery` のようなオブジェクトは参照が変わらない場合、そのまま `track()` に渡しても変化を検知できないことがある。 `track(() => JSON.stringify(searchQuery))` のようにシリアライズして渡すと確実。

--- 以下略 ---

実装Tipsで補強しきれないQwik本体の設計思想は、以下のスクラップに書き溜めてClaude Codeに参照させました。結果として、上述のようなハルシネーションを抑えられました。コンポーネントの変換作業の多くをClaude Code（移行当時はSonnet 4.5）に任せながら、段階的にQwik版に差し替えていきました。

<https://zenn.dev/connect0459/scraps/24bda40cc36afe>

## 移行結果

移行前後で、PageSpeed Insights（以下PSI）を用いてパフォーマンス指標を比較しました。両サイトともCloudflare Pagesでホストし、Google Tag Managerタグ（以下GTMタグ）設定・バックエンドAPIのレスポンスも同一条件で計測しています。

最も明確な差が現れた指標はJS転送サイズです。代表的な3パスの計測値を以下に示します。サードパーティスクリプトはGTMタグが支配的であり、両フレームワークでほぼ同等だったため、ここではファーストパーティJSを比較します。

算出方法

PageSpeed Insights（PSI）の `resource-summary` audit から、Script resourceTypeの転送量を取得しました。各パスをモバイルで3回計測して平均値を集計しています。ファーストパーティとサードパーティの分類はPSIの `network-requests` audit のオリジン情報をもとにしています。

| Path | Next.js | Qwik | 削減率 |
| --- | --- | --- | --- |
| `/` | 127.7 KB | 98.9 KB | 23% |
| `/search/` | 138.7 KB | 91.6 KB | 34% |
| `/cart/` | 132.9 KB | 77.9 KB | 41% |

削減率の考察

`/cart/` はiOSのAmazonアプリのカート画面に近いUIで、数量変更ボタン（+/−）・削除ボタンなど、アイテム1件につき複数のインタラクティブな要素が存在します。

ただし、PSI計測時はログインセッションがないため、カートは空の状態でした。それでも削減率が最大だったのは、 **JSのバンドル構造の差** が主因と考えています。Next.js版ではカート画面をリアクティブなUIにするために、Client Componentが数量変更ボタン、削除ボタンをimportしていました。そのため、カートが空であっても初期バンドルにこれらのコードが含まれ、Hydration時に一括ロードされます。Qwikでは `$` 境界によってハンドラが別チャンクに分離されるため、初期ロードには含まれません。

`/search/` の削減率（34%）も同様で、常にページ上に存在する検索フォームや、カートへの追加ボタンが `$` 境界で分離されています。そのため、Qwikでは初期ロードに含まれないことが削減に寄与していると考えられます。

比較に用いたパスでは、2〜4割の削減を確認しました。この差は、Qwikが `$` 境界をもとにコードを細かく分割し、インタラクション発生まで不要なチャンクをダウンロードしないためです。

Next.jsは「40〜55KBの共有チャンク数本＋ページ固有の小チャンク」という構成なのに対し、Qwikは「22KBのアプリエントリーチャンク＋1〜2KBの小チャンク30〜40本」という構成でした。この値はPSIの `network-requests` auditで確認しています。

なお、PSIのパフォーマンススコアなども比較を試みましたが、こちらはGTMタグなどサードパーティスクリプトがLCPに支配的な影響を与えていたようで、フレームワーク間の優劣を読み取れるデータが得られませんでした。そのため、本記事では掲載を省略しています。

## 開発者視点で見たQwikのPros/Cons

前節ではパフォーマンスの定量比較をしました。ここからは開発者体験として、Qwikの良い点・つらい点を両方お伝えします。

### ここが良いねQwik

#### パフォーマンスを意識したAPI設計

Next.jsでは、サーバーサイドフェッチが直列にならないよう気を遣う必要がありました。公式ドキュメントにも、並行フェッチを実現するためのコード設計例が公開されています。

<https://nextjs.org/docs/15/app/getting-started/fetching-data#parallel-data-fetching>

Next.jsでは `await` で直列に書いてしまうと全体が遅延するため、並列化が必要な箇所は `Promise.all` を意識的に使う必要があります。実際、私の実装でも意識が足りず順次待機（sequential await）になっている箇所が残っていました。

一方、Qwikが提供するルート単位のサーバーサイドデータローダー `routeLoader$` はデフォルトで並列実行されます。また、ある `routeLoader$` の結果に依存して別の `routeLoader$` の解決を待ちたい場合、 `requestEvent.resolveValue()` で先行ローダーの解決を待つことができます。

以下に簡略化した例として、支店情報とそれに紐づく公開設定を取得することを考えます。 `useBranchConfigLoader` はどの支店にアクセスされているかが確定するまで実行されないので、 `requestEvent.resolveValue()` で解決を待ちたいローダーを渡します。

```
export const useBranchLoader = routeLoader$(async (requestEvent) => {
  const { branchId } = requestEvent.params;

  const response = await getValidBranchList();
  const requestedBranch = response.data?.find(
    (branch) => branch.id === branchId,
  );

  return requestedBranch; // { id, name, ... } を後続のloaderが利用できる
});

export const useBranchConfigLoader = routeLoader$(
  async (requestEvent) => {
    // 親のrouteLoader$から支店情報を取得
    const branch = await requestEvent.resolveValue(useBranchLoader);
    return await getBranchConfig(branch.id);
  },
);

export default component$(() => {
  const branch = useBranchLoader();
  const branchConfig = useBranchConfigLoader();

  return (
    <>
      <Header branch={branch.value} />
      <Slot />
      <Footer
        branch={branch.value}
        branchConfig={branchConfig.value}
      />
    </>
  );
});
```

ローダーの並列実行をデフォルトとしつつ、依存関係を `resolveValue()` で宣言できる点はNext.jsにはない特徴です。Qwikが提供する関数には、「開発者がQwikの機能を使えばパフォーマンスが良くなる」という設計思想が一貫して込められています。

<https://qwik.dev/docs/route-loader/>

#### qwikloaderによる一元的なイベント管理

このWebアプリには、サイト内リンクのクリックやフォームのSubmitに応じてフルスクリーンオーバーレイを表示するグローバルローディング機能を実装していました。Next.js版の実装では、 `LoadingLink` コンポーネントが `event.preventDefault()` でデフォルト遷移を止めてグローバルステートを書き換え、 `router.push()` でナビゲーションを実行していました。

```
// Next.js
const handleClick = async (event: React.MouseEvent<HTMLAnchorElement>) => {
  event.preventDefault();
  setIsLoading(true);
  router.push(targetPath);
};
```

このクリックハンドラはHydrationの完了後に登録されます。そのため、通信環境やデバイス性能によってHydrationが遅延している間に押されたリンクでは、実際にオーバーレイが表示されない不具合を確認していました。

Qwik版では、qwikloaderがグローバルイベントリスナーとしてページロード直後から動作するため、Hydration遅延に起因するこのような不具合がほぼ解消されました。具体的な実装としては、 `useSignal` でsignalを作成し、更新用の関数を `$` で包んだQRL関数としてContextに登録するものです。

```
/**
 * @example
 * ```tsx
 * <LoadingProvider>
 *   <App />
 * </LoadingProvider>
 * ```
 */
export const LoadingProvider = component$(() => {
  const isLoading = useSignal(false);

  const setIsLoading = $((value: boolean) => {
    isLoading.value = value;  // signalの更新は .value への代入
  });

  const contextValue: LoadingContextType = {
    isLoading,
    setIsLoading,
  };

  useContextProvider(LoadingContext, contextValue);

  return <Slot />;
});
```

各コンポーネントでは `useLoadingContext()` を呼び出すことで `isLoading` と `setIsLoading` を受け取れます。 `setIsLoading(true)` で値を更新するだけでよく、ページ遷移はQwikの `Link` コンポーネントが担います。

```
// Qwik
const handleClick = $(() => {
  setIsLoading(true);
});

// Linkコンポーネントにハンドラを渡すだけ - router.push() は不要
<Link href={targetPath} onClick$={handleClick}>{/* ... */}</Link>
```

qwikloaderはページ全体を一括管理するグローバルイベントリスナーとして動作します。個々のコンポーネントがHydrationでハンドラを登録するのを待たず、ページロード直後から全クリックイベントを受け取れる状態になっています。

<https://qwik.dev/docs/advanced/qwikloader/>

qwikloaderの内部動作もスクラップにまとめているので、興味があればご覧ください。

<https://zenn.dev/link/comments/5c31e4207cdccb>

### ここがつらいよQwik

#### `$` がついた関数の挙動

Qwikで最初につまずくのが `$` サフィックスです。 `$` がついた関数はコンパイラへの指示であり、その位置がチャンク分割の境界になります。

```
// 見た目はただの関数だが、$によってコンパイラが別チャンクに分離する
const handleClick = $(() => {
  console.log('clicked');
});
```

具体的には、次のような制約が暗黙に存在します。

* チャンクをまたぐ際、値はシリアライズされる必要がある
  + シリアライズできないクラスインスタンスや通常の関数は渡せない
* 「いつ・どこで実行されるか」がコードを読むだけでは判断できない

これはReactの `UI = f(state)` という宣言的なモデルとは異なります。 `$` を境界にコンパイラが別チャンクへ分離・シリアライズする変換が挟まるため、「関数を書いているのか、コンパイラとの契約を書いているのか」という意識の転換が必要です。

<https://qwik.dev/docs/advanced/dollar/>

#### 「Reactに似ている」という罠

Qwikの辛いところは、見た目がReactによく似ているという点です。一見すると馴染みやすく見えますが、それが却って理解の妨げになる場合もあります。

`component$` ・ `useSignal` ・JSXなど、Reactを知っている人ならなんとなく読めてしまいます。しかし実際には、Reactの感覚で書くとすぐエラーになり、「なぜReactで動くのにQwikでは動かないのか」というデバッグに時間を取られます。先述のLoadingLinkのパターンはまさにこれで、Reactライクな見た目への親しみやすさが、むしろ認知的な罠になります。 `$` に関する制約が、この先入観によってさらに見えにくくなります。

Reactにも非自明な部分はありますが、この性質はQwik特有であるため、入門コストは高めです。コンポーネントの定型的な変換作業はAIエージェントにある程度任せられます。しかし、細かい動作の確認やパフォーマンス最適化を考えたとき、イベント管理を行うqwikloaderなどの内部実装を理解することが、結局のところ近道になります。

## 所感

Qwikを使うことで確かにパフォーマンスが改善されたのですが、やはりコーディングする上ではReactとは異なる頭の使い方をします。多少慣れても、qwikloaderの仕組みやQRL解決を常に頭に置いて書く必要があるので、そこから逃げられないのがQwikのしんどさです。

Reactにも `useEffect` の誤用、メモ化漏れによる不要な再レンダリングなどの落とし穴はあります。ただ、 **「とりあえず動くものを書く」** という点ではReactは圧倒的に楽です。関数コンポーネントとhooksが関数型の思想で一貫しているため、内部実装を知らなくてもひとまず動かせます。パフォーマンスを突き詰めようとすると内部実装の理解が必要になりますが、それは後回しにできます。Next.jsがフロントエンドのデファクトスタンダードであり続けているのは、先行者利益もありますが、この「制約の緩さ」も理由の一つだと思います。

また、QwikはReactのエコシステムと比較すると周辺ライブラリも少ないため、欲しい機能を提供するライブラリがなければ自作になります。この実装とメンテナンスのコストを考えると、Qwikがメインストリームになるにはかなり高いハードルを超えなければならないと感じます。

## まとめ

QwikはReact/Next.jsと比べるとクセの強いフレームワークではありますが、それに見合うリターンも確かに存在します。以下のような環境であれば、Qwikの導入は検討に値するでしょう。

* JSバンドルサイズを削ってパフォーマンスを向上させたい
* 使いたいライブラリにQwikで実装されているものがある、あるいは自作できる
* メンバーが継続的にメンテできる体制がある

現在はQwik v2のBetaが公開されており、コメントノードの廃止によるHTML軽量化など内部設計が刷新されています。v1からの移行はnpxコマンドで提供されるようなので、引き続き動向を追っていこうと思います。

<https://qwik.dev/blog/qwik-2-coming-soon/>

Qwikを試してみたい方は、公式の [Getting Started](https://qwik.dev/docs/getting-started/) からサンプルプロジェクトを作成し、各APIの挙動を知るところから始めてみると良さそうです。

<https://qwik.dev/docs/getting-started/>
