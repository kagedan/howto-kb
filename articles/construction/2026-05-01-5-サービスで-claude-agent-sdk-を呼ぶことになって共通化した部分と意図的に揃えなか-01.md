---
id: "2026-05-01-5-サービスで-claude-agent-sdk-を呼ぶことになって共通化した部分と意図的に揃えなか-01"
title: "5 サービスで Claude Agent SDK を呼ぶことになって、共通化した部分と意図的に揃えなかった部分"
url: "https://zenn.dev/zoetaka38/articles/409d4c89fc78a5"
source: "zenn"
category: "construction"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

うちでは Claude Agent SDK を 5 つのサービス(Green / Purple / Red / Blue / Yellow)から叩いている。最初は各サービスに素直に `infrastructure/external_apis/claude_agent_sdk_client.py` を生やしていて、4 サービス目を書いているあたりで「全部別々にメンテしたら破綻する」と気付いて骨格を揃えに行った。

ただ全部を共通ライブラリに切り出すのも違う。Red の 3-retry test feedback ループは Red にしかいらないし、Blue の Playwright MCP サブプロセス起動は他のサービスにとって邪魔になる。「揃えるところ」と「揃えないところ」を、実際の 5 ファイルを読み比べた結論として書き残しておく。

## 揃えた骨格

5 サービスのクライアントは全部同じ形をしている。クラス名も `ClaudeAgentSDKClient`、コンストラクタの中で `_create_mcp_server()` を呼んで MCP サーバを 1 つ抱える、メソッドを呼ぶたびに `async with ClaudeSDKClient(options=options) as client:` で都度 SDK セッションを開く、という形。

```
# どのサービスでも全く同じ起動シーケンス
options = ClaudeAgentOptions(model=self._model, max_turns=10, ...)
async with ClaudeSDKClient(options=options) as client:
    await client.query(prompt)

    response_text = ""
    input_tokens = 0
    output_tokens = 0

    async for message in client.receive_response():
        if hasattr(message, "text"):
            response_text += message.text
        if hasattr(message, "usage"):
            input_tokens += ...
            output_tokens += ...
```

最初バラバラだった頃に「Blue では `AssistantMessage.content[0].text` で取れていたのに、Red では `message.text`、Green では両方とも来ず空文字を返していた」というのを 3 回くらい踏んだ。Agent SDK はバージョンや戻り値の経路で `message.text` と `content` ブロックの両方が来るので、抽出ロジックは 1 か所でガードする方針に倒した。

## 揃えたもの 1: 戻り値のスキーマ `{ "model", "usage": {...} }`

明示的な `ClaudeClientResponse` のような共通の型は切っていない。代わりに **戻り値の dict のキー名を全サービスで同じにする** という地味な約束で揃えた。`usage_tracking_service.py` がこの形を前提にしているからだ。

```
# yellow-codens/backend/src/use_cases/billing/usage_tracking_service.py
async def track_claude_response(
    self,
    organization_id: UUID,
    claude_response: Dict[str, Any],
    operation_type: str,
    ...
) -> Dict[str, Any]:
    """ClaudeAgentSDKClient の戻り値を直接受け取って処理"""
    usage = claude_response.get("usage", {})
    model = claude_response.get("model", "claude-opus-4-5-20251101")

    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
```

この `claude_response` は SDK クライアントの戻り値そのものを受け取る。だから 5 サービスのどのメソッドも、最低限 `model` と `usage` の 2 キーを返すようにしてある。BCP(billing-control-plane) で credit に換算するレイヤが、SDK クライアントの戻り値を **何のラッパも噛まさず** 直接読めるようになっているのが大事だった。途中で `pydantic.BaseModel` に詰め替えたいモードもあったが、AI 呼び出しを増やすたびに schema のメンテが入るのが嫌で、dict のキー名でゆるく揃える側にした。

## 揃えたもの 2: 失敗を例外にせず dict で返す

全サービス共通で、`try/except` で全体を包んで、例外時は同じスキーマの dict を返す。

```
# red-codens の analyze_error 抜粋
except Exception as e:
    logger.error(f"Failed to analyze error: {e}")
    return {
        "analysis": f"Error during analysis: {str(e)}",
        "model": self._model,
        "usage": {},
    }
```

Celery タスクから呼ばれるので、SDK 側で例外が立つと task\_id ごとリトライキューに乗ってしまう。ところが Anthropic のレート制限や一時的な 5xx は **同期 retry してもしばらく直らない** ので、ユースケース層で `confidence_score=0.0` を見て「失敗を結果として扱う」方針にした。`raise` するのは入力検証エラーくらい。

