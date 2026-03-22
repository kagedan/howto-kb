# frontmatter タイトル問題の修正記録

**日付**: 2026-03-22
**対象**: howto-kb リポジトリの収集スクリプトおよび既存記事

---

## 発見した問題

### 問題1: タイトル内の `\"` （バックスラッシュ+クォート）— 15件

**原因**: `_generate_mds.py` の `write_md()` 関数（旧110行目）

```python
title = article["title"].replace('"', '\\"')
```

RSS/X から取得したタイトルに `"` が含まれる場合、`\"` としてYAML frontmatterに書き出していた。
YAML double-quoted value 内の `\"` は `parse_frontmatter`（簡易パーサー）では正しく解釈できず、
`build_index.py` → `json.dumps()` で `\\"` となり、JSONパーサーが文字列終了と誤解釈するチェーンが発生。

**例**:
```yaml
title: "【第2回】AIエージェントに\"憲法\"を与えたら開発が変わった話"
```

### 問題2: マルチラインタイトル — 108件（実質106件は問題1と別）

**原因**: 同じ `write_md()` 関数で、タイトルに含まれる改行を除去せずにfrontmatterに書き出していた。

X投稿のテキストは改行を含むことが多く、タイトルが複数行にまたがると
`parse_frontmatter` が1行目しか読まないためタイトルが途中で切れる。

**例**:
```yaml
title: "@GabriellaG439: New blog post: \"A sufficiently detailed spec is code\"

I wro"
```

### 問題3（付随）: WindowsのパイプによるJSONパースエラー

`cat index.json | python -c "json.load(sys.stdin)"` でエラーが出る。
原因はindex.jsonの不正ではなく、Windows の `stdin` がデフォルトで cp932 を使うため、
UTF-8の日本語ファイルをパイプ経由で渡すと文字化けする。

**回避策**: パイプではなく `open(path, encoding='utf-8')` で直接読む。

---

## 修正内容

### 1. `scripts/_generate_mds.py`

`sanitize_title()` 関数を追加。タイトルをfrontmatterに書き出す前に以下を処理:
- 改行・CR・タブをスペースに置換
- `\"` （バックスラッシュ+クォート）を除去
- 残りの `"` を除去
- `\` 単体を除去
- 連続スペースを正規化

旧: `title = article["title"].replace('"', '\\"')`
新: `title = sanitize_title(article["title"])`

### 2. `scripts/build_index.py`

`parse_frontmatter()` に防御的処理を追加:
- `\"` を `"` にアンエスケープ
- `title` フィールドからバックスラッシュを除去

### 3. `scripts/fix_titles.py`（新規作成）

既存記事の一括修正ツール:
- `python scripts/fix_titles.py` — dry-run（変更内容の表示のみ）
- `python scripts/fix_titles.py --apply` — 実際にファイルを書き換え
- 121件を修正済み。再実行で0件（残存なし確認済み）

---

## 再発防止チェックリスト

- [ ] 新しい収集ソースを追加する際は、タイトルに `"` や改行が含まれるケースをテストする
- [ ] `crawl_*.py` の出力JSONのtitleフィールドに改行がないことを確認する
- [ ] Windowsでパイプ経由のJSON処理を避け、ファイル経由で読み書きする
- [ ] `build_index.py` 実行後に `json.loads()` でバリデーションする習慣をつける
