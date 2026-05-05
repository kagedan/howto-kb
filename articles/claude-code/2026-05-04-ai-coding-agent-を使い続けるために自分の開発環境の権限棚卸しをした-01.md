---
id: "2026-05-04-ai-coding-agent-を使い続けるために自分の開発環境の権限棚卸しをした-01"
title: "AI coding agent を使い続けるために、自分の開発環境の権限棚卸しをした"
url: "https://zenn.dev/yamk/articles/ai-agent-permission-inventory"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

Claude Code や Codex を毎日使うようになって、開発の速度はかなり上がりました。

実装を頼む。テストを回してもらう。差分を見てもらう。commit して push して PR まで作ってもらう。

かなり便利です。

ただ、ふと考えるとこれは単なる補助ツールではありません。自分のローカル環境で shell を実行し、repository を書き換え、GitHub に push できる実行主体です。便利な相棒の顔をしていますが、鍵束を持って作業部屋に入ってきています。

つまり、AI coding agent は「便利なチャット」ではなく、かなり強い権限を持った開発者プロセスとして扱った方がよさそうです。

そこで、自分の環境で AI coding agent の権限棚卸しをしてみました。

棚卸しというと急に経理っぽいですが、やることはもっと素朴です。「この agent、どの鍵を持ってるんだっけ」を見直すだけです。

## きっかけ

最近の supply chain 攻撃を見ていると、本番サーバーだけが狙われているわけではありません。

むしろ、開発者の手元、CI runner、package install 時の lifecycle script、notebook、GitHub token、npm / PyPI token などが狙われています。

そう思ったのは、いくつかの incident で狙われた場所がかなり似ていたからです。

* SAP CAP / Cloud MTA 関連の npm package compromise では、`preinstall` script が追加され、package install 時に外部 binary を取得して実行する経路が作られていました。Socket は、影響を受けた developer machine や CI/CD 環境の token / credential rotation と CI log review を推奨しています。
* PyPI の `lightning` compromise では、package import を起点に payload が動き、repository、environment variable、cloud secret、GitHub token などを狙う挙動が報告されています。CI/CD logs や developer machine の audit も推奨されています。
* Elementary OSS Python CLI v0.23.3 の incident では、GitHub Actions workflow の script injection が悪用され、PyPI release と Docker image publish に至りました。公式 report でも、影響環境でアクセス可能だった `.env`、API token、warehouse credential、cloud key などの rotation が案内されています。

つまり、「package を入れた」「CI が動いた」「開発用 CLI を実行した」という開発時の操作が、そのまま credential exposure につながるケースが現実にあります。

AI coding agent は、まさにその開発者環境の中で動きます。

そして自分の使い方では、agent は単にコードを提案するだけではありません。次のような操作まで任せることがあります。

* repository のコードを読める
* ファイルを書き換えられる
* `.github/workflows/**` を変更できる
* shell command を実行できる
* dependency install で外部ネットワークに出られる
* `.env` や開発用 API key に触れうる
* commit / push / PR 作成ができる

もちろん、これは便利さの源泉でもあります。

問題は「AI agent を使うか使わないか」ではなく、**どこまで任せてよいかを自分で把握しているか**です。

参考:

## 自分の前提

自分の使い方はだいたいこうです。

* メインは Claude Code
* Codex もよく使う
* レビューは Codex と CodeRabbit を使うことが多い
* browser-use は調査や開発中の動作確認でたまに使う
* GitHub は個人 repo だけでなく organization repo も触る
* Claude Code / Codex には commit / push / PR 作成まで任せることがある
* 開発用の `.env` には Convex、Clerk、AI service の API key が入っている
* 本番用 secret はローカルには置いていない
* browser-use は基本的には専用ブラウザ環境のはずだが、正確な権限範囲はまだ確認中

ここまで書くと分かりますが、かなり便利に使っている一方で、権限もそれなりに渡しています。

特に大きいのは、Claude Code / Codex に push まで任せていることです。

一人開発だと「自分しかいないからまあいいか」となりがちですが、AI agent が自分の開発者権限で動けるなら、そこには最低限のガードが必要です。

一人開発の「自分しかいない」は便利な言葉ですが、だいたい未来の自分も巻き込まれます。

## まず権限表を作った

最初にやったのは、難しい設定ではなく表を作ることです。

ただし、この表は精密なリスク評価ではありません。目的は「これで安全です」と言うことではなく、**どの tool がどの境界を越えられるのかを見える化する**ことです。

表を作るだけで安全になるなら、世の中のだいたいの問題はスプレッドシートで解決しています。もちろん、そうはなりません。

