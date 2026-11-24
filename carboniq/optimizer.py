"""
CarbonIQ Sustainable Code Optimizer & Generator
Analyzes Python source code using Abstract Syntax Trees (AST) to detect carbon-heavy
computational patterns, and refactors them into high-efficiency, low-carbon implementations.
"""
import ast
import copy
import re
from typing import Dict, List, Any, Optional


class NameReplacer(ast.NodeTransformer):
    """AST helper that substitutes a variable name with an expression AST node."""
    def __init__(self, target_id: str, replacement_node: ast.AST):
        self.target_id = target_id
        self.replacement_node = replacement_node

    def visit_Name(self, node: ast.Name):
        if node.id == self.target_id and isinstance(node.ctx, ast.Load):
            return copy.deepcopy(self.replacement_node)
        return node


def refactor_loops_to_comprehensions(code_str: str) -> tuple[str, list[str]]:
    """
    Refactors unvectorized append loops and simple nested loops into efficient
    list comprehensions, eliminating repetitive dynamic memory reallocations.
    """
    try:
        tree = ast.parse(code_str)
    except Exception:
        return code_str, []

    lines = code_str.splitlines()
    replacements = []

    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            continue
        body = fn.body
        for i, stmt in enumerate(body):
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                if isinstance(stmt.value, ast.List) and len(stmt.value.elts) == 0:
                    var_name = stmt.targets[0].id
                    if i + 1 < len(body) and isinstance(body[i + 1], ast.For):
                        for_node = body[i + 1]

                        # 1. Nested For Loop (e.g. for u1 in ...: for u2 in ...: var.append(...))
                        if len(for_node.body) == 1 and isinstance(for_node.body[0], ast.For):
                            inner = for_node.body[0]
                            t1 = ast.unparse(for_node.target)
                            iter1 = ast.unparse(for_node.iter)
                            t2 = ast.unparse(inner.target)
                            iter2 = ast.unparse(inner.iter)

                            # Direct append
                            if len(inner.body) == 1 and isinstance(inner.body[0], ast.Expr):
                                call = inner.body[0].value
                                if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'append' and isinstance(call.func.value, ast.Name) and call.func.value.id == var_name:
                                    expr = ast.unparse(call.args[0])
                                    repl = f"{var_name} = [{expr} for {t1} in {iter1} for {t2} in {iter2}]"
                                    replacements.append((stmt.lineno, for_node.end_lineno, repl, f"Vectorized nested loop into list comprehension for '{var_name}'"))
                            # Assign then append (e.g. score = ...; var.append(score))
                            elif len(inner.body) == 2 and isinstance(inner.body[0], ast.Assign) and isinstance(inner.body[1], ast.Expr):
                                call = inner.body[1].value
                                if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'append' and isinstance(call.func.value, ast.Name) and call.func.value.id == var_name:
                                    if len(inner.body[0].targets) == 1 and isinstance(inner.body[0].targets[0], ast.Name):
                                        score_var = inner.body[0].targets[0].id
                                        if len(call.args) == 1 and isinstance(call.args[0], ast.Name) and call.args[0].id == score_var:
                                            expr = ast.unparse(inner.body[0].value)
                                            repl = f"{var_name} = [{expr} for {t1} in {iter1} for {t2} in {iter2}]"
                                            replacements.append((stmt.lineno, for_node.end_lineno, repl, f"Vectorized nested loop into list comprehension for '{var_name}'"))
                            # If then append
                            elif len(inner.body) == 1 and isinstance(inner.body[0], ast.If):
                                if_node = inner.body[0]
                                cond = ast.unparse(if_node.test)
                                if len(if_node.body) == 1 and isinstance(if_node.body[0], ast.Expr):
                                    call = if_node.body[0].value
                                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'append' and isinstance(call.func.value, ast.Name) and call.func.value.id == var_name:
                                        expr = ast.unparse(call.args[0])
                                        repl = f"{var_name} = [{expr} for {t1} in {iter1} for {t2} in {iter2} if {cond}]"
                                        replacements.append((stmt.lineno, for_node.end_lineno, repl, f"Vectorized nested loop with condition into list comprehension for '{var_name}'"))

                        # 2. Single For Loop
                        else:
                            t = ast.unparse(for_node.target)
                            it = ast.unparse(for_node.iter)

                            # Direct append
                            if len(for_node.body) == 1 and isinstance(for_node.body[0], ast.Expr):
                                call = for_node.body[0].value
                                if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'append' and isinstance(call.func.value, ast.Name) and call.func.value.id == var_name:
                                    expr = ast.unparse(call.args[0])
                                    repl = f"{var_name} = [{expr} for {t} in {it}]"
                                    replacements.append((stmt.lineno, for_node.end_lineno, repl, f"Replaced append loop with list comprehension for '{var_name}'"))
                            # If then append
                            elif len(for_node.body) == 1 and isinstance(for_node.body[0], ast.If):
                                if_node = for_node.body[0]
                                cond = ast.unparse(if_node.test)
                                if len(if_node.body) == 1 and isinstance(if_node.body[0], ast.Expr):
                                    call = if_node.body[0].value
                                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'append' and isinstance(call.func.value, ast.Name) and call.func.value.id == var_name:
                                        expr = ast.unparse(call.args[0])
                                        repl = f"{var_name} = [{expr} for {t} in {it} if {cond}]"
                                        replacements.append((stmt.lineno, for_node.end_lineno, repl, f"Replaced conditional append loop with list comprehension for '{var_name}'"))
                            # Assign then if then append (e.g. val = preprocessed[idx]; if idx % 2 == 0: valid_records.append({'id': idx, 'val': val}))
                            elif len(for_node.body) == 2 and isinstance(for_node.body[0], ast.Assign) and isinstance(for_node.body[1], ast.If):
                                if len(for_node.body[0].targets) == 1 and isinstance(for_node.body[0].targets[0], ast.Name):
                                    temp_var = for_node.body[0].targets[0].id
                                    temp_val = for_node.body[0].value
                                    if_node = for_node.body[1]
                                    cond = ast.unparse(if_node.test)
                                    if len(if_node.body) == 1 and isinstance(if_node.body[0], ast.Expr):
                                        call = if_node.body[0].value
                                        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'append' and isinstance(call.func.value, ast.Name) and call.func.value.id == var_name:
                                            append_arg = copy.deepcopy(call.args[0])
                                            replaced_arg = NameReplacer(temp_var, temp_val).visit(append_arg)
                                            expr = ast.unparse(replaced_arg)
                                            repl = f"{var_name} = [{expr} for {t} in {it} if {cond}]"
                                            replacements.append((stmt.lineno, for_node.end_lineno, repl, f"Replaced filtered append loop with list comprehension for '{var_name}'"))

    if not replacements:
        return code_str, []

    # Sort replacements from bottom to top so line indices remain consistent
    replacements.sort(key=lambda x: x[0], reverse=True)
    applied_descriptions = []

    for start_l, end_l, repl_code, desc in replacements:
        orig_line = lines[start_l - 1]
        indent = orig_line[:len(orig_line) - len(orig_line.lstrip())]
        indented_repl = f"{indent}{repl_code}"
        lines[start_l - 1 : end_l] = [indented_repl]
        applied_descriptions.append(desc)

    return "\n".join(lines), applied_descriptions


