import importlib.util
import unittest
from pathlib import Path
from urllib.error import URLError

path = Path(__file__).resolve().parents[1] / 'scripts' / 'daily_source_monitor.py'
spec = importlib.util.spec_from_file_location('monitor', path)
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)

class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.sources = [dict(id='ssc', name='SSC', url='https://ssc.gov.in/')]
        self.today = '2026-10-28'

    def test_new_baseline_does_not_mean_verified_vacancy(self):
        state, obs = monitor.monitor_sources(self.sources, {'sources': {}}, lambda _: 'abc', self.today)
        self.assertEqual(obs[0][1], 'baseline')
        self.assertEqual(state['sources']['ssc']['status'], 'reachable')
        self.assertNotIn('jobs', state)

    def test_unchanged_pages_do_not_modify_state(self):
        initial = {'sources': {'ssc': {'name':'SSC', 'url':'https://ssc.gov.in/', 'status':'reachable', 'fingerprint':'abc', 'last_change_or_status_date':'2026-10-27'}}}
        state, obs = monitor.monitor_sources(self.sources, initial, lambda _: 'abc', self.today)
        self.assertEqual(obs[0][1], 'unchanged')
        self.assertEqual(state['sources']['ssc'], initial['sources']['ssc'])

    def test_changed_page_is_only_a_lead(self):
        initial = {'sources': {'ssc': {'status': 'reachable', 'fingerprint':'abc'}}}
        state, obs = monitor.monitor_sources(self.sources, initial, lambda _: 'new', self.today)
        self.assertEqual(obs[0][1], 'possible_change')
        self.assertNotIn('vacancies', state['sources']['ssc'])

    def test_network_error_does_not_erase_previous_fingerprint(self):
        initial = {'sources': {'ssc': {'status': 'reachable', 'fingerprint':'abc'}}}
        def blocked(_):
            raise URLError('restricted')
        state, obs = monitor.monitor_sources(self.sources, initial, blocked, self.today)
        self.assertEqual(obs[0][1], 'unreachable')
        self.assertEqual(state['sources']['ssc']['fingerprint'], 'abc')

    def test_normalize_ignores_script_noise(self):
        first = monitor.canonical_content(b'<main>Hello India</main><script>var n=1</script>', 'text/html')
        second = monitor.canonical_content(b'<main> Hello India </main><script>var n=2</script>', 'text/html')
        self.assertEqual(first, second)

if __name__ == '__main__':
    unittest.main()
