---
id: "2026-06-07-claude-codeを始めようとしたら先にclaudeと仕様会議が始まった話-01"
title: "Claude Codeを始めようとしたら、先にClaudeと仕様会議が始まった話"
url: "https://qiita.com/savioka/items/b59ac711e98bb80d4a50"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "LLM", "JavaScript", "TypeScript"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

前回の記事では、Claude Codeを勉強しようと思っていたら、気付けば3週間でテニスアプリを公開していた話を書きました。

テニスアプリの本番サイトは以下です。

https://tennisplayer-status.web.app/

今回は、その時に思っていたことと実際に起きたことが全然違った話です。

私は最初、

「Claude Codeを起動して、作りたいものを説明して、コードを書いてもらう」

くらいのイメージを持っていました。

ところが実際には、

Claude Codeを起動する前に、Claudeと延々と仕様の話をしていました。

---

## 最初にやったのはClaude Codeではなかった

UdemyでClaude Codeの教材を買って、いよいよ何か作ってみようと思いました。

題材はテニスアプリです。

以前からコーチにもらったアドバイスをiPhoneのメモに残していたので、

「これをアプリ化できたら面白そうだな」

と思っていました。

そこで私はClaudeにこうお願いしました。

```text
以下のようなスマホアプリをClaude Codeで作成したいので、指示書作成支援をお願いします。
```

そして、作りたい内容を箇条書きで並べました。

```text
・テニスの自分の能力値確認アプリ
・モバイル端末での使用を前提としたデザイン
・プレイヤーレベルとしてNTRP値を使用する
・質問への回答からNTRP値を自動計算する
・フォアやバック、サーブなどもレベル管理する
・練習ログを蓄積する
・AIがレベルアップ提案を行う
```
※NTRP値とは、テニス界では良く知られたテニスの上手さを表す指標を数値で表現した値のことです。

今見返すと結構雑です。

でも当時の私は、

「これをいい感じに仕様書にしてくれるんだろうな」

と思っていました。

---

## なかなか仕様書を書いてくれない

ところがClaudeは、すぐには仕様書を書いてくれません。

代わりに仕様確認と質問が飛んできます。

* NTRPの範囲はどこまで？
* ショット別の分類はこんな感じでどう？
* DB保存はlocalStorageでいい？
* 将来的なiOS,Androidアプリの可能性は？

などなど。

最初は正直、

「いや、仕様書作ってくれればいいんだけど…」

と思っていました。

---

## 気付けば仕様検討会になっていた

でも何回かやり取りしているうちに気付きます。

これ、人間相手の要件定義と同じでは？

私はアイデアを話す。

Claudeが質問する。

私が答える。

Claudeが整理する。

また新しい案が出てくる。

気付けば普通に仕様検討会です。

しかも相手は24時間働くし、文句も言わない。

---

## 一番驚いたのはここ

実は今回一番驚いたのは、Claude Codeの実装能力ではありません。

Claudeが仕様整理を手伝ってくれることでした。

私は最初、

「AIがコードを書く時代になった」

と思っていました。

でも実際に使ってみると、

「AIが要件定義に参加する時代になった」

という感覚の方が強いです。

---

## 仕様がまとまったらMarkdownにする

議論がある程度まとまったら、今度はClaudeにお願いしました。

```text
ここまでの内容をClaude Code向けの指示書としてMarkdown形式で出力してください
```

すると、それまでの会話を整理した.mdファイルを出力してくれます。
<div style="height: 200px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;">
ここに長いテキストやコードを貼り付けてください。<br>
高さが200pxを超えると、自動的にスクロールバーが表示されます。<br>
（以下、長いテキストを続ける）
</div>
こうして出力したのが以下のMarkdown形式のファイルです。



<details>
<summary>「テニス能力値管理アプリ — Claude Code 指示書 v5.0」を展開する（クリックで開きます）</summary>



# テニス能力値管理アプリ — Claude Code 指示書 v5.0

---

## プロジェクト概要

テニスプレイヤーが自分の能力値（NTRP）とショット別スキルを可視化・記録・成長管理できるモバイルファーストのWebアプリ。
コーチが複数の生徒プロフィールをデバイスを問わず安全に管理する用途も想定する。

