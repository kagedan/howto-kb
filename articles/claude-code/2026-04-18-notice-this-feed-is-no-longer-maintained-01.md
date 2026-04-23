---
id: "2026-04-18-notice-this-feed-is-no-longer-maintained-01"
title: "[NOTICE] This feed is no longer maintained"
url: "https://code.claude.com/docs/en/changelog/rss.xml"
source: "rss"
category: "claude-code"
tags: ["claude-code", "rss"]
date_published: "2026-04-18"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

https://code.claude.com/docs
Mintlify
Thu, 23 Apr 2026 02:55:02 GMT

https://code.claude.com/docs

https://code.claude.com/docs/en/changelog#2-1-118
https://code.claude.com/docs/en/changelog#2-1-118
Thu, 23 Apr 2026 00:57:07 GMT
- Added vim visual mode (`v`) and visual-line mode (`V`) with selection, operators, and visual feedback
- Merged `/cost` and `/stats` into `/usage` — both remain as typing shortcuts that open the relevant tab
- Create and switch between named custom themes from `/theme`, or hand-edit JSON files in `~/.claude/themes/`; plugins can also ship themes via a `themes/` directory
- Hooks can now invoke MCP tools directly via `type: "mcp_tool"`
- Added `DISABLE_UPDATES` env var to completely block all update paths including manual `claude update` — stricter than `DISABLE_AUTOUPDATER`
- WSL on Windows can now inherit Windows-side managed settings via the `wslInheritsWindowsSettings` policy key
- Auto mode: include `"$defaults"` in `autoMode.allow`, `autoMode.soft_deny`, or `autoMode.environment` to add custom rules alongside the built-in list instead of replacing it
- Added a "Don't ask again" option to the auto mode opt-in prompt
- Added `claude plugin tag` to create release git tags for plugins with version validation
- `--continue`/`--resume` now find sessions that added the current directory via `/add-dir`
- `/color` now syncs the session accent color to claude.ai/code when Remote Control is connected
- The `/model` picker now honors `ANTHROPIC_DEFAULT_*_MODEL_NAME`/`_DESCRIPTION` overrides when using a custom `ANTHROPIC_BASE_URL` gateway
- When auto-update skips a plugin due to another plugin's version constraint, the skip now appears in `/doctor` and the `/plugin` Errors tab
- Fixed `/mcp` menu hiding OAuth Authenticate/Re-authenticate actions for servers configured with `headersHelper`, and HTTP/SSE MCP servers with custom headers being stuck in "needs authentication" after a transient 401
- Fixed MCP servers whose OAuth token response omits `expires_in` requiring re-authentication every hour
- Fixed MCP step-up authorization silently refreshing instead of prompting for re-consent when the server's `insufficient_scope` 403 names a scope the current token already has
- Fixed an unhandled promise rejection when an MCP server's OAuth flow times out or is cancelled
- Fixed MCP OAuth refresh proceeding without its cross-process lock under contention
- Fixed macOS keychain race where a concurrent MCP token refresh could overwrite a freshly-refreshed OAuth token, causing unexpected "Please run /login" prompts
- Fixed OAuth token refresh failing when the server revokes a token before its local expiry time
- Fixed credential save crash on Linux/Windows corrupting `~/.claude/.credentials.json`
- Fixed `/login` having no effect in a session launched with `CLAUDE_CODE_OAUTH_TOKEN` — the env token is now cleared so disk credentials take effect
- Fixed unreadable text in the "new messages" scroll pill and `/plugin` badges
- Fixed plan acceptance dialog offering "auto mode" instead of "bypass permissions" when running with `--dangerously-skip-permissions`
- Fixed agent-type hooks failing with "Messages are required for agent hooks" when configured for events other than `Stop` or `SubagentStop`
- Fixed `prompt` hooks re-firing on tool calls made by an agent-hook verifier subagent
- Fixed `/fork` writing the full parent conversation to disk per fork — now writes a pointer and hydrates on read
- Fixed Alt+K / Alt+X / Alt+^ / Alt+\_ freezing keyboard input
- Fixed connecting to a remote session overwriting your local `model` setting in `~/.claude/settings.json`
- Fixed typeahead showing "No commands match" error when pasting file paths that start with `/`
- Fixed `plugin install` on an already-installed plugin not re-resolving a dependency installed at the wrong version
- Fixed unhandled errors from file watcher on invalid paths or fd exhaustion
- Fixed Remote Control sessions getting archived on transient CCR initialization blips during JWT refresh
- Fixed subagents resumed via `SendMessage` not restoring the explicit `cwd` they were spawned with
]]>

