---
id: "2026-05-02-claude-code-が出した提案を却下する技術-個人開発saasをdddで作りながら学んだこと-01"
title: "Claude Code が出した提案を却下する技術 - 個人開発SaaSをDDDで作りながら学んだこと"
url: "https://zenn.dev/takepon7/articles/3dd56bd4c46304"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "OpenAI", "zenn"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

## はじめに: なぜこの記事を書くか

Claude Code を使った開発記事は世の中に無数にある。しかしそのほとんどは「Claude Code でこう作れた」という体験記事で、「Claude Code の提案をどう取捨選択したか」を書いた記事は意外と少ない。

この記事で書きたいのは後者だ。

個人開発で Claude Code を使う時、一番やりがちなのが「AI の提案を全部受け入れる」ことだ。動くものは確かにできる。しかしそれは判断停止であって、ポートフォリオとしては弱い。エンジニア転職市場で評価されるのは「設計判断ができる人」であって、「AI に書かせるのが上手い人」ではない。

この記事では、面談記録型のB2B SaaSを Claude Code + DDD で構築した過程で、Claude Code から受けた提案を**何を採用し、何を却下し、何を後回しにしたか**を、実際のログを元に書く。

技術解説の記事ではなく、判断ログの記事だ。

## プロジェクトとセットアップ

### 開発中のプロダクト

* 面談記録型のB2B SaaS (特定業界向けに最適化したAI議事録)
* Next.js 16 + Clerk + Supabase + Stripe + OpenAI Whisper + Claude Sonnet
* DDD (戦術的設計) を厳格適用
* 収益化を視野に入れた個人開発

業界特化テンプレートが事業の心臓部。Notta などの汎用議事録ツールとの差別化軸は、特定業界に最適化した出力フォーマットにある。

### 4 subagents 体制

Claude Code には「subagent」という機能がある。プロジェクトルートに `.claude/agents/*.md` を置くことで、特定の役割を持った subagent を作れる。本プロジェクトでは4つに分けた。

| Subagent | モデル | 役割 |
| --- | --- | --- |
| planner-researcher | Opus | 要件を調査・分解し `./plans/` に実装プランを書く |
| implementer | Sonnet | 既存プランに従ってコードを実装する |
| tester | Sonnet | テストを実行し、失敗ログを要約する |
| code-reviewer | Opus | コミット差分をレビューする(自分で修正はしない) |

**なぜ Opus と Sonnet を使い分けたか**: 設計判断と批評は推論力が要る (Opus 向き)。実装とテスト実行は一定の手順を正確に行う方が大事 (Sonnet で十分、コストも下がる)。

各 subagent の `.md` には「ワークフロー」「アウトプット形式」「守ること」を明記してある。例えば implementer:

```
## 実装の優先順位
1. 動くこと(プランの要件を満たす)
2. 説明可能なこと(なぜこの設計か答えられる) ← ポートフォリオ価値
3. テスト可能なこと(依存注入、副作用の局所化)
4. パフォーマンス(明確な要件があるときだけ)

## 守ること
- プランから外れる判断が必要になったら勝手に進めず、メインに確認
- DDDレイヤーを遵守:
  - Domain は Next.js / Supabase / Stripe / OpenAI を import しない
  - Repository インターフェースは Domain、実装は Infrastructure
  - 原始型を Domain 境界に露出させない
- 1コミット1責務
```

「説明可能なこと」を優先順位2に置いたのは、ポートフォリオ価値を意識したからだ。動くだけでは面接で語れない。「なぜこう書いた?」と聞かれて答えられるコードを書いてもらうために、明示的に書いてある。

### AGENTS.md と Ubiquitous Language

プロジェクト指針は `AGENTS.md` に集約した。Vercel / GitHub Copilot / Cursor / Claude Code が共同で標準化を進めている `AGENTS.md` パターンに乗った形だ。

その中に DDD のユビキタス言語表も全部書いた。例:

| 日本語 | 英語 | 定義 |
| --- | --- | --- |
| 面談 | Meeting | サービス提供者と顧客の1回の面談記録単位 |
| 顧客 | Customer | 継続的な関係を持つ事業者 |
| 構造化記録 | StructuredNote | 業界テンプレに従って構造化された面談記録 |

AGENTS.md には「`議事録` `ユーザー` `クライアント` という言葉を使うな」という禁止語ルールも書いた。汎用議事録ツールとの差別化を保つためだ。

