"""Copyright 2022 by @doldam0. All rights reserved."""

from __future__ import annotations

import argparse
from inspect import Parameter, signature
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)


class ArgumentParser:
    r"""`ArgumentParser` for some projects. Based from `argparse`.

    Usage:
        You can easily parse arguments by making a class inheriting::

            class MainArgument(ArgumentParser):
                ...

        Each arguments can be defined with a `@argument`. For example, if you
        define the property whose name is `num_class`, like below::

            class MainArgument(ArgumentParser):
                @argument
                def num_class(self, value: int) -> int:
                    return value

        then the argument `num_class` will be defined. That’s it!

        You can add some options such as alias, default value, required option,
        etc.::

            class MainArgument(ArgumentParser):
                @argument(
                    aliases='n',
                    default=1,
                    required=True
                )
                def num_class(self, value: int) -> int:
                    return value

        You can check all options at the description of `@argument` decorator.

        A docstring is same with description(help) of argument::

            class MainArgument(ArgumentParser):
                @argument(
                    aliases='n',
                    default=1,
                    required=True
                )
                def num_class(self, value: int) -> int:
                    '''The number of the classes.'''
                    return value

        And if you want to set this argument as parameter, just add `@property`
        decorator::

            class MainArgument(ArgumentParser):
                @property
                @argument(
                    aliases='n',
                    default=1,
                    required=True
                )
                def num_class(self, value: int) -> int:
                    '''The number of the classes.'''
                    return value

        **NOTE**: You should assign `property` before `argument`.

        If you handle the argument `value`, just modify the function body and
        return the handled value::

            class MainArgument(ArgumentParser):
                @property
                @argument(
                    aliases='n',
                    default=1,
                    required=True
                )
                def num_class(self, value: int) -> list[int]:
                    '''The number of the classes.'''
                    if value <= 0:
                        raise ValueError("The value must be positive integer")
                    return value + 1

        If you done writing down the argument class, just make an object of
        parser. Then parsing will be done::

            args = MainArgument()
            do_something(args.num_class)
    """
    __object__ = None

    def __new__(cls: Type[ArgumentParser], *args, **kwds):
        """Overrided function.

        Args:
            cls (Type[ArgumentParser]): Class object type of `ArgumentParser`
                to initialize.

        Returns:
            ArgumentParser: New initialized object.
        """
        if cls.__object__ is None:
            cls.__object__ = object.__new__(cls)
        return cls.__object__

    def __init__(
        self,
        prog: Optional[str] = None,
        usage: Optional[str] = None,
        description: Optional[str] = None,
        epilog: Optional[str] = None,
        lazy_parsing: bool = False,
    ):
        r"""Initializer of `ArgumentParser`.

        Usage:
            You can easily parse arguments by making a class inheriting::

                class MainArgument(ArgumentParser):
                    ...

            Each arguments can be defined with a `@argument`. For example, if
            you define the property whose name is `num_class`, like below::

                class MainArgument(ArgumentParser):
                    @argument
                    def num_class(self, value: int) -> int:
                        return value

            then the argument `num_class` will be defined. That’s it!

            You can add some options such as alias, default value, required
            option, etc.::

                class MainArgument(ArgumentParser):
                    @argument(
                        aliases='n',
                        required=True
                    )
                    def num_class(self, value: int = 1) -> int:
                        return value

            You can check all options at the description of `@argument`
            decorator.

            A docstring is same with description(help) of argument::

                class MainArgument(ArgumentParser):
                    @argument(
                        aliases='n',
                        required=True
                    )
                    def num_class(self, value: int = 1) -> int:
                        '''The number of the classes.'''
                        return value

            And if you want to set this argument as read-only, just add
            `@property` decorator::

                class MainArgument(ArgumentParser):
                    @property
                    @argument(
                        aliases='n',
                        required=True
                    )
                    def num_class(self, value: int = 1) -> int:
                        '''The number of the classes.'''
                        return value

            **NOTE**: You should assign `property` before `argument`.

            If you handle the argument `value`, just modify the function body
            and return the handled value::

                class MainArgument(ArgumentParser):
                    @property
                    @argument(
                        aliases='n',
                        default=1,
                        required=True
                    )
                    def num_class(self, value: int) -> list[int]:
                        '''The number of the classes.'''
                        if value <= 0:
                            raise ValueError("The value must be positive "
                                             "integer")
                        return value + 1

            If you done writing down the argument class, just make an object of
            parser. Then parsing will be done::

            >>> args = MainArgument()
            >>> do_something(args.num_class)
        """
        kwds: Dict[str, str] = {}
        if prog is not None:
            kwds["prog"] = prog
        if usage is not None:
            kwds["usage"] = usage
        if description is not None:
            kwds["description"] = description
        if epilog is not None:
            kwds["epilog"] = epilog

        parser = argparse.ArgumentParser(**kwds)
        arguments: List[Tuple[int, Tuple[str, List[Any], Dict[str, Any]]]] = []
        for name in dir(self.__class__):
            item = getattr(self.__class__, name)
            if isinstance(item, property) and hasattr(
                item.fget, "__argument_info"
            ):
                info = getattr(item.fget, "__argument_info")
                getter_name = info["getter_name"]
                name = info["name"]
                number = info["number"]
                args = info["args"]
                kwds = info["kwds"]

                if item.fget is not None:
                    argument_name = getter_name
                    if name is not None:
                        kwds["dest"] = argument_name
                        argument_name = name
                    argument_name = argument_name.replace("_", "-")
                    arguments.append((number, (argument_name, args, kwds)))

        arguments = sorted(arguments, key=lambda x: x[0])
        for argument_name, args, kwds in [elem[1] for elem in arguments]:
            parser.add_argument(f"--{argument_name}", *args, **kwds)

        if not lazy_parsing:
            self.__arguments = parser.parse_args()

        self.__parser = parser

    @property
    def arguments(self):
        """The object contains all arguments whose type is `Namespace`."""
        return self.__arguments

    def parse_args(self, parameter: str):
        """Parse arguments from `parameter` directly.

        Args:
            parameter (str): A parameter to parse.
        """
        self.__arguments = self.__parser.parse_args(parameter.split())


