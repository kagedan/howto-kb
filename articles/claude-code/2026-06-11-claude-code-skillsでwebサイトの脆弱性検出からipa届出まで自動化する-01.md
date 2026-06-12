---
id: "2026-06-11-claude-code-skillsでwebサイトの脆弱性検出からipa届出まで自動化する-01"
title: "Claude Code SkillsでWebサイトの脆弱性検出からIPA届出まで自動化する"
url: "https://zenn.dev/watab2000_tech/articles/7e7c55329bb160"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "OpenAI", "JavaScript", "zenn"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

IPA通報代行の人です。  
多忙のため、手が足りません。だから、私のコピーを使ってください。

```
https://example.com を監査して、脆弱性をIPAに報告して。
```

# はじめに

Webサイトのセキュリティ確認をしていると、意外と手作業が多いことに気づきます。

* 対象サイトから JavaScript を集める
* 静的に危険なパターンを探す
* 秘密情報や Webhook URL の露出を確認する
* 見つかった内容を整理する
* 必要なら IPA への届出文面を作る

ひとつひとつは難しくなくても、毎回同じ手順を思い出しながら実行するのは手間です。  
そこで、Claude Code Skills として一連の作業をまとめた `ipagent` を作りました。

<https://github.com/WATab2000/ipagent>

`ipagent` は、Webサイトの JavaScript 取得、静的脆弱性解析、IPA への届出メール文面生成までを Claude Code 上で扱えるツールセットです。

# 何ができるか

`ipagent` は 4 つの Claude Code Skill で構成されています。

| スキル | 役割 |
| --- | --- |
| `ipagent-site-mirror` | URL を指定してサイトの JS ファイルを再帰取得する |
| `ipagent-js-vuln-scan` | ローカルの JS を静的解析して脆弱性・秘密情報漏洩を検出する |
| `ipagent-audit-site-js` | JS 取得と監査を順番に実行するオーケストレーター |
| `ipagent-ipa-report` | 監査結果から IPA 届出メールの文面を生成する |

主なユースケースは、次のような流れです。

1. 対象サイトの JS を取得する
2. 取得した JS を静的解析する
3. Webhook URL、API キー、XSS 候補、postMessage の origin 検証漏れなどを確認する
4. 必要に応じて IPA 届出用の文面を生成する

# なぜ Claude Code Skills にしたか

セキュリティ確認では、単純なコマンド実行だけでなく、判断が必要な場面が多くあります。

たとえば、`innerHTML` が出てきたからといって、それだけで XSS とは言えません。  
React や Next.js などのライブラリ内部実装であれば誤検知の可能性があります。  
一方で、`location.search` や `postMessage` 由来の値がアプリ側コードで DOM に流れているなら、詳しく見る必要があります。

このような「検索して終わり」ではない作業は、エージェントに手順と判断基準を持たせると扱いやすくなります。

`ipagent-js-vuln-scan` では、単に危険そうな文字列を grep するだけでなく、次のような観点をスキルに書いています。

* 手書きアプリコードと minify されたライブラリを見分ける
* Slack / Discord Webhook はクライアント露出時点で重大として扱う
* Google Forms / Firebase など公開前提のキーを誤報しない
* XSS シンクはユーザー入力の流入があるかを確認する
* postMessage は `event.origin` の検証有無を見る
* 既知 CVE は推測で断定せず、必要に応じて裏取りする

つまり、手順書とレビュー観点を Claude Code の実行可能な知識として持たせています。

# セットアップ

必要なものは以下です。

`wget` がある場合は再帰取得に `wget` を使います。  
ない場合は `curl` ベースのフォールバック手順を使う想定です。

リポジトリを clone します。

```
git clone https://github.com/WATab2000/ipagent.git
cd ipagent
```

Claude Code Skills は `.claude/skills/` に配置されています。

```
.
├── .claude/
│   └── skills/
│       ├── ipagent-site-mirror/
│       ├── ipagent-js-vuln-scan/
│       ├── ipagent-audit-site-js/
│       └── ipagent-ipa-report/
├── htmls/
└── mails/
```

`htmls/` は取得した JS、`mails/` は生成した IPA 届出文面の保存先です。  
どちらも `.gitignore` しています。

# 使い方

## 自然言語で依頼する

Claude Code のチャットで、普通に日本語で依頼できます。

```
https://example.com を監査して
```

```
https://example.com の JS を取得して
```

スキルの説明文にトリガーとなる自然言語を入れているため、Claude Code が該当スキルを選びやすくなっています。

## スラッシュコマンドで実行する

直接スキルを呼び出すこともできます。

サイトの JS 取得と監査を一括で行う場合:

```
/ipagent-audit-site-js https://example.com
```

JS だけ取得する場合:

```
/ipagent-site-mirror https://example.com
```

取得済みフォルダを解析する場合:

```
/ipagent-js-vuln-scan ./htmls/example.com-js
```

監査結果から IPA 届出文面を作る場合:

届出文面は次のようなパスに出力されます。

```
mails/ipa-vuln-report_<ホスト名>_<日付>.txt
```

