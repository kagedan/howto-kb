---
id: "2026-06-05-claude-code-v21163-リリース毎日changelog解説-01"
title: "Claude Code v2.1.163 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/6b34f99ee37efd372834"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-06-05"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

2.1.163 が公開。組織配布での運用を固める変更と、`claude -p` 周りの長年のハマりどころ修正が中心です。

### 今回の注目ポイント

1. **バージョン範囲の強制** `requiredMinimumVersion` / `requiredMaximumVersion` で範囲外の起動を拒否
2. **`/plugin list` 追加** インストール済みプラグインを一覧、`--enabled` / `--disabled` で絞り込み
3. **`/btw` に「c to copy」** 回答の生 Markdown を整形保ったままクリップボードへ
4. **Stop フックの additionalContext** フックエラー扱いにせずターンを継続
5. **`claude -p` の無限ハング修正** 終わらないバックグラウンドコマンドを結果の約5秒後に停止
6. **Bedrock/Vertex/Foundry の CI 起動失敗修正** `CI=true` かつ API キー未設定でも起動できる

## 組織で使えるバージョンを範囲で縛る

:::note info
対象読者: チーム・組織で Claude Code を配布、管理している人
:::

managed settings に `requiredMinimumVersion` と `requiredMaximumVersion` が入りました。許可レンジの外だと Claude Code は起動を拒否し、承認済みバージョンへユーザーを誘導する。

例えば managed settings をこう書く。

```json
{
  "requiredMinimumVersion": "2.1.160",
  "requiredMaximumVersion": "2.1.163"
}
```

これで 2.1.159 以下と 2.1.164 以上は弾かれます。何が嬉しいか。組織として検証済みのバージョンだけを全員に使わせられる。新バージョンで挙動が変わって社内のフックやスキルが壊れる、といった事故を上限側で止められます。下限側は、古いバージョンに残る既知の不具合を踏ませない用途。

CI でイメージをピン留めするのと同じ縛りが、エンドユーザーの手元にも効くようになった(2.1.163 で追加)。

---

## Stop / SubagentStop フックで会話を止めずに差し戻す

:::note info
対象読者: フックで Claude の出力や完了をチェックしている人
:::

Stop と SubagentStop フックが `hookSpecificOutput.additionalContext` を返せるようになりました。これまではフックから何かを伝えると、フックエラーとして扱われていた。

```json
{
  "hookSpecificOutput": {
    "additionalContext": "テストがまだ通っていません。修正を続けてください"
  }
}
```

Stop フックでこれを返すと、エラーのラベルが付かないままフィードバックが Claude に渡り、ターンが継続する。「lint が通るまで止めない」「テスト緑まで作業を続けさせる」といったガードを、エラー扱いにせず組めます(2.1.163 で追加)。

---

## `claude -p` が結果の後で固まる問題

バックグラウンドで起動したコマンドが終了しないと、最終結果を出したあとの `claude -p` が永久に止まる場合がありました。今回は stdin が閉じたあと、結果の約5秒後にバックグラウンドシェルを停止します。CI やスクリプトで回している人向けの修正。

あわせて、`CI=true` かつ Anthropic API キー未設定の環境で、Bedrock / Vertex / Foundry を使っていても「ANTHROPIC_API_KEY required」で落ちる問題も解消(どちらも 2.1.163)。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| 2.1.163 | Skills | `\$` エスケープ | コマンド本文で数字の前にリテラルの `$` を書ける |
| 2.1.163 | MCP | セッションID共有 | stdio MCP サーバが `--resume` 時に hooks/Bash と同じ `CLAUDE_CODE_SESSION_ID` を受け取る |
| 2.1.163 | agents | 背面アップデート | バックグラウンドのエージェントセッションが裏でバージョン更新、再開時のコールド再起動待ちが消えた |
| 2.1.163 | UI | /メニュー | 組み込みコマンド・スキルの説明がより明確に |
| 2.1.163 | UI | 起動時表示 | サブスク切替の提案をトーストでなく起動時アナウンス枠に表示 |
| 2.1.163 | agents | 作業ディレクトリ | 状態グループ表示からの dispatch が、エージェントビューを開いたディレクトリで開始 |

<details><summary>バグ修正(10件)</summary>

- `$TMPDIR` が全コマンドで `/tmp/claude-{uid}` に上書きされ、bazel や EDR 保護下の Go ワークフローで bash が失敗していた(2.1.154 のリグレッション)。サンドボックス時のみの挙動に戻した
- Windows でセッション env ディレクトリが読み取り専用属性、または OneDrive 配下のとき「EEXIST: file already exists」で Bash が失敗する問題
- 新規 config ディレクトリでの起動中に managed settings の取得が完了すると、組織管理の権限ルールがセッション全体で適用されない問題
- `claude agents` のバックグラウンドセッションが、Claude Code 更新後の再アタッチで実行中タスクを失う問題
- エージェントビューを Esc で抜けるときの端末表示崩れと数秒のハング
- デスクトップアプリでバックグラウンドタスクのチップの Stop を押しても、既にプロセスが消えているとチップが消えない問題
- 終端マーカーが端末に取りこぼされたペーストのあと、キーボード入力が永久に効かなくなる問題
- フックの `if: "Bash(...)"` 条件が `$()` や `$VAR` を含む全 Bash コマンドで発火していた。サブシェルやバッククォート内のコマンドにもマッチするよう修正
- ホームディレクトリパスの deny ルール(例 `Read(~/Desktop/**)`)が、`$HOME` 経由で参照する Bash コマンドをブロックしない問題
- /mcp や /plugins などのパネルダイアログを閉じたあとにトランスクリプトへ残る「(no content)」行

</details>

## まとめ

2.1.163 は新機能より、組織配布と CI 運用まわりの穴埋めが中心。`requiredMinimumVersion` / `requiredMaximumVersion` での範囲固定と `claude -p` のハング修正は、CI やチーム配布で効きます。Stop / SubagentStop フックの `additionalContext` で、テスト未通過を理由に作業を続けさせる、といったガードも書けるようになった。
