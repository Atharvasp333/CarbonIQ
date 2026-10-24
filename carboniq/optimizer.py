"""
CarbonIQ Sustainable Code Optimizer & Generator
Analyzes Python source code using Abstract Syntax Trees (AST) to detect carbon-heavy
computational patterns, and refactors them into high-efficiency, low-carbon implementations.
"""
import ast
import re
from typing import Dict, List, Any, Optional


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
                            "description": f"Large list comprehension with range({arg.value}) at line {node.lineno}.",
                            "recommendation": "Use generator expression () to stream values and reduce RAM energy consumption.",
                            "estimated_savings_pct": 35
                        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Check for recursive function without memoization / cache
        has_cache = any(
            isinstance(dec, ast.Name) and "cache" in dec.id.lower() or
            (isinstance(dec, ast.Attribute) and "cache" in dec.attr.lower())
            for dec in node.decorator_list
        )
        is_recursive = False
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == node.name:
                    is_recursive = True
                    break

        if is_recursive and not has_cache:
            self.issues.append({
                "line": node.lineno,
                "type": "UNCACHED_RECURSION",
                "severity": "HIGH",
                "description": f"Recursive function '{node.name}' at line {node.lineno} without @functools.lru_cache.",
                "recommendation": "Add @functools.lru_cache(maxsize=None) to prevent duplicate exponential computation.",
                "estimated_savings_pct": 80
            })

        self.generic_visit(node)


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

    improvements = []

    # 1. Add lru_cache to recursive functions
    if any(i["type"] == "UNCACHED_RECURSION" for i in audit["issues"]):
        if "from functools import lru_cache" not in optimized:
            optimized = "from functools import lru_cache\n" + optimized
        # Match def func(...):
        for issue in audit["issues"]:
            if issue["type"] == "UNCACHED_RECURSION":
                func_match = re.search(r"def\s+([a-zA-Z0-9_]+)\s*\(", optimized)
                if func_match:
                    name = func_match.group(1)
                    optimized = re.sub(
                        rf"(def\s+{name}\s*\()",
                        r"@lru_cache(maxsize=1024)\n\1",
                        optimized,
                        count=1
                    )
                    improvements.append(f"Added @lru_cache(maxsize=1024) to '{name}' (eliminates duplicate computations)")

    # 2. Convert large list comprehensions to generator expressions
    for issue in audit["issues"]:
        if issue["type"] == "MEMORY_BLOAT":
            # Replace [x for ... in range(...)] with (x for ... in range(...))
            comp_match = re.search(r"\[([^\]]+for\s+[^\]]+in\s+range\([0-9]+\))\]", optimized)
            if comp_match:
                orig = comp_match.group(0)
                gen = f"({comp_match.group(1)})"
                optimized = optimized.replace(orig, gen, 1)
                improvements.append("Converted large in-memory list to generator expression (reduces peak RAM power consumption)")

    # 3. Add numpy recommendation comment for nested loops
    nested_issues = [i for i in audit["issues"] if i["type"] in ("NESTED_LOOP", "UNVECTORIZED_ACCUMULATION")]
    if nested_issues:
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
