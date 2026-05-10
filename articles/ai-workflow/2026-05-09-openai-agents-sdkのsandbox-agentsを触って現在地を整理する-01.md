---
id: "2026-05-09-openai-agents-sdkのsandbox-agentsを触って現在地を整理する-01"
title: "OpenAI Agents SDKのsandbox agentsを触って、現在地を整理する"
url: "https://zenn.dev/peintangos/articles/82fa63869aa2a2"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "OpenAI", "GPT", "TypeScript", "zenn"]
date_published: "2026-05-09"
date_collected: "2026-05-10"
summary_by: "auto-rss"
query: ""
---

こんにちは、松尾淳平です。2026年4月15日にOpenAI Agents SDKにsandbox agentsが登場、5月6日にはTypeScript SDKでも使えるようになりました。この記事では、最小構成の`Agent`との差分に着目して「何が変わったのか」「なぜその設計になっているのか」を整理したいと思います。

## 前提の確認

単純化して考えてみると、通常のAgentは指示（`instructions`）とユーザー入力の2つだけで動きます。

```
import { Agent, run } from "@openai/agents";

const agent = new Agent({
  name: "リリースノートチューター",
  instructions:
    "OpenAI Agents SDK の更新点を日本語で説明してください。簡潔かつ具体的にしてください。",
  model: "gpt-5.4-mini",
});

const result = await run(
  agent,
  "2026年4月以降の Agents SDK 更新で、最初に理解すべきことを1つ教えて。",
);

console.log(result.finalOutput);
```

## sandbox agentsでは何が変わるのか

sandbox agentsでは、Agentに専用の作業環境（workspace）が与えられます。workspaceはホストのファイルシステムから分離された空間で、Agentはその環境の中で作業するようになります。通常のAgentにはなかった作業環境を持つというのが、一番大きな変化です。

具体的にコードで見てみましょう。先ほどの最小構成との差分は3つだけです。

```
import { run } from "@openai/agents";
import { SandboxAgent, shell } from "@openai/agents/sandbox";
import { UnixLocalSandboxClient } from "@openai/agents/sandbox/local";

const agent = new SandboxAgent({                                     // ①
  name: "sandbox作業担当",
  instructions:
    "回答前に sandbox workspace を確認してください。日本語で回答してください。",
  model: "gpt-5.4-mini",
  capabilities: [shell()],                                           // ②
});

const result = await run(
  agent,
  "今の workspace で確認できることを教えて。",
  {
    sandbox: {
      client: new UnixLocalSandboxClient(),                          // ③
    },
  },
);

console.log(result.finalOutput);
```

| # | 何が増えたか | 何をしているか |
| --- | --- | --- |
| ① | `SandboxAgent` | workspace付きのAgentを作る |
| ② | `capabilities` | Agentに許す操作を指定する |
| ③ | `sandbox.client` | sandboxの実体をどこに作るか指定する |

少し補足します。②の`capabilities`は、Agentがworkspaceの中でどんな操作をしてよいかを制御するものです。上の例では`shell()`を渡しているので、Agentはworkspace内でshellコマンドを実行できます。他にも、ファイルの読み書きを許可する`filesystem()`や、作業から得た知見を後続のrunに引き継ぐ`memory()`などがあります。③の`sandbox.client`は、そのworkspaceの実体をどこに作るかを決めるものです。上の例では`UnixLocalSandboxClient`でローカルに作っていますが、`DockerSandboxClient`に差し替えるとDocker上で同じAgentを動かせます。Agent定義は変えず、clientだけの変更で実行場所を切り替えられます。

ここまでの話を図にまとめると、以下のようになります。