https://code.claude.com/docs/en/changelog#2-1-117
https://code.claude.com/docs/en/changelog#2-1-117
Wed, 22 Apr 2026 00:09:38 GMT
- Forked subagents can now be enabled on external builds by setting `CLAUDE_CODE_FORK_SUBAGENT=1`
- Agent frontmatter `mcpServers` are now loaded for main-thread agent sessions via `--agent`
- Improved `/model`: selections now persist across restarts even when the project pins a different model, and the startup header shows when the active model comes from a project or managed-settings pin
- The `/resume` command now offers to summarize stale, large sessions before re-reading them, matching the existing `--resume` behavior
- Faster startup when both local and claude.ai MCP servers are configured (concurrent connect now default)
- `plugin install` on an already-installed plugin now installs any missing dependencies instead of stopping at "already installed"
- Plugin dependency errors now say "not installed" with an install hint, and `claude plugin marketplace add` now auto-resolves missing dependencies from configured marketplaces
- Managed-settings `blockedMarketplaces` and `strictKnownMarketplaces` are now enforced on plugin install, update, refresh, and autoupdate
- Advisor Tool (experimental): dialog now carries an "experimental" label, learn-more link, and startup notification when enabled; sessions no longer get stuck with "Advisor tool result content could not be processed" errors on every prompt and `/compact`
- The `cleanupPeriodDays` retention sweep now also covers `~/.claude/tasks/`, `~/.claude/shell-snapshots/`, and `~/.claude/backups/`
- OpenTelemetry: `user_prompt` events now include `command_name` and `command_source` for slash commands; `cost.usage`, `token.usage`, `api_request`, and `api_error` now include an `effort` attribute when the model supports effort levels. Custom/MCP command names are redacted unless `OTEL_LOG_TOOL_DETAILS=1` is set
- Native builds on macOS and Linux: the `Glob` and `Grep` tools are replaced by embedded `bfs` and `ugrep` available through the Bash tool — faster searches without a separate tool round-trip (Windows and npm-installed builds unchanged)
- Windows: cached `where.exe` executable lookups per process for faster subprocess launches
- Default effort for Pro/Max subscribers on Opus 4.6 and Sonnet 4.6 is now `high` (was `medium`)
- Fixed Plain-CLI OAuth sessions dying with "Please run /login" when the access token expires mid-session — the token is now refreshed reactively on 401
- Fixed `WebFetch` hanging on very large HTML pages by truncating input before HTML-to-markdown conversion
- Fixed a crash when a proxy returns HTTP 204 No Content — now surfaces a clear error instead of a `TypeError`
- Fixed `/login` having no effect when launched with `CLAUDE_CODE_OAUTH_TOKEN` env var and that token expires
- Fixed prompt-input undo (`Ctrl+_`) doing nothing immediately after typing, and skipping a state on each undo step
- Fixed `NO_PROXY` not being respected for remote API requests when running under Bun
- Fixed rare spurious escape/return triggers when key names arrive as coalesced text over slow connections
- Fixed SDK `reload_plugins` reconnecting all user MCP servers serially
- Fixed Bedrock application-inference-profile requests failing with 400 when backed by Opus 4.7 with thinking disabled
- Fixed MCP `elicitation/create` requests auto-cancelling in print/SDK mode when the server finishes connecting mid-turn
- Fixed subagents running a different model than the main agent incorrectly flagging file reads with a malware warning
- Fixed idle re-render loop when background tasks are present, reducing memory growth on Linux
- [VSCode] Fixed "Manage Plugins" panel breaking when multiple large marketplaces are configured
- Fixed Opus 4.7 sessions showing inflated `/context` percentages and autocompacting too early — Claude Code was computing against a 200K context window instead of Opus 4.7's native 1M
]]>

https://code.claude.com/docs/en/changelog#2-1-116
https://code.claude.com/docs/en/changelog#2-1-116
Mon, 20 Apr 2026 22:27:12 GMT
- `/resume` on large sessions is significantly faster (up to 67% on 40MB+ sessions) and handles sessions with many dead-fork entries more efficiently
- Faster MCP startup when multiple stdio servers are configured; `resources/templates/list` is now deferred to first `@`-mention
- Smoother fullscreen scrolling in VS Code, Cursor, and Windsurf terminals — `/terminal-setup` now configures the editor's scroll sensitivity
- Thinking spinner now shows progress inline ("still thinking", "thinking more", "almost done thinking"), replacing the separate hint row
- `/config` search now matches option values (e.g. searching "vim" finds the Editor mode setting)
- `/doctor` can now be opened while Claude is responding, without waiting for the current turn to finish
- `/reload-plugins` and background plugin auto-update now auto-install missing plugin dependencies from marketplaces you've already added
- Bash tool now surfaces a hint when `gh` commands hit GitHub's API rate limit, so agents can back off instead of retrying
- The Usage tab in Settings now shows your 5-hour and weekly usage immediately and no longer fails when the usage endpoint is rate-limited
- Agent frontmatter `hooks:` now fire when running as a main-thread agent via `--agent`
- Slash command menu now shows "No commands match" when your filter has zero results, instead of disappearing
- Security: sandbox auto-allow no longer bypasses the dangerous-path safety check for `rm`/`rmdir` targeting `/`, `$HOME`, or other critical system directories
- Claude Code and installer now use `https://downloads.claude.ai/claude-code-releases` instead of `https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases`
- Fixed Devanagari and other Indic scripts rendering with broken column alignment in the terminal UI
- Fixed Ctrl+- not triggering undo in terminals using the Kitty keyboard protocol (iTerm2, Ghostty, kitty, WezTerm, Windows Terminal)
- Fixed Cmd+Left/Right not jumping to line start/end in terminals that use the Kitty keyboard protocol (Warp fullscreen, kitty, Ghostty, WezTerm)
- Fixed Ctrl+Z hanging the terminal when Claude Code is launched via a wrapper process (e.g. `npx`, `bun run`)
- Fixed scrollback duplication in inline mode where resizing the terminal or large output bursts would repeat earlier conversation history
- Fixed modal search dialogs overflowing the screen at short terminal heights, hiding the search box and keyboard hints
- Fixed scattered blank cells and disappearing composer chrome in the VS Code integrated terminal during scrolling
- Fixed an intermittent API 400 error related to cache control TTL ordering that could occur when a parallel request completed during request setup
- Fixed `/branch` rejecting conversations with transcripts larger than 50MB
- Fixed `/resume` silently showing an empty conversation on large session files instead of reporting the load error
- Fixed `/plugin` Installed tab showing the same item twice when it appears under Needs attention or Favorites
- Fixed `/update` and `/tui` not working after entering a worktree mid-session
]]>

https://code.claude.com/docs/en/changelog#2-1-114
https://code.claude.com/docs/en/changelog#2-1-114
Sat, 18 Apr 2026 15:03:19 GMT
- Fixed a crash in the permission dialog when an agent teams teammate requested tool permission
]]>