ここまでが下地。ここから本題に入る。

## DDD 4層の実装フェーズ

最初の機能として、ヘルスチェックエンドポイント (`GET /api/health`) を DDD 4層で実装した。

```
src/contexts/system/
├── domain/                # フレームワーク非依存
│   ├── valueObjects/HealthStatus.ts
│   └── repositories/IHealthRepository.ts
├── application/
│   ├── usecases/CheckSystemHealthUseCase.ts
│   └── dtos/HealthResponseDto.ts
├── infrastructure/
│   └── repositories/InMemoryHealthRepository.ts
└── presentation/
    └── handlers/healthHandler.ts
```

これを6 Step に分けて progressively 実装した。Domain から始めて Infrastructure → Application → Presentation の順。各 Step ごとに `/clear` でコンテキストをクリーンにし、subagent に新しいコンテキストで取り組んでもらった。

23 unit tests を書いて全グリーン、`curl /api/health` で 200 が返ることを確認したところで、code-reviewer に最終レビューを依頼した。

**ここから判断ログの本番だ。**

## code-reviewer から返ってきた12個の指摘

code-reviewer は Critical 2件、Warning 5件、Suggestion 5件の計12個の指摘を返してきた。これを全部受け入れたら土台が崩れるし、全部却下したらレビューの意味がない。

判断した結果はこうだ。

| ID | 内容 | 判断 |
| --- | --- | --- |
| C-1 | Presentation 層が Infrastructure 層を直接 new している(依存方向違反) | ✅ 採用 |
| C-2 | APP\_VERSION ハードコード | ✅ 採用 (最小対応) |
| W-1 | DTO の status を string 型のまま放置(Union 型にすべき) | ✅ 採用 |
| W-2 | `equals()` という名前が誤解を招く、`hasSameStatus()` に分離 | ⏸ 後回し |
| W-3 | C-1 の副作用で Presentation 単体テストが結合テスト化 | ✅ C-1 修正で自動解決 |
| W-4 | vitest.config の include/exclude 未設定 | ⏸ 後回し |
| W-5 | InMemoryHealthRepository の依存境界が将来リスク | ❌ 却下 |
| S-1 | 複数リポジトリ統合時の Composite パターン提案 | ❌ 却下 |
| S-2 | テスト網羅性: 全ケースで checkedAt/version も検証すべき | ⏸ 後回し |
| S-3 | plans/ を git 管理対象にすべき(ADR として) | ✅ 採用 |
| S-4 | dependency-cruiser を導入してCI で違反検知すべき | ✅ 採用 |
| S-5 | Next.js 16 Route Handler の型定義確認 | ⏸ 後回し |

5/12 採用、3/12 後回し、4/12 却下。

## 採用した提案: 自分のミスを修正してくれた C-1

**C-1 が一番痛快な指摘だった。これは僕の設計ミスを正してくれた。**

僕は最初、Presentation 層の `healthHandler` 内で Infrastructure 層の `InMemoryHealthRepository` を直接 `new` していた。Composition Root を Presentation に置く形だ。これは「Composition Root はアプリのエントリーポイントに近い場所に置く」という原則の解釈ミスで、実際には:

* Presentation が Infrastructure を直接知る = レイヤー違反
* Presentation 単体テストが Infrastructure と結合する
* DI の意味が薄れる

code-reviewer の指摘通り、`route.ts` を真の Composition Root にし、`healthHandler` は `CheckSystemHealthUseCase` を**引数で受け取る**形に直した。

```
// 修正後の healthHandler
export async function healthHandler(
  useCase: CheckSystemHealthUseCase
): Promise<NextResponse> {
  const result = await useCase.execute();
  return NextResponse.json(result);
}

// 修正後の route.ts (Composition Root)
const repo = new InMemoryHealthRepository();
const useCase = new CheckSystemHealthUseCase(repo, pkg.version);
export const GET = () => healthHandler(useCase);
```

修正後、Presentation 単体テストではモック UseCase を渡せばよくなり、Infrastructure と切り離せた。W-3 (テストの結合化) も自動的に解決した。

**AI に間違いを指摘された時に意地を張らない**のが大事だ。code-reviewer の方が正しい時は素直に受け入れる。これも判断のうちだ。

## 採用した提案: 過剰対応しない C-2 (バージョン注入)

