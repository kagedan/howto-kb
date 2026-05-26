---
id: "2026-05-25-claude-code-の-hooks-burnttoast-で-windows-通知を出す-01"
title: "Claude Code の hooks + BurntToast で Windows 通知を出す"
url: "https://qiita.com/PaoJaPao/items/ea62930ea13b8912e118"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "qiita"]
date_published: "2026-05-25"
date_collected: "2026-05-26"
summary_by: "auto-rss"
query: ""
---

Claude Code に大きめの作業をお願いして別作業していると...

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2526379/93eced02-f2bb-4d5f-a5f8-4d193b44f4a8.png)

ツールの許可待ちで止まってしまうの悲しいですよね。
いくらツール許可をしていても、どこかに漏れがあってこの文言が表示されてしまいます。。

そこで、Claude Code の Notification hook と PowerShell の BurntToast を使って、Windows の通知を出す設定を作ります。

## BurntToast とは？

BurntToast は、PowerShell から Windows のトースト通知を出せるモジュールです。

https://github.com/Windos/BurntToast

### まずはインストール

PowerShellを起動して

```powershell
Install-Module -Name BurntToast -Scope CurrentUser
```

同じくPowerShellで動作確認。

```powershell
Import-Module BurntToast

New-BurntToastNotification -Text "Claude Code", "通知テスト"
```

通知が出れば OK

<details>
<summary>こんな感じ</summary>

![Screenshot 2026-05-25 165239.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2526379/ab44c448-4b7b-44f5-8017-a0350638e218.png)


</details>

## Claude Code hooks を設定する

WSL側の`~/.claude/settings.json` に以下を設定します。

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "pwsh.exe -NoProfile -Command \"Import-Module BurntToast; New-BurntToastNotification -Text 'Claude Codeが許可待ちです。', '$(pwd)'\""
          }
        ]
      },
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "pwsh.exe -NoProfile -Command \"Import-Module BurntToast; New-BurntToastNotification -Text 'Claude Codeの出力が終わったらしい。', '$(pwd)'\""
          }
        ]
      }
    ]
  }
}
```

この設定で下記タイミングに通知が走ります。

- permission_prompt
Claude Code がツール使用の許可待ちになった時
- idle_prompt
Claude Code が入力待ち(出力完了)になった時

## 動作確認

Claude Code にファイル変更などの作業を依頼してみてください。

ツールの許可待ち・実行完了後のプロンプト入力待ちで、Windows通知が表示されれば成功です。
※通知までに少しラグがあります

## 補足
- PowerShell 7以降を使っている場合は `powershell.exe` を `pwsh.exe` に変更して下さい
- 通知文に $(pwd) を追加すると、どのプロジェクトからの通知か分かりやすくなります
    例：
    ```powershell
    New-BurntToastNotification -Text 'Claude Code needs your permission. `n$(pwd)'
    ```
- 通知されるまでの間にツール使用の許可・プロンプト実行をすると通知は実行されません

## おわりに

実は公式にWindows向けのHooks設定は記載されてます。

https://code.claude.com/docs/ja/hooks-guide#windows-powershell

ただ、こんな感じのモーダルです。うん
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2526379/7f4c6daf-a80e-4dd3-a134-7cbd5ea6f38e.png)

BurntToastの方が`-AppIcon`でアイコンを追加出来たり、Windowsの通知に溜まってくれるので非常に嬉しいなと思って使用しました。

## 参考文献

https://github.com/Windos/BurntToast

https://code.claude.com/docs/ja/hooks-guide
