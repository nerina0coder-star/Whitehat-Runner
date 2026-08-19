import ast
import math
import os
import time
from multiprocessing import Array, Process

from WhitehatRunner import Whitelist


class ASTSecure(ast.NodeTransformer):

    def __init__(self, whitelist: Whitelist, max_workers: int | None = None, force_optimize: bool = True):
        self.next_name_safe = False
        self.last_assign = None
        self.whitelist = whitelist
        self.numbers: dict[str, int] = {}
        self.made: list[str] = []
        self.isSafe = True
        self.max_workers = max_workers
        self.force_optimize = force_optimize

    @staticmethod
    def __helper(number, arr, chunk: list, whitelist: Whitelist):
        safety_checker = ASTSecure(whitelist)
        safety_checker.visit(ast.parse("".join(f"{x}\n" for x in chunk)))
        arr[number] = 1 if safety_checker.isSafe else 0

    def __call__(self, codes: list[str]) -> tuple[bool, list]:
        """
        Checks the given codes for bad intend.
        """
        max_workers = self.max_workers
        if max_workers is None:
            max_workers = os.cpu_count() - 1
        if max_workers <= 0:
            raise RuntimeError('Expected max_workers to be a positive integer, found {} instead.'.format(max_workers))
        codes = list(filter(lambda code: True if code.strip() else False, codes))
        length = math.ceil(len(codes) // max_workers) + 1
        processes = {}
        arr = Array('b', [-1 for _ in range(max_workers)])
        chunks = [codes[0:length], *[codes[length * (x + 1):length * (x + 2)]
                                     for x in range(max_workers)]]
        worker_id = 0
        dead = []
        brk = False

        optimize = len(codes) > 100 if not self.force_optimize else True

        for chunk in chunks:
            if not chunk: continue
            process = Process(target=ASTSecure.__helper, args=[worker_id, arr, chunk, self.whitelist])
            process.start()
            processes.setdefault(worker_id, process)
            worker_id += 1
        if not optimize:
            for process in processes.values():
                process.join()
        # Stops early, good for too many lines of code.
        while True and optimize:
            for id_, process in processes.items():
                if not process.is_alive():
                    dead.append(process)
                    if len(dead) == len(processes):
                        brk = True
                        break
                    continue
                if arr[id_] == 0:
                    brk = True
                    break
            if brk:
                break
            time.sleep(0.1)
        # Checks if all succeeded.
        if not all(x.exitcode == 0 for x in processes.values()):
            raise RuntimeError("Something went wrong while checking exit codes."
                               f"Return statuses: {"".join(f"\nprocess {x} exited with {y.exitcode} " for x, y in processes.items() if y.exitcode != 0)}")
        # noinspection PyTypeChecker
        return 0 not in arr, list(arr)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id not in self.whitelist._whitelisted_globals\
                and node.func.id not in self.made:
            self.isSafe = False
        elif isinstance(node.func, ast.Attribute) and node.func.attr not in self.whitelist._whitelisted_globals:
            self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module not in self.whitelist._imports:
            self.isSafe = False

        if self.isSafe:
            self.generic_visit(node)

    def visit_alias(self, node):
        if node.name not in self.whitelist._imports:
            self.isSafe = False
        elif node.asname is not None and node.asname not in self.whitelist._aliases:
            self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.value, (ast.Name, ast.Constant)):
            self.last_assign = node.targets
            self.log_if_number(node)
            self.handle_made_appending_for_assign(node)
            self.check_value_safe(node.value)

        if self.isSafe:
            self.generic_visit(node)

    def visit_AugAssign(self, node):
        if isinstance(node.value, (ast.Name, ast.Constant)):
            self.check_value_safe(node.value)
            self.log_if_number(node)
            self.made.append(node.target.id)
            self.last_assign = node.target.id

        if self.isSafe:
            self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.value, (ast.Name, ast.Constant)):
            self.check_value_safe(node.value)
            self.log_if_number(node)
            self.made.append(node.target.id)
            self.last_assign = node.target.id

        if self.isSafe:
            self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        self.check_attr(node)
        if self.isSafe:
            self.next_name_safe = True
            self.generic_visit(node)

    def visit_BinOp(self, node):
        danger = [ast.Mult, ast.Pow, ast.LShift]
        if node.op in danger:
            if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
                if (isinstance(node.right.value, (int, float)) and node.right.value > self.whitelist.max_integer_value) or \
                        (isinstance(node.left.value, (int, float)) and node.left.value > self.whitelist.max_integer_value):
                    self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.made.append(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.made.append(node.name)
        self.generic_visit(node)

    def visit_Name(self, node):
        if not (node.id in self.whitelist._whitelisted_globals or
            node.id in self.made or self.next_name_safe):
            self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)

