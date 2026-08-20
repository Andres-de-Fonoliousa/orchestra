"""Orchestra — session memory helper for opencode."""

import argparse
import hashlib
import html
import http.server
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

ORCHESTRA_VERSION = "2.0.0"
COMMANDS = ["handoff.md", "done.md", "remember.md"]
MEMORY_FILES = ["IDENTITY.md"]
KNOWLEDGE_FILES = ["notes.md"]
PLUGINS = ["journal.ts"]
GIT_IGNORE = [".gitignore"]

INDEX_DB = "index.db"
KNOW_LINE_RE = re.compile(r"^\*\*(\d{4}-\d{2}-\d{2})\s+([^*]+?)\*\*:\s*(.+)$")
TAG_RE = re.compile(r"#([\w-]+)")
TIME_SUFFIX_RE = re.compile(r"\s*[—–-]\s*\d{2}:\d{2}\s*(?:\(.*\))?$")


def brain_dir():
    override = os.environ.get("ORCHESTRA_HOME")
    return Path(override) if override else Path.home() / ".config" / "opencode"


def expand(text):
    return text.replace("{{HOME}}", str(Path.home()))


def run_git(args, cwd):
    try:
        return subprocess.run(
            ["git"] + args, cwd=str(cwd), capture_output=True, text=True
        )
    except OSError:
        return None


def git_ok(cwd):
    r = run_git(["rev-parse", "--is-inside-work-tree"], cwd)
    return bool(r and r.returncode == 0 and r.stdout.strip() == "true")


def git_commit(cwd, message):
    run_git(["add", "-A"], cwd)
    r = run_git(["commit", "-m", message], cwd)
    return bool(r and r.returncode == 0)


def strip_comments(text):
    text = re.sub(r"/\*[\s\S]*?\*/", "", text)
    text = re.sub(r"(?m)(?<!:)//.*$", "", text)
    return text


def load_json(path):
    try:
        return json.loads(strip_comments(path.read_text(encoding="utf-8-sig")))
    except (ValueError, OSError):
        return {}


def write_json(path, data):
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def find_installed_config(brain):
    for name in ["opencode.json", "opencode.jsonc"]:
        p = brain / name
        if p.exists():
            return p
    return None


def merge_config(brain, template_path):
    template = load_json(template_path)
    merged = {}
    existing_path = find_installed_config(brain)
    if existing_path:
        merged = load_json(existing_path)
        backup = brain / (
            existing_path.name + ".bak-" + datetime.now().strftime("%Y%m%d%H%M%S")
        )
        shutil.move(str(existing_path), str(backup))
        print("backed up existing config:", existing_path.name, "->", backup.name)

    for key, value in template.items():
        if key in ("instructions", "references"):
            merged.setdefault(key, {} if isinstance(value, dict) else [])
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    existing = merged[key].get(sub_key)
                    if existing != sub_value:
                        merged[key][sub_key] = sub_value
            else:
                for item in value:
                    if item not in merged[key]:
                        merged[key].append(item)
            if key == "instructions":
                merged[key] = [expand(i) for i in merged[key]]
        else:
            merged.setdefault(key, value)

    merged["instructions"] = [str(Path(expand(i))) for i in merged.get("instructions", [])]
    for alias, ref in merged.get("references", {}).items():
        if isinstance(ref, dict) and "path" in ref:
            ref["path"] = str(Path(expand(ref["path"])))

    write_json(brain / "opencode.json", merged)
    return merged


def copy_expanded(src, dest):
    text = src.read_text(encoding="utf-8")
    dest.write_text(expand(text), encoding="utf-8")


def copy_if_missing(src, dest):
    if not dest.exists():
        shutil.copyfile(str(src), str(dest))
        return True
    return False


