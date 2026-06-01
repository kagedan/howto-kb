---
id: "2026-05-31-claude-code-で-ai営業アシスタントを作った話-企業検索営業メール自動生成-01"
title: "Claude Code で AI営業アシスタントを作った話 ─ 企業検索×営業メール自動生成"
url: "https://zenn.dev/columbus0370/articles/d98592bf88af6c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "Python", "zenn"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

# Claude Code で AI営業アシスタントを作った話

## 作ったもの

**AI営業アシスタント** ─ 国内50万社以上の法人DBから企業を絞り込んで、Claude AIが相手企業に合わせた営業メールを即生成するWebアプリです。

🔗 **Live Demo:** <https://columbus-enterprise-search.vercel.app>

| ステップ | 作業 | 時間 |
| --- | --- | --- |
| 従来 | 企業リスト収集 → 一社ずつメール作成 | 60〜90分 |
| **このツール** | 条件で企業検索 → AIメール生成 | **5分以内** |

フリーランスや営業代行をやっていると「リスト作り」と「初回メール作成」に時間が消えていく問題があります。自分自身もそれで困っていたので作りました。

**技術スタック：**

* フロントエンド：React 19 + Vite + Tailwind CSS
* バックエンド：Python / FastAPI + Anthropic SDK
* AI：Claude Haiku（コスト効率重視）
* データ：gBizINFO REST API（経産省の無料法人DB）
* デプロイ：Vercel（フロント）/ Render.com（バック）

---

## 詰まった5つのポイント

### ① CORS preflight が 400 を返し続ける問題

最初にハマったのがこれです。フロントからAPIを叩くと OPTIONS リクエスト（preflight）が 400 で弾かれる。

**原因：** FastAPIのミドルウェア適用順序の問題でした。`CORSMiddleware` より先に他のミドルウェアが走ってしまい、preflight が正しく処理される前にリクエストが弾かれていました。