実際の送付は自動では行いません。  
届出者本人が IPA の所定窓口から送付します。

# JS 取得で気をつけたこと

Webサイトの JS を集めるだけでも、実サイトではいくつか落とし穴があります。

特に Next.js や SPA では、JS が起点 URL と別のドメインや CDN から配信されることがあります。  
そのため `ipagent-site-mirror` では、先に HTML の `<script src>` を見て、JS の配信元ドメインを確認する手順にしています。

また、JS ファイルにはキャッシュ対策のクエリ文字列が付くことがあります。

この場合、単純な `--accept="js,mjs"` では取りこぼすことがあります。  
そこで `wget` では次のように正規表現で受ける方針にしています。

```
wget \
  --recursive \
  --level=2 \
  --accept-regex='\\.(js|mjs)(\\?.*)?$' \
  --span-hosts \
  --domains="<起点ホスト>,<CDNホスト...>" \
  --restrict-file-names=windows \
  --wait=1 --random-wait \
  --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  --directory-prefix=<保存先> \
  <URL>
```

`--wait=1 --random-wait` も付けて、対象サイトへの負荷を抑えるようにしています。

# 静的解析で見るポイント

`ipagent-js-vuln-scan` では、主に次の観点を確認します。

## 秘密情報の露出

クライアント JS に秘密情報が含まれている場合、影響が大きくなります。  
特に Slack / Discord の Incoming Webhook URL は、見つかった時点で即時 Revoke を検討すべきです。

チェック対象の例:

* Slack / Discord Webhook URL
* GitHub token
* Stripe key
* AWS access key id
* OpenAI API key
* 汎用的な `apiKey`, `secret`, `token`, `password` 代入

一方で、Google Forms や Firebase の Web API key のように公開前提の値もあります。  
文字列だけで判断せず、文脈を見ることを重視しています。

## XSS 候補

危険な DOM 操作を探します。

* `innerHTML`
* `outerHTML`
* `document.write`
* `insertAdjacentHTML`
* `eval`
* `new Function`
* `dangerouslySetInnerHTML`

ただし、これらが出てきただけでは脆弱性とは言えません。  
アプリ側コードで、URL パラメータや `postMessage` 由来の値が流れ込んでいるかを確認します。

## postMessage の origin 検証

`message` イベントを受け取るコードでは、`event.origin` を検証しているかを見ます。  
受信データを DOM 反映、画面遷移、`eval` などに使っている場合は重要度が上がります。

## 依存ライブラリの既知 CVE

JS 内にバージョン情報が含まれている場合、ライブラリ名とバージョンを確認し、既知 CVE の有無を調べます。  
ただし、バージョン文字列だけでは所属ライブラリを誤認しやすいため、周辺コードを読んでから判断します。

# IPA 届出文面の生成

`ipagent-ipa-report` は、監査結果を IPA の「ウェブアプリケーション脆弱性関連情報届出様式」に沿って整形します。

このスキルでは、特に個人情報の扱いに注意しています。

* 届出者の氏名・メールアドレスはユーザー本人に必ず確認する
* 環境情報やログイン情報から推測して埋めない
* 「運営者に知らせてもよい」か「IPA とのみやりとり」かを確認する
* 「IPA とのみ」の場合、本文側に届出者を特定できる記述が混ざらないよう確認する
* 証拠ファイルのプロパティに個人情報が残る可能性も注意喚起する

セキュリティツールは、検出することだけでなく、報告時に余計な情報を混ぜないことも重要です。

# 実装してよかったこと

一番よかったのは、調査手順を毎回思い出さなくてよくなったことです。

「JS を取る」「grep する」「誤検知を減らす」「報告文面にする」という作業は、慣れていても細かい判断が多くあります。  
Claude Code Skills に手順と判断基準を書いておくと、次回以降は自然言語で呼び出せます。

また、スキルを分割したことで役割も明確になりました。

* 取得だけしたいなら `ipagent-site-mirror`
* 解析だけしたいなら `ipagent-js-vuln-scan`
* 一括でやりたいなら `ipagent-audit-site-js`
* 届出文面にしたいなら `ipagent-ipa-report`

小さなスキルを組み合わせる構成にしたことで、改善もしやすくなっています。

# 今後やりたいこと

今後は次のあたりを改善したいです。

* HTML 内インライン script の抽出精度を上げる
* 取得した JS のライブラリ判定をもう少し構造化する
* 監査結果を JSON と Markdown の両方で出力する
* IPA 届出文面生成時の入力チェックをさらに厳密にする
* 誤検知・既知の安全パターンのナレッジを増やす

# まとめ

`ipagent` は、Webサイトの JavaScript 取得から静的脆弱性解析、IPA 届出文面の生成までを Claude Code Skills としてまとめたツールセットです。

単なるコマンド集ではなく、誤検知を減らすための判断基準や、届出時の個人情報取り扱いまでスキルに含めています。

セキュリティ確認は、検出だけでなく、再現性のある手順と適切な報告が重要です。  
Claude Code Skills は、その手順を実行可能な形で残す手段として相性が良いと感じました。

リポジトリはこちらです。

<https://github.com/WATab2000/ipagent>
