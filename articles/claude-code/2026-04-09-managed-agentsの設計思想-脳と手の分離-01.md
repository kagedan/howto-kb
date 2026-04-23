---
id: "2026-04-09-managed-agentsの設計思想-脳と手の分離-01"
title: "「Managed Agents」の設計思想 :「脳」と「手」の分離"
url: "https://zenn.dev/dragon1208/articles/4c1b5549faadc4"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Codeのような強力なAIエージェントを利用、あるいは自社でAIエージェントを組み込んだシステムを開発するにあたり、**「長期間・安全・大規模にエージェントを安定稼働させるための設計」** を理解することは非常に重要です。

Anthropic社は、自社のホスト型エージェント実行基盤である「Managed Agents」を設計する中で、**「Brain（脳）と Hands（手）を分離する」** という重要なアーキテクチャの結論に達しました。本記事では、エンジニアの皆様がClaude Codeを活用する際やLLMアプリケーションを設計する際の指針となるよう、この最新の設計思想をMermaid図やコード例を交えて詳細に解説します。

<https://www.anthropic.com/engineering/managed-agents>

## 1. 従来型アーキテクチャの限界

初期のAIエージェント開発では、実装の容易さから以下のような「全部入り」の構成がよく採用されます。

このアプローチは **「ペット（手厚いサポートが必要なサーバー）」** を飼ってしまうというクラウドインフラにおける古典的な問題を引き起こすと説明されています。

> But by coupling everything into one container, we ran into an old infrastructure problem: we’d adopted a pet.

* **可用性の欠如**: コンテナがクラッシュすると、エージェントのセッション（会話履歴や作業状態）がすべて失われます。
* **デバッグの困難さ**: イベントストリームからのパケット欠落なのか、実行環境のバグなのか判別がつかず、ユーザーデータが同居しているため本番環境に入ってのデバッグも困難でした。
* **インフラの密結合**: ユーザーのVPC内で実行したい場合、コンテナごと移動するかネットワークをピアリングする必要がありました。

## 2. 解決策：コンポーネントの疎結合化

この問題を解決するため、Anthropicはエージェントを構成する要素を完全に分離し、それぞれを独立してスケール・復旧可能な「家畜（Cattle）」として扱うアーキテクチャを採用しました。

エージェントは以下の3つに分割されました。

1. **Brain（脳）**: Claude本体と、ツールのルーティングなどを行う「Harness」。
2. **Hands（手）**: コードを実行する「Sandbox」や外部ツール。
3. **Session（記憶）**: すべてのイベントを記録する永続的な追記型ログ。

## 3. 押さえるべき4つの設計パラダイム

この分離によって得られた、実務でAIシステムを構築・利用する際に役立つ4つの設計パラダイムを解説します。

### A. 実行環境の「ツール化」とリカバリ

Harness（Brain）はSandbox（Hands）と同居するのではなく、外部から**ツールとして呼び出す**形になります。

**【概念コード例】**

```
// Harness側の処理イメージ
async function runAgentAction(actionName, inputData) {
    try {
        // Hands（実行環境）を単なるツールとして呼び出す
        const result = await execute(actionName, inputData); 
        return result;
    } catch (error) {
        // Sandboxコンテナが死んだ場合、Harnessは巻き込まれずにエラーをキャッチ
        console.log("Sandbox is dead. Re-provisioning...");
        
        // 新しい実行環境を標準レシピで立ち上げ直す（Cattleとしての扱い）
        await provision({ resources: "standard" }); 
        
        // エラー結果をClaudeに返し、Claude自身にリカバリを考えさせる
        return "Tool execution failed. Container restarted. Please retry."; 
    }
}
```

このように設計することで、実行環境がクラッシュしても作業履歴は失われず、自動的に新しい環境を作って再開できます。

### B. セキュリティの構造的担保（モデルに秘密を見せない）

AIモデルが賢くなるにつれ、プロンプトインジェクションの脅威も増します。以前の構成では、悪意あるプロンプトがモデルを誘導して環境変数を読み取らせるリスクがありました。

Managed Agentsでは「権限を絞る」のではなく、**「トークン自体をSandboxから物理的に切り離す」構造的対策**を取っています。

* **Git操作**: Sandbox初期化時にリポジトリ側で認証を済ませ、エージェントはトークンに触れずに `git push/pull` のみ可能にします。
* **カスタムツール（MCP）**: 認証情報は外部のVault（金庫）に保持し、専用プロキシを経由してAPIを叩きます。HarnessやClaude自身は資格情報の存在すら知りません。

### C. 長期記憶とコンテキストウィンドウの明確な分離

LLMが扱うタスクが長期化すると、コンテキスト制限を超えてしまいます。これまでは「古い記憶を要約・削除する（Compaction / Trimming）」手法が主流でしたが、これは**不可逆な破壊的変更**であり、「未来のタスクで必要になるかもしれない情報」を消してしまうリスクがありました。

Anthropicは、**「コンテキストウィンドウ（短期記憶）」と「セッションログ（永続記憶）」を完全に分離**しました。

**【概念コード例】**

```
// HarnessがSessionから動的にコンテキストを構築するイメージ
async function buildContextForClaude(sessionId, currentStep) {
    // 記憶（Session）は外部のDBなどに完全に保存されている
    const sessionStore = getSession(sessionId);
    
    // 必要な範囲だけをスライスして取得（ex. 直近のイベントと、初期の前提条件）
    const recentEvents = await sessionStore.getEvents(currentStep - 10, currentStep);
    const setupEvents = await sessionStore.getEvents(0, 2);
    
    // Harness側でモデルに渡すPromptを最適化して組み立てる
    const contextWindow = transformForPromptCache([...setupEvents, ...recentEvents]);
    
    return contextWindow;
}
```

