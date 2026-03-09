#!/usr/bin/env python3
"""
Python Code Quality & Comment Analyzer
Analyzes Python files and generates quality reports
"""

import re
import sys
import os
import json
from typing import Dict, List

class PythonCodeAnalyzer:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.lines = []
        self.total_lines = 0
        self.comment_lines = 0
        self.functions = []
        self.function_count = 0
        self.snake_case_violations = []
        
    def analyze(self) -> Dict:
        """Main analysis method"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                self.lines = file.readlines()
            
            self.total_lines = len(self.lines)
            self._analyze_comments()
            self._extract_functions()
            self._check_snake_case()
            
            return self._generate_report()
            
        except FileNotFoundError:
            return {"error": f"File not found: {self.filepath}"}
        except Exception as e:
            return {"error": f"Error analyzing file: {str(e)}"}
    
    def _analyze_comments(self):
        """Count comment lines"""
        in_multiline_comment = False
        
        for line in self.lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for multiline comments (""")
            if line.startswith('"""') or line.startswith("'''"):
                if line.count('"""') == 2 or line.count("'''") == 2:
                    # Single line multiline comment
                    self.comment_lines += 1
                else:
                    # Start or end of multiline comment
                    in_multiline_comment = not in_multiline_comment
                    self.comment_lines += 1
            elif in_multiline_comment:
                self.comment_lines += 1
            elif line.startswith('#'):
                self.comment_lines += 1
    
    def _extract_functions(self):
        """Extract all function definitions"""
        function_pattern = r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        
        for i, line in enumerate(self.lines):
            match = re.match(function_pattern, line)
            if match:
                function_name = match.group(1)
                # Skip special methods (__init__, etc.)
                if not (function_name.startswith('__') and function_name.endswith('__')):
                    self.functions.append({
                        'name': function_name,
                        'line': i + 1
                    })
                    self.function_count += 1
    
    def _check_snake_case(self):
        """Check if function names follow snake_case convention"""
        snake_case_pattern = r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$'
        
        for func in self.functions:
            if not re.match(snake_case_pattern, func['name']):
                self.snake_case_violations.append({
                    'name': func['name'],
                    'line': func['line']
                })
    
    def _generate_report(self) -> Dict:
        """Generate the analysis report"""
        comment_ratio = (self.comment_lines / self.total_lines * 100) if self.total_lines > 0 else 0
        
        # Calculate quality score
        score = 100
        if self.total_lines > 0:
            comment_ratio_val = self.comment_lines / self.total_lines
            if comment_ratio_val < 0.1:
                score -= 20
            elif comment_ratio_val < 0.2:
                score -= 10
        
        if self.function_count > 0:
            violation_ratio = len(self.snake_case_violations) / self.function_count
            score -= violation_ratio * 30
        
        score = max(0, min(100, int(score)))
        
        return {
            'file_name': os.path.basename(self.filepath),
            'total_lines': self.total_lines,
            'comment_lines': self.comment_lines,
            'comment_ratio': round(comment_ratio, 2),
            'total_functions': self.function_count,
            'functions': self.functions,
            'snake_case_violations': self.snake_case_violations,
            'quality_score': score
        }

def analyze_python_file(filepath: str) -> Dict:
    """Convenience function to analyze a Python file"""
    analyzer = PythonCodeAnalyzer(filepath)
    return analyzer.analyze()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python code_analyzer.py <python_file.py>")
        sys.exit(1)
    
    result = analyze_python_file(sys.argv[1])
    print(json.dumps(result, indent=2))