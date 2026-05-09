---
id: "2026-05-09-skillsの-context-圧迫は1未満-claude-code-v21129-の-skillo-01"
title: "skillsの context 圧迫は1%未満? — Claude Code v2.1.129 の skillOverrides と --plugin-url 使いどころ整理"
url: "https://note.com/ai_eng_tech/n/na8badce4d93d"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "note"]
date_published: "2026-05-09"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

Claude Code v2.1.129 がリリースされました。

目玉は **skillOverrides** 設定の有効化と、**--plugin-url** フラグの追加です。

スキルを多く運用していると、「これだけ増えると context が圧迫されるんじゃないか」という不安が出てきます。

実測してみると、全コンテキストに対する割合は1%にも満たないことが多く、ほとんど無視できる量でした。

この記事では実測値をもとに、**skillOverrides** と **--plugin-url** を「いつ使うべきか・使わなくていいか」を整理します。

## v2.1.129 で変わった2つの機能

  

公式 CHANGELOG では4つの変更が並んでいます。

そのなかで日常運用に効くのは **skillOverrides** と **--plugin-url** の2つです。

残り2つは小さな改善です。

Gateway model discovery は **CLAUDE\_CODE\_ENABLE\_GATEWAY\_MODEL\_DISCOVERY=1** でオプトイン化、Hooks と Bash には **effort.level** JSON フィールドと **$CLAUDE\_EFFORT** 環境変数が渡るようになりました。

詳細は [公式 CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) で確認できます。

ここからは2つの主要機能を、運用視点で見ていきます。

## skillOverrides の仕様 — 4値の対照表

**skillOverrides** は **~/.claude/settings.json** の **skillOverrides** キーで設定します。

各スキルに対して **"on"** / **"name-only"** / **"user-invocable-only"** / **"off"** の4値を割り当てる形です。

公式 docs を整理すると、各値の振る舞いは次の通りです。

* **"on"（default）** — Claude にリスト → 名前+description / ／メニュー → 表示
* **"name-only"** — Claude にリスト → 名前のみ（description は context から削除）/ ／メニュー → 表示
* **"user-invocable-only"** — Claude にリスト → 非表示（自動起動禁止）/ ／メニュー → 表示
* **"off"** — Claude にリスト → 非表示 / ／メニュー → 非表示

設定ファイルへの最小例は次の通りです。

```
{
  "skillOverrides": {
    "morning-routine": "user-invocable-only",
    "deploy": "off"
  }
}
```

注意点が2つあります。

1つ目は、設定に書いていないスキルは自動的に **"on"** 扱いになるという点です。

2つ目は、プラグインスキル（**pr-review-toolkit** など）は **skillOverrides** の対象外で、**/plugin** 側で管理する必要があるという点です。

不在のスキルは **"on"**、プラグインは別管理。

この2点を押さえれば、**skillOverrides** の挙動は迷わないはずです。

## 実測してみるとどうか — context はほぼ圧迫されない

では実際、ある運用環境で context をどれくらい使っているか測ってみました。

各 **SKILL.md** の frontmatter から **description** と **when\_to\_use** を抽出して、合計文字数を測りました。

結果はこうです。

* スキル数: 35件（プラグイン除く）
* **description** + **when\_to\_use** 合計: 数千文字程度
* 1Mコンテキストウィンドウに対する比率: 1%未満
* デフォルトバジェット 8,000 chars に対しては半分強

1Mコンテキスト基準ではごくわずかしか使っておらず、**CLAUDE.md** や **rules/** のほうがずっと重い計算です。

一方、デフォルトバジェット 8,000 chars に対しては半分強を使っています。

8,000 chars はデフォルト fallback の値で、**SLASH\_COMMAND\_TOOL\_CHAR\_BUDGET** 環境変数で上書きできます。

スキル数が60を超えてくると **description** が切り詰められて Claude がスキルを呼び損ねる、という公式アナウンスがあります。

数十件規模なら半分以上の余裕があるので、現時点では問題なしです。

計測スクリプトはこんな形でした。

```
import re
from pathlib import Path

base = Path.home() / ".claude/skills"
total = 0
for skill_md in base.glob("*/SKILL.md"):
    text = skill_md.read_text()
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m: continue
    desc = re.search(r"^description:\s*(.+?)(?=\n[a-zA-Z_-]+:|\Z)", m.group(1), re.MULTILINE | re.DOTALL)
    wtu = re.search(r"^when_to_use:\s*(.+?)(?=\n[a-zA-Z_-]+:|\Z)", m.group(1), re.MULTILINE | re.DOTALL)
    combined = ((desc.group(1) if desc else "") + " " + (wtu.group(1) if wtu else "")).strip()[:1536]
    total += len(combined) + len(skill_md.parent.name) + 5

