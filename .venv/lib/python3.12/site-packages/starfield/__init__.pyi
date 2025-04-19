from typing import List, TypeVar

from attrs import Attribute

T = TypeVar("T")


@overload
def starfield(target_class: Type[T], attributes: List[Attribute]) -> List[Attribute]:
    ...


@overload
def starfield(*, repr: bool = False) -> Callable[[Type[T], List[Attribute]], List[Attribute]]:
    ...