P = TypeVar("P", int, float, str, bool)
R = TypeVar("R")


class _GenerateArgumentGetter:
    """Hidden class for argument getter"""

    def __init__(self):
        self.__num_arguments = 0

    def __call__(
        self,
        getter: Callable,
        /,
        *__args: str,
        name: Optional[str] = None,
        **__kwds: Any,
    ) -> Callable:
        argument_name = getter.__name__

        __kwds["required"] = True

        if getter.__doc__ is not None:
            __kwds["help"] = getter.__doc__

        argument_type = get_type_hints(getter).get("value")
        wrapper = None

        if __kwds.get("const", False):

            def const_wrapper(self: ArgumentParser):
                value = getattr(self.arguments, argument_name)
                if value is None:
                    return None
                return getter(self)

            wrapper = const_wrapper
            __kwds["required"] = False
            __kwds["action"] = "store_const"
        elif argument_type is None:
            raise ValueError(
                "An argument function should have value parameter."
            )

        origin_type = get_origin(argument_type)
        type_args = get_args(argument_type)

        if argument_type == bool:
            __kwds["required"] = False
            __kwds["action"] = "store_true"
            argument_type = None
        elif origin_type == list:
            if len(type_args) > 1:
                raise TypeError(
                    "You should set the return type of argument "
                    "function to list that contains only one "
                    "type."
                )
            __kwds["nargs"] = __kwds.get("nargs", "*")
            argument_type = type_args[0]
        elif origin_type == Union:
            if len(type_args) != 2 or not isinstance(None, type_args[1]):
                raise TypeError("Union type is not allowed.")
            __kwds["required"] = False
            argument_type = type_args[0]

        if argument_type is not None:
            sig = signature(getter).parameters["value"]
            if sig.default != Parameter.empty:
                __kwds["required"] = False
                __kwds["default"] = sig.default
            __kwds["type"] = argument_type

        if wrapper is None:

            def _wrapper(self: ArgumentParser):
                value = getattr(self.arguments, argument_name)
                return getter(self, value)

            wrapper = _wrapper

        setattr(
            wrapper,
            "__argument_info",
            {
                "getter_name": getter.__name__,
                "name": name,
                "number": self.__num_arguments,
                "args": __args,
                "kwds": __kwds,
            },
        )
        self.__num_arguments += 1
        return wrapper


__generate_argument_getter = _GenerateArgumentGetter()


