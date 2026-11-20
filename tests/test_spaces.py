import json
import tempfile
import unittest
from pathlib import Path

from still.core import BrowserState, DEFAULT_SPACE, MAX_SPACES, StateStore, Tab


class SpaceTests(unittest.TestCase):
    def setUp(self):
        self.state = BrowserState()
        self.state.ensure_tab()

    def test_new_space_is_empty_and_active(self):
        home = self.state.active()
        space = self.state.add_space("Work", "blue")
        self.assertEqual(self.state.active_space_id, space.id)
        self.assertEqual(self.state.active().space_id, space.id)
        self.assertNotEqual(home.id, self.state.active_id)

    def test_switch_restores_last_active_tab(self):
        space = self.state.add_space("Research", "sage")
        tab = Tab(space_id=space.id, url="https://example.org")
        self.state.tabs.append(tab)
        self.state.select_tab(tab.id)
        self.state.switch_space(DEFAULT_SPACE)
        self.assertEqual(self.state.active().space_id, DEFAULT_SPACE)
        self.state.switch_space(space.id)
        self.assertEqual(self.state.active_id, tab.id)

    def test_tabs_separated_by_space(self):
        space = self.state.add_space("Research")
        self.assertTrue(all(t.space_id == space.id for t in self.state.tabs_in_space()))
        self.state.switch_space(DEFAULT_SPACE)
        self.assertTrue(all(t.space_id == DEFAULT_SPACE for t in self.state.tabs_in_space()))

    def test_move_tab_unpins_and_keeps_it(self):
        tab = self.state.active()
        tab.pinned = True
        space = self.state.add_space("Other")
        self.state.switch_space(DEFAULT_SPACE)
        self.state.move_tab(tab.id, space.id)
        self.assertIn(tab, self.state.tabs_in_space(space.id))
        self.assertFalse(tab.pinned)
        self.assertEqual(len(self.state.tabs_in_space()), 1)

    def test_private_cannot_move(self):
        private = Tab(private=True)
        self.state.tabs.append(private)
        space = self.state.add_space("Work")
        with self.assertRaises(ValueError):
            self.state.move_tab(private.id, space.id)

    def test_private_id_not_persisted_in_space_metadata(self):
        space = self.state.add_space("Research")
        private = Tab(private=True, space_id=space.id,
                      url="https://secret.example", title="Secret")
        self.state.tabs.append(private)
        self.state.select_tab(private.id)
        serialized = json.dumps(self.state.saved_dict())
        self.assertNotIn(private.id, serialized)
        self.assertNotIn("secret.example", serialized)
        loaded = BrowserState.from_json(json.loads(serialized))
        self.assertEqual(loaded.active_space_id, space.id)
        self.assertFalse(loaded.active().private)

    def test_v1_migration_keeps_tabs_and_bookmarks(self):
        old = {"version": 1,
               "tabs": [{"id": "abc", "url": "https://example.com",
                         "title": "Example", "pinned": True}],
               "active_id": "abc",
               "bookmarks": [{"url": "https://example.com", "title": "Example"}],
               "history": [], "layout": "side", "theme": "dark"}
        state = BrowserState.from_json(old)
        self.assertEqual(state.active().url, "https://example.com")
        self.assertTrue(state.active().pinned)
        self.assertEqual(state.active().space_id, DEFAULT_SPACE)
        self.assertEqual(state.bookmarks, old["bookmarks"])
        self.assertEqual(state.saved_dict()["version"], 2)

    def test_roundtrip_retains_space_name_color_and_tab(self):
        with tempfile.TemporaryDirectory() as root:
            self.state.add_space("Research", "amber")
            self.state.active().url = "https://example.net"
            store = StateStore(Path(root))
            store.save(self.state)
            recovered = store.load()
            self.assertEqual(recovered.current_space().name, "Research")
            self.assertEqual(recovered.current_space().color, "amber")
            self.assertEqual(recovered.active().url, "https://example.net")

    def test_limits_invalid_names_and_invalid_colors(self):
        with self.assertRaises(ValueError):
            self.state.switch_space("missing")
        with self.assertRaises(ValueError):
            self.state.add_space("")
        with self.assertRaises(ValueError):
            self.state.add_space("Invalid", "neon")
        for n in range(MAX_SPACES - 1):
            self.state.add_space(f"Space {n}")
        with self.assertRaises(ValueError):
            self.state.add_space("One too many")

    def test_delete_final_space_denied(self):
        with self.assertRaises(ValueError):
            self.state.delete_space(DEFAULT_SPACE)
        space = self.state.add_space("Work")
        self.state.delete_space(space.id)
        self.assertEqual(self.state.active_space_id, DEFAULT_SPACE)


if __name__ == "__main__":
    unittest.main()
