from typing import List, TypeVar, Type, Callable, Optional, Generator, overload

from attrs import Attribute

T = TypeVar("T")


@overload
def starfield(target_class: Type[T], attributes: List[Attribute]) -> List[Attribute]:
    """
    Modify a class to accept a "star field" argument. A star field is a special type of argument
    that is passed as a tuple of variadic positional arguments (i.e., "*args").

    :param target_class: The class to modify.
    :return: The modified class.
    """


@overload
def starfield(repr: bool = False) -> Callable[[Type[T], List[Attribute]], List[Attribute]]:
    """
    Modify a class to accept a "star field" argument. A star field is a special type of argument
    that is passed as a tuple of variadic positional arguments (i.e., "*args").

    :param repr: Whether to include the star field in the class's __repr__.
    :return: A field transformer that modifies a class to accept a star field.
    """


def starfield(
    maybe_target_class: Optional[Type[T]] = None, attributes: Optional[List[Attribute]] = None, *, repr: bool = False
) -> List[Attribute] | Callable[[Type[T], List[Attribute]], List[Attribute]]:
    def _starfield(target_class: Type[T], attributes: List[Attribute]) -> List[Attribute]:
        # Find the attribute with init="*".
        variadic_attributes = [attribute for attribute in attributes if attribute.init == "*"]
        # Raise an error if there is not exactly one such attribute
        if len(variadic_attributes) != 1:
            raise ValueError(
                f"Expected exactly one attribute with init='*', got {len(variadic_attributes)}: {variadic_attributes}"
            )
        variadic_attribute = attributes[0]

        def __init__(self, *args, **kwargs):
            """
            Modify the original `__init__` method of the class to accept a "star field" argument.
            """
            # Raise an error if the star field is passed as a keyword argument and there are also variadic positional arguments
            if variadic_attribute.name in kwargs and len(args) > 0:
                raise ValueError(
                    f"Cannot pass star field {variadic_attribute.name} as a keyword argument when there are variadic positional arguments"
                )
            # If the `kwargs` dictionary doesn't already contain a value for the star field, use the tuple of variadic positional arguments
            if variadic_attribute.name not in kwargs:
                kwargs[variadic_attribute.name] = args
            # Call the original `__attrs_init__` method of the class, passing it the modified `kwargs` dictionary
            self.__attrs_init__(**kwargs)

        # Modify the class to use the new `__init__` method
        target_class.__init__ = __init__  # type: ignore[misc]

        # Add a `__rich_repr__` method to the class
        def __rich_repr__(self) -> Generator[str, None, None]:
            """
            Generate a rich representation of the class instance.

            :return: A generator of strings that can be joined to form a rich representation of the class instance.
            """
            # Yield from the star field
            yield from getattr(self, variadic_attribute.name)
            # Yield the remaining attributes
            for attribute in attributes:
                if attribute is not variadic_attribute:
                    yield attribute.name, getattr(self, attribute.name), attribute.default

        # Set the `__rich_repr__` method on the class
        target_class.__rich_repr__ = __rich_repr__

        # If the `repr` argument is True, add a `__repr__` method to the class
        if repr:
            def __repr__(self) -> str:
                """
                Generate a rich representation of the class instance.

                :return: A string that can be used as a rich representation of the class instance.
                """
                elements = []
                for yielded in self.__rich_repr__():
                    match yielded:
                        case (name, value, default):
                            if value != default:
                                elements.append(f"{name}={value!r}")
                        case name, value:
                            elements.append(f"{name}={value!r}")
                        case value:
                            elements.append(f"{value!r}")
                return f"{self.__class__.__name__}({', '.join(elements)})"

            # Set the `__repr__` method on the class
            target_class.__repr__ = __repr__

        # Return a list of modified Attribute objects
        return [attribute.evolve(kw_only=True) if attribute != variadic_attribute else attribute for attribute in
            attributes]

    if maybe_target_class is None and attributes is None:
        return _starfield
    elif maybe_target_class is not None and attributes is not None:
        return _starfield(maybe_target_class, attributes)
    else:
        raise ValueError("Expected either no arguments or two arguments")
