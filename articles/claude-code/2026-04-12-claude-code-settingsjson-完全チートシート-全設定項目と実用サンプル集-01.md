---
id: "2026-04-12-claude-code-settingsjson-完全チートシート-全設定項目と実用サンプル集-01"
title: "Claude Code settings.json 完全チートシート — 全設定項目と実用サンプル集"
url: "https://qiita.com/moha0918_/items/ef10d0e9beec96a4aee4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

Claude Codeは `settings.json` 1つで動作を細かく制御できる。しかし設定項目が多すぎて「どこに何を書けばいい？」と迷う人は多い。この記事ではスコープの選び方から各設定項目の実用サンプルまでを一枚のリファレンスとしてまとめた。

## 設定スコープ早見表

「どのファイルに書くか」がClaude Codeの設定でいちばん最初に理解すべきポイントだ。

| スコープ | ファイルパス | 有効範囲 | Gitで共有 |
| --- | --- | --- | --- |
| **Managed** | MDM/レジストリ or `managed-settings.json` | マシン全ユーザー | IT管理者が配布 |
| **User** | `~/.claude/settings.json` | 自分のすべてのプロジェクト | されない |
| **Project** | `.claude/settings.json` | そのリポジトリの全員 | **される** |
| **Local** | `.claude/settings.local.json` | 自分・このリポジトリのみ | されない |

優先度（高い順）: **Managed > コマンドライン引数 > Local > Project > User**

```
// ~/.claude/settings.json（ユーザー設定の例）
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "claude-sonnet-4-6",
  "language": "japanese",
  "autoUpdatesChannel": "stable"
}
```

`$schema` 行を追加すると VS Code / Cursor でオートコンプリートと入力補完が有効になる。追加しない理由はない。

---

## よく使う基本設定 チートシート

### モデル・動作系

| キー | 説明 | 設定例 |
| --- | --- | --- |
| `model` | 使用モデルの上書き | `"claude-sonnet-4-6"` |
| `effortLevel` | 思考の深さ（low/medium/high） | `"medium"` |
| `alwaysThinkingEnabled` | Extended Thinkingをデフォルト有効 | `true` |
| `showThinkingSummaries` | Thinkingの要約を表示 | `true` |
| `availableModels` | 選択可能なモデルを制限（管理用） | `["sonnet", "haiku"]` |
| `autoUpdatesChannel` | アップデートチャンネル（stable/latest） | `"stable"` |

### UI・表示系

| キー | 説明 | 設定例 |
| --- | --- | --- |
| `language` | Claudeの返答言語 | `"japanese"` |
| `outputStyle` | 出力スタイルのカスタマイズ | `"Explanatory"` |
| `spinnerTipsEnabled` | スピナー中のTips表示 | `false` |
| `prefersReducedMotion` | アニメーション削減（アクセシビリティ） | `true` |
| `showClearContextOnPlanAccept` | プラン承認時に「コンテキストクリア」を表示 | `true` |
| `fastModePerSessionOptIn` | Fast Modeをセッションごとに都度オプトインにする | `true` |

### セッション・ファイル系

| キー | 説明 | 設定例 |
| --- | --- | --- |
| `cleanupPeriodDays` | セッションファイルの保持日数（デフォルト30） | `14` |
| `plansDirectory` | プランファイルの保存先 | `"./plans"` |
| `autoMemoryDirectory` | メモリファイルの保存先 | `"~/my-memory"` |
| `respectGitignore` | `@`ファイルピッカーで.gitignoreを尊重 | `false` |
| `includeGitInstructions` | gitワークフロー指示をシステムプロンプトに含める | `false` |

### 認証・外部API系

| キー | 説明 | 設定例 |
| --- | --- | --- |
| `apiKeyHelper` | APIキーを動的生成するスクリプト | `"/bin/gen_key.sh"` |
| `awsCredentialExport` | AWS認証情報を出力するスクリプト（Bedrock用） | `"/bin/gen_aws.sh"` |
| `forceLoginMethod` | ログイン方法の強制（claudeai/console） | `"claudeai"` |
| `forceLoginOrgUUID` | 特定組織のみ許可（エンタープライズ向け） | `"xxxxxxxx-..."` |

---

## 権限設定（permissions）の書き方

`permissions` は安全性に直結する最重要セクション。

### 基本構造

```
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Read(~/.zshrc)"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "deny": [
      "WebFetch",
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ],
    "defaultMode": "acceptEdits",
    "additionalDirectories": ["../docs/"]
  }
}
```

評価順は **deny → ask → allow** の順。最初にマッチしたルールが勝つ。

### ルール構文一覧

| ルール例 | 効果 |
| --- | --- |
| `Bash` | すべてのBashコマンドにマッチ |
| `Bash(npm run *)` | `npm run` で始まるコマンドにマッチ |
| `Read(./.env)` | `.env`ファイルの読み取りにマッチ |
| `Read(./secrets/**)` | `secrets/`以下すべてにマッチ |
| `WebFetch(domain:example.com)` | example.comへのFetchにマッチ |
| `Edit(./src/**)` | `src/`以下のファイル編集にマッチ |

