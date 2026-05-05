---
id: "2026-05-04-claude-code-の設定ファイルを-gui-で生成する-web-アプリを-nextjs-16-01"
title: "Claude Code の設定ファイルを GUI で生成する Web アプリを Next.js 16 + Supabase で作った"
url: "https://zenn.dev/fune/articles/8240544470a0d4"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

<https://claudemd-hub.vercel.app/>

## はじめに

Claude Code を使い始めると、`CLAUDE.md` / `AGENTS.md` / `DESIGN.md` といった設定ファイルを書く機会が増えます。しかし毎回ゼロから書くのは手間で、チームや複数マシン間での共有も面倒です。

そこで、これらのファイルを **GUI でウィザード形式に生成・クラウド保存・ダウンロードできる Web アプリ** を作りました。

* CLAUDE.md — MCP ツール設定・リファクタリングルール・カスタム指示
* AGENTS.md — 技術スタック・Git 規約・アーキテクチャ方針
* DESIGN.md — カラーパレット・タイポグラフィ・コンポーネント規約

本記事では技術選定・アーキテクチャ・実装のポイントを解説します。

---

## 技術スタック

| カテゴリ | 採用技術 |
| --- | --- |
| フレームワーク | Next.js 16 (App Router) |
| UI | React 19 / @base-ui/react / Tailwind CSS v4 |
| アイコン | lucide-react |
| 認証 / DB | Supabase (Auth + PostgreSQL) |
| ホスティング | Vercel |
| ユーティリティ | clsx / tailwind-merge |

### なぜ Next.js 16 App Router か

Server Actions によりクライアント側に API を別途用意せずに CRUD が完結します。また `cookies()` を使ったサーバーサイドでの認証チェックが自然に書けます。

### なぜ @base-ui/react か

Radix UI の後継にあたるスタイルなしコンポーネントライブラリです。Tailwind CSS v4 と組み合わせて、デザイントークンに完全追従したコンポーネントを構築しやすい点を評価しました。

---

## アプリのルート構成

```
app/
├── page.tsx              # ランディング (ツール一覧)
├── layout.tsx            # ルートレイアウト
├── globals.css           # Tailwind v4 テーマトークン
├── actions.ts            # Server Actions (CRUD)
├── claude/page.tsx       # CLAUDE.md ジェネレーター
├── agent/page.tsx        # AGENTS.md ジェネレーター
├── design/page.tsx       # DESIGN.md ジェネレーター
├── files/
│   ├── page.tsx          # 保存済みファイル一覧
│   ├── config-list.tsx   # ファイルリストコンポーネント
│   └── upload-dialog.tsx # アップロードダイアログ
└── auth/
    ├── login/page.tsx
    ├── signup/page.tsx
    └── verify/page.tsx
```

---

## 認証の実装

Supabase Auth の SSR 対応パターンを採用しています。セッション情報は Cookie に保存し、Server Components から `cookies()` で取り出して使います。

### セッション同期フロー

クライアントサイドで Supabase JS SDK がログインを処理した後、取得した `access_token` / `refresh_token` を `/api/auth/sync` エンドポイントへ POST し、サーバー側で Cookie に書き込みます。

```
// app/auth/login/page.tsx (抜粋)
const { data, error } = await signInWithPassword(email, password)

await fetch('/api/auth/sync', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    accessToken: data.session.access_token,
    refreshToken: data.session.refresh_token,
  }),
})
```

こうすることで Server Components から Cookie を読むだけで認証状態を確認できます。

!

**標準パターンとのトレードオフ**

`@supabase/ssr` が推奨する標準パターンでは、Middleware でリクエストごとにトークンを自動更新するため、セッション切れをユーザーが意識しにくい利点があります。本実装はその仕組みを採用せず、ログイン時の一度きりの同期にとどめています。

* **メリット**: 実装がシンプルで、Middleware の複雑さを排除できる
* **デメリット**: アクセストークン（デフォルト 1 時間）が期限切れになるとそのままログアウト扱いになる。リフレッシュトークンを使った自動更新が必要なアプリでは `@supabase/ssr` の標準パターンを採用してください

