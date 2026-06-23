import ast

from WhitehatRunner import Whitelist


class ASTSecure(ast.NodeTransformer):
    def __init__(self, whitelist: Whitelist):
        self.whitelist = whitelist
        self.isSafe = True

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
        self.check_value_safe(node.value)
        if self.isSafe:
            self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.check_value_safe(node.value)
        if self.isSafe:
            self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.check_value_safe(node.value)
        if self.isSafe:
            self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr not in self.whitelist.attributes:
            self.isSafe = False
        if self.isSafe:
            self.generic_visit(node)

    def reset(self):
        self.isSafe = True

    def check_value_safe(self, item):
        if isinstance(item, ast.Name):
            if not item.id in self.whitelist.whitelisted_globals:
                self.isSafe = False


    # TODO
