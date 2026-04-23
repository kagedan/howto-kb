---
id: "2026-03-18-claude-code-を-slack-連携して自動で-github-issue-を起票する-01"
title: "Claude Code を Slack 連携して自動で GitHub Issue を起票する"
url: "https://zenn.dev/my_vision/articles/da7f38744f31a5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

こんにちは！株式会社MyVisionでエンジニアをしている [@sukechannnn](https://x.com/sukechannnn) です。

Claude Code の Slack 連携便利ですよね。Slackのメッセージに返信する形でGitHub Issueを起票したり、Issueの内容をそのまま開発させたりと、活用の幅が広がります。

ただ、Claude Code on the Web (Slack連携の裏で動くやつ) はデフォルトでghコマンドが入っておらず、自分でインストール & 設定をする必要があります。

この記事ではそのやり方を紹介します。

## Slack に Claude アプリをインストール

これは以下のドキュメント通りに進めればできます。

<https://code.claude.com/docs/ja/slack>

## Claude Code on the Web で gh コマンドを使えるようにする

まずは、Claude Code on the Web のセッションを立ち上げた時に、ghコマンドをインストールしてPATHを通すようにします。

以下のような Shell を `.claude/hooks/gh-setup.sh` に配置し、

.claude/hooks/gh-setup.sh

.claude/hooks/gh-setup.sh

```
#!/bin/bash

# SessionStartフック: リモート環境向けにGitHub CLIを自動インストールするためのスクリプト
# このスクリプトは Claude Code on the Web 上で動作している場合に gh CLI をインストールします

LOG_PREFIX="[gh-setup]"
TEMP_DIR=""

log() {
    echo "$LOG_PREFIX $1" >&2
}

cleanup() {
    [ -n "$TEMP_DIR" ] && rm -rf "$TEMP_DIR"
}

trap 'cleanup' EXIT

persist_path() {
    local dir="$1"
    if [[ ":$PATH:" != *":$dir:"* ]]; then
        export PATH="$dir:$PATH"
    fi
    if [ -n "$CLAUDE_ENV_FILE" ] && ! grep -qF "$dir" "$CLAUDE_ENV_FILE" 2>/dev/null; then
        echo "export PATH=\"$dir:\$PATH\"" >> "$CLAUDE_ENV_FILE"
        log "PATH ($dir) persisted to CLAUDE_ENV_FILE"
    fi
}

# Claude Code on the Web のときだけ後続の処理を行う
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
    log "Not a remote session, skipping gh setup"
    exit 0
fi

log "Remote session detected, checking gh CLI..."

# gh が既にインストール済みで動作するか確認
if command -v gh &>/dev/null && gh --version &>/dev/null; then
    log "gh CLI already available: $(gh --version | head -1)"
    persist_path "$(dirname "$(command -v gh)")"
    exit 0
fi

# ローカル bin ディレクトリの準備
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

# ローカル bin に gh が存在し動作するか確認
if [ -x "$LOCAL_BIN/gh" ] && "$LOCAL_BIN/gh" --version &>/dev/null; then
    log "gh found in $LOCAL_BIN"
    persist_path "$LOCAL_BIN"
    exit 0
fi

log "Installing gh CLI to $LOCAL_BIN..."

TEMP_DIR=$(mktemp -d)

# アーキテクチャの検出
ARCH=$(uname -m)
case "$ARCH" in
    x86_64)  GH_ARCH="amd64" ;;
    aarch64|arm64) GH_ARCH="arm64" ;;
    *)
        log "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

# gh CLI の最新バージョンをダウンロード・インストール
GH_VERSION=""
for attempt in 1 2 3 4; do
    GH_VERSION=$(curl -sL --connect-timeout 10 --max-time 30 \
        "https://api.github.com/repos/cli/cli/releases/latest" \
        | grep -o '"tag_name": *"v[^"]*"' | head -1 | sed 's/.*"v\([^"]*\)".*/\1/')
    [ -n "$GH_VERSION" ] && break
    log "Attempt $attempt failed to fetch gh version, retrying in ${attempt}s..."
    sleep "$attempt"
done
[ -z "$GH_VERSION" ] && { log "Failed to fetch latest gh version after 4 attempts"; exit 1; }

GH_TARBALL="gh_${GH_VERSION}_linux_${GH_ARCH}.tar.gz"
GH_URL="https://github.com/cli/cli/releases/download/v${GH_VERSION}/${GH_TARBALL}"

log "Downloading gh v${GH_VERSION} for ${GH_ARCH}..."
if ! curl -sfL "$GH_URL" -o "$TEMP_DIR/$GH_TARBALL"; then
    log "Failed to download gh CLI"
    exit 1
fi

log "Extracting..."
if ! tar -xzf "$TEMP_DIR/$GH_TARBALL" -C "$TEMP_DIR"; then
    log "Failed to extract gh CLI"
    exit 1
fi

# バイナリをローカル bin に配置
GH_BIN=$(find "$TEMP_DIR" -name gh -type f -path "*/bin/gh" | head -1)
[ -z "$GH_BIN" ] && { log "gh binary not found in archive"; exit 1; }
if ! mv "$GH_BIN" "$LOCAL_BIN/gh" || ! chmod +x "$LOCAL_BIN/gh"; then
    log "Failed to install gh CLI"
    exit 1
fi

persist_path "$LOCAL_BIN"

if "$LOCAL_BIN/gh" --version &>/dev/null; then
    log "gh CLI installed successfully: $($LOCAL_BIN/gh --version | head -1)"
else
    log "gh CLI was installed but failed to run"
    exit 1
fi
```

`.claude/settings.json` に次の設定を追記します。

```
...
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "./.claude/hooks/gh-setup.sh"
          }
        ]
      }
    ]
  }
...
```

こうすることで、Claude Code on the Web のセッションを立ち上げたタイミングでghコマンドがインストールされ、利用可能になります。

ここまでの変更はリポジトリに対してコミットするので、一度設定すればOKです。

Shellスクリプトの実装ポイントは以下の通りです。

* CLAUDE\_CODE\_REMOTE による環境判定
  + Claude Code on the Web のみで動作するように `CLAUDE_CODE_REMOTE=true` でガード
* CLAUDE\_ENV\_FILE による PATH の永続化
  + hook 内で export PATH=... してもセッションに反映されなかったので、CLAUDE\_ENV\_FILE に書き込むことでセッションに PATH を伝播

ちなみに、hooks で実行したスクリプトが exit 0 以外で終了しても、Claude のセッションはちゃんと立ち上がるようです。

### GITHUB\_TOKEN の設定

ghコマンドで GitHub API を叩けるように、各自が `GITHUB_TOKEN` を設定する必要があります。

#### GITHUB\_TOKEN の設定手順

##### 1. Personal Access Token を生成する

[Fine-grained personal access tokens](https://github.com/settings/personal-access-tokens/new) からトークンを生成します。  
必要な Permissions / Repository Access は以下の通りです。

* Permissions / Repository Access:
  + Contents: Read and write
  + Issues: Read and write
  + Pull Requests: Read and write
  + Metadata: Read-only（自動付与）

##### 2. Claude Code on the Web のカスタム環境に設定する

1. [Claude Code on the Web](https://claude.ai/code) を開く
2. コンソールの右下の環境選択ボタンをクリックし、「クラウド環境」の「デフォルト」もしくはカスタム環境の設定を開く（場所が分かりにくい）  
   ![環境選択ボタン](https://static.zenn.studio/user-upload/1f03cdc82e40-20260318.png)
3. 環境変数に以下を追加する

```
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxx
```

![環境変数の設定画面](https://static.zenn.studio/user-upload/874de0d33dd4-20260318.png)

ここまでで、セッション開始時に `gh` CLI が自動インストールされ、`GITHUB_TOKEN` を使って GitHub API にアクセスできるようになります。

## 使ってみる

実際に使ってみた様子です。便利ですね〜。

![SlackでClaudeに依頼](https://static.zenn.studio/user-upload/9ef8e9d0b193-20260318.png)

![](https://static.zenn.studio/user-upload/148fa244773b-20260318.png)

## 参考記事
