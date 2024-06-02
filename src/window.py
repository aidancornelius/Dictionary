# window.py
#
# Copyright 2024 Aidan Cornelius-Bell
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk, Pango, Gdk, GLib
import threading
from PyMultiDictionary import MultiDictionary, DICT_WORDNET

@Gtk.Template(resource_path='/net/aidancornelius/Dictionary/window.ui')
class DictionaryWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'DictionaryWindow'

    search_entry = Gtk.Template.Child()
    result_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_entry.connect('activate', self.on_search_activate)
        self.result_view.set_buffer(Gtk.TextBuffer())  # Directly set buffer
        self.setup_tags()
        self.search_entry.grab_focus()  # Set focus to the search entry
        self.set_icon_name("net.aidancornelius.Dictionary")


    def setup_tags(self):
        buffer = self.result_view.get_buffer()
        self.bold_tag = buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.blue_underline_tag = buffer.create_tag("blue_underline", foreground="blue", underline=Pango.Underline.SINGLE)

    def on_search_activate(self, widget):
        search_term = widget.get_text()
        self.show_loading_message()  # Show loading message
        threading.Thread(target=self.perform_search, args=(search_term,)).start()

    def perform_search(self, search_term):
        dictionary = MultiDictionary()
        try:
            definitions = dictionary.meaning('en', search_term, dictionary=DICT_WORDNET)
            synonyms = dictionary.synonym('en', search_term)  # Fetch synonyms
            antonyms = dictionary.antonym('en', search_term)  # Fetch antonyms
        except Exception as e:
            definitions = f"Error fetching definitions: {e}"
            synonyms = f"Error fetching synonyms: {e}"
            antonyms = f"Error fetching antonyms: {e}"

        GLib.idle_add(self.update_ui, search_term, definitions, synonyms, antonyms)

    def show_loading_message(self):
        buffer = self.result_view.get_buffer()
        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
        buffer.insert(buffer.get_end_iter(), "Loading...")

    def update_ui(self, search_term, definitions, synonyms, antonyms):
        buffer = self.result_view.get_buffer()
        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())

        # Insert definitions
        buffer.insert(buffer.get_end_iter(), f"Definitions for '{search_term}':\n")
        start_iter = buffer.get_iter_at_offset(buffer.get_char_count() - len(search_term) - 19)
        end_iter = buffer.get_end_iter()
        buffer.apply_tag(self.bold_tag, start_iter, end_iter)

        if isinstance(definitions, dict):
            for pos, defs in definitions.items():
                buffer.insert(buffer.get_end_iter(), f"{pos}:\n")
                start_iter = buffer.get_iter_at_offset(buffer.get_char_count() - len(pos) - 2)
                end_iter = buffer.get_end_iter()
                buffer.apply_tag(self.bold_tag, start_iter, end_iter)
                for definition in defs:
                    buffer.insert(buffer.get_end_iter(), f"• {definition}\n")
        else:
            buffer.insert(buffer.get_end_iter(), "No definitions found.\n")

        # Insert synonyms
        buffer.insert(buffer.get_end_iter(), f"\nSynonyms for '{search_term}':\n")
        start_iter = buffer.get_iter_at_offset(buffer.get_char_count() - len(search_term) - 14)
        end_iter = buffer.get_end_iter()
        buffer.apply_tag(self.bold_tag, start_iter, end_iter)

        if isinstance(synonyms, list):
            for synonym in synonyms:
                buffer.insert(buffer.get_end_iter(), f"• {synonym}\n")
        else:
            buffer.insert(buffer.get_end_iter(), "No synonyms found.\n")

        # Insert antonyms
        buffer.insert(buffer.get_end_iter(), f"\nAntonyms for '{search_term}':\n")
        start_iter = buffer.get_iter_at_offset(buffer.get_char_count() - len(search_term) - 14)
        end_iter = buffer.get_end_iter()
        buffer.apply_tag(self.bold_tag, start_iter, end_iter)

        if isinstance(antonyms, list):
            for antonym in antonyms:
                buffer.insert(buffer.get_end_iter(), f"• {antonym}\n")
        else:
            buffer.insert(buffer.get_end_iter(), "No antonyms found.\n")

    def on_tag_event(self, tag, widget, event, iter):
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 1:
            buffer = self.result_view.get_buffer()
            start_iter, end_iter = iter.copy(), iter.copy()
            start_iter.backward_to_tag_toggle(tag)
            end_iter.forward_to_tag_toggle(tag)
            synonym = buffer.get_text(start_iter, end_iter, False)
            self.search_entry.set_text(synonym)
            self.on_search_activate(self.search_entry)

