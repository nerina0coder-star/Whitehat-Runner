from os import fork
from typing import List

from typeguard import typechecked

from .Function import Function


class Whitelist:

    @typechecked
    def __init__(self, functions: List[Function] | Function):
        """
        Creates a new instance of Whitelist.
        Args:
            functions (List[Function] | Function): A single or list of functions to whitelist
        """
        if isinstance(functions, Function):
            functions = [functions]
        functions = list(dict.fromkeys(functions))
        self.functions: List[Function] = [function for function in functions if
                                          function is not fork and function is not None]
        self.names = [i.name for i in functions if i.name is not None]
        self.whitelisted_globals = {}
        self.__whitelisted_globals_update__()
        self.imports = []
        self.aliases = []
        self.attributes = []

    @typechecked
    def __getitem__(self, name_or_index: int | str):
        """
        Gets a whitelisted function by its name.
        Args:
            name (str): Name of the function
        """
        if isinstance(name_or_index, int):
            return self.functions[name_or_index]
        return self.functions[self.names.index(name_or_index)] if name_or_index in self.names else None

    def __len__(self):
        return len(self.functions) + len(self.imports) + len(self.attributes)

    def __iter__(self):
        return self.ally()

    @typechecked
    def whitelist(self, functions: Function | List[Function], ignore_present: bool = False):
        """
        Adds whitelisted functions to the whitelist.
        Args:
            functions (List[Function]): List of functions to whitelist
            ignore_present (bool, optional): Whether to ignore existing functions. Defaults to False.
        """
        if isinstance(functions, Function):
            functions = [functions]

        functions = list(dict.fromkeys(functions))
        names = []
        for i in functions:
            if i not in self.functions:
                if i.name in self.names:
                    raise ValueError(f'The name of the functions must be unique, found duplicate: {i.name}')
                names.append(i.name)
            elif ignore_present:
                functions.remove(i)
            else:
                raise ValueError(f'List must contain new functions, existing: {i}')
        self.functions.extend(functions)
        self.names.extend(names)
        self.__whitelisted_globals_update__()

    @typechecked
    def whitelist_imports(self, the_imports: str, the_froms: str | None = None, the_as: str | None = None):
        """
        Whitelists imports of different modules, and limit the alias.
        """

        blocked = ["os", "subprocess", "sys", "pty", "Popen", "CPython", "cffi", "ctypes"]
        the_imports_lst = the_imports.split(',') if the_imports else []
        if the_froms is not None and the_froms:
            the_imports_lst.extend(the_froms)
        all_imports = list(
            dict.fromkeys([port for port in the_imports_lst if port not in blocked and port not in self.imports]))
        self.imports.extend(all_imports)
        if the_as is not None and the_as:
            all_as = list(dict.fromkeys(i for i in the_as.split(',') if i not in self.aliases))
            self.aliases.extend(all_as)

    @typechecked
    def blacklist_imports(self, the_imports: str, the_froms: str | None = None, the_as: str | None = None):
        blacklisting_imports = the_imports.split(',') if the_imports else []
        blacklisting_imports.extend(the_froms) if the_froms and the_froms is not None else []
        for i in blacklisting_imports:
            if i in self.imports:
                self.imports.remove(i)
        removing_as = the_as if the_as is not None and the_as is not None else []
        for i in removing_as:
            if i in self.aliases:
                self.aliases.remove(i)

    @typechecked
    def whitelist_attribute(self, attr: str):
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
        attrs = attr.split(',')
        attrs = list(dict.fromkeys(attr for attr in attrs if attr not in self.attributes and attr not in blocked))
        self.attributes.extend(attrs)

    @typechecked
    def blacklist(self, functions: Function | List[Function], ignore_absent: bool = False):
        """
        Blacklists whitelisted functions.
        Args:
            functions (List[Function]): List of functions to blacklist
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
        self.names = list(filter(lambda x: x not in names, self.names))
        self.__whitelisted_globals_update__()

    @typechecked
    def is_allowed(self, name: str):
        """
        Checks if the whitelisted function is whitelisted.
        Args:
            name (str): Name of the function
        """
        return name in self.names

    @typechecked
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
        for i, j in self.ally():
            if i not in blocked:
                self.whitelisted_globals[i] = j