C-2 は「APP\_VERSION = "0.1.0" がコードにハードコードされていて、package.json と乖離する」という指摘だった。

code-reviewer は「専用の設定値レイヤーから取得する形に変更すべき」と書いていた。これは「ConfigService を作って依存注入で渡す」みたいなパターンを示唆している。

却下する選択肢もあったが、ハードコードのリスクは認めるので採用した。**ただし「設定値レイヤー」までは作らない**。

```
// CheckSystemHealthUseCase の constructor で受け取る
constructor(
  private readonly repository: IHealthRepository,
  private readonly version: string
) {}

// route.ts (Composition Root) で package.json から渡す
import pkg from '../../../package.json';
const useCase = new CheckSystemHealthUseCase(repo, pkg.version);
```

これで package.json と自動同期できる。「ConfigService を作る」は YAGNI なので作らない。**採用するけど過剰対応しない**、というのも判断のうちだ。

## 採用した提案: dependency-cruiser 導入 (S-4)

これは元々プランに書いてあった項目で、code-reviewer が改めて推した。CIで依存方向違反を自動検知できるようにする提案で、これは即採用。

8つのルールを定義した:

```
- Domain → Infrastructure 禁止
- Domain → Application 禁止
- Domain → Presentation 禁止
- Domain → app/ 禁止
- Domain → next, @supabase/*, stripe, openai, @anthropic-ai/* 禁止
- Application → Infrastructure 禁止
- Application → Presentation 禁止
- Application → app/ 禁止
```

`npm run lint:deps` で 0 violations。これを GitHub Actions に組み込んで、PR の度に自動チェックされるようにした。

**設計が時間とともに腐らない仕組みを最初に入れた**、という事実は技術記事でもエンジニア面接でも刺さる。これは Claude Code が提案して僕が即採用した、いい例だ。

## 却下した提案: S-1 Composite Repository

ここから却下ログに入る。

S-1 は「複数の Repository を統合する時のために `ICompositeHealthRepository` への発展を検討すべき」という提案だった。

僕はこれを却下した。理由は単純で、**現時点で Repository は1つしかない**。Composite パターンは複数の Repository を抽象化するためのもので、1つしかない状態で導入するのは過剰抽象化だ。

