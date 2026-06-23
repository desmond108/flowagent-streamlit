# Swimlane & Hierarchy Flow — Legend

Reference for reading the FlowAgent process-flow swimlanes (and the colour cues
shared by the hierarchy views). This legend also appears in the footer of every
swimlane page; this document is the authoritative explanation.

A connector carries **two independent signals** — its **colour** (what kind of
flow) and its **style** (solid vs dashed). A box carries **one** signal — its
**border colour** (the kind of step). Read them together.

---

## Boxes — border colour = the type of step

| Swatch | Colour | Hex | Meaning |
|---|---|---|---|
| 🟡 | **Gold** | `#FFD700` | **Standard step** — a normal activity in the process. (Decision/gateway boxes and end/hand-off boxes also use gold.) |
| 🟢 | **Green** | `#4CAF50` | **New step** — added in the *optimised* version of the process (from the fit-gap analysis). Appears only in the optimised flows. |
| 🟠 | **Amber** | `#FF9800` | **Enhanced step** — an existing step strengthened in the optimised version. Appears only in the optimised flows. |
| 🔴 | **Red** | `#EF5350` | **Exception step** — a reject / hold / lapse / failure outcome. |

> In a **baseline** flow (`2_Process_Flow_Outputs/`, `2b_Corrected_Flow_Outputs/`)
> you will normally see only **gold** and **red** boxes. **Green** and **amber**
> boxes appear in the **optimised** flows (`4_Optimized_Process_Flow_Outputs/`),
> where they mark exactly what the optimisation added or changed.

---

## Connectors — colour = type of flow, style = certainty of the transition

### Colour (what the flow is)

| Sample | Colour | Meaning |
|---|---|---|
| ── | **Gold** | **Standard flow** — the normal path from one step to the next. |
| ── | **Green** | **Flow into a new step** — a connector leading to/from a NEW (optimised) step. |
| ── | **Red** | **Exception / reject path** — routes to a rejection, hold, lapse, or failure. |

### Style (how certain the transition is)

| Sample | Style | Meaning |
|---|---|---|
| ───── | **Solid** | **Sequential** — the main path; the guaranteed next step. |
| ┄┄┄┄ | **Dashed** | **Hand-off / conditional** — a hand-off between parties (e.g. claimant → processor) or a branch taken only under a condition (e.g. a decision outcome, a parallel/async path). |

### Reading the two together

Colour and style combine, so for example:

- **Solid gold** — the normal step-to-step sequence.
- **Dashed gold** — a conditional branch or a hand-off on the standard path.
- **Solid / dashed green** — flow into a step that the optimisation added.
- **Dashed red** — a conditional rejection/exception path (the most common red).

Edge **labels** (small chips on a connector, e.g. `paid` / `unpaid`, `ok` / `rej`,
`cx`) name the condition under which that branch is taken.

---

## Lanes & arrowheads

- **Lanes** (the horizontal bands, labelled on the left) are the **roles /
  systems** that own each step. A box sits in the lane of whoever performs it; a
  connector crossing lanes is a hand-off between parties.
- **Arrowheads** show direction of flow. Connectors are routed orthogonally and
  automatically avoid passing under intervening boxes, so every connector stays
  visible end-to-end.

---

## Where each colour set applies

| Output | Location | Box colours you'll see |
|---|---|---|
| Baseline flows | `2_Process_Flow_Outputs/` | Gold, Red |
| Corrected baseline flows | `2b_Corrected_Flow_Outputs/` | Gold, Red |
| Optimised flows | `4_Optimized_Process_Flow_Outputs/` | Gold, Red, **Green (new)**, **Amber (enhanced)** |
