---
id: "2026-05-13-mini-shai-hulud-第二波をきっかけに個人開発向けの-npm-oss-サプライチェーン攻-01"
title: "Mini Shai-Hulud 第二波をきっかけに、個人開発向けの npm / OSS サプライチェーン攻撃対策を整理した話"
url: "https://zenn.dev/n_tong/articles/3e1ed84f54c827"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "OpenAI", "GPT", "VSCode", "JavaScript"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

## はじめに

Mini Shai-Hulud 第二波の記事を読んで、npm / OSS サプライチェーン攻撃が他人事ではなくなった。

特に刺さったのは、TanStack Router のような信頼されているパッケージが侵害対象になっていた点だ。GMO Flatt Security の記事では TanStack Router を含む 200 超の侵害が整理されており、「怪しいパッケージを入れなければ大丈夫」という認識が崩れた。

私はセキュリティ専門家ではなく、普段は Next.js / SvelteKit / Astro / Vite、個人開発などで Tauri も触るフロントエンドエンジニアだ。だからこそ「完璧な対策」ではなく「個人開発でも続けられる対策」を整理したかった。

この記事では、ChatGPT と Claude に多角的に議論させながら、個人開発・小規模チーム向けの npm / OSS サプライチェーン対策をまとめた過程を共有する。

## Mini Shai-Hulud 第二波とは

npm などのパッケージエコシステムを狙ったサプライチェーン攻撃だ。自分のコードではなく、利用している依存パッケージや開発フローを経由して侵入される。

今回怖いと感じたのは、攻撃の流れが開発者の日常に近いことだ。

**1. 依存パッケージ経由で任意コードが動く**

npm には lifecycle script（インストール時に自動で走るスクリプト）がある。Tauri など Rust を含むプロジェクトでは `build.rs` というビルド時に動く仕組みもある。

**2. クレデンシャルの探索**

`.npmrc` の npm token、`~/.aws`、SSH 鍵、GitHub token などが狙われる可能性がある。

**3. 横展開**

`.github/workflows`、`.vscode`、`.claude`、OS の永続化設定などに仕込まれると、次回以降の開発や CI でも影響が続く可能性がある。

!

`npm audit` や Dependabot は、既知の CVE（既に登録・公開されている脆弱性）や、脆弱性があると分かっているパッケージバージョンの検知には有効。

一方で、今回のようなサプライチェーン攻撃では、問題が少し違う。たとえば、正規のパッケージの特定バージョンに悪性コードが混入したケースや、メンテナアカウントが侵害されて悪意あるリリースが出るケース、タイポスクワッティングで似た名前のパッケージを入れてしまうケースでは、検知やデータベース反映が後追いになる可能性がある。

つまり、「脆弱性のあるバージョンを避ける」だけでなく、「依存取得時に何が実行されるか」「開発環境から何が見えるか」「怪しい差分に気づけるか」まで見る必要がある。

「脆弱性スキャンを入れているから大丈夫」ではなく、依存取得・クレデンシャル管理・設定ファイル改ざん検知を組み合わせる必要があると感じた。

## AI に多角的議論をさせたプロセス

今回は、自分ひとりで考えるのではなく ChatGPT と Claude を使って議論を回した。

最初に ChatGPT 側で 3 人のペルソナを設定した。

* セキュリティアーキテクト
* コンテナ基盤エンジニア
* プロダクト開発リード

それぞれに「攻撃理解・devコンテナ設計・継続可能な運用設計」という役割を持たせ、20 発言の議論を行った。その後 Claude に議論内容を評価してもらい、不足点を指摘してもらった。その指摘を ChatGPT に戻して再議論する、というループを 4 ラウンドほど回した。

このループがかなり効いた。最初の議論では npm / devコンテナ / GitHub Actions まわりが中心だったが、Claude から「Tauri を使うなら Cargo や `build.rs` も見るべき」と指摘された。さらに次のラウンドでは「Tauri の署名情報や updater 秘密鍵をどこに置くか」まで踏み込む必要があると分かった。

`.claude/settings.json` の扱いも印象的だった。最初は「Claude Code を守る設定」として考えていたが、議論を重ねるうちに「**その設定ファイル自体が改ざん対象になる**」という再帰的なリスクに気づいた。

