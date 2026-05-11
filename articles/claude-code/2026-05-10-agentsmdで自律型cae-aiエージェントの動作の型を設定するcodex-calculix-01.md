---
id: "2026-05-10-agentsmdで自律型cae-aiエージェントの動作の型を設定するcodex-calculix-01"
title: "AGENTS.mdで自律型CAE AIエージェントの動作の型を設定する：Codex + CalculiX"
url: "https://zenn.dev/ms_ai/articles/6ed4f9e640ed26"
source: "zenn"
category: "claude-code"
tags: ["AI-agent", "GPT", "Python", "zenn"]
date_published: "2026-05-10"
date_collected: "2026-05-11"
summary_by: "auto-rss"
query: ""
---

# CAE AIエージェントの動作の型を設定する

AIエージェントを通してCAEツールを動かす場合、必ずしもCAE技術者が普段やっているような作業をトレースするとは限らず、想定外の動作をすることがあります。それを防止すべく「これは守ってほしい」という事項を`AGENTS.md`等のファイルに記述して、動作の型を設定したいと思います。

## AGENTS.mdとは？

`AGENTS.md`は、AIエージェントにおいて、**そのプロジェクト内で稼働する「AIエージェント」の定義、役割、権限などを記述したドキュメントファイル**です。  
このファイルにはエージェントの定義・役割、権限、従うべき基本動作を記述します。

プロジェクトディレクトリ直下に置いた`AGENTS.md`は、AIエージェントが何かするたびに毎回読まれるので、あまり長くせずに細かいことは別のファイルに分けて書いたほうが良いとされています。

## AGENTS.md

### CAEワークフローガイダンスを追加

プロジェクトディレクトリ直下の`AGENTS.md`に下記の項目を追加し、CAE解析の各作業段階で`docs/cae-workflows/〇〇〇.md`に書いてある指示を見てもらうようにします。  
また、プロジェクトディレクトリにおいてあるリファレンスも適宜参照してもらうようにします。

AGENTS.md（追加部分）

```
## CAE workflow guides

For each analysis work, consult the relevant guides:

- `docs/cae-workflows/analysis-planning.md`
- `docs/cae-workflows/calculix-coding.md`
- `docs/cae-workflows/result-review.md`
- `docs/cae-workflows/report-writing.md`

Use `reference/` for local manuals and verified technical references.
When selecting element types, loads, constraints, contact settings, material models, or output requests, check `reference/` when available.

For large reference lookup tasks, use the built-in `explorer` subagent when available, and bring back only concise findings and modeling implications.

Do not skip result review before writing reports.
Reports should include engineering figures, not only text summaries.
```

## チェックリストを追加

ワークフローガイダンスを書いておいても無視されてしまうことがあるため、各段階でチェックリストを作成してもらうようにします。

AGENTS.md（追加部分）

```
## CAE workflow checklist

- For each analysis case, maintain `cases/<case>/checklist.md` from `docs/cae-workflows/checklist-template.md`.
- Update the checklist after planning, coding, result review, and report writing.
- Do not finalize reports until failed checklist items are fixed or documented as limitations.
```

## cae-workflows

`docs/cae-workflows/`下に、CAE構造解析の各作業段階における指示を記述しておきます。  
なお、以下の内容はChatGPT（GPT5.5）に壁打ちしつつ筆者独自の見解を踏まえて作成したものです。

### analysis-planning.md

解析のプラン（計画）を立てる場合の動作の型を書いておきます。あまり細かくするのは良くないと思いますが、なるべく解析を行うときの抜け漏れがないようにしてみました。

analysis-planning.md

```
# Analysis planning workflow

Before creating CalculiX input files, create or update `cases/<case>/analysis.md`.

The plan must include:

1. Objective
2. Physical problem definition
3. Unit system
4. Real-world setup and modeling interpretation
5. Geometry assumptions
6. Material model
7. Element type candidates and final selection
8. Boundary conditions
9. Loading method
10. Contacts or constraints
11. Mesh strategy
12. Expected result quantities
13. Validation / sanity checks
14. Known limitations

## Element selection rule

Do not choose element types casually. 

For each analysis, justify:
- solid / shell / beam / plane stress / plane strain / axisymmetric
- linear vs quadratic
- reduced vs full integration if applicable
- compatibility with material, contact, output, and loading requirements

Check the local CalculiX references under `reference/` when available.

## Real-world condition interview

Before finalizing the analysis plan, compare the planned model with the real-world object or test setup.
Ask the user only when the missing information may change the modeling choice or engineering conclusion.
For minor missing details, make a reasonable assumption, state it clearly, and record it in `analysis.md`.

## Planning Rules

- If the analysis objective is unclear, confirm it with the user.
- Do not silently replace real-world conditions with convenient FEM assumptions.
- State the model interpretation before creating CalculiX input files.
- If assumptions are made, explain them to the user and record them in `analysis.md`.
- After creating the analysis plan, review it from the perspective of a veteran CAE engineer, identify weaknesses, and revise the plan.

## Checklist

After planning, create or update `cases/<case>/checklist.md`.
Mark the planning items completed, not applicable, or unresolved.
```

