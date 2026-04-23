---
id: "2026-04-16-連載第3回マイクロサービスの分散トランザクション入門claude-codeとscalardbで分散ト-01"
title: "【連載】（第3回）マイクロサービスの分散トランザクション入門：Claude CodeとScalarDBで分散トランザクションを実装する"
url: "https://zenn.dev/scalar_sol_blog/articles/51caf0cc106150"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

> **連載：マイクロサービスの分散トランザクション入門**

## はじめに

[第1回](/scalar_sol_blog/articles/d4a86cd3a202fa)でSaga/TCCの概念と落とし穴を、[第2回](/scalar_sol_blog/articles/7e1c3d624e774a)でScalarDBのコード量削減効果を見てきました。

ScalarDBを使えばコード量は74%削減できます。しかし、ScalarDBのコードがシンプルとはいえ、2PCのプロトコル順序や例外処理の階層構造など、**正しく実装するために守るべきルール**は存在します。

本記事では、AIコーディングエージェント**Claude Code**にScalarDBの実装ルールを教え込み、正確なコードを生成させる方法を紹介します。あわせて、**なぜSagaやTCCのコードをAIに生成させるとうまくいかないのか**を、第1回・第2回の内容を踏まえて明らかにします。

### 対象読者

* Claude Codeでマイクロサービスを開発したい方
* AIコーディングの限界と使いどころを知りたい方
* ScalarDBの実装パターンを手早く身につけたい方

---

## AIにSaga/TCCを書かせてみると何が起きるか

結論として、**正常系はある程度正確に生成できるものの、異常系の網羅性に大きな問題が出ます**。第1回・第2回の内容を踏まえ、その理由を整理します。

### 1. 状態空間が爆発する

Sagaで3ステップの処理があると、各ステップの成功/失敗＋各補償処理の成功/失敗で、考えるべきパスが数十通りになります。

```
注文作成 → 成功/失敗
  └→ 決済実行 → 成功/失敗
       └→ 在庫確保 → 成功/失敗
            └→ 補償(在庫) → 成功/失敗
                 └→ 補償(決済) → 成功/失敗
                      └→ 補償(注文) → 成功/失敗
```

AIは正常系を正確に生成できます。しかし「在庫確保が失敗→決済の補償が失敗→そのリトライも失敗」といったパスは、多くの場合生成から漏れます。

### 2. 暗黙知が多すぎる

第1回で書いた「空ロールバック」「サスペンション」「べき等性」——これらはSagaパターンの定義には載っていない**現場の暗黙知**です。AIの学習データにも断片的にしか入っていないので、一貫した実装は期待できません。

### 3. 生成するコードの規模が大きすぎる

第2回で示した通り、Sagaパターンの実装は20ファイル・1,058行に達します。RabbitMQの設定、イベントクラス、オーケストレーター、各ハンドラを一貫性を持って生成するのは、現状のAIには困難です。キュー名がファイル間で不一致になる、Saga状態マシンの遷移が不完全になる、といった問題が発生します。

### ScalarDBがAIと相性が良い理由

ScalarDBの場合、AIが守るべきルールは**明確かつ有限**です。

| 観点 | Saga/TCC | ScalarDB |
| --- | --- | --- |
| 考える状態 | ステップ x 補償 x 補償の失敗 | begin → CRUD → commit/abort |
| 異常系 | パターンごとに違う暗黙知 | 例外階層に基づく統一ルール |
| AIへの指示 | 「べき等な補償を実装して」（曖昧） | 「2PCルールに従って」（明確） |
| 検証 | 全パスの網羅テストが必要 | プロトコル準拠をチェックすればいい |

ScalarDBの実装ルールは**ファイルとして明文化できる**ため、AIに正確な知識を与えることが可能です。この点が決定的な違いです。

---

## Nexus Architect：ScalarDBのルールを知っているClaude Codeプラグイン