| Tool | 主用途 | できること | 境界になりそうなもの | 今回の扱い |
| --- | --- | --- | --- | --- |
| Claude Code | 実装・修正 | repo write / shell / commit / push / PR | Actions workflow、`.env`、network、main 反映 | メインなので、危険ファイルと main 反映だけ一拍置く |
| Codex | 実装・修正・レビュー | repo write / shell / commit / push / PR | Actions workflow、`.env`、network、main 反映 | Claude Code と同じ扱い |
| CodeRabbit | レビュー | GitHub 上で repository を読む | GitHub app の読み取り範囲 | 読み込みのみなので、今回は大きな論点にしない |
| browser-use | 調査・動作確認 | ブラウザ上の操作 | ログイン済みセッション | 低頻度なので、まず権限範囲を確認する対象にする |

この表で見たいのは、細かい点数ではありません。

見たいのは、危ない組み合わせです。

* repo write と push ができる tool は、実装だけでなく repository の状態を変えられる
* Actions workflow を変更できる tool は、CI/CD で何を実行するかにも触れうる
* `.env` に触れうる tool は、開発用とはいえ API key や token の扱いに関係する
* network に出られる tool は、dependency install や外部 API 呼び出しを実行できる
* browser-use は repository ではなく、ログイン済みブラウザセッションの権限を見る必要がある

逆に、この表だけでは分からないこともあります。

* 実際にどの secret が読まれたか
* どの command が危険か
* どの GitHub token scope が付いているか
* どの repository に branch protection が入っているか
* browser-use がどのログイン状態で動いているか

なので、この表は監査結果というより、次に確認する場所を決めるための地図です。

自分の場合、この表から見る場所はかなり絞れました。

1. Claude Code / Codex は push までできるので、main 反映前だけ一拍置く
2. `.github/workflows/**`、deploy、auth、secret 周りは危険ファイル扱いにする
3. browser-use は低頻度なので、まずログイン状態がどうなっているかだけ確認する

こうして見ると、自分の場合は Claude Code と Codex が中心です。

この2つは、便利さもリスクも大きいです。repo を書けるし、shell も使えるし、push もできる。さらに `.env` が作業ディレクトリにあれば、開発用とはいえ API key に触れる可能性があります。

CodeRabbit はレビュー用途です。自分の設定では GitHub 上の読み込みのみで、ローカル shell を実行する主体ではありません。そのため、今回は大きな論点にしません。

browser-use は少し別枠です。コードを書くというより、ログイン済みブラウザで何ができるかが論点になります。ただ、自分はたまにしか使っていないので、この時点では「まずログイン状態を確認する」くらいに留めました。

## 一人開発なので、重い統制は続かない

ここで悩んだのが、GitHub の branch protection や review rule をどこまで入れるかです。

チーム開発なら、main branch への direct push 禁止、required review、required status checks などを入れるのが自然です。

ただ、自分は基本的に一人開発です。

一人開発で重い review rule を入れすぎると、たぶん続きません。自分で作ったルールに自分で詰まって、面倒になって外す未来が見えます。

なので目的を変えました。

「レビュー人数を増やす」のではなく、**AI agent や自分が勢いで危険な変更を通してしまうのを防ぐ**ことを目的にします。

一人開発に必要なのは、企業っぽい統制ではなく、一拍置くための軽いガードです。

自分ひとりの開発に、いきなり監査部門みたいな運用を持ち込んでも続きません。

## 一人開発向けのルール

自分向けの v0 ルールはこうしました。

### 通常の実装

* Claude Code / Codex に実装、テスト、commit、push まで任せてよい
* ただし作業は feature branch で行う
* main への反映前に差分確認を挟む
* organization repo では PR 経由を基本にする

### main branch

* main 直 push は原則しない
* 緊急修正だけ例外
* 例外時も `git diff` / `git log` を確認してから push する
* main への force push と branch deletion は禁止する
* feature branch では rebase 後の `--force-with-lease` は許可する

### 危険ファイル

以下を変更する場合は、AI 任せにせず自分で見ることにしました。

* `.github/workflows/**`
* `package.json`
* lockfile
* `Dockerfile`
* `docker-compose.yml`
* `.env*`
* deploy / hosting 設定
* auth / billing / webhook 周り

特に `.github/workflows/**` は強いです。

GitHub Actions workflow を変更できるということは、CI 上で何を実行するかを変えられるということです。repository や organization の設定によっては、secrets、OIDC、package publish、deploy にも関わります。

なので workflow 変更は、普通の UI 修正や README 修正とは別扱いにします。

### secrets

* 本番 secret はローカルに置かない
* 開発用 `.env` も secret として扱う
* `.env` を agent に読ませる前提にしない
* AI service の API key には利用上限を設定する
* `.env.example` にはキー名だけを書く
* `.env` が `.gitignore` されていることを確認する

開発用だからといって、漏れてよいわけではありません。

Convex や Clerk の dev key でも、漏れると開発環境のデータや認証設定に影響する可能性があります。AI service の key なら、コストにも直結します。

本番 secret を置いていないのはよい状態ですが、dev secret も雑に扱わない方がよいです。