def cmd_install(source):
    src = Path(source) if source else Path(__file__).resolve().parent
    brain = brain_dir()
    (brain / "commands").mkdir(parents=True, exist_ok=True)
    (brain / "memory" / "journal").mkdir(parents=True, exist_ok=True)
    (brain / "memory" / "knowledge").mkdir(parents=True, exist_ok=True)
    (brain / "plugins").mkdir(parents=True, exist_ok=True)

    merge_config(brain, src / "opencode.global.json")

    for name in COMMANDS:
        copy_expanded(src / "commands" / name, brain / "commands" / name)

    for name in PLUGINS:
        plugin_src = src / ".opencode" / "plugins" / name
        if plugin_src.exists():
            shutil.copyfile(str(plugin_src), str(brain / "plugins" / name))

    for name in MEMORY_FILES:
        copy_if_missing(src / "memory" / name, brain / "memory" / name)
    for name in KNOWLEDGE_FILES:
        copy_if_missing(
            src / "memory" / "knowledge" / name, brain / "memory" / "knowledge" / name
        )

    shutil.copyfile(str(Path(__file__).resolve()), str(brain / "orchestra.py"))
    shutil.copyfile(str(src / "VERSION"), str(brain / "VERSION"))
    if sys.platform == "win32" and (src / "orchestra.cmd").exists():
        shutil.copyfile(str(src / "orchestra.cmd"), str(brain / "orchestra.cmd"))

    memory_repo = brain / "memory"
    if not git_ok(memory_repo):
        run_git(["init", "-q"], memory_repo)
    for name in GIT_IGNORE:
        copy_if_missing(src / name, memory_repo / name)
    git_commit(memory_repo, "memory: " + datetime.now().strftime("%Y-%m-%d %H:%M"))

    print()
    print(f"Installed Orchestra to: {brain}")
    print("Quit and restart opencode so the global config loads.")
    print("Then: fill in", brain / "memory" / "IDENTITY.md", "once.")


def doctor_results(brain):
    checks = [
        ("global config", brain / "opencode.json"),
        ("identity memory", brain / "memory" / "IDENTITY.md"),
        ("journal dir", brain / "memory" / "journal"),
        ("knowledge base", brain / "memory" / "knowledge" / "notes.md"),
        ("orchestra.py", brain / "orchestra.py"),
        ("command: handoff", brain / "commands" / "handoff.md"),
        ("command: done", brain / "commands" / "done.md"),
        ("command: remember", brain / "commands" / "remember.md"),
    ]
    results = [(label, path, path.exists()) for label, path in checks]
    cfg = load_json(brain / "opencode.json") if (brain / "opencode.json").exists() else {}
    instructions_ok = any("IDENTITY.md" in i for i in cfg.get("instructions", []))
    reference_ok = "memory" in cfg.get("references", {})
    results.append(("IDENTITY.md wired into instructions", None, instructions_ok))
    results.append(("memory reference registered", None, reference_ok))
    return results, git_ok(brain / "memory")


def cmd_doctor():
    brain = brain_dir()
    results, repo_ok = doctor_results(brain)
    ok = True
    for label, path, present in results:
        ok = ok and present
        print(("[OK] " if present else "[MISSING] ") + label + " -> " + str(path))
    print(("[OK] " if repo_ok else "[NOTE] ") + "memory git repo (git not found or not a repo)")
    ok = ok and repo_ok

    version_file = brain / "VERSION"
    installed = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "?"
    if installed != ORCHESTRA_VERSION:
        print("[WARN] brain VERSION is", installed, "— Orchestra repo is", ORCHESTRA_VERSION + ". Run: orchestra upgrade <repo path>")
    if index_stale(brain):
        print("[NOTE] memory index missing or stale — run: orchestra migrate")
    return 0 if ok else 1


def cmd_status():
    brain = brain_dir()
    for path in sorted(brain.rglob("*")):
        if path.is_file():
            rel = path.relative_to(brain.parent.parent)
            print(str(rel))


def cmd_commit():
    repo = brain_dir() / "memory"
    project = Path(os.getcwd()).name
    message = project + ": memory " + datetime.now().strftime("%Y-%m-%d %H:%M")
    if git_commit(repo, message):
        print("Committed:", message)
    else:
        print("Nothing to commit (or git unavailable).")


def index_db_path(brain):
    return brain / "memory" / INDEX_DB


def parse_journal_file(path):
    text = path.read_text(encoding="utf-8-sig")
    date = path.stem
    sections = re.split(r"(?m)^##\s+", text)
    entries = []
    for sec in sections[1:]:
        lines = sec.splitlines()
        title = lines[0].strip() if lines else "untitled"
        body = "\n".join(lines[1:]).strip()
        project = TIME_SUFFIX_RE.sub("", title) or title
        entries.append(
            {
                "kind": "journal",
                "project": project,
                "date": date,
                "title": title,
                "body": body,
                "tags": TAG_RE.findall(title + " " + body),
                "src": str(path),
            }
        )
    return entries


