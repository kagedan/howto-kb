---
id: "2026-07-05-voxelplot-seedance-20-advanced-workflows-series-12-01"
title: "@voxelplot: Seedance 2.0 - Advanced Workflows Series 12. Cinematics wit"
url: "https://x.com/voxelplot/status/2073785741709021494"
source: "x"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "x"]
date_published: "2026-07-05"
date_collected: "2026-07-06"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

Seedance 2.0 - Advanced Workflows Series

12. Cinematics with Unreal Engine and Claude Fable 5
Fable 5 is an absolute beast model that can take control of Unreal Engine and create videogames. 

We can build scenes as a little video game with physics and assets and configure a playable character to create a cinematic scene.

In this example I created a scene of an astronaut lost in space floating between asteroids.

I created a zero gravity environment and made assets like cubes and spheres representing asteroids interact in this environment.

I recorded the gameplay and later place a camera to build the cinematic.

Workflow + Prompts 👇

1. Connect Claude with UE trough MCP
The Model Context Protocol (MCP) is an open-source standard that connects AI assistants to external data sources, local files, and software.

UE 5.8 (latest version) has as a new feature native support for MCP integration. Claude takes control of the program and you give it instructions with natural language:

Tutorial for MCP setup in UE: https://t.co/PL1sJEktTh

2. Run Fable 5 to build a game level
Once the MCP is configured, you only have to give instructions inside Unreal Engine so that Claude takes control and generates what you want.

Prompt:
Generate a zero gravity level, without a floor. The background will be a flat blue color. Create 20 asteroids formed by basic shapes, with red color, that float in space. They will make rotation movements on themselves very slowly and will also move slightly in a random direction in space. Create also a dummy with basic shapes of green color, playable, that also has zero gravity. This dummy will also float and will not brake automatically when handled, in such a way that it maintains an inertial movement when it moves in one direction. The playable character will be located right in front of the asteroid cluster.

3. Generate a cinematic
Once the level is generated, you will be able to play inside it as if it were a game.

For our cinematic, we only nee
