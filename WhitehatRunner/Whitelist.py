from typing import List
from os import fork
from .Function import Function


class Whitelist:
    
    def __init__(self, functions: List[Function] | Function):
        """
        Creates a new instance of Whitelist.
        Args:
            functions (List[Function] | Function): A single or list of functions to whitelist
        """
        if isinstance(functions, Function):
            functions = [functions]
        functions = list(set(functions))
        self.functions: List[Function] = [function for function in functions if function is not fork and function is not None]
        self.names = [i.name for i in functions if i.name is not None]
        self.whitelisted_globals = {}
        for i, j in self.ally():
            self.whitelisted_globals[i] = j()
    def __getitem__(self, name):
        """
        Gets a whitelisted function by its name.
        Args:
            name (str): Name of the function
        """
        return self.functions[self.names.index(name)] if name in self.names else None

    def whitelist(self, functions: Function|List[Function], ignore_present: bool = False):
        """
        Adds whitelisted functions to the whitelist.
        Args:
            functions (List[Function]): List of functions to whitelist
            ignore_present (bool, optional): Whether to ignore existing functions. Defaults to False.
        """
        functions = list(set(functions))
        names = []
        for i in functions:
            if i not in self.functions:
                if i.name in self.names:
                    raise ValueError('The name of the functions must be unique, found duplicate: {i.name}')
                names.append(i.name)
            elif ignore_present:
                functions.remove(i)
            else:
                raise ValueError('List must contain new functions, existing: {i}')
        self.functions.extend(functions)
        self.names.extend(names)
    def blacklist(self, functions: Function|List[Function], ignore_absent: bool = False):
        """
        Blacklists whitelisted functions.
        Args:
            functions (List[Function]): List of functions to blacklist
            ignore_absent (bool, optional): Whether to ignore existing functions. Defaults to False.
        """
        functions = list(set(functions))
        names = []
        for i in functions:
            if i in self.functions: names.append(i.name)
            elif ignore_absent:
                functions.remove(i)
            else:
                raise ValueError('List must contain existing functions, new: {i}')
        self.functions = list(filter(lambda x: x not in functions, self.functions))
        self.names = list(filter(lambda x: x not in names, self.names))
    def is_allowed(self, name: str):
        """
        Checks if the whitelisted function is whitelisted.
        Args:
            name (str): Name of the function
        """
        return name in self.names
    def ally(self):
        """
        Gets all whitelisted functions.
        """
        for i in self.functions:
            yield i.name, i