### 設計方針

- **データ保存はFirebase（Firestore）**：データ消失リスクをゼロにする
- **認証はGoogleログインのみ**：実装をシンプルに保つ
- **コーチ〜生徒間の連携機能はなし**：コーチが自分のアカウントで複数プロフィールを管理する
- **完全なWebサービス**：iOS/Android問わずブラウザで動作。PWA対応
- **維持費無料**：Firebase Sparkプラン（無料）で数百ユーザー規模まで運用可能

---

## 技術スタック

- **フレームワーク**: React (Vite) + TypeScript
- **スタイリング**: Tailwind CSS
- **状態管理**: React Context + useReducer
- **バックエンド**: Firebase
  - Firestore（データ保存）
  - Firebase Authentication（Googleログインのみ）
  - Firebase Hosting（ホスティング）
- **対象環境**: スマートフォンブラウザ（PWA対応）

### Firebase料金（Sparkプラン無料枠）

| リソース | 無料枠 | 想定使用量 |
|---------|--------|-----------|
| Firestore読み取り | 5万回/日 | 十分 |
| Firestore書き込み | 2万回/日 | 十分 |
| Firestore容量 | 1GB | テキストのみなので数百ユーザーでも余裕 |
| Authentication | 無制限 | 制限なし |
| Hosting | 10GB転送/月 | 十分 |

無料枠を超えた場合はBlazeプラン（従量課金）に移行。急激な課金にはなりにくい。

---

## Firebaseプロジェクト設定

```typescript
// src/lib/firebase.ts
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

export const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
```

- 環境変数は `.env.local` に記載し、`.gitignore` に追加すること
- Firestoreのオフラインキャッシュを有効化すること（`enableIndexedDbPersistence`）
  → オフライン時でも閲覧可能になり、復帰時に自動同期される

---

## データモデル（TypeScript型定義）

```typescript
// ショット種別
type ShotType =
  | 'forehand'
  | 'backhand'
  | 'forehand_volley'
  | 'backhand_volley'
  | 'serve'
  | 'return'
  | 'overhead'
  | 'drop_shot';

// スキル要素
type SkillElement = {
  elementId: string;
  name: string;
  level: number; // 1〜10
};

// ショット別スキル
type ShotSkill = {
  shotType: ShotType;
  elements: SkillElement[];
  overallLevel: number; // 要素の平均値（小数第1位）
  lastUpdated: string;
};

// プレイヤープロフィール
type PlayerProfile = {
  id: string;
  ownerUid: string;       // Firebase Auth UID（所有者）
  name: string;
  memo: string;           // コーチ用メモ（自由記述）
  dominantHand: 'right' | 'left';
  backhandType: 'one' | 'two';
  ntrp: number;           // 1.5〜6.0（0.5刻み）
  skills: ShotSkill[];
  createdAt: string;
  updatedAt: string;
};

// テニスログ
type TennisLog = {
  id: string;
  playerId: string;
  ownerUid: string;       // Firebase Auth UID
  date: string;           // 'YYYY-MM-DD'
  sessionType: 'practice' | 'match' | 'lesson';
  duration: number;       // 分
  entries: LogEntry[];
  overallNote: string;
  createdAt: string;
};

// ログエントリ（ショット別メモ）
type LogEntry = {
  shotType: ShotType;
  note: string;
  feltLevel: number | null; // 1〜10
};

// レベルアップ提案
type LevelUpSuggestion = {
  id: string;
  playerId: string;
  ownerUid: string;
  targetType: 'ntrp' | ShotType;
  currentLevel: number;
  suggestedLevel: number;
  reason: string;
  basedOnLogIds: string[];
  status: 'pending' | 'accepted' | 'rejected';
  createdAt: string;
};
```

---

## Firestoreコレクション設計

```
players/
  {playerId}/
    ownerUid: string
    name: string
    memo: string
    dominantHand: string
    backhandType: string
    ntrp: number
    skills: ShotSkill[]   ← 配列として埋め込み（ショット数固定のため）
    createdAt: timestamp
    updatedAt: timestamp

logs/
  {logId}/
    playerId: string
    ownerUid: string
    date: string
    sessionType: string
    duration: number
    entries: LogEntry[]   ← 配列として埋め込み
    overallNote: string
    createdAt: timestamp

suggestions/
  {suggestionId}/
    playerId: string
    ownerUid: string
    targetType: string
    currentLevel: number
    suggestedLevel: number
    reason: string
    basedOnLogIds: string[]
    status: string
    createdAt: timestamp
```