https://code.claude.com/docs/en/changelog#2-1-113
https://code.claude.com/docs/en/changelog#2-1-113
Fri, 17 Apr 2026 21:47:45 GMT
- Changed the CLI to spawn a native Claude Code binary (via a per-platform optional dependency) instead of bundled JavaScript
- Added `sandbox.network.deniedDomains` setting to block specific domains even when a broader `allowedDomains` wildcard would otherwise permit them
- Fullscreen mode: Shift+↑/↓ now scrolls the viewport when extending a selection past the visible edge
- `Ctrl+A` and `Ctrl+E` now move to the start/end of the current logical line in multiline input, matching readline behavior
- Windows: `Ctrl+Backspace` now deletes the previous word
- Long URLs in responses and bash output stay clickable when they wrap across lines (in terminals with OSC 8 hyperlinks)
- Improved `/loop`: pressing Esc now cancels pending wakeups, and wakeups display as "Claude resuming /loop wakeup" for clarity
- `/extra-usage` now works from Remote Control (mobile/web) clients
- Remote Control clients can now query `@`-file autocomplete suggestions
- Improved `/ultrareview`: faster launch with parallelized checks, diffstat in the launch dialog, and animated launching state
- Subagents that stall mid-stream now fail with a clear error after 10 minutes instead of hanging silently
- Bash tool: multi-line commands whose first line is a comment now show the full command in the transcript, closing a UI-spoofing vector
- Running `cd <current-directory> && git …` no longer triggers a permission prompt when the `cd` is a no-op
- Security: on macOS, `/private/{etc,var,tmp,home}` paths are now treated as dangerous removal targets under `Bash(rm:*)` allow rules
- Security: Bash deny rules now match commands wrapped in `env`/`sudo`/`watch`/`ionice`/`setsid` and similar exec wrappers
- Security: `Bash(find:*)` allow rules no longer auto-approve `find -exec`/`-delete`
- Fixed MCP concurrent-call timeout handling where a message for one tool call could silently disarm another call's watchdog
- Fixed Cmd-backspace / `Ctrl+U` to once again delete from the cursor to the start of the line
- Fixed markdown tables breaking when a cell contains an inline code span with a pipe character
- Fixed session recap auto-firing while composing unsent text in the prompt
- Fixed `/copy` "Full response" not aligning markdown table columns for pasting into GitHub, Notion, or Slack
- Fixed messages typed while viewing a running subagent being hidden from its transcript and misattributed to the parent AI
- Fixed Bash `dangerouslyDisableSandbox` running commands outside the sandbox without a permission prompt
- Fixed `/effort auto` confirmation — now says "Effort level set to max" to match the status bar label
- Fixed the "copied N chars" toast overcounting emoji and other multi-code-unit characters
- Fixed `/insights` crashing with `EBUSY` on Windows
- Fixed exit confirmation dialog mislabeling one-shot scheduled tasks as recurring — now shows a countdown
- Fixed slash/@ completion menu not sitting flush against the prompt border in fullscreen mode
- Fixed `CLAUDE_CODE_EXTRA_BODY` `output_config.effort` causing 400 errors on subagent calls to models that don't support effort and on Vertex AI
- Fixed prompt cursor disappearing when `NO_COLOR` is set
- Fixed `ToolSearch` ranking so pasted MCP tool names surface the actual tool instead of description-matching siblings
- Fixed compacting a resumed long-context session failing with "Extra usage is required for long context requests"
- Fixed `plugin install` succeeding when a dependency version conflicts with an already-installed plugin — now reports `range-conflict`
- Fixed "Refine with Ultraplan" not showing the remote session URL in the transcript
- Fixed SDK image content blocks that fail to process crashing the session — now degrade to a text placeholder
- Fixed Remote Control sessions not streaming subagent transcripts
- Fixed Remote Control sessions not being archived when Claude Code exits
- Fixed `thinking.type.enabled is not supported` 400 error when using Opus 4.7 via a Bedrock Application Inference Profile ARN
]]>

https://code.claude.com/docs/en/changelog#2-1-112
https://code.claude.com/docs/en/changelog#2-1-112
Thu, 16 Apr 2026 20:28:49 GMT
- Fixed "claude-opus-4-7 is temporarily unavailable" for auto mode
]]>

https://code.claude.com/docs/en/changelog#2-1-111
https://code.claude.com/docs/en/changelog#2-1-111
Thu, 16 Apr 2026 15:24:50 GMT
- Claude Opus 4.7 xhigh is now available! Use /effort to tune speed vs. intelligence
- Auto mode is now available for Max subscribers when using Opus 4.7
- Added `xhigh` effort level for Opus 4.7, sitting between `high` and `max`. Available via `/effort`, `--effort`, and the model picker; other models fall back to `high`
- `/effort` now opens an interactive slider when called without arguments, with arrow-key navigation between levels and Enter to confirm
- Added "Auto (match terminal)" theme option that matches your terminal's dark/light mode — select it from `/theme`
- Added `/less-permission-prompts` skill — scans transcripts for common read-only Bash and MCP tool calls and proposes a prioritized allowlist for `.claude/settings.json`
- Added `/ultrareview` for running comprehensive code review in the cloud using parallel multi-agent analysis and critique — invoke with no arguments to review your current branch, or `/ultrareview <PR#>` to fetch and review a specific GitHub PR
- Auto mode no longer requires `--enable-auto-mode`
- Windows: PowerShell tool is progressively rolling out. Opt in or out with `CLAUDE_CODE_USE_POWERSHELL_TOOL`. On Linux and macOS, enable with `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` (requires `pwsh` on PATH)
- Read-only bash commands with glob patterns (e.g. `ls *.ts`) and commands starting with `cd <project-dir> &&` no longer trigger a permission prompt
- Suggest the closest matching subcommand when `claude <word>` is invoked with a near-miss typo (e.g. `claude udpate` → "Did you mean `claude update`?")
- Plan files are now named after your prompt (e.g. `fix-auth-race-snug-otter.md`) instead of purely random words
- Improved `/setup-vertex` and `/setup-bedrock` to show the actual `settings.json` path when `CLAUDE_CONFIG_DIR` is set, seed model candidates from existing pins on re-run, and offer a "with 1M context" option for supported models
- `/skills` menu now supports sorting by estimated token count — press `t` to toggle
- `Ctrl+U` now clears the entire input buffer (previously: delete to start of line); press `Ctrl+Y` to restore
- `Ctrl+L` now forces a full screen redraw in addition to clearing the prompt input
- Transcript view footer now shows `[` (dump to scrollback) and `v` (open in editor) shortcuts
- The "+N lines" marker for truncated long pastes is now a full-width rule for easier scanning
- Headless `--output-format stream-json` now includes `plugin_errors` on the init event when plugins are demoted for unsatisfied dependencies
- Added `OTEL_LOG_RAW_API_BODIES` environment variable to emit full API request and response bodies as OpenTelemetry log events for debugging
- Suppressed spurious decompression, network, and transient error messages that could appear in the TUI during normal operation
- Reverted the v2.1.110 cap on non-streaming fallback retries — it traded long waits for more outright failures during API overload
- Fixed terminal display tearing (random characters, drifting input) in iTerm2 + tmux setups when terminal notifications are sent
- Fixed `@` file suggestions re-scanning the entire project on every turn in non-git working directories, and showing only config files in freshly-initialized git repos with no tracked files
- Fixed LSP diagnostics from before an edit appearing after it, causing the model to re-read files it just edited
- Fixed tab-completing `/resume` immediately resuming an arbitrary titled session instead of showing the session picker
- Fixed `/context` grid rendering with extra blank lines between rows
- Fixed `/clear` dropping the session name set by `/rename`, causing statusline output to lose `session_name`
- Improved plugin error handling: dependency errors now distinguish conflicting, invalid, and overly complex version requirements; fixed stale resolved versions after `plugin update`; `plugin install` now recovers from interrupted prior installs
- Fixed Claude calling a non-existent `commit` skill and showing "Unknown skill: commit" for users without a custom `/commit` command
- Fixed 429 rate-limit errors on Bedrock/Vertex/Foundry referencing status.claude.com (it only covers Anthropic-operated providers)
- Fixed feedback surveys appearing back-to-back after dismissing one
- Fixed bare URLs in bash/PowerShell/MCP tool output being unclickable when the terminal wraps them across lines
- Windows: `CLAUDE_ENV_FILE` and SessionStart hook environment files now apply (previously a no-op)
- Windows: permission rules with drive-letter paths are now correctly root-anchored, and paths differing only by drive-letter case are recognized as the same path
]]>