def parse_knowledge_file(path):
    text = path.read_text(encoding="utf-8-sig")
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = KNOW_LINE_RE.match(line)
        if m:
            date, project, body = m.group(1), m.group(2).strip(), m.group(3).strip()
        else:
            date, project, body = "", "", line
        entries.append(
            {
                "kind": "knowledge",
                "project": project,
                "date": date,
                "title": project or "note",
                "body": body,
                "tags": TAG_RE.findall(body),
                "src": str(path),
            }
        )
    return entries


def collect_entries(brain):
    entries = []
    journal_dir = brain / "memory" / "journal"
    if journal_dir.exists():
        for p in sorted(journal_dir.glob("*.md")):
            entries.extend(parse_journal_file(p))
    notes = brain / "memory" / "knowledge" / "notes.md"
    if notes.exists():
        entries.extend(parse_knowledge_file(notes))
    return entries


def build_index(brain):
    db = index_db_path(brain)
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS entries ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "kind TEXT NOT NULL, project TEXT NOT NULL DEFAULT '',"
            "date TEXT NOT NULL DEFAULT '', title TEXT NOT NULL DEFAULT '',"
            "body TEXT NOT NULL DEFAULT '', tags TEXT NOT NULL DEFAULT '',"
            "src TEXT NOT NULL DEFAULT '', hash TEXT NOT NULL UNIQUE)"
        )
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts "
            "USING fts5(project, title, body, tags)"
        )
        conn.execute("DELETE FROM entries_fts")
        conn.execute("DELETE FROM entries")
        n = 0
        for e in collect_entries(brain):
            h = hashlib.sha256(
                "|".join(
                    [e["kind"], e["date"], e["project"], e["title"], e["body"]]
                ).encode("utf-8")
            ).hexdigest()
            cur = conn.execute(
                "INSERT INTO entries (kind, project, date, title, body, tags, src, hash) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (
                    e["kind"],
                    e["project"],
                    e["date"],
                    e["title"],
                    e["body"],
                    ",".join(e["tags"]),
                    e["src"],
                    h,
                ),
            )
            conn.execute(
                "INSERT INTO entries_fts (rowid, project, title, body, tags) "
                "VALUES (?,?,?,?,?)",
                (
                    cur.lastrowid,
                    e["project"],
                    e["title"],
                    e["body"],
                    ",".join(e["tags"]),
                ),
            )
            n += 1
        conn.commit()
    finally:
        conn.close()
    return n


def index_stale(brain):
    db = index_db_path(brain)
    if not db.exists():
        return True
    newest = 0.0
    for folder in [(brain / "memory" / "journal"), (brain / "memory" / "knowledge")]:
        if folder.exists():
            for p in folder.glob("*.md"):
                newest = max(newest, p.stat().st_mtime)
    return db.stat().st_mtime < newest


def ensure_index(brain):
    if index_stale(brain):
        return build_index(brain)
    return None


def cmd_migrate():
    brain = brain_dir()
    n = build_index(brain)
    print("Indexed", n, "entries ->", index_db_path(brain))
    return 0


