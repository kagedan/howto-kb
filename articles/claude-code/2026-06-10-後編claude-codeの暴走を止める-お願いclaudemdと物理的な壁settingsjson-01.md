---
id: "2026-06-10-後編claude-codeの暴走を止める-お願いclaudemdと物理的な壁settingsjson-01"
title: "【後編】Claude Codeの暴走を止める ── 「お願い（CLAUDE.md）」と「物理的な壁（settings.json）」の二段構え"
url: "https://zenn.dev/hi_met/articles/f13088230d9e64"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "zenn"]
date_published: "2026-06-10"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

地方で独立系システムアーキテクトとして活動している、だいこん（H.I. MET Architect）です。副業で業務統合基盤「Weaver」（Redmine + Mattermost + Docker + Cloudflare Tunnel構成）を開発しています。

[前編](https://zenn.dev/hi_met) では「AIに渡すルールを `CLAUDE.md` に書く」という話をしました。

**でも、ここには正直に言わなければならないことがあります。**

> `CLAUDE.md` は"指示"であって、強制力はありません。

後編は「CLAUDE.mdだけでは止まらない操作を、settings.jsonで物理的にブロックする」話です。

そして今回は少しメタな話でもあります。この記事で紹介する設定ファイルは、**Claude Code自身と相談しながら最終化したもの**です。つまり「AIに自分を縛るルールを設計させた」。AIに「あなたが暴走しないためには、どんな制約が必要ですか？」と聞く。なかなかシュールな問いかけですが、返ってきた答えは非常に実用的でした。

---

## 実際のCLAUDE.mdに何を書いているか

WeaverのRedmineプロジェクトには、こんな構成のCLAUDE.mdが置いてあります。

### セッション開始時の必須確認（冒頭に置く）

```
## セッション開始時の必須確認
- 作業開始前に `MEMORY.md` と `ERRORS.md` を必ず読むこと。
- 「ここまで」と言われたら、現在の状態と次のステップを `MEMORY.md` に追記すること。
```

このブロックを**ファイルの一番上**に置くのがポイントです。Claude Codeは先頭から読むので、最初に目に入るものが優先的に効きます。

### 3フェーズの開発フロー（これが核心）

```
### Phase 1 — 設計提示と承認
要求を受け取ったら即座にコードを書かず、以下を提示してユーザーの承認を得る。
1. 実装アプローチ：どのようなロジックで実装・修正するか
2. 設計チェックリスト：デグレ・副作用を防ぐための確認項目

### Phase 2 — 自律実装
承認後、途中で止めずに一気に実装する。

### Phase 3 — 証拠ベースのレビュー
「成功しました」と断言せず、実際に動作した証拠を提示する。
- [ ] 目的・要件を完全に満たしているか？
- [ ] 既存データへの破壊的変更（デグレ）は起きていないか？
- [ ] 冪等性が担保されているか？
```

**Phase 3の「証拠ベース」が特に効きます。**

AIの「完璧です！」は非常に流暢です。流暢すぎて、最初はしばらく信じていました。「できた」と「できているかどうか確認した」は全然違う。人間でいえば、「資料もう送りました」と言いながら下書きフォルダに入れてある状態です。このチェックリストを置いてからは、ログ・差分・クエリ結果という"物証"を添えて返してくるようになりました。

**「冪等性が担保されているか」もリアルに刺さった一行です。**

Mattermostのデモユーザー投入で、同じスクリプトを2回流したら19人が38人になっていた——誰も採用した覚えがないのに人員が倍増していた。夢のような話だが、それはそれで困る。そういう事故を防ぐために、ユーザー作成前に `username` で重複チェックをするルールも個別に追加しています。

### Phase 1 の出力はどんな形か——実際の例

「Phase 1 で設計案を出して待つ」と書きましたが、実際にどんな形で返ってくるのかイメージしにくいかもしれません。

WeaverのRedmine–Mattermost SSO統合タスクで返ってきたPhase 1 の出力を、そのまま載せます。起動直後にClaude Codeが自律的にファイルを読み、DBを調査し、2つの実装アプローチをトレードオフ付きで提示してきた回答です（一部伏字あり）。

Phase 1 実例：Redmine–Mattermost SSO統合の調査報告（クリックで展開）

```
Read 1 file, ran 12 shell commands
Read ERRORS.md (30 lines)
Read MEMORY.md (69 lines)
Referenced file config/config.json
Read plugins/com.weaver.branding/webapp/dist/main.js (44 lines)
Read ../Redmine/nginx/conf.d/default.conf (75 lines)
Skills restored (task01_restore_logo)
```

調査結果をまとめます。VPS環境で「Redmineログイン起点 → 💬チャットボタン → MM自動SSOログイン」を実現するための前提条件が、思ったより整っていることが分かりました。

**調査で判明した重要事実**

1. VPS MattermostのSiteURLは`https://mattermost.met-architect.com`（docker-compose.ymlの環境変数で設定。config.json上の値`http://localhost:8080`は実行時に上書きされる古い表示値）。EnableOAuthServiceProvider=true、GitLabSettings/OpenIdSettingsは両方Enable=false（未設定）。
2. VPS MattermostにOAuthアプリは1件も登録されていない（oauthappsテーブル0件）。.envにある`MATTERMOST_OAUTH_CLIENT_ID/SECRET`（`xxxxxxxxxxxxxxx`等）はローカル専用で、VPSでは未登録＝無効な値。
3. 【最重要】MattermostコンテナはVPS上で既に`weaver-redmine_redmine-network`にも接続済み（デュアルホーム）。つまり `weaver-mattermost-mattermost-1 ⇔ redmine-prod:3000` はDockerネットワーク内で直接到達可能。Cloudflare Tunnelを経由しないサーバー間通信が既に成立する状態。
4. メールアドレスの不一致を再確認（VPS）:
   * Redmine: `weaver_sales_mgr` のデフォルトメールは `sales_mgr@weaver-demo.local`（weaver\_プレフィックスなし）
   * Mattermost: 同名ユーザーのメールは `weaver_sales_mgr@weaver-demo.local`（weaver\_プレフィックスあり、Redmineのloginと一致）
   * → Redmineのemailではなくloginの値を使えば、MM側の既存5アカウントとメールが一致する。
5. Cloudflare TunnelはCloudflareダッシュボード側で管理。ローカルにingress定義ファイルはなく、VPS側からはルーティング詳細は確認できない（ダッシュボード側はユーザー確認が必要）。

---

**実装アプローチ（2案）**

**案A: GitLab SSO方式で実装（推奨）**

RedmineプラグインにGitLab API互換の軽量OAuth2プロバイダー（/oauth/authorize, /oauth/token, /oauth/userinfo）を実装し、MattermostのGitLabSettingsで「Redmineでログイン」を有効化する。

* メリット: OAuth2 Authorization Code Flow + JSON REST APIのみで完結。JWT署名/検証が不要で実装・デバッグが容易。
* デメリット: GitLabSettingsはMM上「レガシー」扱いだが、機能自体は現行バージョンでも動作する。

**案B: OpenID Connect方式**

OIDCプロバイダー（IDトークンのJWT署名・JWKS公開等）を実装し、OpenIdSettingsで連携する。

* メリット: より「標準的」な構成。
* デメリット: JWT署名・検証ロジック、Discovery/JWKSエンドポイントの実装が必要で工数が大きく増える。デモ規模ではオーバースペック。

→ **案Aを推奨します。**

---

**設計チェックリスト**

**ロールバック手順**

* Redmine: 追加ファイル（新規コントローラ・ルート1行・.env追記分）を削除/コメントアウトして`docker restart`
* Mattermost: GitLabSettingsをEnable: falseに戻す（System Console操作、即時反映）
* ユーザー認証方式の変更: `migrate-auth`を逆方向（gitlab→email）で実行すれば復元可能
* チャットボタン: `mattermost_redirect_controller.rb`を1行戻すのみ

---

この方針（案A）で進めてよいか、ENV変数名やGitLabSettingsのエンドポイント構成について認識合わせができたら、Phase 2（実装）に入ります。

これがPhase 1 の出力です。「設計案を出して待つ」というルールを書いておくだけで、**調査・2案比較・チェックリスト・ロールバック手順**まで自律的に揃えて持ってくる。そして設計チェックリストには `idempotent` という言葉が自然に入っています——さっきの冪等性の話が、ここで出てくる、という構造です。

Phase 2 は、この出力に「案Aで進めてください」と一言返すだけで始まります。

### HARD STOP（取り返しのつかない操作）

```
## 取り返しのつかない操作 — 絶対停止
- ファイルの削除・移動・一括置換の前に必ず確認を取る。
- デプロイ・外部サービスへの送信・公開は明示的な許可が出るまで実行しない。
- 機密情報（APIキー・トークン等）をコード／コミットに含めない。
- 本番ブランチへの push は本番デプロイを意味する。明示的な許可なしに push しない。
```

「本番ブランチへのpushは本番デプロイを意味する」は、GitHub連携でCIが走るプロジェクトでは一行書いておくだけで事故がかなり減ります。

---

## しかし「お願い」には物理的な強制力がない

前述のルールは実際によく機能しています。でも文章はあくまで"文脈"です。**Claudeはこれを「守るべきルール」ではなく「参考にする情報」として処理します。** つまり私のCLAUDE.mdは、努力目標です。人間と同じです。

だから次のステップとして入れたのが、`.claude/settings.json` と `.claude/hooks/` です。

同じルールを、より強い方法で二重に持たせる——就業規則（CLAUDE.md）に加えて、金庫の鍵（settings.json）もかけておく、という考え方です。

---

## .claude/settings.json ── HARD STOPをJSONに翻訳する

CLAUDE.mdの「お願い」を、JSONの「強制」に翻訳したのがこれです。

```
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git branch*)",
      "Bash(docker compose logs *)",
      "Bash(docker compose ps)",
      "Bash(docker exec * mysql -u redmine -p* redmine -e *)"
    ],
    "ask": [
      "Write(**)",
      "Edit(**)",
      "Bash(docker compose up*)",
      "Bash(docker compose down*)",
      "Bash(docker compose restart *)",
      "Bash(docker exec -it*)",
      "Bash(git add*)",
      "Bash(git commit*)",
      "Bash(git push*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force*)",
      "Bash(git push * main*)",
      "Bash(git push origin main*)",
      "Bash(docker compose down -v*)",
      "Bash(docker compose down --volumes*)",
      "Bash(docker volume rm*)",
      "Bash(docker volume prune*)",
      "Bash(git reset --hard*)",
      "Bash(git clean -f*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/block-dangerous.sh" }
        ]
      }
    ]
  }
}
```

各 `deny` ルールはCLAUDE.mdのどのルールを翻訳したものか、対応を整理するとこうなります。

| settings.json のdenyルール | 対応するCLAUDE.mdのルール |
| --- | --- |
| `git push * main*` / `git push origin main*` | 「本番ブランチへのpushは本番デプロイを意味する」 |
| `git push --force*` | 「取り返しのつかない操作は絶対停止」 |
| `git reset --hard*` | 「既存データへの破壊的変更は起きていないか（Phase 3）」 |
| `git clean -f*` | 「ファイルの削除の前に必ず確認を取る」 |
| `rm -rf *` | 「ファイルの削除の前に必ず確認を取る」 |
| `docker compose down -v*` / `--volumes*` | 「デプロイコマンドは明示的な許可まで実行しない」 |
| `docker volume rm*` / `prune*` | DBデータ（永続ボリューム）の保護 |

`docker compose down -v` がdenyに入っているのは、Weaverの場合MySQLデータがDockerボリュームに乗っているためです。`-v` フラグひとつでデータが消えます。「良かれと思って環境をクリーンにしようとした」結果、MySQLのデータがまとめて昇天する。悪意はゼロ、被害は100%という、理想的に理不尽な事故です。

---

## .claude/hooks/block-dangerous.sh ── コマンドの中身まで見て止める

`deny` ルールはコマンド名単位のブロックですが、フックはコマンドの**文字列の中身**まで検査できます。終了コード `2` を返すとその操作がキャンセルされます。

設計で一番悩んだのは**入力の受け取り方**です。Claude Codeがフックへのツール入力を渡す方法は、バージョンによって環境変数（`CLAUDE_TOOL_INPUT`）か標準入力（stdin）かが変わる可能性があります。そのため両方に対応しています。

```
#!/usr/bin/env bash
# Weaver — 危険コマンドブロックフック (PreToolUse / Bash)

set -uo pipefail

# --- 入力取得（環境変数 + stdin 両対応）---
INPUT="${CLAUDE_TOOL_INPUT:-}"

if [ ! -t 0 ]; then
  STDIN_DATA="$(timeout 1 cat 2>/dev/null || true)"
  INPUT="${INPUT} ${STDIN_DATA}"
fi

if [ -z "${INPUT// /}" ]; then
  echo "⚠️  [block-dangerous] 入力を取得できませんでした。フックが機能していない可能性があります。" >&2
  exit 0  # 誤検知での全停止を避けて通す
fi

# --- 危険パターン定義 ---
DANGEROUS_PATTERNS=(
  'rm +-[a-zA-Z]*r[a-zA-Z]* '          # rm -rf / -fr / -r などの再帰削除
  'rm +-[a-zA-Z]* +\.env'              # rm -f .env など
  '> +\.env'                           # > .env（上書き空化）
  'DROP +TABLE'
  'DROP +DATABASE'
  'TRUNCATE'
  'DELETE +FROM '                      # WHERE句の有無に関わらず一律ブロック（後述）
  'UPDATE +[a-zA-Z_."`]+ +SET '
  'rake +db:drop'
  'rake +db:reset'
  'compose +down +.*-v'
  'compose +down +.*--volumes'
  'docker +volume +rm'
  'docker +volume +prune'
  'git +reset +--hard'
  'git +clean +-[a-zA-Z]*f'
  'git +push +.*--force'
)

