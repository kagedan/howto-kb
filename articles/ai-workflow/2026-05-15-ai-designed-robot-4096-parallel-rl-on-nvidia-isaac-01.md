---
id: "2026-05-15-ai-designed-robot-4096-parallel-rl-on-nvidia-isaac-01"
title: "AI-Designed Robot × 4,096-Parallel RL on NVIDIA Isaac — Results"
url: "https://zenn.dev/aws_japan/articles/428a16622a29f8"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

## Introduction

This article is the 4th installment of the **Kiro × Design & Development series**.

![](https://static.zenn.studio/user-upload/8a53ad41a86d-20260515.png)

In this series, we use AWS's AI coding assistant "**[Kiro](https://kiro.dev/)**" to carry out design and analysis tasks for manufacturing, driven only by natural-language instructions.

Up to this point, we have covered the design process of "AI performs CAD editing → AI performs strength verification." This time is the continuation: **we move the robot arm completed in FreeCAD over to NVIDIA Isaac Sim / Isaac Lab, and train it to pick up a cube** — the "motion side" of the story.

Specifically, we ran 4,096 robots in parallel as physics simulations on a single GPU, and had them learn suction-cup pickup using the reinforcement learning algorithm PPO (Proximal Policy Optimization). Starting from random motion in the early phase of learning, we finally achieved the following two-stage success rates:

* **Fraction of time the cube was lifted more than 10 cm from the floor (lifted rate): 91.5%**  
  — the "grasp and lift" motion is working
* **Fraction of time the cube, after being lifted, was held within 10 cm of the in-air target position: 77.9%**  
  — just under 80% of the time, the cube is also being carried to the target position

> Note: In this article, Claude Opus 4.7 is used as the foundation model for Kiro CLI. The quality and behavior of generated code may vary depending on the model version.

**[Image] 4,096 robots in reinforcement learning**  
![](https://static.zenn.studio/user-upload/13b39ebd288f-20260512.png)

**[Video] Comparison of immediately after training start (Step 0) vs. training completion (Step 120,000)**  
<https://youtu.be/F5uroi-PkTY?si=9oEPhgIQQWEHTv_P>

---

## Today's flow

```
Step 1: Add a suction pad to the STEP from the CAD editing edition
        -> convert to URDF
Step 2: Deploy the Isaac Sim environment using the AWS official
        workshop CFn
Step 3: Kiro autonomously resolves EC2 sizing and the URDF importer
        issue
Step 4: Derive a suction-cup pickup task from Isaac Lab's built-in
        Lift task
Step 5: PPO training with 4,096 envs in parallel (about 5 hours,
        120,000 steps)
Step 6: Record inference videos and evaluate quantitatively with the
        trained model
```

* **Step 1** starts from the STEP generated in the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8), reusing the same aluminum 6061-T6 material parameters as the [CAE analysis edition](https://zenn.dev/aws_japan/articles/0bb26610096298).
* **Steps 2–3** are covered in detail in the "Environment setup" section below.

---

## Environment setup — Kiro tunes the workshop's CFn

The Isaac Sim / Isaac Lab base environment was deployed based on the CloudFormation template (`IsaacLabEnvSetupHumble.yaml`) distributed in the AWS official workshop [**NVIDIA Omniverse on AWS: An Isaac Lab Deployment Lab**](https://catalog.us-east-1.prod.workshops.aws/workshops/075ce3fe-6888-4ea9-986e-5bdd1b767ef7/en-US).

What the CFn automatically builds:

| Resource | Content |
| --- | --- |
| EC2 | Initially g6.12xlarge (NVIDIA L4 GPU ×4), with Amazon DCV remote desktop |
| Software | Isaac Sim 4.5 Docker image, Isaac Lab repository, skrl |
| GPU stack | NVIDIA driver 570, Vulkan (for the Isaac Sim renderer) |
| Storage | S3 bucket, ECR registry |
| Distributed training | AWS Batch job definition, IAM Role |

Building on this stack, we conveyed to Kiro the objective of this article (reinforcement-learning edition) — "train a suction-cup gripper to pick up a cube with 4,096 envs in parallel" — and Kiro **autonomously performed the following adjustments and problem solving** while looking at the post-deployment environment.

### Autonomous escalation of EC2 sizing

> **Glossary**
>
> * **NVIDIA L4**: A data-center GPU suited to AI inference and small- to medium-scale training. Isaac Sim / Isaac Lab's parallel physics simulation can also realistically run up to around 4,096 envs on a single L4.
> * **EC2's `g6.*xlarge` family**: AWS's GPU instance family equipped with L4. As the size grows, not only CPU and memory but also the number of GPUs increases — `g6.4xlarge` has L4 ×1, `g6.12xlarge` has L4 ×4, and so on.
> * **InsufficientInstanceCapacity**: An AWS error meaning "this instance type has no free space on the physical servers in this region / AZ right now." It often occurs due to temporary capacity shortage, and trying a different type or AZ often resolves it.

The initial g6.12xlarge (L4 ×4) from the CFn hit `InsufficientInstanceCapacity` (no free space) in us-east-1a and could not be launched. Kiro judged as follows and automatically resized:

> "4 GPUs is overkill for the training scale of this article; L4 ×1 + many parallel envs (Isaac Lab's 4,096 envs is a scale that runs on a single GPU) is sufficient. AWS manages EC2 physical-server pools separately per instance type, so a different size (L4 ×1 class such as g6.16xlarge) may be in a different pool and have free space."

As a result, it escalated in four steps as follows, and finally launched successfully on g6.16xlarge:

| Attempt | Type | L4 GPUs | vCPU / Memory | Unit price (us-east-1) | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | g6.4xlarge | 1 | 16 / 64GB | $1.58/h | Insufficient |
| 2 | g6.8xlarge | 1 | 32 / 128GB | $2.01/h | Insufficient |
| 3 | g6.12xlarge | 4 | 48 / 192GB | $4.60/h | Insufficient |
| 4 | **g6.16xlarge** | **1** | 64 / 256GB | **$3.40/h** | **✅ Launched** |

### Missing URDF importer issue on Isaac Sim 4.5

> **Glossary**
>
> **URDF (Unified Robot Description Format)**: An XML-based file format widely used as a standard in the robotics industry. It describes a robot's joint structure, link shapes, masses, inertia, and so on. Many tools, including ROS, Isaac Sim, and Gazebo, can read URDF and place a robot. This time, we convert the STEP (CAD shape) made in the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8) into URDF and bring it into Isaac Sim.

When we tried to build a URDF from the STEP in the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8) and load it into Isaac Sim, it turned out that the Isaac Sim 4.5 deployed by the CFn **does not contain the URDF importer extension (`isaacsim.asset.importer.urdf`)**. Kiro investigated and resolved this as follows:

1. Investigated extensions inside the container → confirmed that only `exporter` exists
2. Pulled the upstream `nvcr.io/nvidia/isaac-sim:4.5.0` and verified → same, not present
3. Tried `pip install isaacsim-asset-importer-urdf` on PyPI → no matching package
4. Judged the alternative `yourdfpy` as parsing-only, without USD conversion capability
5. Hypothesis: "The Isaac Lab official Docker (`nvcr.io/nvidia/isaac-lab:*`) may contain it"
6. Pulled `nvcr.io/nvidia/isaac-lab:2.0.0` → **confirmed the URDF importer extension, conversion succeeded**

Kiro pushed this flow of "root-cause identification → enumerating alternatives → verification → adoption" through to completion.

---

## STEP → URDF conversion, and weight reduction by hollowing

### First: Why we chose a suction cup

Initially, we were going to attach a **two-finger gripper** (a device that pinches the object) to the robot arm from the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8) and train that. The reason was that Isaac Lab's standard sample `Isaac-Lift-Cube-Franka-v0` uses the Franka Panda robot (two fingers), so our judgment was "if we use the same configuration, we can reuse the reference implementation to the maximum."

![](https://static.zenn.studio/user-upload/05e37108b699-20260512.png)

> The Franka Panda robot (two fingers)

However, in early training with two fingers, the policy had to simultaneously learn three factors — "grip strength, opening/closing timing of the fingers, and contact friction" — which was very hard. After consideration, we switched to a suction cup for the following reasons.

* **A 6-axis arm + suction cup is a common configuration at industrial sites** (cardboard transfer in logistics warehouses, ready-meal packing in food factories, semiconductor panel transfer, automotive glass transfer, etc.)
* The flange follows ISO 9409-1, a standard designed from the start for "end-effectors being swapped depending on the use case"
* From an RL-learning standpoint, **suction is dramatically easier to learn** because it requires only an ON/OFF binary.

### Additional design of the suction pad

To the `robot_arm_edited.step` (10-part configuration) generated in the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8), we **added 1 suction pad part**, bringing the total to 11 parts. The suction cup is parametrically designed in CadQuery, and mounted to the existing flange's ISO 9409-1 bolt holes.

**[Image] The robot arm with the suction pad added**

> Rendered in Python (numpy-stl + matplotlib) in the pose computed via forward kinematics from the URDF. 6 axes + suction pad = 11 links total; total mass 20.4 kg thanks to hollowing. Orange at the tip is the flange; red is the newly added suction pad. The pose is the initial pose at training time (j2=0.6, j3=1.5, j5=0.9 rad).

![](https://static.zenn.studio/user-upload/177ab6934db2-20260512.png)

### Weight reduction: hollowing, from 85 kg to 20 kg

The robot arm used in the [CAE analysis edition](https://zenn.dev/aws_japan/articles/0bb26610096298) was a "solid aluminum model with material fully filled inside," and weighed **85 kg in total**. This was 3–4 times heavier than real industrial robots (FANUC M-20iA at 20 kg, Yaskawa MH24 at 30 kg, etc.), and when we brought it as-is into Isaac Sim, a problem occurred: **it was too heavy, and the training did not progress at all**. ([Reason why the CAE analysis edition chose the solid model here](https://zenn.dev/aws_japan/articles/a5cd987ecb59ff#:~:text=%E3%81%95%E3%82%8C%E3%81%BE%E3%81%99%E3%80%82-,%E6%9C%AC%E8%A8%98%E4%BA%8B%E3%81%AE%E4%BD%8D%E7%BD%AE%E3%81%A5%E3%81%91%EF%BC%88%E3%83%A2%E3%83%87%E3%83%AB%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6%E3%81%AE%E6%B3%A8%E8%A8%98%EF%BC%89,-%E4%BB%8A%E5%9B%9E%E8%A7%A3%E6%9E%90%E3%81%99%E3%82%8B))

Almost all of Isaac Lab's official training examples use robots of 35 kg or less (Franka Panda 18 kg, Kinova Gen3 8 kg, Unitree G1 humanoid 35 kg, etc.), and 85 kg was outside the empirical range.

So we took the following 3 steps to **reduce the weight from 85 kg to 20 kg**.

1. Based on the 1,690× safety factor of the [CAE analysis edition](https://zenn.dev/aws_japan/articles/0bb26610096298) (stress margin over 1,000× for a 10 kg payload), we judged that **even a hollow structure with 5 mm wall thickness would maintain a safety factor of 100×**.
2. Modified the CadQuery script to hollow out each link (added new `hollow_cyl` and `hollow_box` functions).
3. Recomputed the moments of inertia for the hollow shapes.

**This got close to the Franka Panda (18 kg) class, and brought it right into the middle of Isaac Lab's empirical range**. A 5 mm wall thickness is a typical value consistent with real industrial arms and is also valid as a design. Only after doing this did RL training start to realistically progress.

### URDF generation flow

What we had Kiro write:

1. **Per-part STEP output with CadQuery** (11 parts: base, swivel, shoulder, upper\_arm, elbow, forearm, wrist\_j4/j5/j6, flange, suction\_pad), hollowed version
2. **Convert each STEP to STL via FreeCAD's Python API** (Isaac Sim can read STL)
3. **Generate the URDF XML**, computing mass and inertia per link

### Why are mass and moment of inertia necessary?

To make a robot move realistically in physics simulation, "mass" and "moment of inertia (resistance to rotation)" of each part are necessary. For example, if the weight of the upper arm is unknown, the simulator cannot compute the acceleration or reaction force when the arm swings, and its behavior under gravity or external force becomes nonsense.

So in step 3 above, using the same aluminum 6061-T6 density of 2,700 kg/m³ as in the [CAE analysis edition](https://zenn.dev/aws_japan/articles/0bb26610096298), we write into the URDF **mass = density × volume** (where **part volume** is computed by CadQuery from the hollow shape) and **moment of inertia = automatically computed from the shape and mass distribution**. By unifying the material parameters with Parts 1–3 of the series, the same robot is kept running with consistent physical properties.

---

## Task definition in Isaac Sim — Derived from the built-in Lift task

### What are Isaac Sim / Isaac Lab?

**Isaac Sim** is NVIDIA's physics simulator for robots. A key feature is that many robots can be run in parallel on GPUs to mass-produce training data.

**Isaac Lab** is a **robot learning framework** that runs on top of it, supporting a variety of methods to teach robot behavior — reinforcement learning, imitation learning, kinematics-based control, demo data collection, and so on. This article uses reinforcement learning (RL), but imitation learning (having the robot mimic a human demo) and a fine-tuning foundation for VLA (Vision-Language-Action) models are other use cases, making it broadly applicable.

Sample tasks with the Franka Panda robot — Lift (pick up an object), Reach (extend the hand to a target position), Push (push an object) — are provided out of the box. In this article, based on one of them, `Isaac-Lift-Cube-Franka-v0` (a task to lift a cube and carry it to a target position), we newly created a **suction-cup pickup task** (`Isaac-Blog4Suction-H-v0`), using our custom robot arm from the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8) + a suction cup instead of the Franka.

### Physics model of the suction cup — our own SimpleSuction

Isaac Sim originally provides an API called `SurfaceGripper` for suction cups, but **we could not get it to work with this article's robot** (see the troubleshooting chapter later for the cause and the story of giving up). So we had Kiro write our own suction logic, `SimpleSuction`.

Paraphrasing the behavior:

```
Every step:
  1) The AI (policy) outputs, in addition to "the position it wants to
     move the suction to," "whether to turn the suction ON or OFF at
     this moment"
  2) Compute the distance d between the suction tip and the cube
  3) If the AI outputs "ON" and d < 5 cm -> consider suction
     established (state=1)
     (Too far away, it does not stick — the same behavior as a real
      suction cup)
  4) While suction is established, update the cube's position and
     orientation every step as if it were "physically stuck" to the
     suction tip (1:1 tracking)
     -> If the suction moves, the cube follows as-is. While suction is
        established, the cube does not "come off."
```

This is a simplified model, inside the simulation, of the behavior of a real electric suction pump (ON/OFF of vacuum suction to grasp/release objects).

### Observation, action, reward — the three elements of reinforcement learning

In reinforcement learning, the AI (a neural network called a policy) learns while exchanging the following three things:

* **Observation** = **what the AI sees every step**. The current state of the robot and the task situation.
* **Action** = **the command the AI issues every step**. Input to the robot.
* **Reward** = **a number** that tells whether the action was good or bad. Positive means "did something good," negative means "did something bad." The AI learns to maximize the total.

The settings of this article are as follows:

**Observation (19 numbers)**

* The angles of the 6 joints (how are they bent now)
* The angular velocities of the 6 joints (how fast are they bending)
* The 3D position of the cube (x, y, z)
* Suction state (ON=1 / OFF=−1)
* The 3D position of the target (x, y, z)

**Action (7 numbers)**

* "Next desired angle" commands for the 6 joints
* ON / OFF command for the suction (positive value = ON, negative value = OFF)

**Reward (sum of 5 items)** — Based on the design of Isaac Lab's Franka Lift task:

| Item | Meaning | Coefficient |
| --- | --- | --- |
| reaching | Plus as the suction gets closer to the cube | × 1.0 |
| grasping | Plus just by having suction established (state=1) | × 3.0 |
| lifting | Plus if the cube has been lifted more than 10 cm from the floor | × 15.0 |
| goal tracking | Plus as the cube approaches the target position | × 16.0 |
| curriculum penalty | **Minus** when joint motion is too abrupt | Strength switches by learning phase |

**curriculum penalty** is a mechanism that "changes the strength of the penalty midway through training." This follows Isaac Lab's official Franka Lift sample (`franka_lift_env_cfg.py`). Specifically:

* Early in training (0 to 10,000 steps): penalty is extremely weak (−1e−4)  
  → The AI can boldly try various motions (exploration)
* Late in training (from 10,000 steps onwards): penalty is 1,000× stronger (−1e−1)  
  → Abrupt motions are penalized, so the AI converges to **smooth motion**.

Without this, the AI would learn a policy that swings the joints around to reach the target faster, resulting in "oscillating / jerky" motion. Conversely, if the penalty is strong from the start, the AI gives up before exploring how to move and learns that "not moving at all is the best bet." **Switching the penalty at the right timing** is the key.

---

## Parallel reinforcement learning with 4,096 robots

### Why run 4,096 robots in parallel?

In reinforcement learning, "number of trials" is everything. If you train with only one robot, you can only process trials (1 episode = 10 seconds) sequentially, and it takes a long time to accumulate enough experience.

Here, by leveraging the parallel computing power of GPUs, you can **run 4,096 of the same robot on a single GPU simultaneously**. Each robot tackles the task with independent initial conditions (cube position, target position), so:

* 4,096 experiences collected in one step → **learning is 4,096× faster**
* The cube position and target position vary widely, so the policy, trained once, can handle diverse situations
* With only one robot, there is a risk of overfitting to "conditions that happen to be easy," but with 4,096 robots these are averaged out

**"4,096 robots" is effectively the default in Isaac Lab's standard sample**. The number seems arbitrary but has reasons:

* `4,096 = 2^12`, which is **compatible with GPUs' parallel compute architecture (thread blocks in units of 16/32/256)** as a power of two. Decimal round numbers such as 1,000 or 10,000 would trigger internal padding (extra computation) and lower efficiency.
* On the 24 GB VRAM of a single L4 GPU, **4,096–8,192 envs is near the realistic upper bound for fitting both the physics simulation and the neural network**.
* The official Franka Lift sample in Isaac Lab is also standardly trained with `--num_envs 4096`, and is tuned based on the empirical observation that "Pick motion emerges in 15 minutes to 1 hour at 4,096 envs."

### Variation in initial conditions (domain randomization)

During training, at every episode reset (every 10 seconds), we randomly set the following:

| Item | Range |
| --- | --- |
| Cube initial position x | 0.80 to 0.86 m (in front of the robot, 6 cm wide) |
| Cube initial position y | −0.03 to 0.03 m (6 cm wide left-right) |
| Cube initial position z | Fixed at 0.02 m above the floor |
| Target position x | 0.70 to 0.90 m (20 cm wide) |
| Target position y | −0.05 to 0.05 m (10 cm wide left-right) |
| Target position z | 0.30 to 0.50 m (height 30–50 cm wide, in the air) |

Since these are **sampled independently from these ranges in each of the 4,096 envs**, a single training step provides simultaneous experience of combinations of "various cube positions × various target positions."

### Training settings

| Item | Value |
| --- | --- |
| Number of parallel environments | 4,096 envs |
| Total number of steps | 120,240 steps (4,096 × 120,240 ≈ 500 million trial experiences) |
| PPO library | skrl (Isaac Lab's standard) |
| Episode length | 10 seconds (600 steps) |
| Training time | About 5 hours (g6.16xlarge, L4 ×1) |
| Cost | About $17 per training run |

### Progress of training — debugging with videos

We instructed Kiro to automatically record a video of 1 env out of the 4,096 envs at step 0 / 30,000 / 60,000 / 90,000 / 120,000 during training.

The reason videos are needed is that **numerical logs you can collect during training (mean reward, loss values, etc.) alone do not tell you how the robot is actually moving**. Even if the reward rises nicely, when you watch the video there are often anomalies like "the arm is just being swung in strange directions" or "the cube is buried in the floor." **Humans and Kiro watching the videos to directly verify behavior while debugging** is indispensable in RL development.

For a comparison video between immediately after training start (Step 0) and training completion (Step 120,000), please see the YouTube video at the beginning of this article.  
From the initial random motion, by the time training is complete, you can see that most robots successfully perform pickup.  
However, after successful pickup, some robots exhibit small oscillations. We examine the nature of this oscillation in the troubleshooting chapter later.

### Inference quantitative results

Detailed evaluation of the final behavior was measured with **inference running a 4-env ×300-step simulation while following each with a camera**, using the trained model (best agent = checkpoint at step 72,000):

![](https://static.zenn.studio/user-upload/c88ca8222c82-20260512.png)

| Metric | Value | Meaning |
| --- | --- | --- |
| **lifted rate** (cube\_z > 10 cm) | **91.5%** | Fraction of steps in which the cube was lifted more than 10 cm from the floor |
| **target within 10 cm rate** | **77.9%** | Fraction of steps in which the cube was held within 10 cm of the target coordinates |
| **suction rate** (suction state=1) | 92.2% | Fraction of steps in which the suction was stuck to the cube |
| **minimum distance d\_cube\_target** | 2.2 cm | Closest approach distance from cube to target |
| **average pick-up height** | 45.2 cm | Average cube altitude from the floor |

> **Why "evaluate with 4 envs"**: The **aggregate judgment** of whether training succeeded is based on "mean reward" and "mean episode length" over all 4,096 envs, which Isaac Lab automatically outputs to TensorBoard during training (we had confirmed in advance that the final reward target was reached in this article). On the other hand, for **carefully examining the details of behavior visually + numerically**, too many envs makes videos too many to watch, so we take a representative sample of 4 envs × 300 steps (= 5 seconds × 4 robots = 20 seconds worth of data). This follows the same flow as the evaluation procedure in Isaac Lab's official samples.

> **What "within 10 cm" accuracy means**: Industrial robots' positioning accuracy is generally ±0.05 to ±0.5 mm, so 10 cm in this article is a fairly coarse metric from a real deployment perspective. However, **for research and textbook-level pick & place tasks in reinforcement learning**, a 5–10 cm arrival rate is the standard evaluation metric, and Isaac Lab's official Franka Lift sample uses the same threshold. The industry sense seems to be that "this is sufficient to confirm whether RL has acquired pick & place motion." At the stage of deploying to real hardware, the usual flow is to raise the accuracy by an order of magnitude or more with Sim2Real transfer + visual servoing, etc.

---

## All the code so far was written by Kiro

Looking back, **no human wrote a single line of Python / YAML / shell scripts**. Listing what Kiro wrote and executed:

| Step | What Kiro implemented |
| --- | --- |
| URDF generation | Hollowing and STEPifying 11 parts with CadQuery + FreeCAD Python API, STL conversion, assembling the URDF XML |
| Suction design | Adding the pad shape with CadQuery, mounting to ISO 9409-1 flange bolt holes |
| Weight reduction | Hollowing from 85 kg to 20 kg (5 mm wall thickness design, mass/inertia recomputation) |
| Isaac Lab task | Gym environment `Isaac-Blog4Suction-H-v0`, 19-dim observation / 7-dim action / reward function |
| Suction physics | `SimpleSuction` class (alternative implementation, since the upstream SurfaceGripper did not work) |
| Training script | `train_blog4_suction_H.py` (skrl PPO) |
| Inference / diagnosis | `play_blog4_suction_H.py`, `diag_H_verbose.py`, intermediate-checkpoint comparative analysis, and so on |
| Remote execution | Launching Docker containers via `aws ssm send-command`, automating training / inference / S3 sync / video retrieval |

Code specific to this article alone amounted to about 6,000 lines. Zero lines were written by humans.

---

## Reinforcement learning didn't get there in one shot — 15 rounds of trial and error

It took 15 versions of trial and error to succeed in suction-cup pickup. We introduce the highlights.

### Points where we stumbled hard

**① Isaac Sim's upstream suction API (SurfaceGripper) did not work**

Isaac Sim originally provides an API called `SurfaceGripper` for suction cups, and in theory you should be able to implement suction behavior using it — but we could not get it to function with this article's robot.

SurfaceGripper's internal design uses a **"raycast method"** — **it shoots a "ray" straight down from the suction cup, and if there is an object within a certain distance, it sticks to it** (similar in concept to a real suction sensor detecting vacuum pressure, substituted in the simulator with ray hit-testing). However, with this article's robot, the behavior was either that the raycast did not hit the cube, or that even when it hit, the process that dynamically creates the constraint for suction (`D6Joint`) failed.

Kiro investigated and modified over 14 items — the physics settings on the USD, the joint drive, ClearanceOffset (allowable distance between suction and object), suction orientation (Z+ or Z−), body mass, etc. — but **the root cause could not be identified in the end**. The major factors likely included:

* Unlike robot shapes in official samples such as Franka Panda, the combination of this article's custom robot + custom suction shape deviated from the geometric relationships the API assumes.
* The internal implementation of Isaac Sim 4.5's SurfaceGripper extension has varied across versions, and there may have been implicit prerequisites not documented.

We gave up after 9 versions, and pivoted to our own `SimpleSuction` (a simple scheme that establishes suction purely by distance check, described above).

**② Suction works, but the cube is not carried**

Even though SimpleSuction achieved suction (state=1) 100% of the time, the cube was not carried to the target position. In the videos, the arm just stood still while maintaining suction.

Kiro numerically analyzed the breakdown of rewards, and the cause was that **the initial design of the lifting reward was too simplistic**. The design at the time was an **ON/OFF (step function) type reward**: "+15 if the cube is lifted more than 10 cm from the floor, 0 otherwise." Once the cube was lifted, the structure gave the AI absolutely no incentive to "put it down." Since +15 kept flowing in just by maintaining the lifted state, the optimal solution the AI learned was to **"hold the cube high without moving the arm."**

> **Why we chose this simplistic design**: This step-function-type lifting reward was directly ported from the standard design of Isaac Lab's official Franka Lift sample (`franka_lift_env_cfg.py`) mentioned earlier. In Franka Lift, **a two-finger gripper physically pinches and holds the cube**, so there is a risk of the fingers opening during transport and the cube falling, which naturally requires the policy to learn "motion for carrying." However, this article's SimpleSuction has a physics model where "during suction, the cube is stuck 1:1 to the suction cup," so **the cube absolutely never falls**, and "hold it up, don't move" became a comfortable optimal solution. **Even with the same reward design, the optimal solution that emerges flips depending on the physics model** — a lesson about the interaction between physics and reward design.

Ideally, the reward for "carry to the target position" should be made sufficiently larger than the reward for "holding it up," but in the initial design this balance was completely reversed, and **holding it up was more lucrative**. The textbook lesson is that RL reward design should be built while imagining "what is the worst shortcut the AI could find."

### Why some robots still oscillated after training completion

This is a phenomenon caused by several AI- and physics-sim-specific elements **forming a closed loop**, and the flow is as follows.

1. **The AI's commands retain a small amount of random noise every step** (in reinforcement learning, "everything deterministic" cannot be learned, so it is normal for the policy to issue commands stochastically). Even late in training, this noise does not go completely to zero.
2. This article includes a rule that **"penalize if the command changes abruptly compared with the previous step"** (action rate penalty). However, this only looks at the difference from the 1 step before. In other words, **alternating patterns that return to the original in 2 steps, such as "+0.05 → −0.05 → +0.05 → −0.05," slip past the penalty**. As an optimal solution, the AI converges to such alternating patterns.
3. This small alternating motion at the joint level is **amplified at the arm tip** like the tip of a pendulum, becoming oscillation of a few cm in amplitude.
4. This article's suction is specified to **stick 1:1 to the cube as-is**, so if the arm tip oscillates, the cube oscillates by the same amount.
5. The cube position is used in reward calculation, and in particular there is a "precise tracking" item where the value changes sharply within 5 cm of the target position. So if the cube oscillates on the 1 cm scale, the reward also fluctuates jaggedly, and **the AI reacts to those fluctuations by oscillating the commands further** — a **self-reinforcing loop** is formed.
6. The **only brake** to suppress all of this is the mechanism "negative reward if joint motion itself is large" (joint velocity penalty). When this works well, oscillation is suppressed, but weakening it fails to suppress it.

### Why we judged it "task complete" despite oscillation

This article's evaluation metric is the "fraction of time the cube is within 10 cm of the target position," which was 77.9% (the standard pass line in RL research is roughly 70–80%).  
In other words, the AI is in a state of **"jerkily, but for most of the time, keeping the cube near the target position."**

Looking at the properties of the oscillation numerically:

* Amplitude: **2.7 cm per step** (about 1/4 of the 10 cm allowable target range — i.e., even when oscillating, it stays within the allowable range)
* Reversal rate: **63%** (going back and forth roughly half-and-half in plus and minus directions)
* As a result, the **effective travel per second is only 7 mm** (because the oscillations go back and forth and cancel out)

As an analogy, it is close to the state of a magician walking with a cup on their palm — **the hand wobbles finely, but the cup does not fall and stays roughly in place**.

### Wouldn't it be better to eliminate the oscillation completely?

Exactly, but we did not get there. **If the brake that suppresses oscillation (joint\_vel penalty) is made too strong**, the AI judges "staying still avoids penalty, so that's more profitable," and in envs with low target positions, learning **converges to a policy that does not move the cube** (a so-called local optimum). As a result, the arrival rate drops.

**The core difficulty of this task is achieving both "not oscillating × moving the cube"**, and the setting of this article is the result of balancing this — "oscillation within the allowable range + a passing level of arrival rate." To aim for higher precision, there is room to refine the reward design further, or to change the policy architecture.

---

## On how to entrust tasks to Kiro

The author is not an expert on reinforcement learning for robots. But with Kiro, it investigates Isaac Lab's documentation and existing implementations, sets up the procedure, writes the code, runs it, sees the results, and proposes the next move — it does all of this in one sweep.  
So at first, I **took the easy path, thinking "if I leave it to Kiro, it'll do well,"** and ran trials by going along with Kiro's proposals. Even when training failed, Kiro would say "the cause is here, I'll fix it this way next," and I would rerun training accordingly — that was the flow.

Gradually, however, a sense of unease emerged.

* Training was promised to "be solved this time," but it failed again
* The cause was explained differently each time, or contradicted the previous hypothesis
* A version that changed 3 parameters at once failed, and it was impossible to isolate "what was responsible"

Ordinarily, "change only one variable at a time in experiments" is basic. I knew this in my head too, but thinking "it's a side gig trial and I want to be lazy" and "Kiro must know more about fine control parameters," **I handed over my own judgment**.

Midway, I **got fed up and started grilling Kiro on the situation in detail**: "What's the basis for that change? Show me numbers." "Where in the logs is the evidence?" "There has to be a way to check with an existing checkpoint before running training." Through the exchanges, I myself gradually came to understand Isaac Lab's mechanisms, PPO's behavior, and the theory of reward design a little (still far from enough), and from there I began to propose directions myself — **"shouldn't we do it this way?"**

* **Don't declare "the cause is this" based on shallow guesswork — separate it with measured data**  
  — Avoid the loop of "I think X is probably the cause" → set direction → run → miss → form another hypothesis
* **An overly heavy / overly large model may not allow RL to converge — consider weight reduction early**  
  — Don't persist with 85 kg; when we hollowed it to 20 kg, training suddenly went through.
* **Before running training, push first to see how much can be learned with what you already have (existing checkpoints, logs, TensorBoard)**  
  — One training run is 5 hours / $17. Before running one, always check whether **a zero-cost verification method** remains.

Kiro's speed at computation, coding, and investigation is very fast, but it often repeats irrational trials many times without being careful.  
Of course, **you can't entrust trials at this level entirely to an AI with the current level of capability; without the human grilling on the overall direction and on "is that actually correct to begin with,"** you end up taking detours.

---

## Summary

In this article, we demonstrated the following:

* **Turned the STEP from the [CAD editing edition](https://zenn.dev/aws_japan/articles/051fb7bbd1fdd8) + suction pad into a URDF, and put it into physics simulation in Isaac Sim 4.5 + Isaac Lab**
* **Trained with PPO on 4,096 envs in parallel, achieving target arrival rate 77.9% and lifted 91.5% at 120,000 steps**
* **Kiro autonomously executed even environment setup (reusing the CFn, EC2 resizing, investigation/resolution of the missing URDF importer)**
* **Succeeded at cube pickup reinforcement learning after more than 15 rounds of trial and error**
* **Analyzed the oscillation phenomenon theoretically** (2-step legalization of PPO Gaussian noise × action\_rate penalty); physically judged not to affect target holding

Through this series, we have shown that the big manufacturing-engineering workflow of **design → CAD editing → CAE → reinforcement learning** can be driven from start to finish, purely from natural-language instructions to Kiro.

---