```
# NG：CORSより先にslowapi（レート制限）が走る
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware, ...)

# OK：CORSを最初に追加（= 最後に実行されるが、preflightは最優先）
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(SlowAPIMiddleware)

FastAPIのミドルウェアはスタック構造で、後から追加したものが先に実行されます。CORS処理は必ずスタックの先頭（= 最後にadd_middleware）に来るべきでした。

さらに、VercelのプレビューURLが毎回変わる問題もあり、正規表現で対応：

# settings.py
cors_origin_regex: str = r"https://.*\.vercel\.app"

Claude Code に「FastAPIでCORSが405になる原因を整理して」と投げたら、ミドルウェア順序の問題を即座に指摘してくれました。

---
② gBizINFO API の検索パラメータ設計

gBizINFO (https://info.gbiz.go.jp/) は経産省が提供する無料の法人DBです。APIトークンさえ取れば50万社以上を検索できますが、クセがある。

ハマりポイント：
- パラメータ名が英語と日本語混在
- 売上高・従業員数・資本金はレンジ指定（min/max）
- None のパラメータをそのままURLに渡すと ?param=None として送られてしまう

# services/gbizinfo.py
async def search(self, params: SearchParams) -> dict:
    query = {k: v for k, v in params.dict().items() if v is not None}
    response = await self.client.get("/v1/hojin", params=query)

Noneフィルタリングを忘れると、gBizINFOが不正なパラメータとして弾いてきます。地味だけど必須の処理です。

---
③ Claude Haiku のプロンプト設計 ─ コストと品質のバランス

メール生成に使うモデルは Claude Haiku（$0.25/1M tokens）にしました。Sonnetだとコストが跳ね上がるので、Haikuで品質を確保するプロンプト設計に注力。

ポイントは 「事業者情報」の自動差し込みです。ユーザーが一度自分の情報（会社名・事業内容・強み）を登録しておくと、プロンプトに自動で反映されます。

# utils/prompts.py
def build_prompt(company: dict, sender: SenderProfile | None) -> str:
    sender_section = ""
    if sender:
        sender_section = f"""
【送信者情報】
会社名: {sender.company_name}
事業内容: {sender.business_description}
強み: {sender.strengths}
"""
    return f"""
あなたは優秀な営業担当者です。
以下の企業情報と送信者情報を元に、初回営業メールを作成してください。

【宛先企業】
会社名: {company['name']}
業種: {company.get('industry', '不明')}
所在地: {company.get('address', '不明')}
{sender_section}
【出力形式】
件名：（件名のみ）
本文：（本文のみ、署名含む）
"""

事業者情報がある場合とない場合で分岐させることで、未登録ユーザーでも使える汎用文面を生成します。

---
④ Render.com のコールドスタート対策

Render.com の無料プランはアイドル時間が続くとコンテナがスリープします。初回アクセスで50〜60秒かかることがあり、ユーザー体験が最悪でした。

前回の書類ジェネレーターと同じ対策を入れました：

# main.py
@app.get("/health")
async def health_check():
    return {"status": "ok"}

フロントエンド側でアプリ起動時にヘルスチェックを叩いてウォームアップ：

// App.jsx
useEffect(() => {
  fetch(`${import.meta.env.VITE_API_URL}/health`).catch(() => {});
}, []);

完全な解決ではないですが、ユーザーが実際に検索ボタンを押す前にコンテナが起動済みになる確率がかなり上がります。

---
⑤ 事業者情報のローカル永続化

事業者情報（氏名・会社名・事業内容）はDBを持たずにブラウザの localStorage で保持しています。サーバーに個人情報を送らないことで、セキュリティ的にも運用コスト的にもシンプルに。

// hooks/useSenderProfile.js
const STORAGE_KEY = 'sender_profile';

export function useSenderProfile() {
  const [profile, setProfile] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  });

  const saveProfile = (data) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    setProfile(data);
  };

  return { profile, saveProfile };
}

検索履歴・メール生成履歴も同様の設計です。「DB不要でどこまで作れるか」を意識したアーキテクチャになっています。

---
セキュリティ対策

前回の書類ジェネレーターと同様、営業ツールとはいえ一応入れてあります：

┌─────────────────────────────┬───────────────────────────────────────┐
│            対策             │                 実装                  │
├─────────────────────────────┼───────────────────────────────────────┤
│ レート制限                  │ slowapi（10req/分）                   │
├─────────────────────────────┼───────────────────────────────────────┤
│ 入力バリデーション          │ Pydantic v2 で全パラメータ型検証      │
├─────────────────────────────┼───────────────────────────────────────┤
│ CORS厳格化                  │ 許可オリジンを明示（正規表現対応）    │
├─────────────────────────────┼───────────────────────────────────────┤
│ プロンプトインジェクション  │ ユーザー入力をf-stringに直接埋め込ま  │
│ 対策                        │ ない                                  │
├─────────────────────────────┼───────────────────────────────────────┤
│ APIキー保護                 │ 環境変数管理、クライアントへの露出な  │
│                             │ し                                    │
└─────────────────────────────┴───────────────────────────────────────┘

プロンプトインジェクション対策は地味に重要で、企業名フィールドに 「以上を無視して...」 みたいな文字列が入っても暴走しないよう、ユーザー入力をそのままプロンプトに差し込む構造を避けています。

---
Claude Code の活用場面

このプロジェクトでも Claude Code がかなり活躍しました。

特に効果的だった使い方：

1. CORS問題のデバッグ
エラーログをそのまま投げると、「ミドルウェアの実行順序が逆です」と即答してくれました。FastAPIのスタック構造まで把握しているのが地味にすごい。

2. gBizINFO APIのレスポンス解析
APIの実レスポンスJSONを貼り付けて「このデータ構造に合うPydanticモデルを作って」と投げると、ネストしたフィールドも含めて一発で生成してくれました。

3. プロンプトのリファイン
「営業メールが硬すぎる」「業種によってトーンが変わらない」などのフィードバックをそのまま伝えると、プロンプトテンプレートを修正してくれます。人間がプロンプトを微調整するより断然早い。

4. READMEの構成設計
実装が終わったタイミングで「このプロジェクトのREADMEを作って」と投げると、技術スタック・アーキテクチャ図・デプロイ手順まで一式生成してくれました。

---
実際の使い方

1. 企業を検索する
業種（例：IT）、都道府県、従業員数などで絞り込み → 最大20件表示
2. 事業者情報を登録する（任意だが推奨）
自分の会社名・事業内容・強みを入れておくと、メールの自己紹介部分が自動パーソナライズ
3. 気になる企業のメールを生成する
企業カードの「メール生成」ボタンを押すだけ → 件名＋本文が即生成
4. 編集してコピー
ブラウザ上でそのまま編集 → 1クリックでコピー → メールに貼り付け

---
所感

前回の書類ジェネレーターに続いて、また「自分が実際に困ってること」を起点に作りました。

営業ツールなので「精度よりスピード」が重要。Claude Haiku でも十分使えるレベルのメールが出るし、1通あたり約 $0.001 なのでコスト的にも全く問題なし。

次は Chrome拡張版も考えています。LinkedInや企業HPを見ながらその場でメール生成できると、もっと実用的になりそう。

フリーランスや営業代行をやっている方はぜひ使ってみてください。

🔗 https://columbus-enterprise-search.vercel.app

---
本ツールで使用している gBizINFO は経済産業省が提供する法人情報プラットフォームです。

---
```
