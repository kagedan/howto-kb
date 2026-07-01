---
id: "2026-07-01-claudecowork-plugin-の-install-が静かに失敗する話-01"
title: "ClaudeCowork plugin の install が静かに失敗する話"
url: "https://qiita.com/ryoji9702/items/19b40e4707666f3b5730"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "cowork", "qiita"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

`mattpocock/skills` の 18 個を Cowork の `.plugin` ファイルにまとめて、自分のマーケットに上げて install しようとしたら、**upload は通るのに install ログだけ出ない**という静かな失敗に昔遭遇しました。

エラーメッセージが何も出ないのが厄介ですが、`bisect`（二分探索）で 1 時間以内に原因を 4 つ特定できたので、その手順と「Cowork plugin の暗黙の validation ルール」をまとめておきます。同じことをやろうとしている人がエラーで詰まる前に読んでほしい記事です。

### 環境・前提

- Claude Cowork（2026 年 6 月時点）のプライベートマーケットに `.plugin`（zip）を upload する構成
- 題材は `mattpocock/skills` の 18 スキル
- ログは Cowork のデスクトップアプリが吐く `[RemotePluginManager]` などのログ出力を参照

## 1. 何が起きたか

やりたかったことはシンプルです。

1. `mattpocock/skills` を clone
2. 18 個の `SKILL.md` を `.claude-plugin/marketplace.json` と一緒に `matt-pocock-skills.zip` に固める
3. Cowork のプライベートマーケットに upload
4. install ボタンを押す

**期待**: ログに `Installed plugin: matt-pocock-skills` が出る
**現実**:

```text
[info] [remoteUploadOps] uploadPluginViaRemote filename=matt-pocock-skills.zip bytes=67760 overwrite=true
[info] [remoteMarketplaceClient] uploadAccountPlugin marketplaceId=... filename=matt-pocock-skills.zip bytes=67760 overwrite=true
（…Installed plugin ログが出ない）
```

**upload は成功しています**。でも `RemotePluginManager` の `Installed plugin:` ログが出ません。エラーメッセージもなく、UI 上も「install ボタンを押した」感覚で終わります。これが厄介です。

ちなみに、対照実験として **テスト用の 2 スキルだけ入れた `mp-test.plugin`** を投げると `Installed plugin: mp-test` がちゃんと出ます。**18 個まとめると validation で何かに引っかかっている**ことが分かりました。

## 2. なぜ bisect で攻めることにしたか

最初は SKILL.md のスキーマを 1 個ずつ点検しようとしましたが、**18 個 × 数十行を目で追うのは非効率**です。それより次の手順を採りました。

1. **18 個を半分（9 個ずつ）に分ける**
2. **どちらの半分が install 失敗するかをログで判定**
3. **失敗側をさらに半分にする**
4. **これを繰り返す**

log₂(18) ≈ 4.2 なので、**最大 5 回の install 試行で原因が特定できる**という見立てです。エラーメッセージが出ない以上、「外側から二分する」のがいちばん速いと考えました。

> **学び**: エラーメッセージが無い／不十分なシステムでは、**「個別調査」より「分割統治」が圧倒的に速い**。binary search は人間の手作業でも有効。

## 3. bisect の実際の手順とログ

時系列で実際の試行を貼っておきます。

### ステップ 1: 9 個ずつに分割

- `mp-batch-a` （前半 9 個: caveman 〜 prototype）
- `mp-batch-b` （後半 9 個: scaffold-exercises 〜 zoom-out）

ログ結果：

```text
[info] [RemotePluginManager] Installed plugin: mp-batch-b
（batch-a の Installed ログは出ない）
```

→ **batch-a の 9 個** に犯人がいる。

### ステップ 2: 9 個を 5 / 4 に分割

- `mp-a1` （5個: caveman, diagnose, git-guardrails-claude-code, grill-me, grill-with-docs）
- `mp-a2` （4個: handoff, improve-codebase-architecture, migrate-to-shoehorn, prototype）

ログ結果：

```text
[info] [RemotePluginManager] Installed plugin: mp-a2
（a1 は出ない）
```

→ **a1 の 5 個**に犯人。

### ステップ 3: 5 個を 2 / 3 に分割

- `mp-a1a` （2個: caveman, diagnose）
- `mp-a1b` （3個: git-guardrails-claude-code, grill-me, grill-with-docs）

ログ結果：

```text
[info] [RemotePluginManager] Installed plugin: mp-a1a
（a1b は出ない）
```

→ **a1b の 3 個**に犯人。

### ステップ 4: 3 個を 1 個ずつ単独 install

- `mp-gg` （git-guardrails-claude-code 単独）
- `mp-gm` （grill-me 単独）
- `mp-gwd` （grill-with-docs 単独）

ログ結果：

```text
[info] [RemotePluginManager] Installed plugin: mp-gm
[info] [RemotePluginManager] Installed plugin: mp-gwd
（mp-gg だけ Installed ログが出ない）
```

→ **犯人は `git-guardrails-claude-code`** に確定。

ここまで **4 回の install 試行で 18 個から 1 個まで絞り込めました**。所要時間 15 分です。

## 4. では `git-guardrails-claude-code` の何がダメだったのか