最終的には以下の 3 ファイルにまとめる形にした。

* `docs/security-roadmap.md`
* `docs/credentials-inventory.md`
* `docs/security-incident.md`

## 議論から得られた 3 原則

!

今回の対策は、次の 3 原則に集約した。

1. 盗まれるものを減らす
2. 改ざんに気づく
3. 危険操作を通常開発から分離する

## 原則 1: 盗まれるものを減らす

侵入されない前提ではなく、**侵入されたときに何を盗まれるか**を考えることが大事だった。

devコンテナを使っていても、GitHub token、AWS キー、npm publish token、SSH 鍵をコンテナに渡していたら、悪性コードから見えてしまう可能性がある。

そのため、通常開発で使う情報と、publish / deploy / 署名など本番環境や外部サービスに影響する操作で使う認証情報を分けることにした。

| 操作 | 方針 |
| --- | --- |
| `npm publish` | 通常開発から切り離す |
| `Tauri release` | 通常開発から切り離す |
| `AWS deploy` | 通常開発から切り離す |
| macOS 署名 | 通常開発から切り離す |

Tauri 込みの場合は、Apple Developer Certificate、notarytool credential、updater 秘密鍵も扱う。これらは通常の devコンテナには入れず、release 専用の環境や手動手順に分ける。

## 原則 2: 改ざんに気づく

危険なファイルの差分に気づけることが重要だ。

確認対象にしたいファイルは以下。

* `.github/workflows`
* `.vscode`
* `.claude`
* `package.json` の `scripts`
* lockfile
* Tauri 込みなら `Cargo.toml` / `Cargo.lock` / `src-tauri/tauri.conf.json`

`.claude/settings.json` も重要だ。Claude Code を守る設定そのものが改ざんされたら、AI ガードが無効化される可能性がある。

最初の一歩として以下のスクリプトを用意することにした。

scripts/security/check-sensitive-diff.sh

```
#!/usr/bin/env bash
set -euo pipefail
BASE_REF="${1:-origin/main}"
git diff --name-only "$BASE_REF"...HEAD -- \
  .github/workflows \
  .vscode \
  .claude \
  package.json \
  package-lock.json \
  pnpm-lock.yaml \
  yarn.lock \
  Cargo.toml \
  Cargo.lock \
  src-tauri/tauri.conf.json
```

保存先は `scripts/security/check-sensitive-diff.sh` とし、`package.json` には次のように追加する。

```
{
  "scripts": {
    "security:diff": "bash scripts/security/check-sensitive-diff.sh"
  }
}
```

## 原則 3: 危険操作を通常開発から分離する

devコンテナの目的は「コンテナに閉じ込めれば安全」というより、**コンテナから見える秘密情報を最小化すること**だと整理した。

CI でも同じ考え方になる。install / test / build job には secret を渡さず、publish / deploy / release job だけに必要最小限の権限を渡す。

Tauri 込みの場合は、署名・notarization・updater 秘密鍵を通常開発から切り離す。純フロントエンドの場合も、本番 deploy token や Cloudflare / Vercel / AWS の本番権限は通常 devコンテナへ渡さない。

## 対策の実装ロードマップ

### 今週やること（3 つだけ）

1. **クレデンシャル棚卸し**
2. **危険差分確認スクリプト作成**
3. **ホストで `npm install` しない運用の README 化**

クレデンシャル棚卸しの対象はこれだけある。

* GitHub PAT
* npm token
* AWS / GCP / Azure
* Docker Hub
* SSH 鍵
* Vercel、Cloudflare
* CMS API key
* Claude / OpenAI API key
* （Tauri 込みなら）updater 秘密鍵、Apple 証明書、notarytool credential

README には最低限これを書く。

```
## セキュリティ上の開発ルール

- 原則としてホスト PC で `npm install` / `pnpm install` / `yarn install` を実行しない
- 依存インストールは devコンテナ内で明示的に実行する
- `.github`、`.vscode`、`.claude`、`package.json`、lockfile の変更は人間レビュー必須
- production credential、npm publish token、AWS 本番キー、Tauri 署名 secret は devコンテナへ渡さない
```

### 今月やること

PR 単位で分けて進める。

