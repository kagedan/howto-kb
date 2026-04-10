---
id: "2026-04-09-lookdevツール-gafferが動かない-01"
title: "Look&Devツール Gafferが動かない"
url: "https://qiita.com/yokamak/items/389e8a69811c5b27ebaf"
source: "qiita"
category: "ai-workflow"
tags: ["Python", "qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

# はじめに
Windows11マシンで、gaffer-1.6.10.0-windowsを動かしていますが、あるマシンで、起動したところ、
```bash
> gaffer
ERROR : IECore.loadConfig : Error executing file "C:\gaffer-1.6.10.0-windows\startup\gui\lightEditor.py" - "File "pointLight" could not be found.".
ERROR :  Traceback (most recent call last):
ERROR :   File "C:\gaffer-1.6.10.0-windows\python\IECore\ConfigLoader.py", line 76, in loadConfig
ERROR :     exec(
ERROR :   File "C:\gaffer-1.6.10.0-windows\startup\gui\lightEditor.py", line 134, in <module>
ERROR :