ファイル数は SKILL.md + scripts/*.sh だけで、構造は他のスキルと変わりません。ファイル内容のどこかが弾かれているはずです。

これも bisect で 3 通り作って試しました。

| variant | 変更点 |
| --- | --- |
| `mp-gg-noscripts` | `scripts/` フォルダを丸ごと削除（.sh ファイルが原因？） |
| `mp-gg-rename` | スキル名を `git-guardrails` に変更（`-claude-code` 接尾辞が原因？） |
| `mp-gg-content` | SKILL.md 本文中の "Claude Code" を別表現に置換（本文中の語が原因？） |

結果：

```text
[info] [RemotePluginManager] Installed plugin: mp-gg-rename
（noscripts も content も Installed ログが出ない）
```

→ **`mp-gg-rename` だけ通った**。

**確定した原因**: スキル名（`name:` フィールド）に **`claude-code`** という文字列が含まれると validation で弾かれます。

Cowork 内部で `claude-code` をネームスペースとして予約しているか、あるいは Anthropic 公式と衝突するスキル名を `claude-code` プレフィックス / サフィックス検出で除外しているらしいです。**スキル名を `git-guardrails` にリネームしただけで install 成功**しました。

## 5. ついでに見つかった「silent しきってない validation エラー」

18 個を bisect する過程で、`mp-batch-b` 側でも別の落とし穴を見つけました。こちらは少しまし（ログにヒントが出ることもある）ですが、それでも沈黙する場合があります。

### 5.1 `disable-model-invocation` フィールド

`setup-matt-pocock-skills` と `zoom-out` の SKILL.md frontmatter に：

```yaml
disable-model-invocation: true
```

という行がありました。Anthropic の Skill 仕様には存在するフィールドですが、**Cowork 側の validator は未知のフィールドとして弾きます**。削除したら通りました。

### 5.2 `argument-hint` フィールド

`handoff` の frontmatter に：

```yaml
argument-hint: "[reason for handoff]"
```

がありました。これも Cowork validator は受け付けません。削除で通ります。

### 5.3 複数行 description

`caveman` の description が複数行 YAML（`description: |` の literal block）になっていました。**Cowork は description を 1 行に圧縮していないと弾きます**。

```yaml
# Before (NG)
description: |
  Ultra-compressed communication mode.
  Cuts token usage ~75% by dropping filler
  while keeping full technical accuracy.

# After (OK)
description: "Ultra-compressed communication mode. Cuts token usage ~75% by dropping filler while keeping full technical accuracy."
```

これも install ログが出ないだけで、エラーメッセージが何も出ませんでした。**bisect しなかったら永遠に気付かなかった**と思います。

## 6. 「Cowork plugin の暗黙ルール」まとめ

bisect の結果、今回ぶつかった validation ルールは 4 つでした。

| ルール | 影響を受けたスキル | 修正 |
| --- | --- | --- |
| **スキル名に `claude-code` を含めない** | `git-guardrails-claude-code` | `git-guardrails` にリネーム |
| **`disable-model-invocation` フィールドを削除** | `setup-matt-pocock-skills`, `zoom-out` | 行ごと削除 |
| **`argument-hint` フィールドを削除** | `handoff` | 行ごと削除 |
| **`description` は 1 行に圧縮** | `caveman` | literal block → flow scalar |

すべて **エラーメッセージが出ない** タイプの validation です。これは「Skill 仕様 = Anthropic 公式」と「Cowork が受け付ける subset」が完全には一致していないことを意味します。

## 7. 学んだこと

### 7.1 「エラーが出ない失敗」には bisect

ログを読み込んで仮説を立てるより、**入力を半分にして binary search する方が確実かつ速い**です。今回は 4 回の試行で原因を 1 個に絞れました。「コンパイル通ったけど挙動が変」「テストが落ちるけど原因不明」みたいなケースでも同じパターンが使えます。

### 7.2 Cowork plugin の SKILL.md は Anthropic 公式仕様の subset

「Anthropic 公式 docs に書いてあるフィールドが全部使える」とは限りません。**Cowork 側は controlled な subset しか受け付けていない**ようです。今後 plugin を作る際は、最初に **frontmatter を最小限（`name` と `description` のみ）に絞ってから足していく**のが安全です。

### 7.3 スキル名のネームスペース予約

`claude-code` を含む名前は弾かれます。おそらく公式エコシステムとの衝突を防ぐためのガードでしょう。**自作スキルに公式製品名を冠するのは避けたほうがいい**です。

### 7.4 ログを「出ること」と「出ないこと」で読み分ける

`Installed plugin:` ログは **「validation を通った」** のシグナルです。`uploadPluginViaRemote` は **「Anthropic のオブジェクトストレージに乗った」** だけのシグナルです。**この 2 つを別物として読むことが、デバッグの第一歩**でした。

## まとめ

- Cowork plugin の install には **エラーメッセージが出ない validation failure** がある
- 18 個まとめて失敗する状況は **bisect で 4 回の試行 / 15 分** で原因スキルを特定できる
- 今回ぶつかった暗黙ルール: **スキル名 / disable-model-invocation / argument-hint / 複数行 description**
- frontmatter は **`name` + `description` のみ** から始めて、必要に応じて足すのが安全
- 「エラーが出ない失敗」は **入力分割の binary search** が最速の調査法

「他人の Skill 集を `.plugin` で配布したい」というニーズはこれから増えるはずです。**沈黙する validation で 1 日溶かす前に、bisect を覚えておきましょう**。

## 参考

- [mattpocock/skills — GitHub](https://github.com/mattpocock/skills)
- [Claude Skills 公式ドキュメント — Anthropic](https://docs.claude.com/en/docs/build-with-claude/skills)
- [Use plugins in Claude Cowork — Claude Help Center](https://support.claude.com/en/articles/13837440-use-plugins-in-claude-cowork)
- [Claude Code Plugins reference — Claude Code Docs](https://code.claude.com/docs/en/plugins)