![通常のAgentとSandboxAgentの違い](https://static.zenn.studio/user-upload/deployed-images/0236927ef764942246f90a98.png?sha=c99fb57abf6615b4e07662024ecfa2a1da034f1c)

## Manifestでworkspaceの初期状態を宣言する

Agentがworkspaceを持つことがわかりました。では、そのworkspaceの中身はどう決まるのでしょうか。`Manifest`は、Agentが起動したときworkspaceに何があるかを宣言するものです。たとえば「2つのリリースノートを比較して」と頼みたい場合、Manifestを使わなければプロンプトに全文を貼り付けることになります。

```
await run(agent, `
  4月の更新: ...（長文）...
  5月の更新: ...（長文）...
  差分をまとめて。
`);
```

ファイルが2つなら何とかなります。しかしファイルが増えたり、ディレクトリ構造を意識させたくなると、この形は破綻します。指示と資料が混在し、「何が指示で何が作業対象か」が曖昧になるからです。Manifestを使うと、workspaceの初期状態をコードで定義できます。

```
import { Manifest, file } from "@openai/agents/sandbox";

const manifest = new Manifest({
  entries: {
    "updates/april.md": file({
      content:
        "# 2026年4月\n\n" +
        "- Agent 作業向けの controlled sandboxes。\n" +
        "- open-source harness の inspect / customize。\n" +
        "- memories をいつ作るか、どこに保存するかの制御。\n",
    }),
    "updates/may.md": file({
      content:
        "# 2026年5月\n\n" +
        "- TypeScript Agents SDK に sandbox agents が組み込まれた。\n" +
        "- TypeScript でも workspace を渡す形で実装可能に。\n",
    }),
  },
});
```

これを`SandboxAgent`の`defaultManifest`に渡すと、Manifestで定義したファイルがworkspaceに配置された状態でAgentが起動します。

```
const agent = new SandboxAgent({
  name: "sandboxリリースノート分析担当",
  instructions:
    "回答前に workspace のファイルを確認してください。ファイル名を引用し、日本語で回答してください。",
  model: "gpt-5.4-mini",
  defaultManifest: manifest,
  capabilities: [shell()],
});

const result = await run(
  agent,
  "updates ディレクトリを読んで、4月から5月にかけて何ができるようになったかを3点でまとめて。",
  {
    sandbox: {
      client: new UnixLocalSandboxClient(),
    },
  },
);
```

ここまでの流れを図にすると、以下のようになります。

![Manifestがworkspaceの初期状態を宣言する](https://static.zenn.studio/user-upload/deployed-images/ca6a63c73cdb15f528b53011.png?sha=a374c335fd1db39f531628a4e9c08ec37c3be06a)

Manifestで定義したファイルはworkspaceに展開されます。指示は`instructions`やユーザー入力で伝え、作業対象はworkspaceに置く。この分離によって、それぞれの関心を独立して管理できるようになります。なお、今回のサンプルでは`file()`で内容をハードコードしていますが、これはManifestの一番単純な形です。SDKにはクラウドストレージをworkspaceにマウントする`GCSMount`や`S3Mount`、`BoxMount`なども用意されており、たとえばBoxに溜まった社内ドキュメントをAgentのworkspaceにマウントして分析させるといった使い方もできます。

## HarnessとSandboxはなぜ分かれているのか

ここまで`SandboxAgent`、`capabilities`、`Manifest`、`sandbox.client`など、いくつかの要素が出てきました。これらはSDKの中で2つの層に分かれています。

| 層 | 何を担うか |
| --- | --- |
| Harness | Agentの動き方を制御する。どのtoolを呼ぶか、いつ人間の承認を挟むか、実行ログをどう取るかなどを管理する |
| Sandbox | Agentが実際に作業する場を提供する。workspace、ファイル操作、コマンド実行などを担う |

では、なぜ2つに分かれているのでしょうか。もしこれが1つの層だったらどうなるかを考えると見えてきます。Agentの動き方の制御と、作業環境の管理が同じ場所にあると、たとえばこういうことが起きます。

* sandboxの実行場所をローカルからDockerに変えたいだけなのに、Agentの制御コードまで影響する
* 人間の承認フローを追加したいだけなのに、ファイル操作の実装と絡まる
* 開発環境と本番でsandboxの構成を分けたいだけなのに、Agentの定義まで変えないといけない

HarnessとSandboxが分かれていると、設計判断の軸が明確になります。「Agentの振る舞いを変えたいならHarness層、作業環境を変えたいならSandbox層」という判断基準が持てます。sandboxの実行場所を差し替えてもAgentの定義は変わらないし、Agentに新しいtoolを足してもsandboxの構成には触れません。

ここまでの話を図にまとめると、以下のようになります。

![HarnessとSandboxの責務の分離](https://static.zenn.studio/user-upload/deployed-images/7e4c3f81c0da6de02d40ebf4.png?sha=4f3b6a5bdb95a60b31470b998ebb4e7f2f3dd904)

## sandbox memory（おまけ）

最後にsandbox memoryにも触れておきます。sandbox memoryは、workspaceでの作業を通じて得た知見を後続のrunで使えるようにする仕組みです。capabilitiesに`memory()`を渡すことで、既存のmemoryを読むか、今回の作業から新たにmemoryを生成するか、どこに保存するかをコードで制御できます。memoryが暗黙的に溜まるのではなく、設計対象として扱えるようになっている点が2026年4月のmemory controlの大きな変化でした。

## sandbox agentsはどこに向かっているのか

ここまで触ってみて、sandbox agentsが想定しているのは「ホストから分離された環境で自律的に作業するエージェント」だと感じました。たとえば社内のデータ処理パイプライン（CSVをworkspaceに配置し、集計スクリプトを書いて実行し、レポートを生成する）や、特定業務に特化した自動化エージェント（決まったワークフローに沿ってファイルを加工・検証する）といったユースケースです。逆に、質問に答えるだけのチャットボットや、APIを叩くだけのエージェントにはsandbox agentsは過剰だなという印象です。

一方で、現時点でのsandbox agentsを本番で使おうとすると、ハードルはそこそこ高いと感じます。たとえばクラウドストレージをworkspaceにマウントするにはネットワーク構成や認証情報の管理が必要ですし、sandbox clientも現時点ではローカルとDockerの2種類です。また、実際に検証したところ、ローカルでもDockerでもsandbox内からインターネットにアクセスできました。ファイルシステムは分離されていますが、ネットワークの制御はSDK側に仕組みがなく、現時点ではDocker側の設定に委ねる形になります。

正直な温度感としては、sandbox agentsは「エージェントが作業環境を持って自律的に動く」という方向性の基盤設計であって、SDKとしての拡張ポイントを先に用意した段階だと思います。capabilities、Manifest、sandbox.clientが分かれている設計は、将来的にsandbox clientが増えたり、より複雑なworkspace構成が求められたときに活きてくるはずです。

## まとめ

最小構成の`Agent`からsandbox agentsへ進むと、変化は3つに集約できます。

1. Agentが作業環境を持つようになった。通常のAgentにはなかったworkspaceが与えられ、その中で実際に作業できるようになった。
2. Manifestで作業環境を宣言できるようになった。指示と作業対象を分離し、それぞれを独立して管理できるようになった。
3. HarnessとSandboxが分離した。Agentの動き方の制御と作業環境が独立し、それぞれを個別に設計・差し替えできるようになった。

AIエージェントの実装は「プロンプトを書くこと」から「workspace・tools・permissions・memory・runtimeを設計すること」へ変わりつつあります。OpenAI Agents SDKのsandbox agentsは、その方向性をわかりやすく示していると感じました。

## 参考
