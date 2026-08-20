"""Swarm engine — Orchestra v3. Drives structured agent hierarchies.

orchestra run "<goal>" [--auto|--guided] [--parallel N] [--depth 1|2]
orchestra resume <run_id>
orchestra status [run_id]
orchestra runs
"""

import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal TEXT NOT NULL,
    plan TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'planning',
    mode TEXT NOT NULL DEFAULT 'auto',
    depth INTEGER NOT NULL DEFAULT 2,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS run_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    depth INTEGER NOT NULL DEFAULT 1,
    task TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    verdict TEXT DEFAULT '',
    retries INTEGER NOT NULL DEFAULT 0,
    result TEXT DEFAULT '',
    decision TEXT DEFAULT '',
    started_at TEXT,
    finished_at TEXT,
    FOREIGN KEY (run_id) REFERENCES runs(id)
);
CREATE TABLE IF NOT EXISTS run_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    ts TEXT NOT NULL,
    type TEXT NOT NULL,
    payload TEXT DEFAULT ''
);
"""


def db_path():
    override = os.environ.get("ORCHESTRA_HOME")
    base = Path(override) if override else Path.home() / ".config" / "opencode"
    return base / "memory" / "runs.db"


def connect():
    db = db_path()
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    conn.executescript(SCHEMA)
    return conn


def roles_dir():
    override = os.environ.get("ORCHESTRA_HOME")
    base = Path(override) if override else Path.home() / ".config" / "opencode"
    return base / "roles"


def skills_dir():
    override = os.environ.get("ORCHESTRA_HOME")
    base = Path(override) if override else Path.home() / ".config" / "opencode"
    return base / "skills"


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def event(conn, run_id, type_, payload=""):
    conn.execute(
        "INSERT INTO run_events (run_id, ts, type, payload) VALUES (?,?,?,?)",
        (run_id, now(), type_, payload),
    )
    conn.commit()


def read_role(name):
    p = roles_dir() / (name + ".md")
    if p.exists():
        return p.read_text(encoding="utf-8-sig", errors="replace")
    return ""


def read_skills(stack_hint):
    out = []
    for name in ["web-stack.md", "python-bot.md", "deploy-safe.md", "security-scan.md"]:
        p = skills_dir() / name
        if p.exists():
            out.append(p.read_text(encoding="utf-8-sig", errors="replace"))
    return "\n\n".join(out)


def opencode_run(args):
    """Run the opencode CLI headless. Returns (returncode, stdout)."""
    cmd = ["opencode", "run"]
    cmd += args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        return r.returncode, r.stdout
    except FileNotFoundError:
        return -1, "opencode CLI not found"
    except subprocess.TimeoutExpired:
        return -2, "timed out"


def _json_block(text):
    """Extract the first JSON object/array from a model reply."""
    start = text.find("{")
    if start == -1:
        start = text.find("[")
    if start == -1:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except ValueError:
                    return None
    return None


def run_plan(conn, run_id, goal, depth):
    """Routing phase: orchestrator role builds the delegation plan (JSON)."""
    conn.execute("UPDATE runs SET status='planning' WHERE id=?", (run_id,))
    conn.commit()
    prompt = (
        read_role("orchestrator")
        + "\n\nGoal: " + goal
        + "\n\nMaximum depth: " + str(depth)
        + "\n\nReply with ONLY the JSON plan."
    )
    rc, out = opencode_run(["--agent", "orchestrator", prompt])
    plan = _json_block(out) if rc == 0 else None
    agents = plan.get("agents", []) if isinstance(plan, dict) else []
    if not agents:
        conn.execute(
            "UPDATE runs SET status='failed', updated_at=? WHERE id=?", (now(), run_id)
        )
        conn.commit()
        event(conn, run_id, "plan_failed", out[:500])
        print("Planning failed — no agent plan produced.")
        print(out[:800])
        return False
    conn.execute(
        "UPDATE runs SET plan=?, status='planned', updated_at=? WHERE id=?",
        (json.dumps(agents, ensure_ascii=False), now(), run_id),
    )
    for a in agents:
        conn.execute(
            "INSERT INTO run_agents (run_id, role, depth, task, status) VALUES (?,?,?,?, 'queued')",
            (run_id, a.get("role", "?"), int(a.get("depth", 1)), a.get("task", "")),
        )
    conn.commit()
    event(conn, run_id, "planned", json.dumps(agents, ensure_ascii=False)[:500])
    return True


def run_execute(conn, run_id, mode, max_parallel):
    """Execution phase: walk agents in dependency order, tester gates each."""
    conn.execute("UPDATE runs SET status='running', updated_at=? WHERE id=?", (now(), run_id))
    conn.commit()
    event(conn, run_id, "started", "mode=" + mode)

    rows = conn.execute(
        "SELECT id, role, depth, task, status, retries FROM run_agents WHERE run_id=? ORDER BY id",
        (run_id,),
    ).fetchall()
    agents = [
        {"id": r[0], "role": r[1], "depth": r[2], "task": r[3], "status": r[4], "retries": r[5]}
        for r in rows
    ]
    done = 0
    total = len(agents)
    for a in agents:
        if a["status"] in ("done", "skipped", "blocked"):
            if a["status"] == "done":
                done += 1
            continue
        if mode == "guided":
            print(f"PAUSED at {a['role']} — approve on the board or 'orchestra resume {run_id}'")
            return False
        rc = execute_one(conn, run_id, a)
        if rc == "ok":
            done += 1
        elif rc == "fail":
            retries = a["retries"]
            if retries < 2:
                a["retries"] += 1
                conn.execute(
                    "UPDATE run_agents SET retries=?, status='queued' WHERE id=?",
                    (a["retries"], a["id"]),
                )
                conn.commit()
                event(conn, run_id, "retry", f"{a['role']} retry {a['retries']}/2")
                print(f"  -> {a['role']} retry {a['retries']}/2")
                rc2 = execute_one(conn, run_id, a)
                if rc2 == "ok":
                    done += 1
                else:
                    conn.execute(
                        "UPDATE run_agents SET status='blocked' WHERE id=?", (a["id"],)
                    )
                    conn.commit()
                    event(conn, run_id, "blocked", a["role"])
                    print(f"  !! {a['role']} BLOCKED after 2 failures")
            else:
                conn.execute(
                    "UPDATE run_agents SET status='blocked' WHERE id=?", (a["id"],)
                )
                conn.commit()
                event(conn, run_id, "blocked", a["role"])
                print(f"  !! {a['role']} BLOCKED")
    if done == total:
        conn.execute("UPDATE runs SET status='done', updated_at=? WHERE id=?", (now(), run_id))
        conn.commit()
        event(conn, run_id, "done", "")
        print(f"Run {run_id} complete: {done}/{total} agents done.")
    else:
        conn.execute("UPDATE runs SET status='partial', updated_at=? WHERE id=?", (now(), run_id))
        conn.commit()
        print(f"Run {run_id} partial: {done}/{total} done, others blocked/skipped.")


def execute_one(conn, run_id, a):
    """Run one agent + tester gate. Returns 'ok' | 'fail'."""
    print(f"== {a['role']}: {a['task']}")
    conn.execute(
        "UPDATE run_agents SET status='running', started_at=? WHERE id=?",
        (now(), a["id"]),
    )
    conn.commit()
    event(conn, run_id, "agent_start", a["role"])

    role_doc = read_role(a["role"])
    prompt = (
        role_doc
        + "\n\n## Task card\n"
        + a["task"]
        + "\n\n## Skills (apply these)\n"
        + read_skills("")
        + "\n\nWork in the current project directory. Do not touch files outside your scope. "
        + "Finish with your output contract."
    )
    rc, out = opencode_run(["--agent", a["role"], prompt])
    result = (out or "")[:3000]
    conn.execute(
        "UPDATE run_agents SET result=?, status='tested', finished_at=? WHERE id=?",
        (result, now(), a["id"]),
    )
    conn.commit()
    if rc != 0:
        event(conn, run_id, "agent_error", a["role"])
        return "fail"

    verdict = tester_check(conn, run_id, a["id"], a["role"])
    conn.execute(
        "UPDATE run_agents SET verdict=? WHERE id=?",
        (verdict.get("verdict", ""), a["id"]),
    )
    conn.commit()
    if verdict.get("verdict") == "PASS":
        conn.execute("UPDATE run_agents SET status='done' WHERE id=?", (a["id"],))
        conn.commit()
        event(conn, run_id, "agent_pass", a["role"])
        print(f"  OK {a['role']}")
        return "ok"
    event(conn, run_id, "agent_fail", a["role"] + ": " + json.dumps(verdict)[:300])
    print(f"  FAIL {a['role']}: {verdict.get('failures', [])}")
    return "fail"


def tester_check(conn, run_id, agent_id, role):
    """Tester agent runs the real suite against the latest changes."""
    verdict = {"verdict": "FAIL", "failures": ["tester unavailable"]}
    prompt = (
        read_role("tester")
        + "\n\n## Skills (verification playbook)\n"
        + read_skills("")
        + "\n\nVerify the work just completed by role " + role
        + " in the current project. Run the real checks. Return ONLY the JSON verdict."
    )
    rc, out = opencode_run(["--agent", "tester", prompt])
    if rc == 0:
        v = _json_block(out)
        if isinstance(v, dict) and v.get("verdict") in ("PASS", "FAIL"):
            verdict = v
    return verdict


def cmd_run(goal, mode, depth):
    if not goal:
        print("usage: orchestra run \"<goal>\" [--auto|--guided] [--depth 1|2]")
        return 1
    conn = connect()
    run_id = conn.execute(
        "INSERT INTO runs (goal, mode, depth, created_at, updated_at) VALUES (?,?,?,?,?)",
        (goal, mode, depth, now(), now()),
    ).lastrowid
    conn.commit()
    print(f"Run #{run_id}: {goal} (mode={mode}, depth={depth})")
    if not run_plan(conn, run_id, goal, depth):
        return 1
    run_execute(conn, run_id, mode, 1)
    return 0


def cmd_resume(run_id):
    conn = connect()
    run = conn.execute(
        "SELECT id, goal, mode, depth, status FROM runs WHERE id=?", (run_id,)
    ).fetchone()
    if not run:
        print("No such run.")
        return 1
    print(f"Resume #{run[0]}: {run[1]} (mode={run[2]}, status={run[4]})")
    run_execute(conn, run[0], run[2], 1)
    return 0


def cmd_status(run_id):
    conn = connect()
    if run_id is None:
        rows = conn.execute(
            "SELECT id, goal, status, mode, created_at FROM runs ORDER BY id DESC LIMIT 10"
        ).fetchall()
        for r in rows:
            print(f"#{r[0]:>3}  {r[2]:<9}  {r[4]}  {r[1][:60]}")
        return 0
    run = conn.execute(
        "SELECT id, goal, plan, status, mode, created_at FROM runs WHERE id=?", (run_id,)
    ).fetchone()
    if not run:
        print("No such run.")
        return 1
    print(f"#{run[0]} {run[5]}  [{run[3]}]  {run[1]}")
    print()
    agents = conn.execute(
        "SELECT role, depth, status, verdict, retries, task FROM run_agents WHERE run_id=? ORDER BY id",
        (run_id,),
    ).fetchall()
    for a in agents:
        v = (" " + a[3]) if a[3] else ""
        print(f"  {'  ' * (a[1] - 1)}- {a[0]:<14} {a[2]:<8}{v:<8} r{a[4]}  {a[5][:50]}")
    return 0


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    args = sys.argv[1:]
    if not args:
        print("swarm: run <goal> | resume <id> | status [id] | runs")
        return 1
    cmd = args[0]
    if cmd == "run":
        mode = "auto"
        depth = 2
        goal = []
        for a in args[1:]:
            if a == "--guided":
                mode = "guided"
            elif a == "--auto":
                mode = "auto"
            elif a == "--depth":
                depth = int(args[args.index(a) + 1])
            elif a.startswith("--depth="):
                depth = int(a.split("=")[1])
            else:
                goal.append(a)
        return cmd_run(" ".join(goal), mode, depth)
    if cmd == "resume":
        return cmd_resume(int(args[1]) if len(args) > 1 else None)
    if cmd == "status":
        return cmd_status(int(args[1]) if len(args) > 1 else None)
    if cmd == "runs":
        return cmd_status(None)
    print("swarm: unknown command", cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())