---
id: "2026-06-11-claude-fable-5-vs-opus-48-コーディングタスクで本当に差が出るか試した-01"
title: "Claude Fable 5 vs Opus 4.8 — コーディングタスクで本当に差が出るか試した"
url: "https://zenn.dev/mukuil_blog/articles/6c76b8199c2fde"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Python", "zenn"]
date_published: "2026-06-11"
date_collected: "2026-06-12"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは！[株式会社ムクイル](https://www.mukuil.com/)のhatです。  
2026年6月9日、AnthropicがClaude Fable 5をリリースしました。これまでの最上位モデルだったOpus 4.8のさらに上に位置する「Mythosクラス」の初の一般公開モデルです。

気になるのは**価格がOpus 4.8のちょうど2倍**という点。

| モデル | 入力 | 出力 |
| --- | --- | --- |
| Claude Fable 5 | $10 / 1M tokens | $50 / 1M tokens |
| Claude Opus 4.8 | $5 / 1M tokens | $25 / 1M tokens |
| Claude Sonnet 4.6 | $3 / 1M tokens | $15 / 1M tokens |

「ベンチマークで最高水準と言われても、実際の開発で差が出るのか？」というのが正直な疑問でした。

今回は**FastAPI / Pythonのバックエンド開発タスク**に絞って、コード品質・正確さの観点で両モデルを比較します。

---

## 検証環境・条件

* 同一プロンプトを各モデルに投げ、出力を比較
* temperature: デフォルト（変更なし）
* 評価軸：動作するか／型ヒントの正確さ／エラーハンドリング／コードの読みやすさ

---

## タスク1：FastAPI エンドポイント設計

### プロンプト

```
以下の仕様でFastAPIのエンドポイントを実装してください。
 
- ユーザー登録API（POST /users）
- リクエストボディ：name（str）, email（str）, age（int, 0以上）
- バリデーションエラーは422で返す
- 正常時は作成したユーザー情報をJSONで返す
- パスワードは不要
```

### Opus 4.8 の出力

```
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
 
app = FastAPI()
 
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int = Field(..., ge=0)
 
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
 
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    # 実際はDBに保存する処理が入る
    return UserResponse(id=1, **user.model_dump())
```

### Fable 5 の出力

```
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import uuid
 
app = FastAPI()
 
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="ユーザー名")
    email: EmailStr = Field(..., description="メールアドレス")
    age: int = Field(..., ge=0, le=150, description="年齢")
 
    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("名前は空白のみにできません")
        return v.strip()
 
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    age: int
 
    model_config = {"from_attributes": True}
 
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate) -> UserResponse:
    # 実際はDBに保存する処理が入る
    created_user = UserResponse(
        id=str(uuid.uuid4()),
        **user.model_dump()
    )
    return created_user
```

### 比較メモ（★で評価）

| 評価軸 | Opus 4.8 | Fable 5 |
| --- | --- | --- |
| 動作するか | ★★★★★ | ★★★★★ |
| 型ヒントの正確さ | ★★★★☆ | ★★★★★ |
| バリデーションの網羅性 | ★★★☆☆ | ★★★★★ |
| コードの読みやすさ | ★★★★★ | ★★★★☆ |
| 実用度 | ★★★★☆ | ★★★★★ |

**所感：**  
Opus 4.8も十分実用的なコードを出した。Fable 5は`field_validator`による空白チェック、`le=150`による上限バリデーション、UUIDによるID生成など、**「普通の開発者が次の一手として書くであろうコード」** まで先回りして実装していた。指示していない部分の判断精度に差を感じた。

---

## タスク2：依存性注入（Dependency Injection）パターン

### プロンプト

```
FastAPIでDBセッションを依存性注入で管理するパターンを実装してください。
SQLAlchemyを使用し、リクエストごとにセッションを開閉する構成にしてください。
```

### Opus 4.8 の出力

```
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
 
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
# 使用例
from fastapi import FastAPI
app = FastAPI()
 
@app.get("/items")
def read_items(db: Session = Depends(get_db)):
    return db.query(...).all()
```

### Fable 5 の出力

```
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
 
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
 
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
 
class Base(DeclarativeBase):
    pass
 
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
 
DBSession = Annotated[AsyncSession, Depends(get_db)]
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
 
app = FastAPI(lifespan=lifespan)
 
# 使用例
@app.get("/items")
async def read_items(db: DBSession):
    # db はセッション確定済み・型ヒント付き
    ...
```

### 比較メモ

| 評価軸 | Opus 4.8 | Fable 5 |
| --- | --- | --- |
| 動作するか | ★★★★★ | ★★★★★ |
| 非同期対応 | ★★☆☆☆（同期） | ★★★★★（async完全対応） |
| エラーハンドリング | ★★★☆☆ | ★★★★★ |
| 現代的な書き方 | ★★★☆☆ | ★★★★★ |
| 実用度 | ★★★★☆ | ★★★★★ |

**所感：**  
Opus 4.8は正しく動くが、同期セッションで実装した。Fable 5はプロンプトに「async」の指定がないにも関わらず、**FastAPI本来の非同期スタイルに合わせた実装** を選択。`Annotated`による型エイリアス、`lifespan`によるDB初期化、rollbackの明示など、実運用に近い構成を出してきた。

---

## タスク3：既存コードのリファクタリング

### プロンプト

```
# 以下のコードをリファクタリングしてください
@app.get("/users/{user_id}")
def get_user(user_id: int, db = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user == None:
        raise HTTPException(status_code=404, detail="Not found")
    return user
```

### Opus 4.8 の出力

```
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return user
```

### Fable 5 の出力

```
@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    responses={404: {"description": "ユーザーが見つかりません"}},
)
async def get_user(user_id: Annotated[int, Path(gt=0)], db: DBSession) -> UserResponse:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {user_id} のユーザーが見つかりません",
        )
    return user
```

### 比較メモ

| 評価軸 | Opus 4.8 | Fable 5 |
| --- | --- | --- |
| `== None` → `is None` の修正 | ✅ | ✅ |
| 型ヒントの整備 | ✅ | ✅ |
| パスパラメータのバリデーション | ❌ | ✅（`gt=0`） |
| HTTPステータスコードの定数化 | ❌ | ✅ |
| エラーメッセージの具体化 | △ | ✅ |
| OpenAPIドキュメントの充実 | ❌ | ✅（`responses`） |

**所感：**  
Opus 4.8は「正しく直す」。Fable 5は「より良くする」。元コードへの忠実さを保ちながら、**APIドキュメントの自動生成まで見据えた修正** を加えてくるのはFable 5ならではだった。

---

## 総合評価

|  | Opus 4.8 | Fable 5 |
| --- | --- | --- |
| 基本的な動作正確さ | ◎ | ◎ |
| 型ヒント・バリデーション | ○ | ◎ |
| 非同期・モダンな書き方 | △〜○ | ◎ |
| 指示外の先回り精度 | ○ | ◎ |
| コードレビュー視点 | ○ | ◎ |

---

## 結論：Fable 5に乗り換えるべきか？

**乗り換えを強くおすすめするケース**

* 本番環境に近いコードを出力させたい
* レビューコストを下げたい
* 複雑な設計判断を含むタスクが多い  
  **Opus 4.8で十分なケース**
* 簡単な実装・定型的なCRUDが中心
* API呼び出しコストを抑えたい
* とりあえず動くコードを素早く出したい  
  **個人的な結論：**  
  「指示していないことへの判断精度」がFable 5の最大の差別化ポイントでした。単純なコード生成よりも、**設計判断が含まれるタスク・リファクタリング・レビュー用途** で特に差が出ます。コスト2倍が許容できる用途には十分に見合います。日常の実装作業はOpus 4.8で、設計・リファクタリングはFable 5で使い分けるのが現時点のベストアンサーかもしれません。

---

## おわりに

今回はFastAPI / Pythonのバックエンドタスクに絞って比較しましたが、フロントエンドや長文生成タスクでは印象が変わる可能性があります。

価格・用途・チームのスキルレベルを考慮したうえで、**自分のユースケースで試してみる**のが一番の判断材料になります。6月22日まではProプランで追加費用なしで試せるので、この機会にぜひ。