# --- 検査 ---
for pat in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$INPUT" | grep -qiE "$pat"; then
    echo "🚫 [block-dangerous] 危険なパターンを検知しました。操作をキャンセルします。" >&2
    echo "   検知パターン : ${pat}" >&2
    echo "   コマンド内容 : ${INPUT}" >&2
    echo "   本当に実行が必要な場合は、手動で実行してください。" >&2
    exit 2
  fi
done

exit 0
```

**「DELETE FROM」と「UPDATE SET」を一律ブロックにした理由**

WHERE句の有無を正規表現で正確に判定するのは思ったより困難です——複数行・サブクエリ・改行のゆらぎで判定ロジックがすぐ破綻します。だから**安全側に倒して一律ブロック**にしました。正当なSQLもここで止まりますが、その場合は内容を確認してから手動実行すればいい。止まって困る場面より、止まらなくて困る場面の方がはるかに痛い。これはClaude Codeと設計を議論した末に出た結論です。

---

## （オプション）MEMORY.md / ERRORS.md でセッションをまたぐ

Claude Codeは毎セッションまっさらな状態で始まります。昨日あれだけ一緒に考えたのに「はじめまして」です。毎朝記憶を完全リセットして出勤してくる同僚です。非常に誠実なのに少し虚しい。引き継ぎに使う2ファイルをプロジェクト直下に置き、CLAUDE.md冒頭で「セッション開始時に必ず読む」と指示します。

```
# MEMORY.md（引き継ぎ記録）
## 不変の事実
- 本番URL: https://weaver.met-architect.com
- デプロイ: main ブランチへのpush = 本番に即反映

