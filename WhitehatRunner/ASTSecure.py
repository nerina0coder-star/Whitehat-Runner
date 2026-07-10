import ast
import math
import os
import time
from multiprocessing import Array, Process as P
from typing import List

from typeguard import typechecked

from WhitehatRunner import Whitelist


class ASTSecure(ast.NodeTransformer):
    @typechecked
    def __init__(self, whitelist: Whitelist, max_workers: int | None = None):
        self.whitelist = whitelist
        # self.numbers: Dict[str, int] = {}
        # self.last_assign = ""
        self.isSafe = True
        self.max_workers = max_workers

    @staticmethod
    @typechecked
    def __helper(number, arr, chunk: list, whitelist: Whitelist):
        safety_checker = ASTSecure(whitelist)
        safety_checker.visit(ast.parse("".join(f"{x}\n" for x in chunk)))
        arr[number] = 1 if safety_checker.isSafe else 0

    @typechecked
    def __call__(self, codes: List[str]):
        max_workers = self.max_workers
        if max_workers is None:
            max_workers = os.cpu_count() - 1
        if max_workers <= 0:
            raise RuntimeError('Expected max_workers to be a positive integer, found {} instead.'.format(max_workers))
        length = math.ceil(len(codes) // max_workers) + 1
        processes = {}
        arr = Array('b', [-1 for _ in range(max_workers)])
        chunks = [codes[0:length], *[codes[length * x + 1:length * x + 2] for x in range(max_workers - 1)]]
        worker_id = 0
        deads = []
        brk = False

        optimize = len(codes) > 500

        for chunk in chunks:
            if not chunk: continue
            process = P(target=ASTSecure.__helper, args=[worker_id, arr, chunk, self.whitelist])
            process.start()
            processes.setdefault(worker_id, process)
            worker_id += 1
        # Stops early, good for too many lines of code.
        while True:
            for id_, process in processes.items():
                if not process.is_alive():
                    deads.append(process)
                    if len(deads) == len(processes):
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
                               f"Return statuses: {"".join(f"\nprocess {x} exited with {y.exitcode} " for x, y in processes.items() if x.exitcode != 0)}")
        return 0 not in arr

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id not in self.whitelist.whitelisted_globals:
            self.isSafe = False
        elif isinstance(node.func, ast.Attribute) and node.func.attr not in self.whitelist.whitelisted_globals:
            self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module not in self.whitelist.imports:
            self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)

    def visit_alias(self, node):
        if node.name not in self.whitelist.imports:
            self.isSafe = False
        elif node.asname is not None and node.asname not in self.whitelist.aliases:
            self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)

    def visit_Assign(self, node):
        self.last_assign = node.targets[0]
        self.check_value_safe(node.value)
        if self.isSafe:
            self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.check_value_safe(node.value)
        self.last_assign = node.target.id
        if self.isSafe:
            self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.check_value_safe(node.value)
        self.last_assign = node.target.id
        if self.isSafe:
            self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr not in self.whitelist.attributes:
            self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)

    def visit_BinOp(self, node):
        danger = [ast.Mult, ast.Pow, ast.LShift]
        if node.op in danger:
            if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
                if node.left.value > 10 or node.right.value > 10:
                    self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)  # TODO

    def reset(self):
        self.isSafe = True

    def check_value_safe(self, item):
        if isinstance(item, ast.Name):
            if not item.id in self.whitelist.whitelisted_globals:
                self.isSafe = False

    # TODO
