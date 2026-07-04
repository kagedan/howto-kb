---
id: "2026-07-04-line風チャット動画メーカーをhtml1枚で作った話-通知音をweb-audio-apiで再現する-01"
title: "LINE風チャット動画メーカーをHTML1枚で作った話 ─ 通知音をWeb Audio APIで再現する"
url: "https://zenn.dev/popopon_me/articles/efe30525859eee"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-07-04"
date_collected: "2026-07-05"
summary_by: "auto-rss"
query: ""
---

TikTokやReelsでよく見る「LINEのトーク画面風の会話がポンポン進む動画」、あれを作ろうとして地獄を見たので、ツールごと作りました。

**Popopon**  
<https://popopon.me>  
（無料・登録不要・ブラウザ完結）

この記事は、その開発で一番面白かった2つの問題——**「効果音の同期」を構造的に消す設計**と、**LINEの通知音をWeb Audio APIでゼロから合成する話**——の技術メモです。

## 問題:「音ハメ」という単純作業の暴力

チャット風動画の作り方は大きく3つあります。実機2台で本物のトークを画面収録する、フェイクトーク画像を作って編集ソフトでアニメーションさせる、CapCut等のテンプレを使う。

どれを選んでも最後に同じ壁が来ます。**通知音の配置**です。

吹き出しが20個あれば、編集ソフトのタイムラインに通知音を20回、出現タイミングに合わせて置く。テンポを直せば全部ズレて置き直し。私はこれを1時間やって挫折しました。

ここで気づきます。音がズレるのは「映像が先に固定されていて、音を後から合わせる」からだと。**逆にすればいい。というか、分けなければいい。**

## 解決:描画と発音を同じ場所で発火させる

Popoponの再生エンジンは、要するにこれだけです。

```
// 吹き出しをDOMに追加した"その次の行"で音を鳴らす
$('chatBody').appendChild(buildBubble(msg));
scrollChat();
if(msg.side === 'other') playRecv(); // 受信音
if(msg.side === 'me')    playSend(); // 送信音
```

吹き出しの出現と発音が同一のイベントループ内で実行されるので、**同期という概念自体が存在しません**。ズレようがない。動画編集の世界で「音ハメ」と呼ばれていた作業は、映像と音を別々のタイムラインで管理するというアーキテクチャの帰結でしかなかった、というオチです。

あとはこの画面を録画モード（スマホ枠だけを全画面表示して3秒カウントダウン→自動再生）で画面収録すれば、音の入った素材が完成します。

## 本題:LINEの通知音って、何の音?

効果音を鳴らすと決めたら、次の問題は「何を鳴らすか」です。

本物のLINEの音源ファイルを使うのは当然アウト（著作物です）。じゃあ「それっぽい音」を合成しようとなるわけですが、そもそもあの音は何なのか。

調べると、iPhone版LINEのデフォルト通知サウンドは「トライトーン」という名前で、正体は**マリンバ系の音色で3音が駆け上がる**構造でした。音程の関係はおおよそ「根音 → 完全5度 → オクターブ」。ドで始まるなら「ド→ソ→ド（上）」です。

つまりあの「ポポポン↑」は、音楽理論的にいちばん安定して気持ちいい跳躍（1度・5度・8度）を最速で駆け上がる設計なんですね。通知音として完成されすぎている。

## マリンバをWeb Audio APIで合成する

マリンバの音色の特徴は、スペクトルを見ると **基音に対して約4倍音が強く出て、しかも高次成分ほど速く減衰する** ことです。サイン波2本で十分それらしくなります。

```
function marimba(freq, start, dur, g){
  const ac = ctx(), t = ac.currentTime + start;

  // 基音
  const o = ac.createOscillator(), ga = ac.createGain();
  o.type = 'sine'; o.frequency.value = freq;
  ga.gain.setValueAtTime(g, t);
  ga.gain.exponentialRampToValueAtTime(.0008, t + dur);
  o.connect(ga).connect(ac.destination);
  o.start(t); o.stop(t + dur + .05);

  // 4倍音（マリンバらしさの正体。基音より速く消す）
  const o2 = ac.createOscillator(), ga2 = ac.createGain();
  o2.type = 'sine'; o2.frequency.value = freq * 4;
  ga2.gain.setValueAtTime(g * .22, t);
  ga2.gain.exponentialRampToValueAtTime(.0006, t + dur * .35);
  o2.connect(ga2).connect(ac.destination);
  o2.start(t); o2.stop(t + dur * .35 + .05);
}
```

これを「根音→5度→オクターブ」で3連発します。D6基準にしました。

