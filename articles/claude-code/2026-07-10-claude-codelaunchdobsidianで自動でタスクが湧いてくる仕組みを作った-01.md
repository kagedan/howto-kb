---
id: "2026-07-10-claude-codelaunchdobsidianで自動でタスクが湧いてくる仕組みを作った-01"
title: "Claude Code×launchd×Obsidianで「自動でタスクが湧いてくる」仕組みを作った"
url: "https://zenn.dev/carf/articles/4dd717f06b5844"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "Python", "zenn"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

# Claude Code×launchd×Obsidianで「自動でタスクが湧いてくる」仕組みを作った

Claude Codeにクラウドの定期ジョブを任せていると、ある問題にぶつかります。**AIは毎朝ちゃんと成果物をpushしてくれるのに、それを人間がレビューし忘れる。** この記事は、その取りこぼしを防ぐために作った「新規ファイル検知→タスク自動起票」の仕組みの記録です。

## 課題:レビュー待ちが物理的に見えない

私は content-factory というリポジトリで、AIに週次・日次で記事や小説の草稿を生成させています。生成ジョブ自体はクラウドのスケジュールルーティンとして動いており、完了すると GitHub に草稿ファイルを push してくれます。

ここで起きるのが「push されたことに気づかない」問題です。

* リポジトリを毎日開く習慣がない
* Obsidian(普段のタスク管理はここに集約している)を見ても、AIが何を生成したかは書かれていない
* 結果、レビュー待ちの草稿が数日〜1週間放置される

生成側(Claude Codeのジョブ定義)に手を入れて「pushしたらタスクも書け」とやる方法もありますが、生成プロンプトとタスク管理の関心事が混ざるのは避けたい。そこで、**生成側には一切触らず、外側から「新規ファイルの出現」だけを監視する独立スクリプト**を作ることにしました。

## 設計:ファイル=API、Obsidianを選ぶ理由

監視対象は3種類のパターンです。

```
PATTERNS = [
    "novel365/stories/*.md",
    "novel365/bekkan/*/chapters/*.md",
    "novel365/izen/*/chapters/*.md",
    "science-history/drafts/**/*.md",
]
```

タスクの置き場所には Obsidian の `Tasks.md` を選びました。理由は単純で、**Markdownファイルへの追記だけで完結する**からです。

* 認証もAPIキーも要らない(ファイルシステムに書くだけ)
* iCloud同期があるのでiPhoneの Obsidian アプリでもそのまま見える
* Obsidian側は普段使っているチェックリスト形式のタスクをそのまま使える(`- [ ]` 記法)

「通知アプリを作る」のではなく「自分がもう見ている場所に書き込む」ことを優先した設計です。

## 実装のポイント

### 1. ローカルだけでなくリモートの未pullファイルも検知する

一番ハマりやすいのがここです。Claude Codeのクラウドジョブはリモート(GitHub)にpushしますが、自分のMacで `git pull` するまではローカルに実ファイルが存在しません。ローカルの `glob` だけを見ていると、pullするまでタスクが起票されない=結局気づかない、という本末転倒が起きます。

そこで `git fetch` してリモートブランチのツリーを `ls-tree` で読み、ローカルとリモートを相対パスで同一視します。**checkout や pull はせず、読み取りだけ**なので作業ツリーは汚しません。

```
def scan() -> dict[str, Path | None]:
    """相対パス(=同一視キー) → ローカル実ファイル(リモートのみならNone) の辞書。"""
    found: dict[str, Path | None] = {}
    for root in ROOTS:
        if not root.is_dir():
            continue
        for pattern in PATTERNS:
            for p in root.glob(pattern):
                if "_TEMPLATE" in p.parts or not p.is_file():
                    continue
                found.setdefault(str(p.relative_to(root)), p)
    # リモート(クラウドジョブのpush先)。オフライン等で失敗したらローカルのみで続行
    try:
        git("fetch", "--quiet", "origin")
        ref = remote_ref()
        if ref:
            for rel in git("ls-tree", "-r", "--name-only", ref).splitlines():
                if "_TEMPLATE" in rel:
                    continue
                if any(fnmatch.fnmatch(rel, pat) for pat in PATTERNS):
                    found.setdefault(rel, None)
    except Exception as e:
        log(f"remote scan skipped: {e!r}")
    return found
```

ローカルパスが `None` のままだったファイルには、後段で「要git pull」の注記をタスク文言に付けます。これで「タスクは見えているのに実ファイルがない」という混乱を防いでいます。

### 2. 相対パスをキーにした状態ファイルで重複起票を防ぐ

Obsidian vault側とリポジトリ側の2箇所にファイルの実体があり得るため(`ROOTS` が2つ)、絶対パスではなく `content-factory` からの相対パスを同一視キーにしています。既知のキー集合は `.draft_watcher_state.json` に保存し、差分だけを新規扱いします。

初回実行時は既存ファイル全部を「既知」として記録するだけで、タスクは起票しません(そうしないと初回起動時に過去の草稿が全部タスク化されてしまいます)。