### calculix-coding.md

CalculiXのコードを書くときの型を書いておきます。  
Codexは便利なCalculiXの機能を使わずに、Pythonコードを力業で書いてしまう傾向があるので、なるべく標準機能を利用してもらうようにします。

calculix-coding.md

```
# CalculiX coding workflow

When creating CalculiX input files:

1. Prefer standard CalculiX keywords over custom Python workarounds.
2. Keep `.inp/.inc` files readable and reviewable.
3. Split inputs into:
   - `mesh.inc`
   - `materials.inc`
   - `sections.inc`
   - `bcs.inc`
   - `loads.inc`
   - `step.inc`
   - `output.inc`
4. Use named node sets and element sets.
5. Avoid hard-coded node IDs unless unavoidable.
6. Document every non-obvious modeling choice in `analysis.md`.

## Prefer solver-native features

Use CalculiX built-in capabilities for:
- distributed loads
- pressure loads
- constraints
- equations
- couplings where appropriate
- contact definitions
- output requests

Do not manually distribute loads or constraints with Python unless:
- CalculiX has no suitable native feature, or
- the approximation is intentionally part of the study.

If a custom distribution is used, explain the formulation and verify force/moment balance.

## Checklist

After creating or updating CalculiX inputs/scripts, update `cases/<case>/checklist.md`.
Document any custom workaround, hard-coded IDs, or deviation from the plan.
```

### result-review.md

解析実行後にレビューする内容を記載しておきます。Codexは動作中に勝手にプランを変えてしまうことがあるため、それについて説明を求めるようにしています。

result-review.md

```
# Result Review Workflow

Review results before writing or finalizing a report.

Result review is not only a solver sanity check.  
It must confirm that the final analysis is consistent with the original objective, plan, assumptions, and intended engineering judgment.

## 1. Check against the plan

Read `analysis.md` first.

Confirm that the final model matches the plan.

If the final model differs from the plan, record:

- what changed
- why it changed
- whether the change is technically justified
- whether the original objective is still satisfied

## 2. Check model and solver validity

Confirm:

- element type, mesh, BCs, loads, and materials are appropriate
- solver finished without unresolved serious warnings
- nonlinear convergence is acceptable when relevant
- requested outputs were actually produced

Solver completion alone does not make the result valid.

## 3. Check physical sanity

Confirm:

- reactions balance applied loads
- deformed shape is physically plausible
- displacement, stress, strain, and contact results are reasonable
- no unintended rigid-body motion, over-constraint, or modeling artifact dominates the result

## Checklist

After reviewing results, update `cases/<case>/checklist.md`.
Record review status as `Accepted`, `Accepted with limitations`, `Needs revision`, or `Diagnostic only`.
```

### report-writing.md

レポート作成時の動作について記述しています。少し長いですが、誰を対象にするかによって内容を書き分けるような指示も入れています。

report-writing.md

