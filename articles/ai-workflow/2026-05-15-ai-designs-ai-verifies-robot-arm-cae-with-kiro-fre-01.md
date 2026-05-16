---
id: "2026-05-15-ai-designs-ai-verifies-robot-arm-cae-with-kiro-fre-01"
title: "AI Designs, AI Verifies — Robot Arm CAE with Kiro × FreeCAD FEM"
url: "https://zenn.dev/aws_japan/articles/0bb26610096298"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "Python", "zenn"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

## Introduction

This article is the 3rd installment of the **Kiro × Design & Development series**.

In this series, we use AWS's AI coding assistant "**[Kiro](https://kiro.dev/)**" to carry out design and analysis tasks for manufacturing, driven only by natural-language instructions.

We drafted and edited parts with FreeCAD. Next, purely from natural-language instructions to Kiro, we execute **structural analysis (CAE) with FreeCAD FEM**, and quantitatively evaluate the stress distribution and displacement when a load is applied to the entire robot arm.

> Note: In this article, Claude Opus 4.6 is used as the foundation model for Kiro CLI. The quality and behavior of generated code may vary depending on the model version.

**A sequel has been published**: We added a suction-cup gripper to the robot arm whose strength was verified in this article, and executed **reinforcement learning (PPO) with 4,096 parallel environments** in NVIDIA Isaac Sim / Isaac Lab. We reached the stage where the AI itself learns "how to move" the robot arm that, via the CAE in this article, we judged to be "unbreakable and sufficiently lightweight."