`usage` も空 dict `{}` を返す。BCP 側は `input_tokens <= 0 and output_tokens <= 0` を見て自動的にトラッキング対象から外すので、失敗呼び出しに対して credit が引かれない。これも 5 サービスで同じ約束。

## 揃えたもの 3: rate limit の入口を全メソッドの先頭に置く

5 サービスとも `_acquire_rate_limit(operation_name)` を全メソッドの先頭で呼んでいる。今は `# TEMPORARILY DISABLED` でただ True を返すスタブだが、入口が揃っているので戻すときは 1 か所触ればいい。

```
async def _acquire_rate_limit(self, operation_name: str) -> bool:
    # TEMPORARILY DISABLED: Rate limiting bypassed for testing
    # acquired = await self._rate_limiter.acquire(tokens=1, timeout=300.0)
    # if not acquired:
    #     ...
    logger.debug(f"{operation_name}: Rate limiter bypassed (disabled for testing)")
    return True
```

一度これを全部消そうとしたが、運用が始まると 429 が固まる瞬間があり、戻すとき「呼び出し点が散らばっていてどこに入れる？」で苦労したくないので、スタブのまま残してある。

GitHub からファイルを読む MCP ツールは、5 サービス共通で `read_file` / `search_code` / `get_repository_structure` / `get_directory_contents` の 4 本に揃えてある。

```
# どのサービスも同じツール名・同じ allowed_tools
options = ClaudeAgentOptions(
    model=self._model,
    max_turns=10,
    mcp_servers={"github": self._mcp_server},
    allowed_tools=[
        "mcp__github__read_file",
        "mcp__github__search_code",
        "mcp__github__get_repository_structure",
        "mcp__github__get_directory_contents",
    ],
)
```

`allowed_tools` を **明示的にホワイトリスト** で渡すと固く決めた。Agent SDK はデフォルトだと `Read` / `Write` / `Edit` / `Glob` / `Grep` / `Bash` が使えるが、有効だとサーバ側の `/app/` 配下を agent が読みに行く事故が起きる。一度ログでそれを観測してから、Blue の test 生成パスでは `disallowed_tools` でも塞ぐ二重防御に落ち着いた。

```
# blue-codens/backend/src/infrastructure/external_apis/claude_agent_sdk_client.py
options = ClaudeAgentOptions(
    model=self._model,
    max_turns=40,
    system_prompt=system_prompt,
    cwd=str(self._workspace_path),
    mcp_servers={"local": self._mcp_server},
    allowed_tools=[
        "mcp__local__read_file",
        "mcp__local__list_directory",
        "mcp__local__get_file_structure",
        "mcp__local__get_multiple_files",
    ],
    # Block all built-in file access tools to prevent reading from /app/
    disallowed_tools=[
        "Read", "Write", "Edit", "Glob", "Grep", "Bash",
        "MultiEdit", "NotebookEdit",
    ],
)
```

ちなみに `permission_mode` は **使っていない**。書き込み系の built-in tools を全部 disallow している以上、permission\_mode を立てる意味がほぼなかった。「ツール側で塞ぐ」と「permission で塞ぐ」は重複していて、後者は要らないと判断した。

## 揃えたもの 5: model alias の解決を 1 か所に集約

4 サービス(Red / Green / Blue / Yellow の一部) は `resolve_model()` という共通ユーティリティで `"opus"` / `"sonnet"` / `"haiku"` の alias を解決している。

```
# {project}/backend/src/utils/model_resolver.py
MODEL_ALIASES: dict[str, str] = {
    "opus": "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5-20251001",
}

def resolve_model(model: str) -> str:
    """Resolve a model alias to its full model ID."""
    return MODEL_ALIASES.get(model, model)
```

クライアントでは `self._model = resolve_model(settings.CLAUDE_MODEL)` と呼ぶだけ。`settings.CLAUDE_MODEL=opus` を切り替えれば全サービスのモデルが一気に上がる。新モデルが出るたびに `MODEL_ALIASES` だけ更新すればいい。完全 ID を渡せば pass-through なので、A/B 比較は直書きで上書きできる。

ちなみに **per-org の model override は実装していない**。env で十分で、組織ごとに切り替えるニーズがまだ立っていない。

## 揃えなかったところ — サービスごとに本当に違う部分

ここからは差分の話。共通化を頑張りすぎて潰したくなかった部分。

### Red Codens — 3-retry test feedback ループ

