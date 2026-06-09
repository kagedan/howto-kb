---
id: "2026-06-08-ポリレポ開発をaiエージェントに任せるためのcontrol-plane設計-01"
title: "ポリレポ開発をAIエージェントに任せるためのcontrol plane設計"
url: "https://zenn.dev/purple_matsu1/articles/20260603-polyrepo-harness-engineering"
source: "zenn"
category: "claude-code"
tags: ["API", "AI-agent", "Python", "zenn"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

## はじめに

前提として、私はAIエージェントで開発するならモノレポのほうが向いていると思っています。

コンテキストを渡しやすいし、repo間の契約も追いやすい。検証コマンドや作業境界も揃えやすいです。

ただ、現実にはすでにポリレポで動いているプロジェクトがあります。

frontend、backend、infraのrepoが分かれているプロジェクトに対してAIエージェントで開発する場合、単に「この機能を作って」と言っても、エージェントはどのrepoを見ればいいのか迷います。

最近は、親repoをcontrol planeとして扱い、そこに開発用のSkillを置くようにしています。

この記事では、自分が作っている `harness-engineering` というSkillを例に、既存ポリレポでAI開発を回すためのハーネス設計を整理してみます。

ポリレポを推奨したいわけではありません。

すでにポリレポで動いているプロジェクトに、どうAIエージェントを接続するか、という話です。

## 本当はモノレポのほうがやりやすい

単一repoなら、AIエージェントに「この機能を作って」と頼んでも、だいたい見るべき場所は決まっています。

もちろん単一repoでも難しさはありますが、少なくとも作業対象の境界は比較的わかりやすいです。

frontendとbackendの契約変更も同じrepo内で追えます。

CIやlint、testの入り口も揃えやすい。

AIエージェントにとっては、モノレポのほうが「状況を把握するための足場」を作りやすいと感じています。

なので、これから新しくAIエージェント前提で開発体制を作るなら、まずはモノレポを検討したほうがいいと思っています。

## それでもポリレポでAI開発する必要がある

ポリレポになると、ここが一気に曖昧になります。

* 対象repoが曖昧になる
* repo間の契約変更が見落とされる
* 検証コマンドがrepoごとに違う
* frontendの変更なのか、backend contractの変更なのか判断が必要になる
* infraの失敗なのか、既存state driftなのか切り分けが必要になる
* main contextにdiffやログが入りすぎる

人間が横で見ていれば、「それはbackendも見る必要があるよ」「そのTerraformエラーは既存リソースのimportかも」と止められます。

でも、それを毎回チャットで説明するのはしんどいです。

あれ？ これはプロンプトで毎回頑張る話ではないのでは。

そう思って、親repo側に開発の進め方そのものを置くようになりました。

ポリレポをモノレポに作り替える話ではありません。

既存のrepo構成はそのままにして、AIエージェントが迷いにくいcontrol planeを足す、という考え方です。

## 親repoをcontrol planeにする

自分の運用では、親repoをcontrol plane、子repoをexecution planeとして扱っています。

親repoは、実装コードを書く場所ではありません。

作業の状態、要件、計画、検証結果、レビュー結果を管理する場所です。

一方で、子repoは実際のコード変更を行う場所です。

ざっくり書くと、こんな構成です。

```
parent-repo/
  harness/
    runs/
      <run_id>/
        request.md
        state.json
        summary.md
        requirements/
        plans/
        dispatch/
        reviews/
        final-summary.md

  worktree/
    app-frontend/
    app-backend/
    app-infra/
```

`harness/runs/<run_id>/` には、その作業で発生したartifactを置きます。

最初の依頼、要件定義、repo別の計画、実装結果、検証証跡、レビュー結果、最終サマリ。

会話の中に流れていくものを、できるだけrepo内のartifactとして残すイメージです。

`worktree/` には、子repoごとの作業用worktreeを置きます。

ここで大事なのは、子repoのworktreeを親repo直下に置いていることです。

親repoで `git worktree add` するのではなく、対象の子repoのgit rootで `git worktree add` を実行し、作成先だけ親repo直下の `worktree/<project-name>/<branch-name>` にします。

少しややこしいですが、これには理由があります。

VS Codeで親repoを開いたときに、作業中の子repoが見えるからです。

hidden directoryに入れるより、どのrepoでどのbranchが動いているかを視覚的に追いやすい。

地味ですが、長い作業ではこういう見通しが効きます。

全体像を図にすると、こんな感じです。

親repoが全部の実装を抱えるわけではありません。

親repoは、作業の状態と判断材料を集める場所です。

実装はあくまで子repo側で行います。

## このSkillが実際にやっていること

`harness-engineering` は、単に「AIにいい感じに実装してもらう」ためのプロンプトではありません。

どちらかというと、ポリレポ開発を進めるための状態管理、作業分離、検証、レビュー、再計画のルールを固定したものです。

ちなみに、`harness-engineering` という名前は仮です。

自分の作業用Skillとしては伝われば十分ですが、もしこれを1つのプロジェクトとして外に出すなら、もう少し適切な名前を考えたほうがよいと思っています。

名前が汎用的すぎると、何をするものなのかが逆に伝わりにくいですからね。

Skillの入口には、こういう役割を書いています。

```
親 repo を control plane、
各子 repo を execution plane として扱い、
Codex subagent に作業を分離してレビュー OK まで進める。
```

この一文がほぼ全体の設計思想です。

AIエージェントを1つの大きな会話で走らせるのではなく、役割ごとに分けます。

要件を整理するエージェント。

計画を作るエージェント。

repoごとに実装するエージェント。

検証するエージェント。

観点別にレビューするエージェント。

レビュー結果を集約するエージェント。

そして、NGだったときに再計画するエージェント。

それぞれに、読むファイル、書くファイル、許可されたwrite scope、出力契約を渡します。

これは「AIに頑張ってもらう」というより、作業単位を小さく切って、各エージェントに担当範囲を明示するやり方です。

## main contextを汚さない

このSkillで特に意識しているのが、main contextを汚さないことです。

AIエージェントにポリレポ開発をさせると、すぐにコンテキストが膨らみます。

* diff全文
* lintやbuildの長いログ
* サブエージェントの試行錯誤
* ブラウザ検証のsnapshot
* Terraform plan
* GitHub PRのコメント
* repoごとの調査メモ

全部をメインセッションに入れると、後半の判断が怪しくなります。

なので `harness-engineering` では、メインセッションが読むものを絞っています。

基本的に読むのは、次のような短いartifactだけです。

* `state.json`
* `summary.md`
* repo別の `status.json`
* 短い `result.md`
* `evidence.md`
* `gate.md`

長いログやdiff全文は、必要なときだけsubagentが読みます。

親が全部を抱え込まない。

でも、判断に必要な要約と状態は親repoに残す。

この分離があると、長い作業でも「今どこにいるのか」を見失いにくくなります。

## 状態遷移として開発を扱う

`harness-engineering` では、開発を状態遷移として扱っています。

ざっくり書くと、こうです。

```
INTAKE
  -> REQUIREMENTS
  -> REQUIREMENTS_REVIEW
  -> PLANNING
  -> PLAN_REVIEW
  -> WORKTREE_PREPARE
  -> IMPLEMENT
  -> VERIFY
  -> REVIEW_MANIFEST
  -> REVIEWERS
  -> REVIEW_GATE
      -> PASS -> FINALIZE
      -> REPLAN -> REPLAN_FROM_REVIEW -> PLAN_REVIEW -> IMPLEMENT
      -> FAIL -> HARNESS_UPDATE -> failed phase
```

ここで大事なのは、レビューNGや検証NGのときに、いきなり実装修正へ戻さないことです。

必ずreplanを挟みます。

普通にAIエージェントへ作業を頼むと、テストが落ちた瞬間にその場で修正しようとします。

レビューで指摘されても、すぐに該当箇所だけ直しにいきます。

それで済む場合もあります。

ただ、既存ポリレポでは危ないです。

frontendの修正に見えて、backend contractの問題かもしれない。

infraの設定変更に見えて、クラウドリソース側の既存state driftかもしれない。

UIの不具合に見えて、APIレスポンス設計がズレているかもしれない。

だから、失敗したら一度planに戻します。

「どの前提が壊れていたのか」

「repo別の手順を変える必要があるのか」

「検証コマンドを追加する必要があるのか」

そこを確認してから、もう一度実装へ戻します。

このreplan gateがあるだけで、場当たり的な修正が減ります。

## repoごとの検証を固定する

ポリレポでは、検証コマンドもrepoごとに違います。

frontendなら `npm run type-check`、`npm run lint`、`npm run build`、必要ならブラウザ検証。

backendならPythonのcompileやunit test。

infraなら `terraform fmt -check -recursive`、`terraform validate`、必要に応じて `terraform plan`。

これを毎回AIに判断させると、抜けます。

なので、Skill側にrepo mapとして書いています。

```
app-frontend       -> type-check / lint / build / browser verification
admin-frontend     -> type-check / lint / build / browser verification
app-backend        -> Python compile / unit test / API or DB spec check
app-infra          -> terraform fmt / validate / plan when needed
```

もちろん、すべての作業で全部を実行するわけではありません。

ただ、「このrepoなら基本的に何を見るべきか」をSkillに置いておくと、検証の抜けが減ります。

検証結果も、ただ「テスト通りました」では終わらせません。

`evidence.md` に、command、cwd、exit code、result、log path、Git Stateを残します。

```
Command: npm run build
CWD: worktree/app-frontend/<branch>
Exit Code: 0
Result: PASS
Log: logs/build.log
```

ログ全文を貼るのではなく、どのコマンドをどこで実行し、結果がどうだったかを残す。

これくらいの粒度が、main contextにも人間の確認にも扱いやすいです。

## レビューは1観点1エージェントに分ける

もう1つ重視しているのが、レビューの分離です。

ポリレポの変更を1つのエージェントにまとめてレビューさせると、論点が混ざります。

要件を満たしているか。

実装品質はよいか。

repo boundaryを破っていないか。

検証証跡は十分か。

security riskはないか。

これを1つのレビューで全部見るのは、人間でもけっこうしんどいです。

なので、`harness-engineering` ではreviewerを分けています。

* `requirements-conformance-reviewer`
* `implementation-quality-reviewer`
* `architecture-integration-reviewer`
* `verification-evidence-reviewer`
* `security-risk-reviewer`
* `domain-specific-reviewer`

それぞれのreviewerは、1つの観点だけを見ます。

たとえば `verification-evidence-reviewer` は、実装の良し悪しを見ません。

必要な検証が実行されているか、evidenceが足りているかだけを見ます。

`implementation-quality-reviewer` は、要件の妥当性を決めません。

過剰抽象化、不要なfallback、既存パターンとのズレ、AIっぽい雑な実装を見ます。

この分け方にすると、レビュー結果が扱いやすくなります。

最後に `review-aggregator` が各レビュー結果を集約します。

ただし、aggregatorは新しい指摘を探しません。

ここも意識して分けています。

reviewerは指摘する人。

aggregatorは判定する人。

同じエージェントに両方やらせると、集約の途中で新しい論点を見つけてしまい、gateの責務が曖昧になります。

## ハーネス自体も改善対象にする

実装が失敗するだけでなく、ハーネス自体が失敗することもあります。

たとえば、次のような失敗です。

* subagentの出力に必要なfieldがない
* `status.json` が壊れている
* verificationが落ちたのに、直接実装へ戻ってしまった
* reviewerが `replan` を出したのに、plan reviewを飛ばした
* implementerが指定されたworktreeの外を編集した
* main contextが長いログやdiff全文を読みすぎた
* evidenceに command / cwd / exit\_code / result が残っていない

これは実装ミスというより、ハーネス設計のミスです。

そこで `harness-update` というSkillも用意しています。

これは、失敗を一回限りの反省で終わらせず、`harness-engineering` のSkillやtemplateに戻すためのものです。

失敗を分類します。

* skill指示不足
* artifact契約不足
* gate不足
* repo map不足
* 検証不足
* subagent分割ミス
* worktree隔離ミス
* main context汚染

そして、必要なら `SKILL.md` やtemplateを更新します。

つまり、ハーネスで開発を回しながら、ハーネス自体も育てていく形です。

ここは大事だと思っています。

AIエージェントの失敗を「モデルが悪い」で終わらせると、次も同じ失敗をします。

でも、失敗をartifact contractやgateの不足として扱うと、次回の作業に反映できます。

この感覚は、普通のプロンプト改善よりも、CIやlint ruleを育てている感覚に近いです。

## Skillは便利プロンプトではなく運用契約

最近は、Skillを便利プロンプト集として見るより、AIエージェント向けの運用契約として見るようになってきました。

どのrepoを触るか。

どこにworktreeを作るか。

どの検証を通すか。

レビューNGならどこへ戻るか。

main contextに何を入れないか。

失敗したときに、何をハーネス側へ反映するか。

このあたりを毎回チャットで説明するのではなく、repoに置いておく。

特に既存ポリレポでは、この差が大きいです。

AIエージェントに任せる範囲が広がるほど、モデルそのものの賢さだけではなく、どんな状態管理、検証、レビュー、再計画の仕組みに接続するかが効いてきます。

私はこれを、既存ポリレポ向けのハーネスエンジニアリングとして捉えています。

## おわりに

このSkillは、外部公開を前提にしていません。

repo mapや検証コマンドまで含めて、プロジェクト固有に寄せています。

だからこそ、汎用Skillというより、このポリレポの開発運用そのものに近いものになっています。

AIエージェントに「実装して」と頼む前に、どのrepoをどう扱うかを決める。

その判断を毎回チャットで説明するのではなく、親repoにハーネスとして置く。

一度この形にすると、AI開発の見え方が少し変わります。

プロンプトを育てているというより、開発環境そのものを育てている感覚に近くなります。
