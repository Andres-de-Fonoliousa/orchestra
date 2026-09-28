import sqlite3, pathlib
db = pathlib.Path.home() / ".config" / "opencode" / "memory" / "runs.db"
conn = sqlite3.connect(str(db))
conn.execute("UPDATE run_agents SET status='queued', retries=0 WHERE run_id=5 AND status='blocked'")
conn.execute("UPDATE runs SET status='running' WHERE id=5")
conn.commit()
conn.close()
print("Run 5 reset successfully")
