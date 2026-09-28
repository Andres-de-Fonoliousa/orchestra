import sqlite3, pathlib
db = pathlib.Path.home() / ".config" / "opencode" / "memory" / "runs.db"
conn = sqlite3.connect(str(db))
conn.execute("UPDATE run_agents SET status='blocked', verdict='FAIL' WHERE run_id=5 AND role='frontend'")
conn.execute("UPDATE runs SET status='partial' WHERE id=5")
conn.commit()
conn.close()
print("Marked frontend as blocked for run 5")
