---
id: "2026-04-18-prologでllmの論理推論を強化するmcpサーバーを作ってみた-01"
title: "PrologでLLMの論理推論を強化するMCPサーバーを作ってみた"
url: "https://qiita.com/rikarazome/items/d78fcb4a810035493c23"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "LLM", "qiita"]
date_published: "2026-04-18"
date_collected: "2026-04-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

LLMに論理パズルを出すと、簡単な三段論法は解けるのに、制約が絡む問題になると間違える。

たとえば覆面算（SEND + MORE = MONEY）。各文字に0-9の異なる数字を当てはめるだけの問題だが、Claude Sonnetでも間違える。組み合わせが多すぎて、推測では正解にたどり着けない。

一方Prologなら制約を書くだけで一瞬で解ける。LLMにPrologを書かせて、実行はPrologに任せればいい。そう考えて、SWI-PrologをMCPサーバーとして使えるようにする [prolog-reasoner](https://github.com/rikarazome/prolog-reasoner) を作った。

### この記事でわかること

* LLMがどういう論理問題で間違えるか
* prolog-reasonerの仕組みと使い方
* Prologに任せるとどれくらい精度が変わるか（ベンチマーク結果）

## LLMが間違える問題

LLM単体だとどこで躓くか、具体例を見る。

### 覆面算 SEND + MORE = MONEY

各文字に0-9の異なる数字を割り当てて `SEND + MORE = MONEY` を成立させる。解空間は10P8 = 約180万通り。LLMには探索しきれない。

Prologだとこう書ける：

```
:- use_module(library(clpfd)).
solve([S,E,N,D,M,O,R,Y]) :-
    Vars = [S,E,N,D,M,O,R,Y],
    Vars ins 0..9,
    all_different(Vars),
    S #> 0, M #> 0,
    1000*S+100*E+10*N+D + 1000*M+100*O+10*R+E
        #= 10000*M+1000*O+100*N+10*E+Y,
    label(Vars).
```

CLP(FD)の制約ソルバーが解空間を刈り込んで `MONEY = 10652` を返す。

### 石取りゲーム（Nim）

> 16個の石から交互に1〜3個取る。最後の石を取った方が勝ち。先手必勝？後手必勝？

再帰的にゲーム木を探索しないと正確に答えられない。LLMは「4の倍数だから後手必勝」と答えることもあるが、数を変えると間違える。

```
wins_from(N) :-
    N > 0,
    between(1, 3, M), M =< N,
    N1 is N - M,
    \+ wins_from(N1).
```

Prologなら石の数をいくつに変えても正確に判定できる。

### タスク割り当て

> Alice(coding/design可), Bob(design/testing可), Carol(testing/deployment可), Dave(deployment/coding可)を1対1で割り当て。何通り？

```
can_do(alice, coding). can_do(alice, design).
can_do(bob, design). can_do(bob, testing).
can_do(carol, testing). can_do(carol, deployment).
can_do(dave, deployment). can_do(dave, coding).

assign(A, B, C, D) :-
    can_do(alice, A), can_do(bob, B),
    can_do(carol, C), can_do(dave, D),
    A \= B, A \= C, A \= D, B \= C, B \= D, C \= D.

count(N) :- findall(_, assign(_,_,_,_), L), length(L, N).
```

答えは2通り。Prologが全組み合わせを列挙するので数え間違えがない。LLMはこの手の数え上げでよくミスする。

## prolog-reasonerの仕組み

上のようなProlog、人間が毎回書くのは面倒だが、LLMなら自然言語から生成できる。prolog-reasonerはこの分業をMCPサーバーとして実現する。

```
ユーザー（自然言語）→ LLM（Prologコードを生成）→ SWI-Prolog（実行）→ 結果
```

Claude DesktopやClaude Codeに登録すると、ユーザーが論理的な質問をしたときにClaudeが自動的にPrologコードを生成・実行し、結果をもとに回答する。ユーザーはPrologを知らなくていい。

MCPサーバーが提供するツールは以下の通り：

* **`execute_prolog`** — 任意のSWI-Prologコードを実行。CLP(FD)も対応
* **`save_rule_base` / `get_rule_base` / `list_rule_bases` / `delete_rule_base`** — よく使うルールを名前付きで保存・再利用する機能

### ルールベース

毎回同じルールを送り直すのは無駄なので、安定したルールを保存しておける。

たとえば経費精算の承認ルール：

```
% description: 経費精算の承認ルール
% tags: expense, approval

requires_manager_approval(Expense) :-
    amount(Expense, Amount),
    Amount > 10000.

requires_director_approval(Expense) :-
    amount(Expense, Amount),
    Amount > 100000.

approved(Expense) :-
    amount(Expense, Amount),
    Amount =< 10000.
approved(Expense) :-
    requires_manager_approval(Expense),
    has_approval(Expense, manager).
approved(Expense) :-
    requires_director_approval(Expense),
    has_approval(Expense, director).
```

`save_rule_base("expense_rules", ...)` で一度保存すれば、以降は個別の申請データだけ渡せばいい：

```
{
  "rule_bases": ["expense_rules"],
  "prolog_code": "amount(req_001, 50000). has_approval(req_001, manager).",
  "query": "approved(req_001)"
}
```

LLMはケース固有のデータだけ書けばよくなる。「ルールは固定、ケースが変わる」パターン向き。

## ベンチマーク

30問の論理問題（演繹・推移律・制約充足・矛盾検出・多段推論）でLLM単体とLLM+prolog-reasonerを比較した。

### 全体

| パイプライン | 正答率 | 平均レイテンシ |
| --- | --- | --- |
| LLM単体 (Claude Sonnet) | 22/30 (73.3%) | 1.7s |
| **LLM + prolog-reasoner** | **27/30 (90.0%)** | 3.8s |

### カテゴリ別

| カテゴリ | 問題例 | LLM単体 | LLM+Prolog |
| --- | --- | --- | --- |
| 演繹 | 三段論法 | 6/6 | 6/6 |
| 推移律 | 祖先関係、到達可能性 | 6/6 | 5/6 |
| **制約充足** | 覆面算、Nクイーン、ナップサック | **3/7** | **6/7** |
| 矛盾検出 | 前提の矛盾判定 | 4/4 | 3/4 |
| **多段推論** | 騎士と悪党、巡回セールスマン | **3/7** | **7/7** |

差が出るカテゴリとそうでないカテゴリがはっきり分かれる。

* **演繹・推移律** → LLM単体で十分。Prologを挟んでもレイテンシが増えるだけ
* **制約充足・多段推論** → 組み合わせ探索と再帰的推論が必要な領域で、Prologの強みがそのまま出る

全部の質問にPrologを使う必要はなく、LLMが苦手な問題に絞って使うのが効率的。

### 失敗した3問について

LLM+Prologで不正解だった3問は、すべてLLMが生成したPrologコードの不備が原因だった。たとえばナップサック問題では、CLP(FD)変数に `label/1` を呼び忘れて変数が未束縛のまま返ってくる、というミスをしていた。

これは論理推論の限界ではなくコード生成の問題なので、LLMのコード生成能力が上がれば自然に解消する。精度の伸びしろはまだある。

また、LLM単体だと「もっともらしい間違い」がブラックボックスから返ってくるだけで原因がわからないが、Prologならエラーメッセージとして、どの理論が原因だったかが見えるのも利点。

### レイテンシについて

平均レイテンシが1.7sから3.8sに増える。Prolog変換＋実行のオーバーヘッド分。精度が重要な場面なら許容範囲だが、用途によっては気になる遅延。

## 他のProlog MCPとの違い

Prolog系のMCPサーバーはいくつかあるが、prolog-reasonerは「論理の電卓」として設計している。

|  | prolog-reasoner | 他のProlog MCP |
| --- | --- | --- |
| 位置づけ | 呼び出し単位の推論ツール | プロジェクト全体の知識ベース |
| 状態管理 | ステートレス（+ルールベース） | 永続セッション |
| 再現性 | 同じ入力→同じ出力 | 蓄積状態に依存 |

必要なときだけ呼んで、不要なときはスキップする。このステートレス性のおかげで、LLM単体とのA/B比較ベンチマークが成り立つ。

永続的な知識ベースが必要なら [adamrybinski/prolog-mcp](https://github.com/adamrybinski/prolog-mcp) や [umuro/prolog-mcp](https://github.com/umuro/prolog-mcp) の方が合う。

## セットアップ

Claude CodeやCursorなら、[GitHubのURL](https://github.com/rikarazome/prolog-reasoner)を渡して「MCPサーバーとして追加して」と頼めばセットアップできる。

### 必要なもの

### Claude Desktop / Claude Codeの設定

`uvx` を使う場合、事前の `pip install` は不要。

```
{
  "mcpServers": {
    "prolog-reasoner": {
      "command": "uvx",
      "args": ["prolog-reasoner"]
    }
  }
}
```

MCPサーバーとして使う場合、LLM APIキーは不要。Claudeが自分でPrologを書いて実行する。

### Docker経由（SWI-Prologのインストール不要）

```
git clone https://github.com/rikarazome/prolog-reasoner.git
cd prolog-reasoner
docker build -f docker/Dockerfile -t prolog-reasoner .
```

```
{
  "mcpServers": {
    "prolog-reasoner": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "prolog-reasoner"]
    }
  }
}
```

## まとめ

LLMが苦手な組み合わせ探索や再帰的推論を、Prologに任せることで精度が改善した。全問にPrologを使う必要はなく、LLMが苦手な問題に絞って使うのがポイント。

フィードバックや使えそうな場面のアイデアがあれば [GitHub Issues](https://github.com/rikarazome/prolog-reasoner/issues) へ。
