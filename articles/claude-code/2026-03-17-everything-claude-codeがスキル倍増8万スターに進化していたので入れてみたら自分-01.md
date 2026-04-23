---
id: "2026-03-17-everything-claude-codeがスキル倍増8万スターに進化していたので入れてみたら自分-01"
title: "Everything Claude Codeがスキル倍増・8万スターに進化していたので入れてみたら、自分の設定が丸裸になった"
url: "https://zenn.dev/lova_man/articles/fa521ace28a12f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## 本文

### 結論から簡潔に

1. Everything Claude Code（ECC）を本番プロダクトに導入したのをきっかけに、`.mcp.json`にAPIキーが3つハードコードされていたのを発見した
2. MCPのタスク別切り替えで、コンテキスト消費が110,000→33,000トークンに（70%削減）
3. 既存のCLAUDE.mdやフックとの競合なくマージできた

この記事は、ECCの機能紹介ではなく、**本番運用中のプロダクトに入れて実際に何が見つかったか**の記録です。ECCの概要や設計思想は、末尾の参考リンクにある先行記事が詳しいので、そちらに譲ります。

---

### 何が見つかったか──APIキー3つ、直書きされていた

[Everything Claude Code（ECC）](https://github.com/affaan-m/everything-claude-code)は、GitHub 8万スター超のClaude Code向け設定集です（21エージェント、102スキル、52コマンド）。自分はクリエイター支援プラットフォーム「サポラバ」（Next.js 15 + Supabase + Stripe Connect）にプラグインとして導入しました。

入れて最初にやったのが、ECCのセキュリティ思想に影響を受けて設定ファイルを棚卸ししたことです。

そこで見つかったのがこれです。

```
# サポラバの .mcp.json に直書きされていたもの
- GitHub Personal Access Token: ghp_***
- Figma API Key: figd_***
- Supabase Access Token: sbp_***
```

`.gitignore`に含まれていたのでリモートにはプッシュされていませんでした。ただ、ローカルに生のAPIキーが平文で残っている状態でした。

---

### なぜ起きていたか──MCPの設定は「.envの外」にある

何が怖かったかというと、MCPの設定ファイルってClaude Codeの初期セットアップ時にサクッと作るものなので、「ちゃんと環境変数にしよう」という意識が薄くなりがちなんです。`.env`は厳重に管理しているのに、`.mcp.json`はノーガードだった。

これは自分だけの問題ではないと思います。Claude CodeのMCP設定は、通常の開発フローとは別の場所にあって、`.env`のように「ここには秘密情報がある」という共通認識がまだ薄い。コードレビューの対象にもなりにくい。

ECCからは`everything-claude-code:security-scan`コマンドで[AgentShield](https://github.com/affaan-m/agentshield)（別リポジトリのセキュリティスキャンツール）を呼べます。CLAUDE.md、settings.json、MCPサーバー設定、フック定義、エージェント定義を対象に、14パターンのシークレット検出、権限監査、プロンプトインジェクションリスクの分析をかけるものです。正直、「CLAUDE.mdのセキュリティ」なんて考えたこともなかったです。設定ファイル自体を監査するという概念が、ECCから学んだ一番大きな気づきでした。

---

### どう直したか①──APIキーを環境変数に移す

対策は単純です。

1. `.mcp.json`のAPIキーを環境変数参照に書き換え
2. `.mcp.json.example`テンプレートを作成（構造だけ残して値を消す）
3. `.gitignore`に`.mcp.json`が含まれていることを再確認

やること自体は`.env`の管理と同じです。ただ、「MCPの設定ファイルにも同じルールを適用する」という意識がなかった。それが今回の教訓です。

---

### どう直したか②──11万トークンの消費を3.3万に削減

ECCのガイドに「MCPを入れすぎると200kのコンテキストが70kまで縮む」という記述があります。MCPサーバーのツールスキーマ定義だけで、コンテキストウィンドウの半分以上が食われることがある、という話です。

これを読んで、サポラバプロジェクトでMCPの消費量を確認しました。Claude Code起動時のコンテキスト使用状況表示で、全MCP一括ロード時と、タスク別JSONに絞った場合の2条件を比較しました。結果、**全MCP一括ロードで約110,000トークン**が消費されていました。200kのコンテキストのうち55%がMCPのスキーマで埋まっていて、実際の作業に使えるのは90k以下です。

タスクの種類ごとにMCPの設定ファイルを分けて、必要なものだけロードする仕組みを作りました。

```
# タスクに応じて最適なMCP設定を自動適用するスクリプト
./scripts/claude-session.sh "UI改善"          → frontend.json（UI関連MCPのみ）
./scripts/claude-session.sh "マイグレーション" → database.json（Supabase MCPのみ）
./scripts/claude-session.sh "Stripe修正"      → payment.json（決済関連MCPのみ）
```

結果、タスク別に絞ることで**33,000トークン**まで削減できました。70%削減です。

体感の変化は明確でした。コンテキストに余裕があるので、長いファイルの読み込みや複数ファイルの比較がスムーズに通る。「コンテキストが足りなくて途中で切れる」という事故が激減しました。

ECCではこれを**コンテキストエンジニアリング**と呼んでいます。「AIを賢くする」のではなく「AIに渡す情報を整理する」というアプローチです。

---

### どう直したか③──既存設定と競合なくマージする

「ECCを入れたいけど、既存の設定と衝突しそうで怖い」という方は多いと思います。

結論から言うと、**プラグインとして入れれば競合しません**。

```
# プラグインとしてインストール
/plugin marketplace add affaan-m/everything-claude-code
/plugin install everything-claude-code@everything-claude-code

# 言語別ルールは別途
npx ecc-install typescript
```

プラグイン経由のスキルやコマンドは名前空間付き（例：`everything-claude-code:plan`）で呼ばれるため、既存のCLAUDE.mdやフックとは干渉しません。

自分はClaude Codeに以下の指示を出してマージしました。

```
ECCプラグインをインストールした。既存設定と最適にマージしてほしい。

方針：
- 既存のCLAUDE.mdの内容はすべて維持
- ECCのルールは~/.claude/rules/に言語別で入れる
- フックは既存のものを優先し、ECCの推奨フックで補完
- 競合がある場合はプロジェクト固有の設定を優先
```

CLAUDE.mdの冒頭に「ECC プラグイン導入済み」と明記して完了です。プロジェクト固有のルール（Stripe決済、RLS設計方針など）はそのまま維持できました。

---

### 導入後にやったこと──フックとコマンドの整備

マージした後、ECCの「AIの判断に委ねるのではなく、フックで機械的に実行する」という思想に影響を受けて、プロジェクト固有のフックを整備しました。

```
{
  "PostToolUse": [
    {
      "matcher": { "tool": "Edit", "filePath": "lib/" },
      "hooks": [{
        "type": "command",
        "command": "npx vitest run --reporter=dot --passWithNoTests 2>&1 | tail -5"
      }]
    }
  ],
  "PreToolUse": [
    {
      "matcher": { "tool": "Bash", "command": "git push" },
      "hooks": [{
        "type": "command",
        "command": "npm run lint && npm run typecheck"
      }]
    }
  ]
}
```

`lib/`配下を編集したら自動でVitestが走る。`git push`前にlintとtypecheckが強制される。Claudeに「テスト回してね」とお願いするのではなく、ファイルを触った瞬間にテストが走る。この差は大きいです。

カスタムコマンドも作りました。`/full-check`と打つだけで、lint → typecheck → test → build → widget build → validateの6ステップが自動で走り、1つでも失敗したら即停止してエラー報告。デプロイ前のヒューマンエラーがなくなりました。

別プロダクト（Lovai）ではフックはESLint自動修正の1つだけで、代わりにプロダクト固有のスキルとエージェントを自作する軽量な使い方をしています。ECCは全部入れる必要はなく、プロジェクトに合わせてグラデーションで使えます。

---

### 最小導入手順──まずセキュリティスキャンから

導入するなら、この順番がおすすめです。

**1. プラグインをインストールする**

```
/plugin marketplace add affaan-m/everything-claude-code
/plugin install everything-claude-code@everything-claude-code
npx ecc-install typescript  # 言語別ルール
```

**2. セキュリティスキャンをかける**

`everything-claude-code:security-scan`を実行して、既存の設定にリスクがないか確認します。自分はここでAPIキー3つを発見しました。

**3. MCPの棚卸しをする**

コンテキストの消費量を確認して、全MCPが本当に必要か見直します。タスク別にMCP設定を分けるだけで、コンテキストが数倍使えるようになる可能性があります。

**4. 3つのコマンドから始める**

`everything-claude-code:plan`（計画先行）、`everything-claude-code:tdd`（テスト先行）、`everything-claude-code:code-review`（自動レビュー）。まずはこの3つで十分です。

---

### 今回の導入で決めた運用ルール

この導入を通じて、3つのルールを決めました。

1. **`.mcp.json`は`.env`と同じ土俵で扱う。** APIキーは環境変数に移し、テンプレートだけリポジトリに入れる
2. **MCPはタスクごとに分ける。** 全部一括ロードしない。タスク別に設定ファイルを切り替える
3. **設定ファイルも定期監査する。** CLAUDE.md、settings.json、フック定義も、コードと同じようにレビュー対象にする

1ヶ月前の自分は、この3つのどれもやっていませんでした。ECCを入れなくてもできることばかりですが、入れたことで「やるべきだった」と気づけた。特に1つ目の「`.mcp.json`は`.env`と同じ土俵で扱う」は、たぶん同じ状態になっている人が多いと思います。

---

## 参考リンク
