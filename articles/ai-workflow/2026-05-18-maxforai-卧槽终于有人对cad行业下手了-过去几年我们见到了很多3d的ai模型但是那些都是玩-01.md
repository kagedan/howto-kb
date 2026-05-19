---
id: "2026-05-18-maxforai-卧槽终于有人对cad行业下手了-过去几年我们见到了很多3d的ai模型但是那些都是玩-01"
title: "@MaxForAI: 卧槽，终于有人对CAD行业下手了 过去几年，我们见到了很多3D的AI模型，但是那些都是玩具，很难用，基本无法用到到工业"
url: "https://x.com/MaxForAI/status/2056222565094522884"
source: "x"
category: "ai-workflow"
tags: ["x"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

卧槽，终于有人对CAD行业下手了

过去几年，我们见到了很多3D的AI模型，但是那些都是玩具，很难用，基本无法用到到工业生产

但刚刚麻省理工开源了一个将照片转换为可完全编辑的 CAD 程序的 AI 模型GenCAD，它悄然终结了每小时 150 美元的 CAD 建模行业。  

GenCAD不只是生成一个3D外形。

它做的是：给一张CAD图像/渲染图，生成对应的参数化CAD命令序列，也就是CAD program，再通过几何内核转成3D solid model。

重要的是它保留了「建模历史」。

所以它不是「AI画了个3D玩具」，而是在尝试把图片变成可编辑、可制造流程能继续接住的CAD模型。

同时它：

→ 无需 SolidWorks 许可 
→ 无需数周建模 
→ 不需要 CAD 工程师  

100% 开源

如果后续这条路线跑通，CAD行业最贵的那部分时间，草图理解、参数化建模、反复改模型，都会被一点点吃掉。

代码、数据和预训练模型入口都已经放出来了。

GenCAD可能是AI真正进入工业设计工作流的一个信号。
项目地址：https://t.co/R9eJ3lMhP4
视频Demo：https://t.co/WY3SGe9yyR
Paper：https://t.co/kBReJW3X8N
github：https://t.co/kKT2uInMBX


--- 引用元 @HowToAI_ ---
MIT open-sourced an AI model that converts photos into fully editable CAD programs and it quietly kills the $150/hour CAD modeling industry.

Just upload a sketch or photo and it generates the full parametric 3D model. exportable as STL. ready for manufacturing.

→ no SolidWorks license
→ no weeks of modeling
→ no CAD engineer needed

100% Open Source

This is a research project published by two MIT engineers.

Here's the GitHub: https://t.co/O0tT8PTid8

No UI,  you need Docker + GPU + command line.

but the tech is insane and the direction is clear.
