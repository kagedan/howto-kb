---
id: "2026-05-05-agent-に-e2e-テストを書かせる時実装-diff-を-context-として渡す設計を入れた-01"
title: "agent に E2E テストを書かせる時、実装 diff を context として渡す設計を入れた話"
url: "https://zenn.dev/zoetaka38/articles/a5f0c8c3ea4156"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

## はじめに

Codens では Purple という orchestrator が「develop step」を回して実装させ、その出力を Blue が受けて E2E テストを書く、という多段の agent 構成にしている。これがそこそこ動いてはいたのだが、ずっと違和感があった。Blue が生成してくる E2E が「Purple がさっき変えた箇所」にぴったり寄ってこなくて、機能ベース、画面ベースで広く撒いてしまう。**Blue が「何を変えたか」を知らない**から、当然と言えば当然だった。

最初は Blue 側の prompt を強めればいいかと思って色々試したのだが、根本解決にはならなくて、結局 Purple→Blue 間で**実装 diff(unified diff のテキスト)を直接渡す**という地味な変更を入れる方向に落ち着いた。今回 commit したのは Blue 側の受け口、つまり internal API と Phase 1 の prompt 構成まで。Purple 側の送信(`BlueCodensClient.generate_e2e_tests` と `GenerateE2EStep` から `code_diff` を実際に渡す配線)はこれから wire するので、前後の出力比較はまだ取れていない。Blue 側の挙動は単体で testable な状態にはあるので、設計の意図と prompt 構成の話を書く。dogfooding が一周したらまた書きます。

## 状況: Blue が「何を変えたか」を知らない問題

Blue の探索的 E2E テスト生成(exploratory E2E)は、ざっくり 3 フェーズで動いている。

1. **Phase 1: Code Analysis**: ワークスペースのコードを Claude Agent SDK でファイル構造から読ませて、ページ・ルート・フォームを把握する
2. **Phase 2: Browser Discovery**: Playwright MCP(Docker) でターゲット URL を実際に開いて、DOM を覗きながら自律的に操作させる
3. **Phase 3: Test Synthesis**: 探索履歴から Playwright テストコードを synthesize する

問題は Phase 1 の入口だった。Blue は「コードベース全部」を analysis 対象として渡されている。Purple が直前に何を触ったかは、**Blue の視点からは見えていない**。だから Blue は「このアプリは login 画面と dashboard と settings があって、それぞれ test しよう」みたいな機能ベースの発想で広げてしまう。

たとえば task goal が「招待リンクからの signup フローのバリデーションを 1 つ追加した」のような極めてピンポイントな変更だった場合でも、Blue は task の自然言語タイトルから「招待リンク signup の機能を全方位でテスト」と推測しがちで、実装で実際に触られた `expires_at` のチェックや `invitation_expired` エラーパスにフォーカスしきれない。scenario の多くは変更と無関係な周辺機能のもので、今回追加された 1 行ぶんのバリデーションは 1〜2 件、しかも周辺の細部(token expire 時の挙動)を踏み込みきれていない、という出力になりがちだった。

書いてしまえばあたりまえなのだが、**「コードベースを盲目的に探索する agent」と「diff focused に動いてほしい QA agent」は要求が違う**。前者は機能カバレッジ、後者は変更カバレッジを最大化したい。同じ codebase 探索フレームワークの上に両方乗せていたので、Blue も前者の挙動になっていた。

## アーキテクチャ: Purple → Blue の diff handoff

直し方はシンプルで、Purple が develop step で生成した変更の `git diff` 出力を、Blue の internal API に丸ごと渡すだけ。Blue 側はそれを Phase 1 の system / user prompt に追加して、Claude Agent SDK に「この diff にフォーカスして探索しろ」と指示する。

### Blue: API と client の接続点

internal API のエンドポイントに `code_diff` を生やす。受け取った diff は Celery タスク経由で `ExploratoryE2EAgentClient` まで伝搬する。

```
# blue-codens/backend/src/api/v1/routes/internal.py
class InternalExploratoryE2ERequest(BaseModel):
    target_url: str
    exploration_goal: str
    focus_areas: list[str] = Field(default_factory=list)
    max_steps: int = Field(default=30, ge=5, le=100)
    auth_config: dict | None = None
    suite_id: str | None = None
    language: str = "ja"
    browser_type: str = "chromium"
    browser_locale: str | None = None
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout: int = 30000
    code_diff: str | None = Field(
        None,
        description=(
            "Git diff of the implementation changes. When provided, the exploratory "
            "agent uses it as context during the code analysis phase."
        ),
    )
```