def cmd_query(text):
    brain = brain_dir()
    ensure_index(brain)
    db = index_db_path(brain)
    if not db.exists():
        print(json.dumps({"error": "no index — run: orchestra migrate"}, ensure_ascii=False))
        return 1
    conn = sqlite3.connect(str(db))
    try:
        phrase = '"' + text.replace('"', '""') + '"'
        try:
            rows = conn.execute(
                "SELECT e.kind, e.project, e.date, e.title, e.tags, e.src, "
                "snippet(entries_fts, 2, '[', ']', '...', 24) "
                "FROM entries_fts JOIN entries e ON e.id = entries_fts.rowid "
                "WHERE entries_fts MATCH ? ORDER BY bm25(entries_fts) LIMIT 20",
                (phrase,),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = conn.execute(
                "SELECT e.kind, e.project, e.date, e.title, e.tags, e.src, "
                "substr(e.body, 1, 240) FROM entries e "
                "WHERE e.body LIKE ? OR e.title LIKE ? OR e.project LIKE ? "
                "ORDER BY e.date DESC LIMIT 20",
                ("%" + text + "%",) * 3,
            ).fetchall()
        out = [
            {
                "kind": r[0],
                "project": r[1],
                "date": r[2],
                "title": r[3],
                "tags": [t for t in r[4].split(",") if t] if r[4] else [],
                "src": r[5],
                "snippet": r[6],
            }
            for r in rows
        ]
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    finally:
        conn.close()


def cmd_start(project):
    project = Path(project or os.getcwd())
    orch = project / ".orchestra"
    orch.mkdir(exist_ok=True)
    handoff = orch / "handoff.md"
    if handoff.exists():
        print("handoff already exists:", handoff)
        return
    handoff.write_text(
        "# Handoff — " + project.name + "\n"
        "Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\n"
        "## Current state\n- \n\n## Next steps\n- \n",
        encoding="utf-8",
    )
    print("Created:", handoff)


def cmd_handoff(project):
    project = Path(project or os.getcwd())
    brain = brain_dir() / "memory"
    print("# Orchestra handoff — " + project.name)
    print("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    print()
    handoff = project / ".orchestra" / "handoff.md"
    if handoff.exists():
        print("## Project state\n")
        print(handoff.read_text(encoding="utf-8-sig"))
    else:
        print("## Project state\n(MISSING — run /handoff in opencode to create it)\n")
    entries = []
    for p in sorted((brain / "journal").glob("*.md"), reverse=True)[:2]:
        entries.append("## " + p.stem + "\n\n" + p.read_text(encoding="utf-8-sig"))
    if entries:
        print("## Recent journal\n")
        print("\n".join(entries), "\n")
    notes = brain / "knowledge" / "notes.md"
    if notes.exists():
        print("## Knowledge\n")
        print(notes.read_text(encoding="utf-8-sig"))


def cmd_upgrade(source):
    brain = brain_dir()
    old_version = "?"
    version_file = brain / "VERSION"
    if version_file.exists():
        old_version = version_file.read_text(encoding="utf-8").strip()
    print("Orchestra upgrade:", old_version, "->", ORCHESTRA_VERSION)
    print()

    backup = brain.parent / ("opencode-backup-" + datetime.now().strftime("%Y%m%d%H%M%S"))
    shutil.copytree(
        str(brain),
        str(backup),
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    print("Backup:", backup)
    print()

    src = Path(source) if source else Path(__file__).resolve().parent
    new_files = 0
    (brain / "plugins").mkdir(parents=True, exist_ok=True)
    (brain / "commands").mkdir(parents=True, exist_ok=True)
    for name in COMMANDS:
        if (src / "commands" / name).exists():
            copy_expanded(src / "commands" / name, brain / "commands" / name)
            new_files += 1
    for name in PLUGINS:
        if (src / ".opencode" / "plugins" / name).exists():
            shutil.copyfile(
                str(src / ".opencode" / "plugins" / name),
                str(brain / "plugins" / name),
            )
            new_files += 1
    shutil.copyfile(str(Path(__file__).resolve()), str(brain / "orchestra.py"))
    shutil.copyfile(str(src / "VERSION"), str(brain / "VERSION"))
    print("Updated", new_files, "command/plugin files, orchestra.py, VERSION")
    print()

    n = build_index(brain)
    print("Indexed", n, "entries ->", index_db_path(brain))
    print()

    results, repo_ok = doctor_results(brain)
    ok = True
    for label, path, present in results:
        ok = ok and present
        print(("[OK] " if present else "[MISSING] ") + label)
    print(("[OK] " if repo_ok else "[NOTE] ") + "memory git repo")
    print()
    print("Upgrade complete.", "All checks passed." if ok else "Some checks failed — see above.")
    return 0 if ok else 1


def cmd_sync():
    repo = brain_dir() / "memory"
    remote = run_git(["remote", "get-url", "origin"], repo)
    if not remote or remote.returncode != 0 or not remote.stdout.strip():
        print("No remote configured for the memory repo.")
        print("Create one first: gh repo create orchestra-memory --private --source <memory> --push")
        return 1
    print("Remote:", remote.stdout.strip())
    pull = run_git(["pull", "--rebase", "-q"], repo)
    if pull and pull.returncode != 0:
        print("Pull failed (conflicts? run manually):", pull.stderr.strip() or pull.stdout.strip())
    elif pull:
        print("Pull: OK")
    git_commit(repo, "memory: sync " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    push = run_git(["push", "-q", "origin", "HEAD"], repo)
    if push and push.returncode == 0:
        print("Push: OK")
        return 0
    print("Push failed:", push.stderr.strip() if push else "git unavailable")
    return 1


DASHBOARD_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Orchestra — v@VERSION@</title>
<style>
:root{--bg:#f7f7f5;--card:#ffffff;--line:#e4e4e0;--text:#1f2328;--muted:#6b7280;--ok:#1a7f37;--bad:#b42318;--accent:#0969da}
*{box-sizing:border-box}
body{margin:0;font:14px/1.6 system-ui,"Segoe UI",sans-serif;background:var(--bg);color:var(--text)}
header{padding:14px 26px;border-bottom:1px solid var(--line);background:var(--card);display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}
header h1{font-size:17px;margin:0}
header .sub{color:var(--muted);font-weight:400;margin-left:8px}
header .tip{display:flex;gap:12px;align-items:center}
main{max-width:980px;margin:0 auto;padding:22px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:760px){.grid{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 20px;margin-bottom:18px}
.card h2{font-size:12px;margin:0 0 10px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
pre{background:#f4f4f2;border:1px solid var(--line);border-radius:8px;padding:12px;overflow:auto;font-size:12.5px;line-height:1.5;margin:0;white-space:pre-wrap;word-break:break-word}
ul.checks{list-style:none;margin:0;padding:0}
ul.checks li{padding:4px 0;border-bottom:1px dashed var(--line)}
ul.checks .muted{display:block;font-size:11.5px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
li.ok{color:var(--ok)}li.bad{color:var(--bad)}
h3{font-size:14px;margin:14px 0 6px}
button{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:8px 16px;font:inherit;cursor:pointer}
button:hover{filter:brightness(1.1)}
a{color:var(--accent)}
code{background:#f4f4f2;border-radius:4px;padding:1px 5px;font-size:12.5px}
</style>
</head>
<body>
<header>
  <h1>Orchestra<span class="sub">v@VERSION@ — memory dashboard</span></h1>
  <span class="tip"><span id="msg"></span><button onclick="commit()">Commit memory</button></span>
</header>
<main>
  <section class="card"><h2>Health</h2>@STATUS@</section>
  <section class="card"><h2>Quick manual</h2>
    <p><code>/handoff</code> — load context in a new chat (journal + handoff + knowledge)<br>
    <code>/done</code> — save session before closing a chat<br>
    <code>/remember fact</code> — store a lasting fact<br>
    <code>orchestra query "what did we decide about X"</code> — search the brain<br>
    <code>orchestra serve</code> — this page · <code>doctor</code> · <code>commit</code> · <code>migrate</code> · <code>sync</code> · <code>upgrade</code></p>
    <p class="muted">Full manual: Orchestra repo, <code>docs/MANUAL.md</code>.</p>
  </section>
  <div class="grid">
    <section class="card"><h2>Identity — memory/IDENTITY.md</h2>@IDENTITY@</section>
    <section class="card"><h2>Knowledge — memory/knowledge/notes.md</h2>@NOTES@</section>
  </div>
  <section class="card"><h2>Journal — memory/journal/ (newest first)</h2>@JOURNAL@</section>
  <section class="card"><h2>Handoff — .orchestra/handoff.md of this folder</h2>@HANDOFF@</section>
</main>
<script>
async function commit(){
  var m=document.getElementById('msg');m.textContent='committing…';
  var r=await fetch('/commit',{method:'POST'});
  m.textContent=await r.text();
}
</script>
</body>
</html>
"""


def render_dashboard(brain):
    esc = html.escape
    version = "?"
    if (brain / "VERSION").exists():
        version = (brain / "VERSION").read_text(encoding="utf-8").strip()

    results, repo_ok = doctor_results(brain)
    rows = []
    for label, path, present in results:
        cls = "ok" if present else "bad"
        suffix = ""
        if path is not None:
            suffix = " <span class='muted'>" + esc(str(path)) + "</span>"
        rows.append("<li class='" + cls + "'>" + esc(label) + suffix + "</li>")
    rows.append("<li class='" + ("ok" if repo_ok else "bad") + "'>memory git repo</li>")
    status_html = "<ul class='checks'>" + "".join(rows) + "</ul>"

    identity_html = "<p class='muted'>not found</p>"
    identity_path = brain / "memory" / "IDENTITY.md"
    if identity_path.exists():
        text = identity_path.read_text(encoding="utf-8-sig")
        identity_html = "<pre>" + esc("\n".join(text.splitlines()[:60])) + "</pre>"

    journal_html = "<p class='muted'>no journal entries yet — run /done after a session.</p>"
    journal_dir = brain / "memory" / "journal"
    if journal_dir.exists():
        entries = []
        for p in sorted(journal_dir.glob("*.md"), reverse=True):
            text = p.read_text(encoding="utf-8-sig")
            short = "\n".join(text.splitlines()[:45])
            entries.append("<h3>" + esc(p.stem) + "</h3><pre>" + esc(short) + "</pre>")
        if entries:
            journal_html = "".join(entries)

    notes_html = "<p class='muted'>not found</p>"
    notes_path = brain / "memory" / "knowledge" / "notes.md"
    if notes_path.exists():
        notes_html = "<pre>" + esc(notes_path.read_text(encoding="utf-8-sig")) + "</pre>"

    handoff_html = "<p class='muted'>no handoff for this folder yet — run /handoff in opencode.</p>"
    handoff_path = Path.cwd() / ".orchestra" / "handoff.md"
    if handoff_path.exists():
        handoff_html = "<pre>" + esc(handoff_path.read_text(encoding="utf-8-sig")) + "</pre>"

    page = DASHBOARD_TEMPLATE
    for token, value in [
        ("@VERSION@", esc(version)),
        ("@STATUS@", status_html),
        ("@IDENTITY@", identity_html),
        ("@JOURNAL@", journal_html),
        ("@NOTES@", notes_html),
        ("@HANDOFF@", handoff_html),
    ]:
        page = page.replace(token, value)
    return page


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    brain = None

    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        body = render_dashboard(self.brain).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path == "/commit":
            message = "memory: " + datetime.now().strftime("%Y-%m-%d %H:%M")
            ok = git_commit(self.brain / "memory", message)
            text = "Committed: " + message if ok else "Nothing to commit (or git unavailable)."
        else:
            self.send_error(404)
            return
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def cmd_serve(port):
    brain = brain_dir()
    handler = type("Handler", (DashboardHandler,), {"brain": brain})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = "http://127.0.0.1:" + str(port) + "/"
    print("Orchestra dashboard: " + url + "  (Ctrl+C to stop)")
    if not os.environ.get("ORCHESTRA_NO_BROWSER"):
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    parser = argparse.ArgumentParser(prog="orchestra", description="Orchestra — session memory helper for opencode")
    parser.add_argument("--home", help="override brain directory (useful for testing)")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("install", help="copy repo into the global config and init memory git repo").add_argument("source", nargs="?", help="repo directory (default: this script's folder)")
    sub.add_parser("doctor", help="validate the installed setup")
    sub.add_parser("status", help="list installed files")
    sub.add_parser("commit", help="git-commit the memory folder")
    sub.add_parser("migrate", help="rebuild the SQLite memory index from markdown")
    sub.add_parser("query", help="search the memory index (FTS5)").add_argument("text", help="search phrase, e.g. \"what did we decide about X\"")
    sub.add_parser("sync", help="pull + commit + push the memory repo")
    sub.add_parser("start", help="create .orchestra/handoff.md in a project").add_argument("project", nargs="?")
    sub.add_parser("handoff", help="print a deterministic context briefing").add_argument("project", nargs="?")
    serve = sub.add_parser("serve", help="open the local visual dashboard")
    serve.add_argument("port", nargs="?", type=int, default=8714)
    serve.add_argument("--no-browser", action="store_true")
    sub.add_parser("upgrade", help="backup, migrate, verify, report").add_argument("source", nargs="?", help="repo directory to pull new files from (default: this script's folder)")

    args = parser.parse_args()
    if args.home:
        os.environ["ORCHESTRA_HOME"] = args.home
    cmd = args.command
    if cmd == "install":
        sys.exit(cmd_install(args.source))
    if cmd == "doctor":
        sys.exit(cmd_doctor())
    if cmd == "status":
        cmd_status()
    elif cmd == "commit":
        cmd_commit()
    elif cmd == "migrate":
        sys.exit(cmd_migrate())
    elif cmd == "query":
        sys.exit(cmd_query(args.text))
    elif cmd == "sync":
        sys.exit(cmd_sync())
    elif cmd == "start":
        cmd_start(args.project)
    elif cmd == "handoff":
        cmd_handoff(args.project)
    elif cmd == "serve":
        if args.no_browser:
            os.environ.setdefault("ORCHESTRA_NO_BROWSER", "1")
        cmd_serve(args.port)
    elif cmd == "upgrade":
        sys.exit(cmd_upgrade(args.source))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()