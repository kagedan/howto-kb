---
id: "2026-04-27-umler-を-prisma-風-dsl-で書いてai-と協業しながら設計を進める-umlay-16-01"
title: "UML/ER を Prisma 風 DSL で書いて、AI と協業しながら設計を進める ── Umlay 1.6 の紹介"
url: "https://qiita.com/kigi316782/items/1eddb61dd7a5a7b64a9b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "LLM", "OpenAI", "Python", "TypeScript"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

---
title: UML を AI と協業する道具に作り直した話 ── Umlay という DSL の開発記録
tags: UML DSL TypeScript Claude 設計
---

## はじめに

「設計の最初に UML を描いて、すぐ嫌われて、その後は誰も触らない」── これに何度遭遇したか分かりません。

UML 自体は今も概念として強力なのに、ツール (Visio / astah / draw.io) は古く、コードと乖離し、AI に渡しても理解されない。一方 Prisma や Hibernate は型レベルでは綺麗だけど、**設計判断 (なぜ集約境界をここに引いたか / どの ADR で決めたか / 後で誰がいつ変えたか)** を残す場所がありません。

「AI と協業しながら UML を運用できる現代的な DSL」── これを目指して [Umlay](https://github.com/umlay/umlay) を作っています。本記事は **発端から spec 1.6 までで学んだこと**の開発記録です。「上手くいった話」より「**作って初めて分かった話**」を多めにしました。

> リポジトリ: <https://github.com/umlay/umlay>  / Web エディタ: <https://umlay.keydrop.net> / npm: [`@umlay/cli`](https://www.npmjs.com/package/@umlay/cli)

---

## 目次

1. [出発点 — UML が現代環境で死んだ理由](#出発点--uml-が現代環境で死んだ理由)
2. [最初の決断 — IR を単一正本にする](#最初の決断--ir-を単一正本にする)
3. [DSL 構文を何にするか — Prisma 風に寄せた](#dsl-構文を何にするか--prisma-風に寄せた)
4. [AI と分業する単位の発見 — 8 本の skill](#ai-と分業する単位の発見--8-本の-skill)
5. [想定外 — diff は git 風では足りない](#想定外--diff-は-git-風では足りない)
6. [AI が頻発する文法ミス — parser に Hint を埋め込む](#ai-が頻発する文法ミス--parser-に-hint-を埋め込む)
7. [spec が肥大した気付き — 1.7 で directive を統合する](#spec-が肥大した気付き--17-で-directive-を統合する)
8. [今と、これから](#今とこれから)

---

## 出発点 — UML が現代環境で死んだ理由

きっかけは別案件で、**Prisma スキーマと UML のクラス図を二重管理**していて気付きました。

- Prisma を変更しても、誰も UML を更新しない
- UML だけ正しい状態 (intent / invariant / 集約境界) を保有しているが、コードに繋がっていない
- AI に「この設計を実装して」と渡しても、UML は読めない (Visio の XML / 画像 PDF)

3 つの問題に分解できます:

1. **テキストでない** — git diff にならない、PR レビューにならない
2. **設計判断を載せる場所がない** — Prisma に `@@id` は書けても、「なぜこれが集約ルートなのか」は書けない
3. **AI が読めない** — 機械可読でない、または機械可読でも仕様が公開されていない

逆に言うと、この 3 つを満たすものを作れば良い。**Prisma 風のテキスト DSL** に **設計判断のスロット** を持たせて、**JSON Schema で IR を公開**すれば。

---

## 最初の決断 — IR を単一正本にする

これは早い段階で決めました: **AST ではなく、正規化された IR (Intermediate Representation) を単一正本にする**。

```
.umlay (DSL)
   ↓  parse (Chevrotain)
   ↓
正規化 IR (Zod schema → JSON Schema 公開)
   ├→ lint (73 ルール)
   ├→ renderer (11 view kind → SVG)
   ├→ codegen (Prisma / SQL / TS)
   └→ AI / LLM 入出力 (構造化 JSON)
```

**何故 IR か**: AST は parser の都合に密着しています。Lint や renderer や codegen は parser の都合を知るべきではありません。IR を間に挟むと、

- **DSL を変えても下流が壊れない** (parser から IR への projection だけ書き換える)
- **JSON で公開できる** (ir.schema.json として配布、他言語の parser でも作れる)
- **AI に渡しやすい** (構造化 JSON は LLM が読める)

実装的には Zod スキーマで IR を定義して、JSON Schema に自動エクスポートする 2 段構成。**正本は Zod 1 か所**で、ドキュメント / fixture / 型定義 / lint・renderer 入力すべてが Zod から派生します。

`scripts/regen-conformance-fixtures.ts` で 41 fixture × 3 level (parse / IR validate / render) = **123 テストが常時走る**ようにしてあります。spec をいじって fixture と差分が出たらすぐ気付く設計。

---

## DSL 構文を何にするか — Prisma 風に寄せた

最初は PlantUML 寄せ、Mermaid 寄せ、独自路線、いくつか試して **Prisma 風 (Prisma-like)** に着地しました。理由:

- Prisma は **多くの開発者が既に書ける**
- `model` / `enum` / `@id` / `@unique` / `@ref` などの語彙が**既知**
- 行頭が宣言キーワードで始まるので**眼で構造を追いやすい**

最終的にこんな構文に:

```umlay
@@mode(strict)
namespace shop

model Order @aggregate_root
  @intent("発注のアグリゲート。draft → confirmed → shipped の片道")
  @inv("total >= 0") {
  +id          UUID!         @id
  +customerId  UUID!         @ref(Customer.id, onDelete: RESTRICT)
  +status      OrderStatus!  @default(DRAFT)
  +total       decimal!

  fn confirm() -> void
    @pre("status == DRAFT")
    @post("status == CONFIRMED")
}

view shop-er @er_diagram { include: shop.* }
```

Prisma 風だが UML 由来の概念 (`@aggregate_root`, `fn` メソッド, `@pre`/`@post` 契約, `view` で図定義) を載せた形。

**意外な落とし穴**: AI (Claude) に `.umlay` を書かせると、訓練データに引っ張られて **`id: UUID!` (TypeScript / Prisma の `name: Type`) と書く頻度が高い**。Umlay は `id UUID!` (コロン無し) なので毎回 parse error。

これは後で parser 側で対処することになります (後述)。

---

## AI と分業する単位の発見 — 8 本の skill

Claude Code が **skill** という概念を持っています。ディレクトリに `SKILL.md` を置くと、Claude がその `description` を見て**意図に合致したものを自動で起動**してくれる仕組み。

最初は `umlay-helper` 1 本にまとめようとしましたが、すぐに破綻しました。**役割を直交させて 8 本に分割**した方が AI も人間も楽だったのです。

| skill | 役割 |
| --- | --- |
| `umlay` | 「何から始めれば?」相談窓口 (2 質問で振り分け) |
| `write-uml` | 自然言語要件 → 初版 `.umlay` |
| `reverse-engineer` | Prisma / SQL / TS → 構造のみ取り込み |
| `review-uml` | 4 層監査 (S spec / L lint / R risk / W+C compatibility) |
| `evolve-schema` | 既存 `.umlay` に後方互換な差分を当てる |
| `change-impact-diff` | 旧 + 新 IR から影響レポート |
| `plan-from-diff` | impact から phase / PR 分割 / rollback 付き計画 |
| `codegen-mapping` | IR → Prisma / SQL / TS の決定論変換 |

**この分割が効いた理由**:

- Claude が `description` を読んで **「この .umlay をレビューして」 → review-uml** を自動選択する
- 各 skill が**他の skill の責務に侵食しない**ので、暴走しにくい
- skill 同士のフロー (greenfield: write → review → evolve → codegen / brownfield: reverse → review → write → evolve → impact → plan → codegen) を README に書ける

副産物: skill カタログを書くと**自分自身の頭が整理される**。「どの skill が何の責務を持つか」を文章化する過程で、それまで曖昧だった責務境界が明確化しました。

---

## 想定外 — diff は git 風では足りない

最初は普通の git diff っぽく「赤と緑」を出すつもりでした。実装してみると**役に立たない**。

reviewer / 設計者は diff から:

- **何のための変更か** (ビジネス意図)
- **どこに波及するか** (touch points)
- **見落としがちな点** (migration / cascade / 意味論シフト)

を読み取りたい。git diff はその情報を**持っていません**。

そこで `change-impact-diff` skill では **3 文固定構造の AI ナラティブ + 構造化 Risk + Impact マップ** を返す形に方向転換しました。

```
Purpose: 顧客接触経路を明示フィールドに集約し、CRM チームがリーチ可能列を
         推測せずアウトバウンド施策を打てる状態にする。
Touch points: auth.Session と billing.Order.customerId は User.id を指すため
         FK 側は壊れないが、ER view 2 本 (auth-overview / senior-review)
         は再描画が要り、sequence checkout-happy-path が User.email を直接
         参照している (DSL 42 行目) ため書き換えが要る。
Do-not-miss: これは純粋な追加ではなく rename + 追加の複合。migration で
         email → contactEmail をバックフィルしてから旧列を drop しないと、
         オープン中のセッションが次回 read で落ちる。
```

ここから:

- **Risk 分類** (Breaking / Caution / Safe) を field-level ルールで自動
- **Impact マップ** (ref / view / participant) を IR 全走査で生成
- **Reviewer checklist** (Risk × Impact のクロス) を AI 不使用で自動生成
- **Hotspot overlay** (ER 図に追加=緑ハロー / 変更=橙枠) で**視覚的にも**変化を伝える

**学び**: AI を「文章生成ツール」として使う時、**自由度を絞った 3 文構造**にしたら格段に安定しました。長文を書かせると毎回トーンがブレるが、`Purpose / Touch / Miss` の 3 文に縛ると Anthropic / OpenAI / WebGPU のどのプロバイダでも安定する。

---

## AI が頻発する文法ミス — parser に Hint を埋め込む

AI が `.umlay` を書くと**毎回同じ間違い**をする ── という発見が spec 1.6.1 への分岐点でした。

頻度ランキング:

1. **`id: UUID!`** (Prisma / TypeScript の `name: Type`)
2. **`fn pay(): Receipt`** (TS の return type 指定)
3. **`model Foo:`** (Python / YAML のブロック開始)
4. **`field = string`** (DSL の代入)

すべて Umlay の正解は別。`id UUID!` (コロン無し) / `fn pay() -> Receipt` (矢印) / `model Foo { ... }` / `field string` (代入なし)。

これに対して 2 段階で対処しました:

### 1. parser 側 — エラーに「Hint:」を埋める

```sh
$ umlay check schema.umlay
ERROR  schema.umlay:4:6 [PARSE] Expecting token of type --> Identifier <-- but found --> ':' <--
  Hint: Umlay attributes are written WITHOUT a colon between name and type — write
        `id UUID! @id` or `email string?`, not `id: UUID!`. (`field: Type` is
        Prisma / TypeScript syntax.)
```

`parser.ts` で specific なパターン (`<ident>:<ident>` のような直前直後トークン) を検出して、Hint を append する。AI が次のターンで**自分のエラーから学習できる**ようになります。

### 2. skill 側 — 失敗ランキングを `write-uml` に明記

```markdown
| ❌ 間違い (他言語の癖) | ✅ Umlay 正解          |
|------------------------|------------------------|
| `id: UUID! @id`        | `id UUID! @id`         |
| `fn pay(): Receipt`    | `fn pay() -> Receipt`  |
| `model User:`          | `model User { ... }`   |
```

`write-uml` skill 本体に**「AI が頻発する文法ミス」表**を入れて、AI が skill を読み込む時点で先に学習する。

**学び**: AI に「正しい構文」を教える時、**間違いやすいパターンを ❌/✅ 対比で書く**方が、文法仕様を抽象的に書くより効きます。

---

## spec が肥大した気付き — 1.7 で directive を統合する

ここまでで block directive (`@@id`, `@@unique`, `@@compliance`, `@@locked`, `@@since`, `@@boundary`, `@@example`, ...) が **30 個前後** に膨らんでいました。

各 directive を spec 1.5 → 1.6 で順次足していった結果なんですが、**ある日 sd.keydrop.net の実プロジェクトで使ってみて気付きました**:

- 一つ一つは妥当でも、**全部覚えるのは重すぎる**
- AI prompt にも全部入れると prompt 予算を圧迫する
- VS Code completion で 30 entries が並ぶと選びづらい

意味グループで眺めると、整理できるはず:

| 1.6.x の現状 (5 系統) | 1.7 で統合 (umbrella 4 directive) |
| --- | --- |
| `@@since` / `@@deprecated` / `@@locked` | → `@@lifecycle` |
| `@@owner` / `@@status` / `@@adrRef` | → `@@review` |
| `@@compliance` / `@@confidence` / `@@provenance` | → `@@governance` |
| `@@inv` / `@@pre` / `@@post` / `@@example` | → `@@contract` |

**4 つの umbrella directive にまとめれば 30 → 12 程度に圧縮**できる、というのが [RFC 0050](https://github.com/umlay/umlay/blob/main/packages/spec/src/rfcs/0050-directive-consolidation-1.7.md) の計画。1.7 で実装、2.0 で legacy alias drop の 2 段。

そして同時に **「spec freeze 期間」** をプロセスとして導入しました。1.6.x で feature freeze、4 週間ドッグフードのみ、1.7 で機能整理 → 進む。**「機能を増やす」より「実利用で破綻したものを直す」フェーズの方が利得が大きい**という当たり前の気づきが、自分で開発していると見えなくなります。

> **release-policy.md 抜粋**
> 「機能を足すより、ゆっくり足してこまめに固める。最大 1 ヶ月に minor 1 回。RFC accept から release tag まで最低 2 週間」

---

## 今と、これから

spec 1.6.1 の現在地:

| 領域 | 状態 |
| --- | --- |
| 文法 | block directive ~30、view kind 11、構造化 `@@inv` |
| Lint | 73 ルール (RFC 0049 で +4) |
| 配布 | Web (`umlay.keydrop.net`) / VS Code 拡張 0.5.6 / `@umlay/cli@0.5.3` (npm) |
| 公開リポジトリ | <https://github.com/umlay/umlay> (Apache-2.0) |
| Skill | 8 本 (Claude Code 連携、`description` で auto-invoke) |
| RFC | 0001–0044, 0049, 0050 (1.7 計画 draft) |

近期予定:

- **1.7 (1〜2 ヶ月後)**: directive consolidation (RFC 0050)、legacy alias は 2.0 まで残す
- **1.8**: codegen 拡充 — 構造化 `@@inv` から runtime バリデータ自動生成、`@@example` から property-based test 自動生成
- **2.0**: legacy directive alias drop、安定版

「**設計ドキュメントを AI と一緒に書く・読む・進化させる**」を spec に焼き込もうとしています。

実利用で違和感が出たら [GitHub Discussions](https://github.com/umlay/umlay/discussions) または [ofuse.me](https://ofuse.me/umlay) からフィードバック頂けると非常に助かります。あるいはこの記事のコメント欄でも。

UML を「もう一度ちゃんと書く道具」にしたい人と、AI と一緒に設計したい人の、両方に届くと嬉しいです。

---

## 参考リンク

- リポジトリ: <https://github.com/umlay/umlay>
- Web エディタ (インストール不要): <https://umlay.keydrop.net>
- npm: [`@umlay/cli`](https://www.npmjs.com/package/@umlay/cli)
- Spec at a glance: [spec-overview.md](https://github.com/umlay/umlay/blob/main/packages/spec/src/spec-overview.md)
- Skill カタログ: [skills/README.md](https://github.com/umlay/umlay/blob/main/skills/README.md)
- RFC 0050 (1.7 計画): [`directive-consolidation-1.7.md`](https://github.com/umlay/umlay/blob/main/packages/spec/src/rfcs/0050-directive-consolidation-1.7.md)
- Release policy: [`spec-release-policy.md`](https://github.com/umlay/umlay/blob/main/docs/spec-release-policy.md)
