"""Copyright 2022 by @doldam0. All rights reserved."""

import unittest

from typing import List, Optional

from clsarg import ArgumentParser, argument


class Argument(ArgumentParser):
    """Test argument class for argparser"""

    @property
    @argument
    def foo(self, value: str) -> str:
        ...

    @property
    @argument(name="name")
    def property_name(self, value: str = "") -> str:
        ...

    @property
    @argument(aliases="b")
    def bar(self, value: int = 0):
        return value + 1

    @property
    @argument(aliases=["z", "az"])
    def baz(self, value: Optional[str]):
        if value is None:
            return []
        return value.split("/")

    @property
    @argument(const=True)
    def const(self):
        return 40

    @property
    @argument(nargs=3, metavar="N")
    def nargs(self, value: List[int]):
        ...

    @property
    @argument
    def boolean(self, value: bool):
        ...

    @property
    @argument
    def optional(self, value: int = 3) -> int:
        if not self.baz:
            return -1
        return value


class AdditionalArgument(Argument):
    ...


class TestArgparser(unittest.TestCase):
    """Testcase for argparser"""

    def setUp(self) -> None:
        self.args = AdditionalArgument(lazy_parsing=True)

    def __foo(self, s: str = ""):
        return "--foo foo --nargs 1 2 3 " + s

    def test_basic_args(self):
        self.args.parse_args(self.__foo("--bar 3 --baz foo/bar"))
        self.assertEqual(self.args.foo, "foo")
        self.assertEqual(self.args.bar, 4)
        self.assertEqual(self.args.baz, ["foo", "bar"])

    def test_custom_name(self):
        self.args.parse_args(self.__foo("--name name"))
        self.assertEqual(self.args.property_name, "name")

    def test_aliases(self):
        self.args.parse_args(self.__foo("-b 7 -z bar/baz"))
        self.assertEqual(self.args.bar, 8)
        self.assertEqual(self.args.baz, ["bar", "baz"])

        self.args.parse_args(self.__foo("--az bar"))
        self.assertEqual(self.args.baz, ["bar"])

    def test_const(self):
        self.args.parse_args(self.__foo("--const"))
        self.assertEqual(self.args.const, 40)

    def test_const_none(self):
        self.args.parse_args(self.__foo())
        self.assertIsNone(self.args.const)

    def test_optional_args(self):
        self.args.parse_args(self.__foo())
        self.assertEqual(self.args.bar, 1)
        self.assertEqual(self.args.baz, [])

    def test_exception(self):
        with self.assertRaises(SystemExit):
            self.args.parse_args("")

    def test_additional_args(self):
        self.args.parse_args(self.__foo())
        self.assertEqual(self.args.bar, 1)
        self.assertEqual(self.args.baz, [])
        self.assertEqual(self.args.optional, -1)

        self.args.parse_args(self.__foo("--baz foo/bar"))
        self.assertEqual(self.args.baz, ["foo", "bar"])
        self.assertEqual(self.args.optional, 3)
