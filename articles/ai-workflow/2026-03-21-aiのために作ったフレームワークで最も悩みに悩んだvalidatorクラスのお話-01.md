---
id: "2026-03-21-aiのために作ったフレームワークで最も悩みに悩んだvalidatorクラスのお話-01"
title: "AIのために作ったフレームワークで、最も悩みに悩んだValidatorクラスのお話"
url: "https://qiita.com/fallout/items/eff6923a9f303615c51c"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

[AIでAIによるAIのためのフレームワークを作り、AIで爆速開発するというお話](https://qiita.com/fallout/items/3d1d96f4e40d3766aaad) にも書きましたが、最近、**AI様のためのフレームワーク**（Claude先生が `Lattice` という[名前をつけてくれた](https://qiita.com/fallout/items/d4867c023df3537c8fd8)ので以下 `Lattice`）を作る事にハマっていました。

もう既に何度か実践投入も済ませており、**AIが間違える事なく爆速コーディングするための専用道路**はほぼ完成した…と満足しています。

今回は、そんな `Lattice` の設計において最も苦労した `Validator` クラスの話をしたいと思います。

---

## 違う 違う そうじゃ そうじゃなーい

* ぼく：先生！ いつもありがとうございます！！
* ぼく：（どれどれ… いやほんと綺麗なコード書くよな…）
* ぼく：…。……！ 違う 違う！ そうじゃ そうじゃなーい！ ◯◯が美しくなーい！！
* ぼく：Claude先生とGemini様、いつもの会議をしましょう。
* ぼく＆Claude先生＆Gemini様：あーでもない…こーでもない…うんたらかんたら……

---

## やっとできたもの

他のクラスは、有名フレームワークも~~上手くパクり~~参考にしながら、直感でわりとすぐ満足のいく結果が出せていたのですが、今回は数回ほど破壊的な仕様変更を行いました。

そしてやっとできたのが、以下のような使い方をするクラスです。

```
$v = Validator::make(Request::postAll(), [
    'title'                 => ['max:100', 'label:タイトル'],
    'body'                  => ['label:本文'],
    'email'                 => ['email', 'max:255', 'label:メールアドレス'],
    'code'                  => ['optional', 'max:20', 'label:従業員コード'],  // 任意
    'is_active'             => ['boolean'],                                   // チェックボックス
    'status'                => ['label:ステータス'],
    'password'              => ['min:8', 'label:パスワード'],
    'password_confirmation' => ['label:パスワード（確認）'],
    'tel'                   => ['optional', 'label:電話番号'],
]);

// 宣言的に書けないルールは手続き型で追加
$v->in('status', ['active', 'inactive']);
$v->confirmed('password', 'password_confirmation');
$v->match('tel', '/^0\d{9,10}$/');

// エラー ※自動PRGパターン
if ($v->fails()) {
    $v->redirectWithErrors('/form');
}

// バリデーションを通ったデータ
$data = $v->validated();        // 全フィールド取得
$title = $v->value('title');    // 単一フィールド取得
```

---

## 設計判断 1: `required` をデフォルトにする

**「バリデーションルールにわざわざ書いたフィールドが任意なわけがない」** — 実務ではこの感覚が9割正しいと思いますし、**AIにとっては** 残りの1割に `optional` と明示する方が、全フィールドに `required` を書くより安全で簡潔です。

もうこれは、自分がAIになったつもりでフレームワークを作り続けてきた私の**直感**です(笑)

---

## 設計判断 2: `make()` をSingle Source of Truth（SSOT）にする

AIは「1箇所だけ見ればいい」状況で最もミスが減ります。

---

## 設計判断 3: 宣言的ルールと手続き型ルールの分離

### 混合バリデーターという選択

多くのバリデーターは、「宣言的オンリー」または「手続き的オンリー」のどちらかです。

```
// 【宣言的オンリー】 Laravel（文字列ベース）
'status' => 'required|in:active,inactive'

// 【手続き的オンリー】 CakePHP（メソッドチェーン）
$validator->requirePresence('status')->inList('status', ['active', 'inactive']);
```

`Lattice` では、この2つを **意図的に混合** しました。

```
// 宣言的: make() のルール配列
$v = Validator::make($input, [
    'title'  => ['max:100', 'label:タイトル'],
    'email'  => ['email', 'max:255', 'label:メールアドレス'],
    'status' => ['label:ステータス'],            // 必須（デフォルト）だがフォーマット制約なし
    'tel'    => ['optional', 'label:電話番号'],
]);

// 手続き的: メソッド呼び出し
$v->in('status', ['active', 'inactive']);
$v->match('tel', '/^0\d{9,10}$/');
```

### 分離の原則

どちらに置くかの基準はシンプルです。

> **値そのものの検証**（型・長さ・形式） → 宣言的（ルール文字列）  
> **外部データとの比較・複雑なパラメータ** → 手続き型（メソッド呼び出し）

…と、もっともらしい理由を書きましたが、この分離を採用した**実際の理由**は、文字列ルールの構文上の制約です。

### Laravel における「記法の選択肢」問題

Laravel では `in` ルールを手軽な文字列で書くことができます。

```
// Laravel — 手軽でスマート
'status' => 'required|in:draft,published,archived'
```

しかし、許可する値にカンマが含まれる場合は？

```
// ❌ 壊れる — "Tokyo, Japan" が "Tokyo" と " Japan" に分割される
'city' => 'required|in:Tokyo\, Japan,Osaka'
```

これを解決するため、Laravel は `Rule::in()` というオブジェクト記法を用意しました。配列記法と組み合わせることで安全に記述できます。

```
use Illuminate\Validation\Rule;

// ✅ 動く。ただし文字列記法との二重化。※これは「美しくない」と思う
'city' => ['required', Rule::in(['Tokyo, Japan', 'Osaka'])],
```

人間のためのFWであれば、後方互換性や手軽さのために「複数の手段を残す」のが正解ですが、AIのためのFWであれば、選択肢（正解）は1つの方が良いです。

### だったら最初から手続き型にすればいい

```
$v->in('status', ['active', 'inactive']);
```

配列をそのまま渡しますので、値にカンマが含まれていても壊れないですし、「2つの書き方」問題も発生しません。

同じ理由で、`match()` （正規表現）も手続き型にしています。正規表現をコロン区切りの文字列ルールに埋め込もうとすると、構文解析が複雑になり直感的ではなくなりますので。

```
$v->match('tel', '/\A0\d{9,10}\z/', '電話番号');
```

---

## 先生に聞いてみた

### 入力必須がデフォなFW

* ぼく：入力必須がデフォになってるFWは多いのですか？
* Claude先生：いえ少数派です。しかし「良いフレームワーク」が同じ判断をしている傾向があると感じています。

#### 🟢 required がデフォルト（安全側）

| フレームワーク | 言語 | オプトアウト方法 |
| --- | --- | --- |
| **Django Forms** | Python | `required=False` |
| **Zod** | TypeScript | `.optional()` |
| **Lattice** | PHP | `'optional'` |

#### 🔴 required は明示が必要（忘れると素通り）

| フレームワーク | 言語 | 必須にする方法 |
| --- | --- | --- |
| **Laravel** | PHP | `'required'` |
| **Rails** | Ruby | `validates :name, presence: true` |
| **Joi** | JavaScript | `.required()` |
| **Yup** | JavaScript | `.required()` |
| **Symfony** | PHP | `#[Assert\NotBlank]` |
| **Java Bean Validation** | Java | `@NotNull` / `@NotBlank` |
| **ASP.NET** | C# | `[Required]` |
| **CakePHP** | PHP | `->requirePresence()` |

* Claude先生：この通り「明示required派」が多数派ですね。
* Claude先生：少数派の `Django` や `Zod` は、**「フォームにフィールドを定義した時点で、それは受け取る意思がある ＝ 普通は必須」** という思想です。

```
# Django
name = forms.CharField(max_length=100)
```

```
// Zod
const schema = z.object({ name: z.string().max(100) });
```

```
// あなたのFW
$v = Validator::make($input, ['name' => ['max:100']]);
```

## 実害の比較

* Claude先生：起こり得る実害を比較してみましょう。

|  | required デフォルト | required 明示 |
| --- | --- | --- |
| 書き忘れた場合 | 任意のつもりが必須に → **ユーザーがエラーを見て気づく** | 必須のつもりが素通り → **空データがDBに入る** |
| 発見しやすさ | すぐ発覚する | しばらく気づかない |
| 被害 | UX上の不便（すぐ直せる） | データ汚染（後処理が必要） |

* Claude先生：**間違えた時の被害が非対称** なんです。安全側に倒れるデフォルトの方が、間違いが起きた時のダメージが小さい。
* Claude先生：`Django` と `Zod` という、世代もエコシステムも全く違うフレームワークが同じ結論に辿り着いているのは、これが本質的に正しい設計だからだと思います。

### Django Forms との共通点

* ぼく：意図的に宣言的と手続き的を混合した設計をしているFWは他にもあるのですか？
* Claude先生：`Django Forms` が先行していますね。

```
class ContactForm(forms.Form):
    # 宣言的: フィールド定義にルールを含む
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    status = forms.CharField()

    # 手続き的: clean_*() メソッドで外部比較やカスタムロジック
    def clean_status(self):
        status = self.cleaned_data['status']
        if status not in ['active', 'inactive']:
            raise ValidationError('無効なステータス')
        return status
```

|  | Django | Lattice |
| --- | --- | --- |
| 宣言的 | フィールドクラス定義 | `make()` のルール配列 |
| 手続き的 | `clean_*()` メソッド | `$v->in()`, `$v->match()` 等 |
| 全体検証 | `clean()` | `$v->addError()` |
| 検証済み取得 | `cleaned_data` | `validated()` / `value()` |

* Claude先生：**ほぼ同じ思想** ですね。Django は Python 界で最も成功した Web フレームワークの一つなので、この設計パターン自体は実績があります。
* Claude先生：違いは、Django がクラス定義を必要とするのに対し、`Lattice` はAIの認知負荷を下げるために **Controller 内にインラインで書けるようにした** 点ですね。
* ぼく：（あ、いや先生…それはただの偶然です…。）

---

## Laravelとの比較

* ぼく：先生！他のPHP用FWとどちらが使いやすいですか？ 忖度なしで率直に答えてください。
* Claude先生：率直に言います。AIにとって最も間違えにくいValidatorの一つだと感じています。

### vs Laravel

```
// Lattice
$v = Validator::make(Request::postAll(), [
    'title'  => ['max:100', 'label:タイトル'],
    'code'   => ['optional', 'max:20', 'label:従業員コード'],
    'status' => ['label:ステータス'],
    'tags'   => ['array'],
    'email'  => ['email', 'max:255', 'label:メールアドレス'],
]);
$v->in('status', ['active', 'inactive']);
```

```
// Laravel
$validated = $request->validate([
    'title'  => 'required|string|max:100',
    'code'   => 'nullable|string|max:20',
    'status' => 'required|in:active,inactive',
    'tags'   => 'sometimes|array',
    'email'  => 'required|email|max:255|unique:users,email,' . $user->id,
]);
```

#### AIが間違えやすいポイントでの差

> ※補足：Laravelの強み（エコシステムの大きさ、`unique` のようなDB連携ルール、  
> `FormRequest` によるバリデーション層の分離など）は割愛した、  
> 「AIにとって何が嬉しいか？」のみの比較表になっているようです。

| 観点 | Laravel | このフレームワーク | AI視点 |
| --- | --- | --- | --- |
| required の扱い | 書き忘れると通る（**バグ**） | デフォルトで必須（**安全側に倒れる**） | ✅ 安全 |
| ルール記法 | パイプ区切り文字列 `'required|string|max:100'` | 配列 `['max:100']` | ✅ AIにとって配列は構造的に扱いやすい |
| inルール | `'in:active,inactive'`（カンマが値に含まれると破綻） | `$v->in('status', [...])` | ✅ 配列渡しが確実 |
| `nullable` vs `optional` | `nullable` は null を許可、`sometimes` はキー不在を許可、紛らわしい | `optional` 一つで統一 | ✅ 迷いがない |
| バリデーション後の取得 | `$validated` に入る / FormRequest なら `$request->validated()` | `$v->validated()` / `$v->value()` | ほぼ同等 |
| エラー後のリダイレクト | 基本自動(手動も可) | `$v->redirectWithErrors()` 一行 | ✅ 選択肢がなく明示的 |

#### vs Symfony

```
// Symfony — アノテーション/アトリビュート方式
#[Assert\NotBlank]
#[Assert\Length(max: 100)]
private string $title;
```

* Claude先生：Symfony は型安全性が高い点が優秀です。
* Claude先生：しかし、Validatorコンポーネントは、`DTO` や `Entity` にアトリビュートを付与して使うのが主流で、1つのバリデーションのために複数ファイルを触る必要があり、AIにとっては認知コストが高いです。

※補足：Validation::createValidator() を呼び出すことで、DTOを作らずとも直接 `Constraints` をインライン適用し、バリデーションを実行することは可能です。しかし、そういう「選択肢」はAIには不要…というのはこれまで何度か書いてきた通りです。

#### vs CakePHP

* Claude先生：CakePHP はメソッドチェーンで組み立てる方式で、可読性は良いです。
* Claude先生：しかし、対象が増える → 記述量が多くなる → AIが書き忘れるリスクが増し、忘れた＝バグとなります。

---

## 先生の総評

### required デフォルトは設計上の最大のヒット

* Claude先生：正直これが一番大きいです。
* Claude先生：AIは「このフィールドは必須かな？」と毎回考える必要がなく、**任意の場合だけ `optional` と書けばいい**。これだけで生成コードのバリデーション漏れが激減します。

### 正直に言う弱点

#### 1. `label:` の位置が自由すぎる

```
['max:100', 'label:タイトル']  // 末尾
['label:タイトル', 'max:100']  // 先頭でも動く
```

* Claude先生：どちらでも動くのは柔軟ですが、この設計はあなたらしくないです。
* Claude先生：AIも「先頭に書く派」と「末尾に書く派」でブレが生じ、生成のたびに微妙に位置が変わりがちです。
* Claude先生：ただ**実害はゼロ**ですので、些末な話です。

#### 2. 複合バリデーション（フィールド間の依存関係）が手動

* Claude先生：例えば `XXXController` の「'その他'のとき reason\_text 必須」のような条件付きバリデーションは `addError()` で手動になります。
* Claude先生：ここはもしLaravel なら、`required_if` で宣言的に書けますね。
* Claude先生：ただし、この手の条件付きルールは**ビジネスロジックに近い**ですので、手動で書く方がむしろ意図が見える、という解釈も成り立ちます。

---

## 最後に

人間にとっての「便利さ」や「柔軟性」は、AIにとっては罠となります。

後方互換性のための複数の記法、明示しないと安全側に倒れないデフォルト設定、どこにでも書ける柔軟な構文…。

これらは、人間にとっては便利な選択肢ですが、AIにとっては「どちらを選ぶか迷うノイズ」や「書き忘れても気づかないバグの温床」になります。

冒頭で私が「違う！そうじゃない！美しくない！」と叫んでいた原因は、Claude先生が間違えたからではなく、\*\*当時の私のフレームワーク設計が許容してしまっていた「柔軟性という名の曖昧さ」\*\*でした。

AIに爆速で、かつ正確にコードを書かせるための専用道路（フレームワーク）を作るのであれば、「AIが迷う余地がない、常に正解が1つしかない状態」を目指すべきだと思います。

## 結論

パッと見で「美しくない」と直感する設計には大抵どこかに穴があり、その穴はAIにとっては大穴となる。
