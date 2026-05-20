---
id: "2026-05-19-windows環境でのai自動化を支えるexit-code-49とcp932エラーを回避する環境構築-01"
title: "Windows環境でのAI自動化を支える：exit code 49とcp932エラーを回避する環境構築の極意"
url: "https://qiita.com/oguri-gmoconnect/items/30675dba289d7cb0bd8e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "Python", "qiita"]
date_published: "2026-05-19"
date_collected: "2026-05-20"
summary_by: "auto-rss"
query: ""
---

# はじめに

Claude CodeなどのAIエージェントに「毎日の作業ログを自動集計してクラウドストレージに保存する」処理を任せていました。スケジュールタスクで毎朝実行し、AIが自律でログ解析・YAML生成・ファイル保存まで完走する、というシナリオです。

初回テストは成功。「これで毎日自動化できる」と思っていたら、**翌朝確認すると止まっていました**。

エラーは2種類。コードには何も問題がなく、原因はWindows環境特有の挙動でした。macやLinuxでは絶対に踏まない地雷です。この記事では根本原因を掘り下げ、再発しない解決策を示します。

## TL;DR

```bash
# NG：Windowsでは2つの理由で止まる
python3 script.py

# OK：この1行に置き換える
PYTHONUTF8=1 py -3 script.py
```

---

# 問題①：exit code 49 — 動いているようで動いていない

## 症状

AIエージェントが `python3 script.py` を実行すると、こんな出力で終了します。

```
Exit code 49
Python
```

スクリプトは一切実行されていません。AIがリトライしても同じ結果。コードをどれだけ見ても原因はわかりません。

## 根本原因：python3 はStoreへのスタブ

Bash（Git Bash）で `which python3` を実行してみます。

```bash
$ which python3
/c/Users/yourname/AppData/Local/Microsoft/WindowsApps/python3
```

この `python3.exe` は**Pythonではありません**。Windowsの「アプリ実行エイリアス」機能によって配置されたMicrosoft Storeへのスタブです。

Windowsはインストールされていないコマンドを実行したとき、Storeへ誘導するスタブを `WindowsApps` に置きます。`python3.exe` はその代表例です。インタラクティブなターミナルで叩くとStoreの画面が開き、非インタラクティブな実行（AIエージェントからの呼び出しなど）では **exit code 49** を返して終了します。

```
AIエージェント
    │
    └─ Bash → python3 script.py
                    │
         WindowsApps\python3.exe  ← Storeスタブ
                    │
              exit code 49 ← 非対話実行を拒否して終了
              （スクリプトは一行も実行されない）
```

Pythonをインストール済みであっても、PATHの優先順位でこのスタブが先に解決されると同じ問題が起きます。

## 解決策：py コマンド（Windows Python Launcher）を使う

`WindowsApps` には `py.exe` も存在します。

```bash
$ which py
/c/Users/yourname/AppData/Local/Microsoft/WindowsApps/py
```

同じパスですが、`py.exe` はStoreスタブではありません。Pythonの公式インストーラが登録する**Python Launcher for Windows**です。レジストリに登録されたPythonインタープリタを探し出して起動します。`-3` でPython 3系を指定できます。

```bash
# NG：Storeスタブで止まる
python3 script.py

# OK：Python Launcherが実際のインタープリタを起動
py -3 script.py
```

:::note info
**公式ドキュメント**
Python Launcher for Windows の詳細仕様（バージョン選択・`py.ini`・シバン行対応）は公式ドキュメントに詳しく記載されています。
https://docs.python.org/3/using/windows.html#python-launcher-for-windows
:::

---

# 問題②：cp932 UnicodeEncodeError — 文字コードの罠

## 症状

`py -3` に切り替えてPythonが正しく動き始めたと思ったら、今度はこのエラーが出ます。

```
Traceback (most recent call last):
  File "script.py", line 42, in main
    print(summarize(sessions, date))
UnicodeEncodeError: 'cp932' codec can't encode character '❌' in position 5972: illegal multibyte sequence
```

`❌` は ❌（CROSS MARK）絵文字です。同様のエラーが `—`（EM DASH、`—`）などでも起きます。

## 根本原因：日本語WindowsのデフォルトエンコーディングはUTF-8ではない

Pythonの標準出力エンコーディングはOS・ロケールに依存します。

```bash
# 何も設定しない状態で確認
$ py -3 -c "import sys; print(sys.stdout.encoding)"
cp932
```

日本語WindowsではデフォルトでCP932（Shift_JIS系）になります。CP932はUnicodeの全文字をカバーしていないため、収録外の文字を `print()` しようとした瞬間に `UnicodeEncodeError` がスローされます。

AIが生成するテキストには絵文字・記号・特殊文字が頻繁に登場します。それらを含む文字列をスクリプトが出力しようとするたびに止まります。

| 文字 | コードポイント | cp932での扱い |
|---|---|---|
| ❌ CROSS MARK | U+274C | エラー（未収録） |
| — EM DASH | U+2014 | エラー（未収録） |
| ✅ CHECK MARK BUTTON | U+2705 | エラー（未収録） |
| 🔍 MAGNIFYING GLASS | U+1F50D | エラー（未収録） |

## 解決策：PYTHONUTF8=1 で UTF-8 モードを有効にする

