from typing import Callable


class Function:
    def __init__(self,
                 function: Callable, explicit_name: str = None) -> None:
        """
        Creates a function to call across files.

        Args:
            function(callable): a callable to return when calling the Function instance.
            explicit_name(str): an explicit name of the function.
        Example:
            Function('calc', {'operation', str}, original_calc)
        """
        if function is None:
            raise TypeError(f'Expected a value, given None: function is None')
        if not isinstance(function, Callable):
            raise TypeError(f'Expected a callable, given {function.__name__} is not callable')
        if explicit_name is None and function.__name__ == '<lambda>':
            raise TypeError(f'explicit_name must be filled when giving a Lambda function')
        if explicit_name is not None and getattr(function, '__name__', None) is None:
            raise TypeError(f'explicit_name must be filled when giving a nameless callable')
        self.name = function.__name__ if explicit_name is None else explicit_name
        self.function = function
    def __repr__(self) -> str:
         return f'<Function {self.name}>'
    def __call__(self, *args, **kwargs):
        return self.function
