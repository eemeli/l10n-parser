# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from textwrap import dedent
from unittest import TestCase

# Show full diff in self.assertEqual. https://stackoverflow.com/a/61345284
# __import__("sys").modules["unittest.util"]._MAX_LENGTH = 999999999


from moz_l10n import (
    CatchallKey,
    Comment,
    Entry,
    Expression,
    FunctionAnnotation,
    Metadata,
    PatternMessage,
    Resource,
    Section,
    SelectMessage,
    VariableRef,
    fluent_parse,
    fluent_serialize,
)


class TestPropertiesParser(TestCase):
    def test_equality_same(self):
        source = 'progress = Progress: { NUMBER($num, style: "percent") }.'
        res1 = fluent_parse(source)
        res2 = fluent_parse(source)
        self.assertEqual(res1, res2)

    def test_equality_different_whitespace(self):
        source1 = b"foo = { $arg }"
        source2 = b"foo = {    $arg    }"
        res1 = fluent_parse(source1)
        res2 = fluent_parse(source2)
        self.assertEqual(res1, res2)

    def test_resource(self):
        res = fluent_parse(
            dedent(
                """\
                ### Resource Comment

                ## Group Comment

                simple = A

                # Standalone Comment

                ##

                # Message Comment
                # on two lines.
                expressions = A {$arg} B {msg.foo} C {-term(x:42)}
                functions = {NUMBER($arg)}{FOO("bar",opt:"val")}
                has-attr = ABC
                  .attr = Attr
                # Attr Comment
                has-only-attr =
                  .attr = Attr

                single-sel =
                  { $num ->
                      [one] One
                     *[other] Other
                  }
                two-sels =
                  pre { $a ->
                      [1] One
                     *[2] Two
                  } mid { $b ->
                     *[bb] BB
                      [cc] CC
                  } post
                deep-sels =
                  { $a ->
                      [0]
                        { $b ->
                            [one] {""}
                           *[other] 0,x
                        }
                      [one]
                        { $b ->
                            [one] {"1,1"}
                           *[other] 1,x
                        }
                     *[other]
                        { $b ->
                            [0] x,0
                            [one] x,1
                           *[other] x,x
                        }
                  }
                """
            )
        )
        other = CatchallKey("other")
        entries = [
            Entry(
                ["expressions"],
                PatternMessage(
                    [
                        "A ",
                        Expression(VariableRef("arg")),
                        " B ",
                        Expression("msg.foo", FunctionAnnotation("message")),
                        " C ",
                        Expression("-term", FunctionAnnotation("message", {"x": "42"})),
                    ]
                ),
                comment="Message Comment\non two lines.",
            ),
            Entry(
                ["functions"],
                PatternMessage(
                    [
                        Expression(VariableRef("arg"), FunctionAnnotation("number")),
                        Expression("bar", FunctionAnnotation("foo", {"opt": "val"})),
                    ]
                ),
            ),
            Entry(["has-attr"], PatternMessage(["ABC"])),
            Entry(["has-attr", "attr"], PatternMessage(["Attr"])),
            Entry(
                ["has-only-attr", "attr"],
                PatternMessage(["Attr"]),
                comment="Attr Comment",
            ),
            Entry(
                ["single-sel"],
                SelectMessage(
                    [Expression(VariableRef("num"), FunctionAnnotation("number"))],
                    {
                        ("one",): ["One"],
                        (other,): ["Other"],
                    },
                ),
            ),
            Entry(
                ["two-sels"],
                SelectMessage(
                    [
                        Expression(VariableRef("a"), FunctionAnnotation("number")),
                        Expression(VariableRef("b"), FunctionAnnotation("string")),
                    ],
                    {
                        ("1", "cc"): ["pre One mid CC post"],
                        ("1", CatchallKey("bb")): ["pre One mid BB post"],
                        (CatchallKey("2"), "cc"): ["pre Two mid CC post"],
                        (CatchallKey("2"), CatchallKey("bb")): ["pre Two mid BB post"],
                    },
                ),
            ),
            Entry(
                ["deep-sels"],
                SelectMessage(
                    [
                        Expression(VariableRef("a"), FunctionAnnotation("number")),
                        Expression(VariableRef("b"), FunctionAnnotation("number")),
                    ],
                    {
                        ("0", "one"): [Expression("")],
                        ("0", other): ["0,x"],
                        ("one", "one"): [Expression("1,1")],
                        ("one", other): ["1,x"],
                        (other, "0"): ["x,0"],
                        (other, "one"): ["x,1"],
                        (other, other): ["x,x"],
                    },
                ),
            ),
        ]
        self.assertEqual(
            res,
            Resource(
                [
                    Section(
                        id=[],
                        entries=[
                            Entry(["simple"], PatternMessage(["A"])),
                            Comment("Standalone Comment"),
                        ],
                        comment="Group Comment",
                    ),
                    Section([], entries),
                ],
                comment="Resource Comment",
            ),
        )
        self.assertEqual(
            fluent_serialize(res),
            dedent(
                """\
                ### Resource Comment


                ## Group Comment

                simple = A

                # Standalone Comment


                ##

                # Message Comment
                # on two lines.
                expressions = A { $arg } B { msg.foo } C { -term(x: 42) }
                functions = { NUMBER($arg) }{ FOO("bar", opt: "val") }
                has-attr = ABC
                    .attr = Attr
                # Attr Comment
                has-only-attr =
                    .attr = Attr
                single-sel =
                    { NUMBER($num) ->
                        [one] One
                       *[other] Other
                    }
                two-sels =
                    { NUMBER($a) ->
                        [1]
                            { $b ->
                                [cc] pre One mid CC post
                               *[bb] pre One mid BB post
                            }
                       *[2]
                            { $b ->
                                [cc] pre Two mid CC post
                               *[bb] pre Two mid BB post
                            }
                    }
                deep-sels =
                    { NUMBER($a) ->
                        [0]
                            { NUMBER($b) ->
                                [one] { "" }
                               *[other] 0,x
                            }
                        [one]
                            { NUMBER($b) ->
                                [one] { "1,1" }
                               *[other] 1,x
                            }
                       *[other]
                            { NUMBER($b) ->
                                [0] x,0
                                [one] x,1
                               *[other] x,x
                            }
                    }
                """
            ),
        )

    def test_attr_comment(self):
        res = fluent_parse("msg = body\n  .attr = value")

        res.sections[0].entries[1].comment = "comment1"
        self.assertEqual(
            fluent_serialize(res),
            dedent(
                """\
                # attr:
                # comment1
                msg = body
                    .attr = value
                """
            ),
        )

        res.sections[0].entries[0].comment = "comment0"
        self.assertEqual(
            fluent_serialize(res),
            dedent(
                """\
                # comment0
                #
                # attr:
                # comment1
                msg = body
                    .attr = value
                """
            ),
        )

    def test_meta(self):
        res = fluent_parse("one = foo\ntwo = bar")
        res.sections[0].entries[1].meta = [Metadata("a", 42), Metadata("b", False)]
        try:
            fluent_serialize(res)
            raise Exception("Expected an error")
        except Exception as e:
            self.assertEqual(
                e.args, ("Metadata requires serialize_metadata parameter",)
            )
        self.assertEqual(
            fluent_serialize(res, lambda _: None), "one = foo\ntwo = bar\n"
        )
        self.assertEqual(
            fluent_serialize(res, lambda m: f"@{m.key}: {m.value}"),
            dedent(
                """\
                one = foo
                # @a: 42
                # @b: False
                two = bar
                """
            ),
        )

    def test_junk(self):
        try:
            fluent_parse("msg = value\n# Comment\nLine of junk")
            raise Exception("Expected an error")
        except Exception as e:
            self.assertEqual(e.args, ('Expected token: "="',))