class CarbonAuditVisitor(ast.NodeVisitor):
    """AST Visitor that inspects code for carbon/energy anti-patterns."""

    def __init__(self):
        self.issues = []
        self.nested_loop_depth = 0
        self.loop_depth = 0

    def visit_For(self, node):
        self.loop_depth += 1
        if self.loop_depth > 1:
            self.issues.append({
                "line": node.lineno,
                "type": "NESTED_LOOP",
                "severity": "HIGH",
                "description": f"Nested loop detected at line {node.lineno} (Depth {self.loop_depth}). High CPU cycle consumption.",
                "recommendation": "Vectorize operations with NumPy/Polars or use list comprehensions/generators.",
                "estimated_savings_pct": 65
            })

        # Check for list.append inside loops
        for item in ast.walk(node):
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute):
                if item.func.attr == 'append':
                    self.issues.append({
                        "line": item.lineno,
                        "type": "UNVECTORIZED_ACCUMULATION",
                        "severity": "MEDIUM",
                        "description": f"Repeated list.append() inside loop at line {item.lineno}.",
                        "recommendation": "Pre-allocate array with NumPy or use list comprehension to avoid memory reallocations.",
                        "estimated_savings_pct": 40
                    })
                    break

        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_ListComp(self, node):
        # Check for large range in list comprehension
        for gen in node.generators:
            if isinstance(gen.iter, ast.Call) and isinstance(gen.iter.func, ast.Name):
                if gen.iter.func.id == 'range' and gen.iter.args:
                    arg = gen.iter.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)) and arg.value > 10000:
                        self.issues.append({
                            "line": node.lineno,
                            "type": "MEMORY_BLOAT",
                            "severity": "MEDIUM",
                            "range_size": arg.value,
                            "description": f"Large list comprehension with range({arg.value}) at line {node.lineno}.",
                            "recommendation": "Use generator expression () to stream values and reduce RAM energy consumption.",
                            "estimated_savings_pct": 35
                        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Check for recursive function without memoization / cache
        def _is_cache(d):
            if isinstance(d, ast.Call):
                return _is_cache(d.func)
            if isinstance(d, ast.Name):
                return "cache" in d.id.lower()
            if isinstance(d, ast.Attribute):
                return "cache" in d.attr.lower()
            return False

        has_cache = any(_is_cache(dec) for dec in node.decorator_list)
        is_recursive = False
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == node.name:
                    is_recursive = True
                    break

        if is_recursive and not has_cache:
            self.issues.append({
                "line": node.lineno,
                "func_name": node.name,
                "type": "UNCACHED_RECURSION",
                "severity": "HIGH",
                "description": f"Recursive function '{node.name}' at line {node.lineno} without @functools.lru_cache.",
                "recommendation": "Add @functools.lru_cache(maxsize=1024) to prevent duplicate exponential computation.",
                "estimated_savings_pct": 80
            })

        self.generic_visit(node)


def _analyze_list_comp_safety(tree: ast.AST) -> Dict[int, Dict[str, Any]]:
    """
    Analyzes list comprehension assignments to determine whether converting them
    into a generator expression is safe without causing runtime errors (like var[i], len(var)).
    Returns a mapping of lineno -> {'safe': bool, 'var_name': str, 'reason': str}
    """
    safety_map = {}
    
    # 1. Map variable assigned from ListComp
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.ListComp):
                target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                if target_names:
                    var_name = target_names[0]
                    safety_map[node.value.lineno] = {
                        "safe": True,
                        "var_name": var_name,
                        "assign_lineno": node.lineno,
                        "reason": ""
                    }

    # 2. Check for unsafe usages of those variables anywhere in the AST
    for lineno, info in safety_map.items():
        vname = info["var_name"]
        for node in ast.walk(tree):
            # Check indexing: vname[...]
            if isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name) and node.value.id == vname:
                    info["safe"] = False
                    info["reason"] = f"'{vname}' is indexed downstream with []"
                    break

            # Check len(vname)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "len":
                    if any(isinstance(arg, ast.Name) and arg.id == vname for arg in node.args):
                        info["safe"] = False
                        info["reason"] = f"len('{vname}') is called downstream"
                        break
                # Check list mutation / methods: vname.append, sort, pop, etc.
                if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    if node.func.value.id == vname and node.func.attr in ("append", "extend", "insert", "pop", "remove", "sort", "reverse", "index", "count"):
                        info["safe"] = False
                        info["reason"] = f"'{vname}.{node.func.attr}()' is called downstream"
                        break

    return safety_map


