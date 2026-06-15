---
id: "2026-06-14-claude-codeのスキルが自動で発火しない本当の理由未文書設定-skilllistingmax-01"
title: "Claude Codeのスキルが自動で発火しない本当の理由——未文書設定 skillListingMaxDescChars(既定1536字)を実機で確かめた"
url: "https://qiita.com/yurukusa/items/2700b4d67f77220fa618"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-06-14"
date_collected: "2026-06-15"
summary_by: "auto-rss"
query: ""
---

## 「スキルを作ったのに自動で起動しない」の本当の原因

Claude Code でスキル(Skills)を自作したのに、いざ会話で関連する作業を頼んでも自動で発火しない。とくに日本語で話しかけると起動しない。こういう経験はないでしょうか。

私(ゆるくさ)も同じところで何度もつまずきました。よく勧められる回避策は「英語で書いた `description` のうしろに日本語のトリガー語を足す」というものですが、これだけだと条件によっては静かに効かなくなります。

原因を突き止めるために、手元にインストールされている Claude Code の本体(`@anthropic-ai/claude-code` のバンドル実体)を実際に調べました。すると、公式ドキュメントにまだ載っていない 2 つの設定が、スキルの自動発火を裏で左右していることが分かりました。この記事は、その実機で確かめた事実と、`settings.json` でできる具体的な対処をまとめたものです。

---

## 仕組み:モデルは「スキル一覧」を見て発火を決める

Claude Code は、各スキルの `description` を集めた「スキル一覧」をモデルへ毎ターン渡します。モデルはその一覧を読んで、今の会話にどのスキルが合うかを判断します。つまり、**`description` の中身がモデルに届いていなければ、そのスキルは候補にすら上がりません。**

ここに 2 つの上限が効いています。どちらも実機のバイナリに実在を確認しました。

### 1. `skillListingMaxDescChars`(既定 1536 文字)

1 つのスキルの `description` を一覧へ載せるときの文字数の上限です。バイナリ内の設定スキーマには、こう書かれています。

> Per-skill description character cap in the skill listing sent to Claude (default: 1536). Descriptions longer than this are truncated. Raise to opt in to higher per-turn context cost.

訳すと「Claude へ送るスキル一覧での、1 スキルあたりの説明文の文字数の上限(既定 1536)。これより長い説明文は切り詰められる。上げると毎ターンの文脈コストが増えるのを承知で広げられる」。

つまり、**1536 文字を超えた分は黙って切り落とされます。** 警告も出ません。

### 2. `skillListingBudgetFraction`(既定 0.01 = 1%)

スキル一覧の全体に割く、文脈窓(context window)の割合です。

> Fraction of the context window (in characters) reserved for the skill listing sent to Claude (default: 0.01 = 1%). When the listing exceeds this, descriptions are shortened to fit. Raise to opt in to higher per-turn context cost.

「Claude へ送るスキル一覧のために確保する、文脈窓(文字数換算)の割合(既定 0.01 = 1%)。一覧がこれを超えると、収まるように説明文が短縮される」。

スキルの数が多いと、一覧そのものがこの 1% の枠に収まるように圧縮されます。**つまり、スキルが増えるほど、1 つあたりの説明文に使える文字数は実質さらに減ります。**

---

## なぜ「英語の説明文に日本語を足す」が静かに失敗するのか

ここまで分かると、よくある回避策の弱点が見えてきます。

英語で書いた長めの `description` のうしろに、日本語のトリガー語を継ぎ足すとします。合計が 1536 文字を超えると、**切り詰めは末尾から起きるので、あとから足した日本語の部分が真っ先に消えます。** 結果、設定したつもりのトリガー語がモデルに届かず、「ときどき発火しない」「日本語だと起動しない」という症状が再発します。

しかも切り詰めは無言です。`description` を長く凝るほど、この罠にはまりやすくなります。

---

## 実機での確かめ方

私が確認した手順です。Claude Code の本体は、おおむね次の場所にあります(環境によりパスは変わります)。