また、クライアントサイドでトークンを取得して API エンドポイントへ POST する手法は、HTTPS 環境であれば安全に動作しますが、Cookie には `httpOnly` を付与して JavaScript からアクセスできないようにするとよりセキュアです。

```
// app/files/page.tsx (抜粋)
import { cookies } from 'next/headers'

const cookieStore = await cookies()
const accessToken = cookieStore.get('sb-access-token')?.value
if (!accessToken) redirect('/auth/login')
```

### Supabase REST API を直接呼ぶ

Server Actions からデータベースを操作する際、Supabase JS クライアントは使わず REST API を直接呼んでいます。

```
// lib/supabase-auth.ts
export function getSupabaseAuthHeaders(token: string) {
  return {
    Authorization: `Bearer ${token}`,
    apikey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  }
}
```

```
// app/actions.ts (抜粋)
export async function createConfigFile(name: string, content: string) {
  const accessToken = await getAccessToken()
  const user = await fetchSupabaseUser(accessToken)

  const response = await fetch(CONFIG_FILES_URL(), {
    method: 'POST',
    headers: jsonHeaders(accessToken, true),
    body: JSON.stringify({ user_id: user.id, name, content }),
  })
  // ...
}
```

Supabase の Row Level Security (RLS) を有効にしているため、`Authorization: Bearer <token>` を渡すだけでユーザー自身のデータのみアクセスできます。

### DB スキーマ

```
CREATE TABLE config_files (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name       TEXT NOT NULL,
  content    TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  UNIQUE(user_id, name)
);

ALTER TABLE config_files ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users access own configs"
  ON config_files FOR ALL
  USING (auth.uid() = user_id);
```

---

## ウィザード UI のパターン

各ジェネレーターページは「左カラムにナビゲーション、中央にフォーム、右カラムにプレビュー」という 3 ペイン構成です。

```
┌──────────────┬──────────────────────────┬─────────────────┐
│ WizardSidebar│  フォームセクション群     │ PreviewSavePanel│
│ 1 参照ファイル│                          │  (Markdownプレ  │
│ 2 言語設定   │  <SectionCard> x N        │   ビュー +      │
│ 3 MCPツール  │                          │   保存ボタン)   │
│ 4 リファクタ  │                          │                 │
│ 5 カスタム   │                          │                 │
└──────────────┴──────────────────────────┴─────────────────┘
```

ステップ一覧を表示し、クリックで対応セクションへスクロールします。`activeSection` props によりアクティブ状態を管理します。

```
// components/patterns/wizard-sidebar.tsx
export function WizardSidebar({ steps, activeSection, onNavigate }: WizardSidebarProps) {
  return (
    <aside className="hidden lg:block">
      <nav className="space-y-0.5">
        {steps.map((step, i) => {
          const StepIcon = step.icon
          return (
            <button
              key={step.id}
              onClick={() => onNavigate(step.id)}
              className={cn(
                'flex items-center gap-2 w-full text-left px-2.5 py-2 rounded-md text-xs',
                activeSection === step.id
                  ? 'bg-primary-surface text-primary font-semibold'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              )}
            >
              <span className="w-4 font-mono text-2xs opacity-40">{i + 1}</span>
              <StepIcon className="size-3" />
              <span>{step.label}</span>
            </button>
          )
        })}
      </nav>
    </aside>
  )
}
```

各ジェネレーターページでは以下のように定義するだけでサイドバーが完成します。

```
const WIZARD_STEPS = [
  { id: 'refs',        label: '参照ファイル', icon: Link2 },
  { id: 'language',   label: '言語設定',     icon: MessageSquare },
  { id: 'mcp',        label: 'MCPツール',    icon: Plug2 },
  { id: 'refactoring',label: 'リファクタリング', icon: Wrench },
  { id: 'custom',     label: 'カスタムルール', icon: Sliders },
] as const
```