Red は **検出したエラーに対して修正 PR を出す** のが仕事なので、初回の `generate_fix` で生成した patch をテストに通して、落ちたら結果を Claude にフィードバックして `improve_fix_with_test_feedback` を呼ぶ、というループを持っている。

```
# red-codens 系のクライアントだけが持つメソッド
async def improve_fix_with_test_feedback(
    self,
    error_analysis: str,
    code_context: Dict[str, str],
    previous_fix: str,
    test_output: str,
    language: str = "python",
    ai_instructions: Optional[str] = None,
    extra_env: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
```

ユースケース層では `max_retries=3` で回している。

```
# generate_fix_use_case.py 抜粋
for attempt in range(1, max_retries + 1):
    logger.info(f"Fix generation attempt {attempt}/{max_retries}")
    ...
    if attempt > 1:
        fix_result = await self._claude_client.improve_fix_with_test_feedback(...)
    ...
    if attempt < max_retries:
        # tests failed, will retry with feedback
        ...
```

これを共通基盤に上げるべきか悩んだが、結局上げなかった。Blue(QA 自動化) もテストは走らせるが、目的は **テストレポートとして人に見せる** ことで AI フィードバックループにしない。Green / Yellow はコードを書かない。3-retry を共通化するとインターフェースが Red の都合に引っ張られすぎる。

### Green Codens — Notion 書き戻しと Anthropic SDK 直叩きの並走

Green は PRD を Notion と双方向同期しているので、SDK 経由で生成した文章を Notion ページのプロパティに書き戻す責務がある。さらに Green の `claude_agent_sdk_client.py` には、Agent SDK ではなく **`anthropic.AsyncAnthropic` で直接叩く** メソッドが共存している。

```
# green-codens/backend/src/infrastructure/external_apis/claude_agent_sdk_client.py
from anthropic import AsyncAnthropic
from src.utils.claude_structured_output import call_claude_json_with_retry, call_claude_text

async def diagnose_plan_progress(self, context: Dict[str, Any]) -> Dict[str, Any]:
    ...
    anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY.get_secret_value())
    parsed, raw_text, usage, success = await call_claude_json_with_retry(
        client=anthropic_client,
        model=self._model,
        system_prompt=system_prompt,
        user_message=user_message,
        schema=PROPOSED_DIFF_V1_SCHEMA,
        max_tokens=4096,
        max_retries=2,
    )
```

なぜ Agent SDK で統一しないかと言うと、`proposed_diff_v1` のように **JSON Schema に厳密に従う構造化出力** が欲しい時、Agent SDK 経由だと tool 呼び出しのオーバーヘッドが乗る上に schema validate のリトライが書きづらい。Notion 書き戻しのために dict を確実に得たいユースケースは、`anthropic` SDK の structured output を直で叩く方が確実だった。**MCP ツールを呼ばない用途には Agent SDK は重すぎる** と判断して、Green は「探索系は Agent SDK、構造化 JSON は anthropic 直叩き」を併存させている。

`mask_secrets(response_text)` で response をマスクしてから返しているのも Green だけの差分。PRD は社外秘を含むことが多く、AI 出力に偶然 API キー風の文字列が混じった時に下流へ流れないようにしている。

### Blue Codens — Playwright MCP のサブプロセス起動と max\_turns

Blue だけ MCP サーバの構成が大きく違う。**ローカルにクローンしたワークスペース** を見る MCP と、**Playwright を実プロセスで起動した上に被せた MCP** の 2 つを刺す。

```
# blue-codens/backend/src/infrastructure/external_apis/exploratory_agent_client.py
async with async_playwright() as playwright:
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()

    playwright_mcp_server = self._create_playwright_mcp_server(
        playwright, browser, page
    )

    mcp_servers: dict[str, Any] = {"playwright": playwright_mcp_server}
    if self._local_mcp_server:
        mcp_servers["local"] = self._local_mcp_server

    options = ClaudeAgentOptions(
        model=self._model,
        max_turns=session.max_steps + 10,  # Extra turns for analysis
        system_prompt=system_prompt,
        mcp_servers=mcp_servers,
        allowed_tools=[
            "mcp__playwright__browser_navigate",
            "mcp__playwright__browser_snapshot",
            "mcp__playwright__browser_click",
            "mcp__playwright__browser_type",
            ...
        ],
        disallowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
    )
```

他のサービスは `max_turns` を 10〜15 で抑えているが、Blue の探索的 E2E 生成は **40** まで上げている。1 ページずつクリックして DOM snapshot を取りながら探索するので、ターン数を絞ると **探索が途中で打ち切られて使い物にならないテスト** が出てくる。用途別に max\_turns を変えるのは早めに諦めて分岐させた。

