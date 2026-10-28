import importlib.util
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError

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

    def test_http_block_is_diagnostic_not_a_closed_vacancy(self):
        blocked = HTTPError('https://ssc.gov.in/', 403, 'Forbidden', None, None)
        label = monitor.describe_fetch_failure(blocked)
        self.assertIn('HTTP 403', label)
        state, obs = monitor.monitor_sources(self.sources, {'sources': {}},
                                             lambda _: (_ for _ in ()).throw(blocked), self.today)
        self.assertEqual(obs[0][1], 'unreachable')
        self.assertIn('HTTP 403', state['sources']['ssc']['note'])
        self.assertNotIn('jobs', state)

    def test_same_error_reason_avoids_repeated_state_changes(self):
        def inaccessible(_):
            raise URLError('restricted')
        first, _ = monitor.monitor_sources(self.sources, {'sources': {}}, inaccessible, self.today)
        second, observations = monitor.monitor_sources(self.sources, first, inaccessible, '2026-10-29')
        self.assertEqual(observations[0][1], 'unchanged_unreachable')
        self.assertEqual(first, second)

    def test_different_error_reason_updates_monitor_diagnostic(self):
        first, _ = monitor.monitor_sources(self.sources, {'sources': {}},
                                          lambda _: (_ for _ in ()).throw(URLError('offline')), self.today)
        def rejected(_):
            raise HTTPError('https://ssc.gov.in/', 429, 'Too Many Requests', None, None)
        second, observations = monitor.monitor_sources(self.sources, first, rejected, '2026-10-29')
        self.assertEqual(observations[0][1], 'unreachable')
        self.assertIn('HTTP 429', second['sources']['ssc']['note'])

    def test_recovery_does_not_claim_new_verified_vacancy(self):
        first, _ = monitor.monitor_sources(self.sources, {'sources': {}},
                                          lambda _: (_ for _ in ()).throw(URLError('offline')), self.today)
        second, observations = monitor.monitor_sources(self.sources, first, lambda _: 'digest', '2026-10-29')
        self.assertEqual(observations[0][1], 'baseline')
        self.assertEqual(second['sources']['ssc']['status'], 'reachable')
        self.assertNotIn('jobs', second)

    def test_report_contains_diagnostic_and_counts(self):
        def denied(_):
            raise HTTPError('https://ssc.gov.in/', 403, 'Forbidden', None, None)
        state, _ = monitor.monitor_sources(self.sources, {'sources': {}}, denied, self.today)
        report = monitor.report_markdown(state)
        self.assertIn('Unreachable:** 1', report)
        self.assertIn('HTTP 403', report)
        self.assertIn('not** proof', report)
        self.assertNotIn('verified new vacancies', report.splitlines()[-1])

    def test_normalize_ignores_script_noise(self):
        first = monitor.canonical_content(b'<main>Hello India</main><script>var n=1</script>', 'text/html')
        second = monitor.canonical_content(b'<main> Hello India </main><script>var n=2</script>', 'text/html')
        self.assertEqual(first, second)

if __name__ == '__main__':
    unittest.main()
