# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from unittest import TestCase

from moz_l10n import Entry, Resource, Section, add_entries


class TestAddEntries(TestCase):
    def test_no_changes(self):
        target = Resource([Section([], [Entry(["foo"], "Foo 1")])])
        source = Resource([Section([], [Entry(["foo"], "Foo 2")])])
        self.assertEqual(add_entries(target, source), 0)
        self.assertEqual(target, Resource([Section([], [Entry(["foo"], "Foo 1")])]))

    def test_message_not_in_source(self):
        target = Resource(
            [Section([], [Entry(["foo"], "Foo 1"), Entry(["bar"], "Bar 1")])]
        )
        source = Resource([Section([], [Entry(["foo"], "Foo 2")])])
        self.assertEqual(add_entries(target, source), 0)
        self.assertEqual(
            target,
            Resource([Section([], [Entry(["foo"], "Foo 1"), Entry(["bar"], "Bar 1")])]),
        )

    def test_message_added_in_source(self):
        target = Resource([Section([], [Entry(["foo"], "Foo 1")])])
        source = Resource(
            [Section([], [Entry(["foo"], "Foo 2"), Entry(["bar"], "Bar 2")])]
        )
        self.assertEqual(add_entries(target, source), 1)
        self.assertEqual(
            target,
            Resource([Section([], [Entry(["foo"], "Foo 1"), Entry(["bar"], "Bar 2")])]),
        )

    def test_messages_reordered(self):
        target = Resource(
            [Section([], [Entry(["foo"], "Foo 1"), Entry(["bar"], "Bar 1")])]
        )
        source = Resource(
            [Section([], [Entry(["bar"], "Bar 2"), Entry(["foo"], "Foo 2")])]
        )
        self.assertEqual(add_entries(target, source), 0)
        self.assertEqual(
            target,
            Resource([Section([], [Entry(["foo"], "Foo 1"), Entry(["bar"], "Bar 1")])]),
        )

    def test_message_addition_order(self):
        target = Resource(
            [Section([], [Entry(["foo"], "Foo 1"), Entry(["bar"], "Bar 1")])]
        )
        source_entries = [
            Entry(["bar"], "Bar 2"),
            Entry(["x"], "X"),
            Entry(["foo"], "Foo 2"),
            Entry(["y"], "Y"),
        ]
        source = Resource([Section([], source_entries)])
        self.assertEqual(add_entries(target, source), 2)
        exp_entries = [
            Entry(["foo"], "Foo 1"),
            Entry(["y"], "Y"),
            Entry(["bar"], "Bar 1"),
            Entry(["x"], "X"),
        ]
        self.assertEqual(target, Resource([Section([], exp_entries)]))

    def test_added_sections(self):
        target = Resource(
            [Section(["1"], [Entry(["foo"], "Foo 1"), Entry(["bar"], "Bar 1")])]
        )
        source = Resource(
            [
                Section(["0"], [Entry(["x"], "X")]),
                Section(["1"], [Entry(["foo"], "Foo 2"), Entry(["bar"], "Bar 2")]),
                Section(["2"], [Entry(["x"], "Y")]),
            ]
        )
        self.assertEqual(add_entries(target, source), 2)
        self.assertEqual(
            target,
            Resource(
                [
                    Section(["0"], [Entry(["x"], "X")]),
                    Section(["1"], [Entry(["foo"], "Foo 1"), Entry(["bar"], "Bar 1")]),
                    Section(["2"], [Entry(["x"], "Y")]),
                ]
            ),
        )

    def test_anon_sections(self):
        target = Resource(
            [
                Section([], [Entry(["foo"], "Foo 1")], "C1"),
                Section([], [Entry(["bar"], "Bar 1")], "C2"),
            ]
        )
        source = Resource(
            [
                Section([], [Entry(["x"], "X")], "C0"),
                Section([], [Entry(["y"], "Y")], "C2"),
                Section([], [Entry(["z"], "Z")], "C1"),
            ]
        )
        self.assertEqual(add_entries(target, source), 3)
        self.assertEqual(
            target,
            Resource(
                [
                    Section([], [Entry(["x"], "X")], "C0"),
                    Section([], [Entry(["foo"], "Foo 1"), Entry(["z"], "Z")], "C1"),
                    Section([], [Entry(["bar"], "Bar 1"), Entry(["y"], "Y")], "C2"),
                ]
            ),
        )
