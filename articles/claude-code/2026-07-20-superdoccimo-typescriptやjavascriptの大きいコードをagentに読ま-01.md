---
id: "2026-07-20-superdoccimo-typescriptやjavascriptの大きいコードをagentに読ま-01"
title: "@superdoccimo: TypeScriptやJavaScriptの大きいコードをagentに読ませる時、つい「とりあえずファイル全体」を渡しが"
url: "https://x.com/superdoccimo/status/2079175216832365045"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "JavaScript", "TypeScript"]
date_published: "2026-07-20"
date_collected: "2026-07-21"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

TypeScriptやJavaScriptの大きいコードをagentに読ませる時、つい「とりあえずファイル全体」を渡しがちです。でも実際に欲しいのは、関数ひとつ、呼び出し元、参照箇所、型の解決結果だけ、という場面がかなり多いと思います。

SymbolPeek はそこを AST-backed な MCP server にするRust製の新しいOSSです。READMEを見る限り、TypeScript Compiler API と Language Service を使い、read_symbol、read_symbol_context、find_references、find_callers、get_type、search_symbols などをagentに渡せます。

面白いのは、grepの置き換えを名乗っていないところです。コメントや設定を見るならgrepでいい。関数の中の制御フローを読むなら普通に読むべき。だけど、import aliasやbarrel exportをまたいで「このsymbolはどこで定義され、誰が呼び、型は何か」を追う時は、文字列検索よりAST側に寄せたほうが事故が少ない。

CodexやClaude Codeへの接続手順もREADMEにあります。ただし今回はREADMEとGitHub APIレベルの確認で、僕はまだ実行や性能比較まではしていません。大規模monorepoでは短命workerがprogramを作り直すため遅延があり得る、という注意も含めて、agentに読む量を減らす小さな専門道具として見るのが良さそうです。

情報元: GitHub
