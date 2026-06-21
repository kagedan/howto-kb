---
id: "2026-06-19-1トピック複数sns配信saasを個人開発platformadapterで抽象化した話-01"
title: "1トピック→複数SNS配信SaaSを個人開発：PlatformAdapterで抽象化した話"
url: "https://zenn.dev/nichepilot_dev/articles/d9c725e8e45f20"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "zenn"]
date_published: "2026-06-19"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

副業クリエイター向けに、**1トピック入力 → 4プラットフォームに最適化されたコンテンツが自動配信される** SaaS を個人開発しました。

* WordPress 6,000字 SEO 記事 + Threads 500字 + X 117字 + Instagram 2,200字キャプション、全部同時生成・同時投稿
* `Publisher` ABC + プラットフォーム別 Adapter で異種プラットフォームを統一抽象化
* OAuth 2.0 `state` を HMAC で自己完結 (Redis 不要)
* `asyncio.gather(return_exceptions=True)` で部分失敗を吸収
* Fernet 暗号化で OAuth トークン群を BYTEA 保存
* 既存 `wp_sites` を破壊せず新 `connected_platforms` テーブル追加で後方互換

この記事では、**4プラットフォーム配信を1つのアーキテクチャに統合する設計判断** と、その実装の核を書きます。

> **現在の稼働状況 (2026-06)**: **WordPress / Threads は顧客が自分で連携して本番で自動投稿が動いています。** Instagram は投稿 Adapter は実装・稼働済みですが、新規顧客の自己連携は **Meta のアプリ審査通過後に順次開放**（審査中はテスター招待で連携可）。**X は Adapter 実装済みだが本番は「近日対応」**（無料APIで refresh\_token が使えず、有料API tier 待ち）。本記事の「4プラットフォーム抽象化」は X/Instagram Adapter を含む設計全体の話で、今すぐ顧客が自助で同時配信できるのは WordPress + Threads です。

---

## 作ったもの

