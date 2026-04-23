---
id: "2026-03-19-react-native開発が変わるrozeniteでcoding-agentに目と手を与えた話-01"
title: "React Native開発が変わる。RozeniteでCoding Agentに「目と手」を与えた話"
url: "https://zenn.dev/tellernovel_inc/articles/bb27cd0f28f8cb"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

こんにちは！テラーノベルでiOS/Android/Webとフロントエンド周りを担当している [@kazutoyo](https://twitter.com/kazutoyo)です！

以前、React Native開発でCoding Agentを活用するためのSkillsを紹介しました。

<https://zenn.dev/tellernovel_inc/articles/7bb1facb9cfb4d>

今回は、Coding Agent自身がモバイルアプリを操作・検証できるようになるツールを2つ紹介します。

## Coding Agentに「自分の作業を検証する方法」を与えることの重要性

Claude Codeのベストプラクティスにも、「Claudeに自分の作業を検証する方法を与える」という項目があります。

[https://code.claude.com/docs/ja/best-practices#claude-に自分の作業を検証する方法を与える](https://code.claude.com/docs/ja/best-practices#claude-%E3%81%AB%E8%87%AA%E5%88%86%E3%81%AE%E4%BD%9C%E6%A5%AD%E3%82%92%E6%A4%9C%E8%A8%BC%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95%E3%82%92%E4%B8%8E%E3%81%88%E3%82%8B)

Webのフロントエンド開発であれば、ブラウザを操作させてスクリーンショットを撮るなど、比較的簡単に実現できます。しかしモバイルアプリ開発では、これまで難しかったのが実情でした。

エラーログを取得したり、実機・シミュレータのスクリーンショットを渡したりするには、人間がAIの手足となって情報を渡す必要があったのです。

それを解決するのが、今回紹介する Rozenite と agent-device です。

---

## Rozeniteとは

<https://www.rozenite.dev/>

RozeniteはReact Native DevToolsを拡張するためのフレームワークです。プラグインによって、標準のDevToolsにさまざまな機能を追加できます。

### 公式プラグインの紹介

**Expo Atlasプラグイン**

バンドルされたJSのサイズを分析するツール「Expo Atlas」をDevToolsから利用できます。どのモジュールがサイズを肥大化させているかを視覚的に確認できます。

<https://www.rozenite.dev/docs/official-plugins/expo-atlas>

**TanStack Queryプラグイン**

[TanStack Query DevTools](https://tanstack.com/query/v5/docs/framework/react/devtools)のReact Native版。クエリの監視やキャッシュされているデータの確認ができます。

<https://www.rozenite.dev/docs/official-plugins/tanstack-query>

**React Navigationプラグイン**

React NavigationのStateを確認できるツール。ディープリンクテストの実行なども可能です。

<https://www.rozenite.dev/docs/official-plugins/react-navigation>

**オーバーレイプラグイン**

実行中のアプリ上にグリッドや画像をオーバーレイして、デザインのズレを確認するためのツール。

<https://www.rozenite.dev/docs/official-plugins/overlay>

他にも [Redux DevTools](https://www.rozenite.dev/docs/official-plugins/redux-devtools)、[Performance Monitor](https://www.rozenite.dev/docs/official-plugins/performance-monitor)、[MMKV](https://www.rozenite.dev/docs/official-plugins/mmkv)、[Storage](https://www.rozenite.dev/docs/official-plugins/storage)、[Controls](https://www.rozenite.dev/docs/official-plugins/controls)、[Require Profiler](https://www.rozenite.dev/docs/official-plugins/require-profiler) などが公式プラグインとして提供されています。

### Rozenite for Agent

最近のバージョンでAgent向けの機能が追加されました。

これにより、DevToolsの機能やRozeniteのプラグイン機能を、Coding Agentが直接扱えるようになりました。

例えば、React NativeのエラーログをAI Agentが自ら取得し、そのままエラーを修正→動作確認という流れが自律的に行えます。

こちらはRozenite for AgentでClaude Codeがエラー内容を取得し、修正を行っている様子です。（動画は3倍速）  
![](https://static.zenn.studio/user-upload/be81add496d6-20260319.gif)

また、パフォーマンスのプロファイルやExpo Atlasの情報をAgentに渡すことで、アプリの品質向上も自律的に進められます。

これまでは人間がこれらの情報をAIに渡す必要がありましたが、ついにその役目から解放されそうです。

Rozenite用のAgent向けSkillも公開されているので、合わせて導入しておくとよりスムーズに使えます。

```
npx skills add https://github.com/callstackincubator/rozenite --skill rozenite-agent
```

---

## agent-device: AIにiOS/Androidアプリの「目と手」を与える

<https://github.com/callstackincubator/agent-device>

agent-deviceは、同じくCallstackによるAgent向けのCLIツールです。

Vercelの [agent-browser](https://github.com/vercel-labs/agent-browser)（ブラウザをAgentが操作するためのツール）にインスパイアされており、iOS/Androidで実行されているアプリをAgentが操作できるようになります。

内部的には、AndroidではADB、iOSでは`simctl`/`devicectl`を使ってアプリを操作しています。これらを直接使っても似たことはできますが、agent-deviceはそれらを抽象化し、プラットフォームを横断した統一APIを提供しているのが特徴です。

これを使うことで、AI AgentにiOS/Androidアプリの「目と手」を与えることができます。

例えば、AI Agent自身にアプリを操作させてスクリーンショットを撮りながら、気になる点を自律的に洗い出してもらうことが可能です。これにより「AI自身がアプリを触って確認しながら修正する」というループが実現できます。

以下はagent-deviceでClaude Codeにアプリを回遊させ、画面から気になるところを収集して、修正のプランを作成している様子です。（動画は8倍速）  
![](https://static.zenn.studio/user-upload/918cc57ff80a-20260319.gif)

agent-device用のSkillも公開されています。

```
npx skills add callstackincubator/agent-device
```

---

## まとめ

Claude Codeのベストプラクティスにも書かれていますが、「Claudeに自分の作業を検証する方法を与える」というのはCoding Agentが作業をするうえでとても重要なことです。

モバイルアプリ開発においてこれまで難しかったその課題を、RozeniteとAgent-deviceという2つのツールが解決してくれます。Rozeniteによってエラーログやパフォーマンス情報をAgentが自ら取得できるようになり、agent-deviceによってAgentがアプリを直接操作して目で確認できるようになりました。

これによって、モバイルアプリ開発でも人が介在せずに進められる範囲が大幅に広がります。開発スピードの向上にとても期待しています！

## 参考リンク

それでは、よいReact Nativeライフを！
