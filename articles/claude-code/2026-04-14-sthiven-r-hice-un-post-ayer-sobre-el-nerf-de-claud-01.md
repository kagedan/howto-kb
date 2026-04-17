---
id: "2026-04-14-sthiven-r-hice-un-post-ayer-sobre-el-nerf-de-claud-01"
title: "@Sthiven_R: Hice un post ayer sobre el nerf de Claude Opus 4.6, Desde en"
url: "https://x.com/Sthiven_R/status/2043992488109899849"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-04-14"
date_collected: "2026-04-17"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

Hice un post ayer sobre el nerf de Claude Opus 4.6, Desde entonces todos buscan el fix... Despues de tanta prueba y error al fin di con la solucion...

Despues de ver muchas "Soluciones" que han estado circulando como por ejemplo: 

{
    "model": "claude-opus-4-6",
    "effortLevel": "high",
    "alwaysThinkingEnabled": true,
    "env": {
      "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1",
      "MAX_THINKING_TOKENS": "31999"
    }
  }

  Probé eso. No es la solución.

  MAX_THINKING_TOKENS y alwaysThinkingEnabled son ruido. Hacen que el modelo gaste más tokens sin que el
  razonamiento mejore realmente. Es como subir el volumen de un parlante roto.

  — ¿Entonces qué funciona?

  Dos pasos. Sin misterio:

  𝗣𝗮𝘀𝗼 𝟭: Desinstalar tu versión actual de Claude Code e instalar una versión estable especialmente la de 2.1.98

  npm uninstall -g @anthropic-ai/claude-code
  npm install -g @anthropic-ai/claude-code@2.1.98

  𝗣𝗮𝘀𝗼 𝟮: Agregar UNA sola variable en tu .claude/settings.json

  "env": {
    "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING": "1"
  }

  Eso es todo.

  — ¿Por qué funciona?

  Lo que Anthropic activó se llama "adaptive thinking". En teoría, el modelo decide cuánto pensar por turno. En
  práctica, en ciertos turnos asigna CERO tokens de razonamiento.

  Cero. El modelo literalmente deja de pensar.

  De ahí vienen las alucinaciones, los commits inventados, los paquetes que no existen, las ediciones sin leer el
  archivo primero.

  Desactivar eso le devuelve al modelo un presupuesto fijo de razonamiento en cada turno. Simple.

  — ¿Qué cambió después de aplicar esto?

  → El modelo razona más tiempo antes de responder
  → Las respuestas son más largas, más estructuradas, más inteligentes
  → Vuelve a leer archivos antes de editarlos
  → Deja de inventar cosas que no existen

  No es magia. Es devolverle lo que le quitaron.

  — ¿Por qué la versión del CLI importa?

  Las versiones más recientes del CLI traen cambios internos que refuerzan el comportamiento nerfe
