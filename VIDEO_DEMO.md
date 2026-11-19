# Video demo: conversation flows and explainability

Use `python3 matching_agent.py --root resumes --chat` and keep the terminal visible. For each flow, point out the report's user-facing rationale: extracted criteria, matched skills, years evidence, gaps, recommendation, and any re-ranking change. This is auditable decision evidence, not private model chain-of-thought.

## 1. Search for candidates

**Say/type:**

```text
Find me candidates with React and 3+ years experience
```

**Show:** The top-10 initial screen and the parsed requirement (`React`, minimum three years). For the first candidate, read the visible `Strengths`, `Gaps`, score, and recommendation. Explain that the score combines must-have skills (55%), nice-to-have skills (15%), experience (20%), and role relevance (10%).

## 2. Compare candidates side by side

**Say/type:**

```text
Compare R086, R026, and R045 side by side
```

**Show:** The candidate comparison output. Call out that every person is evaluated against the same criteria, and identify the visible skills/gaps that distinguish them.

## 3. Ask why someone ranked higher

**Say/type:**

```text
Why did R086 rank higher?
```

**Show:** The explanation containing the candidate's score, matched requirements, stated years compared with the requested minimum, and missing requirements. This is the agent's concise, evidence-based reasoning record.

## 4. Refine requirements and re-rank

**Say/type:**

```text
Require TypeScript and at least 5 years
```

**Show:** The `Refined ... rankings were recalculated` message, then compare the new top candidate and their gaps to the earlier list. Explain that the prior query is retained in conversation history and the new criteria are added before the graph runs again.

## 5. Generate screening questions

**Say/type:**

```text
questions for R086
```

**Show:** The three questions. Explain that one validates a demonstrated strength, one probes a gap, and one checks technical judgement. This is the second-round/deep-analysis stage.

## 6. Demonstrate preferred versus required skills

**Say/type:**

```text
Find candidates with Python and SQL, 4+ years required; AWS preferred
```

**Show:** The must-have and nice-to-have lines plus the results. Explain that a missing required skill becomes a gap, while AWS contributes as a preference rather than automatically excluding a candidate. Point out the final `HIRE`, `HOLD / INTERVIEW`, or `NO HIRE` recommendation.

## Suggested closing

State that resume access is performed through the MCP filesystem server, the state graph executes parse → extract → search → rank → deep analysis → recommendation → report → feedback, and the reasoning displayed is tied to resume evidence and adjustable hiring criteria.
