---
id: "2026-05-14-letting-ai-run-your-cad-step-generation-to-freecad-01"
title: "Letting AI Run Your CAD — STEP Generation to FreeCAD with Kiro"
url: "https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8"
source: "zenn"
category: "claude-code"
tags: ["MCP", "prompt-engineering", "API", "Python", "zenn"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

## Introduction

In the [previous article](https://zenn.dev/aws_japan/articles/0bb6554b10c6bc), we introduced AWS's "[Auto&Manufacturing - Kiro for Business Users](https://catalog.us-east-1.prod.workshops.aws/workshops/2b863a58-f3b0-414e-98c2-2cb095c4ac81/en-US)" workshop. That article used the AI coding assistant "Kiro" to run CFD simulations and 3D modeling from natural-language instructions alone.

In the "[Applied example: 3D modeling of more complex industrial machinery](https://zenn.dev/aws_japan/articles/0bb6554b10c6bc#%E5%BF%9C%E7%94%A8%EF%BC%9A%E3%82%88%E3%82%8A%E8%A4%87%E9%9B%91%E3%81%AA%E7%94%A3%E6%A5%AD%E6%A9%9F%E6%A2%B0%E3%81%AE3d%E3%83%A2%E3%83%87%E3%83%AA%E3%83%B3%E3%82%B0)" section of the previous article, we generated a 3D model of a 6-axis articulated robot arm from natural-language instructions alone.

The method used at that time was Python's numpy-stl library, which directly computes triangle vertex coordinates to **output an STL file. No CAD software was used at all**.

The workshop adopted STL because the environment can be set up with a single `pip install numpy-stl`, making it easy for beginners. However, STL is just a collection of triangle meshes, so feature-based editing in CAD software (changing hole diameters, adding fillets, etc.) is practically difficult. **STL can be used for early-stage shape exploration or concept checks, but it does not fit directly into real CAD workflows in practice**.

![](https://static.zenn.studio/user-upload/649edc2a456b-20260416.png)  
[Image] STL model of the 6-axis robot arm generated previously

This time we take a step further, re-outputting this robot arm in **STEP format**, thereby **demonstrating that an AI-generated 3D model can be opened and edited in CAD software**.

![](https://static.zenn.studio/user-upload/4f80068c8f90-20260416.png)

> Note: In this workshop, Claude Opus 4.6 is used as the foundation model for Kiro CLI. The quality and behavior of generated code may vary depending on the model version.

**A sequel has been published**: Using the robot arm that was STEP-exported and FreeCAD-edited in this article, we had Kiro run structural analysis (CAE) with FreeCAD FEM, and quantitatively evaluated stress and displacement. An end-to-end pipeline of design → CAD editing → strength verification is now complete.

> 👉 [AI Designs, AI Verifies — Robot Arm CAE with Kiro × FreeCAD FEM](https://zenn.dev/aws_japan/articles/a5cd987ecb59ff)

**And a 4th sequel has also been published**: Using the robot arm whose strength was verified in the CAE above, we added a suction-cup gripper and executed **reinforcement learning (PPO) with 4,096 parallel environments** in NVIDIA Isaac Sim / Isaac Lab. We reached the point where the AI itself learns "how to move" the shape that was CAD-edited in this article.

> 👉 [AI-Designed Robot × 4,096-Parallel RL on NVIDIA Isaac — Results](https://zenn.dev/aws_japan/articles/096dec97613a01)

### Difference between STL and STEP

|  | STL | STEP |
| --- | --- | --- |
| Data content | Collection of triangle vertex coordinates | B-rep (mathematical definitions of faces, edges, vertices) |
| Editing in CAD software | Mesh editing is possible, but feature-based editing is practically difficult | Hole addition, fillets, Boolean operations are all possible |
| Shape information retained | Approximate surface geometry only | Face/edge topology and exact curved-surface definitions |
| Parametric design history | None | None (STEP does not retain a feature tree either) |
| Use cases | 3D printing, visualization, analysis | CAD design, handover of manufacturing data |

**If STL is like a bitmap image (JPEG), then STEP is closer to a PowerPoint file**. With a JPEG you can see what is drawn, but you cannot select and edit individual characters or shapes in the image. With PowerPoint, by contrast, you can select text boxes or shapes one by one to move, deform, or delete them. STEP is similar — you can select faces or edges to add fillets or drill holes.

However, this analogy is not strict. PowerPoint also retains the creation history of "in what order the objects were made," whereas STEP does not. What STEP retains is "the shape itself," not "how the shape was made (design history)." When you open a STEP in SolidWorks, for example, it is read as a "dumb solid" and the feature tree is empty. In other words, you can select faces or edges and add new machining operations, but you cannot roll back the original design steps and do things like "change only the diameter of this hole."

---

## Today's flow

In this article, we proceed in the following three steps.

```
Step 1: Kiro generates CadQuery code and outputs a STEP file
        (natural-language instruction -> Python script -> STEP)

Step 2: Kiro edits the STEP via FreeCAD's Python API
        (scripted CAD operations such as adding fillets and holes)

Step 3: Open the STEP in FreeCAD's GUI to confirm that a human can
        edit it interactively
        (standard CAD operations such as part selection and feature
        addition)
```

Steps 1–2 are completed purely with natural-language instructions to Kiro. Step 3 is a manual FreeCAD operation by a human, confirming that the same editing Kiro did via script in Step 2 can also be done in the GUI.

---

## Environment setup

| Tool | Version | Purpose |
| --- | --- | --- |
| CadQuery | 2.7.0 | Generate STEP files from Python |
| OpenCASCADE (OCP) | 7.8.1.2 | CadQuery's internal CAD engine |
| FreeCAD | 1.1.0 | Load, edit, and visualize STEP files |
| Python | 3.12 | Script execution environment |

### Installation steps

CadQuery embeds OpenCASCADE (the CAD engine), so it cannot be installed with pip alone. We install it via conda (miniforge). The following are the steps on macOS.

```
# Install miniforge if you don't have it (macOS)
brew install miniforge

# Create a CadQuery environment (Python 3.12 + CadQuery + OCP all together)
micromamba create -n cadquery python=3.12 cadquery -c conda-forge -y

# Install FreeCAD (macOS)
brew install --cask freecad
```

On Windows, download and run the [miniforge installer](https://github.com/conda-forge/miniforge#miniforge3); the `micromamba create` command is the same. FreeCAD can be obtained from the [official site](https://www.freecad.org/downloads.php).

Compared with the previous workshop, where numpy-stl could be installed with a single `pip install numpy-stl`, CadQuery requires a conda environment. This is likely one of the reasons why the previous workshop adopted STL — in a 25-minute workshop, the stability of environment setup is prioritized.

---

## Generating the STEP model

### Target model: 6-axis articulated robot arm

We recreate the [6-axis robot arm](https://zenn.dev/aws_japan/articles/0bb6554b10c6bc#%E5%BF%9C%E7%94%A8%EF%BC%9A%E3%82%88%E3%82%8A%E8%A4%87%E9%9B%91%E3%81%AA%E7%94%A3%E6%A5%AD%E6%A9%9F%E6%A2%B0%E3%81%AE3d%E3%83%A2%E3%83%87%E3%83%AA%E3%83%B3%E3%82%B0) that was introduced in STL form in the previous article, this time as a STEP using CadQuery.

### Prompt to Kiro

For reference, here is an excerpt of the prompt used in the previous article to generate the STL version of the robot arm.

```
Please build a Python script called generate_robot_arm.py that generates
a 3D model of an industrial 6-axis articulated robot arm. Use only
numpy-stl, numpy, and matplotlib.

■ Robot arm configuration (from base to tip):
1. Base (J1 axis: swivel) — fixed pedestal: cylinder diameter 300mm
   height 50mm; swivel part: cylinder diameter 250mm height 100mm
2. Shoulder (J2 axis: forward/back tilt) — joint housing: diameter
   200mm height 150mm
3. Upper arm (link 1) — length 500mm, cross-section: 150mm x 120mm
4. Elbow (J3 axis: up/down tilt) — joint housing: diameter 160mm
   height 120mm
5. Forearm (link 2) — length 450mm, cross-section: 120mm x 100mm
6. Wrist (J4/J5/J6 axes) — 3-stage cylinders
7. End effector (tool flange) — diameter 63mm (ISO 9409-1 compliant),
   6 bolt holes

■ Pose parameters:
- Make joint angles J1-J6 variables, and compute each link's position
  and orientation via forward kinematics (FK)
```

This time, we instruct Kiro to output the same shape specification as the STL version, but in STEP format.

```
Please write a script that outputs, in STEP format, the same shape
specification as the 6-axis robot arm we created previously
(demos/06_robot-arm/generate_robot_arm.py), using CadQuery.

- Generate each part (base, swivel, shoulder joint, upper arm,
  elbow joint, forearm, 3 wrist stages, flange) as an individual solid
- Compute each part's position and orientation from the joint angles
  using forward kinematics (FK)
- Assemble the parts using CadQuery's Assembly feature
- Export in STEP format
```

### Highlights of the generated code

Characteristic parts of the CadQuery script Kiro generated:

```
import cadquery as cq

# CadQuery solid modeling — difference from the STL version
def make_cylinder(radius, height):
    return cq.Workplane("XY").circle(radius).extrude(height)

def make_box(w, d, h):
    return cq.Workplane("XY").rect(w, d).extrude(h)

# Drill bolt holes in the flange — an operation that is practically
# difficult with STL
def make_flange(radius, height, bolt_r, bolt_pcd, bolt_count):
    wp = cq.Workplane("XY").circle(radius).extrude(height)
    for k in range(bolt_count):
        angle = 2 * math.pi * k / bolt_count
        bx = (bolt_pcd / 2) * math.cos(angle)
        by = (bolt_pcd / 2) * math.sin(angle)
        wp = wp.faces(">Z").workplane().pushPoints([(bx, by)]).hole(bolt_r * 2)
    return wp
```

In the STL version, triangle vertex coordinates were computed directly, but in the CadQuery version the model is built from **CAD-style operations** such as "draw a circle and extrude" or "drill a hole." CadQuery internally uses OpenCASCADE (a CAD kernel) to build solid models, so the output STEP retains B-rep (the mathematical definition of faces and edges). **This is the source of later editability**.

### Execution results

```
STEP save complete: robot_arm.step
Number of parts: 10
Part list: ['base', 'swivel', 'shoulder_joint', 'upper_arm',
            'elbow_joint', 'forearm', 'wrist_j4', 'wrist_j5',
            'wrist_j6', 'flange']
End-effector tip: (28.2, 0.0, 1156.8) mm
File size: 108.8 KB
```

A STEP file with 10 named parts was generated.

![](https://static.zenn.studio/user-upload/7ac19148b448-20260416.png)  
[Image] STEP version of the robot arm, four-view

---

## Verification and editing in FreeCAD

This is the core of this article. We open the generated STEP file in FreeCAD and perform CAD-software operations on it.

### Loading in the FreeCAD GUI

First, we open the STEP file in FreeCAD's GUI.

![](https://static.zenn.studio/user-upload/4f80068c8f90-20260416.png)  
[Image] The STEP file opened in the FreeCAD GUI

The model tree in the left panel shows the 10 parts by name (base, swivel, shoulder\_joint, upper\_arm, elbow\_joint, forearm, wrist\_j4/j5/j6, flange). Clicking a part selects it individually (forearm is highlighted in light blue in the image), and the right panel lists CAD editing tools such as "Fillet" and "Chamfer."

When an STL file is opened in FreeCAD, the model tree shows only a single mesh object, and part-wise selection and B-rep-based editing tools are not available. **This difference is the value of STEP**.

### Editing with FreeCAD's Python API

In addition to interactive editing in the GUI, script-based editing using FreeCAD's Python API (FreeCADCmd) is also possible. **For reproducibility for the blog, we executed the editing operations via the Python API this time**.

#### Editing operation 1: Adding a fillet

We add an R5mm fillet to the long edges of the upper-arm link (upper\_arm).

```
# Add a fillet with FreeCAD's Python API
edges = shape.Edges
fillet_edges = [e for e in edges if e.Length > 400]  # select long edges
filleted = shape.makeFillet(5.0, fillet_edges)
```

```
Fillet addition complete: R5mm on 4 edges
```

Because STL is a mesh (a collection of triangles), B-rep-based operations like "add a fillet to this edge" are practically difficult. STEP retains face/edge topology, so you can select edges and apply fillets precisely.

#### Editing operation 2: Adding a hole

We add a Ø16mm through hole at the center of the tool flange (the end-effector mounting face) at the tip of the robot arm. This part originally had 6 bolt holes.

```
# Add a hole with FreeCAD's Python API
center_hole = Part.makeCylinder(8, 17, ...)
new_shape = shape.cut(center_hole)  # Boolean (difference) operation
```

```
Volume before edit: 44,214 mm^3
Center hole addition complete: diameter 16mm
Volume after edit: 42,532 mm^3
```

The decrease in volume confirms that the hole was opened correctly.

![](https://static.zenn.studio/user-upload/cca27b6747b6-20260416.png)  
[Image] After editing — isometric view (fillet + hole added)

### Exporting after editing

We export the edited model in both STEP and STL.

```
STEP save: robot_arm_edited.step (102.5 KB)
STL save:  robot_arm_edited.stl  (177.8 KB)
```

Since we can save it in STEP format even after editing, it is possible to open it in yet another CAD software for further edits. However, the parametric design history is not retained each time STEP is traversed (the "dumb solid" issue mentioned earlier), so final detailed design is generally done in the CAD software's native format.

---

## Comparison with the STL version

![](https://static.zenn.studio/user-upload/d25d621ba9b6-20260416.png)  
[Image] STL version vs. STEP version comparison

|  | STL version (previous) | STEP version (this time) |
| --- | --- | --- |
| File size | 60.6 KB | 108.8 KB |
| Number of triangles | 1,240 | 3,640 (after STL conversion) |
| Part information | None (all parts merged into a single mesh) | 10 parts (with name, volume, surface area) |
| Adding fillets | Approximately possible in mesh editors, but with precision limits | Added precisely on a B-rep basis |
| Adding holes | Boolean operations are possible but mesh quality tends to degrade | Added accurately with Boolean operations |
| Editing in CAD software | Only as a mesh | Feature addition confirmed in FreeCAD |
| Generation library | numpy-stl (single pip install) | CadQuery (conda required) |

The difference in triangle count comes from different tessellation (mesh subdivision) settings when converting from STEP to STL. STEP files themselves contain no triangles; curved surfaces are retained as mathematical definitions (NURBS and so on).

---

## Discussion

### Position in the design process

```
[Shape exploration / concept review] -> [Detailed design] -> [Drawings] -> [Manufacturing]
 ^ Previously (STL)                    ^ This time (STEP)
 View only                             Starting point for edits in CAD software
```

The previous STL output covered up to the "shape exploration" phase. With this STEP output, we have reached the point where AI-generated models can be imported into CAD software and used as a starting point for editing with feature additions and Boolean operations.

That said, opening in STEP does not mean you can freely edit anything. What we demonstrated this time is the **addition of new machining operations** such as "attaching a fillet" or "drilling a hole." On the other hand, the operation "change an existing hole's diameter from 10 mm to 12 mm" is not easy. STEP does not record the design step "a Ø10mm hole was drilled here," so from the CAD software's perspective, it is just "a lump that happens to have this shape." If you want to change the hole diameter, you end up with the roundabout procedure of first filling in the hole and then redrilling at 12 mm.

With SolidWorks' native format (.sldprt), the feature "hole: diameter 10mm" remains in the design history, so it is enough to rewrite 10 to 12. STEP does not have this. That is why it is called a "dumb solid" in the industry.

In other words, the realistic workflow is to use AI-generated STEP models as the "starting point of a shape," and then have humans proceed with detailed design in CAD software.

### Integration into existing CAD software

Three approaches are conceivable for integrating this method into existing CAD workflows:

1. **STEP import method** (demonstrated this time): Kiro → CadQuery → STEP → import into CAD software
2. **API code generation method**: Have Kiro write API code for the target CAD software and run it directly
3. **MCP integration method**: Build an MCP server for the CAD software and operate it directly from Kiro

MCP (Model Context Protocol) is a standard protocol for AI assistants to integrate with external tools, and Kiro supports it too. If an MCP server for a CAD software is realized, interactive design operations like "add a Ø20mm hole to the flange" → check the result → "offset the hole position by 10mm in the X direction from the center" become possible. At present, there are almost no MCP-capable CAD software products, but for software with rich Python APIs like FreeCAD, building your own MCP server is technically feasible.

---

## Summary

In this article, going one step beyond the previous STL output, we demonstrated the following:

* **Generated a STEP-format 3D model with Kiro + CadQuery** (10 parts, 108.8 KB)
* **Loaded the STEP in FreeCAD and confirmed in the GUI that part-wise selection/editing is possible**
* **Executed fillet and hole additions via FreeCAD's Python API**
* **Re-exported the edited model in STEP/STL**

As AI-generated 3D models move from "view-only" STL to "usable as a starting point in CAD software" STEP, they can be connected to real CAD workflows. The generated STEP is a "dumb solid" without parametric history, but the workflow of bringing it into CAD software as a shape starting point and then having humans proceed with detailed design from there is practical enough.

As a sequel, we published an article that runs structural analysis (CAE) with Kiro on this STEP model. It verifies, end-to-end, whether AI-edited shapes actually satisfy strength and stiffness requirements.  
👉 [AI Designs, AI Verifies — Robot Arm CAE with Kiro × FreeCAD FEM](https://zenn.dev/aws_japan/articles/a5cd987ecb59ff)

And in the 4th article of the series, we brought the robot arm whose strength was verified above into NVIDIA Isaac Sim / Isaac Lab, and had Kiro execute reinforcement learning (PPO, 4,096 envs in parallel) for suction-cup pickup of a cube. We reached the point where the AI itself learns "how to move" the 3D shape edited in this article.  
👉 [AI-Designed Robot × 4,096-Parallel RL on NVIDIA Isaac — Results](https://zenn.dev/aws_japan/articles/096dec97613a01)