Python 3.7以降、`PYTHONUTF8=1` 環境変数を設定すると**UTF-8モード**で起動します。

```bash
$ PYTHONUTF8=1 py -3 -c "import sys; print(sys.stdout.encoding)"
utf-8
```

UTF-8モードでは標準入出力だけでなく、`open()` のデフォルトエンコーディングもUTF-8になります。

```bash
# Before（PYTHONUTF8なし）
$ py -3 script.py
UnicodeEncodeError: 'cp932' codec can't encode character '❌' ...

# After（PYTHONUTF8=1）
$ PYTHONUTF8=1 py -3 script.py
（正常終了）
```

### PYTHONIOENCODING との違い

類似の環境変数に `PYTHONIOENCODING=utf-8` がありますが、効果範囲が異なります。

| 環境変数 | 標準入出力 | ファイルopen() | 推奨場面 |
|---|---|---|---|
| `PYTHONUTF8=1` | ✅ | ✅ | 全面的にUTF-8化したいとき |
| `PYTHONIOENCODING=utf-8` | ✅ | ❌ | 出力だけ対処すれば十分なとき |

スクリプトがファイル読み書きも行う場合は `PYTHONUTF8=1` を使う方が安全です。

コマンドライン引数として `-X utf8` を渡す方法もあります（Python 3.7+）。

```bash
py -3 -X utf8 script.py
```

こちらは環境変数を汚染しないため、一時的に試すときや特定スクリプトだけに適用したい場面で便利です。

:::note info
**公式ドキュメント**
`PYTHONUTF8` の詳細仕様と影響するコンポーネントの一覧は以下を参照してください。
https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUTF8
:::

---

# 解決策のまとめ

```bash
# この1行で両方の問題を解決する
PYTHONUTF8=1 py -3 script.py
```

| 問題 | 原因 | 対策 |
|---|---|---|
| exit code 49 | `python3` がStoreスタブを指している | `py -3` に変える |
| cp932エラー | stdout encodingがデフォルトでcp932 | `PYTHONUTF8=1` を付ける |

---

# AIエージェントへの周知：SKILL.md に書く

コマンドを直した後に考えるのは、「AIが次回も正しいコマンドを使ってくれるか」です。

AIはセッションをまたいで記憶を持ちません。エラーに遭遇して学習しても、次のセッションではまたゼロから始まります。実際、今回のケースでもAIは一度エラーを踏んでから自力で修正しています。

```
[AIエージェントの実行ログ]
→ python3 を呼び出す
→ exit code 49 で失敗
→ 「文字エンコードエラーが出ています。環境変数で対処します。」
→ PYTHONUTF8=1 py -3 に切り替えて再実行
→ 成功
```

この試行錯誤は毎セッションで発生します。AIが読み込むスキル定義ファイル（`SKILL.md` や `CLAUDE.md`）に**最初から正しいコマンドを明示しておく**ことで、無駄な往復をなくせます。

```markdown
## スクリプト実行（Windows環境）

`python3` コマンドは使用禁止。Microsoft Storeスタブが干渉してexit code 49になる。
必ず以下の形式で実行すること：

    PYTHONUTF8=1 py -3 ~/.claude/skills/my-skill/scripts/run.py --date YYYY-MM-DD
    # ↑ パスとオプションは各自の環境に合わせて変更
```

---

# PYTHONUTF8 の永続化

毎回コマンド頭に書くのが面倒な場合、永続化できます。

| 方法 | 効果範囲 | 管理コスト |
|---|---|---|
| コマンド頭に `PYTHONUTF8=1` | そのコマンドのみ | 都度必要 |
| `~/.bashrc` に `export PYTHONUTF8=1` | 全Bashセッション | 低 |
| Windowsシステム環境変数 | 全プロセス | 中 |
| スクリプト内で `sys.stdout.reconfigure(encoding='utf-8')` | そのスクリプトのみ | スクリプト修正が必要 |

Git Bash環境では `~/.bashrc` がデフォルトで存在しない場合があります。その場合は新規作成します。

```bash
echo 'export PYTHONUTF8=1' >> ~/.bashrc
source ~/.bashrc
```

ただし、AIエージェントが必ずしも `~/.bashrc` を読んで実行するとは限りません。スクリプトを直接 `exec` で呼ぶケースなどでは環境変数が引き継がれないことがあります。前述のスキル定義にコマンドを書く方式と組み合わせるのが最も確実です。

---

# おわりに

2つのエラーの正体を振り返ります。

- **exit code 49**：`python3` がPythonではなくMicrosoft Storeへのスタブを指している。`py -3`（Python Launcher）で回避。
- **cp932エラー**：日本語Windows特有のデフォルトエンコーディング。`PYTHONUTF8=1` でUTF-8モードを強制。

どちらも「Pythonのコードに問題がある」わけではないため、コードを読んでいても原因にたどり着けません。Windows環境の特性として知っているかどうかで、詰まる時間が大きく変わります。

AIに自律的に動いてもらうほど、こういった**環境の安定性**が重要になります。AIはエラーを見て自己修正できますが、それを毎回やらせるのは無駄です。一度整備してしまえば毎日止まらずに動き続ける。そのための30分は十分に価値があります。
