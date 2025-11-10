from pydriller.metrics.process.lines_count import LinesCount
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pydriller import Repository

import ast
from typing import List, Dict

console = Console()

def analyze_loc(repo_url: str, from_commit: str, to_commit: str):
    console.print(Panel.fit(
        f"[bold cyan] Analisando evolução de LOC[/bold cyan]\n"
        f"Repositório: [yellow]{repo_url}[/yellow]\n"
        f"De: [green]{from_commit[:10]}[/green] → Até: [green]{to_commit[:10]}[/green]",
        style="blue"
    ))

    metric = LinesCount(
        path_to_repo=repo_url,
        from_commit=from_commit,
        to_commit=to_commit
    )

    added_count = metric.count_added()
    added_max = metric.max_added()
    added_avg = metric.avg_added()

    # total de linhas adicionadas
    console.print("\n[bold underline cyan]→ Total de linhas adicionadas:[/bold underline cyan]")
    table_total = Table(show_header=True, header_style="bold magenta")
    table_total.add_column("Arquivo", style="yellow")
    table_total.add_column("Total", style="green")
    for key, value in added_count.items():
        table_total.add_row(key, str(value))
    console.print(table_total)

    # maximo de linhas adicionadas
    console.print("\n[bold underline cyan]→ Máximo de linhas adicionadas por commit:[/bold underline cyan]")
    table_max = Table(show_header=True, header_style="bold magenta")
    table_max.add_column("Arquivo", style="yellow")
    table_max.add_column("Máximo", style="green")
    table_max.add_column("Média", style="cyan")
    table_max.add_column("Aviso", style="red")
    for key, value in added_max.items():
        warning = ""
        if value > (2 * added_avg[key]):
            warning = "[ALERTA] Commit muito grande!"
        table_max.add_row(key, str(value), str(round(added_avg[key], 2)), warning)
        if warning:
            console.print(warning)
    console.print(table_max)

    # media de linhas adicionadas
    console.print("\n[bold underline cyan]→ Média de linhas adicionadas por commit:[/bold underline cyan]")
    table_avg = Table(show_header=True, header_style="bold magenta")
    table_avg.add_column("Arquivo", style="yellow")
    table_avg.add_column("Média", style="cyan")
    for key, value in added_avg.items():
        table_avg.add_row(key, str(round(value, 2)))
    console.print(table_avg)

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
            
            print("Conteúdo do arquivo:")
            print(modified_file.source_code)
            
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

