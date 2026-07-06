---
id: "2026-07-06-claudeにpythonでexcelを読み込ませファイルを出力する機能を実装してもらった-01"
title: "ClaudeにPythonでExcelを読み込ませファイルを出力する機能を実装してもらった"
url: "https://qiita.com/soldierboy/items/542dc571f560c3784e2d"
source: "qiita"
category: "ai-workflow"
tags: ["Python", "qiita"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

# ClaudeのPythonコードを生成してもらった

Excelを読み込みファイルを出力する．

```py
#!/usr/bin/env python3
# Excelを読み込みTOMLファイル群を生成する
#
# Excelレイアウト:
#   B1        : クラス名
(r_<B1>_xxx のプレフィックスに使用)
#   2行目F列- : パラメータ名(動的に増加、TB_で始まる名前はプレフィックスなし)
#   4行目F列- : 初期値(データ行のセルが空の場合に使用)
#   6行目-    : A=comment("#"で行コメント) B=pattern_name C=rand D=frame_num E=frame_name F-=設定値

import sys
import os
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

HDR_ROW   = 2  # レジスタ名の行
DEF_ROW   = 4  # 初期値の行
START_ROW = 6  # データ開始行
REG_COL0  = 6  # F列


def norm( v ):
  # セル値の正規化(整数値のfloatはintへ、文字列はstrip)
  if( isinstance(v, float) and v.is_integer() ):
    return int(v)
  if( isinstance(v, str) ):
    return v.strip()
  return v


def to_int( v ):
  # 整数として解釈できればintを、できなければNoneを返す
  if( isinstance(v, bool) ):
    return None
  if( isinstance(v, int) ):
    return v
  if( isinstance(v, float) and v.is_integer() ):
    return int(v)
  if( isinstance(v, str) ):
    s = v.strip()
    if( s=="" ):
      return None
    try:
      return int(s, 10)
    except ValueError:
      return None
  return None


def fmt_val( v ):
  if( isinstance(v, int) ):
    return "%d" % v
  return str(v)


def lhs_name( module, name ):
  # TB_で始まる名前はそのまま、それ以外は r_<モジュール名>_<名前>
  if( name.startswith("TB_") ):
    return name
  return "r_%s_%s" % (module, name)


def main():
  if( len(sys.argv)<2 ):
    sys.exit("usage: %s <input.xlsx> [output_dir]" % sys.argv[0])
  in_name = sys.argv[1]
  out_dir = "."
  if( len(sys.argv)>=3 ):
    out_dir = sys.argv[2]

  try:
    wb = load_workbook(in_name, data_only=True)
  except Exception as e:
    sys.exit("cannot open: %s (%s)" % (in_name, e))
  ws = wb.active

  errors   = []
  warnings = []

  # ---- B1(モジュール名)チェック ----------------------------------------------
  module = norm(ws.cell(row=1, column=2).value)
  if( module is None or module=="" ):
    errors.append("B1(モジュール名)が空です。空は禁止です")
    module = ""

  # ---- 2行目F列以降のレジスタ名収集と重複チェック -----------------------------
  regs = []  # (列番号, 名前)
  seen = {}  # 名前 -> [列レター]
  for c in range(REG_COL0, ws.max_column+1):
    v = ws.cell(row=HDR_ROW, column=c).value
    if( v is None or str(v).strip()=="" ):
      continue
    name = str(v).strip()
    regs.append((c, name))
    seen.setdefault(name, []).append(get_column_letter(c))
  for name in seen:
    if( len(seen[name])>=2 ):
      errors.append("2行目のレジスタ名 \"%s\" が重複しています(%s列)"
                    % (name, "列と".join(seen[name])))

  # ---- 4行目の初期値収集 ------------------------------------------------------
  defaults = {}
  for c, name in regs:
    defaults[c] = norm(ws.cell(row=DEF_ROW, column=c).value)

  # ---- データ行(6行目以降)の読み込み ------------------------------------------
  patterns = {}  # pattern_name -> [record] (出現順を保持)
  for r in range(START_ROW, ws.max_row+1):
    a  = norm(ws.cell(row=r, column=1).value)
    b  = norm(ws.cell(row=r, column=2).value)
    cv = ws.cell(row=r, column=3).value
    dv = ws.cell(row=r, column=4).value
    e  = norm(ws.cell(row=r, column=5).value)

    # A列が"#"始まりの行はコメント: 出力にもチェックにも含めない
    if( a is not None and str(a).startswith("#") ):
      continue

    # B列が空の行: 全列空ならスキップ、データがあれば警告してスキップ
    if( b is None or b=="" ):
      has_data = (cv is not None) or (dv is not None) or (e is not None and e!="")
      for c, name in regs:
        if( ws.cell(row=r, column=c).value is not None ):
          has_data = True
      if( has_data ):
        warnings.append("%d行目: B列(pattern_name)が空のため行をスキップします" % r)
      continue
む
    # C列(rand)の数値チェック
    rand = to_int(cv)
    if( rand is None ):
      errors.append("C%d(rand)が数字ではありません: %r" % (r, cv))

    # D列(frame_num)の数値チェック(FRAME_タグ生成に必須のため追加チェック)
    fnum = to_int(dv)
    if( fnum is None ):
      errors.append("D%d(frame_num)が数字ではありません: %r" % (r, dv))

    if( e is None or e=="" ):
      if( rand is not None and rand!=0 ):
        # randが0以外の行はframe_name必須
        errors.append("E%d(frame_name)が空です。randが0以外(rand=%d)の行はframe_name必須です"
                      % (r, rand))
      else:
        warnings.append("E%d(frame_name)が空のためframe_name行を省略します" % r)
      e = None


    # 設定値: セルが空なら4行目の初期値を使用
    vals = []
    for c, name in regs:
      v = norm(ws.cell(row=r, column=c).value)
      if( v is None or v=="" ):
        v = defaults[c]
      if( v is None or v=="" ):
        warnings.append("%s%d: 設定値も初期値も空のため \"%s\" を省略します"
                        % (get_column_letter(c), r, name))
        continue
      vals.append((name, v))

    patterns.setdefault(str(b), []).append(
      {"row": r, "rand": rand, "fnum": fnum, "fname": e, "vals": vals})

  # ---- パターン内のframe_num重複チェック(TOMLタグ重複防止の追加チェック) --------
  for pname in patterns:
    used = {}
    for rec in patterns[pname]:
      if( rec["fnum"] is None ):
        continue
      used.setdefault(rec["fnum"], []).append(rec["row"])
    for fn in used:
      if( len(used[fn])>=2 ):
        errors.append("pattern \"%s\" 内でframe_num=%d が重複しています(%s行目)"
                      % (pname, fn, ", ".join(str(x) for x in used[fn])))

  # ---- チェック結果 -----------------------------------------------------------
  for w in warnings:
    print("WARNING: %s" % w, file=sys.stderr)
  if( len(errors)>0 ):
    for e in errors:
      print("ERROR: %s" % e, file=sys.stderr)
    sys.exit(1)
  if( len(patterns)==0 ):
    sys.exit("no output target rows")

  # ---- TOML出力 ---------------------------------------------------------------
  for pname in patterns:
    group = sorted(patterns[pname], key=lambda rec: rec["fnum"])
    rands = sorted(set(rec["rand"] for rec in group))
    if( len(rands)>=2 ):
      print("WARNING: pattern \"%s\" 内でrandが不一致(%s)。先頭行の値を使用します"
            % (pname, rands), file=sys.stderr)
    fname = os.path.join(out_dir, "%s.toml" % pname)
    with open(fname, "w", encoding="utf-8", newline="\n") as f:
      f.write("[%s]\n" % pname)
      f.write("RAND=%d\n" % group[0]["rand"])
      f.write("frame=%d\n" % len(group))
      for rec in group:
        f.write("[FRAME_%d]\n" % rec["fnum"])
        if( rec["fname"] is not None ):
          f.write("frame_name=%s\n" % rec["fname"])
        for name, v in rec["vals"]:
          f.write("%s = %s\n" % (lhs_name(module, name), fmt_val(v)))
    print("%s : %d frame(s)" % (fname, len(group)))


if( __name__=="__main__" ):
  main()
```

実行方法

```sh
pip install openpyxl
python3 xlsxo.py サンプル.xlsx [出力ディレクトリ]
```
