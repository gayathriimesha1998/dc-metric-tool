import re

decision_keywords = ['if', 'else if', 'for', 'while', 'switch', 'case', 'catch', '?']
excluded_calls = ['runtime_error', 'invalid_argument', 'out_of_range', 'logic_error', 'domain_error', 'length_error']

def analyze_cpp_code(code):
    lines = code.split('\n')
    total_dc = 0
    cc = 1
    nesting_stack = []
    line_scores = {}
    methods = {}
    classes = {}
    structures = {}
    current_method = None
    current_class = None

    method_dc = 0
    method_cc = 1
    class_dc = 0
    class_cc = 1
    inside_method = False
    inside_class = False

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            continue

        # Class detection
        class_match = re.match(r'class\s+(\w+)', stripped)
        if class_match:
            if current_class:
                classes[current_class] = {'dc': class_dc, 'cc': class_cc}
                class_dc, class_cc = 0, 1
            current_class = class_match.group(1)
            inside_class = True
            continue

        # ACTUAL FIX HERE: Match only real function definitions with return type + name + () + {
        if not inside_method:
            func_def_match = re.match(r'^\s*([\w:<>\*&]+)\s+(\w+)\s*\([^)]*\)\s*\{', stripped)
            if func_def_match:
                return_type, method_name = func_def_match.groups()
                if method_name not in excluded_calls and not stripped.startswith("throw"):
                    if current_method:
                        methods[current_method] = {'dc': method_dc, 'cc': method_cc}
                        method_dc, method_cc = 0, 1
                    current_method = method_name
                    inside_method = True
                    continue

        # Control structure detection
        nesting_level = len(nesting_stack)

        # Ternary operator
        if '?' in stripped and ':' in stripped:
            dc, c = process_condition(stripped, 'ternary', nesting_level)
            cc += c
            method_cc += c
            class_cc += c
            total_dc += dc
            method_dc += dc
            class_dc += dc
            line_scores[i] = line_scores.get(i, 0) + dc
            update_structure(structures, 'ternary', nesting_level, nesting_stack)

        elif match := re.match(r'(if|else if|for|while|switch|case|catch)\b', stripped):
            keyword = match.group(1)
            nesting_stack.append(keyword)
            dc, c = process_condition(stripped, keyword, nesting_level)
            cc += c
            method_cc += c
            class_cc += c
            total_dc += dc
            method_dc += dc
            class_dc += dc
            line_scores[i] = line_scores.get(i, 0) + dc
            update_structure(structures, keyword, nesting_level, nesting_stack)

        # End of block
        if '}' in stripped:
            if nesting_stack:
                nesting_stack.pop()
            if inside_method and current_method:
                methods[current_method] = {'dc': method_dc, 'cc': method_cc}
                current_method = None
                method_dc, method_cc = 0, 1
                inside_method = False
            if inside_class and current_class:
                classes[current_class] = {'dc': class_dc, 'cc': class_cc}
                current_class = None
                class_dc, class_cc = 0, 1
                inside_class = False

    # Final flush
    if current_method:
        methods[current_method] = {'dc': method_dc, 'cc': method_cc}
    if current_class:
        classes[current_class] = {'dc': class_dc, 'cc': class_cc}

    return {
        'decisional_complexity': total_dc,
        'cyclomatic_complexity': cc,
        'line_scores': line_scores,
        'methods': methods,
        'classes': classes,
        'structures': structures
    }

def process_condition(line, keyword, nesting):
    base_weight = {
        'if': 2, 'else if': 2, 'for': 2, 'while': 3,
        'switch': 2, 'case': 1, 'catch': 1, 'ternary': 2
    }.get(keyword, 1)

    condition_part = extract_condition(line, keyword)
    num_conditions = len(re.findall(r'(&&|\|\||\?)', condition_part)) + 1
    num_operators = len(re.findall(r'[=!<>+\-*/%]', condition_part))
    num_operands = len(re.findall(r'\b\w+\b', condition_part))

    token_sum = num_conditions + num_operators + num_operands
    nesting_depth = max(nesting, 1)
    weight = nesting_depth * base_weight * token_sum
    return weight, 1

def extract_condition(line, keyword):
    if keyword == 'ternary':
        return line.split('?')[0]
    elif '(' in line and ')' in line:
        return line[line.find('(')+1:line.find(')')]
    return ''

def update_structure(structures, keyword, nesting_level, nesting_stack):
    if keyword not in structures:
        structures[keyword] = {
            'count': 0,
            'nesting_levels': [],
            'level_counts': {},
            'nested_conditions': {}
        }

    structures[keyword]['count'] += 1
    structures[keyword]['nesting_levels'].append(nesting_level)
    level_str = str(nesting_level)
    level_counts = structures[keyword]['level_counts']
    level_counts[level_str] = level_counts.get(level_str, 0) + 1

    if level_str not in structures[keyword]['nested_conditions']:
        structures[keyword]['nested_conditions'][level_str] = {}

    if nesting_level > 0 and len(nesting_stack) > 1:
        parent = nesting_stack[-2]
        parent_level_str = str(nesting_level - 1)
        if parent not in structures:
            structures[parent] = {
                'count': 0,
                'nesting_levels': [],
                'level_counts': {},
                'nested_conditions': {}
            }
        if parent_level_str not in structures[parent]['nested_conditions']:
            structures[parent]['nested_conditions'][parent_level_str] = {}
        nested = structures[parent]['nested_conditions'][parent_level_str]
        nested[keyword] = nested.get(keyword, 0) + 1
