"""Decorator-based registration for parsers and formatters."""

from .protocols import SectionFormatter, SectionParser


class DefaultParserRegistry:
    """Default implementation of parser registry."""

    def __init__(self) -> None:
        self._parsers: list[SectionParser] = []

    def register(self, parser: SectionParser) -> None:
        self._parsers.append(parser)

    def get_all(self) -> list[SectionParser]:
        return list(self._parsers)


class DefaultFormatterRegistry:
    """Default implementation of formatter registry."""

    def __init__(self) -> None:
        self._formatters: list[SectionFormatter] = []

    def register(self, formatter: SectionFormatter) -> None:
        self._formatters.append(formatter)

    def get_all(self) -> list[SectionFormatter]:
        return list(self._formatters)


_parser_registry = DefaultParserRegistry()
_formatter_registry = DefaultFormatterRegistry()


def register_parser[T](cls: type[T]) -> type[T]:
    _parser_registry.register(cls())  # type: ignore[arg-type]
    return cls


def register_formatter[T](cls: type[T]) -> type[T]:
    _formatter_registry.register(cls())  # type: ignore[arg-type]
    return cls


def get_parser_registry() -> DefaultParserRegistry:
    return _parser_registry


def get_formatter_registry() -> DefaultFormatterRegistry:
    return _formatter_registry
