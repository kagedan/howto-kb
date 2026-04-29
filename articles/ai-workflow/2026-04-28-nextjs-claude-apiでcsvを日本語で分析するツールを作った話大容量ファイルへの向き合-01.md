---
id: "2026-04-28-nextjs-claude-apiでcsvを日本語で分析するツールを作った話大容量ファイルへの向き合-01"
title: "Next.js + Claude APIでCSVを日本語で分析するツールを作った話——大容量ファイルへの向き合い方"
url: "https://zenn.dev/enaga7561/articles/3bd55b1def1e48"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-04-28"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

## なぜ自分で作ったのか

Claude.aiにCSVをアップロードして日本語で質問するだけで分析できます。小さなファイルなら問題ありません。

問題は大容量ファイルです。製造業の基幹システムから1年分の生産実績を出力すると、10万行を超えることがよくあります。このサイズをそのままClaudeに渡そうとすると、コンテキストウィンドウの制限でエラーになります。

この問題を解決するために、ツールを作ることにしました。

## 2段階方式——Claudeに生データを渡さない

解決策のポイントは「Claudeには生データを渡さない」ことです。

```
【Claude.aiに直接渡す方法】
CSV全行（10万行） → Claude → 回答
                    ↑コンテキスト制限でエラー

【2段階方式】
CSV全行 → STEP1: Claudeに集計方法だけ聞く
        → STEP2: Node.jsで全行集計
        → 集計結果（最大100行）→ Claude → 回答
```

Claudeが得意なのは自然言語の理解と生成です。大量データの集計計算はNode.jsに任せる、という役割分担です。

## STEP1: 集計仕様を取得する

ユーザーの質問文とCSVのヘッダー行・先頭3行のサンプルだけをClaudeに送り、「この質問に答えるにはどう集計するか」をJSONで返してもらいます。

```
const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 512,
  system: `ユーザーの質問に答えるために必要な集計方法をJSONで返してください。

回答は必ず以下のJSON形式のみで返してください：
{
  "operation": "group_by" | "filter" | "top_n" | "aggregate" | "cross",
  "group_by_columns": ["列名"],
  "aggregate_column": "列名",
  "aggregate_function": "sum" | "avg" | "count" | "max" | "min",
  "sort_by": "asc" | "desc",
  "limit": 20
}`,
  messages: [{
    role: 'user',
    content: `CSVのヘッダー行: ${headers.join(', ')}
サンプルデータ（先頭3行）:
${sampleText}

質問: ${question}`,
  }],
});
```

STEP1でClaudeに送るのはヘッダー行と先頭3行だけです。10万行のデータは一切送りません。

## STEP2: Node.jsで全行処理して集計する

Claudeから返ってきた集計仕様をもとに、Node.js側で実際のCSVを全行処理します。集計結果は最大100行に絞ってからClaudeに渡します。

```
export function aggregateCsv(
  rows: string[][],
  headers: string[],
  spec: AggregationSpec
): AggregatedResult {
  switch (spec.operation) {
    case 'group_by':  return groupBy(rows, headers, spec);
    case 'filter':    return filterRows(rows, headers, spec);
    case 'top_n':     return topN(rows, headers, spec);
    case 'aggregate': return aggregateAll(rows, headers, spec);
    case 'cross':     return crossTab(rows, headers, spec);
    default:          return groupBy(rows, headers, spec);
  }
}
```

group\_byの実装例です。列名の検索はファジーマッチで行います。製造業のデータは列名に全角スペースが入っていたり、大文字小文字が揺れていたりするため、完全一致だと意図した列が見つからないケースがあります。

```
function findColIndex(headers: string[], colName: string): number {
  const exact = headers.indexOf(colName);
  if (exact >= 0) return exact;
  const normalized = colName.trim().toLowerCase();
  return headers.findIndex(h => h.trim().toLowerCase() === normalized);
}

function groupBy(rows: string[][], headers: string[], spec: AggregationSpec): AggregatedResult {
  const groupCols = (spec.group_by_columns ?? [])
    .map(col => findColIndex(headers, col))
    .filter(i => i >= 0);
  const aggColIdx = spec.aggregate_column
    ? findColIndex(headers, spec.aggregate_column)
    : -1;

  const groups = new Map<string, string[]>();
  for (const row of rows) {
    const key = groupCols.map(i => row[i] ?? '').join('\0');
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(aggColIdx >= 0 ? row[aggColIdx] ?? '' : '1');
  }

  let resultRows: string[][] = [];
  groups.forEach((values, key) => {
    resultRows.push([...key.split('\0'), applyAggregation(values, spec.aggregate_function)]);
  });

  if (spec.sort_by) {
    const last = resultRows[0].length - 1;
    resultRows.sort((a, b) => {
      const aNum = parseNumeric(a[last]);
      const bNum = parseNumeric(b[last]);
      if (!isNaN(aNum) && !isNaN(bNum)) {
        return spec.sort_by === 'desc' ? bNum - aNum : aNum - bNum;
      }
      return spec.sort_by === 'desc'
        ? b[last].localeCompare(a[last], 'ja')
        : a[last].localeCompare(b[last], 'ja');
    });
  }

  return {
    headers: [...(spec.group_by_columns ?? []), aggLabel],
    rows: resultRows.slice(0, spec.limit ?? MAX_TABLE_ROWS),
    totalRows: rows.length,
  };
}
```