---

## Firestoreセキュリティルール

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // 全コレクション共通: 自分のデータのみ読み書き可
    match /players/{playerId} {
      allow read, write: if request.auth != null
        && request.auth.uid == resource.data.ownerUid;
      allow create: if request.auth != null
        && request.auth.uid == request.resource.data.ownerUid;
    }

    match /logs/{logId} {
      allow read, write: if request.auth != null
        && request.auth.uid == resource.data.ownerUid;
      allow create: if request.auth != null
        && request.auth.uid == request.resource.data.ownerUid;
    }

    match /suggestions/{suggestionId} {
      allow read, write: if request.auth != null
        && request.auth.uid == resource.data.ownerUid;
      allow create: if request.auth != null
        && request.auth.uid == request.resource.data.ownerUid;
    }
  }
}
```

---

## NTRPレベル定義（1.5〜6.0）

| NTRP | 説明 |
|------|------|
| 1.5 | 経験がほとんどなく、ボールをコートに入れることが主な目標 |
| 2.0 | 基本ポジションは理解しているが、ストロークに明らかな弱点がある |
| 2.5 | ゆっくりしたラリーをある程度続けられる。コートカバーはまだ弱い |
| 3.0 | 中程度のペースなら安定して打てるが、方向・深さ・パワーのコントロールは不安定 |
| 3.5 | 方向コントロールが改善された。ただし深さとバリエーションにはまだ課題あり |
| 4.0 | 安定したストロークで方向・深さをコントロールできる。スピンやスライスも使える |
| 4.5 | パワーと安定性を兼ね備えたストロークが打てる。戦術的なプレーが可能 |
| 5.0 | 強力な武器ショットを持ち、試合全体を通じてその武器を活かせる |
| 5.5 | パワーまたは安定性（あるいは両方）が本物の武器。プレッシャー下でも安定 |
| 6.0 | ジュニア・大学レベルの全国大会経験者。都道府県以上のランキング保持者レベル |

---

## ショット別スキルレベル設計（1〜10、要素分解）

### フォアハンド

| 要素 | Lv1〜3 | Lv4〜6 | Lv7〜8 | Lv9〜10 |
|------|--------|--------|--------|---------|
| グリップ・準備 | 握り方が不安定 | 毎回同じグリップで構えられる | セミウエスタン以上で安定 | 戦術的なグリップ変化 |
| テイクバック | ラケットが遅れる | ユニットターンができる | コンパクトで早い準備 | 球種に応じて即座に変化 |
| インパクト | 芯を外すことが多い | だいたい芯で捉えられる | 毎回安定した面で打てる | 意図した打点で確実に |
| フォロースルー | バラバラ | 一定のフォームになってきた | 安定した振り抜き | 打ち分けに応じたFSが使える |
| 方向コントロール | ほぼランダム | クロス/ストレートを意識できる | 狙ったコースに打てる | コーナーを正確に狙える |
| スピン/スライス | かけられない | 少しトップスピンがかけられる | スピン/フラット使い分け | スピン量を自在に調整 |

### バックハンド

| 要素 | 説明 |
|------|------|
| グリップ・準備 | バックハンドグリップへの切り替え速度 |
| テイクバック | 両手/片手に応じた適切な引き方 |
| インパクト | 安定した打点でボールを捉えられるか |
| 方向コントロール | クロス/ストレートの打ち分け |
| スライス活用 | スライスバックハンドが使えるか |
| 高いボール対応 | 高い打点のバックハンドを処理できるか |

### サーブ

| 要素 | 説明 |
|------|------|
| トス | 安定したトスが上げられるか |
| コンチネンタルグリップ | サーブ用グリップが使えるか |
| プロネーション | ラケットの回内動作ができているか |
| 1stサーブ確率 | ファーストサーブの入確率 |
| 2ndサーブ安定性 | セカンドでダブルフォルトしない安定感 |
| コース打ち分け | ワイド/ボディ/センターを意図的に打てるか |
| スピン/スライス | キックサーブやスライスサーブが使えるか |

### フォアボレー／バックボレー

| 要素 | 説明 |
|------|------|
| コンチネンタルグリップ | ボレー用グリップへの切り替え |
| コンパクトなスイング | 大きく振らずに打てるか |
| 前でのインパクト | 体より前で打てているか |
| 方向コントロール | 狙った方向に打てるか |
| ローボレー対応 | 低いボールを拾えるか |

### リターン

| 要素 | 説明 |
|------|------|
| 構え・スプリットステップ | リターン前の適切な準備 |
| ファーストサーブへの対応 | 速いサーブに対して返球できるか |
| セカンドサーブへの積極性 | セカンドに対して攻めていけるか |
| コースの読み | サーバーの動きからコースを予測できるか |

### スマッシュ

| 要素 | 説明 |
|------|------|
| ポジショニング | 素早く下がってボールの下に入れるか |
| テイクバック | サーブに近い準備ができているか |
| インパクト | 高い打点で確実に捉えられるか |
| 決定力 | ポイントを取りきれるか |

### ドロップショット

| 要素 | 説明 |
|------|------|
| タイミング | 相手が下がったときに使えるか |
| スピンコントロール | バックスピンで手前で止められるか |
| フォームの隠し方 | ドロップと悟らせないスイングができているか |

---

## 画面構成

```
[未ログイン時]
  └─ ログイン画面（Googleログインボタンのみ）

