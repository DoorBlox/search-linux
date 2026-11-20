"""Still: native GTK4 / WebKitGTK browser with Arc-like Spaces.

Native WebKit handles pages and networking; this module owns browser chrome.
Chrome extensions, secure password saving and true profile isolation are NOT
implemented by this milestone.
"""
from __future__ import annotations

from pathlib import Path
import os
import time

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gdk, Gio, GLib, Gtk, WebKit

from .core import (
    BrowserState, HOME, SPACE_COLORS, StateStore, Tab,
    cache_dir, data_dir, normalize_location, safe_display_url,
)


def clear_children(box):
    while (child := box.get_first_child()) is not None:
        box.remove(child)


def button(label, tooltip, callback, css="chrome-button"):
    item = Gtk.Button(label=label)
    item.add_css_class(css)
    item.set_tooltip_text(tooltip)
    item.connect("clicked", lambda *_: callback())
    return item


class StillWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title="Still")
        self.set_default_size(1180, 760)
        self.set_size_request(560, 390)
        self.store = StateStore()
        self.state = self.store.load()
        self.state.ensure_tab()
        self.views = {}
        self.private_sessions = {}
        self.closed = []
        self.save_timeout = None
        self.popover = None

        data = data_dir() / "webkit"
        cache = cache_dir() / "webkit"
        data.mkdir(parents=True, exist_ok=True, mode=0o700)
        cache.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.session = WebKit.NetworkSession.new(str(data), str(cache))
        self.session.connect("download-started", self.download_started)

        styles = Gtk.CssProvider()
        styles.load_from_path(str(Path(__file__).with_name("style.css")))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), styles, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self._build()
        self._install_shortcuts()
        self.apply_theme()
        self.show_tab(self.state.active_id)
        self.connect("close-request", self.close_window)

    def _build(self):
        header = Gtk.HeaderBar()
        header.add_css_class("chrome-header")
        header.set_show_title_buttons(True)
        self.set_titlebar(header)

        nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.back = button("‹", "Back", self.go_back)
        self.forward = button("›", "Forward", self.go_forward)
        self.reload = button("↻", "Reload", self.refresh)
        for widget in (self.back, self.forward, self.reload):
            nav.append(widget)
        header.pack_start(nav)

        self.address = Gtk.Entry()
        self.address.add_css_class("address")
        self.address.set_hexpand(True)
        self.address.set_placeholder_text("Search or enter an address")
        self.address.connect("activate", self.address_enter)
        header.set_title_widget(self.address)

        for mark, title, operation in (
            ("☆", "Bookmark this page", self.bookmark),
            ("◷", "History", lambda: self.library("history")),
            ("☰", "Bookmarks", lambda: self.library("bookmarks")),
        ):
            header.pack_end(button(mark, title, operation))

        self.root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.set_child(self.root)

        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        self.sidebar.add_css_class("sidebar")
        self.sidebar.set_size_request(226, -1)
        self.root.append(self.sidebar)

        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        top.add_css_class("sidebar-header")
        label = Gtk.Label(label="still")
        label.add_css_class("wordmark")
        top.append(label)
        filler = Gtk.Box()
        filler.set_hexpand(True)
        top.append(filler)
        top.append(button("+", "New tab (Ctrl+T)", self.new_tab, "small-button"))
        self.sidebar.append(top)

        self.space_title = button("Personal ▾", "Select or manage Spaces",
                                  lambda: self.space_menu(), "space-title")
        self.sidebar.append(self.space_title)

        self.pin_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.pin_row.set_margin_start(10)
        self.pin_row.set_margin_end(10)
        self.sidebar.append(self.pin_row)
        self.sidebar.append(Gtk.Separator())

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_vexpand(True)
        self.tab_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.tab_column.set_margin_start(8)
        self.tab_column.set_margin_end(8)
        scroller.set_child(self.tab_column)
        self.sidebar.append(scroller)

        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        footer.add_css_class("sidebar-footer")
        for text, title, callback in (
            ("+", "New tab", self.new_tab),
            ("◐", "Light or dark mode", self.toggle_theme),
            ("↔", "Switch vertical / top tabs", self.toggle_layout),
            ("▤", "Hide tabs", self.toggle_sidebar),
        ):
            footer.append(button(text, title, callback, "small-button"))
        self.sidebar.append(footer)

        self.space_dock = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.space_dock.add_css_class("space-dock")
        self.sidebar.append(self.space_dock)

        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content.set_hexpand(True)
        self.content.set_vexpand(True)
        self.root.append(self.content)

        self.top_scroller = Gtk.ScrolledWindow()
        self.top_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.top_scroller.add_css_class("top-tabs")
        self.top_tabs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.top_tabs.set_margin_start(8)
        self.top_tabs.set_margin_end(8)
        self.top_scroller.set_child(self.top_tabs)
        self.content.append(self.top_scroller)

        self.findbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.findbar.add_css_class("findbar")
        self.findbar.set_visible(False)
        self.find_entry = Gtk.SearchEntry()
        self.find_entry.set_hexpand(True)
        self.find_entry.connect("search-changed", self.find_text)
        self.findbar.append(self.find_entry)
        self.findbar.append(button("×", "Close find", self.hide_find))
        self.content.append(self.findbar)

        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.content.append(self.stack)

        self.status = Gtk.Label(label="")
        self.status.add_css_class("statusline")
        self.status.set_halign(Gtk.Align.START)
        self.content.append(self.status)

        for tab in self.state.tabs:
            self._placeholder(tab)
        self.refresh_ui()

    def _placeholder(self, tab):
        if self.stack.get_child_by_name(tab.id) is not None:
            return
        place = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        place.set_valign(Gtk.Align.CENTER)
        place.set_halign(Gtk.Align.CENTER)
        place.add_css_class("welcome")
        title = Gtk.Label(label="still")
        title.add_css_class("welcome-title")
        place.append(title)
        place.append(Gtk.Label(label="A quieter place for the web."))
        place.append(Gtk.Label(label="Ctrl+L   ·   Search or enter an address"))
        self.stack.add_named(place, tab.id)

    def ensure_view(self, tab):
        if tab.id in self.views:
            return self.views[tab.id]
        if tab.private:
            session = WebKit.NetworkSession.new_ephemeral()
            session.connect("download-started", self.download_started)
            self.private_sessions[tab.id] = session
        else:
            session = self.session
        view = WebKit.WebView(network_session=session)
        view.set_hexpand(True)
        view.set_vexpand(True)
        view.get_settings().set_enable_developer_extras(True)
        view.connect("notify::title", lambda web, _: self.web_title(tab.id, web))
        view.connect("notify::uri", lambda web, _: self.web_uri(tab.id, web))
        view.connect("load-changed", lambda web, event: self.web_load(tab.id, web, event))
        view.connect("web-process-terminated",
                     lambda web, reason: self.status.set_text("Page crashed. Press Ctrl+R to retry.")
                     if self.state.active_id == tab.id else None)
        view.connect("create", lambda web, navigation: self.popup(tab, navigation))
        old = self.stack.get_child_by_name(tab.id)
        if old is not None:
            self.stack.remove(old)
        self.views[tab.id] = view
        self.stack.add_named(view, tab.id)
        if tab.url != HOME:
            view.load_uri(tab.url)
        return view

    def show_tab(self, tab_id=None):
        tab = next((t for t in self.state.tabs if t.id == tab_id), None)
        if tab is None:
            self.state.ensure_tab()
            tab = self.state.active()
        if tab is None:
            return
        self.state.select_tab(tab.id)
        self._placeholder(tab)
        if tab.url != HOME:
            self.ensure_view(tab)
        self.stack.set_visible_child_name(tab.id)
        self.address.set_text("" if tab.url == HOME else safe_display_url(tab.url))
        self.refresh_ui()
        self.update_nav()
        self.queue_save()

    def refresh_ui(self):
        self.sidebar.set_visible(self.state.layout == "side" and not self.state.sidebar_hidden)
        self.top_scroller.set_visible(self.state.layout == "top" and not self.state.sidebar_hidden)
        clear_children(self.pin_row)
        clear_children(self.tab_column)
        clear_children(self.top_tabs)
        visible = self.state.tabs_in_space()
        ordered = [t for t in visible if t.pinned] + [t for t in visible if not t.pinned]
        for tab in ordered:
            active = tab.id == self.state.active_id
            if tab.pinned:
                pin = button((tab.title or "·")[:1].upper(), tab.title,
                             lambda tab_id=tab.id: self.show_tab(tab_id), "pin")
                if active:
                    pin.add_css_class("selected")
                self.pin_row.append(pin)
            else:
                self.tab_column.append(self.tab_button(tab, active))
            self.top_tabs.append(self.tab_button(tab, active, horizontal=True))
        self.top_tabs.append(button("+", "New tab", self.new_tab))
        current = self.state.current_space()
        self.space_title.set_label(f"{current.name} ▾")
        clear_children(self.space_dock)
        for index, space in enumerate(self.state.spaces):
            space_btn = button(space.name[:1].upper(), space.name,
                               lambda sid=space.id: self.switch_space(sid), "space-pill")
            space_btn.add_css_class(f"space-{space.color}")
            if space.id == current.id:
                space_btn.add_css_class("selected")
            space_btn.set_tooltip_text(f"{space.name} · Ctrl+Alt+{index + 1}")
            self.space_dock.append(space_btn)
        self.space_dock.append(button("+", "Create Space", self.new_space_dialog, "small-button"))

    def tab_button(self, tab, active=False, horizontal=False):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        row.add_css_class("tab-row")
        if active:
            row.add_css_class("selected")
        if horizontal:
            row.add_css_class("horizontal-tab")
        title = ("● " if tab.private else "") + (tab.title or "New Tab")
        choose = button(title, tab.url, lambda: self.show_tab(tab.id), "tab-title")
        choose.set_hexpand(True)
        row.append(choose)
        row.append(button("×", "Close tab", lambda: self.close_tab(tab.id), "tab-close"))

        gesture = Gtk.GestureClick()
        gesture.set_button(3)
        gesture.connect("pressed", lambda *args: self.tab_context(row, tab))
        row.add_controller(gesture)
        return row

    def tab_context(self, anchor, tab):
        pop = Gtk.Popover()
        pop.set_parent(anchor)
        pop.set_autohide(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(9)
        box.set_margin_bottom(9)
        box.append(button("Unpin" if tab.pinned else "Pin tab", "Keep as a compact tile",
                          lambda: (self.toggle_pin(tab.id), pop.popdown()), "menu-item"))
        if not tab.private:
            for space in self.state.spaces:
                if space.id != tab.space_id:
                    box.append(button(f"Move to {space.name}", "Move tab to another Space",
                                      lambda sid=space.id: (self.move_tab(tab.id, sid), pop.popdown()),
                                      "menu-item"))
        pop.set_child(box)
        pop.popup()

    def new_tab(self, url=HOME, private=False):
        tab = Tab(url=url, private=private, space_id=self.state.active_space_id)
        self.state.tabs.append(tab)
        self._placeholder(tab)
        self.show_tab(tab.id)
        if url == HOME:
            self.address.grab_focus()
        return tab

    def close_tab(self, tab_id):
        tab = next((t for t in self.state.tabs if t.id == tab_id), None)
        if not tab:
            return
        if tab.pinned:
            self.unload(tab.id)
            if self.state.active_id == tab.id:
                other = next((t for t in self.state.tabs_in_space() if t.id != tab.id), None)
                if other:
                    self.show_tab(other.id)
                else:
                    tab.url = HOME
                    self.show_tab(tab.id)
            return
        if not tab.private:
            self.closed.append((tab.url, tab.space_id))
            self.closed = self.closed[-30:]
        self.unload(tab_id)
        self.state.tabs.remove(tab)
        if self.state.active_id == tab_id:
            self.state.active_id = None
            self.state.ensure_tab()
            self.show_tab(self.state.active_id)
        else:
            self.refresh_ui()
        self.queue_save()

    def unload(self, tab_id):
        view = self.views.pop(tab_id, None)
        if view is not None:
            view.stop_loading()
            self.stack.remove(view)
        other = self.stack.get_child_by_name(tab_id)
        if other is not None:
            self.stack.remove(other)
        self.private_sessions.pop(tab_id, None)

    def reopen(self):
        if self.closed:
            url, space_id = self.closed.pop()
            if any(s.id == space_id for s in self.state.spaces):
                self.switch_space(space_id)
            self.new_tab(url)

    def switch_space(self, space_id):
        tab = self.state.switch_space(space_id)
        self.show_tab(tab.id)

    def move_tab(self, tab_id, space_id):
        try:
            self.state.move_tab(tab_id, space_id)
        except ValueError as error:
            self.status.set_text(str(error))
            return
        self.show_tab(self.state.active_id)
        self.queue_save()

    def toggle_pin(self, tab_id):
        tab = next((t for t in self.state.tabs if t.id == tab_id), None)
        if tab and not tab.private:
            tab.pinned = not tab.pinned
            self.refresh_ui()
            self.queue_save()

    def _prompt_name(self, target=None):
        dialog = Gtk.Dialog(title="Rename Space" if target else "Create Space",
                            transient_for=self, modal=True)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save" if target else "Create", Gtk.ResponseType.ACCEPT)
        dialog.set_default_response(Gtk.ResponseType.ACCEPT)
        content = dialog.get_content_area()
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        field = Gtk.Entry()
        field.set_placeholder_text("Space name")
        field.set_text(target.name if target else "")
        field.set_activates_default(True)
        content.append(field)

        def on_response(widget, response):
            if response == Gtk.ResponseType.ACCEPT:
                try:
                    if target:
                        self.state.rename_space(target.id, field.get_text())
                    else:
                        self.state.add_space(field.get_text())
                        self.show_tab(self.state.active_id)
                    self.refresh_ui()
                    self.queue_save()
                except ValueError as error:
                    self.status.set_text(str(error))
            widget.destroy()
        dialog.connect("response", on_response)
        dialog.present()
        field.grab_focus()

    def new_space_dialog(self):
        self._prompt_name()

    def space_menu(self):
        pop = Gtk.Popover()
        pop.set_parent(self.space_title)
        pop.set_autohide(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        for space in self.state.spaces:
            box.append(button(space.name, "Switch Space",
                              lambda sid=space.id: (pop.popdown(), self.switch_space(sid)),
                              "menu-item"))
        box.append(Gtk.Separator())
        box.append(button("Rename Space", "Rename selected Space",
                          lambda: (pop.popdown(), self._prompt_name(self.state.current_space())),
                          "menu-item"))
        box.append(button("+ New Space", "Add a Space",
                          lambda: (pop.popdown(), self.new_space_dialog()),
                          "menu-item"))
        pop.set_child(box)
        pop.popup()

    def address_enter(self, entry):
        try:
            self.navigate(normalize_location(entry.get_text()))
        except ValueError as error:
            self.status.set_text(str(error))

    def navigate(self, url):
        tab = self.state.active()
        if tab is None:
            tab = self.new_tab()
        tab.url = url
        if url == HOME:
            self.unload(tab.id)
            self._placeholder(tab)
        elif tab.id in self.views:
            self.views[tab.id].load_uri(url)
        else:
            self.ensure_view(tab)
        self.stack.set_visible_child_name(tab.id)
        self.address.set_text("" if url == HOME else safe_display_url(url))
        self.status.set_text("")
        self.queue_save()

    def current_view(self):
        return self.views.get(self.state.active_id)

    def go_back(self):
        view = self.current_view()
        if view and view.can_go_back():
            view.go_back()

    def go_forward(self):
        view = self.current_view()
        if view and view.can_go_forward():
            view.go_forward()

    def refresh(self):
        view = self.current_view()
        if view:
            view.reload()

    def update_nav(self):
        view = self.current_view()
        self.back.set_sensitive(bool(view and view.can_go_back()))
        self.forward.set_sensitive(bool(view and view.can_go_forward()))
        self.reload.set_sensitive(view is not None)

    def web_uri(self, tab_id, web):
        tab = next((t for t in self.state.tabs if t.id == tab_id), None)
        if tab:
            uri = web.get_uri() or HOME
            if uri != HOME:
                tab.url = uri
            if tab_id == self.state.active_id:
                self.address.set_text("" if uri == HOME else safe_display_url(uri))
                self.update_nav()
            self.queue_save()

    def web_title(self, tab_id, web):
        tab = next((t for t in self.state.tabs if t.id == tab_id), None)
        if tab:
            tab.title = (web.get_title() or web.get_uri() or "New Tab")[:180]
            self.refresh_ui()
            self.queue_save()

    def web_load(self, tab_id, web, event):
        tab = next((t for t in self.state.tabs if t.id == tab_id), None)
        if not tab:
            return
        if event == WebKit.LoadEvent.STARTED and tab_id == self.state.active_id:
            self.status.set_text("Loading…")
        elif event == WebKit.LoadEvent.COMMITTED:
            uri = web.get_uri() or HOME
            tab.url = uri
            self.state.record_visit(uri, web.get_title() or tab.title, private=tab.private)
            self.queue_save()
        elif event == WebKit.LoadEvent.FINISHED and tab_id == self.state.active_id:
            self.status.set_text("")
            self.update_nav()

    def popup(self, parent_tab, navigation):
        try:
            gesture = navigation.is_user_gesture()
        except (AttributeError, TypeError):
            gesture = False
        if not gesture:
            self.status.set_text("Blocked unsolicited pop-up")
            return None
        tab = self.new_tab(private=parent_tab.private)
        return self.ensure_view(tab)

    def download_started(self, session, download):
        folder = Path.home() / "Downloads"
        folder.mkdir(parents=True, exist_ok=True)
        def destination(d, filename):
            name = Path(str(filename or "download")).name
            if name in ("", ".", ".."):
                name = "download"
            output = folder / name
            count = 1
            while output.exists():
                output = folder / f"{output.stem}-{count}{output.suffix}"
                count += 1
            d.set_destination(Gio.File.new_for_path(str(output)).get_uri())
            return True
        download.connect("decide-destination", destination)
        download.connect("finished", lambda *_: self.status.set_text("Download complete"))
        download.connect("failed", lambda *_: self.status.set_text("Download failed"))

    def bookmark(self):
        tab = self.state.active()
        if tab and tab.url != HOME and not tab.private:
            active = self.state.toggle_bookmark(tab.url, tab.title)
            self.status.set_text("Bookmarked" if active else "Bookmark removed")
            self.queue_save()

    def library(self, kind):
        if self.popover is not None:
            self.popover.popdown()
            self.popover.unparent()
        pop = Gtk.Popover()
        pop.set_parent(self.address)
        pop.set_autohide(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_size_request(330, 320)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.append(Gtk.Label(label=kind.title()))
        field = Gtk.SearchEntry()
        box.append(field)
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        items = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        scroll.set_child(items)
        box.append(scroll)
        if kind == "bookmarks":
            records = list(reversed(self.state.bookmarks))
        elif kind == "history":
            records = self.state.history
        else:
            records = [{"title": t.title, "url": t.url, "id": t.id}
                       for t in self.state.tabs_in_space()]
        def draw(term=""):
            clear_children(items)
            for item in records:
                name = str(item.get("title", "")) or str(item.get("url", ""))
                if term.casefold() not in (name + " " + str(item.get("url", ""))).casefold():
                    continue
                url = item.get("url", "")
                action = (lambda ident=item.get("id"): self.show_tab(ident)) if kind == "tabs" else (
                    lambda link=url: self.navigate(link))
                items.append(button(name, url, lambda f=action: (pop.popdown(), f()), "menu-item"))
        field.connect("search-changed", lambda widget: draw(widget.get_text()))
        draw()
        pop.set_child(box)
        self.popover = pop
        pop.popup()

    def find_page(self):
        self.findbar.set_visible(True)
        self.find_entry.grab_focus()

    def find_text(self, entry):
        view = self.current_view()
        if view is not None:
            search = view.get_find_controller()
            query = entry.get_text().strip()
            if query:
                search.search(query, WebKit.FindOptions.CASE_INSENSITIVE, 100)
            else:
                search.search_finish()

    def hide_find(self):
        self.findbar.set_visible(False)
        view = self.current_view()
        if view:
            view.get_find_controller().search_finish()

    def zoom(self, amount):
        view = self.current_view()
        if view:
            view.set_zoom_level(1.0 if amount == 0 else
                                max(0.5, min(3.0, view.get_zoom_level() + amount)))

    def toggle_theme(self):
        self.state.theme = "dark" if self.state.theme != "dark" else "light"
        self.apply_theme()
        self.queue_save()

    def apply_theme(self):
        dark = self.state.theme == "dark"
        self.remove_css_class("dark-mode")
        if dark:
            self.add_css_class("dark-mode")
        if self.state.theme != "system":
            Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", dark)

    def toggle_sidebar(self):
        self.state.sidebar_hidden = not self.state.sidebar_hidden
        self.refresh_ui()
        self.queue_save()

    def toggle_layout(self):
        self.state.layout = "top" if self.state.layout == "side" else "side"
        self.state.sidebar_hidden = False
        self.refresh_ui()
        self.queue_save()

    def select_tab_relative(self, delta):
        visible = self.state.tabs_in_space()
        if not visible:
            return
        index = next((i for i, t in enumerate(visible) if t.id == self.state.active_id), 0)
        self.show_tab(visible[(index + delta) % len(visible)].id)

    def select_tab_number(self, position):
        visible = self.state.tabs_in_space()
        if visible:
            self.show_tab(visible[min(position, len(visible) - 1)].id)

    def queue_save(self):
        if self.save_timeout is not None:
            GLib.source_remove(self.save_timeout)
        self.save_timeout = GLib.timeout_add(500, self.save)

    def save(self):
        self.save_timeout = None
        try:
            self.store.save(self.state)
        except OSError as error:
            self.status.set_text(f"Session not saved: {error}")
        return GLib.SOURCE_REMOVE

    def close_window(self, window):
        if self.save_timeout is not None:
            GLib.source_remove(self.save_timeout)
            self.save_timeout = None
        self.save()
        return False

    def _install_shortcuts(self):
        actions = {
            "new-tab": (["<Primary>t"], self.new_tab),
            "new-private": (["<Primary><Shift>n"], lambda: self.new_tab(private=True)),
            "close-tab": (["<Primary>w"], lambda: self.close_tab(self.state.active_id)),
            "reopen-tab": (["<Primary><Shift>t"], self.reopen),
            "address": (["<Primary>l"], lambda: (self.address.grab_focus(), self.address.select_region(0, -1))),
            "tab-switcher": (["<Primary>k"], lambda: self.library("tabs")),
            "find": (["<Primary>f"], self.find_page),
            "reload": (["<Primary>r"], self.refresh),
            "back": (["<Alt>Left"], self.go_back),
            "forward": (["<Alt>Right"], self.go_forward),
            "bookmark": (["<Primary><Shift>b"], self.bookmark),
            "history": (["<Primary>y"], lambda: self.library("history")),
            "zoom-in": (["<Primary>plus", "<Primary>equal"], lambda: self.zoom(0.1)),
            "zoom-out": (["<Primary>minus"], lambda: self.zoom(-0.1)),
            "zoom-reset": (["<Primary>0"], lambda: self.zoom(0)),
            "next-tab": (["<Control>Tab"], lambda: self.select_tab_relative(1)),
            "prev-tab": (["<Control><Shift>Tab"], lambda: self.select_tab_relative(-1)),
            "tabs-top-side": (["<Primary><Shift>s"], self.toggle_layout),
            "fold-sidebar": (["<Primary>s"], self.toggle_sidebar),
        }
        for i in range(1, 10):
            actions[f"tab-{i}"] = ([f"<Primary>{i}"],
                                   lambda index=i - 1: self.select_tab_number(index))
            actions[f"space-{i}"] = ([f"<Control><Alt>{i}"],
                                     lambda index=i - 1: self.switch_space(self.state.spaces[index].id)
                                     if index < len(self.state.spaces) else None)
        app = self.get_application()
        for name, (accels, func) in actions.items():
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", lambda _, param, callback=func: callback())
            self.add_action(action)
            app.set_accels_for_action(f"win.{name}", accels)


class StillApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.stillbrowser.Still")
        self.window = None
        self.started = time.monotonic()

    def do_activate(self):
        if self.window is None:
            self.window = StillWindow(self)
            self.window.connect("close-request", lambda *_: setattr(self, "window", None))
        self.window.present()
        print(f"[still] window requested in {time.monotonic() - self.started:.2f}s", flush=True)


def main(argv):
    return StillApplication().run(argv)
