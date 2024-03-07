# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class VariableRef:
    name: str


@dataclass
class FunctionAnnotation:
    name: str
    options: dict[str, str | VariableRef] = field(default_factory=dict)


@dataclass
class UnsupportedAnnotation:
    source: str
    """
    The "raw" value (i.e. escape sequences are not processed).
    """


@dataclass
class Expression:
    """
    A valid Expression must contain a non-None `arg`, `annotation`, or both.
    """

    arg: str | VariableRef | None
    annotation: FunctionAnnotation | UnsupportedAnnotation | None = None
    attributes: dict[str, str | VariableRef | None] = field(default_factory=dict)


@dataclass
class Markup:
    kind: Literal["open", "standalone", "close"]
    name: str
    options: dict[str, str | VariableRef] = field(default_factory=dict)
    attributes: dict[str, str | VariableRef | None] = field(default_factory=dict)


Pattern = list[str | Expression | Markup]
"""
A linear sequence of text and placeholders corresponding to potential output of a message.

String values represent literal text.
String values include all processing of the underlying text values, including escape sequence processing.
"""


@dataclass
class CatchallKey:
    value: str | None = field(default=None, compare=False)
    """
    An optional string identifier for the default/catch-all variant.
    """

    def __hash__(self) -> int:
        """
        Consider all catchall-keys as equivalent to each other
        """
        return 1


@dataclass
class Declaration:
    name: str
    value: Expression


@dataclass
class UnsupportedStatement:
    keyword: str
    """
    A non-empty string name.
    """

    body: str | None
    """
    If not empty, the "raw" value (i.e. escape sequences are not processed)
    starting after the keyword and up to the first expression,
    not including leading or trailing whitespace.
    """

    expressions: list[Expression]


@dataclass
class PatternMessage:
    """
    A message without selectors and with a single pattern.
    """

    pattern: Pattern
    declarations: list[Declaration | UnsupportedStatement] = field(default_factory=list)


Variants = dict[tuple[str | CatchallKey, ...], Pattern]


@dataclass
class SelectMessage:
    """
    A message with one or more selectors and a corresponding number of variants.
    """

    selectors: list[Expression]
    variants: Variants
    declarations: list[Declaration | UnsupportedStatement] = field(default_factory=list)


Message = PatternMessage | SelectMessage
