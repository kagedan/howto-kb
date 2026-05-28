---
id: "2026-05-28-claude-code-k8sgptでeksクラスタの障害調査をやってみる-01"
title: "Claude Code & K8sGPTでEKSクラスタの障害調査をやってみる！"
url: "https://qiita.com/daitak/items/dfc1d165f16846061349"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "GPT", "qiita"]
date_published: "2026-05-28"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

こんにちは、タカサオです！
今回はClaude CodeとK8sGPTを使って、EKSクラスタの障害調査ができるか試してみたいと思います！

# K8gGPTとは？

K8sGPTは生成AIを使ってKubernetesクラスタ内のリソース状態を調査してくれるツールです。

https://k8sgpt.ai/

現在、K8sGPTはCNCFのSandboxプロジェクトとして管理されています。

https://www.cncf.io/projects/k8sgpt/

K8sGPTについては以前ブログを書いていますので、良ければこちらも合わせてご参照ください!

https://qiita.com/daitak/items/c1e3f8e35309f011899f

# 前提構成

自分のPCにK8sGPTのCLIがインストールされており、```k8sgpt analyze```コマンドが実行できるところからスタートします。

```コマンド実行例.

~/bin/k8sgpt analyze --explain --backend amazonbedrockconverse

AI Provider: amazonbedrockconverse

0: ConfigMap default/kube-root-ca.crt()
- Error: ConfigMap kube-root-ca.crt is not used by any pods in the namespace
Error: The ConfigMap `kube-root-ca.crt` is currently not being utilized by any pods within the namespace.

Solution: Verify pod configurations to ensure they reference `kube-root-ca.crt`. Update pod specs if necessary and reapply.
1: ConfigMap kube-node-lease/kube-root-ca.crt()
- Error: ConfigMap kube-root-ca.crt is not used by any pods in the namespace
Error: The ConfigMap `kube-root-ca.crt` is currently not being utilized by any pods within the namespace.

Solution: Verify pod configurations to ensure they reference `kube-root-ca.crt`. Update pod specs if necessary and reapply.

〜〜以下略〜〜
```

# 今回作りたい構成

今回やりたいことは、Claude CodeからK8sGPTを実行してEKSクラスタの障害調査をできるようにしたい!です。

そのため、以下の様にK8sGPTのMCPサーバを使う構成を試してみます。

```
Claude Code (MCPクライアント)
    ↓
K8sGPT (MCPサーバ)
    ↓
EKSクラスタ
```

k8sGPTにはMCPサーバの機能があります。

https://k8sgpt.ai/docs/reference/mcp

実際試してみたところ、```k8g gpt serve --mcp```コマンドでMCPサーバが起動しました、便利ですね!

```コマンド実行例.
~/bin/k8sgpt serve --mcp  --backend amazonbedrockconverse 
{"level":"info","ts":1779915072.2478552,"caller":"server/server.go:149","msg":"binding metrics to 8081"}
{"level":"info","ts":1779915072.2494028,"caller":"server/server.go:108","msg":"binding api to 8080"}
```

ただ、```k8sgpt serve --mcp```はstdioでMCP通信するため、Claude Codeが起動するたびにサブプロセスとして自動的に立ち上がります。そのため、事前に手動で```k8sgpt serve --mcp```を起動しておく必要はありません。

# Claude Codeに登録する

Claude Codeからk8sGPTを使うためには、k8sGPTのMCPサーバをClaude Codeに登録する必要があります。
```claude mcp add```コマンドでMCPサーバを登録します。

```
# 基本的な構文
claude mcp add --transport http <name> <url>

# コマンド実行例
claude mcp add k8sgpt -e AWS_DEFAULT_REGION=us-east-1 -- k8sgpt serve --mcp --backend amazonbedrockconverse

Added stdio MCP server k8sgpt with command: k8sgpt serve --mcp --backend amazonbedrockconverse to local config
File modified: /Users/hogehoge/.claude.json [project: /Users/hogehoge]
```

MCPサーバとして登録できたのかは```claude mcp list```コマンドで確認できます。
正しく登録できたみたいです!

```コマンド実行例.
claude mcp list
k8sgpt: k8sgpt serve --mcp --backend amazonbedrockconverse - ?Connected
```

# Claude CodeからEKSクラスタの障害調査をやってみる!

いよいよ、Claude CodeからEKSクラスタの障害調査をやってみましょう!

今回はイメージの指定が誤ったPodを作成してみます。

```コマンド実行例.
/Users/hogehoge% kubectl run problem-pod --image hogehoge
pod/problem-pod created
/Users/hogehoge% kubectl get pod
NAME          READY   STATUS         RESTARTS   AGE
problem-pod   0/1     ErrImagePull   0          9s
```

Claude Codeに障害調査を依頼して、このPodが検出され、原因調査してくれることを期待します。
```EKSクラスタ上で問題のあるPodを洗い出し、その原因を調査してください。```とClaude Codeに依頼しました。

![スクリーンショット 2026-05-28 6.28.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/d87b2205-bb5d-4af1-a20e-b20be68a6b3a.png)

ちゃんとK8sGPTのMCPサーバを実行してくれています!早々に問題のあるPodを見付けてくれました!

![スクリーンショット 2026-05-28 6.32.52.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/5d73f4be-bdca-4c69-9e00-27734484169a.png)

![スクリーンショット 2026-05-28 6.33.32.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1905292/ed2364ca-85e2-4d8e-b33b-74c596ec9c84.png)

調査完了しました。問題の原因がイメージ指定が誤っている事をちゃんと報告してくれました!
問題の時系列や対処方法もわかりやすく書いてあります、すごい便利ですね!!!!

# まとめ

今回はK8sGPTのMCPサーバをClaude Codeできる様にセットアップしました。
そして、試しに問題のあるPodの調査をClaude Codeに依頼し、ちゃんとK8sGPTを使って障害調査を行ってくれる事を確認できました。

ClaudeがK8sGPTの結果をわかりやすい日本語で解説してくれるので、とってもわかりやすいですし便利ですねー
これはKubernetesのトラブルシュートが捗るな!と思いました!
それではまた!