https://code.claude.com/docs/en/changelog#2-1-110
https://code.claude.com/docs/en/changelog#2-1-110
Wed, 15 Apr 2026 22:21:10 GMT
- Added `/tui` command and `tui` setting — run `/tui fullscreen` to switch to flicker-free rendering in the same conversation
- Added push notification tool — Claude can send mobile push notifications when Remote Control and "Push when Claude decides" config are enabled
- Changed `Ctrl+O` to toggle between normal and verbose transcript only; focus view is now toggled separately with the new `/focus` command
- Added `autoScrollEnabled` config to disable conversation auto-scroll in fullscreen mode
- Added option to show Claude's last response as commented context in the `Ctrl+G` external editor (enable via `/config`)
- Improved `/plugin` Installed tab — items needing attention and favorites appear at the top, disabled items are hidden behind a fold, and `f` favorites the selected item
- Improved `/doctor` to warn when an MCP server is defined in multiple config scopes with different endpoints
- `--resume`/`--continue` now resurrects unexpired scheduled tasks
- `/context`, `/exit`, and `/reload-plugins` now work from Remote Control (mobile/web) clients
- Write tool now informs the model when you edit the proposed content in the IDE diff before accepting
- Bash tool now enforces the documented maximum timeout instead of accepting arbitrarily large values
- SDK/headless sessions now read `TRACEPARENT`/`TRACESTATE` from the environment for distributed trace linking
- Session recap is now enabled for users with telemetry disabled (Bedrock, Vertex, Foundry, `DISABLE_TELEMETRY`). Opt out via `/config` or `CLAUDE_CODE_ENABLE_AWAY_SUMMARY=0`.
- Fixed MCP tool calls hanging indefinitely when the server connection drops mid-response on SSE/HTTP transports
- Fixed non-streaming fallback retries causing multi-minute hangs when the API is unreachable
- Fixed session recap, local slash-command output, and other system status lines not appearing in focus mode
- Fixed high CPU usage in fullscreen when text is selected while a tool is running
- Fixed plugin install not honoring dependencies declared in `plugin.json` when the marketplace entry omits them; `/plugin` install now lists auto-installed dependencies
- Fixed skills with `disable-model-invocation: true` failing when invoked via `/<skill>` mid-message
- Fixed `--resume` sometimes showing the first prompt instead of the `/rename` name for sessions still running or exited uncleanly
- Fixed queued messages briefly appearing twice during multi-tool-call turns
- Fixed session cleanup not removing the full session directory including subagent transcripts
- Fixed dropped keystrokes after the CLI relaunches (e.g. `/tui`, provider setup wizards)
- Fixed garbled startup rendering in macOS Terminal.app and other terminals that don't support synchronized output
- Hardened "Open in editor" actions against command injection from untrusted filenames
- Fixed `PermissionRequest` hooks returning `updatedInput` not being re-checked against `permissions.deny` rules; `setMode:'bypassPermissions'` updates now respect `disableBypassPermissionsMode`
- Fixed `PreToolUse` hook `additionalContext` being dropped when the tool call fails
- Fixed stdio MCP servers that print stray non-JSON lines to stdout being disconnected on the first stray line (regression in 2.1.105)
- Fixed headless/SDK session auto-title firing an extra Haiku request when `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` or `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` is set
- Fixed potential excessive memory allocation when piped (non-TTY) Ink output contains a single very wide line
- Fixed `/skills` menu not scrolling when the list overflows the modal in fullscreen mode
- Fixed Remote Control sessions showing a generic error instead of prompting for re-login when the session is too old
- Fixed Remote Control session renames from claude.ai not persisting the title to the local CLI session
]]>

https://code.claude.com/docs/en/changelog#2-1-109
https://code.claude.com/docs/en/changelog#2-1-109
Wed, 15 Apr 2026 07:04:49 GMT
- Improved the extended-thinking indicator with a rotating progress hint
]]>

