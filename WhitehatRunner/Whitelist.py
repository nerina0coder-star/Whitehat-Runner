from collections.abc import Callable
from os import fork



from .Function import Function


class Whitelist:

    
    def __init__(self, functions: list[Function] | Function):
        """
        Creates a new instance of Whitelist.
        Args:
            functions (List[Function] | Function): A single or list of functions to whitelist
        """
        if isinstance(functions, Function):
            functions = [functions]
        functions = list(dict.fromkeys(functions))
        self.functions: list[Function] = [function for function in functions if
                                          function is not fork and function is not None]
        self._names = [i.name for i in functions if i.name is not None]
        self._whitelisted_globals = {}
        self.__whitelisted_globals_update__()
        self._imports = []
        self._aliases = []
        self._attributes = {}

        self.max_integer_value: int = 100
        """
        You can interpreter it as:
        When doing variable assignment or math, what is the limit of it?
        """


    
    def __getitem__(self, name_or_index: int | str):
        """
        Gets a whitelisted function by its name.
        Args:
            name_or_index (str): Name of the function
        """
        if isinstance(name_or_index, int):
            return self.functions[name_or_index]
        return self.functions[self._names.index(name_or_index)] if name_or_index in self._names else None

    def __len__(self):
        return len(self.functions) + len(self._imports) + len(self._attributes)

    def __iter__(self):
        return self.ally()

    
    def whitelist(self, functions: Function | list[Function | Callable] | Callable, ignore_present: bool = False):
        """
        Adds whitelisted functions to the whitelist.
        Args:
            functions (List[Function]): List of "Whitehat Runner Function"-s to whitelist.
            ignore_present (bool, optional): Whether to ignore existing functions. Defaults to False.
        """
        if isinstance(functions, Function):
            functions = [functions]

        if not all(isinstance(i, Function) for i in functions):
            raise ValueError("Expected a function or a list of functions.")

        functions = list(dict.fromkeys(functions))
        names = []
        for i in functions:
            if i not in self.functions:
                if i.name in self._names:
                    raise ValueError(f'The name of the functions must be unique, found duplicate: {i.name}')
                names.append(i.name)
            elif ignore_present:
                functions.remove(i)
            else:
                raise ValueError(f'List must contain new functions, existing: {i}')
        self.functions.extend(functions)
        self._names.extend(names)
        self.__whitelisted_globals_update__()

    
    def whitelist_imports(self, the_imports: str, the_froms: str | None = None, the_as: str | None = None):
        """
        Whitelists imports of different modules, and limit the alias.
        """

        blocked = ["os", "subprocess", "sys", "pty", "Popen", "CPython", "cffi", "ctypes"]
        the_imports_lst = the_imports.split(',') if the_imports else []
        if the_froms is not None and the_froms:
            the_imports_lst.extend(the_froms.split(','))
        all_imports = list(
            dict.fromkeys([port for port in the_imports_lst if port not in blocked and port not in self._imports]))
        self._imports.extend(all_imports)
        if the_as is not None and the_as:
            all_as = list(dict.fromkeys(i for i in the_as.split(',') if i not in self._aliases))
            self._aliases.extend(all_as)

    
    def blacklist_imports(self, the_imports: str, the_froms: str | None = None, the_as: str | None = None):
        blacklisting_imports = the_imports.split(',') if the_imports else []
        blacklisting_imports.extend(the_froms.split(',')) if the_froms and the_froms is not None else []
        for i in blacklisting_imports:
            if i in self._imports:
                self._imports.remove(i)
        removing_as = the_as if the_as is not None and the_as is not None else []
        for i in removing_as:
            if i in self._aliases:
                self._aliases.remove(i)

    
    def whitelist_attribute(self, attr: dict[str, list[str]]):
        blocked = [
            "__builtins__",
            "__builtin__",
            "__class__",
            "__bases__",
            "__mro__",
            "__subclasses__",
            "__globals__",
            "__dict__",
            "__code__",
            "__self__",  # CVE-2026-47392: print.__self__ leaks builtins
            "__traceback__",  # CVE-2026-39888: frame traversal
            "tb_frame",
            "f_back",
            "f_builtins",
        ]
        for k, v in attr.items():
            if not hasattr(self.whitelist_attribute, k):
                self._attributes[k] = v

    
    def blacklist(self, functions: Function | list[Function | Callable] | Callable, ignore_absent: bool = False):
        """
        Blacklists whitelisted functions.
        Args:
            functions (List[Function]): List of "Whitehat Runner Function"-s to blacklist
            ignore_absent (bool, optional): Whether to ignore existing functions. Defaults to False.
        """

        if isinstance(functions, Function):
            functions = [functions]

        functions = list(dict.fromkeys(functions))
        names = []
        for i in functions:
            if i in self.functions:
                names.append(i.name)
            elif ignore_absent:
                functions.remove(i)
            else:
                raise ValueError(f'List must contain existing functions, new: {i}')
        self.functions = list(filter(lambda x: x not in functions, self.functions))
        self._names = list(filter(lambda x: x not in names, self._names))
        self.__whitelisted_globals_update__()

    
    def is_allowed(self, name: str):
        """
        Checks if the whitelisted function is whitelisted.
        Args:
            name (str): Name of the function
        """
        return name in self._names

    
    def ally(self):
        """
        Gets all whitelisted functions.
        """
        for i in self.functions:
            yield i.name, i

    def __whitelisted_globals_update__(self):
        blocked = [
            "exec",
            "eval",
            "compile",
            "open",
            "input",
            "breakpoint",
            "vars",  # CVE-2026-47392: vars(builtins) leaks everything
            "getattr",  # Can fetch blocked attrs dynamically
            "setattr",
            "delattr",
            "dir",
        ]
        builtin_base = globals()["__builtins__"]
        self._whitelisted_globals = {"__builtins__":builtin_base} # essential, but not checked inside it, it's so it can function. I liked it to get tighter, but it would then get annoying.
        for i, j in self.ally():
            if i not in blocked:
                self._whitelisted_globals[i] = j
