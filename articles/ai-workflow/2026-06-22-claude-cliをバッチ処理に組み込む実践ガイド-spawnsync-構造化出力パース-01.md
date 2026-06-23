---
id: "2026-06-22-claude-cliをバッチ処理に組み込む実践ガイド-spawnsync-構造化出力パース-01"
title: "Claude CLIをバッチ処理に組み込む実践ガイド — spawnSync + 構造化出力パース"
url: "https://qiita.com/denden56/items/d96c65b1007a92a047f6"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "JavaScript", "qiita"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

## 導入：なぜ必要か

Node.jsのバッチ処理でClaude CLIを呼び出し、構造化出力をパースすれば、複数のテキストを効率よく処理・分類・集計できる。スクリーンショット分析や定期的なデータ判定といった定型業務の自動化に向く。

## Claude CLIの基本呼び出し

Claude CLIは標準出力にテキストを返す。`child_process.spawnSync`で捕捉し、正規表現で抽出する。

```javascript
const { spawnSync } = require('child_process');

function callClaude(prompt, model = 'claude-3-5-sonnet-20241022') {
  const result = spawnSync('claude', ['-m', model], {
    input: prompt,
    encoding: 'utf-8',
    timeout: 30000,
    maxBuffer: 10 * 1024 * 1024
  });

  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`Claude CLI failed: ${result.stderr}`);
  
  return result.stdout;
}
```

`maxBuffer`を増やしておくと、長い出力が切られない。`timeout`はms単位。

## 構造化出力のパース設計

プロンプトに出力形式を指定してから、正規表現で抽出する。

```javascript
const prompt = `以下の文を分類し、カテゴリーと信頼度を "<category>カテゴリー名</category> <confidence>数値</confidence>" の形式で出力せよ。

文: ${text}`;

const output = callClaude(prompt);

const categoryMatch = output.match(/<category>(.+?)<\/category>/);
const confidenceMatch = output.match(/<confidence>(\d+)<\/confidence>/);

const category = categoryMatch ? categoryMatch[1] : null;
const confidence = confidenceMatch ? parseInt(confidenceMatch[1]) : null;

if (!category || confidence === null) {
  console.warn('パース失敗:', output);
}
```

XMLタグで囲むと、正規表現がシンプルになる。非マッチ時の対応も必須。

## 複数行・複数項目の処理

JSONを出力させると配列処理が楽になる。

```javascript
function parseMultipleItems(prompt) {
  const output = callClaude(prompt + '\n\n出力はJSON配列の形式: [{"id": ..., "value": ...}]');
  
  try {
    const jsonMatch = output.match(/\[\s*{[\s\S]*}\s*\]/);
    if (!jsonMatch) throw new Error('JSON not found in output');
    return JSON.parse(jsonMatch[0]);
  } catch (e) {
    console.error('JSON parse error:', e.message, output);
    return [];
  }
}
```

JSONが大きい場合、正規表現で抽出した後にパースする。

## バッチ処理での連続呼び出し

連続呼び出しときは、タイムアウトと失敗時の再試行を組み込む。

```javascript
async function processBatch(items, fn, maxRetries = 2) {
  const results = [];
  
  for (const item of items) {
    let attempts = 0;
    let output = null;
    
    while (attempts < maxRetries && !output) {
      try {
        output = fn(item);
        results.push({ item, output, success: true });
      } catch (e) {
        attempts++;
        if (attempts >= maxRetries) {
          results.push({ item, error: e.message, success: false });
          console.error(`Failed for ${JSON.stringify(item)}: ${e.message}`);
        }
      }
    }
  }
  
  return results;
}

const items = ['text1', 'text2', 'text3'];
const results = processBatch(items, text => callClaude(`分類: ${text}`));
```

同期的に処理すればレート制限の心配が少ない。

## Windowsタスクスケジューラーでの定期実行

バッチファイルでNode.jsスクリプトを呼び、タスクスケジューラーで定期実行する。

```batch
@echo off
cd /d "C:\path\to\project"
node batch-processor.js >> logs\batch_%date:~0,4%%date:~5,2%%date:~8,2%.log 2>&1
```

タスクスケジューラーで「プログラムの実行」を選び、このバッチファイルを指定。実行アカウントが適切な権限を持つ必要がある。

環境変数（APIキーなど）は、タスクスケジューラーのタスクプロパティで「操作」→「編集」→「操作」タブから「変数の編集」で設定できる。

## エラーハンドリング

```javascript
function safeCall(prompt, fallback = null) {
  try {
    return callClaude(prompt);
  } catch (e) {
    if (e.code === 'ETIMEDOUT') {
      console.error('Timeout: Claude CLI did not respond');
    } else if (e.code === 'ENOENT') {
      console.error('Claude CLI not found. Install: pip install -U anthropic');
    } else {
      console.error(`Claude error: ${e.message}`);
    }
    return fallback;
  }
}
```

タイムアウトとコマンドなしの区別は、エラーコードで判定する。

## 実運用のポイント

- プロンプトに「出力形式は〜」と明記する。CLIが解釈を迷わない。
- `maxBuffer`と`timeout`は余裕を持たせる。
- バッチ処理中のログは日時付きで保存する。
- 定期実行時は標準出力をファイルにリダイレクトする。
- APIキーは環境変数から読む。コードに埋め込まない。

---

参考: https://note.com/large_yarrow1156/n/nbbeaa3e6e1c8
