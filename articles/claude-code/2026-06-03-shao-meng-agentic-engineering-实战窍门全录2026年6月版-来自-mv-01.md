---
id: "2026-06-03-shao-meng-agentic-engineering-实战窍门全录2026年6月版-来自-mv-01"
title: "@shao__meng: Agentic Engineering 实战窍门全录（2026年6月版） 来自 @mvanhorn 的分享 👏🏻，他三"
url: "https://x.com/shao__meng/status/2061974983094755575"
source: "x"
category: "claude-code"
tags: ["prompt-engineering", "AI-agent", "LLM", "Python", "x"]
date_published: "2026-06-03"
date_collected: "2026-06-03"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Agentic Engineering 实战窍门全录（2026年6月版）

来自 @mvanhorn 的分享 👏🏻，他三个月内从「高中后没发布过有价值软件」到 last30days（27K stars）、Printing Press、Agent Cookie，以及对 Python、Go 等主流项目的实质贡献（结尾列出作者推荐全部工具）

看看 Agentic Engineering 给软件开发带来了什么变化
· 80% 编码，20% 规划 -> 规划交给 agent，人做方向与品味
· 人在键盘前执行 -> 人做 signal（信号），agent 做 volume（产出量）
· IDE 是中心 -> 终端 + plan.md + 语音是中心

方法论骨架：Research → Plan → Work
/last30days（社区现况调研）
  ↓
/ce-plan（结构化 plan.md，含验收标准）
  ↓
/ce-work（机械执行，可跨 session 续跑）
  ↓
Human Signal（品味、取舍、纠偏）

Compound Engineering 是使这套循环落地的插件（/ce-plan、/ce-work、/ce-brainstorm）。plan.md 的价值不在于给人读，而在于约束 agent 不偷懒——有研究、有方案、有 checkbox，执行才完整。

# 22 条 Hack 的精简归类

一、规划层（最重要）
1. 有想法立刻 /ce-plan，不先想、不先写代码；模糊时用 /ce-brainstorm 再 plan。
2. plan 给人看，但作者几乎不读——plan 是 agent 的作业；人只 skim 标题，有疑问 inline 问（TLDR / eli5 / why this approach）。
3. 非工程任务同样适用：「make a plan for the plan」——先规划如何产出 deliverable，再执行，避免 LLM 直接写成品时偷工减料。
4. plan.md 也是协作介质：Proof 把 plan 变成可评论文档，非终端用户也能 review。

二、执行与并行
5. cmux 多 tab（4–6 个）：plan 一个、build 一个、测 bug 一个……research 和 build 并行，cycle 回来第一个已完。
6. 新 terminal tab 默认进 Claude/Codex，不是 shell——降低开 session 成本。
7. YOLO 权限：bypassPermissions + skipDangerousModePermissionPrompt；多 session 无法逐条点确认。配合 Stop hook 音效，知道哪个 session 结束。
8. Claude 规划 + Codex 构建：Claude xhigh 关 fast mode；Codex xhigh 开 fast mode。通过 IDE 扩展、/ce-work --codex、Printing Press 委托，不必切 CLI。

三、输入方式
9. 语音优先：Monologue / Wispr Flow（Mac）+ 鹅颈麦；手机用 Apple 听写即可——LLM 能补全转写错误。共享办公室仍是痛点。
10. Granola raw transcript 直接丢进 /ce-plan，不先摘要；配合 Printing Press Granola CLI 检索历史会议。
11. last30days 在 plan 前跑：Reddit/X/HN/YouTube 等并行搜，让 plan 基于「社区当下认知」而非训练数据 cutoff。

四、随处可达
12. Remote control 常开：桌面 session 手机续接。
13. 给 Claude 一个邮箱（AgentMail + agentmail-to-claude-code）：邮件/附件触发新 session；Hermes 的 cc <task> 从手机派活。
14. Mac mini 远程：Mosh（低延迟 SSH）、tmux（断网续跑）、Hermes/OpenClaw 自治、Agent Cookie 同步 cookie/.env。

五、产出扩展
15. HyperFrames：视频 = HTML composition → MP4；与代码 loop 同构（script.md → render）。
16. 笔记即 RAG：Bear CLI、Obsidian、gbrain、supermemory——agent 可读写的个人知识库，plan 质量随历史 compound。
17. 自写 Skills：重复两次以上的 wor
