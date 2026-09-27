import sqlite3
import json
import shutil
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)
DB_PATH = Path.home() / ".config" / "opencode" / "memory" / "index.db"

@app.route('/api/projects', methods=['GET'])
def get_projects():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT project FROM entries WHERE project IS NOT NULL AND project != ''")
    rows = cursor.fetchall()
    conn.close()
    
    data = [r[0] for r in rows]
    return jsonify(data)

@app.route('/api/memory', methods=['GET'])
def get_memory():
    project = request.args.get('project')
    print(f"DEBUG: API /api/memory called with project: {project}")
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    if project:
        cursor.execute("SELECT project, title, body, date FROM entries WHERE project=? ORDER BY date DESC LIMIT ? OFFSET ?", (project, limit, offset))
    else:
        cursor.execute("SELECT project, title, body, date FROM entries ORDER BY date DESC LIMIT ? OFFSET ?", (limit, offset))
        
    rows = cursor.fetchall()
    print(f"DEBUG: Found {len(rows)} entries")
    conn.close()
    
    data = [{"project": r[0], "title": r[1], "body": r[2], "date": r[3]} for r in rows]
    return jsonify(data)

@app.route('/api/identity', methods=['GET'])
def get_identity():
    identity_path = Path.home() / ".config" / "opencode" / "memory" / "IDENTITY.md"
    content = identity_path.read_text(encoding='utf-8') if identity_path.exists() else ""
    return jsonify({"content": content})

@app.route('/api/config/identity', methods=['POST'])
def update_identity():
    data = request.json
    identity_path = Path.home() / ".config" / "opencode" / "memory" / "IDENTITY.md"
    identity_path.write_text(data.get('content', ''), encoding='utf-8')
    return jsonify({"status": "success"})

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    notes_path = Path.home() / ".config" / "opencode" / "memory" / "knowledge" / "notes.md"
    content = notes_path.read_text(encoding='utf-8') if notes_path.exists() else ""
    return jsonify({"content": content})

@app.route('/api/config/knowledge', methods=['POST'])
def update_knowledge():
    data = request.json
    notes_path = Path.home() / ".config" / "opencode" / "memory" / "knowledge" / "notes.md"
    notes_path.write_text(data.get('content', ''), encoding='utf-8')
    return jsonify({"status": "success"})

# --- PROJECT METADATA SYSTEM ---

def init_metadata_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_metadata (
            project TEXT PRIMARY KEY,
            description TEXT NOT NULL DEFAULT '',
            tech_stack TEXT NOT NULL DEFAULT '',
            current_state TEXT NOT NULL DEFAULT '',
            next_steps TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'WIP'
        )
    """)
    
    # Pre-seed some smart, rich defaults for major projects if they don't exist
    seeds = [
        (
            'agent_orchistration',
            'Persistent memory and orchestration layer for AI development across ephemeral chat sessions.',
            'Python, Flask, SQLite, Vue 3, Tailwind CSS',
            'Sleek Visualizer UI completely overhauled; core control center with live agents control and metadata management online.',
            'Finalize HN/Reddit launch posts, package/test deployment, and gather star-worth public validation.',
            'Stable'
        ),
        (
            'core-store',
            'Enterprise-grade multi-tenant SaaS platform for digital goods with per-tenant branding and wallet billing.',
            'Laravel 13, Vue 3, Inertia, Tailwind CSS, MySQL, Redis',
            'Automated SHAM Cash payments fully integrated, real-time KPI tracking dashboard fully implemented.',
            'Optimize per-tenant subdomains routing and expand automated test suites for multi-tenancy edge cases.',
            'WIP'
        ),
        (
            'andres-dev-portfolio',
            'High-fidelity, bilingual (EN/AR) Stripe-grade developer showcase portfolio.',
            'Vue 3, Vite, Tailwind CSS, Vercel',
            'Aurora gradients, interactive terminal, FAQ accordion, FAQ sections, and bilingual i18n fully deployed.',
            'Integrate the new live Orchestra visualizer into a dedicated showcase section of the portfolio.',
            'Stable'
        )
    ]
    
    for project, desc, stack, state, steps, status in seeds:
        cursor.execute("SELECT 1 FROM project_metadata WHERE project=?", (project,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO project_metadata (project, description, tech_stack, current_state, next_steps, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project, desc, stack, state, steps, status))
    conn.commit()
    conn.close()

init_metadata_db()

@app.route('/api/projects/metadata/<project>', methods=['GET'])
def get_project_metadata(project):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT description, tech_stack, current_state, next_steps, status 
        FROM project_metadata WHERE project=?
    """, (project,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            "project": project,
            "description": row[0],
            "tech_stack": row[1],
            "current_state": row[2],
            "next_steps": row[3],
            "status": row[4]
        })
    else:
        # Provide fallback defaults for any new/unseeded project
        return jsonify({
            "project": project,
            "description": "An active development workspace tracked by Orchestra.",
            "tech_stack": "HTML, JS, CSS, Python",
            "current_state": "WIP - Tracked via git-backed memory timeline.",
            "next_steps": "Define core architectural requirements and draft next milestone steps.",
            "status": "WIP"
        })

