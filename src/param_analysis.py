from pydriller.metrics.process.lines_count import LinesCount
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pydriller import Repository

import ast
from typing import List, Dict

console = Console()

def check_functions_exceed_param_limit(repo_url, commit_hash):
    """
    Analisa os arquivos Python de um commit de um repositório e verifica se
    alguma função tem muitos parâmetros.

    Args:
    repo_url: O caminho para o repositorio.
    commit_hash: Hash do commit a ser analisado.
    """

    console.print(Panel.fit(
        f"[bold cyan] Analisando quantidade de parâmetros das funções[/bold cyan]\n"
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
            
            accused = check_functions_num_params(modified_file.source_code, modified_file.filename)

            if accused:
                print(f"As seguintes funções em '{modified_file.filename}' possuem mais de 5 parâmetros:")
                for func in accused:
                    print(f"- Função '{func['function_name']}' tem {func['param_count']} parâmetros")
            else:
                print(f"Nenhuma função em '{modified_file.filename}' excede 5 parâmetros.")


def check_functions_num_params(source_code: str, filename: str) -> List[Dict]:
    """
    Args:
        source_code: string com o código fonte python a ser analisado
        filename: nome do arquivo analisado
    Returns:
        Uma lista de dicionários com os resultados para funções que excedem 200 linhas.
    """
    # constroi a AST
    tree = ast.parse(source_code)
    
    results = []
    
    # percorre todos os nós na arvore
    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            function_name = node.name

            # seleciona todos os parâmetros que não são de quantidade variável
            # (como *args e **kwargs seriam, por ex.)
            non_variable_params = getattr(node.args, "posonlyargs", []) + getattr(node.args, "args", []) + getattr(node.args, "kwonlyargs", [])
            param_count = len(non_variable_params)
                
            if param_count > 1:
                results.append({
                    "function_name": function_name,
                    "param_count": param_count,
                    "file_path": filename
                })
                
    return results 