### defaultMode の選択肢

| 値 | 動作 |
| --- | --- |
| `default` | 都度確認（通常起動時のデフォルト） |
| `acceptEdits` | ファイル編集は自動承認 |
| `plan` | 実行前にプランを作成してから確認 |
| `auto` | AI判断で自動実行（高速だがリスクあり） |
| `bypassPermissions` | すべてを自動承認（CI用途） |

`bypassPermissions` はCI/自動化専用。対話型セッションでの使用は危険。  
`disableBypassPermissionsMode: "disable"` で組織全体で無効化できる。

---

## サンドボックス設定（sandbox）

サンドボックスはBashコマンドをファイルシステム・ネットワークからOSレベルで隔離する。

```
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker *"],
    "filesystem": {
      "allowWrite": ["/tmp/build", "~/.kube"],
      "denyRead": ["~/.aws/credentials"]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"],
      "allowUnixSockets": ["/var/run/docker.sock"],
      "allowLocalBinding": true
    }
  }
}
```

### サンドボックス主要設定

| キー | 説明 | デフォルト |
| --- | --- | --- |
| `enabled` | サンドボックスを有効化 | `false` |
| `autoAllowBashIfSandboxed` | サンドボックス内Bashを自動承認 | `true` |
| `excludedCommands` | サンドボックス外で実行するコマンド | `[]` |
| `failIfUnavailable` | 起動できなければ終了（マネージド設定用） | `false` |
| `filesystem.allowWrite` | 書き込みを許可する追加パス | `[]` |
| `filesystem.denyRead` | 読み取りを拒否するパス | `[]` |
| `network.allowedDomains` | 許可するドメイン（ワイルドカード可） | `[]` |
| `network.allowLocalBinding` | localhostポートへのバインド許可 | `false` |

パスの書き方: `/tmp/build`（絶対パス）、`~/path`（ホームディレクトリ相対）、`./path`（プロジェクトルート相対）。

---

## Worktree設定

大規模モノレポで `--worktree` 使用時にディスク使用量と起動時間を削減できる。

```
{
  "worktree": {
    "symlinkDirectories": ["node_modules", ".cache"],
    "sparsePaths": ["packages/my-app", "shared/utils"]
  }
}
```

| キー | 説明 |
| --- | --- |
| `symlinkDirectories` | メインリポジトリからworktreeへシンボリックリンクするディレクトリ |
| `sparsePaths` | sparse-checkoutで部分的にチェックアウトするパス |

---

## グローバル設定（~/.claude.json）

`settings.json` ではなく `~/.claude.json` に書く設定。settings.jsonに誤って書くとスキーマエラーになる。

| キー | 説明 | デフォルト |
| --- | --- | --- |
| `editorMode` | 入力プロンプトのキーバインド（normal/vim） | `"normal"` |
| `autoConnectIde` | 外部ターミナルから起動時にIDEへ自動接続 | `false` |
| `autoInstallIdeExtension` | VSCode拡張を自動インストール | `true` |
| `showTurnDuration` | 処理時間を表示 | `true` |
| `terminalProgressBarEnabled` | ターミナルプログレスバー | `true` |
| `teammateMode` | Agent Teamの表示方法（auto/in-process/tmux） | `"auto"` |

---

## Attribution設定（コミット帰属）

Claudeが作るコミットやPRに付く帰属表示をカスタマイズ・非表示にできる。

```
{
  "attribution": {
    "commit": "Generated with AI\n\nCo-Authored-By: AI <ai@example.com>",
    "pr": ""
  }
}
```

コミット・PR両方を非表示にするには `commit` と `pr` を空文字列にする。

---

## 実用的なサンプル集

### 個人開発向け（~/.claude/settings.json）

```
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "claude-sonnet-4-6",
  "language": "japanese",
  "effortLevel": "medium",
  "autoUpdatesChannel": "stable",
  "cleanupPeriodDays": 14,
  "permissions": {
    "defaultMode": "acceptEdits",
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

### チーム開発向け（.claude/settings.json）

```
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(git merge *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ],
    "defaultMode": "default"
  },
  "companyAnnouncements": [
    "PR前にnpm run lintを忘れずに"
  ]
}
```

### CI/CD向け（Headless実行）

```
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "defaultMode": "bypassPermissions",
    "deny": [
      "Bash(curl *)",
      "WebFetch"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "0"
  }
}
```

---

## まとめ

`settings.json` は個人設定からチーム共有・エンタープライズポリシーまで4つのスコープで柔軟に管理できる。まず `$schema` を追加してエディタ補完を有効にし、`permissions` の allow/deny/ask で危険な操作を制御するところから始めるのが最短コースだ。チームで使うなら `.claude/settings.json` をリポジトリに含めることで設定を統一でき、個人の試行錯誤は `settings.local.json` で安全に分離できる。
