from __future__ import annotations

from typing import Optional, List
import ast
from dataclasses import dataclass

from pydriller import Repository
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

CONTROL_NODES = (
	ast.If,
	ast.For,
	ast.While,
	ast.With,
	ast.Try,
	ast.AsyncFor,
	ast.Match if hasattr(ast, "Match") else (),
)

FLOW_NODES = (
	ast.Return,
	ast.Break,
	ast.Continue,
	ast.Raise,
)

@dataclass
class FunctionComplexity:
    file_path: str
    function_name: str
    complexity: int
    lineno: Optional[int] = None
    end_lineno: Optional[int] = None
    param_count: Optional[int] = None

class CognitiveComplexityVisitor(ast.NodeVisitor):
    """
    Visitor que calcula uma métrica de complexidade cognitiva para uma subárvore AST.

    Algoritmo:
    - cada estrutura de controle (If, For, While, With, Try, Match, AsyncFor) adiciona 1 + nível_de_aninhamento_atual.
    - Cada operador booleano (and/or) dentro de BoolOp aumenta a complexidade pelo número de operadores presentes, isso para penalizar expressões booleanas complexas
    - Instruções que alteram o fluxo (Return, Break, Continue, Raise) adicionam 1.
    - Blocos aninhados aumentam o nível de aninhamento enquanto seus filhos são visitados.
    """

    def __init__(self):
        self.complexity = 0
        self._nesting = 0

    # função generica para os nós de controle
    def _enter_control(self):
        # 1 + penalidade pelo nível de aninhamento atual
        self.complexity += 1 + self._nesting
        self._nesting += 1

    def _exit_control(self):
        self._nesting = max(self._nesting - 1, 0)

    def generic_visit(self, node):
        # para BoolOp dentro de condições, queremos contar operadores booleanos
        # mas evitar contagem dupla tratando BoolOp explicitamente.
        
        super().generic_visit(node)

    def visit_If(self, node: ast.If):
        self._enter_control()
        self._count_boolops_in_node(node.test)
        
        for child in node.body:
            self.visit(child)
        for child in node.orelse:
            self.visit(child)
        self._exit_control()

    def visit_For(self, node: ast.For):
        self._enter_control()
        self.generic_visit(node)
        self._exit_control()

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self._enter_control()
        self.generic_visit(node)
        self._exit_control()

    def visit_While(self, node: ast.While):
        self._enter_control()
        self._count_boolops_in_node(node.test)
        self.generic_visit(node)
        self._exit_control()

    def visit_With(self, node: ast.With):
        self._enter_control()
        self.generic_visit(node)
        self._exit_control()

    def visit_Try(self, node: ast.Try):
        # try/except/finally: conta uma vez e percorre o interior
        self._enter_control()
        
        for child in node.body:
            self.visit(child)
        for h in node.handlers:
            # conta 'except' como uma estrutura de controle também
            self._enter_control()
            if h.type:
                self._count_boolops_in_node(h.type)
            for child in h.body:
                self.visit(child)
            self._exit_control()
        for child in node.orelse:
            self.visit(child)
        for child in node.finalbody:
            self.visit(child)
        self._exit_control()

    if hasattr(ast, "Match"):
        def visit_Match(self, node: ast.Match):
            self._enter_control()
            self.generic_visit(node)
            self._exit_control()

    # instruções que alteram o fluxo adicionam uma pequena penalidade
    def visit_Return(self, node: ast.Return):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Break(self, node: ast.Break):
        self.complexity += 1

    def visit_Continue(self, node: ast.Continue):
        self.complexity += 1

    def visit_Raise(self, node: ast.Raise):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        #a and b and c -> 2 operadores
        num_ops = max(len(node.values) - 1, 0)
        self.complexity += num_ops
        # ainda visita os filhos
        self.generic_visit(node)

    def _count_boolops_in_node(self, node: ast.AST):
        """metodo de teste que percorre uma subárvore e conta nós BoolOp."""
        for n in ast.walk(node):
            if isinstance(n, ast.BoolOp):
                num_ops = max(len(n.values) - 1, 0)
                self.complexity += num_ops


# ---- funções auxiliares ----

def analyze_functions_in_source(source_code: str, filename: str) -> List[FunctionComplexity]:
    """
    Args:
        source_code: string com o código fonte python a ser analisado
        filename: nome do arquivo analisado
    Returns:
        Uma lista com a complexidade por função.
    """
    try:
        tree = ast.parse(source_code)
    except Exception as e:
        console.print(f"[red]Erro ao parsear {filename}: {e}[/red]")
        return []

    results: List[FunctionComplexity] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visitor = CognitiveComplexityVisitor()
            # visita apenas a subárvore da função
            visitor.visit(node)

            results.append(
                FunctionComplexity(
                    file_path=filename,
                    function_name=node.name,
                    complexity=visitor.complexity,
                )
            )

    return results


# ---- função principal ----

def show_cognitive_analysis(repo_url: str, commit_hash: Optional[str] = None, complexity_level_threshold: int = 12) -> None:
    """
    Args:
        source_code: string com o código fonte python a ser analisado
        commit_hash: Hash do commit a ser analisado.
        complexity_level_threshold: nível de complexidade máximo aceitável antes de emitir um alerta.
    Returns:
        A complexidade cognitiva das funções Python no commit especificado ou nos últimos 5 commits.
    """

    complexity_threshold = complexity_level_threshold if isinstance(complexity_level_threshold, int) else 12 # nível de complexidade para alerta

    header = f"Analisando complexidade cognitiva do repositório: {repo_url}"
    if commit_hash:
        header += f" (commit: {commit_hash})"

    console.print(Panel.fit(header, style="blue"))

    # caso commit seja fornecido, analisa só ele
    if commit_hash:
        commits = list(Repository(repo_url, single=commit_hash).traverse_commits())
    else:
        # caso contrario, pegar os últimos 5 commits
        all_commits = list(Repository(repo_url).traverse_commits())
        commits = all_commits[:5]

    for commit_obj in commits:
        console.print(Panel.fit(f"Commit: [green]{commit_obj.hash}[/green] - {commit_obj.msg[:80]}", style="cyan"))

        all_results: List[FunctionComplexity] = []

        for mf in commit_obj.modified_files:
            if not mf.filename.endswith(".py"):
                continue
            if not mf.source_code:
                continue

            file_results = analyze_functions_in_source(mf.source_code, mf.filename)
            all_results.extend(file_results)

        if not all_results:
            console.print("Nenhuma função Python encontrada neste commit.")
            continue

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Arquivo", overflow="fold")
        table.add_column("Função")
        table.add_column("Complexidade")
        table.add_column("Status")

        all_results.sort(key=lambda x: x.complexity, reverse=True)

        for r in all_results:
            print("r.complexity", r.complexity)
            status = "[green]OK[/green]" if int(r.complexity) <= complexity_threshold else "[red]ALERTA[/red]"
            table.add_row(r.file_path, r.function_name, str(r.complexity), status)

        console.print(table)