---

## Markdown 生成ロジック

フォームの状態を受け取り Markdown 文字列を返す純粋な関数として切り出しています。

```
// lib/generate-claude.ts (概略)
export function generateClaudeMarkdown(config: ClaudeConfig): string {
  const lines: string[] = ['# CLAUDE.md']

  if (config.agentsPath) lines.push(`\n@${config.agentsPath}`)
  if (config.designPath)  lines.push(`@${config.designPath}`)

  if (config.language) {
    lines.push('\n## Language')
    lines.push(`- ${config.language}`)
  }

  if (config.mcpTools.length > 0) {
    lines.push('\n## MCP Tools')
    for (const tool of config.mcpTools) {
      lines.push(`\n### ${tool.name}`)
      lines.push(`**Trigger**: ${tool.trigger}`)
      lines.push(`**Tools**: \`${tool.tools}\``)
      if (tool.notes) lines.push(`**Notes**: ${tool.notes}`)
    }
  }

  // ...
  return lines.join('\n')
}
```

UI はこの関数を `useMemo` でリアクティブに呼び出し、右カラムのプレビューに渡すだけです。

```
const preview = useMemo(() => generateClaudeMarkdown(config), [config])
```

UI と生成ロジックが完全に分離されているため変更時の影響範囲も明確です。純粋関数なので、Vitest でのユニットテストも直感的に書けます。

```
// lib/generate-claude.test.ts
import { describe, it, expect } from 'vitest'
import { generateClaudeMarkdown } from './generate-claude'