ここで決めの一つは、 **diff を「文字列(unified diff フォーマット)そのまま」で受け取った** こと。最初は file path のリスト + per-file の hunk JSON みたいな structured 表現を考えていたのだが、結局やめた。理由は後述するが、Claude Agent SDK に渡す文脈として、unified diff のテキストは LLM 側がもう「読み慣れた」フォーマットなので、変に構造化して渡すよりプレーンに `git diff` の出力をぶち込むほうが安定すると判断した。

Celery タスクから agent client への伝搬。

```
# blue-codens/backend/src/infrastructure/tasks/exploratory_e2e_generation.py
async def _generate_exploratory_e2e_async(
    project_id: str,
    target_url: str,
    exploration_goal: str,
    # ... (中略)
    code_diff: str | None = None,
) -> dict[str, Any]:
    # ...
    agent_client = ExploratoryE2EAgentClient(
        workspace_path=workspace_path,
        progress_callback=progress_callback,
        code_diff=code_diff,
    )
```

そして Phase 1 の prompt に diff context を差し込む部分。これが今回の本体に近い。

```
# blue-codens/backend/src/infrastructure/external_apis/exploratory_agent_client.py
async def _run_code_analysis_phase(self, session: ExplorationSession) -> dict[str, Any]:
    system_prompt = """You are a code analyst. Analyze the codebase to understand:
1. Page/route structure
2. Form components and their fields
...
ONLY use mcp__local__ tools. Start with get_file_structure."""

    diff_context = ""
    if self._code_diff:
        diff_context = (
            f"\n\nIMPLEMENTATION DIFF (focus your analysis on these changed files):\n"
            f"```diff\n{self._code_diff}\n```\n"
        )

    user_prompt = f"""Analyze this codebase for E2E testing.

Exploration goal: {session.exploration_goal}
Focus areas: {', '.join(session.focus_areas) if session.focus_areas else 'All features'}{diff_context}
Start by getting the file structure, then read key page/component files.
{('Pay special attention to the files and endpoints shown in the diff above.' if self._code_diff else '')}"""
```

ポイントは **`diff_context` を user\_prompt に「追加で」差すだけで、system\_prompt は触らない** こと。最初 system\_prompt 側に「diff があれば〜」みたいな分岐を書いていたのだが、Claude Agent SDK 経由で動かす時、system\_prompt が長くなるほど phase 全体の cwd 探索が乱れるのを観察した。code analysis phase は `mcp__local__get_file_structure` を起点に動くので、system 側はあくまで「フォーマット指示」と「使うツール指定」に閉じておきたい。文脈情報は user\_prompt に寄せた。

最後の "Pay special attention to ..." の 1 行はちょっとした steering で、これがないと Claude が diff を補足情報として読み流す挙動を Blue 単体テストで観察した。1 行入れるだけで「diff を優先で読む」ほうにバイアスがかかる想定。

### もう一系統: task goal ベースの軽量 test gen

Blue には exploratory ではなく軽量な「task goal ベースの test scenario 生成」もある(acceptance criteria から最大 N 件 抽出するやつ)。こちらにも同じ `code_diff` を流せるようにした。

```
# blue-codens/backend/src/infrastructure/external_apis/claude_client.py
async def generate_test_scenarios_from_task_goal(
    self,
    task_goal: str,
    acceptance_criteria: list[str] | None = None,
    count: int = 3,
    code_diff: str | None = None,
) -> list[str]:
    # ...
    diff_section = ""
    if code_diff:
        diff_section = (
            f"\n\n実装差分(この実装内容を参照してテストシナリオを生成してください):\n"
            f"```diff\n{code_diff}\n```\n"
        )

    user_prompt = f"""タスクゴール:
{task_goal}{diff_section}
上記のタスクゴール{('と実装差分' if code_diff else '')}から最大{count}個のE2Eテストシナリオを抽出してください。
各シナリオは「- 」で始まる形式で1行ずつ出力してください。"""
```

