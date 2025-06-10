import ast

def analyze_python_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            'total_dc': 0,
            'total_cc': 0,
            'line_scores': {},
            'methods': {},
            'classes': {},
            'structures': {}
        }

    line_scores = {}
    total_dc = 0
    total_cc = 1
    methods = {}
    classes = {}
    structures = {}

    class CodeAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.current_class = None
            self.current_func = None
            self.dc_stack = []
            self.cc_stack = []
            self.depth = 0

        def _register_structure(self, type_name, lineno, test_node=None, body=None, base_weight=1):
            if type_name not in structures:
                structures[type_name] = {
                    'count': 0,
                    'nesting_levels': [],
                    'level_counts': {},
                    'nested_conditions': {}
                }

            structures[type_name]['count'] += 1
            structures[type_name]['nesting_levels'].append(self.depth)

            level_str = str(self.depth)
            level_counts = structures[type_name]['level_counts']
            level_counts[level_str] = level_counts.get(level_str, 0) + 1

            if level_str not in structures[type_name]['nested_conditions']:
                structures[type_name]['nested_conditions'][level_str] = {}

            # Add DC
            if test_node:
                conds, ops, operands = self._extract_tokens(test_node)
            else:
                conds, ops, operands = 1, 0, 0

            token_sum = conds + ops + operands
            weight = (self.depth * base_weight * token_sum) if self.depth > 0 else (base_weight * token_sum)

            nonlocal total_dc
            total_dc += weight
            line_scores[lineno] = line_scores.get(lineno, 0) + weight

            if self.cc_stack:
                self.cc_stack[-1] += 1
            if self.dc_stack:
                self.dc_stack[-1] += weight

            # Track nested control structures from the body (not just test)
            if body:
                flat_nodes = [n for stmt in body for n in ast.walk(stmt)]
                nested = structures[type_name]['nested_conditions'][level_str]
                for n in flat_nodes:
                    kind = None
                    if isinstance(n, ast.If):
                        kind = 'if'
                    elif isinstance(n, ast.For):
                        kind = 'for'
                    elif isinstance(n, ast.While):
                        kind = 'while'
                    elif isinstance(n, ast.Try):
                        kind = 'try'
                    elif isinstance(n, ast.IfExp):
                        kind = 'ternary'
                    if kind:
                        nested[kind] = nested.get(kind, 0) + 1

        def _extract_tokens(self, test_node):
            conds = 1
            ops = 0
            operands = 0
            for node in ast.walk(test_node):
                if isinstance(node, ast.BoolOp):
                    conds += len(node.values) - 1
                elif isinstance(node, ast.BinOp):
                    ops += 1
                elif isinstance(node, ast.Compare):
                    ops += len(node.ops)
                elif isinstance(node, (ast.Name, ast.Constant)):
                    operands += 1
            return conds, ops, operands

        def visit_FunctionDef(self, node):
            self.current_func = node.name
            self.dc_stack.append(0)
            self.cc_stack.append(1)
            self.generic_visit(node)
            methods[self.current_func] = {
                'dc': self.dc_stack.pop(),
                'cc': self.cc_stack.pop()
            }
            self.current_func = None

        def visit_ClassDef(self, node):
            self.current_class = node.name
            self.dc_stack.append(0)
            self.cc_stack.append(1)
            self.generic_visit(node)
            classes[self.current_class] = {
                'dc': self.dc_stack.pop(),
                'cc': self.cc_stack.pop()
            }
            self.current_class = None

        def visit_If(self, node):
            self.depth += 1
            self._register_structure('if', node.lineno, test_node=node.test, body=node.body, base_weight=2)
            self.generic_visit(node)
            self.depth -= 1

        def visit_While(self, node):
            self.depth += 1
            self._register_structure('while', node.lineno, test_node=node.test, body=node.body, base_weight=3)
            self.generic_visit(node)
            self.depth -= 1

        def visit_For(self, node):
            self.depth += 1
            self._register_structure('for', node.lineno, body=node.body, base_weight=2)
            self.generic_visit(node)
            self.depth -= 1

        def visit_Try(self, node):
            self._register_structure('try', node.lineno, body=node.body, base_weight=1)
            self.generic_visit(node)

        def visit_IfExp(self, node):
            self._register_structure('ternary', node.lineno, test_node=node.test, base_weight=2)
            self.generic_visit(node)

        def visit_BoolOp(self, node):
            nonlocal total_cc
            total_cc += len(node.values) - 1
            if self.cc_stack:
                self.cc_stack[-1] += len(node.values) - 1
            self.generic_visit(node)

    CodeAnalyzer().visit(tree)

    return {
        'total_dc': total_dc,
        'total_cc': total_cc,
        'line_scores': line_scores,
        'methods': methods,
        'classes': classes,
        'structures': structures
    }