def audit_code(code_str: str) -> Dict[str, Any]:
    """
    Perform a static carbon audit on Python source code.
    Returns audit findings, carbon intensity rating (A to F), and potential savings.
    """
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return {
            "valid_syntax": False,
            "error": str(e),
            "carbon_grade": "N/A",
            "issues": []
        }

    visitor = CarbonAuditVisitor()
    visitor.visit(tree)

    # Score calculation
    high_count = sum(1 for i in visitor.issues if i["severity"] == "HIGH")
    med_count = sum(1 for i in visitor.issues if i["severity"] == "MEDIUM")

    score = 100 - (high_count * 25) - (med_count * 10)
    score = max(20, min(100, score))

    if score >= 90:
        grade = "A (Eco-Optimal)"
    elif score >= 75:
        grade = "B (Good Efficiency)"
    elif score >= 60:
        grade = "C (Moderate Footprint)"
    elif score >= 40:
        grade = "D (High Energy Waste)"
    else:
        grade = "F (Severe Carbon Intensity)"

    avg_savings = sum(i["estimated_savings_pct"] for i in visitor.issues) / len(visitor.issues) if visitor.issues else 0

    return {
        "valid_syntax": True,
        "carbon_score": score,
        "carbon_grade": grade,
        "total_issues": len(visitor.issues),
        "issues": visitor.issues,
        "potential_energy_reduction_pct": round(min(85, avg_savings), 1)
    }


