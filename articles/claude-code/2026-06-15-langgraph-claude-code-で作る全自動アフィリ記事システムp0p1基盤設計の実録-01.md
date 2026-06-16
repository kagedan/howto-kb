---
id: "2026-06-15-langgraph-claude-code-で作る全自動アフィリ記事システムp0p1基盤設計の実録-01"
title: "LangGraph × Claude Code で作る全自動アフィリ記事システム――P0/P1基盤設計の実録"
url: "https://qiita.com/sorabcjanne1/items/11f9d968919920073837"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "OpenAI", "Python", "qiita"]
date_published: "2026-06-15"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

# LangGraph × Claude Code で作る全自動アフィリ記事システム――P0/P1基盤設計の実録

## はじめに

「実装指示書を渡せば、AIがフェーズごとに止まりながら実装してくれる」という開発スタイルを試しました。題材は **5体のワーカーエージェント（リサーチ→生成→校正→配信→計測）＋オーケストレーター** を LangGraph で直列に回す全自動アフィリ記事システムです。

外部APIは**全てモック**、実デプロイ・実課金はなし。P0（基盤）→P1（ツール層）→P2（単線パイプ）→P3（ガードレール）→P4（計測・学習）の5フェーズに分割し、**各フェーズ完了後に必ず停止・報告**するよう指示しました。

この記事では P0・P1 で実際にやったこと、ハマったポイント、設計上の学びを記録します。

---

## やったこと

### P0：リポジトリ基盤

まず `docker-compose.dev.yml`（pgvector + Redis）・`pyproject.toml`・`alembic` の初期マイグレーションを用意しました。

**設計の要点：**

- 設定は `pydantic-settings` で `.env` から読み込み。秘密は `SecretStr` にする
- alembic の接続 URL は `env.py` から動的注入し、**ファイルに秘密を残さない**
- Celery のブローカー/バックエンドは Redis。concurrency=2 で 4GB VPS に合わせてメモリを抑制

```python
# app/config.py（抜粋）
from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    anthropic_api_key: SecretStr
    database_url: SecretStr
    redis_url: str = "redis://localhost:6379/0"
    embedding_dim: int = 1024  # ハードコードしない。Voyageモデルに合わせる

    class Config:
        env_file = ".env"
```

```python
# alembic/env.py（接続URL動的注入）
from app.config import get_settings

def get_url() -> str:
    return get_settings().database_url.get_secret_value()
```

P0 の受け入れ基準は「`make lint` 通過・`pytest` 7件グリーン・compose 構文 OK」。Docker デーモン未起動のため実起動は P2 前に持ち越しましたが、それ以外は全て達成しました。

---

### P1：ツール層（抽象 IF ＋ モック実装）

Claude / WordPress / ASP / 楽天 / Amazon / GA4 / GSC / SNS / Embedding の 9 クライアントを実装しました。

**設計方針：生の dict を上位に漏らさない**

全クライアントは ABC で抽象化し、戻り値は Pydantic モデルに統一しています。

```python
# tools/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel

class ArticleResult(BaseModel):
    post_id: int
    url: str
    status: str  # draft / future / publish

class WordPressClientBase(ABC):
    @abstractmethod
    async def create_post(
        self,
        *,
        title: str,
        content: str,
        status: str = "draft",
        idempotency_key: str,
    ) -> ArticleResult: ...
```

**Claude クライアント：モデルルーティング＋コスト計上**

Haiku / Sonnet / Opus を用途別にルーティングし、トークン消費とコストをこの層で吸収します。

```python
# tools/claude.py（抜粋）
MODEL_COSTS: dict[str, tuple[float, float]] = {
    "claude-haiku-3":   (0.00025, 0.00125),   # (input/1k, output/1k) USD
    "claude-sonnet-4":  (0.003,   0.015),
    "claude-opus-4":    (0.015,   0.075),
}

async def complete(self, prompt: str, model: str, max_tokens: int) -> ClaudeResult:
    # 上限チェック → API呼び出し → コスト計上
    ...
```

**レートリミット IF の差し込み口**

ASP・SNS などの外部系には、実装は P3 で行うとしても**インターフェースだけは P1 で確定**させます。

