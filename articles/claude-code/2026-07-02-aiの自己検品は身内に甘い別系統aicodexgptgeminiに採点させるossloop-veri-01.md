---
id: "2026-07-02-aiの自己検品は身内に甘い別系統aicodexgptgeminiに採点させるossloop-veri-01"
title: "AIの自己検品は身内に甘い。別系統AI(codex/GPT/Gemini)に採点させるOSS「loop-verify」を公開した"
url: "https://qiita.com/akihidem/items/3b989b7b987acd351875"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "OpenAI", "Gemini", "GPT", "Python"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

AI に成果物を作らせて、AI に検品させる。この自己検証ループには構造的な穴が1つある。**書いた本人と同じ系統のモデルが検品すると、盲点まで共有する**ことだ。

[loop-verify](https://github.com/akihidem/loop-verify) はその穴に対する小さな道具で、検品だけを**別系統のモデル(codex / GPT / Gemini)に渡す** MCP サーバ兼 Python 関数として公開した。MIT ライセンスで、README の言葉どおり "no accounts, no metering, no billing"[1]。アカウント登録も課金もない、ただのツールである。

## 問題: builder と checker が同族だと、同じ見落としをする

自己検証ループ(凍結した YES/NO 基準 → 実装 → 機械チェック → AI 検品 → 修正の反復)は、AI 開発の実務でよく機能する。ただし検品役を Claude にやらせて Claude の成果物を見せる、という構成には限界がある。同族モデルは学習も癖も近く、書き手が踏んだ穴を検品側も同じように踏む。

これは精神論ではなく、採点者の独立性の問題だ。README の設計説明にあるとおり、検品者を別系統にする理由は "so it doesn't share their blind spots"[2]、つまり盲点を共有しないことに尽きる。

## 何をするツールか

入力は2つ。

- `criteria`: 凍結済みの YES/NO 受け入れ基準
- `artifact`: 検品対象(diff かファイル内容)

出力は1つの verdict。`PASS`/`FAIL`、基準ごとの `OK`/`NG`、基準外で見つけた欠陥、そして具体的な `fix_instructions`。

ポイントは、この verdict の契約を [loop-kit](https://github.com/akihidem/loop-kit)(自己検証ループの Claude Code プラグイン)の同族 `validator` と**同一**にしてあることで、既存ループへの drop-in 置換になる。loop-kit 側の `loop-protocol` は「セッション内に cross-vendor checker があればそれを優先する」設計なので、loop-verify を MCP サーバとして立てておくだけで、パッチ無しで独立検品に切り替わる。

## 独立性は実際に効くのか(edge bench)

同梱の bench で測ってある。README の記載[3]のとおり、同梱 9 fixtures(clean 4 / buggy 5・バグ種は多様)に対して、codex バックエンドの成績は **"recall 1.0, false-positive 0.0 → GO"**[4]。仕込んだ実バグを全部拾い、健全な fixture を1つも誤検知しなかった。

```bash
python bench/edge_bench.py --backend codex   # independent checker -> GO/NO-GO
```

bench 自体が GO/NO-GO を返すので、「この環境で独立検品を採用してよいか」の判定にそのまま使える。

## 使い方

```bash
# install(標準的な venv)
python3 -m venv ~/.venvs/loop-verify
~/.venvs/loop-verify/bin/pip install -r requirements.txt

# デモ(決定的・オフライン。exit 0 がスモークテストを兼ねる)
python demo/run_demo.py

# 本物の edge(codex の枠を消費)
python demo/run_demo.py --backend codex
```

MCP サーバとして立てると `independent_verify(criteria, artifact)` ツールがセッションに生える。Claude Code から使う場合はこれだけで loop-kit のループが独立検品に切り替わる。

Docker で運用する場合は、codex CLI がイメージに入らないためキー方式のバックエンド(`LOOP_VERIFY_BACKEND=openai` など)を使う。**hosted インスタンスは提供しない**。Dockerfile を配るだけで、動かすのは各自の環境という設計判断にした(検品対象のコードを他人のサーバに送る構造を作りたくなかった)。

## 開発中に出た学び(1つだけ)

検品プロンプトに「必ず欠陥を探せ」と書くと精度が死ぬ。checker が忖度して健全な成果物にも難癖をつけ始め、false positive が跳ねる。「欠陥があれば列挙、なければ PASS」という中立な指示と、基準(criteria)の凍結が、独立検品の精度を支える。採点者を替えるだけでなく、採点者への聞き方も設計対象になる。

## まとめ

- 自己検証ループの検品を、書き手と別系統のモデルに渡す OSS
- verdict 契約は loop-kit validator と同一 = drop-in
- 実測: 9 fixtures で codex backend が recall 1.0 / false-positive 0.0 → GO
- MIT・アカウント不要・hosted なし

リポジトリ: https://github.com/akihidem/loop-verify

## 出典

本稿の引用はすべて一次資料と逐語照合（verify_article 通過）のうえ掲載しています（2026-07-02 検証）。

[1] https://raw.githubusercontent.com/akihidem/loop-verify/main/README.md