* **PR2**: devコンテナ整備
* **PR3**: Claude Code ガード（hooks は最初は log モードから）
* **PR4**: Renovate / Dependabot / CI permissions 見直し

PR4 では通常更新は少し待ち、脆弱性対応は例外扱いにする考え方で整理する。

### 半年で整えること

* Tauri release 分離
* npm trusted publishing / provenance
* Takumi Guard 導入検討
* safe devcontainer
* SLSA 学習・導入判断

Takumi Guard は npm registry と開発環境・CI の間に proxy として入り、危険なパッケージの取得をブロックするサービスだ。devコンテナや CI の依存インストール経路に組み込めれば、悪性パッケージを踏むリスクを下げる選択肢になる。

## Claude Code での実装指示の工夫

「セキュリティを強化して」という依頼では粗すぎると実感した。Claude Code には PR 単位で依頼した方が安全だ。

今週版の Claude Code 依頼テンプレート

```
このプロジェクトに Mini Shai-Hulud 型の npm/OSS サプライチェーン攻撃対策の第一段階を入れたい。
以下を作成・更新してください。

1. `scripts/security/check-sensitive-diff.sh` を新規作成する。
   対象ファイル: `.github/workflows`、`.vscode`、`.claude`、
   `package.json`、`package-lock.json`（または `pnpm-lock.yaml` / `yarn.lock`）。
   Tauri プロジェクトの場合のみ、`Cargo.toml`、`Cargo.lock`、`src-tauri/tauri.conf.json` を追加する。
   スクリプトは `git diff --name-only` ベースで、BASE_REF を引数で受け取れるようにする。

2. `package.json` の `scripts` に `"security:diff": "bash scripts/security/check-sensitive-diff.sh"` を追加する。

3. README.md に以下の内容を追記する。
   - ホスト PC で npm / pnpm / yarn install を実行しない
   - 依存インストールは devコンテナ内で明示的に実行する
   - `.github`、`.vscode`、`.claude`、`package.json`、lockfile の変更は人間レビュー必須
   - production credential・npm publish token・AWS 本番キー・Tauri 署名 secret は devコンテナへ渡さない

既存の build・test・dev 挙動は変更しないこと。
作成後に「人間が確認すべきポイント」を箇条書きで出すこと。
```

## devコンテナと認証情報の設計

devコンテナは便利だが、万能ではない。大事なのは**コンテナに何を見せるか**だ。

最小構成はこう考えた。

.devcontainer/devcontainer.json

```
{
  "name": "safe-node-dev",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:22",
  "remoteUser": "node",
  "workspaceFolder": "/workspaces/${localWorkspaceFolderBasename}",
  "customizations": {
    "vscode": {
      "extensions": []
    }
  },
  "containerEnv": {
    "NODE_ENV": "development"
  }
}
```

ポイントはこれだけ。

* `postCreateCommand` で自動 install しない
* `~/.ssh` をマウントしない
* `~/.aws` をマウントしない
* `~/.npmrc` をマウントしない
* Docker socket を渡さない
* `remoteUser` は root にしない

!

devコンテナに渡さないものの例:

* npm publish token
* AWS 本番キー
* SSH 秘密鍵
* GitHub の広い権限を持つ PAT
* Docker Hub publish token
* Tauri 署名 secret
* Apple Developer Certificate
* notarytool credential

渡してよいのは、ローカル開発用の低権限な値や再発行しやすい一時的な情報だ。渡してはいけないのは、publish / deploy / 署名など、本番環境や外部サービスに影響する操作に使う認証情報だ。

## まとめ

ChatGPT と Claude に議論させることで、自分だけでは見落としやすい視点を拾えた。

特に以下は、普通に考えていたら後回しにしていたと思う。

* Cargo 側の `build.rs` リスク
* `.claude/` 改ざんの再帰性
* Claude Code hooks の誤検知バランス
* Tauri updater 秘密鍵の扱い

重要なのは全部を一気にやることではない。

* 盗まれるものを減らす
* 改ざんに気づく
* 危険操作を通常開発から分離する

この 3 原則を守りながら、まずは今週の 3 つから始めるのが現実的だ。

個人開発でも `security-roadmap.md`、`credentials-inventory.md`、`security-incident.md` のようなファイルをリポジトリに置いておくだけで、かなり意識が変わる。

## 参考リンク
