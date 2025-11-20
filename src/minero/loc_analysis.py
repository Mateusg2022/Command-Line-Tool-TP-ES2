from pydriller.metrics.process.lines_count import LinesCount
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pydriller import Repository

import ast
from typing import List, Dict

console = Console()

def check_function_exceed_limit_size(repo_url, commit_hash):
    """
    Analisa os arquivos python de um commit de um repositório
    e verifica se alguma função tem mais de 200 linhas.

    Args:
        repo_url: O caminho para o repositorio.
        commit_hash: Hash do commit a ser analisado.
    """
    console.print(Panel.fit(
        f"[bold cyan] Analisando evolução de LOC[/bold cyan]\n"
        f"Repositório: [yellow]{repo_url}[/yellow]\n"
        f"Commit: [green]{commit_hash}[/green]",
        style="blue"
    ))

    commits = Repository(repo_url, single=commit_hash).traverse_commits()
    
    for commit in commits:
        for modified_file in commit.modified_files:

            if not modified_file.filename.endswith('.py'):
                continue

            print(f"Arquivo: {modified_file.filename}")
            print(f"Hash do Commit: {commit.hash}")
            
            print("-" * 40)

            long_functions = check_function_sizes(modified_file.source_code, modified_file.filename)

            if long_functions:
                print(f"As seguintes funções em '{modified_file.filename}' excedem 200 linhas:")
                for func in long_functions:
                    print(f"- Função '{func['function_name']}' tem {func['line_count']} linhas (linhas {func['start_line']} a {func['end_line']})")
            else:
                print(f"Nenhuma função em '{modified_file.filename}' excede 200 linhas.")

def check_function_sizes(source_code: str, filename: str) -> List[Dict]:
    """
    Args:
        source_code: string com o codigo python completo a ser analisado.
        filename: nome do arquivo analisado, somente para clareza nos logs.
    Returns:
        Uma lista de dicionários com os resultados para funções que excedem 200 linhas.
    """
    # constroi a AST
    tree = ast.parse(source_code)
    
    results = []
    
    # percorre todos os nós na arvore
    for node in ast.walk(tree):
        # verifica se o nó é uma função ou metodo
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            function_name = node.name
            # calcula o numero de linhas da função
            # node.lineno é o numero da primeira linha
            # node.end_lineno é o numero da ultima linha
            if hasattr(node, 'end_lineno'):
                line_count = node.end_lineno - node.lineno + 1

            if line_count > 200:
                results.append({
                    'function_name': function_name,
                    'line_count': line_count,
                    'start_line': node.lineno,
                    'end_line': node.end_lineno,
                    'file_path': filename
                })
                
    return results 