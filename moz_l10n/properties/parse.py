# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections.abc import Callable
from re import sub
from typing import cast, overload

from translate.storage.properties import propfile

from ..resource import Comment, Entry, Resource, Section, V


def parse_comment(lines: list[str]) -> str:
    return "\n".join(sub("^# ?", "", line) for line in lines if line.startswith("#"))


class propfile_shim(propfile):  # type: ignore[misc]
    def detect_encoding(
        self, text: bytes | str, default_encodings: list[str] | None = None
    ) -> tuple[str, str]:
        """
        Allow propfile().parse() to parse str inputs.
        """
        if isinstance(text, str):
            return (text, default_encodings[0] if default_encodings else "utf-8")
        else:
            return cast(
                tuple[str, str], super().detect_encoding(text, default_encodings)
            )


@overload
def properties_parse(
    source: bytes | str,
    encoding: str = "utf-8",
    parse_message: Callable[[str], str] | None = None,
) -> Resource[str, None]: ...


@overload
def properties_parse(
    source: bytes | str,
    encoding: str = "utf-8",
    parse_message: Callable[[str], V] | None = None,
) -> Resource[V, None]: ...


def properties_parse(
    source: bytes | str,
    encoding: str = "utf-8",
    parse_message: Callable[[str], V] | None = None,
) -> Resource[V, None]:
    """
    Parse a .properties file into a message resource
    """
    pf = propfile_shim(personality="java-utf8")
    if encoding != "utf-8":
        pf.default_encoding = encoding
    pf.parse(source)
    entries: list[Entry[V, None] | Comment] = []
    resource = Resource([Section([], entries)])
    for unit in pf.getunits():
        if unit.name or unit.value:
            entries.append(
                Entry(
                    id=[unit.name],
                    value=parse_message(unit.source) if parse_message else unit.source,
                    comment=parse_comment(unit.comments),
                )
            )
        else:
            comment = parse_comment(unit.comments)
            if comment:
                if entries or resource.comment:
                    entries.append(Comment(comment))
                else:
                    resource.comment = comment
    return resource
