# Execution Mastery — The "Get Stuff Done" Skill

## Overview
This skill enforces a rigorous, 3-brick execution protocol for all complex engineering tasks in Orchestra. It eliminates shortcuts, mandates contextual analysis, enforces swarm delegation for large tasks, and requires rigorous self-verification before completion.

---

## Brick 1: Contextual Understanding & Spec-First Protocol
Before writing a single line of code or executing modifications:
1. **Input Analysis:** Read all relevant files, inspect project structure, and understand existing conventions. Never guess.
2. **Physical Goal Definition:** Define the exact tangible deliverable (e.g., "A functioning DXF parser producing 100% valid entities" rather than "write script").
3. **Acceptance Test First:** Define how success will be verified before implementation begins.
4. **Atomic CTO Plan:** Break the work down into small, sequential, verifiable steps.

---

## Brick 2: Tool Awareness & Swarm Empowerment
Always leverage the right tool for the job:
1. **Tool Inventory:** 
   - *Search & Read:* Glob, Grep, Read (always inspect before editing).
   - *Modification:* Edit, Write (exact matching, preserving indentation).
   - *Execution:* Bash (with command explanation for safety).
2. **Mandatory Swarm Delegation:** 
   - For multi-domain, complex, or multi-file tasks (e.g., backend API + frontend UI + testing), **DO NOT** do everything sequentially in a single linear thread.
   - **Spawn specialized subagent swarms** using the `task` tool (e.g., backend-dev, frontend-dev, tester-sentinel) to parallelize work and maximize accuracy.
3. **Resourcefulness:** Utilize web fetching, testing utilities, and auxiliary scripts as needed.

---

## Brick 3: Self-Verification & Quality Gate
Never claim completion based on intent:
1. **Execution Verification:** Run project build, test suites, linters, or validation scripts.
2. **Defect-Free Guarantee:** Eliminate placeholders, mock shortcuts, or unverified code.
3. **Post-Check:** Verify output against the acceptance criteria defined in Brick 1.