```
def main() -> None:
    current = scan()

    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps(sorted(current), ensure_ascii=False, indent=1))
        log(f"baseline: {len(current)} existing file(s) recorded, no tasks filed")
        return

    seen = set(json.loads(STATE_FILE.read_text()))
    new = {rel: p for rel, p in current.items() if rel not in seen}
    if not new:
        return
    ...
```

### 3. frontmatterのtitleを読んでタスク名を人間可読にする

ファイル名だけだと `chapter03.md` のような無機質な文字列になり、Tasks.mdを見返したときに何の話か分かりません。そこでMarkdownのfrontmatterから `title:` を正規表現で拾い、タスク文言に埋め込みます。ローカルにファイルがなければ `git show <ref>:<path>` で内容だけ読みます(こちらもcheckoutなしの読み取り専用)。

```
def read_title(rel: str, path: Path | None) -> str | None:
    """frontmatterのtitle:を読む(ローカル優先、リモートのみならgit showで読む)。"""
    try:
        if path is not None:
            head = path.read_text(encoding="utf-8", errors="replace")[:500]
        else:
            ref = remote_ref()
            head = git("show", f"{ref}:{rel}")[:500] if ref else ""
    except Exception:
        return None
    m = re.search(r"^title:\s*(.+)$", head, re.MULTILINE)
    return m.group(1).strip().strip('"') if m else None
```

生成されるタスクは、たとえばこんな形になります。

```
- [ ] 『◯◯』第3章の確認(novel365/izen/xxx/chapters/03.md) #novel365
- [ ] △△ の開架チェック→note公開判断(novel365/stories/yyy.md・要git pull) #novel365
```

### 4. launchdでの定期実行

30分おきに動かしたいだけなので、cronではなく launchd を使っています。`StartInterval` を秒数で指定し、`RunAtLoad` でログイン時にも1回走らせます。

```
<key>Label</key>
<string>com.user1.draftwatcher</string>
<key>ProgramArguments</key>
<array>
    <string>/usr/bin/python3</string>
    <string>/Users/user1/content-factory/scripts/draft_task_watcher.py</string>
</array>
<key>StartInterval</key>
<integer>1800</integer>
<key>RunAtLoad</key>
<true/>
```

### 5. 週次の完了タスク自動掃除

タスクは起票されっぱなしだとTasks.mdが肥大化するので、完了(`- [x]`)行だけを週1で削除するスクリプトも別途 launchd に登録しています。こちらはシェルスクリプト一枚です。

```
TMP=$(mktemp)
grep -v '^- \[x\]' "$TASKS_FILE" > "$TMP"
REMOVED=$(grep -c '^- \[x\]' "$TASKS_FILE")
mv "$TMP" "$TASKS_FILE"
echo "$(date): removed $REMOVED completed task(s)" >> "$LOG"
```

`StartCalendarInterval` で毎週月曜9時に実行するよう指定しています(`Weekday: 1` は月曜)。

### 6. 人間側の入口も同じファイルに集める(おまけ)

ここまではAI成果物の自動起票でしたが、人間の思いつきタスクも同じ場所に合流させています。仕組みはさらに単純で、Claude Codeの**メモリ(永続指示)に「メッセージが『t+スペース+内容』の形だったら、即座にTasks.mdへチェックボックスで追記する」というルールを覚えさせるだけ**です。

と打てば、会話の文脈が何であれ `- [ ] 牛乳を買う` がTasks.mdに増えます。スクリプトもホットキー登録も要りません。launchd側(自動検知)とメモリ側(人間の走り書き)で実装手段は違いますが、どちらも「Tasks.mdという1枚のMarkdownに書き込むだけ」という同じ出口に向かっているのがポイントで、結果としてAIが生成したレビュー待ちと自分の雑用が同じ画面に並びます。

## 運用してみて分かったこと

* **タスク文言の規約は、書いてみないと決まらない。** 最初は起票日を入れていたのですが、Tasks.mdを見返すと日付よりも「何のファイルか」が知りたい情報で、日付はノイズでした。運用しながら削りました。
* **状態ファイルを直接いじれば再起票できる。** チェックを外さずにタスク行をCmd+Zで消してしまっても、`.draft_watcher_state.json` から該当キーを消してやれば次回実行で復活します。事故った時の逃げ道として地味に効きます。
* **「要git pull」の注記は思ったより重要だった。** リモート検知を入れる前は、pull漏れのファイルがそもそも見えず、結局「気づかない」問題の一部が再発していました。checkoutせず読むだけ、という制約を守りながらここを埋めたのが今回の設計のキモです。

## おわりに

この仕組み自体も、設計からコードまでClaude Codeに書かせています。しかも「ローカル監視だけではpush済み未pullのファイルが漏れる」という設計上の穴は、私が指摘したのではなく、Claude Code自身が過去の運用メモ(生成ジョブはGitHub経由で届く、という記録)を読み返して気づき、リモート検知を足して塞ぎました。人間がやったのは要件を出したことと、タスク文言の言い回しを実際に使いながら調整したことくらいです。「AIに生成させ、人間はレビューと運用調整に専念する」という構図は、この監視スクリプト自体にも当てはまっていました。

次回は、Claude Codeを日常的に使い倒す中で溜まった実運用術(権限設定・スキル・エージェント分業まわり)をまとめる予定です。