> 👉 [AI-Designed Robot × 4,096-Parallel RL on NVIDIA Isaac — Results](https://zenn.dev/aws_japan/articles/428a16622a29f8)

![](https://static.zenn.studio/user-upload/c2e73793f80e-20260420.png)

### Today's flow

```
Step 1: Load the STEP model generated in the [CAD editing edition]
Step 2: Generate a mesh with Gmsh (subdivide into finite elements)
Step 3: Set up the material, boundary conditions, and load
Step 4: Run the structural analysis with the CalculiX solver
Step 5: Visualize the stress and displacement distributions
```

Running FreeCAD FEM headlessly required some trial and error. The story behind that is summarized in the [appendix section](#appendix-trial-and-error-before-getting-the-structural-analysis-running) at the end of this article; those interested can refer to it. In the main text, we start with the results.

### What is structural analysis (FEA)?

Structural analysis is a simulation that calculates "if this force is applied to this shape, where and how much stress is generated, and how much it deforms." The shape is divided into small elements (finite elements), the elastic behavior of each element is expressed as a matrix, the whole is solved as a single system of equations (the stiffness equations), and the displacement at each node is obtained. Stress and strain are then computed from the displacements.

In robot arm design, it is a standard process, verifying the following:

* Whether the arm breaks when it holds a payload at the tip (whether the stress exceeds the material's yield stress)
* How much the arm deflects under load (directly affects positioning accuracy)
* Where stress concentrates (identifying locations that need reinforcement)

---

This article is entirely executed **headlessly** (no GUI — only the command line and scripts). Kiro cannot operate GUI applications like a human, but it can autonomously assemble and run CLI commands and Python scripts, so we proceed on a headless premise throughout.

| Tool | Version | Purpose |
| --- | --- | --- |
| FreeCAD | 1.1.0 | Load STEP, export brep |
| Gmsh | 4.15.0 | Mesh generation (bundled with FreeCAD) |
| CalculiX | 2.23 | FEA solver (bundled with FreeCAD) |
| Python | 3.14.1 | Script execution environment |
| matplotlib | 3.10.8 | Result visualization |

* **[Gmsh](https://gmsh.info/)**: An open-source 3D finite-element mesh generation tool. It takes CAD shapes such as STEP or brep as input and generates meshes with tetrahedral or hexahedral elements.
* **[CalculiX](https://calculix.de/)**: An open-source 3D structural FEA **solver** (the computational engine that solves the system of equations to calculate stress and displacement). It supports linear/nonlinear, static/dynamic, and thermal analyses. It adopts the same `.inp` keyword syntax as the commercial software Abaqus, so it is also familiar to Abaqus users. The compute engine itself is launched by the command `ccx` (short for `CalculiX Crunchier`).

---

## Subject of analysis

We analyze the entire **6-axis articulated robot arm (STEP)** generated in the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8). The 10 parts (base, swivel, shoulder\_joint, upper\_arm, elbow\_joint, forearm, wrist\_j4/j5/j6, flange) are combined with Boolean Fuse and analyzed as a single solid.

* **Pose**: J2=-30°, J3=60°, J5=-45° (working pose)
  + J1=base swivel, J2=shoulder forward/back tilt, J3=elbow up/down tilt, J4-J6=3 wrist axes. In other words, a common working pose with the elbow bent and the arm extended diagonally upward-forward.
* **Material**: Aluminum alloy 6061-T6
  + One of the most common choices for industrial robot frames, said to account for about 70% of worldwide robot-frame use. Reasons are its good strength-to-weight ratio, high machinability, and low cost.
* **Boundary conditions**: The base bottom is fixed, and a 100 N (≈10 kg) downward load is applied to the flange (tip)
  + Actual robot arms are bolted to the floor or a mounting frame, so fully fixing the bottom face is a standard boundary condition in robot FEA. The concentrated tip load is the most simplified model, treating the arm as a "cantilever beam fixed at its root." 10 kg falls within the typical payload range of a mid-size industrial robot (around 1 m reach).
  + In actual operation, the analysis becomes harsher due to gravity torque, motion inertia, offset loads (a center of gravity away from the flange extends the moment arm), and so on. This article is a verification of the static, simplest case.

### Material properties (aluminum alloy 6061-T6)

| Property | Value |
| --- | --- |
| Young's modulus | 69 GPa |
| Poisson's ratio | 0.33 |
| Yield stress | 276 MPa |

Safety factor = yield stress ÷ maximum stress. For ordinary mechanical parts made of ductile materials, a safety factor of 1.5–2.0 or more is often used as a guideline.

### Positioning of this article (note about the model)

The STEP model we analyze this time is a **"solid model," with material fully filled inside**, made as teaching material with CadQuery in the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8). Actual industrial robot arms use hollow aluminum boxes or cast hollow pipes of 2–5 mm wall thickness for the upper-arm and forearm links, achieving both light weight and low cost. The solid model has a cross-section that is an order of magnitude larger than the real thing, so the absolute values of stress and displacement come out more than an order of magnitude smaller than in the real product.

The main purpose of this article is to demonstrate that "the FEM workflow (mesh → material → boundary conditions → solver → result visualization) can be completed from natural-language instructions to AI (Kiro) alone"; it is not a strength certification of the actual robot. That said, the procedure and tool chain apply directly to real hardware, and by swapping the input STEP for a thin-walled hollow one, the same script will yield numbers closer to the real product.

---

## Instructions to Kiro

Wanting to check the strength of the whole robot arm, we gave Kiro the following instruction:

```
Please perform structural analysis on the whole robot arm, using the
robot arm's STEP file (robot_arm.step) generated in the CAD editing
edition.

- Load the STEP in FreeCAD, and combine the 10 parts into a single
  solid with Boolean Fuse
- Generate a mesh with Gmsh (C3D4 tetrahedral elements)
- Material: aluminum alloy 6061-T6
- Boundary condition: fix the base bottom
- Load: a 100 N (≈10 kg) downward force on the flange (tip)
- Run the analysis with CalculiX
- Visualize the distributions of Von Mises stress and displacement
```

---

## Analysis results

From mesh generation to running CalculiX to visualizing the results, Kiro executed everything headlessly. We did not open FreeCAD's GUI; `ccx` is invoked directly from Python, and the resulting `.frd` file is read and summarized. Running FEM headlessly is not straightforward, and we finally completed the analysis only after switching methods three times (the technical story is summarized in the [appendix section](#appendix-trial-and-error-before-getting-the-structural-analysis-running) at the end of this article).

The result images below were obtained by opening the same `.frd` file in FreeCAD's FEM workbench. In this article we run the analysis without using the GUI, but the result file can also be read in the GUI, which is convenient for switching colormaps or rotating the model to inspect things interactively.

### Stress distribution (Von Mises stress)

Von Mises stress is an index that converts a complex three-dimensional stress state (the 6 components of tension/compression/shear) into a single scalar value that can be directly compared with the yield stress measured in a tensile test (uniaxial stress). It is the most commonly used criterion for yielding of ductile materials such as metals; if `σ_vm < yield stress`, you can judge that no permanent deformation occurs. For our aluminum 6061-T6, the reference is 276 MPa.

![](https://static.zenn.studio/user-upload/9172c6a8a8c9-20260420.png)

* **Maximum Von Mises stress: 0.13 MPa**
* **Safety factor: 2,144** (yield stress 276 MPa ÷ maximum stress 0.13 MPa)

The stress is concentrated around the elbow joint and at the base of the upper-arm link. Near the base and the wrist, the stress is low. This is a reasonable result for the structure of a robot arm — bending stress concentrates at the roots of long links.

### Displacement distribution

If stress is an index for "will it break," displacement is another evaluation axis for "is it usable?" For a robot arm, positioning accuracy is important; if the arm deflects under load and the tip deviates from the taught coordinates, the arm is not usable even without breaking.

![](https://static.zenn.studio/user-upload/00a980510e7d-20260420.png)

* **Maximum displacement: 5.76 μm (0.00576 mm)**

The displacement becomes larger going from the base (fixed end) to the flange (tip). A maximum displacement of 5.76 μm under a 100 N load is sufficiently small compared with the positioning accuracy of industrial robots (generally around ±0.05 mm).

The excessive margin — safety factor of over 2,000 against a 100 N (≈10 kg) load, and displacement an order of magnitude below the positioning accuracy — is due to the fact that **this model is an "aluminum solid model" with material fully filled inside**. Actual industrial robot arms use thin-walled hollow structures (aluminum boxes or cast pipes) of a few mm thickness for the upper-arm and forearm links, and the cross-section is only 1/5 to 1/10 that of the solid model.

---

## Appendix: Trial and error before getting the structural analysis running

Compared with the CAD editing in the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8), this structural analysis did not go smoothly. To state the conclusion up front, however, **one of the points of this article is that, starting from the error messages, Kiro broke the problem down and, after switching methods three times, finally got the analysis to complete**.

As a premise, to run a structural analysis with FreeCAD FEM, you need to connect four steps: **(1) mesh subdivision of the shape → (2) generation of an input file (`.inp`) for CalculiX → (3) execution of the solver `ccx` → (4) reading of the results**. The choice of which steps to delegate to FreeCAD and which to do yourself determines the method.

### Attempt 1: Delegate everything to FreeCAD FEM's Python API → failure

The simplest method is to set up the analysis object, solver, material, boundary conditions, and mesh entirely via the Python API provided by FreeCAD FEM (`ObjectsFem`), have FreeCAD itself write the inp, and have `FemToolsCcx` launch ccx. The idea is to automate, via a script, the same procedure that is done manually in the GUI.

Two problems occurred.

**Problem 1: API names have changed across versions, so existing sample code does not work as-is**

The FreeCAD FEM module is still being actively refactored, and function and property names change across versions (e.g. `makeSolverCalculixCcxTools` → in FreeCAD 1.1.0, `makeSolverCalculiXCcxTools` with an uppercase `X`; `mesh_obj.Part` → `mesh_obj.Shape`).

The [FreeCAD official Wiki](https://wiki.freecad.org/FEM_Module) carefully documents GUI procedures for the FEM workbench, but there is no reference that systematically covers the signatures of internal Python APIs such as `ObjectsFem.makeSolverCalculiXCcxTools`. What is officially provided is GUI tutorials and sample scripts; for the rest, you have to read the source code (under `src/Mod/Fem/femobjects/`) and fragmentary forum posts to infer usage. Kiro too initially tried samples that hit in search (targeting older versions) and ran into `AttributeError`, and from there went directly to reading the latest source code to fix the code.

**Problem 2: `NodeLoadTable` error when setting the load direction of `ConstraintForce`**

FreeCAD's `ConstraintForce` (the force boundary condition) decides the load direction via geometric references: **"perpendicular to / along which face or edge."** In the GUI you click a face to specify the direction, but in headless script execution, the face or edge that serves as the direction reference must be explicitly passed via the API.

If you call the inp export without setting this "direction reference," FreeCAD cannot internally compute how to distribute the load direction, and constructing the per-node load table (`NodeLoadTable`) fails, yielding `KeyError: 'NodeLoadTable'`. Accurately passing face/edge references in a headless environment through the API alone is cumbersome, so we stopped Attempt 1 at this point. This is less an AI-specific difficulty than a constraint coming from the fact that **FreeCAD FEM's headless API is designed on the assumption of GUI operation**.

### Attempt 2: Write the inp ourselves → hit a different error

To avoid the `NodeLoadTable` error from Attempt 1, we switched to a method in which **we let FreeCAD handle "loading the shape and creating a mesh," and we write the inp file ourselves and launch ccx directly**. The contents of the inp (node coordinates, element connectivity, material, boundary conditions, load) are plain text, so as long as we can extract the mesh information, we can write it all out in Python.

Here we hit another error.

**Problem 3: `*ERROR in e_c3d: nonpositive jacobian determinant`**

When we ran ccx, an error "nonpositive Jacobian determinant" appeared for almost all elements, and the calculation stopped. Tetrahedral elements (C3D4) expect 4 nodes ordered in a specific way; if the order is reversed, the element is interpreted as "flipped inside out" and the Jacobian becomes negative (this is [a common trouble in the CalculiX community too](https://calculix.discourse.group/t/help-error-in-e-c3d-nonpositive-jacobian/1320)).

It appears that the convention for node ordering differs between the mesh format FreeCAD holds internally (`.unv`) and the inp format CalculiX expects. When we wrote the mesh extracted via FreeCAD directly into an inp, this error occurred frequently. The behavior was the same for both the Boolean-Fused full shape of 10 parts and the upper-arm link in isolation.

### Attempt 3: Call Gmsh directly → success

In the end, the method that worked was **not using FreeCAD's meshing, but calling Gmsh directly from the command line, and having it generate a CalculiX-compatible inp**.

```
# In FreeCAD, STEP -> brep export (per part)
# In Gmsh, brep -> inp (CalculiX format) direct output
gmsh upper_arm.brep -3 -clmax 12 -clmin 3 -order 1 -format inp -o mesh.inp
```

**Why this solved it**: Gmsh has a mode (`-format inp`) that directly outputs in CalculiX-compatible inp format, and in that mode the C3D4 element node ordering is written out in the orientation ccx expects. The "convention mismatch during FreeCAD's unv → inp conversion" that we hit in Attempt 2 can be skipped wholesale by having Gmsh write the inp directly — that is the key.

**Why didn't we adopt this from the start?**: Generally speaking, when starting to use a piece of software, entering through the "officially integrated GUI / API" is the natural order. FreeCAD FEM's official documentation is also organized along the lines of "operate the FEM workbench in the GUI" → "automate the same procedure via the Python API," and it does not say "bypass the internal meshing and call Gmsh directly." Calling Gmsh directly this time is a method you can choose only after diagnosing that "FreeCAD's integrated functionality itself has a problem at the inp-writing stage," and it is hard to come up with before hitting the two kinds of errors in Attempts 1–2. Looking back, **when using FreeCAD for FEM headlessly, relying not on the internal functionality but on calling Gmsh and ccx directly for mesh generation and solver launch is the most robust approach**.

The inp output by Gmsh also contains non-volume elements such as edge elements (T3D2) and face elements (CPS3), so we extracted only the C3D4 volume elements in Python, added the material, boundary conditions, and load, and assembled a complete inp. We then ran `ccx` directly, and the analysis completed normally.

---

## Summary

### End-to-end design → editing → analysis

Through three articles, we have shown that the following pipeline can be realized from natural-language instructions alone:

Within the scope of a simple static structural analysis such as the robot arm we dealt with this time, **we were able to turn the loop of "I want this kind of shape" → "Is the strength and deformation of this shape within an acceptable range?" at the early design stage, without writing a single line of code.**

And in Part 4 of the series, we brought the robot arm whose strength was verified in this article into NVIDIA Isaac Sim / Isaac Lab, and had Kiro execute reinforcement learning (PPO, 4,096 envs in parallel) for suction-cup pickup of a cube. The entire workflow of **design → CAD editing → CAE → motion learning** has reached the point where it can be turned end-to-end from natural-language instructions alone.  
👉 [AI-Designed Robot × 4,096-Parallel RL on NVIDIA Isaac — Results](https://zenn.dev/aws_japan/articles/428a16622a29f8)