```
function playRecv(){
  const g = vol() * 0.5;
  marimba(1174.66, 0,   .50, g);        // D6（根音）
  marimba(1760.00, .13, .50, g);        // A6（完全5度）
  marimba(2349.32, .26, .62, g * 1.05); // D7（オクターブ）
}
```

ポイントは3つ。

1. **アタックは即立ち上げ、減衰はexponentialRamp**。打楽器は「叩いた瞬間が最大音量→指数減衰」なので、linearRampだとオルガンっぽくなって台無しになります
2. **発音間隔130ms**。これより速いと3音が団子になり、遅いとメロディに聞こえて通知音らしさが消えます
3. **最後の音だけ少し長く・少し大きく**。駆け上がりの着地感が出ます

送信音のほうは、LINEの「ポンッ」という丸い短音を、ピッチが落ちるサイン波1本で作りました。

```
function playSend(){
  const ac = ctx(), t = ac.currentTime, g = vol() * 0.3;
  const o = ac.createOscillator(), ga = ac.createGain();
  o.type = 'sine';
  o.frequency.setValueAtTime(920, t);
  o.frequency.exponentialRampToValueAtTime(540, t + .07); // 70msで落とす
  ga.gain.setValueAtTime(g, t);
  ga.gain.exponentialRampToValueAtTime(.001, t + .12);
  o.connect(ga).connect(ac.destination);
  o.start(t); o.stop(t + .16);
}
```

音源ファイルを1つも持たずに済むので、\*\*アプリ全体がHTML1枚（依存ゼロ・ビルドなし・約15KB）\*\*のまま保てます。ちなみにAudioContextはユーザー操作なしに音を出せない仕様（autoplay policy）があるので、再生ボタンのハンドラ内で `resume()` を叩くのを忘れると無音デバッグで1時間溶けます（溶けました）。

## テンポは「文字数」から自動計算する

もう一つの設計判断が表示間隔です。全メッセージ等間隔だと、長文でも短文でも同じ速度で流れて読めない動画になります。かといって1通ずつ手動指定は音ハメ地獄の再来。

なので「人は文字数に比例した時間をかけて読む」という雑だが正しいモデルで自動化しました。

```
// 表示間隔 = 基本の間 + 直前のセリフの文字数 × 1文字あたりms
const prevLen = messages[i-1].text.length;
const wait = gapBase + prevLen * charMs; // 既定: 700ms + 55ms/字
```

これだけで動画のテンポが「読む速さに追従」します。決めゼリフの前だけ手動で間を上書きできる逃げ道（1メッセージ単位のdelay指定）も残してあります。ホラー系のオチの前に3000msの沈黙を置く、みたいな演出用です。

## ハマりポイント:iOSの100vh

スマホ対応で古典的なやつを踏みました。`height: calc(100vh - ...)` で組んだレイアウトが、iOS Safariだとツールバーの伸縮分だけ狂ってタブバーが画面外に消える。

対策は `100dvh`（dynamic viewport height）へのフォールバック付き切り替えと、ホームバー回避の `env(safe-area-inset-bottom)` です。

```
body{
  height: 100vh;   /* フォールバック */
  height: 100dvh;  /* iOS Safariはこちらが効く */
}
.tabbar{
  height: calc(50px + env(safe-area-inset-bottom));
  padding-bottom: env(safe-area-inset-bottom);
}
```

2026年にもなって100vhで殴られるとは思わなかった。

## HTML1枚という思想

最後に構成の話を。PopoponはReactもビルドツールも使っていない、素のHTML+CSS+JSの1ファイルです。理由は3つあります。

第一に、**入力データが一切サーバーに行かない**こと。台本も添付画像も全部ブラウザ内で完結するので、クライアント案件の台本を扱う動画制作者でも安心して使えます（プライバシーポリシーに書ける最強の一文「サーバーに送信されません」が実装コストゼロで手に入る）。

第二にホスティングが静的配信のみで済むこと。Cloudflareに置いたのでランニングコストは実質ドメイン代の年1,500円だけです。

第三に、この規模（1,000行弱）ならフレームワークの恩恵よりファイル1個の見通しの良さが勝つこと。`view-source:` で全実装が読めるツールって、ちょっといいですよね。

## まとめ

* 「音ハメ」は作業ではなくアーキテクチャの問題。描画と発音を同一イベントで発火させれば同期は消える
* LINEのトライトーンの正体は「根音→5度→オクターブのマリンバ3連」。サイン波2本×3音で合成できる
* マリンバらしさ＝強い4倍音を基音より速く減衰させること
* iOSの100vhは2026年も現役で人を殴ってくる

作ったもの: **Popopon**<https://popopon.me> （無料・登録不要）  
使い方の記事はnoteに書きました。台本をAIに書かせるプロンプトも配布しているので、興味があればXで声かけてください → @popopon\_me