def optimize_code(code_str: str) -> Dict[str, Any]:
    """
    Generate an optimized, carbon-efficient version of the input Python code.
    Applies vectorization, generator expressions, caching, and energy-aware patterns.
    """
    audit = audit_code(code_str)
    optimized = code_str

    try:
        tree = ast.parse(code_str)
        safety_map = _analyze_list_comp_safety(tree)
    except Exception:
        safety_map = {}

    improvements = []

    # 1. Add lru_cache only to the specific recursive functions that need it
    rec_issues = [i for i in audit["issues"] if i["type"] == "UNCACHED_RECURSION"]
    if rec_issues:
        if "from functools import lru_cache" not in optimized:
            optimized = "from functools import lru_cache\n" + optimized
        for issue in rec_issues:
            func_name = issue.get("func_name")
            if func_name:
                pattern = rf"(def\s+{re.escape(func_name)}\s*\()"
                # Only wrap if @lru_cache is not already applied
                if re.search(pattern, optimized) and not re.search(rf"@lru_cache[^\n]*\n\s*def\s+{re.escape(func_name)}", optimized):
                    optimized = re.sub(
                        pattern,
                        r"@lru_cache(maxsize=1024)\n\1",
                        optimized,
                        count=1
                    )
                    improvements.append(f"Added @lru_cache(maxsize=1024) to '{func_name}' (eliminates duplicate computations)")

    # 2. Convert large list comprehensions to generator expressions ONLY IF safe
    for issue in audit["issues"]:
        if issue["type"] == "MEMORY_BLOAT":
            lineno = issue.get("line")
            safety_info = safety_map.get(lineno)

            # If safety analysis found downstream indexing / len, DO NOT convert to generator
            if safety_info and not safety_info.get("safe", True):
                vname = safety_info.get("var_name", "variable")
                note = f"# [CarbonIQ] Kept list comprehension for '{vname}' ({safety_info.get('reason', 'subscripted/sized downstream')})"
                if note not in optimized:
                    improvements.append(f"Preserved '{vname}' list comprehension (safe execution: {safety_info.get('reason')})")
                continue

            # Safe to convert: Replace [x for ... in range(...)] with (x for ... in range(...))
            comp_match = re.search(r"\[([^\]]+for\s+[^\]]+in\s+range\([0-9]+\))\]", optimized)
            if comp_match:
                orig = comp_match.group(0)
                gen = f"({comp_match.group(1)})"
                optimized = optimized.replace(orig, gen, 1)
                improvements.append("Converted large in-memory list to generator expression (reduces peak RAM power consumption)")

    # 3. Refactor unvectorized append loops and simple nested loops to list comprehensions
    optimized, loop_improvements = refactor_loops_to_comprehensions(optimized)
    improvements.extend(loop_improvements)

    # 4. Add numpy recommendation hint if high-order nested loops remain
    nested_issues = [i for i in audit["issues"] if i["type"] == "NESTED_LOOP"]
    if nested_issues and not loop_improvements:
        hint = (
            "# [CarbonIQ Hint] For large matrix/array workloads, replace nested loops with NumPy:\n"
            "# e.g. np.dot(A, B) or np.sum(arr * 2) reduces energy consumption by up to 75%.\n"
        )
        if hint not in optimized:
            optimized = hint + optimized
            improvements.append("Added vectorization blueprint for high-cycle loops")

    return {
        "original_grade": audit.get("carbon_grade"),
        "audit": audit,
        "optimized_code": optimized,
        "improvements_applied": improvements,
        "estimated_energy_reduction_pct": audit.get("potential_energy_reduction_pct", 0)
    }
