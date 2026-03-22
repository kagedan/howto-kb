"""
fix_titles.py - 既存 Markdown 記事の frontmatter タイトル問題を一括修正する。

修正対象:
  1. タイトル内の \" (バックスラッシュ+クォート) を除去
  2. 複数行にまたがるタイトルを1行に正規化

使い方:
    python scripts/fix_titles.py          # dry-run (変更内容の表示のみ)
    python scripts/fix_titles.py --apply  # 実際にファイルを書き換える
"""

import io
import os
import re
import sys
from pathlib import Path

# Windows cp932 対策: stdout を UTF-8 に切り替え
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"

FRONTMATTER_RE = re.compile(r"^(---\s*\n)(.*?)(\n---\s*\n)", re.DOTALL)


def sanitize_title_value(raw_value: str) -> str:
    """YAML frontmatter の title 値をサニタイズする。

    raw_value: 'title: ' の後ろの部分（外側のクォート含む）
    """
    inner = raw_value.strip()
    # 外側のダブルクォートを除去
    if inner.startswith('"'):
        inner = inner[1:]
    if inner.endswith('"'):
        inner = inner[:-1]

    # バックスラッシュ+クォートのペアを除去
    inner = inner.replace('\\"', "")
    # 残りのダブルクォートを除去
    inner = inner.replace('"', "")
    # バックスラッシュ単体を除去
    inner = inner.replace("\\", "")
    # 改行・タブをスペースに
    inner = inner.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").replace("\t", " ")
    # 連続スペースを正規化
    inner = re.sub(r"\s+", " ", inner).strip()

    return inner


def fix_frontmatter(content: str) -> tuple[str, bool, str]:
    """Markdown ファイルの frontmatter を修正する。

    Returns:
        (修正後の全文, 変更があったか, 変更内容の説明)
    """
    m = FRONTMATTER_RE.match(content)
    if not m:
        return content, False, ""

    fm_text = m.group(2)
    body = content[m.end():]

    lines = fm_text.splitlines()
    new_lines = []
    in_title_continuation = False
    title_changed = False
    old_title = ""
    new_title = ""

    for line in lines:
        stripped = line.strip()

        if in_title_continuation:
            # 複数行タイトルの続き行 → スキップ（タイトルは既に修正済み）
            # 閉じクォートを含む行で終了
            if stripped.endswith('"'):
                in_title_continuation = False
            continue

        if stripped.startswith("title:"):
            _, _, val = stripped.partition(":")
            val = val.strip()
            old_title = val

            # 問題1: バックスラッシュを含む
            has_backslash = "\\" in val

            # 問題2: ダブルクォートで始まるが同じ行で閉じていない
            is_multiline = val.startswith('"') and not val.endswith('"')

            if has_backslash or is_multiline:
                sanitized = sanitize_title_value(val)
                new_title = sanitized
                new_lines.append(f'title: "{sanitized}"')
                title_changed = True

                if is_multiline:
                    in_title_continuation = True
                continue

        new_lines.append(line)

    if not title_changed:
        return content, False, ""

    new_fm = "\n".join(new_lines)
    new_content = f"---\n{new_fm}\n---\n{body}"
    desc = f"  old: {old_title[:100]}\n  new: \"{new_title[:100]}\""
    return new_content, True, desc


def main():
    apply = "--apply" in sys.argv

    fixed_count = 0
    error_count = 0

    for md_path in sorted(ARTICLES_DIR.rglob("*.md")):
        try:
            content = md_path.read_text(encoding="utf-8")
        except Exception:
            continue

        new_content, changed, desc = fix_frontmatter(content)
        if not changed:
            continue

        rel = md_path.relative_to(REPO_ROOT)
        print(f"{'FIX' if apply else 'WOULD FIX'}: {rel}")
        print(desc)
        print()

        if apply:
            try:
                md_path.write_text(new_content, encoding="utf-8")
                fixed_count += 1
            except Exception as e:
                print(f"  ERROR: {e}")
                error_count += 1
        else:
            fixed_count += 1

    mode = "fixed" if apply else "would fix"
    print(f"\nTotal {mode}: {fixed_count} files")
    if error_count:
        print(f"Errors: {error_count}")
    if not apply and fixed_count > 0:
        print("\nRun with --apply to actually modify files.")


if __name__ == "__main__":
    main()