```python
# tools/rate_limit.py
from abc import ABC, abstractmethod

class RateLimiterBase(ABC):
    @abstractmethod
    async def acquire(self, key: str, tokens: float = 1.0) -> None:
        """トークンバケット方式。実装はRedis、テストはインメモリ。"""
        ...

class NoopRateLimiter(RateLimiterBase):
    async def acquire(self, key: str, tokens: float = 1.0) -> None:
        return  # テスト・開発用
```

**WordPress：idempotency key と投稿 status**

冪等性キーの受け口は最初から用意しておかないと後で差し込めません。Basic 認証（アプリパスワード）も同様です。

```python
# tools/wordpress.py（モック実装抜粋）
class MockWordPressClient(WordPressClientBase):
    async def create_post(self, *, title, content, status="draft", idempotency_key):
        # 同一キーなら既存IDを返す（冪等）
        if idempotency_key in self._store:
            return self._store[idempotency_key]
        result = ArticleResult(post_id=len(self._store) + 1, url="http://mock/...", status=status)
        self._store[idempotency_key] = result
        return result
```

**テストはネットワーク遮断下で**

httpx の respx を使い、実ネットワークに触れずに正常系・異常系を検証します。

```python
# tests/tools/test_wordpress.py
import respx, httpx

@respx.mock
async def test_create_post_timeout():
    respx.post("https://example.com/wp-json/wp/v2/posts").mock(
        side_effect=httpx.TimeoutException("timeout")
    )
    with pytest.raises(ToolTimeoutError):
        await client.create_post(title="test", content="...", idempotency_key="key-1")
```

P1 完了時点で **33 件のテストが全てモックでグリーン**、ruff・mypy strict も通過しました。

---

## ハマったポイント

### 1. Embedding の次元をハードコードしかけた

開発初期に `embedding_dim = 1536`（OpenAI 系の値）をベタ書きしていました。しかし Voyage AI の推奨モデルは 1024 次元であり、**pgvector の列定義と不一致になると後で ALTER TABLE が必要になる**という指摘を受けて修正。設定値（環境変数）として外出しし、モデル変更時に列定義と同時に変わる構造にしました。

### 2. mypy strict で Celery の型エラー

`@app.task` デコレータが mypy strict 下で `[misc]` エラーになります。`# type: ignore[misc]` でシルエンシングしようとしたところ、エラーコードが微妙に違い `# type: ignore[no-untyped-def]` が正解でした。ruff の `UP035`（StrEnum への移行推奨）も初回実行で複数出ました。

### 3. レートリミット IF を「後回し」にしそうになった

「実装は P3 でいいや」と思っていたところ、**IF が確定していないと各クライアントのコンストラクタ引数が決まらず、P2 でグラフを組むときに型が合わなくなる**という問題が予見されました。IF だけ P1 で固めておくことで、後段の型の一貫性を保てています。

---

## 学び

1. **フェーズ分割＋停止報告が効く**：1フェーズで変更範囲が絞れるため、レビューが楽。AI が暴走して全部書いてしまうのを防げます。
2. **生 dict を上位に漏らさない**：Pydantic モデルで境界を引くと、エージェント間のデータ受け渡しが型安全になり、後段の LangGraph `RunState` 設計が楽になります。
3. **IF は実装より先に確定させる**：レートリミットや冪等性キーのように「後で足す」が難しいものほど、インターフェースを最初に決めておくコストが低く、後で変えるコストが高い。
4. **秘密の置き場所を決める**：alembic の接続 URL、Celery のブローカー URL など、設定が複数箇所にまたがりやすい。`Settings` を単一の真実源にして動的注入するパターンが安定します。

> **個人の感想**：「実装指示書を渡して段階的に止める」スタイルは、AI に自由にコードを書かせるより設計の意図が通りやすく、レビュー負荷も下がりました。特にセキュリティ・型安全・冪等性まわりのレビューポイントを指示書に明示しておくと、その通りに実装されてくる点が面白いと感じました（個人の感想）。

---

## 次のステップ

P2 では LangGraph グラフ・`RunState`・checkpointer と 5 体のエージェントを実装します。P2 着手前に `make up && make migrate` の実起動確認が必須（DB/checkpointer が要るため）。P3 でガードレール（法令ゲート・コスト上限・キルスイッチ）を追加し、P4 で計測・学習ループを閉じる予定です。