system\_prompt 側にも「実装コードが提供されている場合は、実際に実装されたエンドポイントや UI パスを優先してテストする」という 1 行を追加してある。これが効くだろうと想定しているのは、**「タスクゴールの自然言語」と「実装の実態」が微妙にズレた時**。「招待リンクからの signup を実装」という goal に対して、実装は invitation token を URL query から拾う形だったとしよう。goal だけで test gen させると Blue は「メール経由で signup する」と推測してテストを書きがちで、実装と乖離する。diff があれば `?token=...` を読みに行ってる行が見えるので、test もその形に寄るはず、というのが設計時の仮説。

### Purple 側の整合(これから wire する)

Purple は `BlueCodensClient.trigger_exploratory_e2e()` から POST するクライアントを既に持っている(`purple-codens/backend/src/infrastructure/external_apis/blue_codens_client.py`)。あとは `BlueCodensClient.generate_e2e_tests` と `GenerateE2EStep` で `git diff <base>...HEAD` を取って context variable に詰め、`code_diff` 引数として流すだけ。 **Blue 側は受け口を先に開けて、`code_diff is not None` で挙動が変わる「opt-in 設計」** にしてあるので、Purple 側の追従が遅れても既存の呼び出しは 1 行も壊れない。`test_generate_without_code_diff_still_works` という回帰テストで未指定時の挙動を pin している。

## 設計の意図と、観察したいこと

実装 diff を渡すようにすると、Blue の attention の置き方が変わる、というのが今回の仮説。dogfooding はこれから一周回すので、ここから先は「観察する予定の変化」として書く。

### 変更近傍に scenario が寄ることを期待している

「token expire 検証を 1 行追加」のような変更で、diff なしだと Blue は task goal から「signup の happy path / error path / dashboard 遷移」のような機能ベースの scenario を組み立てがち。diff を渡すと、prompt 中の `expires_at`、`invitation_expired`、`consumed_at` のような **実装で実際に触られている symbol が Blue の attention に入る** ので、Browser Discovery phase でその token を持って遷移するページを優先で踏みに行ってほしい、というのが設計意図。LLM が diff の hunk を読んで「この変更が観測できる UI 動作はどれか」を逆算することで、scenario の主語が「機能」から「変更」に移る、という方向。実際にそうなるかは次の dogfooding で観察する。

### scenario 数は減るはず

生成数自体は減ると見込んでいる。前は 機能 × 3 = 30+ 件出ていたところが、変更にフォーカスしたぶん 5〜8 件程度に絞れるはず、というのが想定。これは網羅性が犠牲になるのではなく、 **「変更と無関係な機能テスト」をそもそも書かなくなる**設計で、機能カバレッジは別レーン(suite に溜まった既存テスト、定期 full-suite)で持つ分業。Purple → Blue の handoff で書く E2E は「この PR が壊さないことを保証する E2E」で十分。

### 効かないと予想しているケース

設計時点で「diff を渡しても効かないだろうな」と予想しているケース:

* **diff が巨大すぎる時**(数千行のリファクタ): Phase 1 の context window を食い潰す。Purple 側でサイズ閾値を持って summary に置き換える fallback を検討中
* **diff が「設定ファイルだけ」の時**: `requirements.txt` の 1 行追加など、LLM が「ライブラリ更新によって UI 動作がどう変わるか」を書こうとして空回りする可能性
* **diff が複数の独立タスクを跨ぐ時**: 1 commit に複数機能を詰めてしまうと、Blue が交差した scenario を書きそう。これは Purple 側の commit 分割粒度の問題

dogfooding 中に踏みに行く想定で、踏んだら fallback を入れる。

## ハマり / 学び

### diff フォーマット選定

最初に書いた通り、unified diff のテキストそのまま、で落ち着いた。検討した代替は次のとおり。

| 案 | 採否 | 理由 |
| --- | --- | --- |
| unified diff 文字列 | 採用 | LLM が学習データで一番見ているフォーマット。プレーンに渡すのが安定 |
| 変更ファイルパスのリストのみ | 不採用 | 「どう変えたか」が落ちる。出力がブレる |
| 変更後ファイル全文 + パス | 不採用 | コンテキスト重い割に diff の意図が伝わらない |
| AST diff の JSON | 不採用 | 自前構築コストが高く、LLM 側のフォーマット理解で逆にロスする |
| files-changed リスト + unified diff | 検討中 | 巨大 diff の時の fallback 用 |

LLM に逆算してほしい時は unified diff、機械的に処理する時は構造化、という棲み分けで考えている。

### context window の食われ方

