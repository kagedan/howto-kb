---
id: "2026-05-16-claude-codeでskillsを導入する-01"
title: "Claude CodeでSkillsを導入する"
url: "https://zenn.dev/yuna_aoki/articles/e4e317fe803956"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "TypeScript", "zenn"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

今回は、Claude Codeで自作Skillsを使う前提で設定します。

Claude CodeのSkillsは、`SKILL.md` というMarkdownファイルに指示をまとめておく仕組みです。

毎回プロンプトに長いレビュー観点を書くのではなく、よく使う観点をSkillとして登録しておくことで、React開発やテスト設計のレビューを依頼しやすくします。

## Skillsの配置場所

Claude Codeでは、以下のように `~/.claude/skills/` 配下にSkillを配置します。

```
~/.claude/
└── skills/
    ├── react-best-practices/
    │   └── SKILL.md
    ├── tailwind-design-system/
    │   └── SKILL.md
    ├── redux-toolkit-review/
    │   └── SKILL.md
    └── vitest-testing/
        └── SKILL.md
```

各Skillは、1つのディレクトリと `SKILL.md` で構成します。

## ディレクトリを作成する

まずは、Claude Code用のskillsディレクトリを作成します。

```
mkdir -p ~/.claude/skills/react-best-practices
mkdir -p ~/.claude/skills/tailwind-design-system
mkdir -p ~/.claude/skills/redux-toolkit-review
mkdir -p ~/.claude/skills/vitest-testing
```

## Reactレビュー用Skillを作成する

まずはReact / TypeScriptのレビュー用Skillを作成します。

```
touch ~/.claude/skills/react-best-practices/SKILL.md
```

`SKILL.md` に以下を記述します。

```
---
name: react-best-practices
description: React / TypeScript のコンポーネント設計、props設計、責務分離、パフォーマンスをレビューするときに使う
---

# React Best Practices

React / TypeScript のコードをレビューするときは、以下の観点で確認してください。

## レビュー観点

- コンポーネントの責務が大きすぎないか
- 表示用コンポーネントとロジックが分離されているか
- propsの設計が分かりやすいか
- useEffectの依存配列が適切か
- 不要な再レンダリングが起きやすい構成になっていないか
- mapのkeyが適切か
- TypeScriptの型定義が適切か
- anyに頼りすぎていないか
- データ取得処理がUIコンポーネントに密結合していないか
- 将来的なAPI通信を考慮した責務分離になっているか

## 出力形式

レビュー結果は以下の形式で出力してください。

1. 良い点
2. 気になる点
3. 修正した方がよい理由
4. 修正例
5. 優先度
```

## Tailwind CSSレビュー用Skillを作成する

次に、Tailwind CSS v4とUI設計のレビュー用Skillを作成します。

```
touch ~/.claude/skills/tailwind-design-system/SKILL.md
```

```
---
name: tailwind-design-system
description: Tailwind CSS v4を使ったUI設計、余白、色、コンポーネント共通化、アクセシビリティをレビューするときに使う
---

# Tailwind Design System

Tailwind CSS v4を使ったUIをレビューするときは、以下の観点で確認してください。

## レビュー観点

- 余白や文字サイズに一貫性があるか
- 色の使い方が分かりやすいか
- Button、Input、Select、Badge、Cardなどに共通化できる箇所がないか
- classNameが長くなりすぎて可読性が落ちていないか
- レスポンシブ対応で崩れそうな箇所がないか
- hover、focus、disabledなどの状態が考慮されているか
- アクセシビリティ上の問題がないか
- Tailwind CSS v4の前提に合っているか

## 注意点

Tailwind CSS v4では、基本的に以下を前提としてください。

- Viteでは `@tailwindcss/vite` を使用する
- `src/index.css` には `@import "tailwindcss";` を書く
- `@tailwind base;`、`@tailwind components;`、`@tailwind utilities;` は使わない
- `tailwind.config.js` は基本不要

## 出力形式

レビュー結果は以下の形式で出力してください。

1. 良い点
2. 気になる点
3. 共通コンポーネント化できる箇所
4. 修正例
5. アクセシビリティ上の注意点
```

