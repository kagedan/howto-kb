---
id: "2026-05-22-claudecode-mdmなしでも組織にclaudemdを配布する-01"
title: "[ClaudeCode] MDMなしでも組織にCLAUDE.mdを配布する"
url: "https://qiita.com/K5K/items/1440a3bcd977e0a95a68"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "qiita"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

## 概要

組織にてClaude CodeをTeamプランで利用していると、「メンバー全員に共通のCLAUDE.mdを配布したい」と思うようになるかと思います。

MDMのような端末管理配布の仕組みがあれば、CLAUDE.mdを組織のメンバー全員に配布することが可能です。ではMDMなどを利用できない場合はどうすればいいでしょうか？
CLAUDE.mdをどこかにアップロードしておき、それを個々でダウンロードするというのも1つの手段ですが、それだと本当に全員に行き渡っているかわかりませんし、組織の規模が大きければ必ずと言っていいほど漏れが生じます。

実はClaudeのMDMを使わずに、CLAUDE.mdを配布する仕組みがあります。

Teams プランの Managed Settings にある `claudeMd` というキーを使えば、組織共通の CLAUDE.md を全メンバーの Claude Code に配信できます。MDM などの端末管理基盤は不要で、Anthropic の管理コンソール上の操作だけで完結します。

この記事では、claudeMdについて解説していきます。

## 前提知識

### Managed Settings とは

Claude for Teams / Enterprise プランには「Managed Settings」という機能があります。これは、組織の管理者が Claude Code の設定（`settings.json` の内容）を組織配下のメンバー全員に配布できる仕組みです。

> Managed 設定：集中管理が必要な組織向けに、Claude Code は managed 設定の複数の配信メカニズムをサポートしています。すべて同じ JSON 形式を使用し、ユーザー設定またはプロジェクト設定でオーバーライドできません：

