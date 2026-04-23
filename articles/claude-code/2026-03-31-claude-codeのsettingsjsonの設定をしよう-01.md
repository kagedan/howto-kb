---
id: "2026-03-31-claude-codeのsettingsjsonの設定をしよう-01"
title: "Claude Codeのsettings.jsonの設定をしよう"
url: "https://qiita.com/makoto-ogata@github/items/641a26f0d5d40aa1c0c4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

## 前提

Claudeを今月から本格的に使いはじめ、仕事でもプライベートの両方でClaude使ってますが実際のところ「使いこなしている」とは到底言えません。  
どの程度の知識レベルかというと、大体の設定は「CLAUDE.md」書いて追加で「SKILL.md」とか書いておけばいいんでしょ？というレベルです。

## settings.jsonの役割

settings.jsonの役割は「何ができるかを制御する（権限・動作）」がメインで、何かをお願いするファイルではないということです。  
何をするのか「指示」するのはCLAUDE.mdに書いておきましょう。

## やれること

めちゃくちゃ多いので、公式見たほうが早いです。

設定の中には権限を付与できるのもあるので、権限設定も併せて見ておくと良いと思います。  
最初は下の表の3つを抑えていればだいたいは大丈夫だと思っています。

| キー | 説明 |
| --- | --- |
| Allow | 確認なしで自動実行してOK |
| Ask | 実行前に確認を求める |
| Deny | 絶対に実行させない |

## とりあえず組んでみた

Claudeに直接壁打ちしながらSettings.jsonを作りました。

あくまでも自分の設定です。PCのglobalな設定なので、プロジェクトに置く場合はまた違った設定が必要になってくると思います。

settings.json

```
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git checkout *)",
      "Bash(git branch *)",
      "Bash(gh repo view *)",
      "Bash(gh pr list *)",
      "Bash(gh pr view *)",
      "Bash(gh issue list *)",
      "Bash(gh issue view *)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(rm *)",
      "Bash(sudo *)"
    ],
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(./secrets/**)",
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)"
    ]
  },
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "70"
  },
  "showTurnDuration": true,
  "spinnerTipsEnabled": false,
  "langage": "japanese"
}
```

### ざっくりと説明

#### permissions

gitやghの閲覧するだけのコマンドはいちいち確認をされるのは面倒なので`allow`にしています。  
pushや削除のrmコマンドは許可を取るようにしています。

#### env CLAUDE\_AUTOCOMPACT\_PCT\_OVERRIDE

コンテキストウィンドウが70%埋まったら自動で圧縮する設定です。  
デフォルトは95%で早めに圧縮することで、長いセッションでも文脈が詰まりにくくなるようです。  
60〜75%が使いやすいとされているみたいです。  
（そして100％になったら強制的に落ちるとのことでした）

#### showTurnDuration

Claudeが1回の処理にかかった時間を表示する設定。  
どの操作にどれくらいかかったか振り返れたりします。

#### spinnerTipsEnabled

Claudeが処理中に表示されるローディングアニメーションのTips（豆知識）をオフにする設定です。

#### langage

言語設定です。  
settings.jsonを知る前はCLAUDE.mdに「日本語で返答してください」と書いてました。

## 感想

プライベートで使っているclaudeの`.claude/settings.json`は何も書かれていない状態だったので、色々と無駄な時間があったなぁと思いました。  
せっかくの強力なツールなので、上手に使えるようになりたいですね。

## 参考