Claude Agent SDK の `ClaudeAgentOptions` には max\_turns しか直接出ていないが、Phase 1 はもともと「ファイル構造の探索 + 主要コンポーネント read」で 5〜10 turn 使う構成になっている。ここに diff context を 1 turn ぶんとして注入するので、 **diff のサイズはそのまま phase の余裕に響く**。Purple 側で `git diff --stat` を先に取って、合計変更行が一定値を超えたら handoff 自体をスキップしてフルスキャン phase に倒す、というガードを足す予定。

### develop step 完了タイミングと Blue 起動タイミング

Purple の develop 系 step は `develop_finalize` という別 step で commit 漏れと secondary repo の push 忘れを検証する構造になっている。 **diff を取るのは `develop_finalize` が `repos_verified` を返した直後**が正解になりそう。直接 develop step の直後だと unstaged な変更が残ることがあり、`git diff` が中途半端な状態を拾う事故が発生しうる。具体的には `claude_code` → `develop_finalize` → `git_branch` → `trigger_exploratory_e2e` の順で、最後の step で `git diff <base>...HEAD` を計算して `code_diff` 引数に詰める想定。順序を間違えると、 secondary repo の commit が remote に届いていない状態で Blue がコードを読み、 workspace\_path と remote が乖離する race を踏むので、ここは Purple 側を wire する時に気をつけたい論点。

### opt-in 設計の旨味

`code_diff: str | None = None` で受けて、None なら従来挙動、というデフォルトを徹底したのは正解だった。 **Purple 側がまだ `code_diff` を流さない状態でも、Blue の internal API を更新してデプロイできる** ので、今回みたいに「片側だけ先に出す」 commit が無理なくできる。回帰テストも「diff を受けた時の挙動」と「diff を受けなかった時の挙動」を 2 本で pin している。

```
# blue-codens/backend/tests/unit/api/test_internal.py 抜粋
def test_generate_accepts_code_diff(self):
    diff = "diff --git a/login.py b/login.py\n+def login(): pass\n"
    # ... mock setup ...
    resp = client.post(
        f"/api/v1/internal/projects/{proj_id}/e2e-tests/generate",
        json={"task_goal": "Test login", "code_diff": diff},
        headers={"X-Internal-Api-Key": "test-key"},
    )
    assert resp.status_code == 201
    call_kwargs = mock_claude.generate_test_scenarios_from_task_goal.call_args.kwargs
    assert call_kwargs["code_diff"] == diff

def test_generate_without_code_diff_still_works(self):
    """diff を受けなかった時の後方互換も pin する"""
    # ... 同じく検証 ...
```

agent 間のプロトコル変更は、片側がいつ追従するか読めないので、後方互換のテストを別個に書いておくのが結果として一番ストレスがなかった。

## まとめ

multi-agent system でドメイン情報をどう受け渡すかは、**「receive 側がそれを使って何を逆算するか」** で形が決まる、というのがこの一連の設計検討で得た一番の感覚。今回 Blue は実装の意図を逆算して E2E scenario を書きたかったので、 LLM が読み慣れた unified diff を渡すのが筋が良いはず、という判断になった。これが「機械的に CI に流すための変更ファイル一覧」が欲しい場面なら、structured な files-changed リストのほうが正解になるはず。同じ「変更を伝える」 でも、 receive 側のタスクが書き手なのか実行者なのかで、最適なフォーマットが分岐する。

そして agent 間プロトコルは opt-in で広げるのが圧倒的に楽。`code_diff: str | None = None` のデフォルト 1 個と、受け取った時だけ prompt が伸びる分岐 1 個で、Blue 側の挙動を前後互換の上に伸ばせる。今回の commit が Blue 側だけで止まっているのもこの設計のおかげで、Purple の送信側 wire は安心して別 PR に切り出せる。Yellow(activity ledger)や Green(PRD) からも Blue / Red に文脈情報を流す予定があるので、同じパターンで広げていく。

ところで聞きたいんですが、 multi-agent で「片方の agent の出力を別の agent の context に流す」時、皆さんどういう単位で渡してますか? task の自然言語 goal だけ? diff まで? それとも task graph のノード単位で trace を渡している? 自分は今「LLM の receive 側が何を逆算したいか」 で形を決めるという原則に落ち着きつつあるけれど、 **送り手と受け手が同じプロジェクト内で進化する時のプロトコル設計** は、まだ最適解に辿り着いていない感じがする。同じ問題踏んでる人いたら聞いてみたいです。
