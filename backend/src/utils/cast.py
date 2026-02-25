from typing import TypeVar, Callable

T = TypeVar("T")


def create_caster(schema_class: type[T]) -> Callable[[dict], T]:
    def cast(data: dict) -> T:
        return schema_class(**data)

    return cast
