# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from textwrap import dedent
from unittest import TestCase

from moz_l10n import Comment, Entry, Resource, Section, ini_parse, ini_serialize

# Show full diff in self.assertEqual. https://stackoverflow.com/a/61345284
# __import__("sys").modules["unittest.util"]._MAX_LENGTH = 999999999


class TestIni(TestCase):
    def test_section_comment(self):
        res = ini_parse(
            dedent(
                """\
                ; This file is in the UTF-8 encoding
                [Strings]
                TitleText=Some Title
                """,
            )
        )
        self.assertEqual(
            res,
            Resource(
                [
                    Section(
                        id=["Strings"],
                        entries=[Entry(["TitleText"], "Some Title")],
                        comment="This file is in the UTF-8 encoding",
                    )
                ]
            ),
        )
        self.assertEqual(
            "".join(ini_serialize(res)),
            dedent(
                """\
                # This file is in the UTF-8 encoding
                [Strings]
                TitleText = Some Title
                """
            ),
        )
        self.assertEqual(
            "".join(ini_serialize(res, trim_comments=True)),
            "[Strings]\nTitleText = Some Title\n",
        )

    def test_resource_comment(self):
        res = ini_parse(
            dedent(
                """\
                ; This Source Code Form is subject to the terms of the Mozilla Public
                ; License, v. 2.0. If a copy of the MPL was not distributed with this file,
                ; You can obtain one at http://mozilla.org/MPL/2.0/.

                [Strings]
                TitleText=Some Title
                """
            )
        )
        self.assertEqual(
            res,
            Resource(
                [
                    Section(
                        id=["Strings"],
                        entries=[Entry(["TitleText"], "Some Title")],
                    )
                ],
                comment="This Source Code Form is subject to the terms of the Mozilla Public\n"
                "License, v. 2.0. If a copy of the MPL was not distributed with this file,\n"
                "You can obtain one at http://mozilla.org/MPL/2.0/.",
            ),
        )
        self.assertEqual(
            "".join(ini_serialize(res)),
            dedent(
                """\
                # This Source Code Form is subject to the terms of the Mozilla Public
                # License, v. 2.0. If a copy of the MPL was not distributed with this file,
                # You can obtain one at http://mozilla.org/MPL/2.0/.

                [Strings]
                TitleText = Some Title
                """
            ),
        )
        self.assertEqual(
            "".join(ini_serialize(res, trim_comments=True)),
            "[Strings]\nTitleText = Some Title\n",
        )

    def test_junk(self):
        with self.assertRaises(Exception):
            ini_parse(
                dedent(
                    """\
                    Junk
                    [Strings]
                    TitleText=Some Title
                    """
                )
            )

    def test_line_comment(self):
        res = ini_parse(
            dedent(
                """\
                [Strings] ; section comment
                ; entry pre comment
                TitleText=Some Title ; entry line comment
                    Continues
                """
            )
        )
        self.assertEqual(
            res,
            Resource(
                [
                    Section(
                        id=["Strings"],
                        entries=[
                            Entry(
                                ["TitleText"],
                                "Some Title\nContinues",
                                comment="entry pre comment\nentry line comment",
                            ),
                        ],
                        comment="section comment",
                    )
                ],
            ),
        )
        self.assertEqual(
            "".join(ini_serialize(res)),
            dedent(
                """\
                # section comment
                [Strings]
                # entry pre comment
                # entry line comment
                TitleText = Some Title
                  Continues
                """
            ),
        )
        self.assertEqual(
            "".join(ini_serialize(res, trim_comments=True)),
            "[Strings]\nTitleText = Some Title\n  Continues\n",
        )

    def test_trailing_comment(self):
        res = ini_parse(
            dedent(
                """\
                [Strings]
                TitleText=Some Title
                ;Stray trailing comment
                """
            )
        )
        self.assertEqual(
            res,
            Resource(
                [
                    Section(
                        id=["Strings"],
                        entries=[
                            Entry(["TitleText"], "Some Title"),
                            Comment("Stray trailing comment"),
                        ],
                    )
                ],
            ),
        )
        self.assertEqual(
            "".join(ini_serialize(res)),
            dedent(
                """\
                [Strings]
                TitleText = Some Title

                # Stray trailing comment

                """
            ),
        )
        self.assertEqual(
            "".join(ini_serialize(res, trim_comments=True)),
            "[Strings]\nTitleText = Some Title\n",
        )

    def test_empty_line_in_value(self):
        res = ini_parse(
            dedent(
                """\
                [Strings]
                TitleText=Some Title

                  Continues
                """
            )
        )
        self.assertEqual(
            res,
            Resource(
                [
                    Section(
                        id=["Strings"],
                        entries=[Entry(["TitleText"], "Some Title\n\nContinues")],
                    )
                ],
            ),
        )
        self.assertEqual(
            "".join(ini_serialize(res)),
            dedent(
                """\
                [Strings]
                TitleText = Some Title

                  Continues
                """
            ),
        )

    def test_empty_file(self):
        empty = Resource([])
        self.assertEqual(ini_parse(""), empty)
        self.assertEqual(ini_parse("\n"), empty)
        self.assertEqual(ini_parse("\n\n"), empty)
        self.assertEqual(ini_parse(" \n\n"), empty)
        self.assertEqual("".join(ini_serialize(empty)), "")