@app.route('/api/projects/metadata/<project>', methods=['POST'])
def update_project_metadata(project):
    data = request.json
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO project_metadata (project, description, tech_stack, current_state, next_steps, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(project) DO UPDATE SET
            description=excluded.description,
            tech_stack=excluded.tech_stack,
            current_state=excluded.current_state,
            next_steps=excluded.next_steps,
            status=excluded.status
    """, (
        project,
        data.get("description", ""),
        data.get("tech_stack", ""),
        data.get("current_state", ""),
        data.get("next_steps", ""),
        data.get("status", "WIP")
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/runs', methods=['GET'])
def get_runs():
    db_p = Path.home() / ".config" / "opencode" / "memory" / "runs.db"
    if not db_p.exists():
        return jsonify([])
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    cursor.execute("SELECT id, goal, status, mode, depth, created_at, updated_at FROM runs ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "goal": r[1], "status": r[2], "mode": r[3], "depth": r[4], "date": r[5], "updated_at": r[6]} for r in rows])

@app.route('/api/runs', methods=['POST'])
def create_run():
    data = request.json or {}
    goal = data.get('goal', '').strip()
    depth = int(data.get('depth', 2))
    mode = data.get('mode', 'auto')
    if not goal:
        return jsonify({"error": "Goal is required"}), 400
    
    import subprocess
    import sys
    script_path = Path(__file__).resolve().parent / "swarm.py"
    cmd = [sys.executable, str(script_path), "run", goal, f"--depth={depth}"]
    if mode == "guided":
        cmd.append("--guided")
    
    # Spawn background process
    subprocess.Popen(cmd, cwd=str(Path(__file__).resolve().parent))
    return jsonify({"status": "success", "message": f"Swarm run started for goal: {goal}"})

@app.route('/api/runs/<int:run_id>', methods=['GET'])
def get_run_details(run_id):
    db_p = Path.home() / ".config" / "opencode" / "memory" / "runs.db"
    if not db_p.exists():
        return jsonify([])
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    cursor.execute("SELECT id, role, depth, task, status, verdict, retries, result, decision, started_at, finished_at FROM run_agents WHERE run_id=? ORDER BY id", (run_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{
        "id": r[0],
        "role": r[1],
        "depth": r[2],
        "task": r[3],
        "status": r[4],
        "verdict": r[5],
        "retries": r[6],
        "result": r[7],
        "decision": r[8],
        "started_at": r[9],
        "finished_at": r[10]
    } for r in rows])

@app.route('/api/runs/<int:run_id>/events', methods=['GET'])
def get_run_events(run_id):
    db_p = Path.home() / ".config" / "opencode" / "memory" / "runs.db"
    if not db_p.exists():
        return jsonify([])
    conn = sqlite3.connect(str(db_p))
    cursor = conn.cursor()
    cursor.execute("SELECT id, ts, type, payload FROM run_events WHERE run_id=? ORDER BY id DESC LIMIT 50", (run_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "ts": r[1], "type": r[2], "payload": r[3]} for r in rows])

@app.route('/api/runs/<int:run_id>/decision', methods=['POST'])
def save_agent_decision(run_id):
    data = request.json or {}
    agent_id = int(data.get('agent_id', 0))
    note = data.get('decision', '').strip()
    db_p = Path.home() / ".config" / "opencode" / "memory" / "runs.db"
    conn = sqlite3.connect(str(db_p))
    conn.execute("UPDATE run_agents SET decision=? WHERE run_id=? AND id=?", (note, run_id, agent_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

ROLES_DIR = Path(__file__).resolve().parent / "roles"

@app.route('/api/agents', methods=['GET'])
def get_agents():
    files = [f.stem for f in ROLES_DIR.glob("*.md")]
    return jsonify(files)

@app.route('/api/agents/<role>', methods=['GET'])
def get_agent(role):
    role_path = ROLES_DIR / f"{role}.md"
    content = role_path.read_text(encoding='utf-8') if role_path.exists() else ""
    return jsonify({"content": content})

@app.route('/api/agents/<role>', methods=['POST'])
def update_agent(role):
    data = request.json
    role_path = ROLES_DIR / f"{role}.md"
    backup_path = ROLES_DIR / f"{role}.md.bak"
    
    if role_path.exists():
        shutil.copyfile(str(role_path), str(backup_path))
    
    role_path.write_text(data.get('content', ''), encoding='utf-8')
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(port=8715)
