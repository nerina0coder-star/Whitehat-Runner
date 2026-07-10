import keyword
from typing import Callable

from typeguard import typechecked


class Function:

    @staticmethod
    @typechecked
    def define(explicit_name: str | None = None) -> Callable[[Callable], "Function"]:
        def decorator(function: Callable) -> "Function":
            return Function(function=function, explicit_name=explicit_name)
        return decorator

    @typechecked
    def __init__(self,
                 function: Callable,
                 explicit_name: str | None = None) -> None:
        """
        Creates a function to call across files.

        Args:
            function(callable): a callable to return when calling the Function instance.
            explicit_name(str): an explicit name of the function.
        Example:
            Function('calc', {'operation', str}, original_calc)
        """
        if explicit_name is None and function.__name__ != '<lambda>':
            explicit_name = function.__name__

        Function.__validate(function, explicit_name)

        Function.__wrap__(self, function)
        self.name = explicit_name
        self.function = function
        Function.__wrap__(self, function)

        return

    def __repr__(self) -> str:
        return f'<Function {self.name}>'

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @staticmethod
    def __validate(function: Callable,
                   explicit_name: str | None = None) -> None:
        if explicit_name is None and function.__name__ == '<lambda>':
            raise TypeError(f'explicit_name must be filled when giving a Lambda function')
        if (explicit_name is None or not explicit_name) and \
                getattr(function, '__name__', None) is None:
            raise TypeError(f'explicit_name must be filled when giving a nameless callable')
        if explicit_name is not None and \
                not explicit_name.isidentifier() or keyword.iskeyword(explicit_name):
            raise TypeError(f'explicit_name cannot be a keyword and must be an identifier')

    @staticmethod
    @typechecked
    def __wrap__(function_obj: "Function", func: Callable):
        for i in ('__module__', '__name__', '__qualname__', '__doc__', '__annotations__'):
            method = getattr(func, i, None)
            if method is None: continue
            setattr(function_obj, i, method)