print(f"合計: {total:,} chars")
```

5分で書けるスクリプトで、自分の環境を一度測っておくことをおすすめします。

「context が圧迫されているかも」という漠然とした不安が、数字を見ると消えます。

## skillOverrides の正しい用途 — 「誤起動防止」として使う

実測してわかったのは、**skillOverrides** は context 節約のための機能ではない、ということです。

全体に対して1%未満。

数字で見ると、context 節約を目的に **skillOverrides** を使う必要はほぼないとわかります。

では何のためにあるのか。

主な用途は「Claude が空気を読まずに自動起動するスキル」を止めることです。

たとえば **morning-routine** というスキルを持っていると、朝以外の時間にも「ルーティンを実行しますか？」と Claude が起動候補に挙げてくる、というケースがあり得ます。

この場合、**morning-routine** を **"user-invocable-only"** にすると、自分が **/morning-routine** と打つまで Claude は起動しません。

```
{
  "skillOverrides": {
    "morning-routine": "user-invocable-only",
    "weekly-planning": "user-invocable-only"
  }
}
```

実測してみた結果、現状の判断は「全部 default のまま」です。

理由は2つあります。

1つ目は、35スキルでも誤起動が頻発していないこと。

2つ目は、**description** にはトリガー条件を書いてあるので、Claude が誤って呼ぶケースが少ないこと。

もし「このスキルが頻繁に誤発火する」と感じたら、そのスキルだけ **"user-invocable-only"** にする、というピンポイント対応が筋がよさそうです。

## --plugin-url の使い方 — チーム配布の新選択肢

もう一方の主役、**--plugin-url** は、プラグインの zip を URL から読み込むフラグです。

```
claude --plugin-url https://example.com/my-plugin.zip
```

この機能の重要な制約は「そのセッション限り」だという点です。

永続インストールではなく、起動したセッションが終わるとプラグインも消えます。

なので、プラグインマーケットプレイスへの登録が不要で、URL さえ知っていれば誰でも試せます。

実用シナリオをいくつか挙げます。

* GitHub Releases に zip を置いて、社内勉強会で URL 共有
* CI 環境で「このジョブだけ特定のスキル群を一時注入」
* 設定リポジトリを zip にエクスポートして、新メンバーに「とりあえずこれで」と渡す

個人スキル群を Git で管理している場合、Releases に zip として置いておけば、別マシンで **claude --plugin-url** で取り込めるのは便利だと感じました。

注意点としては、URL が落ちたらセッションがブロックされる可能性があること、プライベートリポジトリの認証は別途仕組みを考える必要があることが挙げられます。

公開できる範囲のスキル群だけを配布、と割り切るのが現実的です。

## まとめ — あなたは今すぐ使うべきか

そもそもほとんどの人はスキルを大量運用しないので、skillOverrides はごく一部のヘビーユーザー向けの機能です。普通に5〜10個のスキルで使っているうちは、この設定はまず不要と考えてよいです。

最後に、判断軸を整理します。

* スキルが10〜20件程度で、誤起動も気にならない → 何もしなくてOK
* 特定のスキルが Claude に頻繁に誤発火される → そのスキルだけ **"user-invocable-only"** に
* スキル数が60件を超えてきた → **"name-only"** 化や **SLASH\_COMMAND\_TOOL\_CHAR\_BUDGET** の引き上げを検討
* チームでスキルを共有したい → **--plugin-url** で zip 配布を試す

実測値（1%未満）と運用感の両面から、「現状維持」が現実的な選択です。

数字で判断すると「設定しないという判断」が自信を持ってできるようになります。

スキル運用を始めたばかりで「context 大丈夫かな」と不安に感じている人は、まず一度自分の環境を測ってみてください。

1分で済む計測スクリプトを動かすだけで、漠然とした不安が消えるはずです。

## 参考
