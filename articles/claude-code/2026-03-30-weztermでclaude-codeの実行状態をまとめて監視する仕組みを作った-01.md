---
id: "2026-03-30-weztermでclaude-codeの実行状態をまとめて監視する仕組みを作った-01"
title: "WezTermでClaude Codeの実行状態をまとめて監視する仕組みを作った"
url: "https://zenn.dev/soramarjr/articles/7d9ea81fe643dd"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

一人前食堂のYoutubeが更新されなくなって早1年ですね。  
[fujitani sora](https://x.com/sorafujitani)です。

WezTermでもAgentの実行/待機 の状態をまとめて確認できる仕組みを実装したので、  
その概要と技術的詳細についてまとめました 👀

## Agentの実行状態を監視する

モチベーションになったのは[cmux](https://cmux.com/ja)です。  
Agentの実行状態をまとめて監視できる仕組みは便利そうでしたが、WezTermに引き篭りたかったので今回の実装を考えました。  
体験的にはそれを売りに作られているcmuxなどの方がリッチかもしれませんが、自分にとっては自作の仕組みでも十分にAgentの実行状態監視を効率化できていると感じています。

## 動かし方

default, blog, noteの3つのWezTerm Workspaceを開き、合計4つのClaude Codeを起動しているケースを想定します。

```
$ wezterm cli list --format json | jq -r '.[].workspace' | sort -u
blog
default
note
```

WezTermのCommand Paletteを開くと、ロボットアイコンの`Agent`の項目が用意されており、グレーの点がついています。  
これが現在WezTerm上で開いているClaude Codeセッションの一覧です。  
`Agent ⚫ directoryName [workspaceName]`の形式で、グレーの点は実行状態ではないことを表しています。

また、右Status BarにもAgentの状態をリアルタイム表示しています。  
`🔵 2/3 workspace-name` のように、running数/total数が常に見えるので、Command Paletteを開かなくても現在の状況がひと目でわかります。  
Agentが1つも検出されていない場合はアイコンは表示されず、ワークスペース名のみになります。  
![](https://static.zenn.studio/user-upload/e0f8deb72886-20260329.png)  
*これ*

noteとdefaultのWorkspaceで、Claude Codeのセッションを実行します。  
実行後にCommand Paletteを開くと、実行中のClaude Codeセッションの色がリアルタイムで青色に変化します。  
右Status Barの色とカウントも変化しています。  
![](https://static.zenn.studio/user-upload/00124b5b1f11-20260329.png)

Claude Codeの実行完了後にまたCommand Paletteを開くと、グレーに戻っています。  
実行状態が終了したためです。  
OSからの通知で、どのWorkspaceのClaude Codeセッションが完了したのかも見えるようにしています。  
![](https://static.zenn.studio/user-upload/067c7a2a68a9-20260329.png)

`LEADER + a`コマンド実行で、TUIでClaude Codeセッション全体を確認できるようにしています。  
キーボードナビゲーション（j/k, ↑/↓）、ステータスの色分け、選択中のAgentの詳細パネル（タスク名、ディレクトリ、Pane ID）、3秒ごとの自動リフレッシュに対応しています。  
![](https://static.zenn.studio/user-upload/9d369d985058-20260329.png)  
*アップにした画像*

wez-cc-viewerというOSSを公開していて、これを使ってWezTerm上で実行しているClaude Codeの情報をTUI表示しています

go installとluaへの組み込みで使用できます。  
GitHub Starお願いします⭐️  
<https://github.com/sorafujitani/wez-cc-viewer>

この仕組みによって、Command Paletteで確認できることで垂直タブのように特定領域をAgentの確認に占有されることもないです。  
トグルでパッと確認して必要なければしまっておけます。

## 組み込み方

前提として、下記のツールを利用していることに依存しています

* WezTerm
* Claude Code
* macOS

macOS固有のコマンドラインツールにも依存しているので、そのままだとLinuxやWindowsとかでは動かないと思います。  
よしなに読み替えてください。  
また、Agentを監視するmoduleと、wezterm.luaはファイル単位で分離しているので、dotfilesをそこまで変更しなくてもシンプルなインターフェースで使えるようになっているはずです。  
うまく動かなければ、筆者を問い詰めるか、お使いのAgentに直させてください。

コードについては、後続の実装詳細セクションで解説しています。

dotfileは下記です。  
<https://github.com/sorafujitani/weztermdot>

0. wez-cc-viewerのインストール

```
go install github.com/sorafujitani/wez-cc-viewer@latest
```

1. agent.luaをコピペ  
   上記で示した環境であればそのままのコピペで問題ないです。  
   .config/wezterm/agent.luaを作成してください。

agent.lua（長いのでtoggle）

agent.lua

```
local wezterm = require("wezterm")
local act = wezterm.action

local M = {}

-- Resolve wez-cc-viewer binary path (cached after first call)
local _wez_cc_viewer_cache = nil
local function find_wez_cc_viewer()
	if _wez_cc_viewer_cache then
		return _wez_cc_viewer_cache
	end
	local ok, stdout = wezterm.run_child_process({
		os.getenv("SHELL") or "/bin/zsh", "-lic", "which wez-cc-viewer",
	})
	if ok and stdout then
		local path = stdout:gsub("%s+$", "")
		if path ~= "" then
			_wez_cc_viewer_cache = path
			return path
		end
	end
	return nil
end

function M.notify(title, message)
    wezterm.run_child_process({
        "osascript",
        "-e",
        string.format(
            'display notification %q with title %q sound name "Glass"',
            message,
            title
        ),
    })
end

local STATUS_ICON = { idle = "⚫", running = "🔵", unknown = "?" }
local cache = { result = {}, timestamp = 0 }
local CACHE_TTL = 3

-- Track previous agent info per pane_id for completion detection
local prev_agents = {} -- pane_id -> agent info table

-- Walk ppid chain to find a claude ancestor pid
local function find_claude_ancestor(pid, procs, claude_pids)
    local visited = {}
    local current = pid
    while current and current > 1 and not visited[current] do
        visited[current] = true
        if claude_pids[current] then
            return current
        end
        local info = procs[current]
        if not info then
            break
        end
        current = info.ppid
    end
    return nil
end

-- Detect agent status for a single pane; returns status string or nil
local function detect_pane_agent(p, procs, claude_pids, claude_status)
    local ok_info, fg_info = pcall(function()
        return p:get_foreground_process_info()
    end)
    local fg_pid = ok_info and fg_info and fg_info.pid

    if fg_pid and procs[fg_pid] then
        local cpid = find_claude_ancestor(fg_pid, procs, claude_pids)
        return cpid and (claude_status[cpid] or "idle") or nil
    end

    local proc_path = p:get_foreground_process_name() or ""
    local proc_name = proc_path:match("([^/]+)$") or proc_path

    if proc_name:find("claude") then
        return "idle"
    end

    for pid, info in pairs(procs) do
        if info.name == proc_name or info.fullpath == proc_path then
            local cpid = find_claude_ancestor(pid, procs, claude_pids)
            if cpid then
                return claude_status[cpid] or "idle"
            end
        end
    end
    return nil
end

--- Scan all panes for running agents. Results are cached for CACHE_TTL seconds.
function M.scan()
    local now = os.time()
    if now - cache.timestamp < CACHE_TTL then
        return cache.result
    end

    local ok, stdout = wezterm.run_child_process({ "ps", "-eo", "pid,ppid,comm" })
    local procs = {}
    local children = {}
    local claude_pids = {}
    if ok and stdout then
        for line in stdout:gmatch("[^\n]+") do
            local pid_s, ppid_s, comm = line:match("(%d+)%s+(%d+)%s+(.+)")
            if pid_s then
                local pid = tonumber(pid_s)
                local ppid = tonumber(ppid_s)
                local name = comm:gsub("^%s+", ""):gsub("%s+$", "")
                local basename = name:match("([^/]+)$") or name
                procs[pid] = { ppid = ppid, name = basename, fullpath = name }
                if not children[ppid] then
                    children[ppid] = {}
                end
                table.insert(children[ppid], pid)
                if basename:find("claude") then
                    claude_pids[pid] = true
                end
            end
        end
    end

    -- Claude Code spawns caffeinate while running and kills it when idle.
    local claude_status = {}
    for cpid in pairs(claude_pids) do
        local is_active = false
        for _, child_pid in ipairs(children[cpid] or {}) do
            if procs[child_pid].name == "caffeinate" then
                is_active = true
                break
            end
        end
        claude_status[cpid] = is_active and "running" or "idle"
    end

    local agents = {}
    for _, mux_win in ipairs(wezterm.mux.all_windows()) do
        local workspace = mux_win:get_workspace()
        for _, tab in ipairs(mux_win:tabs()) do
            for _, p in ipairs(tab:panes()) do
                local status = detect_pane_agent(p, procs, claude_pids, claude_status)
                if status then
                    local cwd = p:get_current_working_dir()
                    local dir = cwd and cwd.file_path or "unknown"
                    table.insert(agents, {
                        workspace = workspace,
                        pane_id = p:pane_id(),
                        project = dir:match("([^/]+)$") or dir,
                        dir = dir,
                        status = status,
                    })
                end
            end
        end
    end

    -- Detect agents that completed: running->idle or running->gone
    local completed = {}
    local current_agents = {}
    for _, a in ipairs(agents) do
        current_agents[a.pane_id] = a
        local prev = prev_agents[a.pane_id]
        if prev and prev.status == "running" and a.status == "idle" then
            table.insert(completed, a)
        end
    end
    -- Check for agents that were running but disappeared entirely
    for pane_id, prev in pairs(prev_agents) do
        if prev.status == "running" and not current_agents[pane_id] then
            table.insert(completed, prev)
        end
    end
    prev_agents = current_agents

    -- Log scan results for debugging
    local statuses = {}
    for _, a in ipairs(agents) do
        table.insert(statuses, a.project .. "=" .. a.status)
    end
    if #agents > 0 then
        wezterm.log_info("agent scan: " .. table.concat(statuses, ", "))
    end
    for _, a in ipairs(completed) do
        wezterm.log_info("agent completed: " .. a.project .. " [" .. a.workspace .. "]")
        M.notify("Agent Complete", a.project .. " [" .. a.workspace .. "]")
    end

    cache.result = agents
    cache.timestamp = now
    return agents, completed
end

--- Return cached agents without triggering a new scan.
function M.cached()
    return cache.result
end

--- Return a wezterm action that opens the agent dashboard InputSelector.
function M.dashboard_action()
    return wezterm.action_callback(function(window, pane)
        cache.timestamp = 0
        local agents = M.scan()
        if #agents == 0 then
            window:toast_notification("wezterm", "No running agents", nil, 3000)
            return
        end

        local choices = {}
        for _, a in ipairs(agents) do
            local icon = STATUS_ICON[a.status] or "?"
            table.insert(choices, {
                label = string.format("%s %s [%s]  %s", icon, a.project, a.workspace, a.dir),
                id = a.workspace,
            })
        end

        window:perform_action(act.InputSelector({
            title = string.format("Running Agents (%d)", #agents),
            choices = choices,
            action = wezterm.action_callback(function(win, p, id)
                if id then
                    win:perform_action(act.SwitchToWorkspace({ name = id }), p)
                end
            end),
        }), pane)
    end)
end

--- Return a wezterm action that opens the wez-cc-viewer TUI in an overlay pane.
function M.tui_dashboard_action()
    return wezterm.action_callback(function(window, pane)
        local wez_cc_viewer = find_wez_cc_viewer()
        if not wez_cc_viewer then
            window:toast_notification("wezterm", "wez-cc-viewer not found in PATH", nil, 3000)
            return
        end
        local new_pane = pane:split({
            direction = "Bottom",
            args = { wez_cc_viewer },
        })
        window:perform_action(act.TogglePaneZoomState, new_pane)
    end)
end

--- Return command palette entries for augment-command-palette.
function M.palette_entries()
    local ok, result = pcall(M.scan)
    local agents = ok and result or cache.result
    local running_count = 0
    for _, a in ipairs(agents) do
        if a.status == "running" then
            running_count = running_count + 1
        end
    end

    local dashboard_label = #agents == 0 and "wez-cc-viewer"
        or string.format("wez-cc-viewer (%d agents, %d running)", #agents, running_count)

    local entries = {
        {
            brief = dashboard_label,
            icon = "md_robot",
            action = M.tui_dashboard_action(),
        },
        {
            brief = "Agent: Test Notification",
            icon = "md_bell",
            action = wezterm.action_callback(function()
                M.notify("Agent Complete", "Test notification")
            end),
        },
    }
    for _, a in ipairs(agents) do
        local icon = STATUS_ICON[a.status] or "?"
        table.insert(entries, {
            brief = string.format("Agent %s %s [%s]", icon, a.project, a.workspace),
            icon = "md_robot",
            action = wezterm.action_callback(function(win, p)
                win:perform_action(act.SwitchToWorkspace({ name = a.workspace }), p)
            end),
        })
    end
    return entries
end

return M
```

2. wezterm.luaでrequire  
   agent.luaで定義したmoduleを読み込んでWezTerm APIに渡してあげます。  
   以下は必要な部分のみ抜粋です。ご自身の設定に合わせて統合してください。  
   wez-cc-viewerと組み込む際は、READMEも参照してください。

wezterm.lua

```
local agent = require("agent")

-- wez-cc-viewerからのワークスペース切り替えを受け取る
wezterm.on("user-var-changed", function(window, pane, name, value)
    if name == "switch_workspace" then
      window:perform_action(act.SwitchToWorkspace({ name = value }), pane)
    end
end)

-- 右ステータスバーにAgent状態を表示
wezterm.on("update-right-status", function(window)
    local agents = agent.scan()
    local running = 0
    for _, a in ipairs(agents) do
      if a.status == "running" then running = running + 1 end
    end
    
    local parts = {}
    if #agents > 0 then
      local icon = running > 0 and "🔵" or "⚫"
      table.insert(parts, { Text = string.format(" %s %d/%d ", icon, running, #agents) })
    end
    table.insert(parts, { Text = window:active_workspace() .. " " })
    window:set_right_status(wezterm.format(parts))
end)

-- Command PaletteにAgentエントリを追加
wezterm.on("augment-command-palette", function()
    return agent.palette_entries()
end)

-- LEADER + a でTUIダッシュボードを開く
config.keys = {
    {
      key = "a",
      mods = "LEADER",
      action = agent.tui_dashboard_action(),
    },
}
```

## 実装詳細

### 全体のアーキテクチャ

主に3つの構成要素があります。

* `wezterm.lua` — メインの設定ファイル。キーバインドやUI設定に加えて、Agentスキャンの起動とCommand Paletteへのエントリ登録をしています
* `agent.lua` — Agent監視のロジックをまとめたモジュール。プロセスツリーの走査、状態判定、完了通知などを担当しています
* [wez-cc-viewer](https://github.com/sorafujitani/wez-cc-viewer) — Go製のTUIダッシュボード。Bubbletea + Lipglossで構築されており、Agent一覧の表示・ナビゲーション・ワークスペース切り替えを担当しています

### Agentの検出方法

WezTermにはLuaから[Mux](https://wezterm.org/config/lua/wezterm.mux/all_windows.html)（multiplexer）の全ウィンドウ・タブ・ペインにアクセスできるAPIがあります。これを使って全ペインを走査し、各ペインのフォアグラウンドプロセスから プロセスツリーを親方向にたどって、claudeプロセスが祖先にいるかどうかを判定しています。

具体的な流れは以下です。

1. `ps -eo pid,ppid,comm` でシステム上の全プロセスを取得
2. プロセス名に `claude` を含むPIDをclaude候補として記録
3. 各ペインのフォアグラウンドプロセスから親PIDチェーンを上にたどり、claude候補に到達したらそのペインは「Agentが動いている」と判定

```
local function find_claude_ancestor(pid, procs, claude_pids)
    local visited = {}
    local current = pid
    while current and current > 1 and not visited[current] do
        visited[current] = true
        if claude_pids[current] then
            return current
        end
        local info = procs[current]
        if not info then break end
        current = info.ppid
    end
    return nil
end
```

単にフォアグラウンドプロセス名だけを見るのではなく、プロセスツリーを走査するのがポイントです。Claude Codeはtool useの過程で様々な子プロセス（npm, git, node等）をspawnするので、フォアグラウンドが `node` であっても、その祖先に `claude` がいればAgentとして検出できます。

<https://wezterm.org/config/lua/pane/get_foreground_process_info.html>

### Running / Idle の判定

Agentを検出できたとして、次に「今まさにタスクを実行中なのか、それとも入力待ちでアイドル状態なのか」を区別したいです。

Claude Codeはタスク実行中に `caffeinate` プロセスを子プロセスとしてspawnし、アイドルになると殺すという挙動があります。macOSの `caffeinate` はスリープを抑制するコマンドで、Claude Codeが長時間タスク中にMacがスリープしないよう使っているようです。

この挙動を利用して、claudeプロセスの直接の子プロセスに `caffeinate` がいれば `running`、いなければ `idle` と判定しています。

```
local claude_status = {}
for cpid in pairs(claude_pids) do
    local is_active = false
    for _, child_pid in ipairs(children[cpid] or {}) do
        if procs[child_pid].name == "caffeinate" then
            is_active = true
            break
        end
    end
    claude_status[cpid] = is_active and "running" or "idle"
end
```

公式にドキュメントされた仕様ではないですが、実用上は十分に機能しています。  
最新の言及では、v2.1.83で`caffeinate`に関連する修正がリリースされている。

<https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md>

> Fixed caffeinate process not properly terminating when Claude Code exits, preventing Mac from sleeping

macOS側のcaffeinate仕様  
<https://ss64.com/mac/caffeinate.html>

この辺りの記事も参考にしました  
<https://dev.ngockhuong.com/posts/preventing-mac-sleep-during-claude-code-sessions/>

### スキャンのタイミングとキャッシュ

スキャンは [update-right-status](https://wezterm.org/config/lua/window-events/update-right-status.html) イベントにフックして実行しています。これはWezTermがステータスバーを更新するたびに発火するイベントで、ユーザーの操作やフォーカス変更のたびに呼ばれます。

スキャン結果をそのまま右ステータスバーの表示にも活用しています。  
running数/total数をアイコン付きで表示することで、Command Paletteを開かずとも常にAgentの状態が視界に入る形になっています。

```
wezterm.on("update-right-status", function(window)
  local agents = agent.scan()
  local running = 0
  for _, a in ipairs(agents) do
      if a.status == "running" then
          running = running + 1
      end
  end

  local status_parts = {}
  if #agents > 0 then
      local icon = running > 0 and "🔵" or "⚫"
      table.insert(status_parts, { Foreground = { Color = scheme.foreground } })
      table.insert(status_parts, { Text = string.format(" %s %d/%d ", icon, running, #agents) })
  end
  table.insert(status_parts, { Text = window:active_workspace() .. " " })

  window:set_right_status(wezterm.format(status_parts))
end)
```

毎回 `ps` コマンドを叩くのはコストが高いので、3秒間のTTLキャッシュを設けています。スキャン結果はモジュールレベルの `cache` テーブルに保存され、TTL内であればキャッシュから返す形です。

### 完了通知

Agentの状態遷移を追跡して、running → idle に変わったタイミング、つまりタスクが完了した瞬間を検出しています。

仕組みとしては、各ペインIDごとに前回のスキャン結果を `prev_agents` テーブルに保持しておき、今回のスキャン結果と比較します。

* 前回 `running` だったペインが今回 `idle` になっていたら → 完了
* 前回 `running` だったペインが今回のスキャン結果に存在しない場合（ペインが閉じられた等）→ 完了

完了を検出したら、macOSの `osascript` 経由でデスクトップ通知を飛ばします。

```
function M.notify(title, message)
    wezterm.run_child_process({
        "osascript", "-e",
        string.format(
            'display notification %q with title %q sound name "Glass"',
            message, title
        ),
    })
end
```

「Glass」のサウンド付きで通知が来るので、別の作業をしていてもAgentの完了に気づけます。複数のAgentを並行して走らせているときに特に便利です。  
通知の手段は他にもあると思いますが、agent.luaの仕組みと密結合にした方が管理しやすそうだったので今はこの方針にしています。

### wez-cc-viewer

`LEADER + a`（Ctrl+a → a）で[wez-cc-viewer](https://github.com/sorafujitani/wez-cc-viewer)が開きます。Go（Bubbletea + Lipgloss）で構築したTUIダッシュボードで、WezTermのオーバーレイペインとして全画面表示されます。

現在検出されている全Agentが一覧表示され、各エントリにはステータスインジケータ（● running / ○ idle）、プロジェクト名、ワークスペース名が表示されます。選択中のAgentについては詳細パネルでタスク名、ディレクトリ、Pane IDも確認できます。3秒ごとに自動リフレッシュされるため、リアルタイムに状態変化を追えます。

| Key | Action |
| --- | --- |
| `j` / `↓` | Move selection down |
| `k` / `↑` | Move selection up |
| `Enter` | Switch to selected agent's workspace |
| `r` | Manual refresh |
| `g` / `G` | Jump to first / last |
| `q` / `Esc` | Quit |

ワークスペースの切り替えには、iTerm2互換の[SetUserVar](https://iterm2.com/documentation-escape-codes.html)エスケープシーケンスを利用しています。wez-cc-viewerがエスケープシーケンスを送信し、WezTerm側の`user-var-changed`イベントハンドラが`SwitchToWorkspace`アクションを実行する形です。

```
wezterm.on("user-var-changed", function(window, pane, name, value)
  if name == "switch_workspace" then
    window:perform_action(act.SwitchToWorkspace({ name = value }), pane)
  end
end)
```

### Command Paletteとの統合

`CMD+SHIFT+P` で開くWezTerm標準のCommand PaletteにもAgentの情報を統合しています。  
[augment-command-palette](https://wezterm.org/config/lua/window-events/augment-command-palette.html) イベントで動的にエントリを追加していて、下記が表示されます。

* wez-cc-viewer — TUIダッシュボードを開く。検出中のAgent数とrunning数がラベルに含まれます
* 個別のAgentエントリ — 各Agentへの直接ジャンプ

Command Paletteはファジー検索が効くので、「agent」と打つだけで関連エントリが絞り込まれます。

### まとめ

やっていることをざっくり言えば、「プロセスツリーを見てclaude ancestorがいるペインを見つけ、caffeinate子プロセスの有無でrunning/idleを判定し、状態遷移で完了通知を出す」という仕組みです。

[もずます](https://x.com/mozumasu?s=20)さんの資料にいいことが書いてあって

![](https://static.zenn.studio/user-upload/cca247a3f975-20260328.png)  
*<https://www.docswell.com/s/mozumasu/5PR9PQ-2026-03-27-190503>*

これは多分そうで、細かいハンドリングを考えるとWezTermは楽でいいよなと。

今回は以上です。  
別のアイデアや改善案などあれば教えていただけると嬉しいです ！  
あと記事のいいねと拡散も😋
