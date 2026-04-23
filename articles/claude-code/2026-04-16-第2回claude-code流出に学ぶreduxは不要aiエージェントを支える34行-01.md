---
id: "2026-04-16-第2回claude-code流出に学ぶreduxは不要aiエージェントを支える34行-01"
title: "第2回：【Claude Code流出に学ぶ】Reduxは不要？AIエージェントを支える「34行」"
url: "https://zenn.dev/guba98/articles/889d141406e46d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/1f5351e5608f-20260416.png)

フロントエンドエンジニアの皆様、深呼吸して聞いてください。  
50万行規模の商用AIエージェントOSである「Claude Code」は、ReduxもZustandも、その他の巨大な状態管理ライブラリも使っていませんでした。

彼らがAIの「記憶（コンテキスト）」と「UI状態」を管理するために書いていたのは、依存関係ゼロのわずか34行の自作Storeだったのです。今回は、この極小Storeの設計思想から、AI時代のシステムアーキテクチャを紐解きます。

巨大ライブラリを捨てたAnthropicの決断  
AIエージェントは、ユーザーの入力、LLMの思考状態、ツールの実行結果など、膨大で非同期な状態（State）を管理する必要があります。通常なら強力な状態管理ライブラリを導入したくなる場面ですが、流出コードにあったのは以下のような極限まで削ぎ落とされたコードでした。

TypeScript  
type Listener<T> = (state: T) => void;

export function createStore<T>(initialState: T) {  
let state = initialState;  
const listeners = new Set<Listener<T>>();

return {  
getState: () => state,  
setState: (nextState: T) => {  
// 変更がなければ何もしない（無駄な再レンダリングを防止）  
if (Object.is(state, nextState)) return;  
state = nextState;  
listeners.forEach(listener => listener(state));  
},  
subscribe: (listener: Listener<T>) => {  
listeners.add(listener);  
return () => listeners.delete(listener);  
}  
};  
}  
なぜこれで十分なのか？  
このコードの美しさは、Object.is() によるシンプルな変更検知と、購読（Subscribe）モデルのみで完結している点です。Reactの useSyncExternalStore などと組み合わせることで、完全にリアクティブなUIを構築できます。

なぜAnthropicは外部ライブラリを避けたのでしょうか。それは\*\*「LLM自体が極めて複雑で不確実なコンポーネントだから」\*\*です。  
システムの中核に「何を出力するかわからないブラックボックス（LLM）」を抱える以上、その周辺を囲むアーキテクチャ（状態管理やルーティング）は、完全に予測可能で、極限までシンプルかつ疎結合でなければなりません。複雑な状態管理ライブラリの魔法は、デバッグを困難にするノイズにしかならないのです。

AI業界のトレンド：周辺技術の「ミニマリズム」  
AIアプリケーション開発において、現在「インフラやフレームワークのミニマリズム」が強く推奨されています。  
LangChainやLlamaIndexのような巨大フレームワークから、よりプリミティブなLangGraphや自前実装への回帰が起きているのも同じ理由です。AI（脳）が複雑な分、エンジニアリング（骨格）はシンプルに保つ。このバランス感覚こそが、これからのAIエンジニアに求められる最も重要なスキルセットと言えるでしょう。
