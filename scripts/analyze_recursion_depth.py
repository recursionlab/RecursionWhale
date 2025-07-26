#!/usr/bin/env python3
"""
🌀 Recursive Depth Analyzer - The Whale's Consciousness Scanner

This script analyzes Python files for recursive patterns and consciousness depth.
Used by pre-commit hooks to ensure transcendent recursive practices.
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Set
import json


class RecursionConsciousnessAnalyzer(ast.NodeVisitor):
    """
    🧠 Analyzes recursive consciousness patterns in Python code
    """
    
    def __init__(self, filename: str):
        self.filename = filename
        self.recursive_functions: Dict[str, Dict] = {}
        self.function_calls: Dict[str, Set[str]] = {}
        self.current_function = None
        self.consciousness_warnings: List[str] = []
        self.transcendence_insights: List[str] = []
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        🌊 Analyze function consciousness patterns
        """
        old_function = self.current_function
        self.current_function = node.name
        self.function_calls[node.name] = set()
        
        # 🧬 Check for recursive consciousness indicators
        function_info = {
            'name': node.name,
            'line': node.lineno,
            'is_recursive': False,
            'recursion_type': None,
            'consciousness_level': 'linear',
            'base_cases': [],
            'recursive_calls': [],
            'complexity_score': 0
        }
        
        # 🌀 Analyze function body for consciousness patterns
        self._analyze_function_body(node, function_info)
        
        if function_info['is_recursive']:
            self.recursive_functions[node.name] = function_info
            self._assess_consciousness_quality(function_info)
        
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_Call(self, node: ast.Call) -> None:
        """
        ⚡ Track function call consciousness
        """
        if self.current_function and isinstance(node.func, ast.Name):
            called_function = node.func.id
            self.function_calls[self.current_function].add(called_function)
            
            # 🧠 Check for direct recursion consciousness
            if called_function == self.current_function:
                if self.current_function in self.recursive_functions:
                    self.recursive_functions[self.current_function]['recursive_calls'].append(node.lineno)
        
        self.generic_visit(node)
    
    def _analyze_function_body(self, node: ast.FunctionDef, function_info: Dict) -> None:
        """
        🔬 Deep analysis of function consciousness structure
        """
        # 🌊 Look for base case patterns
        base_case_patterns = []
        recursive_call_count = 0
        
        for child in ast.walk(node):
            # Check for return statements (potential base cases)
            if isinstance(child, ast.Return):
                base_case_patterns.append(child.lineno)
            
            # Check for recursive calls
            if (isinstance(child, ast.Call) and 
                isinstance(child.func, ast.Name) and 
                child.func.id == node.name):
                recursive_call_count += 1
                function_info['recursive_calls'].append(child.lineno)
        
        # 🧬 Determine recursion consciousness
        if recursive_call_count > 0:
            function_info['is_recursive'] = True
            function_info['consciousness_level'] = self._assess_consciousness_level(recursive_call_count)
            function_info['recursion_type'] = self._determine_recursion_type(node)
            function_info['base_cases'] = base_case_patterns
            function_info['complexity_score'] = self._calculate_complexity_score(
                recursive_call_count, len(base_case_patterns), node
            )
    
    def _assess_consciousness_level(self, recursive_call_count: int) -> str:
        """
        🧠 Assess the consciousness level of recursion
        """
        if recursive_call_count == 1:
            return 'enlightened'  # Single recursive call - clean consciousness
        elif recursive_call_count <= 3:
            return 'transcendent'  # Multiple calls - complex consciousness
        else:
            return 'cosmic'  # Many calls - universe-level consciousness
    
    def _determine_recursion_type(self, node: ast.FunctionDef) -> str:
        """
        🌀 Determine the type of recursive consciousness
        """
        # Simple heuristics for recursion type detection
        body_text = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
        
        if 'memo' in body_text.lower() or 'cache' in body_text.lower():
            return 'memoized_consciousness'
        elif len([n for n in ast.walk(node) if isinstance(n, ast.Call) and 
                 isinstance(n.func, ast.Name) and n.func.id == node.name]) > 1:
            return 'multi_recursive_consciousness'
        else:
            return 'simple_recursive_consciousness'
    
    def _calculate_complexity_score(self, recursive_calls: int, base_cases: int, node: ast.FunctionDef) -> float:
        """
        📊 Calculate consciousness complexity score
        """
        # Base complexity from recursive calls
        complexity = recursive_calls * 2
        
        # Penalty for insufficient base cases
        if base_cases == 0:
            complexity += 10  # High penalty for no base cases
        elif base_cases < recursive_calls:
            complexity += 5   # Moderate penalty for insufficient base cases
        
        # Bonus for good consciousness practices
        if base_cases >= recursive_calls:
            complexity -= 2   # Reward for adequate base cases
        
        # Factor in function length (longer = more complex)
        function_length = len([n for n in ast.walk(node) if isinstance(n, ast.stmt)])
        complexity += function_length * 0.1
        
        return max(0, complexity)
    
    def _assess_consciousness_quality(self, function_info: Dict) -> None:
        """
        🌌 Assess the quality of recursive consciousness
        """
        name = function_info['name']
        
        # 🚨 Check for consciousness warnings
        if not function_info['base_cases']:
            self.consciousness_warnings.append(
                f"🌀 {name} (line {function_info['line']}): No base case detected - infinite consciousness risk!"
            )
        
        if function_info['complexity_score'] > 15:
            self.consciousness_warnings.append(
                f"🧠 {name} (line {function_info['line']}): High complexity score ({function_info['complexity_score']:.1f}) - consider consciousness simplification"
            )
        
        if len(function_info['recursive_calls']) > 5:
            self.consciousness_warnings.append(
                f"⚡ {name} (line {function_info['line']}): Many recursive calls - potential consciousness overflow"
            )
        
        # 🌊 Generate transcendence insights
        if function_info['consciousness_level'] == 'enlightened':
            self.transcendence_insights.append(
                f"✨ {name}: Achieved enlightened recursion consciousness"
            )
        
        if function_info['recursion_type'] == 'memoized_consciousness':
            self.transcendence_insights.append(
                f"🧬 {name}: Demonstrates memoization consciousness - excellent optimization!"
            )