[Claude Code の設定](https://code.claude.com/docs/ja/settings)

Managed Settingsをユーザーに提供するには複数の方式があります。

- サーバー管理設定 : Anthropic のサーバーから Claude.ai 管理コンソール経由で配信される方式。端末側に何も置かなくてよく、管理画面で JSON を登録するだけで全メンバーに行き渡る
- MDM/OSレベル : macOS の managed preferences（`com.anthropic.claudecode` ドメイン）や Windows のレジストリ（`HKLM\SOFTWARE\Policies\ClaudeCode`）を経由する方式。Jamf / Kandji / Intune / グループポリシーといった端末管理基盤から配布する
- ファイルベース : OS ごとに決まったシステムディレクトリ（macOS: `/Library/Application Support/ClaudeCode/`、Linux/WSL: `/etc/claude-code/`、Windows: `C:\Program Files\ClaudeCode\`）に `managed-settings.json` を直接配置する方式。Ansible などの構成管理ツールでの配布が前提になる

ここで重要なのは、1つ目のサーバー管理設定（server-managed settings）が MDM（端末管理基盤）を必要としない点です。公式ドキュメントでも「集中管理が必要な組織向け」の選択肢として、端末側のセットアップを伴わない配信メカニズムとして紹介されています。

設定は Claude.ai の管理画面（製品 > Claude Code > 管理設定（settings.json））から「管理」ボタンで JSON を登録するだけで、各メンバーの Claude Code が起動時および1時間ごとのポーリングで自動的に受け取ります。
![Claude.ai 管理コンソールの管理設定（settings.json）画面](https://raw.githubusercontent.com/kskmats/blog-images/main/qiita/20260521-01/managed-settings-console.png)

> 補足: server-managed settings の利用には Claude for Teams / Enterprise プランと、Claude Code 2.1.38 以降（Claude for Teams の場合）が必要です。

### settings.json は配れる。では CLAUDE.md は？

permissions の deny リストや環境変数など、`settings.json` で表現できる設定は Managed Settings で配布できます。

ここで自然に湧く疑問が、「settings.json が配れるなら、CLAUDE.md も組織配布できるのでは？」というものです。

CLAUDE.md は Claude Code への永続的な指示書ですが、標準では個人単位かリポジトリ単位でしか持てません。「組織共通の CLAUDE.md」を正面から登録する欄は、一見すると見当たりません。

### 紛らわしいポイント: 組織設定の「組織の指示」欄

Anthropic の管理コンソールの「組織設定 > 組織とアクセス」には、「組織の指示」という欄があります。一見すると「ここに組織共通の CLAUDE.md を書けばよいのでは」と思えますが、これは Claude.ai（チャット製品）向けの設定であり、Claude Code には適用されません。

![組織設定の「組織の指示」欄](https://raw.githubusercontent.com/kskmats/blog-images/main/qiita/20260521-01/organization-instructions.png)

欄の説明文にも「組織全体のすべての会話に適用され、ユーザーの個人設定よりも優先されます」と書かれており、対象が「会話」、つまり Claude.ai のチャットセッションであることがわかります。Claude Code のセッションには反映されないので、組織共通の CLAUDE.md をここに書いても意図した動作にはなりません。

### Managed CLAUDE.md ファイルという方法（ただし MDM 必須）

公式には、組織共通の CLAUDE.md を配布する方法が2つ用意されています。

1つ目は「Managed CLAUDE.md ファイル」方式です。OS ごとに決まったパスに CLAUDE.md ファイルを置くと、Claude Code がそれを最上位の指示書として読み込みます。

- macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`
- Linux / WSL: `/etc/claude-code/CLAUDE.md`
- Windows: `C:\Program Files\ClaudeCode\CLAUDE.md`

ただしこの方式は、各メンバーの端末の固定パスにファイルを配置する必要があります。それを全社的に行うには MDM / Group Policy / Ansible といった構成管理の仕組みが前提になります。

MDM が導入済みの組織なら、これが素直な解です。しかし、MDM の導入・運用は組織によっては現実的に難しいケースも多いはずです。「CLAUDE.md を組織配布したいだけなのに、そのために MDM を入れるのか」となると、ハードルが高すぎます。

ここで登場するのが、2つ目の方法である `claudeMd` キーです。

## claudeMd について

### claudeMd キーとは

`claudeMd` は `settings.json` に書けるキーのひとつで、CLAUDE.md の内容を文字列としてそのまま設定に埋め込めるものです。

公式ドキュメント（[Claude Code の設定 - 利用可能な設定](https://code.claude.com/docs/en/settings#available-settings)）では次のように説明されています。

> (Managed settings only) CLAUDE.md-style instructions injected as organization-managed memory. Only honored when set in managed or policy settings and ignored in user, project, and local settings.

ざっくり訳すと「（Managed settings 専用）組織管理のメモリとして注入される CLAUDE.md 形式の指示。managed / policy settings に書いたときだけ有効で、user / project / local settings に書いても無視される」となります。

使い方はシンプルで、JSON の文字列値として CLAUDE.md の中身を書くだけです。

```json
{
  "claudeMd": "Always run `make lint` before committing.\nNever push directly to main."
}
```

改行は `\n` で表現します。Markdown もそのまま書けます。

### 仕様のポイント

| 項目 | 内容 |
|---|---|
| 値の型 | 文字列（複数行は `\n` 区切り、Markdown 可） |
| 有効な場所 | managed / policy settings のみ。user / project / local settings では無視される |
| 読み込み順 | Managed CLAUDE.md ファイルと同じ。user / project の CLAUDE.md より先に読み込まれる |

CLAUDE.md の読み込み順は、公式ドキュメントによると次のとおりです。

1. Managed policy（除外不可）
2. User instructions（`~/.claude/CLAUDE.md`）
3. Project instructions（`./CLAUDE.md`）
4. Local instructions（`./CLAUDE.local.md`）

`claudeMd` で配信した内容は 1 の Managed policy として扱われ、個人やプロジェクトの CLAUDE.md より先に読み込まれます。

### endpoint-managed settings はスコープ外

なお、Managed Settings には server-managed のほかに endpoint-managed（OS の固定パスに `managed-settings.json` を置く方式）もありますが、こちらは MDM 前提のため本記事では扱いません。

## 実際にやってみる

### 何を claudeMd に書くか

`claudeMd` は全セッションの最初に毎回読み込まれます。長すぎると毎回のコンテキストを圧迫し、指示の追従率も落ちます。公式でも CLAUDE.md は簡潔さが推奨されているので、全メンバー・全リポジトリで共通して効かせたい最小限の指示に絞るのがよいでしょう。

最小の例として、次のような内容を考えます。

```markdown
# 組織共通指示（Claude Code）

この指示は組織から配信されています。個人の ~/.claude/CLAUDE.md と矛盾する場合は本書を優先してください。

- 機密情報（認証情報・顧客情報など）をプロンプトや出力に含めない
- 本番環境への変更操作は実行前に必ず利用者に確認する
```

これを `claudeMd` の値にすると、改行を `\n` でエスケープして次のようになります。

```json
{
  "claudeMd": "# 組織共通指示（Claude Code）\n\nこの指示は組織から配信されています。個人の ~/.claude/CLAUDE.md と矛盾する場合は本書を優先してください。\n\n- 機密情報（認証情報・顧客情報など）をプロンプトや出力に含めない\n- 本番環境への変更操作は実行前に必ず利用者に確認する"
}
```

### Managed Settings に claudeMd を登録する

実際の登録は、Claude.ai の管理画面（Claude Code > 管理設定（settings.json））で行います。既存の設定 JSON に `claudeMd` キーを追加して保存するだけです。
保存後、各メンバーの Claude Code は起動時または1時間ごとのポーリングで新しい設定を受け取ります。すぐに反映を確認したい場合は Claude Code を再起動します。

`claudeMd` を初めて受け取った端末でセッションを開始すると、次のような確認画面が表示されます。

```text
Managed settings require approval

 Your organization has configured managed settings that could allow execution of arbitrary code or interception of your prompts and responses.

 Settings requiring approval:
   · claudeMd

 Only accept if you trust your organization's IT administration and expect these settings to be configured.

 ❯ 1. Yes, I trust these settings
   2. No, exit Claude Code
```

claudeMdの配布によるものなので、1のtrustを選択して問題ないです。

## あとがき

Managed Settings の `claudeMd` を使えば、MDM のような端末管理基盤がなくても、組織共通の CLAUDE.md を全メンバーの Claude Code に配信できます。Anthropic の管理コンソールだけで完結するため、Team プランの組織にとっては手軽にガバナンスを効かせる現実的な選択肢になります。

一方で、MDM がないと結局きびしい場面も残ります。
たとえば Hooks です。Managed Settings では Hooks の定義自体は配布できますが、Hook が実行するスクリプトの実体は各端末に存在している必要があります。そのスクリプトを全端末に配布するには、やはり MDM のような仕組みが要ります。
将来的に MDM のような端末管理の仕組みを入れられるのであれば、Managed CLAUDE.md ファイル方式や Hooks スクリプトの配布も視野に入り、統制の幅は広がります。入れられるなら入れたほうがよい、というのが正直なところです。

まずは `claudeMd` で組織共通の CLAUDE.md を配ってみる。そこから始めるのが、多くの Team プラン組織にとって現実的だと思います。
