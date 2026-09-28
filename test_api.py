import unittest
from api import app

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_agents(self):
        response = self.app.get('/api/agents')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_get_runs(self):
        response = self.app.get('/api/runs')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_create_run_missing_goal(self):
        response = self.app.post('/api/runs', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_get_monitor_telemetry(self):
        response = self.app.get('/api/monitor/telemetry')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("total_runs", data)
        self.assertIn("success_rate", data)
        self.assertIn("recent_errors", data)

    def test_get_run_errors(self):
        response = self.app.get('/api/runs/999999/errors')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_run_session_state(self):
        from api import get_runs_db
        conn = get_runs_db()
        conn.execute("INSERT OR REPLACE INTO runs (id, goal, status, created_at, updated_at) VALUES (999, 'Test Goal', 'planning', '2026-09-27 00:00:00', '2026-09-27 00:00:00')")
        conn.commit()
        conn.close()

        # Test updating and getting session state for run ID 999
        res_post = self.app.post('/api/runs/999/session', json={"status": "testing", "checkpoint": "step1"})
        self.assertEqual(res_post.status_code, 200)
        
        res_get = self.app.get('/api/runs/999/session')
        self.assertEqual(res_get.status_code, 200)
        data = res_get.get_json()
        self.assertEqual(data.get("status"), "testing")
        self.assertEqual(data.get("checkpoint"), "step1")

    def test_run_guidance(self):
        from api import get_runs_db
        conn = get_runs_db()
        conn.execute("INSERT OR REPLACE INTO runs (id, goal, status, created_at, updated_at) VALUES (1000, 'Test Guidance Goal', 'running', '2026-09-27 00:00:00', '2026-09-27 00:00:00')")
        conn.commit()
        conn.close()

        res = self.app.post('/api/runs/1000/guidance', json={"guidance": "Focus on unit tests"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "success")

    def test_orchestrator_interact(self):
        res = self.app.post('/api/orchestrator/interact', json={"prompt": "Status report"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("response", data)

    def test_run_control(self):
        from api import get_runs_db
        conn = get_runs_db()
        conn.execute("INSERT OR REPLACE INTO runs (id, goal, status, created_at, updated_at) VALUES (1001, 'Test Control Goal', 'running', '2026-09-27 00:00:00', '2026-09-27 00:00:00')")
        conn.commit()
        conn.close()

        res = self.app.post('/api/runs/1001/control', json={"action": "pause"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("run_status"), "paused")

if __name__ == '__main__':
    unittest.main()