ResultMessage で `total_cost_usd` を logger に出しているのも Blue だけ。

```
elif isinstance(message, ResultMessage):
    ...
    total_cost = getattr(message, "total_cost_usd", 0) or 0
    stop_reason = getattr(message, "stop_reason", "unknown")
    logger.info(
        f"  [RESULT] cost=${total_cost:.4f}, stop={stop_reason}, "
        f"tokens={input_tokens}/{output_tokens}"
    )
```

探索 1 セッションで $1 を超えることもある(40 ターン × 数千トークン)ので、運用ログにドルが見えると後で調査が楽。他のサービスは入出力トークンしか見ていない。

### Yellow Codens — rules-first との合流

Yellow は activity ledger なので、AI への問い合わせは **「ルールベースで判定できなかったエッジケースだけ」** に絞っている。クライアント自体は他と同じ形だが、

```
# yellow-codens のクライアントには env も extra_env もなく、API key を直接渡す
options = ClaudeAgentOptions(
    model=self._model,
    max_tokens=self._max_tokens,
    api_key=settings.ANTHROPIC_API_KEY,
)
```

…という古い書き方が残っている。Red / Green / Blue は env 変数で渡す方式(後述)に移行済みだが、Yellow は AI が advisory にしか出てこないので優先度が低くて、まだ Agent SDK の旧シグネチャのままだ。「揃えなかった」というより「揃えるのが間に合っていない」差分。

## env 経由の API key 注入 — Red と Green が揃った

Red と Green の最近のコミットで、`api_key=` を直接渡す代わりに `env=` 経由で注入する書き方に揃えた。

```
# red-codens / green-codens の最近のスタイル
env = {
    **(extra_env or {}),
    "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY.get_secret_value(),
}
options = ClaudeAgentOptions(
    model=self._model,
    max_turns=10,
    env=env,
)
# Create agent options — extra_env is merged first so ANTHROPIC_API_KEY cannot
# be overridden by user-supplied credentials
```

`extra_env` を **先にマージして後から ANTHROPIC\_API\_KEY を上書き** する順序が肝で、org ごとに PROXY 設定などを渡したい時に、リクエスト由来の値で API key を奪われない経路を確保している。地味だが、merge 順序を間違えると認証情報が漏れるルートになるので、コメントで意図まで書き残してある。

## 共通基盤の前と後で何が変わったか

定量で測ったわけではないので体感ベースだが、

* **新サービスの立ち上げが速い**: `codens-template/` をコピーしてプロンプトだけ書き換えれば最初の 1 メソッドが動く。allowed\_tools / 戻り値スキーマ / rate\_limit / try-except / model alias がもう揃っているので、**「Agent SDK の起動シーケンスをまた書く」が消えた** のが一番ありがたい。
* **billing 配線でハマらなくなった**: `{model, usage}` の dict が必ず返ると分かっているので、新メソッド追加時に `track_claude_response()` の引数を改めて確認しなくていい。
* **セキュリティの予防線が定型になった**: `disallowed_tools=["Read","Write","Edit",...]` を毎回書く、`env=` の merge 順序を `extra_env` 先にする、というのを **書かないと違和感がある** 状態にできた。PR レビューでも指摘しやすい。
* **揃えすぎたところは戻した**: 一時期メッセージ抽出ロジックを util に切り出していたが、Blue の `AssistantMessage` / `TextBlock` / `ToolUseBlock` を扱う部分はかなり違うので戻した。共通化するなら「クラスの形」「戻り値の dict 形」までで、**ストリーミング処理の中身は揃えない** のが正解だった。

## まとめ

揃えたのはクラスの形と戻り値の dict 形(`{model, usage: {input_tokens, output_tokens}}`)、`_acquire_rate_limit` の入口、`resolve_model()` での alias 解決、allowed\_tools のホワイトリスト、env 経由の ANTHROPIC\_API\_KEY 注入くらい。差分として残したのは Red の 3-retry、Green の Notion 書き戻しと anthropic 直叩きの併存、Blue の Playwright MCP と `max_turns=40`、Yellow の rules-first での薄い使い方。`permission_mode` や per-org の model override のように **採用しなかった** 決定の方が、運用してみると効いている気がする。

複数サービスから Agent SDK を叩いている人、どこを共通化してどこを分けてるか教えてほしい。戻り値の型を `pydantic.BaseModel` に詰め替える運用にしているチームがあったら、そのトレードオフが特に気になる。