https://code.claude.com/docs/en/changelog#2-1-108
https://code.claude.com/docs/en/changelog#2-1-108
Tue, 14 Apr 2026 19:29:02 GMT
- Added `ENABLE_PROMPT_CACHING_1H` env var to opt into 1-hour prompt cache TTL on API key, Bedrock, Vertex, and Foundry (`ENABLE_PROMPT_CACHING_1H_BEDROCK` is deprecated but still honored), and `FORCE_PROMPT_CACHING_5M` to force 5-minute TTL
- Added recap feature to provide context when returning to a session, configurable in `/config` and manually invocable with `/recap`; force with `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` if telemetry disabled.
- The model can now discover and invoke built-in slash commands like `/init`, `/review`, and `/security-review` via the Skill tool
- `/undo` is now an alias for `/rewind`
- Improved `/model` to warn before switching models mid-conversation, since the next response re-reads the full history uncached
- Improved `/resume` picker to default to sessions from the current directory; press `Ctrl+A` to show all projects
- Improved error messages: server rate limits are now distinguished from plan usage limits; 5xx/529 errors show a link to status.claude.com; unknown slash commands suggest the closest match
- Reduced memory footprint for file reads, edits, and syntax highlighting by loading language grammars on demand
- Added "verbose" indicator when viewing the detailed transcript (`Ctrl+O`)
- Added a warning at startup when prompt caching is disabled via `DISABLE_PROMPT_CACHING*` environment variables
- Fixed paste not working in the `/login` code prompt (regression in 2.1.105)
- Fixed subscribers who set `DISABLE_TELEMETRY` falling back to 5-minute prompt cache TTL instead of 1 hour
- Fixed Agent tool prompting for permission in auto mode when the safety classifier's transcript exceeded its context window
- Fixed Bash tool producing no output when `CLAUDE_ENV_FILE` (e.g. `~/.zprofile`) ends with a `#` comment line
- Fixed `claude --resume <session-id>` losing the session's custom name and color set via `/rename`
- Fixed session titles showing placeholder example text when the first message is a short greeting
- Fixed terminal escape codes appearing as garbage text in the prompt input after `--teleport`
- Fixed `/feedback` retry: pressing Enter to resubmit after a failure now works without first editing the description
- Fixed `--teleport` and `--resume <id>` precondition errors (e.g. dirty git tree, session not found) exiting silently instead of showing the error message
- Fixed Remote Control session titles set in the web UI being overwritten by auto-generated titles after the third message
- Fixed `--resume` truncating sessions when the transcript contained a self-referencing message
- Fixed transcript write failures (e.g., disk full) being silently dropped instead of being logged
- Fixed diacritical marks (accents, umlauts, cedillas) being dropped from responses when the `language` setting is configured
- Fixed policy-managed plugins never auto-updating when running from a different project than where they were first installed
]]>

https://code.claude.com/docs/en/changelog#2-1-107
https://code.claude.com/docs/en/changelog#2-1-107
Tue, 14 Apr 2026 06:23:41 GMT
- Show thinking hints sooner during long operations
]]>

https://code.claude.com/docs/en/changelog#2-1-105
https://code.claude.com/docs/en/changelog#2-1-105
Mon, 13 Apr 2026 22:00:30 GMT
- Added `path` parameter to the `EnterWorktree` tool to switch into an existing worktree of the current repository
- Added PreCompact hook support: hooks can now block compaction by exiting with code 2 or returning `{"decision":"block"}`
- Added background monitor support for plugins via a top-level `monitors` manifest key that auto-arms at session start or on skill invoke
- `/proactive` is now an alias for `/loop`
- Improved stalled API stream handling: streams now abort after 5 minutes of no data and retry non-streaming instead of hanging indefinitely
- Improved network error messages: connection errors now show a retry message immediately instead of a silent spinner
- Improved file write display: long single-line writes (e.g. minified JSON) are now truncated in the UI instead of paginating across many screens
- Improved `/doctor` layout with status icons; press `f` to have Claude fix reported issues
- Improved `/config` labels and descriptions for clarity
- Improved skill description handling: raised the listing cap from 250 to 1,536 characters and added a startup warning when descriptions are truncated
- Improved `WebFetch` to strip `<style>` and `<script>` contents from fetched pages so CSS-heavy pages no longer exhaust the content budget before reaching actual text
- Improved stale agent worktree cleanup to remove worktrees whose PR was squash-merged instead of keeping them indefinitely
- Improved MCP large-output truncation prompt to give format-specific recipes (e.g. `jq` for JSON, computed Read chunk sizes for text)
- Fixed images attached to queued messages (sent while Claude is working) being dropped
- Fixed screen going blank when the prompt input wraps to a second line in long conversations
- Fixed leading whitespace getting copied when selecting multi-line assistant responses in fullscreen mode
- Fixed leading whitespace being trimmed from assistant messages, breaking ASCII art and indented diagrams
- Fixed garbled bash output when commands print clickable file links (e.g. Python `rich`/`loguru` logging)
- Fixed alt+enter not inserting a newline in terminals using ESC-prefix alt encoding, and Ctrl+J not inserting a newline (regression in 2.1.100)
- Fixed duplicate "Creating worktree" text in EnterWorktree/ExitWorktree tool display
- Fixed queued user prompts disappearing from focus mode
- Fixed one-shot scheduled tasks re-firing repeatedly when the file watcher missed the post-fire cleanup
- Fixed inbound channel notifications being silently dropped after the first message for Team/Enterprise users
- Fixed marketplace plugins with `package.json` and lockfile not having dependencies installed automatically after install/update
- Fixed marketplace auto-update leaving the official marketplace in a broken state when a plugin process holds files open during the update
- Fixed "Resume this session with..." hint not printing on exit after `/resume`, `--worktree`, or `/branch`
- Fixed feedback survey shortcut keys firing when typed at the end of a longer prompt
- Fixed stdio MCP server emitting malformed (non-JSON) output hanging the session instead of failing fast with "Connection closed"
- Fixed MCP tools missing on the first turn of headless/remote-trigger sessions when MCP servers connect asynchronously
- Fixed `/model` picker on AWS Bedrock in non-US regions persisting invalid `us.*` model IDs to `settings.json` when inference profile discovery is still in-flight
- Fixed 429 rate-limit errors showing a raw JSON dump instead of a clean message for API-key, Bedrock, and Vertex users
- Fixed crash on resume when session contains malformed text blocks
- Fixed `/help` dropping the tab bar, Shortcuts heading, and footer at short terminal heights
- Fixed malformed keybinding entry values in `keybindings.json` being silently loaded instead of rejected with a clear error
- Fixed `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` in one project's settings permanently disabling usage metrics for all projects on the machine
- Fixed washed-out 16-color palette when using Ghostty, Kitty, Alacritty, WezTerm, foot, rio, or Contour over SSH/mosh
- Fixed Bash tool suggesting `acceptEdits` permission mode when exiting plan mode would downgrade from a higher permission level
]]>