[初回ログイン時]
  └─ プロフィールが0件 → 新規作成フローへ自動遷移

[新規プロフィール作成フロー]
  └─ Step1: 名前・利き手・バックハンドタイプ・メモ
  └─ Step2: NTRPアセスメント（質問7問）
  └─ Step3: ショット別微調整（質問4問）
  └─ Step4: 完了 → ホーム画面へ

[メイン画面]
  ├─ ホーム: 人体図スキルマップ
  ├─ ログ入力: 練習・試合の記録
  ├─ 履歴: カテゴリ別ログ一覧
  └─ 設定: プロフィール管理・ログアウト
```

---

## ログイン画面（LoginScreen）

```
┌─────────────────────────────────┐
│                                  │
│     🎾 テニス能力値管理           │
│                                  │
│   プレイヤーとコーチのための      │
│   スキル記録・成長管理アプリ      │
│                                  │
│  ┌───────────────────────────┐  │
│  │  G  Googleでログイン       │  │
│  └───────────────────────────┘  │
│                                  │
└─────────────────────────────────┘
```

- Googleログインボタンのみ表示（メール/パスワード不要）
- ログイン成功後、プロフィールの有無を確認して遷移先を決定

---

## 新規プロフィール作成フロー

### Step 1: 基本情報

- 名前入力（必須）
- 利き手: 右手 / 左手
- バックハンドタイプ: 片手 / 両手
- メモ（任意・コーチが生徒の特徴を記入するための自由欄）

### Step 2: NTRPアセスメント

| # | 質問 | 選択肢（スコア） |
|---|------|----------------|
| 1 | テニス歴はどのくらいですか？ | 未経験(0) / 〜1年(1) / 1〜3年(2) / 3〜7年(3) / 7年以上(4) |
| 2 | ラリーを何球続けられますか？ | 3球以下(0) / 3〜10球(1) / 10〜20球(2) / 20球以上(3) |
| 3 | サーブはどのくらい入りますか？ | ほぼ入らない(0) / 半分くらい(1) / 安定して入る(2) / コースを狙える(3) |
| 4 | 試合経験はありますか？ | なし(0) / 草トーナメント(1) / 市区町村大会(2) / 都道府県以上(3) |
| 5 | スピンをかけて打てますか？ | できない(0) / 少しかけられる(1) / 安定してかけられる(2) / 使い分けられる(3) |
| 6 | ボレーはできますか？ | ほぼできない(0) / 当てるだけ(1) / 方向を狙える(2) / コントロールできる(3) |
| 7 | 戦術を意識して試合ができますか？ | していない(0) / 少し意識する(1) / 戦術的に動ける(2) / 相手に合わせて変えられる(3) |

**NTRP計算ロジック**:
```
合計  0〜 3 → NTRP 1.5
合計  4〜 6 → NTRP 2.0
合計  7〜 9 → NTRP 2.5
合計 10〜12 → NTRP 3.0
合計 13〜14 → NTRP 3.5
合計 15〜16 → NTRP 4.0
合計 17〜18 → NTRP 4.5
合計 19〜20 → NTRP 5.0
合計    21  → NTRP 5.5以上
```

### Step 3: ショット別微調整

| ショット | 質問 | 補正 |
|---------|------|------|
| フォアハンド | 「フォアはテニスで一番得意なショットですか？」 | 得意 → +1、普通 → ±0、苦手 → -1 |
| バックハンド | 「バックハンドは安定して打てますか？」 | 安定 → ±0、やや不安 → -1、苦手 → -2 |
| サーブ | 「サーブに自信はありますか？」 | 自信あり → +1、普通 → ±0、弱点 → -1 |
| ボレー | 「ネットプレーは積極的に使いますか？」 | 積極的 → +1、たまに → ±0、ほぼしない → -1 |

**NTRP → ショットレベル基準値**:
```
NTRP 1.5 → Lv.1〜2  /  NTRP 2.0 → Lv.2〜3
NTRP 2.5 → Lv.3     /  NTRP 3.0 → Lv.3〜4
NTRP 3.5 → Lv.4〜5  /  NTRP 4.0 → Lv.5
NTRP 4.5 → Lv.6     /  NTRP 5.0 → Lv.7
NTRP 5.5 → Lv.8〜9  /  NTRP 6.0 → Lv.9〜10
```

---

## ホーム画面（SkillMapScreen）

### プロフィール切り替えバー（画面最上部）

```
┌─────────────────────────────────┐
│ [自分▼]  田中  鈴木  山田  [+] │ ← 横スクロール可能なタブ
└─────────────────────────────────┘
```

- タップで表示するプロフィールを切り替える
- `[+]` で新規プロフィール作成フローへ遷移
- 現在選択中のプロフィール名を太字で表示

### スキルマップ（右利きの場合）

```
┌─────────────────────────────────┐
│ [自分▼]  田中  鈴木  [+]        │
├─────────────────────────────────┤
│      [サーブ Lv.5 ██████░░░░]   │ ← 上部中央
│      [スマッシュ Lv.4 █████░░░] │
│                                  │
│ [FHボレー]   🏃‍♂️   [BHボレー]     │
│ Lv.6 ████  シルエット  Lv.4 ████ │
│                                  │
│ [フォア]             [バック]     │
│ Lv.7 ███████     Lv.5 █████░░   │
│                                  │
│      [リターン Lv.4 ████░░░░]   │ ← 下部中央
│      [ドロップ Lv.3 ███░░░░░]   │
└─────────────────────────────────┘
```

- 右利き → フォア/FHボレーが右側、バック/BHボレーが左側
- 左利き → フォア/FHボレーが左側、バック/BHボレーが右側
- シルエットはインラインSVGで実装（ラケットを持つポーズ、外部リソース不使用）
- レベルバーの色: Lv1〜3グレー / 4〜6ブルー / 7〜8グリーン / 9〜10ゴールド
- レベルアップ提案がある場合は ⬆️ バッジをカードに表示

---

## ショット詳細シート（ShotDetailSheet）

ショットカードタップ時にBottomSheetで表示。

```
┌──────────────────────────────┐
│ フォアハンド         Lv. 6.4 │
│                              │
│ 要素別スキル:                 │
│ グリップ・準備  ████████░░ 8 │
│ テイクバック    ███████░░░ 7 │
│ インパクト      ██████░░░░ 6 │
│ フォロースルー  ██████░░░░ 6 │
│ 方向コントロール █████░░░░░ 5 │
│ スピン/スライス  ████░░░░░░ 4 │
│                              │
│ 直近の気づき:                 │
│ 5/28「インパクトで面が…」     │
│ 5/25「回り込みフォアが…」     │
│              [もっと見る]     │
│  [⬆️ Lv.7への提案あり]       │
└──────────────────────────────┘
```

---

## ログ入力画面（LogInputScreen）

- 日付（デフォルト: 今日）
- セッション種別: 練習 / 試合 / レッスン
- 練習時間（分）
- 全体メモ（自由記述）
- ショット別メモ（アコーディオン展開）
  - 各ショットに「今日の気づき」テキストエリア
  - 今日の感覚レベル（任意スライダー 1〜10）
- 保存時にレベルアップ判定を自動実行

---

## ログ履歴画面（LogHistoryScreen）

- タブ絞り込み: 全体 / フォア / バック / サーブ / ボレー / その他
- 時系列カード（新しい順）
- カードタップで詳細展開・削除

---

## 設定画面（SettingsScreen）

- プロフィール一覧（名前・NTRP・作成日）
- 各プロフィールの編集（名前・利き手・メモ）
- プロフィールの削除（確認ダイアログあり）
- ログアウトボタン
- アカウント削除（全データ削除 + Firebase Authからの削除）

---

## レベルアップ判定ロジック

ログ保存時に自動実行。

```typescript
function evaluateLevelUp(
  logs: TennisLog[],
  skills: ShotSkill[],
  currentNTRP: number
): LevelUpSuggestion[] {
  const suggestions: LevelUpSuggestion[] = [];

  for (const skill of skills) {
    const recentLogs = getRecentLogsForShot(logs, skill.shotType, 5);

    // ルール1: 感覚レベル平均が現在レベル+1以上（3件以上ある場合）
    const feltLevels = recentLogs
      .map(l => l.feltLevel)
      .filter((v): v is number => v !== null);
    if (feltLevels.length >= 3) {
      const avg = feltLevels.reduce((a, b) => a + b, 0) / feltLevels.length;
      if (avg >= skill.overallLevel + 1.0) {
        suggestions.push(createSuggestion(
          skill, `直近${feltLevels.length}回の感覚平均が${avg.toFixed(1)}`
        ));
      }
    }

    // ルール2: ポジティブキーワードが直近5件中3件以上
    const positiveKeywords = [
      '安定', '入った', '改善', '上手', 'できた', '会心', 'よくなった', 'つかめた'
    ];
    const positiveCount = recentLogs.filter(l =>
      positiveKeywords.some(kw => l.note.includes(kw))
    ).length;
    if (positiveCount >= 3) {
      suggestions.push(createSuggestion(
        skill, `ポジティブな記録が${positiveCount}件続いています`
      ));
    }
  }

  // NTRP全体評価
  const avgLevel = skills.reduce((a, s) => a + s.overallLevel, 0) / skills.length;
  const ntrpEquivalent = ntrpToSkillLevel(currentNTRP);
  if (avgLevel >= ntrpEquivalent + 1.0) {
    suggestions.push(createNTRPSuggestion(
      currentNTRP, `全ショット平均レベルが${avgLevel.toFixed(1)}に達しました`
    ));
  }

  return suggestions;
}
```

---

## レベルアップ提案UI

```
┌─────────────────────────────┐
│ 🎾 レベルアップ提案！         │
│                              │
│ フォアハンド                  │
│ Lv.6 → Lv.7                  │
│                              │
│ 直近5回の感覚レベル平均が     │
│ 7.2です。メモにも「安定」が   │
│ 3回見られます。               │
│                              │
│ [今は見送る]  [レベルアップ！] │
└─────────────────────────────┘
```

---

## ファイル構成

```
src/
├── components/
│   ├── auth/
│   │   └── LoginScreen.tsx
│   ├── onboarding/
│   │   ├── OnboardingFlow.tsx
│   │   ├── BasicInfoStep.tsx
│   │   ├── NTRPAssessment.tsx
│   │   └── ShotLevelStep.tsx
│   ├── home/
│   │   ├── SkillMap.tsx
│   │   ├── ProfileSwitcher.tsx
│   │   ├── PlayerSilhouette.tsx   ← インラインSVG
│   │   ├── ShotCard.tsx
│   │   └── ShotDetailSheet.tsx
│   ├── log/
│   │   ├── LogInputScreen.tsx
│   │   ├── ShotLogEntry.tsx
│   │   └── LogHistoryScreen.tsx
│   ├── settings/
│   │   └── SettingsScreen.tsx
│   └── common/
│       ├── BottomSheet.tsx
│       ├── LevelBar.tsx
│       └── LevelUpProposal.tsx
├── context/
│   ├── AuthContext.tsx             ← Firebase Auth状態管理
│   ├── PlayerContext.tsx           ← プロフィール一覧・切り替え管理
│   └── LogContext.tsx
├── hooks/
│   ├── useNTRPCalculator.ts
│   ├── useLevelUpEvaluator.ts
│   └── useFirestore.ts             ← Firestore操作の共通フック
├── utils/
│   ├── ntrpMapping.ts
│   ├── shotSkillDefinitions.ts
│   └── keywordAnalysis.ts
├── lib/
│   └── firebase.ts
├── types/
│   └── index.ts
└── App.tsx
```

---

## 実装ロードマップ

| ステップ | 内容 |
|---------|------|
| 1 | Firebaseプロジェクト作成・設定（firebase.ts + .env.local） |
| 2 | 型定義・shotSkillDefinitions・ntrpMappingの実装 |
| 3 | AuthContext（Googleログイン/ログアウト） |
| 4 | ログイン画面 |
| 5 | PlayerContext・LogContext（Firestore連携） |
| 6 | 新規プロフィール作成フロー（Step1〜3） |
| 7 | ホーム画面（ProfileSwitcher + SkillMap + SVGシルエット） |
| 8 | ショット詳細BottomSheet |
| 9 | ログ入力画面 |
| 10 | ログ履歴画面 |
| 11 | レベルアップ判定 + 提案UI |
| 12 | 設定画面 |
| 13 | Firestoreセキュリティルールの適用・テスト |
| 14 | PWA対応（manifest + service worker） |
| 15 | Firebase Hostingへのデプロイ |
| 16 | デザイン調整・アニメーション・全体QA |

---

## 実装時の注意事項

1. **モバイルファースト**: 最大幅390px基準。タップターゲット最小44px。
2. **認証ガード**: 未ログイン状態でメイン画面にアクセスした場合はログイン画面にリダイレクト。
3. **Firestoreオフラインキャッシュ**: `enableIndexedDbPersistence` を有効化し、オフライン時も閲覧可能にする。
4. **ownerUidの徹底**: 全ドキュメントに `ownerUid` を付与し、他ユーザーのデータへのアクセスをセキュリティルールで完全に遮断する。
5. **SVGシルエット**: 人体図（ラケットを持つポーズ）はインラインSVGで実装。外部リソース不使用。
6. **利き手ミラーリング**: 利き手の設定変更時にSkillMapのレイアウトが即座に反映される。
7. **レベルバー色**: Lv1〜3グレー / 4〜6ブルー / 7〜8グリーン / 9〜10ゴールド。
8. **環境変数**: Firebase設定情報は `.env.local` に記載し、`.gitignore` に追加すること。
9. **アクセシビリティ**: ショットカードにaria-label付与。

</details>
</b>

※私自身は技術的なところに関してはほぼ介入していません。
技術スタックの内容に関しても詳細を詳しく知っているわけではありません！笑

私はこのファイルをプロジェクトフォルダへコピーしました。

---

## Claude Codeの出番はそこから

その後、

```bash
claude
```

でClaude Codeを起動し、

```bash
/init
```

を実行。

生成されたCLAUDE.mdを元に実装を依頼していきます。

つまり私の場合、

Claude Codeを使う前に、

まずClaudeで指示書を作っていました。

---

## 今のところの結論

最初の私は、

「どうやってClaude Codeに指示を出そう」

と考えていました。

でも今は少し考え方が変わっています。

まずClaudeと会話する。

仕様を整理する。

指示書を作る。

その後でClaude Codeに実装してもらう。

この流れの方がずっとスムーズでした。

もしこれからClaude Codeを触る方がいたら、いきなり実装を始める前に、

「指示書作成を手伝ってください」

とClaudeへお願いしてみるのもおすすめです。

少なくとも私は、その方法でかなり助けられました。

もしかするとClaude Codeを既に触っている人なら、
「そんなの当たり前すぎるわ！」
と思われるかもですよね。

そうかもしれません笑

次回はClaude Codeにまかせて失敗したことについて書いていきたいと思います。

よろしければお付き合いください！