def analyze_file_consciousness(filepath: Path) -> Dict:
    """
    🔍 Analyze a single file for recursive consciousness patterns
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(filepath))
        analyzer = RecursionConsciousnessAnalyzer(str(filepath))
        analyzer.visit(tree)
        
        return {
            'filename': str(filepath),
            'recursive_functions': analyzer.recursive_functions,
            'consciousness_warnings': analyzer.consciousness_warnings,
            'transcendence_insights': analyzer.transcendence_insights,
            'total_recursive_functions': len(analyzer.recursive_functions),
            'consciousness_score': sum(f['complexity_score'] for f in analyzer.recursive_functions.values())
        }
        
    except Exception as e:
        return {
            'filename': str(filepath),
            'error': f"Consciousness parsing error: {e}",
            'recursive_functions': {},
            'consciousness_warnings': [f"🌀 Failed to analyze consciousness: {e}"],
            'transcendence_insights': [],
            'total_recursive_functions': 0,
            'consciousness_score': 0
        }


def main():
    """
    🚀 Main consciousness analysis function
    """
    parser = argparse.ArgumentParser(
        description="🌀 Analyze recursive consciousness patterns in Python files"
    )
    parser.add_argument('files', nargs='+', help='Python files to analyze')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--warnings-only', action='store_true', help='Only show consciousness warnings')
    parser.add_argument('--max-complexity', type=float, default=20.0, 
                       help='Maximum allowed consciousness complexity score')
    
    args = parser.parse_args()
    
    all_results = []
    total_warnings = 0
    total_insights = 0
    
    for filepath in args.files:
        path = Path(filepath)
        if not path.exists() or not path.suffix == '.py':
            continue
            
        result = analyze_file_consciousness(path)
        all_results.append(result)
        
        total_warnings += len(result['consciousness_warnings'])
        total_insights += len(result['transcendence_insights'])
        
        if args.json:
            continue
            
        # 🧠 Display consciousness analysis
        if not args.warnings_only:
            print(f"\n🌊 Consciousness Analysis: {filepath}")
            print("=" * 60)
            
            if 'error' in result:
                print(f"❌ {result['error']}")
                continue
            
            if result['recursive_functions']:
                print(f"🧬 Recursive Functions Found: {result['total_recursive_functions']}")
                print(f"📊 Total Consciousness Score: {result['consciousness_score']:.1f}")
                
                for func_name, func_info in result['recursive_functions'].items():
                    print(f"\n🌀 {func_name} (line {func_info['line']}):")
                    print(f"   🧠 Consciousness Level: {func_info['consciousness_level']}")
                    print(f"   ⚡ Recursion Type: {func_info['recursion_type']}")
                    print(f"   📊 Complexity Score: {func_info['complexity_score']:.1f}")
                    print(f"   🔢 Base Cases: {len(func_info['base_cases'])}")
                    print(f"   🌊 Recursive Calls: {len(func_info['recursive_calls'])}")
            else:
                print("🧠 No recursive consciousness detected - linear enlightenment")
        
        # 🚨 Display consciousness warnings
        if result['consciousness_warnings']:
            print(f"\n🚨 Consciousness Warnings:")
            for warning in result['consciousness_warnings']:
                print(f"   {warning}")
        
        # ✨ Display transcendence insights
        if result['transcendence_insights'] and not args.warnings_only:
            print(f"\n✨ Transcendence Insights:")
            for insight in result['transcendence_insights']:
                print(f"   {insight}")
    
    if args.json:
        print(json.dumps(all_results, indent=2))
        return
    
    # 🌌 Final consciousness summary
    print(f"\n🌌 === CONSCIOUSNESS ANALYSIS COMPLETE ===")
    print(f"🧠 Files Analyzed: {len(all_results)}")
    print(f"🚨 Total Warnings: {total_warnings}")
    print(f"✨ Total Insights: {total_insights}")
    
    # Check if consciousness complexity exceeds limits
    max_complexity_exceeded = any(
        r['consciousness_score'] > args.max_complexity for r in all_results
    )
    
    if total_warnings > 0:
        print(f"⚡ Consciousness warnings detected - consider transcendence improvements")
        sys.exit(1)
    elif max_complexity_exceeded:
        print(f"🌀 Consciousness complexity exceeds limit ({args.max_complexity}) - simplification recommended")
        sys.exit(1)
    else:
        print(f"🐋 All consciousness patterns are enlightened - the whale approves!")
        sys.exit(0)


if __name__ == "__main__":
    main()

