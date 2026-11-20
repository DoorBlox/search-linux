import unittest
from still.core import BrowserState, Tab, DEFAULT_SPACE


class GroupTests(unittest.TestCase):
    def setUp(self):
        self.state = BrowserState()
        self.state.ensure_tab()

    def test_create_group_from_pinned_tab(self):
        tab = self.state.active()
        tab.pinned = True
        g = self.state.create_group("Research", tab.id)
        self.assertEqual(tab.group_id, g.id)
        self.assertFalse(tab.pinned)
        self.assertEqual(g.space_id, DEFAULT_SPACE)

    def test_collapse_rename_roundtrip(self):
        g = self.state.create_group("Old")
        self.assertTrue(self.state.toggle_group(g.id))
        self.state.rename_group(g.id, "Reading")
        restored = BrowserState.from_json(self.state.saved_dict())
        self.assertEqual(restored.groups[0].name, "Reading")
        self.assertTrue(restored.groups[0].collapsed)

    def test_remove_group_preserves_tabs(self):
        tab = self.state.active()
        g = self.state.create_group("Work", tab.id)
        self.state.delete_group(g.id)
        self.assertIn(tab, self.state.tabs)
        self.assertIsNone(tab.group_id)

    def test_group_never_crosses_spaces(self):
        tab = self.state.active()
        self.state.add_space("Work")
        g = self.state.create_group("Group")
        with self.assertRaises(ValueError):
            self.state.set_tab_group(tab.id, g.id)
        self.assertIsNone(tab.group_id)

    def test_private_group_denied(self):
        g = self.state.create_group("Private?")
        tab = Tab(private=True)
        self.state.tabs.append(tab)
        with self.assertRaises(ValueError):
            self.state.set_tab_group(tab.id, g.id)
        with self.assertRaises(ValueError):
            self.state.create_group("Bad", tab.id)

    def test_reorder_only_group_peers(self):
        first = self.state.active()
        second = Tab(space_id=DEFAULT_SPACE, title="Second")
        third = Tab(space_id=DEFAULT_SPACE, title="Third")
        self.state.tabs.extend((second, third))
        g = self.state.create_group("Group", first.id)
        self.state.set_tab_group(second.id, g.id)
        self.state.move_tab_in_group(second.id, -1)
        order = [t.id for t in self.state.tabs if t.group_id == g.id]
        self.assertEqual(order, [second.id, first.id])
        self.assertEqual(self.state.tabs[-1], third)

    def test_moving_between_spaces_ungroups(self):
        tab = self.state.active()
        self.state.create_group("Research", tab.id)
        other = self.state.add_space("Work")
        self.state.switch_space(DEFAULT_SPACE)
        self.state.move_tab(tab.id, other.id)
        self.assertIsNone(tab.group_id)
        self.assertEqual(tab.space_id, other.id)

    def test_delete_space_deletes_only_its_groups(self):
        other = self.state.add_space("Work")
        g = self.state.create_group("Research", self.state.active_id)
        self.state.delete_space(other.id)
        self.assertNotIn(g, self.state.groups)

    def test_v2_migration_preserves_tabs(self):
        old = self.state.saved_dict()
        old["version"] = 2
        old.pop("groups", None)
        loaded = BrowserState.from_json(old)
        self.assertEqual(loaded.active_id, self.state.active_id)
        self.assertEqual(loaded.groups, [])
        self.assertEqual(loaded.saved_dict()["version"], 3)

    def test_invalid_group_binding_removed_on_load(self):
        raw = self.state.saved_dict()
        raw["tabs"][0]["group_id"] = "not-existent"
        state = BrowserState.from_json(raw)
        self.assertIsNone(state.active().group_id)

    def test_space_color_set_persists(self):
        self.state.set_space_color(DEFAULT_SPACE, "violet")
        loaded = BrowserState.from_json(self.state.saved_dict())
        self.assertEqual(loaded.current_space().color, "violet")
        with self.assertRaises(ValueError):
            self.state.set_space_color(DEFAULT_SPACE, "invalid")


if __name__ == "__main__":
    unittest.main()
