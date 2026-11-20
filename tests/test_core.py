import json
import tempfile
import unittest
from pathlib import Path

from still.core import BrowserState, StateStore, Tab, normalize_location, safe_display_url


class LocationTests(unittest.TestCase):
    def test_normalize(self):
        cases = {
            "https://example.org/x?q=1": "https://example.org/x?q=1",
            "example.com/foo": "https://example.com/foo",
            "localhost:3000": "http://localhost:3000",
            "127.0.0.1:8888": "http://127.0.0.1:8888",
            "[::1]:8080": "http://[::1]:8080",
            "two words": "https://www.google.com/search?q=two+words",
            "javascript:alert(1)": "https://www.google.com/search?q=javascript%3Aalert%281%29",
            "file:///etc/passwd": "https://www.google.com/search?q=file%3A%2F%2F%2Fetc%2Fpasswd",
            "": "about:blank",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(normalize_location(source), expected)

    def test_embedded_password_rejected(self):
        with self.assertRaises(ValueError):
            normalize_location("https://username:secret@example.com")

    def test_display_url_removes_password(self):
        self.assertEqual(safe_display_url("https://u:pass@example.org:443/path?q=2#f"),
                         "https://example.org:443/path?q=2")


class BrowserPrivacyTests(unittest.TestCase):
    def test_private_tab_never_serialized_or_restored_as_active(self):
        normal = Tab(url="https://example.org")
        private = Tab(url="https://sensitive.example", title="Secret", private=True)
        st = BrowserState(tabs=[normal, private], active_id=private.id)
        st.record_visit(private.url, private.title, private=True)
        dumped = json.dumps(st.saved_dict())
        self.assertNotIn("sensitive.example", dumped)
        self.assertNotIn("Secret", dumped)
        restored = BrowserState.from_json(json.loads(dumped))
        self.assertEqual(len(restored.tabs), 1)
        self.assertEqual(restored.active_id, normal.id)

    def test_visit_limit_and_private_history(self):
        st = BrowserState()
        st.record_visit("https://example.org/1", "One", private=True)
        self.assertEqual(st.history, [])
        st.record_visit("https://example.org/2", "Two")
        self.assertEqual(len(st.history), 1)

    def test_bookmark_toggle(self):
        st = BrowserState()
        self.assertTrue(st.toggle_bookmark("https://example.org", "Home"))
        self.assertFalse(st.toggle_bookmark("https://example.org", "Home"))
        self.assertEqual(st.bookmarks, [])

    def test_corrupt_file_recovers_without_wiping_it(self):
        with tempfile.TemporaryDirectory() as root:
            file = Path(root) / "state.json"
            file.write_text("{bad json", encoding="utf-8")
            state = StateStore(Path(root)).load()
            self.assertEqual(len(state.tabs), 1)
            self.assertEqual(file.read_text(encoding="utf-8"), "{bad json")

    def test_private_state_not_on_disk(self):
        with tempfile.TemporaryDirectory() as root:
            st = BrowserState(tabs=[Tab(url="https://normal.example"),
                                    Tab(url="https://private.example", private=True)])
            store = StateStore(Path(root))
            store.save(st)
            data = store.file.read_text(encoding="utf-8")
            self.assertNotIn("private.example", data)
            self.assertIn("normal.example", data)
            self.assertEqual(store.load().tabs[0].url, "https://normal.example")

    def test_file_private_permissions(self):
        with tempfile.TemporaryDirectory() as root:
            store = StateStore(Path(root))
            store.save(BrowserState())
            self.assertEqual(store.file.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
