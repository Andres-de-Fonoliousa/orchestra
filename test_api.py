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

if __name__ == '__main__':
    unittest.main()