```bash
# nvm を使っている場合の一例
BIN=$(find ~/.nvm -path '*claude-code*' -name 'claude' | head -1)

# 2つの既定値が実在するか
grep -ao 'skillListingMaxDescChars' "$BIN" | head -1
grep -ao 'skillListingBudgetFraction' "$BIN" | head -1

# 既定値の本体(短縮名で埋め込まれている)
grep -ao 'q75=[0-9]*' "$BIN" | head -1   # → q75=1536
grep -ao 'H75=0.01' "$BIN" | head -1     # → H75=0.01
```

設定値を解決している関数も、`settings.json` の値があればそちらを優先し、なければ既定値にフォールバックする形で実在します(おおよそ `skillListingMaxDescChars ?? 1536`、`skillListingBudgetFraction ?? 0.01` という分岐)。

> 注意:バージョンによって内部の短縮名(`q75` など)は変わり得ます。確実なのは `skillListingMaxDescChars` / `skillListingBudgetFraction` という設定キー名と、スキーマに書かれた既定値の方です。短縮名でなくキー名で探すことをおすすめします。

---

## 対処:`settings.json` で上限を上げる

この 2 つは、`settings.json` で明示的に変更できる設定です。`description` をどうしても長く書きたい、あるいはスキルの数が多い場合は、上限を引き上げるのが正攻法です。

```json
{
  "skillListingMaxDescChars": 4096,
  "skillListingBudgetFraction": 0.03
}
```

ただし、スキーマの説明にもある通り、**これは「毎ターンの文脈コストが増えるのを承知で広げる」設定です。** スキル一覧は毎ターン送られるので、上げた分だけトークン消費が増えます。むやみに大きくせず、必要な範囲で上げてください。

コストを増やさずに直したい場合は、設定をいじる前に次を見直すのが先です。

- **トリガーに効く語を `description` の先頭に置く。** 切り詰めは末尾から起きるので、重要語を前に出せば、上限内でも生き残ります。
- **`description` を短くする。** 1536 文字に対して説明文が長すぎないか。装飾的な前置きより、何のための・どんなときに使うスキルかを簡潔に。
- **使っていないスキルを減らす。** スキルの数が多いほど 1% の枠が圧迫されます。常用しないものは無効化する。

---

## 正直に書いておくこと

「この設定を変えれば発火率が何 % 上がる」とは書けません。発火するかどうかはモデルの判断であり、手元で確率を厳密に測る方法がないからです。この記事で言えるのは、**「説明文が切り詰められると、トリガー語がモデルに届かない経路が確かに存在する」**という、実機で確認できた事実までです。発火しない原因の一つを、設定で潰せる、というのが要点です。

---

## まとめ

- スキルの自動発火は、`description` を集めた「スキル一覧」をモデルが読んで決める。
- 1 スキルの説明文は既定 `1536` 文字で**無言で切り詰められる**(`skillListingMaxDescChars`)。
- スキル一覧の全体は文脈窓の**既定 1%** に収められ、スキルが多いとさらに圧縮される(`skillListingBudgetFraction`)。
- だから「英語の説明文の末尾に日本語を足す」は、合計が上限を超えると日本語側から消えて静かに失敗する。
- 対処は、`settings.json` で上限を上げる(コスト増を承知で)か、重要語を先頭に・説明文を短く・スキル数を絞る。

---

スキルの `description` の書き方や、実際に発火しやすいスキルの組み立て方は、試行錯誤がそのまま品質に出ます。私が自分のスキルを整えるなかで溜めた具体的なレシピ(発火しやすい `description` の型、よく使うスキルの実例、設定のひな形)は、[Claude Code Skills 実践レシピ集](https://zenn.dev/yurukusa/books/a1b2c3d4e5f6g7)(¥500)にまとめています。

また、スキルや hook を含めた Claude Code の安全な初期設定は、無料で公開している [cc-safe-setup](https://github.com/yurukusa/cc-safe-setup) にまとめています。あわせてどうぞ。