[Nexus Architect](https://github.com/wfukatsu/nexus-architect) は、ScalarDBのベストプラクティスを「ルールファイル」として体系化したClaude Codeプラグインです。Claude Codeが `.java` ファイルを書くときに自動でルールを参照して、正しいパターンでコードを生成してくれます。

### プラグインの構成

| プラグイン | スキル数 | 用途 |
| --- | --- | --- |
| **architect** | 40 | レガシーリファクタリング、新規設計、レビュー、レポート |
| **scalardb** | 11 | スキーマ設計、設定生成、コード生成、コードレビュー |

### インストール

```
claude plugin marketplace add wfukatsu/nexus-architect
claude plugin install architect@nexus-architect --scope user
claude plugin install scalardb@nexus-architect --scope user
```

### ルールファイルがAIの知識の源泉

`rules/` ディレクトリに格納された12のルールファイルが、Claude Codeの知識基盤となっています。これらはClaude Codeが `.java` ファイルを操作する際に自動的に参照されます。

| ルールファイル | 内容 |
| --- | --- |
| `scalardb-2pc-patterns.md` | 2PCの順序、Coordinator/Participant、rollbackの原則 |
| `scalardb-exception-handling.md` | 例外のcatch順序、リトライ可否、UnknownTransactionStatusの扱い |
| `scalardb-crud-patterns.md` | Get/Scan/Put/Delete の使い方 |
| `scalardb-jdbc-patterns.md` | JDBC/SQLインターフェースのパターン |
| `scalardb-schema-design.md` | パーティションキー、クラスタリングキー設計 |
| `scalardb-config-validation.md` | 設定ファイルの矛盾チェック |
| `scalardb-java-best-practices.md` | Javaコーディング規約 |
| `spring-boot-integration.md` | Spring Boot統合パターン |

以降では、特に重要な2つのルール——**2PCパターン**と**例外処理**——を詳しく解説します。

---

## ルール解説（1）：ScalarDB 2PCパターン

[`scalardb-2pc-patterns.md`](https://github.com/wfukatsu/nexus-architect/blob/main/rules/scalardb-2pc-patterns.md) に書かれているルールです。

### プロトコルの順序（厳守）

2PCプロトコルは以下の順序に従わなければなりません。

```
Coordinator: begin() → CRUD → prepare() → validate() → commit()
Participant: join(txId) → CRUD → (待機) → prepare() → validate() → commit()
```

Claude Codeがこのルールを参照することで、プロトコルの順序を間違えたコードを生成することがなくなります。

### マイクロサービスでの実装パターン

マイクロサービス構成では、各サービスがCoordinatorまたはParticipantとして振る舞います。

```
// Coordinator（注文サービス）
TwoPhaseCommitTransaction tx = manager.begin();
String txId = tx.getId();

// Participant（顧客サービス）— gRPCでtxIdを受け取って参加
TwoPhaseCommitTransaction tx = manager.join(txId);
```

1. Coordinatorが `begin()` して `txId` を取得
2. gRPCで `txId` をParticipantに送る
3. 各Participantが `join(txId)` してCRUD実行
4. Coordinatorが全員に `prepare()` → `validate()` → `commit()` を指示
5. どこかで失敗したら**全員 `rollback()`**

### 「全員prepare、全員rollback」

**1つでもprepareが失敗したら、全Participantをrollback**するのが鉄則です。

```
try {
    tx1.prepare();
    tx2.prepare();
} catch (PreparationException e) {
    tx1.rollback();
    tx2.rollback();  // 片方だけrollbackとかダメ
    throw e;
}
```

一方、commitは**ベストエフォート**。どれか1つのcommitが成功すれば、トランザクションは成立したとみなされます。残りは失敗してもLazy Recoveryが後で回復してくれます。

```
tx1.commit();
tx2.commit(); // 成功すべきだが、失敗してもデータは最終的に回復される
```

第1回で議論した「補償トランザクションの失敗」問題と対照的です。ScalarDBではそもそも補償処理が不要であり、commitの部分的な失敗もConsensus CommitのLazy Recoveryが自動的に回復します。

### validate()はいつ必要？

`validate()` は以下の**両方**に該当する場合だけ必要です。

* `scalar.db.consensus_commit.isolation_level=SERIALIZABLE`
* `scalar.db.consensus_commit.serializable_strategy=EXTRA_READ`

この条件を把握していないと、不要な `validate()` を追加したり、必要な場合に省略したりするミスが発生します。ルールファイルに記載されているため、Claude Codeは設定に応じて正しく判断できます。

---

## ルール解説（2）：ScalarDB 例外処理

[`scalardb-exception-handling.md`](https://github.com/wfukatsu/nexus-architect/blob/main/rules/scalardb-exception-handling.md) に定義されているルールです。例外処理はScalarDBコードの中で**最もバグが混入しやすい領域**であり、AIコード生成でも頻繁に間違いが発生します。

### 例外のcatch順序（最重要ルール）

ScalarDBの例外は階層構造を持っており、**子クラスを親クラスより先にcatchしなければ到達不能**になります。

```
// ✅ 正しい
catch (CrudConflictException e) { /* リトライ可能 */ }
catch (CrudException e) { /* リトライ不可かも */ }

// ❌ 間違い — CrudConflictExceptionには到達しない
catch (CrudException e) { ... }
catch (CrudConflictException e) { /* ここには到達しない */ }
```

IDEの警告を見落とすと、そのまま本番コードに混入するリスクがあります。対象となるペアは以下の通りです。

| 先にcatch（子） | 後にcatch（親） |
| --- | --- |
| `CrudConflictException` | `CrudException` |
| `CommitConflictException` | `CommitException` |
| `PreparationConflictException` | `PreparationException` |
| `ValidationConflictException` | `ValidationException` |

### Conflict例外はリトライすればいい

`*ConflictException` 系の例外は一時的な競合によるものであり、トランザクション全体を `begin()` からリトライすれば解決します。

```
int maxRetries = 3;
for (int i = 0; i < maxRetries; i++) {
    DistributedTransaction tx = manager.start();
    try {
        // CRUD操作
        tx.commit();
        return; // 成功
    } catch (CommitConflictException e) {
        tx.rollback();
        // begin()からリトライ
    } catch (CommitException e) {
        tx.rollback();
        throw e; // これはリトライしても無駄
    }
}
```

### UnknownTransactionStatusException — 最も注意が必要な例外

commitが成功したか失敗したか**不明**な状態を示す例外です。

!

**やってはいけないこと**

* rollbackしてはいけない（成功している可能性がある）
* 盲目的にリトライしてはいけない（データ重複の恐れ）

**やるべきこと**

* トランザクションIDをログに記録する
* べき等性パターンで安全にリトライするか、手動で状態を確認する

```
} catch (UnknownTransactionStatusException e) {
    // rollbackしない。commitが成功している可能性がある
    logger.error("Unknown transaction status. txId={}",
        e.getTransactionId().orElse("unknown"), e);
}
```

第1回で「ScalarDBでは補償処理の失敗問題が発生しない」と述べましたが、`UnknownTransactionStatusException` はScalarDBにおける唯一の「状態が不確定になるケース」です。ただし、Saga/TCCのように複数サービスの補償処理を連鎖的に管理する必要はなく、**この単一の例外をハンドリングするだけ**で対処できます。

### 読み取り専用でもcommit()を忘れない

見落としやすい点ですが重要です。read-onlyでも `commit()` を呼ばないと、トランザクションが開いたままリソースを浪費します。

```
DistributedTransaction tx = manager.start();
try {
    Result result = tx.get(get);  // 読み取りのみ
    tx.commit();                   // 必須
    return result;
} catch (TransactionException e) {
    tx.rollback();
    throw e;
}
```

---

## 実践：Claude Codeでのワークフロー

Nexus Architectのスキルを使って、ScalarDBマイクロサービスを実装するワークフローを紹介します。

### ステップ1：スキーマ設計

対話的にテーブルスキーマを設計します。パーティションキーやクラスタリングキーの設計ルールが `scalardb-schema-design.md` に基づいて適用されます。

### ステップ2：設定ファイル生成

Consensus Commitの分離レベル、ストレージバックエンド、2PC設定などを対話的に選択し、正しい `scalardb.properties` を生成します。`scalardb-config-validation.md` のルールにより、矛盾する設定（例：2PCとGroup Commitの併用）を防止します。

### ステップ3：プロジェクト生成

ScalarDBの6つのインターフェース組み合わせ（Core/Cluster x CRUD/JDBC x 1PC/2PC）に応じたスタータープロジェクトを丸ごと生成。

### ステップ4：アプリケーション実装

要件を伝えるとアプリケーション全体を構築。2PCルールと例外処理ルールが自動適用されるので、プロトコル順序の間違いやcatch順序のミスが起きません。

### ステップ5：コードレビュー

16カテゴリでコードを検証。例外のcatch順序、2PCプロトコルの遵守、commit漏れなど、この記事で解説したルールへの準拠をチェックします。

---

## Saga/TCC vs ScalarDB：AIコード生成の比較

| 観点 | Saga | TCC | ScalarDB + Nexus Architect |
| --- | --- | --- | --- |
| **ルールの明確さ** | 低（暗黙知が多い） | 低（エッジケースが多い） | 高（ルールファイルで明文化） |
| **生成コードの正確性** | 低（異常系が漏れる） | 低（空ロールバック等が漏れる） | 高（ルール準拠を自動検証） |
| **コードの規模** | 大（20ファイル超） | 大（3フェーズ x サービス数） | 小（4ファイル程度） |
| **AIへの知識注入** | 困難（パターンが多様） | 困難（FW依存） | 容易（ルールファイル12個） |
| **レビューの自動化** | 困難 | 困難 | 可能（16カテゴリ） |

実際にSaga/TCCをAIに書かせると、こんな問題が起きます。

* **補償処理の漏れ** — 正常系は書けるけど、特定ステップの失敗時の補償が抜ける
* **べき等性を考えてない** — 補償が2回呼ばれたときの二重実行
* **キュー名の不一致** — RabbitMQの設定とコードで名前がズレる
* **状態遷移の矛盾** — Sagaステートマシンが不完全

ScalarDBだとこういう問題が**構造的に存在しない**ので、AIの生成するコードの範囲が限定され、ルールファイルで正確に制御できます。

---

## 連載のまとめ

本連載では3回にわたってマイクロサービスの分散トランザクションを掘り下げてきました。

| 回 | テーマ | 主な結論 |
| --- | --- | --- |
| [第1回](./20260408-scalardb-distributed-tx-01.md) | Saga/TCCの概念 | 補償/Cancel処理自体の失敗が実運用上の最大の課題 |
| [第2回](./20260408-scalardb-distributed-tx-02.md) | ScalarDBによるコード量比較 | ファイル数80%減、行数74%減。ACID保証を自動化 |
| 第3回（本記事） | Claude Code + ScalarDBで実装 | ルールファイルによりAIが正確なコードを生成可能 |

**ScalarDBがコードをシンプルにし、Nexus Architectのルールファイルがそれを明文化してAIに正確な知識を与える。** この組み合わせにより、分散トランザクションの実装は「パターンの暗黙知を熟知したエキスパートにしかできない仕事」から「AIと人間の協働で効率的に進められる仕事」へと変わります。

Saga/TCCの概念を理解することは重要です。分散システムの設計判断において、「なぜScalarDBを使うのか」の根拠になるためです。しかし、その実装——特に異常系の網羅的な対処——をすべて手作業で行うのは、人間にとってもAIにとっても現実的に困難です。

ScalarDBで構造的に問題を排除し、さらにAIコーディングエージェントで実装を自動化する。この2段階のアプローチが、マイクロサービスにおける分散トランザクション実装の現実解だと考えています。

---

## 参考