https://code.claude.com/docs/en/changelog#2-1-101
https://code.claude.com/docs/en/changelog#2-1-101
Fri, 10 Apr 2026 19:27:00 GMT
- Added `/team-onboarding` command to generate a teammate ramp-up guide from your local Claude Code usage
- Added OS CA certificate store trust by default, so enterprise TLS proxies work without extra setup (set `CLAUDE_CODE_CERT_STORE=bundled` to use only bundled CAs)
- `/ultraplan` and other remote-session features now auto-create a default cloud environment instead of requiring web setup first
- Improved brief mode to retry once when Claude responds with plain text instead of a structured message
- Improved focus mode: Claude now writes more self-contained summaries since it knows you only see its final message
- Improved tool-not-available errors to explain why and how to proceed when the model calls a tool that exists but isn't available in the current context
- Improved rate-limit retry messages to show which limit was hit and when it resets instead of an opaque seconds countdown
- Improved refusal error messages to include the API-provided explanation when available
- Improved `claude -p --resume <name>` to accept session titles set via `/rename` or `--name`
- Improved settings resilience: an unrecognized hook event name in `settings.json` no longer causes the entire file to be ignored
- Improved plugin hooks from plugins force-enabled by managed settings to run when `allowManagedHooksOnly` is set
- Improved `/plugin` and `claude plugin update` to show a warning when the marketplace could not be refreshed, instead of silently reporting a stale version
- Improved plan mode to hide the "Refine with Ultraplan" option when the user's org or auth setup can't reach Claude Code on the web
- Improved beta tracing to honor `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS`, and `OTEL_LOG_TOOL_CONTENT`; sensitive span attributes are no longer emitted unless opted in
- Improved SDK `query()` to clean up subprocess and temp files when consumers `break` from `for await` or use `await using`
- Fixed a command injection vulnerability in the POSIX `which` fallback used by LSP binary detection
- Fixed a memory leak where long sessions retained dozens of historical copies of the message list in the virtual scroller
- Fixed `--resume`/`--continue` losing conversation context on large sessions when the loader anchored on a dead-end branch instead of the live conversation
- Fixed `--resume` chain recovery bridging into an unrelated subagent conversation when a subagent message landed near a main-chain write gap
- Fixed a crash on `--resume` when a persisted Edit/Write tool result was missing its `file_path`
- Fixed a hardcoded 5-minute request timeout that aborted slow backends (local LLMs, extended thinking, slow gateways) regardless of `API_TIMEOUT_MS`
- Fixed `permissions.deny` rules not overriding a PreToolUse hook's `permissionDecision: "ask"` — previously the hook could downgrade a deny into a prompt
- Fixed `--setting-sources` without `user` causing background cleanup to ignore `cleanupPeriodDays` and delete conversation history older than 30 days
- Fixed Bedrock SigV4 authentication failing with 403 when `ANTHROPIC_AUTH_TOKEN`, `apiKeyHelper`, or `ANTHROPIC_CUSTOM_HEADERS` set an Authorization header
- Fixed `claude -w <name>` failing with "already exists" after a previous session's worktree cleanup left a stale directory
- Fixed subagents not inheriting MCP tools from dynamically-injected servers
- Fixed sub-agents running in isolated worktrees being denied Read/Edit access to files inside their own worktree
- Fixed sandboxed Bash commands failing with `mktemp: No such file or directory` after a fresh boot
- Fixed `claude mcp serve` tool calls failing with "Tool execution failed" in MCP clients that validate `outputSchema`
- Fixed `RemoteTrigger` tool's `run` action sending an empty body and being rejected by the server
- Fixed several `/resume` picker issues: narrow default view hiding sessions from other projects, unreachable preview on Windows Terminal, incorrect cwd in worktrees, session-not-found errors not surfacing in stderr, terminal title not being set, and resume hint overlapping the prompt input
- Fixed Grep tool ENOENT when the embedded ripgrep binary path becomes stale (VS Code extension auto-update, macOS App Translocation); now falls back to system `rg` and self-heals mid-session
- Fixed `/btw` writing a copy of the entire conversation to disk on every use
- Fixed `/context` Free space and Messages breakdown disagreeing with the header percentage
- Fixed several plugin issues: slash commands resolving to the wrong plugin with duplicate `name:` frontmatter, `/plugin update` failing with `ENAMETOOLONG`, Discover showing already-installed plugins, directory-source plugins loading from a stale version cache, and skills not honoring `context: fork` and `agent` frontmatter fields
- Fixed the `/mcp` menu offering OAuth-specific actions for MCP servers configured with `headersHelper`; Reconnect is now offered instead to re-invoke the helper script
- Fixed `ctrl+]`, `ctrl+\`, and `ctrl+^` keybindings not firing in terminals that send raw C0 control bytes (Terminal.app, default iTerm2, xterm)
- Fixed `/login` OAuth URL rendering with padding that prevented clean mouse selection
- Fixed rendering issues: flicker in non-fullscreen mode when content above the visible area changed, terminal scrollback being wiped during long sessions in non-fullscreen mode, and mouse-scroll escape sequences occasionally leaking into the prompt as text
- Fixed crash when `settings.json` env values are numbers instead of strings
- Fixed in-app settings writes (e.g. `/add-dir --remember`, `/config`) not refreshing the in-memory snapshot, preventing removed directories from being revoked mid-session
- Fixed custom keybindings (`~/.claude/keybindings.json`) not loading on Bedrock, Vertex, and other third-party providers
- Fixed `claude --continue -p` not correctly continuing sessions created by `-p` or the SDK
- Fixed several Remote Control issues: worktrees removed on session crash, connection failures not persisting in the transcript, spurious "Disconnected" indicator in brief mode for local sessions, and `/remote-control` failing over SSH when only `CLAUDE_CODE_ORGANIZATION_UUID` is set
- Fixed `/insights` sometimes omitting the report file link from its response
- [VSCode] Fixed the file attachment below the chat input not clearing when the last editor tab is closed
]]>

https://code.claude.com/docs/en/changelog#2-1-98
https://code.claude.com/docs/en/changelog#2-1-98
Thu, 09 Apr 2026 19:57:48 GMT
- Added interactive Google Vertex AI setup wizard accessible from the login screen when selecting "3rd-party platform", guiding you through GCP authentication, project and region configuration, credential verification, and model pinning
- Added `CLAUDE_CODE_PERFORCE_MODE` env var: when set, Edit/Write/NotebookEdit fail on read-only files with a `p4 edit` hint instead of silently overwriting them
- Added Monitor tool for streaming events from background scripts
- Added subprocess sandboxing with PID namespace isolation on Linux when `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` is set, and `CLAUDE_CODE_SCRIPT_CAPS` env var to limit per-session script invocations
- Added `--exclude-dynamic-system-prompt-sections` flag to print mode for improved cross-user prompt caching
- Added `workspace.git_worktree` to the status line JSON input, set whenever the current directory is inside a linked git worktree
- Added W3C `TRACEPARENT` env var to Bash tool subprocesses when OTEL tracing is enabled, so child-process spans correctly parent to Claude Code's trace tree
- LSP: Claude Code now identifies itself to language servers via `clientInfo` in the initialize request
- Fixed a Bash tool permission bypass where a backslash-escaped flag could be auto-allowed as read-only and lead to arbitrary code execution
- Fixed compound Bash commands bypassing forced permission prompts for safety checks and explicit ask rules in auto and bypass-permissions modes
- Fixed read-only commands with env-var prefixes not prompting unless the var is known-safe (`LANG`, `TZ`, `NO_COLOR`, etc.)
- Fixed redirects to `/dev/tcp/...` or `/dev/udp/...` not prompting instead of auto-allowing
- Fixed stalled streaming responses timing out instead of falling back to non-streaming mode
- Fixed 429 retries burning all attempts in ~13s when the server returns a small `Retry-After` — exponential backoff now applies as a minimum
- Fixed MCP OAuth `oauth.authServerMetadataUrl` config override not being honored on token refresh after restart, affecting ADFS and similar IdPs
- Fixed capital letters being dropped to lowercase on xterm and VS Code integrated terminal when the kitty keyboard protocol is active
- Fixed macOS text replacements deleting the trigger word instead of inserting the substitution
- Fixed `--dangerously-skip-permissions` being silently downgraded to accept-edits mode after approving a write to a protected path via Bash
- Fixed managed-settings allow rules remaining active after an admin removed them, until process restart
- Fixed `permissions.additionalDirectories` changes not applying mid-session — removed directories lose access immediately and added ones work without restart
- Fixed removing a directory from `additionalDirectories` revoking access to the same directory passed via `--add-dir`
- Fixed `Bash(cmd:*)` and `Bash(git commit *)` wildcard permission rules failing to match commands with extra spaces or tabs
- Fixed `Bash(...)` deny rules being downgraded to a prompt for piped commands that mix `cd` with other segments
- Fixed false Bash permission prompts for `cut -d /`, `paste -d /`, `column -s /`, `awk '{print $1}' file`, and filenames containing `%`
- Fixed permission rules with names matching JavaScript prototype properties (e.g. `toString`) causing `settings.json` to be silently ignored
- Fixed agent team members not inheriting the leader's permission mode when using `--dangerously-skip-permissions`
- Fixed a crash in fullscreen mode when hovering over MCP tool results
- Fixed copying wrapped URLs in fullscreen mode inserting spaces at line breaks
- Fixed file-edit diffs disappearing from the UI on `--resume` when the edited file was larger than 10KB
- Fixed several `/resume` picker issues: `--resume <name>` opening uneditable, filter reload wiping search state, empty list swallowing arrow keys, cross-project staleness, and transient task-status text replacing conversation summaries
- Fixed `/export` not honoring absolute paths and `~`, and silently rewriting user-supplied extensions to `.txt`
- Fixed `/effort max` being denied for unknown or future model IDs
- Fixed slash command picker breaking when a plugin's frontmatter `name` is a YAML boolean keyword
- Fixed rate-limit upsell text being hidden after message remounts
- Fixed MCP tools with `_meta["anthropic/maxResultSizeChars"]` not bypassing the token-based persist layer
- Fixed voice mode leaking dozens of space characters into the input when re-holding the push-to-talk key while the previous transcript is still processing
- Fixed `DISABLE_AUTOUPDATER` not fully suppressing the npm registry version check and symlink modification on npm-based installs
- Fixed a memory leak where Remote Control permission handler entries were retained for the lifetime of the session
- Fixed background subagents that fail with an error not reporting partial progress to the parent agent
- Fixed prompt-type Stop/SubagentStop hooks failing on long sessions, and hook evaluator API errors showing "JSON validation failed" instead of the real message
- Fixed feedback survey rendering when dismissed
- Fixed Bash `grep -f FILE` / `rg -f FILE` not prompting when reading a pattern file outside the working directory
- Fixed stale subagent worktree cleanup removing worktrees that contain untracked files
- Fixed `sandbox.network.allowMachLookup` not taking effect on macOS
- Improved `/resume` filter hint labels and added project/worktree/branch names in the filter indicator
- Improved footer indicators (Focus, notifications) to stay on the mode-indicator row instead of wrapping at narrow terminal widths
- Improved `/agents` with a tabbed layout: a Running tab shows live subagents, and the Library tab adds Run agent and View running instance actions
- Improved `/reload-plugins` to pick up plugin-provided skills without requiring a restart
- Improved Accept Edits mode to auto-approve filesystem commands prefixed with safe env vars or process wrappers
- Improved Vim mode: `j`/`k` in NORMAL mode now navigate history and select the footer pill at the input boundary
- Improved hook errors in the transcript to include the first line of stderr for self-diagnosis without `--debug`
- Improved OTEL tracing: interaction spans now correctly wrap full turns under concurrent SDK calls, and headless turns end spans per-turn
- Improved transcript entries to carry final token usage instead of streaming placeholders
- Updated the `/claude-api` skill to cover Managed Agents alongside Claude API
- [VSCode] Fixed false-positive "requires git-bash" error on Windows when `CLAUDE_CODE_GIT_BASH_PATH` is set or Git is installed at a default location
- Fixed `CLAUDE_CODE_MAX_CONTEXT_TOKENS` to honor `DISABLE_COMPACT` when it is set.
- Dropped `/compact` hints when `DISABLE_COMPACT` is set.
]]>

https://code.claude.com/docs/en/changelog#2-1-97
https://code.claude.com/docs/en/changelog#2-1-97
Wed, 08 Apr 2026 22:26:51 GMT
- Added focus view toggle (`Ctrl+O`) in `NO_FLICKER` mode showing prompt, one-line tool summary with edit diffstats, and final response
- Added `refreshInterval` status line setting to re-run the status line command every N seconds
- Added `workspace.git_worktree` to the status line JSON input, set when the current directory is inside a linked git worktree
- Added `● N running` indicator in `/agents` next to agent types with live subagent instances
- Added syntax highlighting for Cedar policy files (`.cedar`, `.cedarpolicy`)
- Fixed `--dangerously-skip-permissions` being silently downgraded to accept-edits mode after approving a write to a protected path
- Fixed and hardened Bash tool permissions, tightening checks around env-var prefixes and network redirects, and reducing false prompts on common commands
- Fixed permission rules with names matching JavaScript prototype properties (e.g. `toString`) causing `settings.json` to be silently ignored
- Fixed managed-settings allow rules remaining active after an admin removed them until process restart
- Fixed `permissions.additionalDirectories` changes in settings not applying mid-session
- Fixed removing a directory from `settings.permissions.additionalDirectories` revoking access to the same directory passed via `--add-dir`
- Fixed MCP HTTP/SSE connections accumulating ~50 MB/hr of unreleased buffers when servers reconnect
- Fixed MCP OAuth `oauth.authServerMetadataUrl` not being honored on token refresh after restart, fixing ADFS and similar IdPs
- Fixed 429 retries burning all attempts in ~13 seconds when the server returns a small `Retry-After` — exponential backoff now applies as a minimum
- Fixed rate-limit upgrade options disappearing after context compaction
- Fixed several `/resume` picker issues: `--resume <name>` opening uneditable, Ctrl+A reload wiping search, empty list swallowing navigation, task-status text replacing conversation summary, and cross-project staleness
- Fixed file-edit diffs disappearing on `--resume` when the edited file was larger than 10KB
- Fixed `--resume` cache misses and lost mid-turn input from attachment messages not being saved to the transcript
- Fixed messages typed while Claude is working not being persisted to the transcript
- Fixed prompt-type `Stop`/`SubagentStop` hooks failing on long sessions, and hook evaluator API errors displaying "JSON validation failed" instead of the actual message
- Fixed subagents with worktree isolation or `cwd:` override leaking their working directory back to the parent session's Bash tool
- Fixed compaction writing duplicate multi-MB subagent transcript files on prompt-too-long retries
- Fixed `claude plugin update` reporting "already at the latest version" for git-based marketplace plugins when the remote had newer commits
- Fixed slash command picker breaking when a plugin's frontmatter `name` is a YAML boolean keyword
- Fixed copying wrapped URLs in `NO_FLICKER` mode inserting spaces at line breaks
- Fixed scroll rendering artifacts in `NO_FLICKER` mode when running inside zellij
- Fixed a crash in `NO_FLICKER` mode when hovering over MCP tool results
- Fixed a `NO_FLICKER` mode memory leak where API retries left stale streaming state
- Fixed slow mouse-wheel scrolling in `NO_FLICKER` mode on Windows Terminal
- Fixed custom status line not displaying in `NO_FLICKER` mode on terminals shorter than 24 rows
- Fixed Shift+Enter and Alt/Cmd+arrow shortcuts not working in Warp with `NO_FLICKER` mode
- Fixed Korean/Japanese/Unicode text becoming garbled when copied in no-flicker mode on Windows
- Fixed Bedrock SigV4 authentication failing when `AWS_BEARER_TOKEN_BEDROCK` or `ANTHROPIC_BEDROCK_BASE_URL` are set to empty strings (as GitHub Actions does for unset inputs)
- Improved Accept Edits mode to auto-approve filesystem commands prefixed with safe env vars or process wrappers (e.g. `LANG=C rm foo`, `timeout 5 mkdir out`)
- Improved auto mode and bypass-permissions mode to auto-approve sandbox network access prompts
- Improved sandbox: `sandbox.network.allowMachLookup` now takes effect on macOS
- Improved image handling: pasted and attached images are now compressed to the same token budget as images read via the Read tool
- Improved slash command and `@`-mention completion to trigger after CJK sentence punctuation, so Japanese/Chinese input no longer requires a space before `/` or `@`
- Improved Bridge sessions to show the local git repo, branch, and working directory on the claude.ai session card
- Improved footer layout: indicators (Focus, notifications) now stay on the mode-indicator row instead of wrapping below
- Improved context-low warning to show as a transient footer notification instead of a persistent row
- Improved markdown blockquotes to show a continuous left bar across wrapped lines
- Improved session transcript size by skipping empty hook entries and capping stored pre-edit file copies
- Improved transcript accuracy: per-block entries now carry the final token usage instead of the streaming placeholder
- Improved Bash tool OTEL tracing: subprocesses now inherit a W3C `TRACEPARENT` env var when tracing is enabled
- Updated `/claude-api` skill to cover Managed Agents alongside the Claude API
]]>
