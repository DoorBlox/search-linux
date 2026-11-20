"""GUI-independent URL, tabs, Spaces, privacy and atomic persistence models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus, urlsplit, urlunsplit
import json
import os
import re
import tempfile
import uuid

SCHEMA = 3
DEFAULT_SPACE = "home"
SPACE_COLORS = ("neutral", "blue", "sage", "amber", "rose", "violet")
MAX_SPACES = 12
MAX_GROUPS = 80
SEARCH_TEMPLATE = "https://www.google.com/search?q={query}"
HOME = "about:blank"
MAX_HISTORY = 2000


def data_dir() -> Path:
    root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "still-browser"


def cache_dir() -> Path:
    root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return root / "still-browser"


def normalize_location(text: str, template: str = SEARCH_TEMPLATE) -> str:
    """An intentional, Enter-only omnibox. Never execute javascript/data/file URLs."""
    text = text.strip()
    if not text:
        return HOME
    if not re.search(r"\s", text) and text.lower().startswith(("localhost:", "127.0.0.1:", "[::1]:")):
        return f"http://{text}"
    try:
        parts = urlsplit(text)
    except ValueError:
        return template.format(query=quote_plus(text))
    if parts.scheme.lower() in ("http", "https") and parts.netloc:
        if parts.username is not None or parts.password is not None:
            raise ValueError("URLs with embedded credentials are not supported")
        if re.search(r"\s", parts.netloc):
            raise ValueError("Invalid web address")
        try:
            _ = parts.port
        except ValueError as exc:
            raise ValueError("Invalid web address port") from exc
        return text
    if text == HOME:
        return HOME
    if parts.scheme and parts.scheme.lower() not in ("http", "https"):
        return template.format(query=quote_plus(text))
    if not re.search(r"\s", text) and (
        text.lower().startswith("localhost")
        or text.startswith("127.0.0.1")
        or text.startswith("[::1]")
        or ("." in text.split("/", 1)[0] and not text.startswith("."))
    ):
        scheme = "http" if text.lower().startswith(("localhost", "127.0.0.1", "[::1]")) else "https"
        return f"{scheme}://{text}"
    return template.format(query=quote_plus(text))


def safe_display_url(url: str) -> str:
    """A URL displayed to the user, without its fragment or embedded credentials."""
    try:
        parts = urlsplit(url)
        host = parts.hostname or ""
        if not host:
            return url
        port = f":{parts.port}" if parts.port else ""
        return urlunsplit((parts.scheme, f"{host}{port}", parts.path, parts.query, ""))
    except ValueError:
        return ""


def today_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Tab:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    url: str = HOME
    title: str = "New Tab"
    pinned: bool = False
    private: bool = False
    space_id: str = DEFAULT_SPACE
    group_id: str | None = None

    def snapshot(self) -> dict:
        return {"id": self.id, "url": self.url, "title": self.title,
                "pinned": self.pinned, "space_id": self.space_id, "group_id": self.group_id}

    @classmethod
    def from_json(cls, raw: dict) -> "Tab":
        if not isinstance(raw, dict):
            raise ValueError("invalid saved tab")
        location = str(raw.get("url", HOME))
        if location != HOME and urlsplit(location).scheme not in ("https", "http"):
            location = HOME
        title = str(raw.get("title", "New Tab"))[:200] or "New Tab"
        return cls(id=str(raw.get("id"))[:64] or uuid.uuid4().hex,
                   url=location, title=title, pinned=bool(raw.get("pinned", False)),
                   space_id=str(raw.get("space_id", DEFAULT_SPACE))[:64],
                   group_id=str(raw.get("group_id"))[:64] if raw.get("group_id") else None)


@dataclass
class Space:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = "Personal"
    color: str = "neutral"
    last_active_id: str | None = None

    def snapshot(self) -> dict:
        return {"id": self.id, "name": self.name, "color": self.color,
                "last_active_id": self.last_active_id}

    @classmethod
    def from_json(cls, raw: dict) -> "Space":
        if not isinstance(raw, dict):
            raise ValueError("invalid saved space")
        name = str(raw.get("name", "Space")).strip()[:32] or "Space"
        color = raw.get("color", "neutral")
        return cls(id=str(raw.get("id", ""))[:64] or uuid.uuid4().hex,
                   name=name, color=color if color in SPACE_COLORS else "neutral",
                   last_active_id=raw.get("last_active_id"))


@dataclass
class TabGroup:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = "Group"
    space_id: str = DEFAULT_SPACE
    collapsed: bool = False

    def snapshot(self) -> dict:
        return {"id": self.id, "name": self.name, "space_id": self.space_id,
                "collapsed": self.collapsed}

    @classmethod
    def from_json(cls, raw: dict) -> "TabGroup":
        if not isinstance(raw, dict):
            raise ValueError("invalid saved group")
        name = str(raw.get("name", "Group")).strip()[:40] or "Group"
        return cls(id=str(raw.get("id", ""))[:64] or uuid.uuid4().hex,
                   name=name, space_id=str(raw.get("space_id", DEFAULT_SPACE))[:64],
                   collapsed=bool(raw.get("collapsed", False)))


@dataclass
class BrowserState:
    tabs: list[Tab] = field(default_factory=list)
    groups: list[TabGroup] = field(default_factory=list)
    spaces: list[Space] = field(default_factory=lambda: [Space(id=DEFAULT_SPACE)])
    active_space_id: str = DEFAULT_SPACE
    active_id: str | None = None
    history: list[dict] = field(default_factory=list)
    bookmarks: list[dict] = field(default_factory=list)
    layout: str = "side"
    theme: str = "system"
    sidebar_hidden: bool = False

    def current_space(self) -> Space:
        if not self.spaces:
            self.spaces.append(Space(id=DEFAULT_SPACE))
        found = next((s for s in self.spaces if s.id == self.active_space_id), None)
        if found is None:
            found = self.spaces[0]
            self.active_space_id = found.id
        return found

    def tabs_in_space(self, space_id: str | None = None) -> list[Tab]:
        selected = space_id or self.current_space().id
        return [tab for tab in self.tabs if tab.space_id == selected]

    def ensure_tab(self) -> None:
        space = self.current_space()
        visible = self.tabs_in_space()
        if not visible:
            tab = Tab(space_id=space.id)
            self.tabs.append(tab)
            self.active_id = tab.id
            space.last_active_id = tab.id
        elif self.active_id not in {t.id for t in visible}:
            self.active_id = (space.last_active_id if space.last_active_id in
                              {t.id for t in visible} else visible[0].id)
            space.last_active_id = self.active_id

    def active(self) -> Tab | None:
        return next((t for t in self.tabs if t.id == self.active_id
                     and t.space_id == self.active_space_id), None)

    def select_tab(self, tab_id: str) -> Tab:
        tab = next((t for t in self.tabs if t.id == tab_id), None)
        if tab is None:
            raise ValueError("unknown tab")
        self.active_space_id = tab.space_id
        self.active_id = tab.id
        self.current_space().last_active_id = tab.id
        return tab

    def switch_space(self, space_id: str) -> Tab:
        if not any(s.id == space_id for s in self.spaces):
            raise ValueError("unknown space")
        self.active_space_id = space_id
        self.ensure_tab()
        return self.active()

    def add_space(self, name: str, color: str = "neutral") -> Space:
        name = name.strip()[:32]
        if not name:
            raise ValueError("space name cannot be empty")
        if color not in SPACE_COLORS:
            raise ValueError("unsupported space color")
        if len(self.spaces) >= MAX_SPACES:
            raise ValueError("space limit reached")
        space = Space(name=name, color=color)
        self.spaces.append(space)
        self.switch_space(space.id)
        return space

    def rename_space(self, space_id: str, name: str) -> None:
        name = name.strip()[:32]
        if not name:
            raise ValueError("space name cannot be empty")
        space = next((s for s in self.spaces if s.id == space_id), None)
        if space is None:
            raise ValueError("unknown space")
        space.name = name

    def move_tab(self, tab_id: str, target_space_id: str) -> None:
        if not any(s.id == target_space_id for s in self.spaces):
            raise ValueError("unknown target space")
        tab = next((t for t in self.tabs if t.id == tab_id), None)
        if tab is None:
            raise ValueError("unknown tab")
        if tab.private:
            raise ValueError("private tabs cannot be moved between spaces")
        tab.space_id = target_space_id
        tab.group_id = None
        tab.pinned = False
        if tab_id == self.active_id:
            self.ensure_tab()

    def delete_space(self, space_id: str) -> None:
        if len(self.spaces) <= 1:
            raise ValueError("cannot remove final space")
        if not any(s.id == space_id for s in self.spaces):
            raise ValueError("unknown space")
        self.tabs = [t for t in self.tabs if t.space_id != space_id]
        self.groups = [g for g in self.groups if g.space_id != space_id]
        self.spaces = [s for s in self.spaces if s.id != space_id]
        if self.active_space_id == space_id:
            self.active_space_id = self.spaces[0].id
        self.ensure_tab()

    def set_space_color(self, space_id: str, color: str) -> None:
        if color not in SPACE_COLORS:
            raise ValueError("unsupported space color")
        space = next((s for s in self.spaces if s.id == space_id), None)
        if space is None:
            raise ValueError("unknown space")
        space.color = color

    def groups_in_space(self, space_id: str | None = None) -> list[TabGroup]:
        selected = space_id or self.current_space().id
        return [group for group in self.groups if group.space_id == selected]

    def create_group(self, name: str, tab_id: str | None = None) -> TabGroup:
        name = name.strip()[:40]
        if not name:
            raise ValueError("group name cannot be empty")
        if len(self.groups) >= MAX_GROUPS:
            raise ValueError("group limit reached")
        group = TabGroup(name=name, space_id=self.current_space().id)
        if tab_id is not None:
            tab = next((t for t in self.tabs if t.id == tab_id), None)
            if tab is None or tab.space_id != group.space_id or tab.private:
                raise ValueError("cannot group this tab")
        self.groups.append(group)
        if tab_id is not None:
            self.set_tab_group(tab_id, group.id)
        return group

    def rename_group(self, group_id: str, name: str) -> None:
        name = name.strip()[:40]
        group = next((g for g in self.groups if g.id == group_id), None)
        if group is None or not name:
            raise ValueError("invalid group or name")
        group.name = name

    def toggle_group(self, group_id: str) -> bool:
        group = next((g for g in self.groups if g.id == group_id), None)
        if group is None:
            raise ValueError("unknown group")
        group.collapsed = not group.collapsed
        return group.collapsed

    def set_tab_group(self, tab_id: str, group_id: str | None) -> None:
        tab = next((t for t in self.tabs if t.id == tab_id), None)
        if tab is None or tab.private:
            raise ValueError("invalid tab for grouping")
        group = next((g for g in self.groups if g.id == group_id), None) if group_id else None
        if group_id is not None and (group is None or group.space_id != tab.space_id):
            raise ValueError("cannot group across spaces")
        tab.group_id = group_id
        if group is not None:
            tab.pinned = False
            group.collapsed = False

    def delete_group(self, group_id: str) -> None:
        if not any(g.id == group_id for g in self.groups):
            raise ValueError("unknown group")
        for tab in self.tabs:
            if tab.group_id == group_id:
                tab.group_id = None
        self.groups = [g for g in self.groups if g.id != group_id]

    def move_tab_in_group(self, tab_id: str, delta: int) -> None:
        tab = next((t for t in self.tabs if t.id == tab_id), None)
        if tab is None:
            raise ValueError("unknown tab")
        siblings = [t for t in self.tabs if t.space_id == tab.space_id and
                    t.group_id == tab.group_id and t.pinned == tab.pinned]
        index = siblings.index(tab)
        target = index + delta
        if not 0 <= target < len(siblings):
            return
        left, right = self.tabs.index(tab), self.tabs.index(siblings[target])
        self.tabs[left], self.tabs[right] = self.tabs[right], self.tabs[left]

    def record_visit(self, url: str, title: str, *, private: bool = False) -> None:
        if private or url == HOME or urlsplit(url).scheme not in ("http", "https"):
            return
        if urlsplit(url).username is not None:
            return
        self.history.insert(0, {"url": url, "title": title[:200], "visited": today_utc()})
        self.history = self.history[:MAX_HISTORY]

    def toggle_bookmark(self, url: str, title: str) -> bool:
        current = next((b for b in self.bookmarks if b.get("url") == url), None)
        if current:
            self.bookmarks.remove(current)
            return False
        if urlsplit(url).scheme not in ("http", "https"):
            return False
        self.bookmarks.append({"url": url, "title": title[:200]})
        return True

    def saved_dict(self) -> dict:
        # Private tabs, their IDs, titles and URLs must never reach disk.
        normal = [t for t in self.tabs if not t.private]
        active_space = self.current_space().id
        normal_active = [t for t in normal if t.space_id == active_space]
        active_id = self.active_id if any(t.id == self.active_id for t in normal_active) else (
            normal_active[0].id if normal_active else None)
        saved_spaces = []
        for space in self.spaces:
            present = {t.id for t in normal if t.space_id == space.id}
            saved = space.snapshot()
            if saved["last_active_id"] not in present:
                saved["last_active_id"] = next(iter(present), None)
            saved_spaces.append(saved)
        return {
            "version": SCHEMA,
            "spaces": saved_spaces,
            "groups": [g.snapshot() for g in self.groups],
            "active_space_id": active_space,
            "tabs": [t.snapshot() for t in normal],
            "active_id": active_id,
            "history": self.history[:MAX_HISTORY],
            "bookmarks": self.bookmarks,
            "layout": self.layout if self.layout in ("side", "top") else "side",
            "theme": self.theme if self.theme in ("light", "dark", "system") else "system",
            "sidebar_hidden": self.sidebar_hidden,
        }

    @classmethod
    def from_json(cls, raw: dict) -> "BrowserState":
        if not isinstance(raw, dict) or raw.get("version") not in (1, 2, SCHEMA):
            return cls()
        tabs = []
        for entry in raw.get("tabs", [])[:100]:
            try:
                tabs.append(Tab.from_json(entry))
            except (ValueError, TypeError):
                continue
        spaces = []
        for entry in raw.get("spaces", [])[:MAX_SPACES]:
            try:
                spaces.append(Space.from_json(entry))
            except (ValueError, TypeError):
                continue
        if not spaces:
            spaces = [Space(id=DEFAULT_SPACE)]
        known = {s.id for s in spaces}
        for tab in tabs:
            if tab.space_id not in known:
                tab.space_id = spaces[0].id
        groups = []
        for entry in raw.get("groups", [])[:MAX_GROUPS]:
            try:
                group = TabGroup.from_json(entry)
                if group.space_id in known and group.id not in {g.id for g in groups}:
                    groups.append(group)
            except (ValueError, TypeError):
                continue
        known_groups = {g.id: g for g in groups}
        for tab in tabs:
            if tab.group_id and (tab.group_id not in known_groups or
                                 known_groups[tab.group_id].space_id != tab.space_id):
                tab.group_id = None
            if tab.group_id and tab.pinned:
                tab.pinned = False
        raw_history = raw.get("history", [])
        raw_bookmarks = raw.get("bookmarks", [])
        state = cls(
            tabs=tabs,
            spaces=spaces,
            groups=groups,
            active_space_id=raw.get("active_space_id") if raw.get("active_space_id") in known else spaces[0].id,
            active_id=raw.get("active_id"),
            history=[r for r in raw_history if isinstance(r, dict) and urlsplit(str(r.get("url", ""))).scheme in ("http", "https")][:MAX_HISTORY],
            bookmarks=[r for r in raw_bookmarks if isinstance(r, dict) and urlsplit(str(r.get("url", ""))).scheme in ("http", "https")][:10000],
            layout=raw.get("layout") if raw.get("layout") in ("side", "top") else "side",
            theme=raw.get("theme") if raw.get("theme") in ("light", "dark", "system") else "system",
            sidebar_hidden=bool(raw.get("sidebar_hidden", False)),
        )
        state.ensure_tab()
        return state


class StateStore:
    def __init__(self, directory: Path | None = None):
        self.directory = directory or data_dir()
        self.file = self.directory / "state.json"

    def load(self) -> BrowserState:
        try:
            return BrowserState.from_json(json.loads(self.file.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            s = BrowserState()
            s.ensure_tab()
            return s

    def save(self, state: BrowserState) -> None:
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, staging = tempfile.mkstemp(prefix="state-", suffix=".tmp", dir=self.directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(state.saved_dict(), handle, ensure_ascii=False, separators=(",", ":"))
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(staging, 0o600)
            os.replace(staging, self.file)
        finally:
            if os.path.exists(staging):
                os.unlink(staging)