Redux Toolkitの状態管理を確認するためのSkillも作成します。

```
touch ~/.claude/skills/redux-toolkit-review/SKILL.md
```

```
---
name: redux-toolkit-review
description: Redux Toolkitのstate設計、slice設計、createAsyncThunk、loading/error管理、API連携をレビューするときに使う
---

# Redux Toolkit Review

Redux Toolkitを使った状態管理をレビューするときは、以下の観点で確認してください。

## レビュー観点

- stateの構造が分かりやすいか
- Reduxで管理すべき状態とローカルstateでよい状態が分かれているか
- actionの責務が適切か
- reducerが複雑になりすぎていないか
- createAsyncThunkの使い方が自然か
- loading / error の管理が適切か
- repository層との責務分離ができているか
- 将来的にAPI通信へ切り替えやすいか
- selectorに切り出した方がよい処理がないか
- TypeScriptで型安全に扱えているか

## 今回のプロジェクト前提

人材管理SaaS風アプリでは、以下の状態を扱います。

- employees
- selectedEmployee
- searchCondition
- loading
- error

社員情報の取得・登録・更新・削除は、repository層を経由する方針です。

## 出力形式

レビュー結果は以下の形式で出力してください。

1. 良い点
2. 気になる点
3. Reduxに持つべきではない可能性がある状態
4. selector化した方がよい処理
5. 修正例
```

## Vitestテスト設計用Skillを作成する

最後に、Vitestでテストケースを考えるためのSkillを作成します。

```
touch ~/.claude/skills/vitest-testing/SKILL.md
```

```
---
name: vitest-testing
description: Vitestで単体テスト、Reactコンポーネントテスト、Redux Sliceのテストケースを考えるときに使う
---

# Vitest Testing

Vitestでテストケースを考えるときは、以下の観点で確認してください。

## テスト観点

- 正常系
- 異常系
- 空データ
- 境界値
- 複数条件の組み合わせ
- エラー時の挙動
- モックが必要な箇所
- テスト名が分かりやすいか
- 実装詳細に依存しすぎていないか
- 将来的な仕様変更で壊れやすい箇所を確認できているか

## 優先してテストしたい対象

- filterEmployees
- employeeLabels
- employeeSlice
- React Hook Form + Zodのバリデーション
- EmployeeTable
- EmployeeSearchForm

## 出力形式

以下の形式で出力してください。

1. テストすべき観点
2. 優先度
3. テストケース一覧
4. Vitestのコード例
5. 注意点
```

## Claude Codeで使う

Skillを作成したら、Claude Codeを起動して対象プロジェクトを開きます。

```
cd employee-profile-app
claude
```

その後、以下のように依頼します。

```
react-best-practices の観点で EmployeeListPage.tsx をレビューしてください。
```

または、直接スラッシュ付きで呼び出せる場合は以下のように使います。

```
/react-best-practices EmployeeListPage.tsx をレビューしてください。
```

Redux Sliceをレビューしたい場合は、以下のように依頼します。

```
redux-toolkit-review の観点で employeeSlice.ts をレビューしてください。
```

Vitestのテストケースを考えてもらう場合は、以下のように依頼します。

```
vitest-testing の観点で filterEmployees のテストケースを洗い出してください。
```

Tailwind CSSのUIレビューをしたい場合は、以下のように依頼します。

```
tailwind-design-system の観点で EmployeeTable のUIをレビューしてください。
```

## 使うときのポイント

Skillを作っただけで終わりにせず、実際の開発では以下のように使います。

```
実装する
↓
Claude Codeでレビュー依頼する
↓
指摘内容を確認する
↓
必要なものだけ修正する
↓
修正理由をZenn記事やREADMEに残す
```

AIの提案は便利ですが、すべてをそのまま採用する必要はありません。

今回のアプリは学習用・ポートフォリオ用なので、複雑にしすぎず、今の目的に合う改善だけを取り入れるようにします。