### Claude Code の設定に落とすなら

「一拍置く」を運用だけにすると忘れそうなので、Claude Code では設定にも落とせます。

Claude Code の docs では、`.claude/settings.json` や `.claude/settings.local.json` に `permissions` を書けます。自分用に試すなら、commit しない `.claude/settings.local.json` から始めるのがよさそうです。

たとえば、こんな感じです。

```
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ],
    "ask": [
      "Edit(/.github/workflows/**)",
      "Edit(/Dockerfile)",
      "Edit(/package.json)",
      "Bash(git push *)",
      "Bash(npm publish *)",
      "Bash(pnpm publish *)"
    ]
  }
}
```

これでやりたいことは、次の2つです。

* `.env` や `secrets/**` の読み取りはブロックする
* workflow、Dockerfile、package metadata、push / publish は確認を挟む

ただし、これは万能ではありません。Claude Code docs でも、`Read(./.env)` の deny は Claude Code の built-in file tools に効くもので、Bash subprocess の `cat .env` までは防げないと説明されています。

なのでこれは「これで完全に安全」ではなく、普段の作業でうっかり踏みにくくするためのガードです。厳密にやるなら sandbox など OS 側の制限も必要になります。

このあたりは、玄関に鍵をかける話に近いです。壁を金庫にする話ではありません。

この考え方は、PreToolUse hooks でも補えます。

たとえば、`.env` のような機密ファイルや `.github/workflows/**` のような危険ファイルに触る操作を、tool 実行前に検査して止める、または確認に回す、という考え方です。

この記事では具体的な hook script までは載せませんが、`permissions` だけに寄せるのではなく、「読ませない」「編集させない」「実行前に一度止める」を重ねると、うっかり事故は減らせます。

参考:

### Codex 側ではどうするか

Codex については、この記事では設定ファイル例までは踏み込みません。

自分の使い方だと Codex App、Codex CLI、sandbox、approval の扱いが環境によって変わるためです。ここで雑に `~/.codex/config.toml` の例を書くより、考え方だけ揃える方が安全だと思いました。

見る場所は Claude Code と同じです。

* ファイルを書き換える前に確認が入るか
* shell command の実行前に確認が入るか
* network access が必要な作業か
* `.env` や secret に触れうる作業か
* `git push` や PR 作成まで任せるか

特に長めの実装や自動実行に寄せる場合は、作業ディレクトリ、network、secret、git push の境界を確認してから使うようにします。

参考:

## GitHub 側で設定すること

一人開発向けには、GitHub 側の設定も最低限にします。

GitHub の branch protection や ruleset で強制したいのは、まずこの2つです。

* main branch への force push 禁止
* main branch deletion 禁止

feature branch は rebase することがあるので、force push を一律で禁止しません。必要なときは `--force` ではなく `--force-with-lease` を使います。

feature branch まで完全に縛ると、未来の自分が rebase のたびに過去の自分へ文句を言うことになります。

あとは GitHub の設定というより、自分の運用で見ることにしました。

* main への direct push を避ける
* workflow 変更は手動確認する
* deploy / secret / auth 周りの変更は差分を読む

それよりも、main 反映前に自分が差分を見ること、workflow や secret 周りだけ明確に特別扱いすることの方が続きそうです。

## 禁止ではなく、任せる範囲を決める

この棚卸しは、AI agent を怖がって使わないためのものではありません。

むしろ逆です。

**AI agent を使い続けたいから、権限を見える化する。**

Claude Code や Codex に実装を任せるのはかなり便利です。push や PR 作成までやってもらえるのも助かります。だからこそ、どこまで任せるかを決めておいた方がよいです。

自分の場合は、こう整理しました。

| 任せる | 一拍置く |
| --- | --- |
| 通常の実装 | main への反映 |
| テスト実行 | workflow 変更 |
| commit 作成 | deploy 設定変更 |
| feature branch への push | secret / `.env` 周り |
| PR 作成 | auth / billing / webhook 周り |

全部を止める必要はありません。

危ない場所だけ、一拍置けばよいです。

全部のドアに鍵をかけると、自分も家に入れなくなります。

## まとめ

AI coding agent は、もはや単なる補助ツールではありません。

少なくとも自分の環境では、Claude Code / Codex は repository を書き換え、shell を実行し、push や PR 作成までできる実行主体です。

だからといって、使うのをやめたいわけではありません。

むしろ使い続けたいので、権限を棚卸ししました。

一人開発で必要なのは、重い統制ではなく、続けられる軽いガードです。

* main 直 push を避ける
* workflow / deploy / secret 周りは一拍置く
* dev `.env` も secret として扱う
* browser-use はログイン状態をまず確認する
* AI agent ごとの権限表を持つ

これだけでも、かなり見通しがよくなります。

AI agent を安全に使うというのは、AI を信用しないという話ではありません。

**自分が渡している権限を、自分で分かっておく**という話です。