```
# Analysis Report Writing Workflow

Write reports as engineering analysis reports, not work logs.

Select the report audience before writing:

- CAE engineer
- Designer
- Project manager

If the audience is not specified, default to `CAE engineer`.

Use the same reviewed analysis results, but adjust emphasis, detail level, figures, and conclusion style for the audience.

## Common report contents

Every report should include:

1. Title
2. Summary
3. Objective
4. Model overview
5. Geometry and assumptions
6. Material properties
7. Element type and mesh
8. Boundary conditions and loads
9. Solver settings
10. Result review
11. Main results
12. Discussion
13. Limitations
14. Conclusion
15. Reproducibility information

Do not write the report as a chronological work log.  
Focus on final modeling choices, reviewed results, engineering interpretation, and limitations.

## CAE engineer report

Use the common contents as the standard structure.

Emphasize:

- analysis category
- software version and unit system
- element type selection rationale
- mesh strategy and mesh quality
- boundary condition and load definitions
- contact, constraints, equations, or couplings if used
- solver warnings and convergence behavior
- reaction/load balance
- result quantity definitions:
  - `.dat`, `.frd`, CGX, script, or CSV
  - integration point, element-nodal, nodal-averaged, or extrapolated
- reproducibility

The report should allow another CAE engineer to review validity and reproduce the analysis.

## Designer report

Start from the common contents, but reduce solver-specific detail.

Emphasize:

- design judgment
- critical locations
- deformation behavior
- stress, displacement, contact, or safety margin relevant to design
- comparison with allowable values or design targets when available
- cause of high stress or excessive deformation
- suggested design changes
- assumptions that affect design interpretation

Move detailed solver settings, convergence logs, and result-definition details to an appendix or omit them if not needed.

The report should help the designer decide what to change or confirm.

## Project manager report

Start from the common contents, but keep only the detail needed for project decisions.

Emphasize:

- main conclusion
- whether the result is accepted, accepted with limitations, needs revision, or diagnostic only
- confidence level
- key technical risks
- impact on design, schedule, cost, test plan, or next milestone
- open issues
- recommended next actions

Minimize detailed FEM modeling discussion unless it affects project risk or decision making.

The report should help decide what to do next.

# Figures for analysis reports

Use figures to support engineering judgment, not merely to decorate the report.

For most structural FEM reports, include the following figures when applicable:

## Required figures

1. Geometry overview
   - Show overall dimensions or key geometric features.
   - Indicate symmetry, simplifications, or omitted features if relevant.

2. Mesh overview
   - Show global mesh.
   - Show local mesh refinement around stress concentration, contact, load, or constraint regions.
   - For 2D/3D element studies, show actual FEM element edges, not plotting triangulation artifacts.

3. Boundary condition and load figure
   - Show constrained regions, loaded regions, contact pairs, coupling regions, and reference points.
   - Prefer visualizing named node sets and element sets.

4. Deformed shape
   - Show displacement magnification factor.
   - State whether deformation is scaled or true scale.
   - Use this mainly to check boundary condition behavior and global stiffness.

5. Main result contour
   - Show the primary result quantity relevant to the objective.
   - For stress and strain results, prioritize contour plots that have been extrapolated and averaged to the nodes.
   - Examples: von Mises stress, principal stress, displacement magnitude, contact pressure, reaction force distribution.

6. Critical region close-up
   - Zoom into the region controlling the conclusion.
   - Include mesh visibility when useful.
   - If necessary, illustrate the location where the maximum value was detected.

7. Reaction / load balance summary
   - Use a table or simple plot if appropriate.
   - Confirm that applied loads and reactions are consistent.

## Style

- Include modeling choices and their rationale.
- Clearly distinguish facts, assumptions, and interpretations.
- Include figures and tables when useful.

## Figure quality rules

- Draw actual element edges. Do not use plotting methods that misrepresent FEM topology.
- State whether contour values are:
  - integration point values
  - element-nodal values
  - nodal-averaged values
  - extrapolated values
- Do not compare CGX contour maxima and `.dat` integration point values without checking whether they represent the same quantity.
- Include units, scale factors, legends, and captions.
- Use consistent view orientation, color scale for before/after comparison figures.

## Checklist

Before finalizing the report, update `cases/<case>/checklist.md`.
The report is not final until missing checklist items are fixed or documented as limitations.
```

## チェックリストのテンプレート

各段階で記述してもらうチェックリストのテンプレートです。これを書いてもらうことで、記述したルールを守ってもらう（思い出してもらう）ことを意図しています。

checklist-template.md

```
# Case Checklist

## 1. Analysis planning

- [ ] `analysis.md` was created or updated.
- [ ] Objective is clear.
- [ ] Unit system is stated.
- [ ] Real-world setup and modeling interpretation are stated.
- [ ] Geometry assumptions are recorded.
- [ ] Material model is defined.
- [ ] Element type candidates and final selection are justified.
- [ ] Boundary conditions and loading method are defined.
- [ ] Contacts, constraints, or their absence are stated.
- [ ] Expected result quantities are defined.
- [ ] Validation / sanity checks are planned.
- [ ] Known limitations are recorded.

Notes:

## 2. CalculiX coding

* [ ] CalculiX-native features were preferred over custom workarounds.
* [ ] Input files are split into readable `.inp/.inc` files.
* [ ] Named node sets and element sets are used when practical.
* [ ] Hard-coded node IDs are avoided when practical.
* [ ] Non-obvious modeling choices are documented in `analysis.md`.
* [ ] Solver execution is separated from post-processing and report generation.

Notes:

## 3. Result review

* [ ] Final model matches the analysis plan.
* [ ] Plan deviations are recorded and justified.
* [ ] Element type, mesh, BCs, loads, and materials are appropriate.
* [ ] Solver finished without unresolved serious warnings.
* [ ] Requested outputs were produced.
* [ ] Reactions balance applied loads.
* [ ] Deformed shape is physically plausible.
* [ ] Main result quantities are clearly defined.

Review status:

* [ ] Accepted
* [ ] Accepted with limitations
* [ ] Needs revision
* [ ] Diagnostic only

Notes:

## 4. Report writing

* [ ] Report audience is selected.
* [ ] Report is written as an engineering report, not a work log.
* [ ] Geometry overview is included.
* [ ] Actual mesh figure is included.
* [ ] Boundary condition and load figure is included.
* [ ] Deformed shape with scale factor is included.
* [ ] Main result contour is included.
* [ ] Critical-region close-up is included.
* [ ] Reaction/load balance is included.
* [ ] Stress/result value definition is stated.
* [ ] Max result location is stated.
* [ ] Engineering conclusion and limitations are included.
* [ ] Report figures are saved under `report/figures/`.

Notes:
```

## まとめ

ここでは`docs/cae-workflows/`下に、CAE解析の各作業段階における指示を`.md`ファイルに記述することで、CAE技術者が普段気を付けている内容を動作の型として定義し、AIエージェントが意図したような動作になることを目指しました。  
今後も状況をみて随時改訂する予定です。
