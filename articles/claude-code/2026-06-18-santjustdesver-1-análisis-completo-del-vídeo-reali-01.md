---
id: "2026-06-18-santjustdesver-1-análisis-completo-del-vídeo-reali-01"
title: "@SantJustDesver: 1) Análisis completo del vídeo realizado con Manus IA: El ví"
url: "https://x.com/SantJustDesver/status/2067521839098687810"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "x"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

1)
Análisis completo del vídeo realizado con Manus IA:
El vídeo es un tutorial en inglés de +- 31 minutos en el que  se explica cómo construir un pipeline de trading semi-automatizado con IA combinando tres herramientas:
Herramienta Rol en el sistema
Claude Code (Anthropic) Motor de IA que recibe instrucciones en lenguaje natural y genera/ejecuta código
TradingView Desktop Plataforma de gráficos y datos de mercado
tradingview-mcp Puente MCP (Model Context Protocol) que conecta Claude Code con TradingView vía Chrome DevTools Protocol
El repositorio central que se muestra es 
tradesdontlie/tradingview-mcp
, un proyecto open-source con más de 3.700 estrellas en GitHub que actúa como servidor MCP con 78 herramientas para leer y controlar TradingView Desktop desde una IA.
¿Para qué sirve?
El tutorial enseña a construir un sistema de planificación de trading automatizado compuesto por varios módulos encadenados:
Módulo 1 — Scanner pre-mercado (Scanner A)
Cada mañana antes de la apertura del mercado, Claude Code ejecuta un script que consulta Yahoo Finance para obtener los mayores "gappers" (acciones que suben más del 5% respecto al cierre anterior, precio > $3, volumen pre-mercado > 50.000 acciones) y Benzinga para obtener el catalizador de noticias de cada ticker. El resultado se guarda en un archivo JSON con fecha.
Módulo 2 — Scanner de estrategia (Scanner B)
Toma los resultados del Scanner A y los filtra según criterios de entrada de una estrategia concreta (en el vídeo, la estrategia "Trend Join Long"). Usa la conexión MCP para leer indicadores técnicos directamente desde los gráficos de TradingView.
Módulo 3 — Backtesting con Pine Script
Claude Code genera código Pine Script, lo inyecta en TradingView y ejecuta backtests sobre múltiples activos (NVIDIA, Tesla, Apple, Amazon, Meta, Google, MU) en marcos temporales de 15 minutos.
Módulo 4 — Alertas automáticas a Telegram
El sistema envía los resultados del scanner pre-mercado al teléfono del trader cada mañana mediante
