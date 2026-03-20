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

1) Docker + Node + Gemini CLI を一気に入れる（PowerShell）
winget install -e --id Docker.DockerDesktop
winget install -e --id OpenJS.NodeJS.LTS

Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Start-Sleep -Seconds 10
net start com.docker.service

npm install -g @google/gemini-cli

 2) ...
