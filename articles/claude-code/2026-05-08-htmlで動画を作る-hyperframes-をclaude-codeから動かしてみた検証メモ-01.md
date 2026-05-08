---
id: "2026-05-08-htmlで動画を作る-hyperframes-をclaude-codeから動かしてみた検証メモ-01"
title: "HTMLで動画を作る HyperFrames をClaude Codeから動かしてみた検証メモ"
url: "https://qiita.com/ikkun9595/items/56ae15af2e6dfc106ea1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "AI-agent", "qiita"]
date_published: "2026-05-08"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

## はじめに

2026年4月にHeyGenがオープンソース公開した [HyperFrames](https://github.com/heygen-com/hyperframes) を、Claude Codeと組み合わせて動かすまでを検証したログです。

HyperFramesは、HTML / CSS / JavaScript で書いたコンポジションをヘッドレスChromeでフレームキャプチャし、FFmpegでMP4にエンコードする動画レンダリングフレームワークです。生成AIの動画生成（Sora、Kling、Veo系）とは設計思想がまったく異なり、「コードで決定論的にフレームを作る」方向のアプローチです。

検証環境:

- macOS / Apple M4 Pro
- Node.js v24.13.0
- FFmpeg 8.1.1
- Claude Code

## HyperFramesの仕組み（事実ベース）

ドキュメントとソースから読み取れる構造:

- 1プロジェクト = 1本の動画
- ルートの `index.html` がメインコンポジション
- `data-composition-id`, `data-start`, `data-duration`, `data-width`, `data-height`, `data-track-index` などのデータ属性で動画タイムラインを宣言
- アニメーションはGSAPタイムラインを `window.__timelines[id]` に登録する規約
- `npx hyperframes render` でヘッドレスChromeを起動 → 指定fpsでフレームキャプチャ → FFmpegでMP4化

つまり「HTMLで動画を作るAI」というよりは、**HTMLを動画化する決定論的レンダラ**です。AI連動はあくまでスキル（`/hyperframes` スラッシュコマンド経由）で動画オーサリングを助ける部分に留まります。

## 環境要件

- Node.js 22 以上（公式要件）
- FFmpeg
- Chrome（システムにインストールされていればOK）
- 推奨: Docker（`--docker` で再現性のあるレンダリングをしたい場合）

確認コマンド:

```bash
npx -y hyperframes@0.5.3 doctor
```

`doctor` は Node / Chrome / FFmpeg / Docker の有無と、メモリ・ディスク容量までチェックします。

## セットアップ手順

### 1. プロジェクトの初期化

```bash
mkdir -p ~/work && cd ~/work
npx -y hyperframes@0.5.3 init my-video --non-interactive --example blank
cd my-video
```

`init` した直後の構成:

```
my-video/
├── AGENTS.md
├── CLAUDE.md
├── hyperframes.json
├── index.html
├── meta.json
└── package.json
```

`package.json` には次のスクリプトが定義されています:

```json
{
  "scripts": {
    "dev": "npx --yes hyperframes@0.5.3 preview",
    "check": "npx --yes hyperframes@0.5.3 lint && npx --yes hyperframes@0.5.3 validate && npx --yes hyperframes@0.5.3 inspect",
    "render": "npx --yes hyperframes@0.5.3 render",
    "publish": "npx --yes hyperframes@0.5.3 publish"
  }
}
```

### 2. Claude Code向けスキルの登録

```bash
npx -y skills add heygen-com/hyperframes
```

実行するとスキル選択UIが出ます。**最小推奨セットは以下の5つ**:

- `hyperframes` — コンポジション作成全般
- `hyperframes-cli` — init / lint / preview / render の操作
- `hyperframes-media` — TTS、文字起こし、背景除去
- `hyperframes-registry` — 公式ブロックの取り込み
- `gsap` — 既定のテンプレートで使われているアニメーションライブラリ

それ以外の `tailwind`, `animejs`, `css-animations`, `lottie`, `three`, `waapi`, `website-to-hyperframes`, `remotion-to-hyperframes` は、該当ライブラリを使う場面で後から追加すれば十分です。

### 3. つまずきポイント: スキルがClaude Codeに認識されない

ここで詰まりました。

`skills add` 後にClaude Codeを再起動しても `/skills` 一覧に出てこない。`npx -y skills list` で確認すると、スキルは確かにインストール済み:

```
Project Skills
gsap                  ~/work/my-video/.agents/skills/gsap
hyperframes           ~/work/my-video/.agents/skills/hyperframes
hyperframes-cli       ~/work/my-video/.agents/skills/hyperframes-cli
hyperframes-media     ~/work/my-video/.agents/skills/hyperframes-media
hyperframes-registry  ~/work/my-video/.agents/skills/hyperframes-registry
```

**原因**: `skills` CLIが `.agents/skills/` 配下にスキルを置く一方、Claude Codeが読みに行くのは `.claude/skills/`。フォーマット（SKILL.md + frontmatter）は同一ですがパスがズレています。

**解決策**: シンボリックリンクで両者を繋ぐ。

```bash
cd ~/work/my-video
mkdir -p .claude/skills
cd .claude/skills
for s in gsap hyperframes hyperframes-cli hyperframes-media hyperframes-registry; do
  ln -sfn ../../.agents/skills/$s $s
done
```

これでClaude Codeを再起動すると `/skills` に5つ表示され、`/hyperframes` などのスラッシュコマンドが利用可能になりました。

`skills` CLIのバージョンによっては将来的に解消される可能性があります。

## 基本ワークフロー

```bash
# ライブプレビュー（ホットリロード対応のスタジオエディタ）
npm run dev
# → http://localhost:3002/#project/<project-name>

# Lint + バリデーション + ビジュアル検査
npm run check

# MP4出力
npm run render
# → renders/<name>_<timestamp>.mp4
```

`npm run check` でやること:

- `lint` — `data-composition-id` 漏れ、トラック重複、未登録タイムラインの検出
- `validate` — スキーマ検証
- `inspect` — ヘッドレスChromeでタイムラインを走査し、テキストのはみ出しやクリッピング外の要素を検出

レンダリングは fps / quality / format オプションが選べます:

```bash
npx -y hyperframes@0.5.3 render --quality draft       # 反復用、軽い
npx -y hyperframes@0.5.3 render --quality high --fps 60  # 最終納品用
npx -y hyperframes@0.5.3 render --format webm         # 透過対応
npx -y hyperframes@0.5.3 render --docker              # 再現性重視
```

## 最小サンプル: テキストアニメ3秒

`npx hyperframes init --example blank` で生成されるテンプレートに、テキストとフェードインを足したものです:

```html
<!doctype html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body {
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      }
      .clip { position: absolute; }
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="3"
      data-width="1920"
      data-height="1080"
    >
      <div
        id="title"
        class="clip"
        data-start="0"
        data-duration="3"
        data-track-index="1"
        style="top: 420px; left: 0; width: 1920px; text-align: center;
               font-size: 140px; font-weight: 800; color: #fff;"
      >
        Hello, HyperFrames
      </div>
      <div
        id="subtitle"
        class="clip"
        data-start="0"
        data-duration="3"
        data-track-index="2"
        style="top: 600px; left: 0; width: 1920px; text-align: center;
               font-size: 48px; color: #93c5fd; letter-spacing: 4px;"
      >
        rendered from HTML
      </div>
    </div>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      tl.from("#title",    { opacity: 0, y: -60, duration: 1, ease: "power3.out" }, 0);
      tl.from("#subtitle", { opacity: 0, y:  40, duration: 1, ease: "power3.out" }, 0.4);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
```

上記から作成された動画
![hyperframes_2026-05-07_23-23-36.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4313579/b68bd8fa-1ec6-4eeb-9b79-e7943b802def.gif)



ポイント:

1. ルートdivに `data-composition-id="main"` と `data-duration="3"`（3秒）を指定
2. 子要素（クリップ）にも `data-start` / `data-duration` / `data-track-index` を付与
3. GSAPタイムラインを **`paused: true` で作成** し `window.__timelines["main"]` に登録（HyperFramesがこれをseekする）

`paused: true` を忘れると、レンダリング時にすでにアニメが進行していて再現できません。これは規約として `hyperframes-cli` のlintが拾います。

## 1動画 = 1プロジェクト の設計

検証中に「複数案を見比べたい」場面で気付いたのですが、HyperFramesは**1プロジェクト1動画モデル**です。

- ルート `index.html` は必ず1つ
- 別案を比較したい場合は別フォルダに `init` するのが標準
- サブコンポジションを `compositions/` 配下に置いて `data-composition-src` でメインから参照する仕組みはあるが、これは**メイン動画の中に並べる用途**で、独立動画の比較用ではない

複数案を同時プレビューするには、別ポートで複数の preview サーバーを立てます:

```bash
# ターミナル1
cd ~/work/proposal-a && npx -y hyperframes@0.5.3 preview --port 3002

# ターミナル2
cd ~/work/proposal-b && npx -y hyperframes@0.5.3 preview --port 3003
```

色やコピーだけ変えたい場合は、`data-composition-variables` を使ったvariables方式で1テンプレ複数バリアントもできます:

```bash
npx -y hyperframes@0.5.3 render --variables '{"title":"案A","accent":"#ff5722"}'
```

## できること / できないこと

検証して把握できた範囲。

**できること**

- HTML/CSS/JSで決定論的に動画を作る（同じ入力なら毎回同じ出力。`--docker` でさらに厳密に）
- GSAP / Anime.js / CSSアニメ / Lottie / Three.js / WAAPI と統合
- 1920x1080 / 1080x1920 などの一般的な解像度
- mp4 / webm / mov 出力（webm/movは透過対応）
- TTS（Kokoro-82M）と文字起こし（Whisper）をローカル実行で取り込み
- variablesで同テンプレを複数バリエーション量産

**できないこと / 注意点**

- ARM64 Linux環境ではChrome headlessバイナリが配布されていないため、サンドボックスやarm系VPSではレンダリング不可（M系MacはmacOSなので問題なし）
- 「ピクセル指定の絶対配置でフルHDを組み立てる」設計なので、レスポンシブWebの感覚で書くと噛み合わない（あくまで動画の固定キャンバスとして書く）
- 生成AI動画（Sora等）のような「プロンプトから映像を作る」ものではない。**素材は自分で書く**

## 印象（事実ベース）

- 1080p/30fpsで数秒の動画はM4 Proで体感数十秒以内にレンダリング完了
- HTMLが書ければ動画が書ける、という制約と自由度のトレードオフは明確
- Claude Codeとの連携はスキルパス問題さえ解決すれば実用的。スキル経由で `data-*` 属性のお作法を踏まえたコードが出る
- バージョンや生成AI動画と競合する技術ではなく、**プログラマブルな動画生成という別カテゴリ**に位置付けるのが正確

## まとめ

検証範囲のまとめ:

- セットアップ: `npx hyperframes init` → `npx skills add heygen-com/hyperframes` → `.claude/skills/` シンボリックリンク作成、で動作
- 環境要件は満たしやすい（Node 22+ / FFmpeg / Chrome）
- 1プロジェクト1動画。複数案は別プロジェクトで並列管理
- 生成AI動画ツールではなく、HTMLを動画にする決定論的レンダラ

「コードで動画を量産する仕組み」が欲しい場合の選択肢として有効でした。プロンプト1発で映像が出てくるツールが必要なら別のサービスを検討する必要があります。

## おまけ

[弊社のニュースサイト](https://nahato.co.jp/latest-news/)から最新情報をもとに1年のニュースをまとめて！
とお願いしたらこんな感じでした。
雑投げの１発クオリティでこれくらいのものが出来上がってくるのであれば、作り込めばいいものが作れそうですね。

<iframe width="560" height="315" src="https://www.youtube.com/embed/VbaGZCiViZk?si=W8Hx0x0obeO1iB9f" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


## 参考

- [HeyGen / hyperframes (GitHub)](https://github.com/heygen-com/hyperframes)
- [HyperFrames Documentation](https://hyperframes.heygen.com/)
- [HyperFrames Quickstart](https://hyperframes.heygen.com/quickstart)
