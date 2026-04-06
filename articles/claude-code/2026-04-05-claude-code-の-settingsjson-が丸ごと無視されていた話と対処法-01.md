---
id: "2026-04-05-claude-code-の-settingsjson-が丸ごと無視されていた話と対処法-01"
title: "Claude Code の settings.json が丸ごと無視されていた話と対処法"
url: "https://qiita.com/gumiyuya/items/645484ec42b221b719ef"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## はじめに

気づいたきっかけは、Claude Codeの `settings.json` にsandboxのデフォルト有効設定を書いたことでした。
`~/.claude/settings.json` に以下の設定を追加して起動し `/sandbox` で確認するも反映されず、
よく見ると `"model": "claude-opus-4-6"` すら効いておらず Sonnet 4.5 で起動していました。

```
{
  // 元々書いてた
  "model": "claude-opus-4-6",

  // ~略~

  // 追記
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true
  }
}
```

<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3718885/12040ea0-3adb-4428-b263-a0a0f468f8ef.png" width="50%">

確信はありま