describe('generateClaudeMarkdown', () => {
  it('agentsPath が指定されていれば @参照行を出力する', () => {
    const result = generateClaudeMarkdown({ agentsPath: 'AGENTS.md', designPath: '', language: '', mcpTools: [] })
    expect(result).toContain('@AGENTS.md')
  })

  it('mcpTools が空のときは MCP セクションを出力しない', () => {
    const result = generateClaudeMarkdown({ agentsPath: '', designPath: '', language: '', mcpTools: [] })
    expect(result).not.toContain('## MCP Tools')
  })

  it('mcpTools が 1 件あれば name と trigger を含む', () => {
    const tool = { name: 'Figma MCP', trigger: 'UI実装時', tools: 'get_design_context', notes: '' }
    const result = generateClaudeMarkdown({ agentsPath: '', designPath: '', language: '', mcpTools: [tool] })
    expect(result).toContain('Figma MCP')
    expect(result).toContain('UI実装時')
  })
})
```

DOM も外部 API も不要で、入力と出力だけを検証できます。

---

## MCP プリセット機能

よく使う MCP サーバーはプリセットとして用意し、ワンクリックで追加できます。

```
export const MCP_PRESETS = [
  {
    label: 'Figma',
    tool: {
      name: 'Figma MCP',
      trigger: 'UIコンポーネントの実装・修正時',
      tools: 'get_design_context, get_screenshot, get_metadata',
      notes: 'DESIGN.md のカラートークンはFigmaの値と同期済みのため、実装時はFigma MCPの値を正とする',
    },
  },
  {
    label: 'GitHub',
    tool: { /* ... */ },
  },
  {
    label: 'Supabase',
    tool: { /* ... */ },
  },
  // Context7, Playwright, Linear ...
]
```

---

## カスタムフック設計

### useFormState

認証フォームで共通して使うエラー状態とローディング状態を 1 つのフックに集約しました。

```
// lib/hooks/use-form-state.ts
export function useFormState() {
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  return {
    error,
    isLoading,
    setError: useCallback((msg: string) => setError(msg), []),
    setIsLoading,
    clearError: useCallback(() => setError(''), []),
  }
}
```

ログイン・サインアップ・パスワードリセットの全ページでこのフックを使い回すことで、フォームの状態管理コードを 1 箇所に集約しています。

### useSaveConfigFile

ファイル保存に関するロジック（ファイル名管理・保存上限チェック・フィードバック表示）を切り出したフックです。

```
// lib/hooks/use-save-config-file.ts (抜粋)
export function useSaveConfigFile(defaultFileName = 'DESIGN.md') {
  const [fileCount, setFileCount] = useState<number | null>(null)
  const [feedback, setFeedback] = useState<SaveFeedback>(null)

  const save = async (content: string) => {
    if (fileCount !== null && fileCount >= MAX_FILES) {
      setFeedback({ message: ERROR_MESSAGES.SAVE_LIMIT_REACHED, type: 'error' })
      return
    }
    // createConfigFile (Server Action) を呼ぶ
  }

  return { fileName, setFileName, isSaving, save, fileCount, maxFiles: MAX_FILES, feedback }
}
```

CLAUDE.md / AGENTS.md / DESIGN.md の 3 ページで同じロジックを使い回しています。

---

## Tailwind CSS v4 のテーマ設計

Tailwind v4 の `@theme` ブロックを使い、CSS 変数ベースのデザイントークンを定義しています。

```
/* app/globals.css (抜粋) */
@theme {
  --color-background: oklch(var(--background));
  --color-foreground: oklch(var(--foreground));
  --color-primary: oklch(var(--primary));
  --color-primary-surface: oklch(var(--primary) / 0.08);
  --color-muted: oklch(var(--muted));
  --color-muted-foreground: oklch(var(--muted-foreground));
  --color-destructive: oklch(var(--destructive));

  --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;

  /* text-2xs は標準 Tailwind に存在しないため独自定義 */
  --font-size-2xs: 0.625rem;

  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
}
```

ダークモードは `next-themes` と CSS 変数の切り替えで対応しています。`oklch()` を採用しているため、透過バリアント（`primary-surface` など）を CSS 側で柔軟に派生させられます。

---

## 工夫した点

### 同名ファイルの自動リネーム

ファイル名が既存と衝突する場合、`CLAUDE (2).md` のように連番サフィックスを付与します。

```
// app/actions.ts (抜粋)
let uniqueName = name
if (existingNames.has(name)) {
  const ext  = name.includes('.') ? name.slice(name.lastIndexOf('.')) : ''
  const base = name.includes('.') ? name.slice(0, name.lastIndexOf('.')) : name
  let counter = 2
  while (existingNames.has(`${base} (${counter})${ext}`)) counter++
  uniqueName = `${base} (${counter})${ext}`
}
```

### モバイルガード

ウィザード形式の UI はデスクトップ向けのため、スマートフォンでアクセスした場合は専用のメッセージを表示します。

```
// components/custom/mobile-guard.tsx
export function MobileGuard({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className="lg:hidden flex flex-1 items-center justify-center px-6">
        <p className="text-sm text-muted-foreground text-center">
          このページはデスクトップ環境でご利用ください
        </p>
      </div>
      <div className="hidden lg:contents">{children}</div>
    </>
  )
}
```

---

## 今後の展望

* **バージョン履歴**: ファイルの変更履歴を追跡する
* **インポート**: 既存の設定ファイルを読み込んでフォームに反映する
* **GitHub 連携**: リポジトリへ直接コミットする

---

## まとめ

* **Next.js 16 App Router + Server Actions** で、API ルートを増やさずに CRUD を完結できる
* **Supabase Auth の Cookie 同期パターン** で Server Components からシンプルに認証状態を参照できる
* **生成ロジックを純粋関数に分離** することで UI と疎結合になり、`useMemo` でリアクティブなプレビューが簡単に実現できる
* **カスタムフック** でフォーム状態・保存ロジックを共通化し、DRY を保てる
* **Tailwind CSS v4 の `@theme` + oklch** で柔軟なデザイントークン管理ができる

Claude Code の設定ファイルを書く手間を減らし、チームで統一した指示を使い回せる環境が整いました。ぜひ参考にしてみてください。

<https://claudemd-hub.vercel.app/>

---

## 参考リンク

---

## 著者