YAGNI (You Aren't Gonna Need It) の典型例で、「将来必要になるかもしれない」で作る抽象は、ほとんどの場合、必要にならない。仮に必要になっても、その時には「実際に何を抽象化すべきか」が明確になっているので、その時に作る方が良い設計になる。

採用すると:

* 不要なコードが増える
* 「これ何のためにあるの?」と後で自分でも分からなくなる
* ポートフォリオでも「過剰設計をする人」と見られる

これは却下一択。Claude Code の提案には、こういう「**正論っぽいが YAGNI 違反**」がたまに混じる。判断軸を持たないと毎回採用してしまう。

## 却下した提案: W-2 命名変更 (equals → hasSameStatus)

W-2 は「`HealthStatus.equals()` は checkedAt を除外した部分比較なので名前が誤解を招く、`hasSameStatus()` に分離すべき」という指摘。

これも却下した。理由:

1. **HealthStatus は VO (Value Object)** で、`equals()` は VO の標準的な等値性メソッドの名前
2. checkedAt を除外する判断自体は、**「ステータス」の本質を比較する設計** として妥当
3. `hasSameStatus()` という名前にすると「`equals()` は何を比較するのか」が逆に不明確になる
4. **チームコンテキストに依存する命名議論**は、1人開発の段階では結論が出ない

これは「正しい指摘」ではなく「議論すべき指摘」だ。1人開発で結論を出すべきではないし、出したとしても後で覆る。**判断を留保する**のも判断のうちだ。

## 却下した提案: W-5 InMemoryRepository の依存境界

W-5 は「現状は許容範囲だが、将来のリスクとして依存境界を意識しておくこと」という指摘だった。

これも却下した。**code-reviewer 自身が「許容範囲」と書いている時点で、却下できる**。「念のため改善しろ」はノイズだ。

提案を全部受け入れるとコードが膨れる一方になる。「気持ち分かるけどやらない」を選択できるかが、設計判断の能力だ。

## 後回しにした提案: W-4 vitest.config と S-5 Next.js 16 型確認

W-4 (vitest.config に include/exclude が無い) と S-5 (Next.js 16 Route Handler の型確認) は、却下ではなく**後回し**にした。

理由は「**今は必要ない、将来必要になったらやる**」だ。

* W-4: E2E テストが無いうちは include/exclude の不整合は起きない。E2E を追加するタイミングで設定する
* S-5: curl で 200 が返って動作確認済み。型エラーが出たらその時直す

却下と後回しは違う。**却下は「やらない」、後回しは「今やらない」**。後回しをちゃんと記録に残しておけば、将来必要になった時に思い出せる。

## 判断のために何をしたか: 運用ノウハウ

ここまでで「採用5、後回し3、却下4」というログを残せた。これができたのは、いくつかの運用ルールがあったからだ。

### 1. `/clear` を毎フェーズで打つ

Claude Code は会話の文脈を保持しているので、長いセッションになると古い情報に引きずられる。フェーズ(プラン → 実装 → テスト → レビュー)が変わるタイミングで `/clear` を打って、subagent に新しいコンテキストで取り組んでもらった。

### 2. subagent ごとにモデルを使い分け

Opus は推論力が高いがコストが高い。Sonnet はバランス型でコストも低い。これを役割に応じて使い分けた:

* 設計判断・批評 (planner-researcher, code-reviewer): **Opus**
* 実装・テスト実行 (implementer, tester): **Sonnet**

### 3. Step を区切る指示を毎回明示する

implementer に実装を依頼する時は、必ず「Step N だけ実装、Step N+1 はまだ着手しないで」と明示した。AI は放置すると全 Step を一気にやろうとする。区切らないとレビューやテストの粒度が崩れる。

### 4. plans/ をコミットして ADR として残す

各機能の実装プランは `./plans/YYYYMMDD-feature-name-plan.md` として残した。これは S-3 でも提案された通り、git 管理対象にして ADR (Architecture Decision Record) として機能させる。

「プランを書いた → 実装した → 結果こうだった」を記録に残しておくと、後から「なぜこの設計にしたか」を答えられる。

## 結果と数字

ここまでの作業で達成したもの:

* ✅ DDD 4層分離 + 23 unit tests + 4 integration tests = 全グリーン
* ✅ dependency-cruiser 0 violations
* ✅ GitHub Actions CI 緑
* ✅ 1人 + AI で2日で実装(Domain層から RLS 統合テストまで)

CI が緑になっているのは「`git clone` するだけで誰でも同じ環境を再構築できる」という証明でもある。これが採用面接で「環境構築のドキュメントは整備されてますか?」と聞かれた時の答えになる。

## まとめ: AI と判断する技術

AI コード生成が当たり前になった今、**「AI に書かせる人」と「AI と判断する人」の差**が大きくなっている。

「全部受け入れる」は楽だが、ポートフォリオでは弱い。コミット履歴を見れば、AI の言いなりだったかが透ける。

「全部却下する」も違う。AI の提案には正しい指摘もある。

大事なのは**1個ずつ判断して、判断ログを残すこと**だ。採用したものには「なぜ採用したか」、却下したものには「なぜ却下したか」を、後で自分でも答えられるようにしておく。

この記事で出した5採用・3後回し・4却下のログは、僕の判断軸がある程度反映されている。あなたの判断軸は違うはずだし、違っていい。**自分の判断軸で取捨選択できることが、AI 時代のエンジニアとしての価値**だと思う。

---

## おまけ: ハマったポイント

参考までに、このフェーズでハマった3つを残しておく。詳細は別途 Qiita に書く予定。

1. **Docker Desktop で容量不足 → I/O エラー**: 開発機の空き容量が 1.2GB まで減っていて、Supabase 起動時にメタデータが破損した。容量空けて Clean / Purge data で復旧。
2. **Supabase CLI 新形式キーと統合テストヘルパーの不整合**: 新形式 (`sb_publishable_*` / `sb_secret_*`) と旧形式 JWT (`eyJhbGc...`) で混乱したが、結果的にローカル開発では新形式キーで RLS テストが通った。
3. **別マシンに環境移行したら .claude/ が無かった**: 元の開発機で作った AGENTS.md と subagent 設定が git に未追跡だった。クローン後に再構築してコミット。

ケーススタディリポジトリ: [github.com/takepon7/claude-code-ddd-case-study](https://github.com/takepon7/claude-code-ddd-case-study)

実際の AGENTS.md、subagent 設定、plans/、コミット履歴がここで確認できる。
