---
id: "2026-05-14-ai-assisted-engineering-with-kiro-cfd-and-3d-model-01"
title: "AI-Assisted Engineering with Kiro — CFD and 3D Modeling from Text"
url: "https://zenn.dev/aws_japan/articles/965c6981b60cc2"
source: "zenn"
category: "claude-code"
tags: ["prompt-engineering", "API", "Python", "zenn"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

## Introduction

In manufacturing engineering work, building simulations and creating 3D models are indispensable processes. However, these tasks require mastery of specialized software and a corresponding amount of time.

In this article, we introduce the "[Auto&Manufacturing - Kiro for Business Users](https://catalog.us-east-1.prod.workshops.aws/workshops/2b863a58-f3b0-414e-98c2-2cb095c4ac81/en-US)" workshop, which uses AWS's AI coding assistant "[Kiro](https://kiro.dev/)" to build fluid simulations and 3D models from natural language instructions alone.

> Note: In this workshop, Claude Opus 4.6 is used as the foundation model for Kiro CLI. The quality and behavior of generated code may vary depending on the model version.
>
> Note: In the trials shown in this article, Kiro basically uses only libraries available from Python, and executes 3D modeling and fluid simulations without using any specific CAD software or simulation software.

![](https://static.zenn.studio/user-upload/af20ec3da9fe-20260330.png)

The workshop includes the following two modules.

| Module | Content | Duration |
| --- | --- | --- |
| [Engineering](https://catalog.us-east-1.prod.workshops.aws/workshops/2b863a58-f3b0-414e-98c2-2cb095c4ac81/en-US/16-remote-linux/50-engineering-simulation) | Building a CFD simulation using the lattice Boltzmann method | 25 min |
| [Product Design](https://catalog.us-east-1.prod.workshops.aws/workshops/2b863a58-f3b0-414e-98c2-2cb095c4ac81/en-US/16-remote-linux/70-product-design) | Parametric design of a NACA airfoil turbine blade | 25 min |

Both modules offer an experience where participants generate engineering deliverables without writing a single line of code, using only natural-language conversation.

**[Image 1] Overview of workshop deliverables**

> CFD velocity field, turbine blade comparison, jet engine, and robot arm images arranged in a 2×2 grid. All generated from natural-language instructions alone.

![](https://static.zenn.studio/user-upload/a36bd86c6b0e-20260330.png)

**A sequel has been published**: This article covered output in STL format, but the sequel goes a step further, achieving STEP-format 3D model output and then editing in FreeCAD — all from natural-language instructions.

> 👉 [Letting AI Run Your CAD — STEP Generation to FreeCAD with Kiro](https://zenn.dev/aws_japan/articles/45fb5d3130035d)

**A further sequel has also been published**: Using the robot arm edited via STEP in the sequel above, we had Kiro run structural analysis (CAE) with FreeCAD FEM and quantitatively evaluated stress and displacement. An end-to-end pipeline of design → CAD editing → strength verification is now complete.

> 👉 [AI Designs, AI Verifies — Robot Arm CAE with Kiro × FreeCAD FEM](https://zenn.dev/aws_japan/articles/a5cd987ecb59ff)

**And a 4th sequel has also been published**: We added a suction-cup gripper to the robot arm that has been designed, edited, and strength-verified so far, and executed **reinforcement learning (PPO) with 4,096 parallel environments** in NVIDIA Isaac Sim / Isaac Lab. An AI-designed robot is now learning its own movements — completing an end-to-end pipeline of design → CAD editing → CAE → reinforcement learning.

> 👉 [AI-Designed Robot × 4,096-Parallel RL on NVIDIA Isaac — Results](https://zenn.dev/aws_japan/articles/096dec97613a01)

---

## Module 1: CFD Simulation — An AI That Understands Physics

### Overview

In the first module, we perform a fluid analysis around a cylinder placed inside a 2D channel. Participants simply enter a natural-language prompt like the following into Kiro, and a CFD simulation is constructed.

```
I want to build an interactive 2D fluid dynamics simulation in Python
that visualizes flow around a cylinder.

Setup:
- 2D channel, 2 meters long, 0.8 meters high
- A cylinder with diameter 0.1 m placed at position (0.5, 0.4)
- Fluid flowing from left to right at 0.1 m/s
- Kinematic viscosity = 5e-4 m^2/s (Re=20 in the default settings)

Solver:
- Use the Lattice Boltzmann Method (LBM) with a D2Q9 lattice
- Grid resolution: 400x160 cells
- Bounce-back boundary condition on the cylinder and walls
...
```

> **Glossary**
>
> * **Lattice Boltzmann Method (LBM)**: A method for calculating fluid motion. It computes the flow of water or air using rule-based updates that describe "how a group of small particles move on a grid". Implementation is simpler than conventional methods (directly solving the Navier–Stokes equations), and it is well suited to parallel computation.
> * **D2Q9 lattice**: A rule setting where, on a two-dimensional (D2) grid, particles at each cell can move in nine directions (Q9 = up/down/left/right + four diagonals + stationary).
> * **Grid resolution 400x160 cells**: The simulation space is divided into 400 cells horizontally and 160 cells vertically. Finer cells increase accuracy but make the calculation heavier. 400×160 strikes a balance that can be computed on a laptop in a few minutes.
> * **Bounce-back boundary condition**: A rule that particles hitting a wall or the cylinder "bounce straight back." This reproduces zero flow velocity at the wall surface (the no-slip condition).
> * **Reynolds number (Re)**: A dimensionless number representing how "calm" the flow is. Small values mean laminar flow (orderly), large values mean turbulent flow (full of vortices). Re=20 is a setting that starts from a calm flow.
>
> In plain words, this prompt is saying: "Place a circular pillar in a 2 m × 0.8 m water channel, flow water from the left, and compute/visualize it using the grid-based approach." Participants can paste this prompt directly into Kiro and the code is generated automatically.

### Step 1: Exploring the simulation

The generated simulation has sliders built in, allowing the inlet velocity and the cylinder diameter to be changed in real time.

| Inlet velocity | Reynolds number | Phenomenon observed |
| --- | --- | --- |
| 0.05 m/s | ~10 | Steady, symmetric flow |
| 0.1 m/s | ~20 | Steady flow with an elongated wake |
| 0.25 m/s | ~50 | Onset of vortex shedding |
| 0.5 m/s | ~100 | Periodic Kármán vortex street |

### Step 2: Adding visualization modes

In the same chat session, functionality is added to the existing simulation. Kiro adds features to the existing code rather than rewriting it from scratch.

```
Please add three visualization modes switchable via radio buttons.
Keep the dark background style:

1. Velocity magnitude (current — inferno colormap + streamlines)
2. Vorticity field — zero-centered 'RdBu_r' colormap, emphasizing vortex
   shedding with red/blue vortices
3. Pressure distribution — 'coolwarm' colormap, showing the high/low
   pressure zones around the cylinder
4. Streamlines only — dense streamlines colored by velocity magnitude
   using the 'plasma' colormap

Also, add a second subplot below the main plot showing the drag and lift
coefficients vs. time step as smooth lines.
```

### Step 3: Generating publication-quality figures

For use in reports and presentations, high-resolution static images are produced.

```
Please create a script called generate_figures.py.
Run a simulation at inlet velocity 0.25 m/s (Re=50) for 5000 time steps,
and save three publication-quality figures as PNG.
dark_background style, figure size 14x6, DPI 200.

1. cfd_velocity.png — velocity magnitude with the inferno colormap + a
   semi-transparent white streamline overlay
2. cfd_vorticity.png — vorticity field with the RdBu_r colormap,
   zero-centered with symmetric color limits
3. cfd_streamlines.png — dense streamlines (density=4) colored by
   velocity using the plasma colormap

Each figure should have a title, axis labels in meters, and
aspect='equal'. Please run the script after creating it.
```

**[Image 2] Velocity field visualization**

> Velocity field with the inferno colormap (a matplotlib colormap preset — higher values are brighter). The wake structure behind the cylinder is clearly visualized.

![](https://static.zenn.studio/user-upload/f9c49429033c-20260330.png)

**[Image 3] Vorticity field visualization**

> Vorticity field with the RdBu\_r colormap. Red and blue indicate different directions of rotation.

![](https://static.zenn.studio/user-upload/b85f87fe72f4-20260330.png)

### Step 4: Parameter study

Comparison images across conditions can also be generated with a single instruction.

```
Please create a script called parameter_study.py.
Run simulations for 4000 time steps each at five different inlet
velocities (0.05, 0.1, 0.2, 0.35, 0.5 m/s), and generate
reynolds_comparison.png (20x8 inches, DPI 200) with five subplots
arranged side by side showing the vorticity fields.
Label each subplot "Re = X". Please run the script.
```

**[Image 4] Reynolds number comparison**

> Vorticity fields at five Reynolds numbers. Vortex shedding becomes more pronounced as Re increases.

![](https://static.zenn.studio/user-upload/ff3562deba9e-20260330.png)

### Step 5: HTML report generation

Finally, we generate a report that collects all deliverables.

```
Please create an HTML report called cfd_report.html. Contents:
1. Title "CFD Simulation Report — Flow Around a Cylinder in a Channel"
2. Simulation parameters (tunnel size, cylinder position, fluid
   properties)
3. All generated PNG figures embedded
4. A brief description of what each figure shows
5. A table of Reynolds numbers and the flow regimes observed
Clean CSS styling, professional appearance. Please open it in a browser.
```

From building the simulation, to extending the visualization, to producing publication-quality figures, to a parameter study, to report creation — everything is completed with five instructions within a single chat session.

![](https://static.zenn.studio/user-upload/0c73e0553aeb-20260330.png)

---

## Module 2: Product Design — Design Iteration by Conversation

### Overview

In the second module, we design and iterate on a parametric turbine blade with NACA airfoil cross-sections. In traditional CAD workflows, manual operations in the software are needed for each parameter change, but in this workshop we evolve the design through conversation.

Note — NACA: an abbreviation of National Advisory Committee for Aeronautics, the predecessor of NASA. The "NACA airfoil" series, which defines airfoil cross-sections with mathematical formulas, is well known. A 4-digit number specifies parameters such as thickness and camber. Here, "NACA symmetric airfoil with 12% thickness ratio" means a symmetric airfoil cross-section whose maximum thickness is 12% of the chord length.

### Design iteration workflow

The workflow proceeds in the following three steps.

### Step 1: Generating the base design

In the first prompt, all blade parameters are specified.

```
Please create a folder called turbine-blade.

Build a Python script called generate_blade.py that creates a
parametric turbine blade and saves it as an STL file.

Blade parameters:
- Blade length: 120 mm
- Root chord: 40 mm
- Tip chord ratio: 100% (no taper initially)
- Twist angle: 15 degrees (increasing linearly from root to tip)
- Airfoil: NACA symmetric airfoil with 12% thickness ratio
- Grid: 40 sections along the span, 60 points per airfoil

What the script does:
1. Generates NACA 4-digit symmetric airfoil coordinates for each
   section
2. Applies a linear twist along the span
3. Applies linear taper (chord scaling from root to tip)
4. Builds a triangle mesh between adjacent sections
5. Closes the root and tip with caps
6. Saves as turbine_blade_base.stl using numpy-stl

Create a 4-view visualization as blade_base_views.png:
- Isometric, front (leading edge), top, and side views
- Dark background, blue color (#4a90d9), axis labels in mm
- Figure size 16x10, DPI 150

Install numpy-stl, numpy, and matplotlib as needed. Please run the
script after creating it.
```

**[Image 5] Four-view of the base blade**

> Isometric, front, top, and side views of the generated base blade.

![](https://static.zenn.studio/user-upload/7eb61516241c-20260330.png)

### Step 2: Inspecting the STL

We ask Kiro about the generated shape.

```
Please load the STL file and tell me the following:
1. Number of triangles and vertices
2. Bounding-box dimensions (X, Y, Z extents in mm)
3. Total surface area
4. Is the mesh watertight (closed)?
```

### Step 3: Conversational design changes

In the same session, we create a modified version with changed twist angle and taper, and generate a comparison visualization.

```
Please modify the blade generator to create a second blade with the
following changes:
- Increase the twist angle from 15° to 25° (improves flow turning)
- Taper the tip to 60% of the root chord (reduces tip losses)
- Keep all other parameters the same

Save the modified blade as turbine_blade_modified.stl, and generate
a comparison visualization called blade_comparison.png:

Top row (three subplots):
1. Base design in blue (#4a90d9) — isometric view
2. Modified design in orange (#e8943a) — same viewpoint
3. Overlay of both blades (base semi-transparent, modified on top)

Bottom row (three subplots):
4. Cross-section comparison at 25% span
5. Cross-section comparison at 50% span
6. Cross-section comparison at 75% span

Each cross-section should fill both profiles with their respective
colors and include labels.
Dark background, figure size 18x10, DPI 150. Please run the script.
```

**[Image 6] Comparison of design variants**

> Top row: isometric-view comparison of base (blue) vs. modified (orange). Bottom row: cross-section overlays at three spanwise locations.

![](https://static.zenn.studio/user-upload/f6a751ebd2d7-20260330.png)

### Step 4: Adding a root fillet

An instruction to add post-processing to an existing shape.

```
Please add a 3 mm radius fillet at the blade root junction.
The fillet must blend smoothly from the blade surface onto a flat
mounting platform (a 50 mm x 20 mm rectangle at z=0).
Update the modified STL and regenerate the comparison. Please run it.
```

### Step 5: Design report generation

```
Please create an HTML report called blade_report.html. Contents:
1. Title: "Turbine Blade Design Iteration Report"
2. A parameter comparison table for base vs. modified (blade length,
   root chord, tip chord ratio, twist angle, thickness ratio, fillet
   radius)
3. Embed blade_base_views.png (base design)
4. Embed blade_comparison.png (iteration comparison)
5. A "Design Rationale" section explaining the reasons for each change
6. A "Next Steps" section with suggestions: cooling channel
   integration, FEA stress analysis, flutter analysis
7. Professional dark theme, clean CSS
Please open it in a browser.
```

![](https://static.zenn.studio/user-upload/0e91179f23dc-20260330.png)

### Step 6: Exporting manufacturing data

```
Please create a script called export_manufacturing.py:
1. Load both STL files
2. Validate mesh quality (check for degenerate triangles and
   non-manifold edges)
3. Export key dimensions at 10 spanwise locations as CSV (chord
   length, thickness, twist angle, leading-edge position)
4. Print a manufacturing summary: total volume, surface area,
   bounding box, center of gravity
Please run it.
```

### What this module shows

The traditional sequence of "open the CAD software → manually change parameters → re-render → create comparison images" is completed within minutes, through conversation. Especially at the early stage of design for shape exploration and parameter studies, this approach offers a large time saving.

---

## Applied example: 3D modeling of more complex industrial machinery

We extended the workshop approach to more complex 3D modeling. Here we introduce two examples.

### Example 1: Turbofan jet engine

A jet engine is a complex shape composed of many sections, including the nacelle, fan blades, compressor, combustor, turbine, and exhaust nozzle. With a prompt like the following, we generated a 3D model with parameterized sections all at once.

```
Please build a Python script called generate_jet_engine.py that
generates a simplified 3D model of a turbofan jet engine.

■ Overall engine configuration:
Total length: 3000 mm, maximum outer diameter: 1200 mm

■ Specifications of each section (from the front):
1. Fan casing — truncated cone, front diameter 400 mm → rear
   diameter 1200 mm
2. Fan blades — 18 blades, twist angle 15 degrees
3. Bypass duct — outer diameter 1200 mm → 900 mm
4. Low-pressure compressor — 3 stator-vane stages, 12 vanes per
   stage
5. High-pressure compressor — 5 stator-vane stages, 16 vanes per
   stage
6. Combustor — annular shape with liner
7. Turbine — 2 turbine blade stages, 14 blades per stage
8. Exhaust nozzle — with tail cone

■ For parameter-change demo:
FAN_BLADE_COUNT = 18
COMPRESSOR_STAGES_LP = 3
TURBINE_STAGES = 2
...
```

By simply changing the parameters at the top of the script, variations with different numbers of fan blades or compressor stages can be generated instantly.

**[Image 7] Four-view of the jet engine**

> 3D model of the generated turbofan jet engine. 8-section configuration, 4,120 triangles.

![](https://static.zenn.studio/user-upload/43129f2f2af8-20260330.png)

### Example 2: Six-axis articulated robot arm

A distinctive feature of industrial robot arms is that the pose changes greatly with joint angles. In this model, we had Kiro implement pose calculation based on forward kinematics (FK).

```
Please generate a 3D model of an industrial 6-axis articulated robot
arm.

■ Pose parameters (variables at the top of the script):
- J1_ANGLE = 0      # base swivel angle
- J2_ANGLE = -30    # shoulder angle
- J3_ANGLE = 60     # elbow angle
- J4_ANGLE = 0      # forearm rotation angle
- J5_ANGLE = -45    # wrist tilt angle
- J6_ANGLE = 0      # wrist rotation angle

For each joint angle, compute each link's position and orientation
using forward kinematics, and rotate/translate the mesh accordingly.
```

By simply changing the combination of joint angles, variations such as home position, working pose, and folded pose can be generated automatically.

**[Image 8] Comparison of three robot-arm poses**

> Comparison of three poses of the same model. Generated by changing only the joint-angle parameters.

![](https://static.zenn.studio/user-upload/df375f35cdfa-20260330.png)

---

## Technical note: The role of Python-based 3D shape generation

### Why draft in Python?

The approach used in this workshop generates STL (triangle mesh) files directly from Python code, using the numpy-stl library. The reason this approach fits well with parametric design is that the dimensions and configuration of the shape can all be managed as variables in code.

```
FAN_BLADE_COUNT = 18    # → change to 24 to generate a variation
TURBINE_STAGES = 2      # → change to 3 for a 3-stage turbine
```

### Choosing between STL and STEP

The STL files produced are a de facto standard format that can be read by almost all CAD software and 3D-printer slicers. However, because STL is a collection of triangle meshes, it is not suited to feature-based editing in CAD software, such as "change the diameter of a hole" or "add a fillet."

For such use cases, outputting STEP format using a Python library such as CadQuery is a better fit.

| Use case | Recommended format | Library |
| --- | --- | --- |
| Shape exploration / parameter studies | STL | numpy-stl |
| 3D printing | STL | numpy-stl |
| Integration with CAD software / subsequent editing | STEP | CadQuery |
| Handover to manufacturing | STEP | CadQuery |

### Position in the design process

This approach is most effective in the early stages of design, for shape exploration and concept verification. Final detailed design and manufacturing drawings remain the domain of traditional CAD software, but in the phase of rapidly iterating on "what shapes should we consider," the combination of natural language × Python × AI is a powerful tool.

Regarding this development from STL to STEP, the sequel article introduces the full workflow of actually generating a STEP with CadQuery and editing it in FreeCAD.  
👉 [Letting AI Run Your CAD — STEP Generation to FreeCAD with Kiro](https://zenn.dev/aws_japan/articles/45fb5d3130035d)

In the article that follows, we have Kiro run structural analysis (CAE) with FreeCAD FEM on the FreeCAD-edited robot arm, and complete a quantitative evaluation of stress and displacement.  
👉 [AI Designs, AI Verifies — Robot Arm CAE with Kiro × FreeCAD FEM](https://zenn.dev/aws_japan/articles/a5cd987ecb59ff)

And in the 4th article of the series, we brought the CAE-verified robot arm into NVIDIA Isaac Sim / Isaac Lab, and had Kiro run reinforcement learning (PPO, 4,096 envs in parallel) for suction-cup pickup of a cube. We reached the point where the designed shape itself has its "how to move" learned by the AI.  
👉 [AI-Designed Robot × 4,096-Parallel RL on NVIDIA Isaac — Results](https://zenn.dev/aws_japan/articles/096dec97613a01)

---

## Summary

Through this workshop, the following were confirmed.

* **Automatic construction of physics simulations**: A CFD solver based on the lattice Boltzmann method can be built from natural-language instructions alone.
* **Conversation-based design iteration**: Turbine blade parameter changes, comparison visualizations, and report generation can be completed within a chat-session dialogue.
* **Complex 3D modeling**: Shapes composed of many components, such as a jet engine or a 6-axis robot arm, can also be generated from parameterized natural-language prompts.

Engineering work in manufacturing is a domain that requires advanced expertise and time. By having AI take on part of it, engineers can focus on more essential design decisions and creative work. Kiro shows its potential as a practical tool for that.