@overload
def argument(
    name: Optional[str] = None,
    aliases: Optional[Union[str, Iterable[str]]] = None,
    metavar: Optional[str] = None,
    choices: Optional[Iterable[P]] = None,
    const: Literal[False] = False,
) -> Callable[
    [
        Union[
            Callable[[Any, P], R],
            Callable[[Any, Optional[P]], R],
            Callable[[Any, List[P]], R],
        ]
    ],
    Callable[[Any], R],
]:
    ...


@overload
def argument(
    name: Optional[str] = None,
    aliases: Optional[Union[str, Iterable[str]]] = None,
    metavar: Optional[str] = None,
    choices: Optional[Iterable[P]] = None,
    const: Literal[True] = True,
) -> Callable[[Callable[[Any], R]], Callable[[Any], Optional[R]]]:
    ...


@overload
def argument(
    name: Optional[str] = None,
    aliases: Optional[Union[str, Iterable[str]]] = None,
    metavar: Optional[str] = None,
    choices: Optional[Iterable[P]] = None,
    const: Literal[False] = False,
    nargs: Optional[Union[int, Literal["*"], Literal["+"]]] = "*",
) -> Callable[[Callable[[Any, List[P]], R]], Callable[[Any], R]]:
    ...


@overload
def argument(
    getter: Union[
        Callable[[Any, P], R],
        Callable[[Any, Optional[P]], R],
        Callable[[Any, List[P]], R],
    ],
    /,
) -> Callable[[Any], R]:
    ...


@overload
def argument(
    getter: Union[
        Callable[[Any, P], None],
        Callable[[Any, Optional[P]], None],
        Callable[[Any, List[P]], None],
    ],
    /,
) -> Callable[[Any], P]:
    ...


def argument(
    name: Optional[
        Union[
            str,
            Union[
                Callable[[Any, P], R],
                Callable[[Any, Optional[P]], R],
                Callable[[Any, List[P]], R],
                Callable[[Any, P], None],
                Callable[[Any, Optional[P]], None],
                Callable[[Any, List[P]], None],
            ],
        ]
    ] = None,
    aliases: Optional[Union[str, Iterable[str]]] = None,
    metavar: Optional[str] = None,
    choices: Optional[Iterable[P]] = None,
    const: bool = False,
    nargs: Optional[Union[int, Literal["*"], Literal["+"]]] = None,
) -> Union[
    Callable[[Any], P],
    Callable[[Any], R],
    Callable[[Callable[[Any], R]], Callable[[Any], Optional[R]]],
    Callable[[Callable[[Any, P], R]], Callable[[Any], R]],
    Callable[[Callable[[Any, Optional[P]], R]], Callable[[Any], R]],
    Callable[[Callable[[Any, List[P]], R]], Callable[[Any], R]],
]:
    """The decorator for an argument.

    Args:
        name (str, optional):
            A name of the argument.

            If you set the name of the argument, users should pass
            the parameter by this name, but you can still access the argument
            by argument function name.

            Defaults to None.

        aliases (Union[str, Iterable[str]], optional):
            An alias or aliases of the argument.

            If the alias is one character, its flag will starts with one
            bar(-). Otherwise, if the alias is a sequence of two or more
            character, its flag will starts with two bar(--).

            For example, if the alias is `f`, its flag will be `-f`. If the
            alias is `foo`, its flag will be `--foo`.

            Defaults to None.

        metavar (str, optional): Defaults to None.

        choices (ReturnType, optional): Defaults to None.

        const (ReturnType, optional): Defaults to None.

        nargs (Union[int, Literal["*"], Literal["+"]], optional):
            Defaults to None.

    Returns:
        Callable[[Any], R]: An argument function.

        Callable[[Getter[T, R]], Callable[[Any], R]]:
            A decorator for argument function.
    """
    # @overload: If name is getter function
    if name is not None and not isinstance(name, str):
        return __generate_argument_getter(name)

    args: List[str] = []
    kwds: Dict[str, Any] = {}

    if aliases is not None:
        if isinstance(aliases, str):
            aliases = [aliases]
        for alias in aliases:
            if len(alias) == 1:
                args.append(f"-{alias}")
            else:
                alias = alias.replace("_", "-")
                args.append(f"--{alias}")

    if nargs is not None:
        kwds["nargs"] = nargs

    if const:
        kwds["const"] = const

    if choices is not None:
        kwds["choices"] = choices

    if metavar is not None:
        kwds["metavar"] = metavar

    return lambda getter: __generate_argument_getter(
        getter, name=name, *args, **kwds
    )