## 進行中タスク
- [ ] タスク3: かんばん空ステータス「0」不具合調査
- [ ] タスク4: ファイル画面404エラー調査

## 決定事項ログ
<!-- 日付付きで追記 -->
```

```
# ERRORS.md（失敗ログ）
## [日付] 試みたこと（失敗）
- 操作内容 / 失敗の症状 / 原因 / 結論（次回この手順を試みないこと）
```

---

## まとめ

前編と後編を合わせると、安全に自律実装を任せるための層はこうなります。

| 役割 | ファイル | 効力 |
| --- | --- | --- |
| 応答ルール・作業規約 | `CLAUDE.md` | "お願い"（強く効くが強制ではない） |
| 権限（allow/deny/ask） | `.claude/settings.json` | ツール単位の物理的ブロック |
| コマンド内容の検査 | `.claude/hooks/block-dangerous.sh` | 文字列レベルでの即時キャンセル |
| セッション引き継ぎ | `MEMORY.md` / `ERRORS.md` | 文脈の継続 |

CLAUDE.mdで「こう動いてほしい」と伝え、settings.jsonで「これは破れない」と担保する。そしてhooksで「コマンドの中身まで見て止める」。この三層が揃うと、大胆に任せても事故りにくい開発体制になります。

この「ルールを決めてAIを動かす」考え方は、私が開発している業務統合基盤 **Weaver** の作り方そのものでもあります。地方のシステムアーキテクトとして、これからも「ルールでAIを乗りこなす」知見を発信していきます。
