import ast

from WhitehatRunner import Whitelist


class ASTSecure(ast.NodeTransformer):
    def __init__(self, whitelist: Whitelist):
        self.whitelist = whitelist
        self.isSafe = True

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id not in self.whitelist.whitelisted_globals:
            self.isSafe = False
        self.generic_visit(node)
        self.isSafe = True and self.isSafe

    def visit_ImportFrom(self, node):
        self.isSafe = False
        self.generic_visit(node)

    def visit_Import(self, node):
        self.isSafe = False
        self.generic_visit(node)

    def visit_alias(self, node):
        self.isSafe = False
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Constant):
            if node.value not in self.whitelist.whitelisted_globals:
                self.isSafe = False
        elif isinstance(node.value, ast.Tuple):
            for i in node.value.elts:
                if i not in self.whitelist.whitelisted_globals:
                    self.isSafe = False
        self.isSafe = True and self.isSafe
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if isinstance(node.value, ast.Constant):
            if node.target.id not in self.whitelist.whitelisted_globals:
                self.isSafe = False
        self.isSafe = True and self.isSafe
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            if node.target.id not in self.whitelist.whitelisted_globals:
                self.isSafe = False
        self.isSafe = True and self.isSafe

        self.generic_visit(node)

    def reset(self):
        self.isSafe = True

    # TODO
