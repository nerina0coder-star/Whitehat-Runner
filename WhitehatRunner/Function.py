from typing import Callable

from typeguard import typechecked


class Function:

    @typechecked
    def __init__(self,
                 function: Callable, explicit_name: str | None = None) -> None:
        """
        Creates a function to call across files.

        Args:
            function(callable): a callable to return when calling the Function instance.
            explicit_name(str): an explicit name of the function.
        Example:
            Function('calc', {'operation', str}, original_calc)
        """
        if explicit_name is None and function.__name__ == '<lambda>':
            raise TypeError(f'explicit_name must be filled when giving a Lambda function')
        if (explicit_name is None or not explicit_name) and getattr(function, '__name__', None) is None:
            raise TypeError(f'explicit_name must be filled when giving a nameless callable')
        self.name = function.__name__ if explicit_name is None else explicit_name
        self.function = function

    def __repr__(self) -> str:
        return f'<Function {self.name}>'

    def __call__(self):
        return self.function