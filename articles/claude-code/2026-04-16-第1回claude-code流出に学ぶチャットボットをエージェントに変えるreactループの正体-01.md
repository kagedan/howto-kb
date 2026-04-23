---
id: "2026-04-16-第1回claude-code流出に学ぶチャットボットをエージェントに変えるreactループの正体-01"
title: "第1回：【Claude Code流出に学ぶ】チャットボットを「エージェント」に変えるReActループの正体"
url: "https://zenn.dev/guba98/articles/0e98bf54b43960"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/4cff303a1aac-20260416.jpeg)

「プロンプトエンジニアリングの終焉と、AIソフトウェアエンジニアリングの幕開け」

これが、2026年3月に起きたAnthropicの公式CLIツール「Claude Code」の約51万行に及ぶソースコード流出事件が我々に突きつけた現実です。

AIを「単なるチャットボット」から「自律的に仕事をするエージェント」へと昇華させるための魔法は、複雑なプロンプトの奥底にはありませんでした。それは、我々ソフトウェアエンジニアが日常的に書いている、泥臭くも堅牢な「ループ構造」の中にあったのです。

今回は、流出コードから読み解くエージェントの心臓部、「ReAct（推論と行動）ループ」の正体に迫ります。

AIは「答える存在」から「仕事をする存在」へ  
ChatGPTの登場以降、我々は「いかにAIに良い答えを出させるか」に腐心してきました。しかし、Claude Codeのコードベースには、AIに一発で完璧な答えを出させようとする設計はありません。  
その代わり、AIに「考えて（Thought）、行動し（Action）、その結果を観察する（Observation）」というサイクルを何度も回させるアーキテクチャが採用されていました。

エージェントの正体は while ループである  
流出コードのアーキテクチャを極限までシンプルに削ぎ落とすと、その中核は以下のような単なる while ループに行き着きます。

TypeScript  
async function runAgent(prompt: string) {  
let done = false;  
let context = [prompt];

while (!done) {  
// 1. LLMに現在のコンテキストを渡し、次の行動（または回答）を決定させる  
const response = await callLLM(context);

```
// 2. LLMが「ツールを使いたい」と言った場合（Action）
if (response.toolCall) {
  const toolResult = await executeTool(response.toolCall);
  // 結果をコンテキストに追加してループの先頭に戻る（Observation）
  context.push(`Tool Result: ${toolResult}`);
} 
// 3. LLMが「最終回答が出た」と言った場合
else {
  console.log(response.answer);
  done = true; // ループを抜ける
}
```

}  
}  
「AIが自律的に動いている」ように見えるのは、このループの中でLLMが「ファイルの読み込み」や「コマンドの実行」といったツール（Tool）を呼び出し、その結果を次のプロンプト（Observation）として自身に再入力しているからです。エラーが起きてもパニックにならず、「エラーが出たから別の方法を試そう」と推論（Thought）し、再びツールを実行します。

AI業界のトレンド：単一プロンプトからオーケストレーションへ  
この設計が示すのは、「巨大な1つのプロンプトで全てを解決する時代は終わった」ということです。  
現在のエンタープライズAIの主流は、Plan-and-Execute（計画と実行）やReActといったアーキテクチャ・パターンを用いて、AIのタスクを細分化し、ループの中で堅実に実行させる「オーケストレーション」へと移行しています。

我々エンジニアが学ぶべきは、AIのご機嫌を取るプロンプトの書き方ではなく、「非決定的なLLMの出力を、決定的なコードのループの中でいかに制御・循環させるか」というシステム設計の第一性原理なのです。
