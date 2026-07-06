---
id: "2026-07-06-claude-code設定のアンチパターン5つsettingsjsonでやりがちなng例と直し方-01"
title: "Claude Code設定のアンチパターン5つ。settings.jsonでやりがちなNG例と直し方"
url: "https://qiita.com/Rapls/items/c7905c331f0fa75f2db5"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "qiita"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

Claude Codeのsettings.jsonは、書き方ひとつで「静かに損する」設定になります。動いてはいるので気づきにくい。自分が実際にやっていた（直した）NGを5つ、悪い例と直し方で並べます。

設定ファイルの場所は、全体が `~/.claude/settings.json`、プロジェクト単位が `.claude/settings.json` です。以下はどちらでも使えます。

1. モデルを固定して、切り戻しを用意しない
2. deny を設定せず、危険コマンドを素通しにする
3. CLAUDE.md に書きすぎる
4. モデルの切り替わりに、気づけない
5. permissions を広く開けすぎる

## 1. モデルを固定して、切り戻しを用意しない

主モデルが過負荷や提供停止で落ちると、そのまま作業が止まります。

```jsonc
// ❌ NG：主モデルだけ。落ちたら手が止まる
{
  "model": "claude-fable-5"
}
```

```jsonc
// ✅ OK：fallbackModel で切り戻し先を用意する
{
  "model": "claude-fable-5",
  "fallbackModel": ["claude-opus-4-8", "claude-sonnet-4-6"]
}
```

なぜ。`fallbackModel` は、主モデルが応答できないとき、配列の順に試して最初に通ったモデルで続行します。エントリは最大3つ、v2.1.166以降の機能です。長いエージェント作業やCI中に主モデルが詰まる、を一行で救えます。無ければ `claude update` を。ただし認証やAPIキーの失敗は、どのモデルでも同じ理由で落ちるので、これでは救えません。そこは切り分けが要ります。

## 2. deny を設定せず、危険コマンドを素通しにする

一度ヒヤッとしてから入れるより、先に入れておくほうが安全です。

```jsonc
// ❌ NG：permissions を素のまま。何でも走りうる
{
  "permissions": {}
}
```

```jsonc
// ✅ OK：壊す系を deny で止めておく
{
  "permissions": {
    "deny": [
      "Bash(rm -rf*)",
      "Bash(git push --force*)"
    ]
  }
}
```

なぜ。`rm -rf` やforce pushは、一度やると戻せません。deny に入れておけば、その手のコマンドは実行前に止まります。自分の環境で「これだけは走らせたくない」を、事故る前に言語化しておく作業でもあります。

## 3. CLAUDE.md に書きすぎる

良かれと思って盛るほど、効かなくなります。

```text
❌ NG：数百行のCLAUDE.md。全部を「重要」で並べる
（優先順位が伝わらず、肝心の前提が埋もれる）
```

```text
✅ OK：短い前提だけに絞る
・本当に毎回効かせたいルールだけ残す
・例外や細部は、その都度プロンプトで渡す
・迷ったら、行を半分に減らしてみる
```

なぜ。CLAUDE.mdの内容は毎ターンのコンテキストに乗ります。長いほどトークンを食い、しかもモデルはどれを優先すべきか分からなくなる。増やすほど効く、ではありません。短く保つほうが、結局よく効きました。

## 4. モデルの切り替わりに、気づけない

fallbackや、Fable 5の内容ベースの切り替えが起きても、気づかなければ「静かに質が変わった」で終わります。

```jsonc
// ❌ NG：今どのモデルで動いているか、画面から分からない
{
  "model": "claude-fable-5"
}
```

```jsonc
// ✅ OK：ステータスラインにモデルを常時表示する
{
  "model": "claude-fable-5",
  "statusLine": { "type": "command", "command": "your-statusline-script" }
}
```

なぜ。Fable 5は安全分類器に引っかかると、そのリクエストを既定のOpusで再実行し、以降そのまま続きます。セッションの最初のリクエストでも、CLAUDE.mdやgit statusの内容で発火することがある。切り替わりが視界に入っていないと、指摘の粒度が変わったことに後から気づきます。`/status` でも確認できますが、常時表示のほうが取りこぼしません。戻すときは `/model fable` です。

## 5. permissions を広く開けすぎる

自動化を優先して全部許可すると、便利さと引き換えに事故の面が広がります。

```jsonc
// ❌ NG：確認をなくすために、広く allow する
{
  "permissions": {
    "allow": ["Bash(*)"]
  }
}
```

```jsonc
// ✅ OK：よく使う安全なものだけ allow、危険は deny
{
  "permissions": {
    "allow": ["Bash(npm run test*)", "Bash(git status)"],
    "deny": ["Bash(rm -rf*)", "Bash(curl*| sh)"]
  }
}
```

なぜ。`Bash(*)` のような広い許可は、確認の手間を消してくれますが、AIの判断ミスや外部からの指示混入が、そのまま実行に届きます。よく使う安全なコマンドだけを名指しで許可して、危険は deny で塞ぐ。手間と安全のあいだで、線を自分で引くのがちょうどよかったです。

## 早見でまとめ

- `fallbackModel` で切り戻し先を用意する（最大3つ、v2.1.166〜）。ただし認証系は救えない
- `deny` で壊す系コマンドを先に止める
- CLAUDE.md は短い前提だけ。盛るほど効かない
- ステータスラインにモデルを常時表示。切り替わりに気づく
- permissions は「安全を allow、危険を deny」で、線を自分で引く

どれも、設定した直後は違いが見えません。効いてくるのは、モデルが落ちた日、危険コマンドが走りかけた日、質が静かに変わった日です。事が起きる前に一度だけ整えておくと、あとの自分が助かります。役に立ったらストックして、settings.jsonを見直すとき戻ってきてください。

参考（公式ドキュメント）:
- Model configuration: https://code.claude.com/docs/en/model-config
- Claude Code model configuration: https://support.claude.com/en/articles/11940350-claude-code-model-configuration

---

ふだんはraplsworks.comで、WordPressプラグイン開発やClaude Codeまわりのことを書いています。

https://raplsworks.com/