#    def visit_ListComp(self, node): ...
#    def visit_DictComp(self, node): ...
#    def visit_SetComp(self, node): ...
#    def visit_GeneratorExp(self, node): ...

    def reset(self):
        self.isSafe = True

    def check_value_safe(self, item):
        if isinstance(item, ast.Name):
            if not item.id in \
                self.whitelist._whitelisted_globals:
                self.isSafe = False
        if isinstance(item, ast.Constant):
            if isinstance(item.value, (int, float)) and item.value > 100:
                self.isSafe = False

    def log_if_number(self, assign: ast.AugAssign | ast.AnnAssign | ast.Assign):
        if not type(assign) in [ast.AugAssign, ast.AnnAssign, ast.Assign]:
            return

        if isinstance(assign, ast.AugAssign | ast.AnnAssign):
            if not isinstance(assign.value, ast.Constant):
                return
            if isinstance(assign.value.value, int | float):
                self.numbers[assign.target.id] = assign.value.value
        if isinstance(assign, ast.Assign):
            if isinstance(assign.value, ast.Constant):
                if isinstance(assign.value.value, int | float):
                    for target in assign.targets:
                        if not isinstance(target, ast.Name):
                            continue
                        self.numbers[target.id] = assign.value.value
            elif isinstance(assign.value, ast.Tuple):
                if len(assign.targets) == 1 and isinstance(assign.targets[0], ast.Tuple):
                    # noinspection PyTypeChecker
                    target: ast.Tuple = assign.targets[0]
                    if len(assign.value.elts) == len(target.elts):
                        for i in range(len(target.elts)):
                            if not (isinstance(target.elts[i], ast.Name) and
                                    isinstance(assign.value.elts[i], ast.Constant)):
                                continue
                            if not isinstance(assign.value.elts[i].value, int | float): # type: ignore
                                continue
                            self.numbers[target.elts[i].id] = assign.value.value[i] # type: Ignore
        return

    # TODO

    def check_attr(self, attr: ast.Attribute | ast.Name):
        if isinstance(attr, ast.Name):
            if attr.id not in self.whitelist._attributes:
                self.isSafe = False
            return attr.id
        # noinspection PyTypeChecker
        parent = self.check_attr(attr.value)
        if not self.isSafe:
            return attr
        lst = self.whitelist._attributes.get(parent)
        if lst is None or attr.attr not in lst:
            self.isSafe = False
        return attr

    def handle_made_appending_for_assign(self, node):
        def handle_tuple(tpl: ast.Tuple):
            for elt in tpl.elts:
                if isinstance(elt, ast.Tuple):
                    handle_tuple(elt)
                elif isinstance(elt, ast.Name):
                    self.made.append(elt.id)

        for target in node.targets:
            if not isinstance(target, ast.Name | ast.Tuple):
                continue
            if isinstance(target, ast.Tuple):
                handle_tuple(target)
                continue
            self.made.append(target.id)

#    def check_comp(self, comp: ast.comprehension, elt: ast.expr):
#        switch = {
#
#        } TODO