フロントエンド開発における「Source of Truth（状態管理）」と「View（UI）」の分離と同じように、**「完全なイベント履歴はDurableなログに持ち、推論のたびに必要な部分だけを切り出してモデルに渡す」**　という構成にしています。

### D. 必要な時だけ「手」を借りる（TTFTの劇的改善）

分離のもう一つの恩恵はパフォーマンスです。  
以前はセッション開始時に重いコンテナをプロビジョニングしていたため、ユーザーが最初の文字を受け取るまでの時間（TTFT: Time-to-first-token）が長くなっていました。  
脳と手を分けることで、**「推論（Brain）は即座に開始し、コード実行環境（Hands）はモデルが要求したタイミングで初めて立ち上げる（遅延評価）」**　ことが可能になり、TTFTの中央値が約60%、p95では90%以上も低下しました。

## 4. 実行モデルのパラダイムシフト：「Code Mode」

Anthropicの「Hands」の概念をさらに進化させ、実践的なアプリケーションへの組み込みを容易にするのが、TanStackが提唱する **「Code Mode」** です。  
<https://tanstack.com/blog/tanstack-ai-code-mode>

現在の最先端LLMには次のような特性があります。

1. **ツール呼び出しは遅くて高価**: 個別のAPI呼び出しはラウンドトリップを発生させ、コンテキストウィンドウを肥大化させます。
2. **計算（算数）が絶望的に苦手**: 複数のAPIレスポンスから数値を合計させると、自信満々に間違える傾向があります。
3. **TypeScriptを書くのは非常に得意**: 膨大な訓練データにより、非同期制御（Promise）やデータ操作に長けています。

#### 個別ツール呼び出しによるN+1問題

例えば「トップ5の商品の平均評価を計算して」と依頼した場合、従来は「商品一覧取得」→「各商品の評価を5回個別取得」→「LLMが頭の中で計算」という手順を踏みます。これでは7回のラウンドトリップが発生し（N+1問題）、さらにLLMが浮動小数点の計算を間違える可能性が高くなります。

#### 解決策：LLMにプログラムを書かせてサンドボックスで実行する

Code Modeでは、LLMに細々としたツールを個別に渡すのではなく、**execute\_typescript** という単一のツールを与えます。LLMは、APIの並列フェッチ、データの集約、計算をすべて含む短いTypeScriptコードを生成し、それを隔離された環境（Node, QuickJS, Cloudflare Workers等）で実行させます。

*(※具体的なコードスニペット自体は参考ドキュメント内では省略されていますが、記事の説明に基づき、Code Modeが実際に生成・実行する仕組みのイメージを以下のTypeScriptコードで表現してます。)*

```
// Code ModeにおいてLLMが生成・実行するTypeScriptのイメージ
async function calculateAverageRatings() {
  // LLMが外部ツールをサンドボックス内で関数として呼び出す
  const topProducts = await external_getTopProducts(5);
  
  // N+1問題を回避し、Promise.allで5件のAPIフェッチを並列化
  const ratings = await Promise.all(
    topProducts.map(product => external_getProductRatings(product.id))
  );
  
  // LLMの曖昧な推論ではなく、JSのランタイム（.reduce）で正確に集約・計算
  const totalRating = ratings.reduce((sum, rating) => sum + rating.value, 0);
  const average = totalRating / ratings.length;
  
  return { products: topProducts, averageRating: average };
}
```

これにより、**N+1問題が解消し、算術計算はJavaScriptランタイム上で100%正確になり、コンテキストウィンドウのトークン節約効果も複利で効いてきます**。

### 4. 自己進化するエージェント：Skills（スキル）

さらにCode Modeの強力な機能として、\*\*「Skills（スキル）」\*\*という概念があります。通常、LLMは同じタスクを与えられると、毎回ゼロからコードを書き直してしまいます。しかし、一度サンドボックスで成功したTypeScriptコードを、名前やスキーマ付きの永続的なスキルとして登録（register\_skill）しておけば、次回以降の会話ではLLMがそのスキルを直接ツールとして呼び出すことができるようになります。これらのスキルは実行回数と成功率に応じて「信頼スコア」を獲得し、将来的なワークフローの自動化に繋げることも可能です。

## まとめ

私たちが実務で利用する**Claude Code**は、このアーキテクチャ上で動作する「非常に優れた特定用途向けハーネス」の一つとして位置づけられています。

この思想は、以下の比喩で分かりやすく表現できます。

> **【従来の危険な構成】**  
> 脳・手・記憶・金庫が全部同じ部屋にある。部屋が燃えたらすべて終わり。
>
> **【スケーラブルな構成（Managed Agents思想）】**
>
> * **脳** は推論と判断に専念する
> * **手** は必要な時だけツールとして呼び出す（壊れたら新しくする）
> * **記憶** は外部の安全なログに永続化する
> * **金庫** は別室に置き、必要な処理はプロキシに代行させる

私たちが社内で自動化スクリプトを書く際や、エージェントを自作・拡張する際も、**「実行環境のコンテナにすべてを詰め込んでいないか？」「プロンプト制御だけでセキュリティを守ろうとしていないか？」「永続化すべき履歴をモデルのコンテキスト内に押し留めていないか？」**　を問うことで、より堅牢でスケーラブルなシステムを構築できるはずです。