## ClaudeのレスポンスをJSONとして扱う際の注意

「JSONのみ返してください」と指示しても、コードブロックで囲んで返してくることがあります。

```
{ "operation": "group_by", ... }
```

正規表現でJSONオブジェクト部分だけを抽出するようにしています。

```
const jsonMatch = text.match(/\{[\s\S]*\}/);
if (!jsonMatch) {
  throw new Error('集計方法の解析に失敗しました。もう一度お試しください。');
}
const spec = JSON.parse(jsonMatch[0]) as AggregationSpec;
```

## Shift-JIS対応

製造業の基幹システムから出力されるCSVはShift-JISエンコーディングが多いです。[前回の記事](https://zenn.dev/enaga7561/articles/7862d56167e18e)ではNode.jsでiconv-liteを使う方法を書きましたが、このツールではサーバー側でNode.js組み込みの`TextDecoder`を使って検出・変換しています。

`TextDecoder`にUTF-8を指定して`fatal: true`にすると、不正なバイト列があった時点で例外が発生します。これを使って「UTF-8としてデコードできなければShift-JIS」と判定し、そのままShift-JISとしてデコードします。

```
function decodeBuffer(buffer: Buffer): { text: string; encoding: 'UTF-8' | 'Shift-JIS' } {
  try {
    const text = new TextDecoder('utf-8', { fatal: true }).decode(buffer);
    return { text: text.replace(/^\uFEFF/, ''), encoding: 'UTF-8' };
  } catch {
    return { text: new TextDecoder('shift-jis').decode(buffer), encoding: 'Shift-JIS' };
  }
}
```

BOM付きUTF-8の場合は`\uFEFF`を除去しています。Node.js 18以降はiconv-liteなしでShift-JISを扱えるため、追加パッケージ不要です。

## Excelファイルへの対応

製造業の現場では「Excelで管理している台帳をそのまま分析したい」というニーズが強いため、`.xlsx/.xls`にも対応しました。

`xlsx`（SheetJS）ライブラリ1つでExcelの読み込みと出力の両方を賄えます。サーバー側ではバイナリBufferをそのまま渡すため、`type: 'buffer'`を指定します。

```
import * as XLSX from 'xlsx';

const workbook = XLSX.read(buffer, {
  type: 'buffer',      // サーバー側はBufferで受け取る
  cellFormula: false,  // 数式は計算済みの値を使用
  cellHTML: false,
  cellDates: true,
});

const worksheet = workbook.Sheets[sheetName];

// 結合セルを解除して結合元の値を各セルにコピー
if (worksheet['!merges']) {
  for (const merge of worksheet['!merges']) {
    const firstCell = XLSX.utils.encode_cell({ r: merge.s.r, c: merge.s.c });
    const firstCellValue = worksheet[firstCell];
    if (!firstCellValue) continue;
    for (let r = merge.s.r; r <= merge.e.r; r++) {
      for (let c = merge.s.c; c <= merge.e.c; c++) {
        if (r === merge.s.r && c === merge.s.c) continue;
        worksheet[XLSX.utils.encode_cell({ r, c })] = { ...firstCellValue };
      }
    }
  }
}

const rows = XLSX.utils.sheet_to_json(worksheet, {
  header: 1,
  raw: false,   // 数式は計算済みの値を文字列で取得
  defval: '',
});
```

製造業のExcelはヘッダー行が結合セルになっていることが多いため、結合解除の処理は必須でした。

## まとめ

大容量CSVをClaudeで分析するポイントは「Claudeに集計方法を聞いて、実際の集計はNode.jsでやる」という役割分担です。この方式であれば、元データが何万行あってもClaudeに渡すのは常に最大100行の集計結果だけになります。

今回作ったツール「[キクデータ（KikuData）](https://kikudata.enaga-labs.com/lp)」は、中小製造業向けにフリープランで公開しています。製造現場でCSV集計に手間をかけている方がいれば、ぜひ触ってみてください。