* **サービス名**: NichePilot ([niche-pilot.com](https://niche-pilot.com))
* **コンセプト**: 副業クリエイター向け マルチプラットフォーム配信 SaaS
* **入力**: 1トピック + 投稿先プラットフォーム選択 (1〜4個)
* **出力**: 各プラットフォーム最適化済みコンテンツが自動配信
* **状態**: β招待50枠開放中

技術スタック:

* FastAPI + PostgreSQL 16 (RLS) + Celery + Redis (Upstash)
* Anthropic Claude Sonnet 4.6 (BYOK + prompt cache)
* OAuth 2.0 PKCE (X) + Meta Graph API (Threads/Instagram)
* Fly.io (Tokyo) + Neon (Postgres) + Cloudflare (DNS + Email Worker)
* Fernet 暗号化 (app-level、Fly secret 管理)

---

## 課題: 4プラットフォーム横断は「文字数・認証方式・規約」が全部違う

副業クリエイター向けの SaaS なので、最初は WordPress 単独で動いていました。  
途中で「SNS にも同時配信したい」要件が立ち、複数プラットフォーム対応に拡張。

ただし4プラットフォームは、共通項がほぼありません:

| 軸 | WordPress | Threads | X | Instagram |
| --- | --- | --- | --- | --- |
| 認証 | Application Password (Basic Auth) | OAuth 2.0 + long-lived token (60日) | OAuth 2.0 PKCE + refresh\_token | OAuth 2.0 + Business Account 必須 |
| 文字数 | 無制限 (実質6,000字推奨) | 500字 | 280字 (URL=23字) | 2,200字 + ハッシュタグ30個 |
| 投稿フロー | 1リクエスト | 2段階 (container作成→publish) | 1リクエスト | 2段階 (media→publish) |
| 画像 | 任意 | 任意 (Phase 1 = text-only) | 任意 (Phase 1 = text-only) | **必須** |
| アダルト規約 | 自由 | OK | OK | 禁止 |
| トークン更新 | 不要 | `th_refresh_token` | OAuth 2.0 標準 | `fb_exchange_token` |

**これを1つの共通インターフェースで抽象化する** のがこのプロジェクトの肝でした。

---

## 設計: `Publisher` ABC + プラットフォーム別 Adapter

```
# worker/publishers/base.py (抜粋)
class PlatformType(str, Enum):
    WORDPRESS = "wordpress"
    THREADS = "threads"
    X = "x"
    INSTAGRAM = "instagram"

@dataclass
class PostContent:
    """プラットフォーム横断の投稿コンテンツ表現。"""
    title: str
    body: str
    excerpt: str = ""
    image_urls: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    source_url: Optional[str] = None  # SNS が WP記事URLを参照する用

@dataclass
class PublishResult:
    post_id: str
    post_url: str
    raw_response: dict

class Publisher(ABC):
    platform_type: PlatformType = None

    @abstractmethod
    def verify_credentials(self, site_url: str, credentials: dict) -> None: ...

    @abstractmethod
    def publish(self, *, site_url, credentials, title, content, ...) -> PublishResult:
        """[Legacy] WordPress用の細かい引数ベース投稿。"""

    def publish_content(self, *, credentials: dict, content: PostContent, site_url: str = "") -> PublishResult:
        """[New] PostContent を受け取る汎用インターフェース。デフォルトは publish() に委譲。"""
        return self.publish(site_url=site_url, credentials=credentials,
                            title=content.title, content=content.body, ...)
```

ポイント:

* **`publish()` (旧シグネチャ) を残す** ことで既存 WordPress 実装の後方互換を保証
* **`publish_content()` (新シグネチャ) を default 実装付きで追加** することで、新 SNS adapter は dataclass ベースの綺麗な API を使える
* **`platform_type` をサブクラス属性として強制** し、registry で動的解決

これで「既存ロジックを破壊せず、新プラットフォーム追加が容易」という両立を実現。

---

## SNS Adapter 3つの実装

```
class ThreadsPublisher(Publisher):
    platform_type = PlatformType.THREADS
    API_BASE = "https://graph.threads.net/v1.0"
    MAX_TEXT_LENGTH = 500

    def publish_content(self, *, credentials, content, site_url=""):
        # Step 1: media container 作成
        r = requests.post(
            f"{self.API_BASE}/{credentials['account_id']}/threads",
            data={
                "media_type": "TEXT",
                "text": self._format_text(content),
                "access_token": credentials["access_token"],
            },
        )
        creation_id = r.json()["id"]
        # Step 2: publish
        r2 = requests.post(
            f"{self.API_BASE}/{credentials['account_id']}/threads_publish",
            data={"creation_id": creation_id, "access_token": credentials["access_token"]},
        )
        return PublishResult(post_id=str(r2.json()["id"]), ...)

    def refresh_token(self, credentials):
        # Long-lived token (60日) 自動延長
        r = requests.get(
            f"{self.API_BASE}/refresh_access_token",
            params={"grant_type": "th_refresh_token", "access_token": credentials["access_token"]},
        )
        ...
```

### X (X API v2 + OAuth 2.0 PKCE)

```
class XPublisher(Publisher):
    platform_type = PlatformType.X
    MAX_TEXT_LENGTH = 280  # URL は t.co 短縮で 23字としてカウント

    def publish_content(self, *, credentials, content, site_url=""):
        r = requests.post(
            "https://api.twitter.com/2/tweets",
            headers={"Authorization": f"Bearer {credentials['access_token']}"},
            json={"text": self._format_text(content)},
        )
        return PublishResult(post_id=str(r.json()["data"]["id"]), ...)

    def _format_text(self, content):
        # URL を 23字としてカウント、本文は 117字以内に整形
        ...

    def refresh_token(self, credentials):
        # OAuth 2.0 PKCE refresh_token フロー
        basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        r = requests.post(
            "https://api.twitter.com/2/oauth2/token",
            headers={"Authorization": f"Basic {basic}"},
            data={"refresh_token": credentials["refresh_token"], "grant_type": "refresh_token", ...},
        )
        ...
```

```
class InstagramPublisher(Publisher):
    platform_type = PlatformType.INSTAGRAM
    MAX_CAPTION_LENGTH = 2200

    def publish_content(self, *, credentials, content, site_url=""):
        if not content.image_urls:
            raise RuntimeError("Instagram requires at least one image")
        # 2段階投稿
        r = requests.post(
            f"{self.API_BASE}/{credentials['account_id']}/media",
            data={
                "image_url": content.image_urls[0],
                "caption": self._format_caption(content),
                "access_token": credentials["access_token"],
            },
        )
        creation_id = r.json()["id"]
        r2 = requests.post(
            f"{self.API_BASE}/{credentials['account_id']}/media_publish",
            data={"creation_id": creation_id, "access_token": ...},
        )
        return PublishResult(...)
```

---

## OAuth 2.0 フロー — `state` を HMAC で署名 (Redis 不要設計)

複数プラットフォームの OAuth コールバックを 1エンドポイントで受ける設計:

```
# api/utils/oauth_state.py
def make_state(*, tenant_id: str, platform: str, extra: dict | None = None) -> str:
    payload = {
        "tenant_id": tenant_id,
        "platform": platform,
        "ts": int(time.time()),
        "nonce": secrets.token_urlsafe(8),
    }
    if extra:
        payload.update(extra)
    raw = json.dumps(payload, sort_keys=True).encode()
    sig = hmac.new(settings.fernet_key.encode(), raw, hashlib.sha256).digest()
    return f"{_b64url_encode(raw)}.{_b64url_encode(sig)}"

def verify_state(state: str) -> dict:
    payload_b64, sig_b64 = state.split(".", 1)
    raw = _b64url_decode(payload_b64)
    sig = _b64url_decode(sig_b64)
    expected_sig = hmac.new(settings.fernet_key.encode(), raw, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("invalid_state_signature")
    payload = json.loads(raw)
    if time.time() - payload["ts"] > 600:  # 10分 TTL
        raise ValueError("state_expired")
    return payload
```

ポイント:

* **HMAC-SHA256 + 10分 TTL** で改ざん検知 + 期限切れ判定
* **Redis 不要** (state にすべて含めて自己完結)
* **X の PKCE code\_verifier は state の `extra` に埋め込み** (HMAC で守られるので tamper 不可)

```
# X だけ PKCE が必要、 verifier を state に埋め込む
state = make_state(
    tenant_id=str(tenant_id),
    platform="x",
    extra={"cv": code_verifier},  # callback で取り出す
)
```

---

## 並列投稿のオーケストレーション

```
# worker/topic_orchestrator.py
async def dispatch_sns_after_wp(
    *, tenant_id, topic, wp_post_url, wp_title,
    sns_platforms, sns_contents, image_url=None,
) -> list[PlatformOutcome]:
    """WordPress 投稿後、SNS のみ並列投稿。"""
    tasks = []
    ordered = []

    if "threads" in sns_platforms and sns_contents.get("threads"):
        content = PostContent(
            title=wp_title, body=sns_contents["threads"],
            source_url=wp_post_url,  # WP URLを SNS で参照
        )
        tasks.append(_publish_sns(tenant_id, "threads", content))
        ordered.append("threads")

    # 同様に X / Instagram

    if not tasks:
        return []

    results = await asyncio.gather(*tasks, return_exceptions=True)

    outcomes = []
    for platform, res in zip(ordered, results):
        if isinstance(res, Exception):
            outcomes.append(PlatformOutcome(platform, False, error=str(res)[:300]))
        else:
            outcomes.append(res)
    return outcomes
```

`asyncio.gather(return_exceptions=True)` で **部分失敗** を吸収するのがポイント:

* 3プラットフォーム選んで1個レート制限ヒット → 他2個は成功
* 結果は `Job.platform_results` JSON に集約
* `Job.status` は `done` / `partial_failure` / `failed` の3値

---

## プロンプト最適化 — プラットフォームごとに「別人格」で書く

Claude のプロンプトをプラットフォーム別に分離:

```
# worker/prompts.py
THREADS_SYSTEM_PROMPT = """あなたは Threads でフォロワーを増やす副業クリエイター運用者です。
【絶対ルール】
- 500字以内、単体で読み切れる中身 (リンク誘導なし)
- 1行目に「フック」(質問・問題提起・意外な数字)
- 絵文字は1-3個
- 「いかがでしたでしょうか」「ぜひ参考に」禁止
"""

X_SYSTEM_PROMPT = """X (旧Twitter) でフォロワーを増やす運用者として、
117字以内、単体で完結する密度の高い一文を1本作る。
"""

INSTAGRAM_SYSTEM_PROMPT = """Instagram キャプション 2000字以内 + ハッシュタグ10-20個。
本文中リンク不可。キャプション単体で完結させる。
"""
```

同じトピックでも、各プラットフォーム用に **別 Claude 呼び出し** で個別生成。  
これにより、プラットフォーム文化に合わせた自然な投稿が生成されます (単純切り詰めではない)。

---

## DB スキーマ — 既存テーブルを破壊せず後方互換

WordPress は `wp_sites` (Application Password 専用カラム) のまま、SNS用は別テーブル:

```
CREATE TABLE connected_platforms (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    platform TEXT CHECK (platform IN ('wordpress','threads','x','instagram')),
    encrypted_credentials BYTEA,  -- Fernet 暗号化 JSON
    account_id TEXT,
    username TEXT,
    token_expires_at TIMESTAMPTZ,
    is_active BOOLEAN,
    consecutive_failures INT DEFAULT 0,
    last_post_at TIMESTAMPTZ,
    last_error_message TEXT,
    UNIQUE(tenant_id, platform)
);

ALTER TABLE connected_platforms ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_connected_platforms ON connected_platforms
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

`Job` テーブル拡張も後方互換重視:

```
ALTER TABLE jobs
    ALTER COLUMN wp_site_id DROP NOT NULL,  -- SNSのみ投稿対応
    ADD COLUMN target_platforms TEXT,        -- JSON array
    ADD COLUMN image_url VARCHAR,
    ADD COLUMN platform_results TEXT;        -- 結果 JSON 配列
```

`target_platforms` が空 or `["wordpress"]` のみなら **旧フロー (WP単独)** を維持。  
SNS を含むなら新フロー (`dispatch_sns_after_wp`) を呼ぶ。

---

## 認証情報の暗号化 — Fernet (app-level)

```
# api/utils/secrets.py
from cryptography.fernet import Fernet
_fernet = Fernet(settings.fernet_key.encode())

def encrypt(plaintext: str) -> bytes:
    return _fernet.encrypt(plaintext.encode())

def decrypt(ciphertext: bytes) -> str:
    return _fernet.decrypt(ciphertext).decode()
```

OAuth トークン群を JSON 文字列化して暗号化 → DB に BYTEA で保存:

```
creds_dict = {"access_token": "...", "refresh_token": "...", "account_id": "..."}
encrypted = encrypt(json.dumps(creds_dict))
```

* **Fly.io secret** に `FERNET_KEY` を配置
* **DB ダンプ流出時も平文トークン漏洩しない**
* AWS KMS は外部依存増えるので採用せず、Fernet で十分と判断

---

## プラン構成 — 「プラットフォーム数」で価格を決める

```
Solo (¥1,980): 1プラットフォーム / 60投稿
Duo (¥2,980): 2プラットフォーム / 120投稿
Trio (¥4,980): 3プラットフォーム / 180投稿
All Access (¥7,980): 対応プラットフォーム全部 / 無制限 (X追加時も追加料金なし)
```

API側で制限:

```
PLAN_PLATFORM_LIMITS = {"solo": 1, "duo": 2, "trio": 3, "all": None}

if platform_limit is not None and len(payload.platforms) > platform_limit:
    raise HTTPException(402, "プラン上限超過")
```

月次クォータは **トピック単位** でカウント (選択プラットフォーム数に依らず1ジョブ=1カウント)。

---

## UX — 連携状態の見える化

App ダッシュボードのサイドバーに「連携SNS」カード3枚:

* **状態バッジ**: 未連携 / ✓連携済 / 期限7日以内 / 期限切れ / 要確認 (連続3回失敗)
* **テスト投稿 / トークン手動更新 / 連携解除** ボタン
* **OAuth 戻り検知** で歓迎メッセージ + 自動 refresh + URL クリーンアップ

副業クリエイターは技術に詳しくない層が多いので、OAuth エラーが出ても優しい日本語で誘導する設計に。

---

## まとめ

* **抽象化レイヤー (PlatformAdapter / PostContent / PublishResult)** で異種プラットフォームを統一
* **OAuth state を HMAC 自己完結** で Redis 不要設計
* **`asyncio.gather` + `return_exceptions`** で部分失敗を吸収
* **既存 wp\_sites を破壊せず新 connected\_platforms 追加** で後方互換
* **Job 拡張で target\_platforms / image\_url / platform\_results を JSON 保存** (スキーマ複雑化を最小限に)
* **プラットフォーム別プロンプト** で「文字数だけ違う」ではなく「文化が違う」最適化を実現

副業クリエイターが「ブログ + SNS + Instagram」を回す技術コストを、月¥1,980 で買い戻せる SaaS にしました。

技術的な質問・突っ込み、大歓迎です。

---

**🔗 サービス**: [niche-pilot.com](https://niche-pilot.com)  
**📧 質問**: support@niche-pilot.com (24時間以内に運営者本人が返信)  
**💻 GitHub**: 公開予定 (ローンチ後数ヶ月内)

#NichePilot #個人開発 #SaaS #FastAPI #Claude #OAuth
