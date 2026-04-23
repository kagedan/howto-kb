---
id: "2026-03-19-windowsでdockergemini-clieverything-claude-code-ski-01"
title: "WindowsでDocker×Gemini CLI×everything-claude-code Skillsを一気に動かす"
url: "https://zenn.dev/kafka2306/articles/cd6f21d4a26bdd"
source: "zenn"
category: "claude-code"
tags: ["Gemini", "zenn"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

## 1) Docker + Node + Gemini CLI を一気に入れる（PowerShell）

```
winget install -e --id Docker.DockerDesktop
winget install -e --id OpenJS.NodeJS.LTS

Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Start-Sleep -Seconds 10
net start com.docker.service

npm install -g @google/gemini-cli
```

## 2) 動作確認（最小）

```
docker version
docker run --rm node:24-alpine node -v
docker run --rm node:24-alpine npm -v
node -v
npm -v
gemini --version
```

## 3) ECC skills を最も効率的に一括導入（確認自動 `y`）

```
$repo = "https://github.com/affaan-m/everything-claude-code.git"
$skills = @(
  "search-first",
  "security-review",
  "strategic-compact",
  "continuous-learning-v2",
  "frontend-patterns",
  "coding-standards",
  "ai-first-engineering",
  "blueprint",
  "api-design",
  "agentic-engineering",
  "ai-regression-testing",
  "backend-patterns",
  "e2e-testing",
  "eval-harness",
  "prompt-optimizer",
  "security-scan"
)

foreach ($s in $skills) {
  cmd /c "echo y| gemini skills install $repo --path skills/$s"
}
```
