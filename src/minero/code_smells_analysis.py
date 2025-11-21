from pydriller import Repository
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import ast
import re
from typing import List, Dict
from collections import Counter

console = Console()

def check_code_smells(repo_url: str, commit_hash: str):
    """
    Analisa os arquivos python de um commit de um repositório
    e detecta code smells relacionados à manutenção.

    Args:
        repo_url: O caminho para o repositorio.
        commit_hash: Hash do commit a ser analisado.
    """
    console.print(Panel.fit(
        f"[bold cyan] Analisando Code Smells[/bold cyan]\n"
        f"Repositório: [yellow]{repo_url}[/yellow]\n"
        f"Commit: [green]{commit_hash}[/green]",
        style="blue"
    ))

    commits = Repository(repo_url, single=commit_hash).traverse_commits()
    
    files_analyzed = 0
    total_smells_found = 0
    
    for commit in commits:
        for modified_file in commit.modified_files:

            if not modified_file.filename.endswith('.py'):
                continue

            # Verificar se o arquivo tem código fonte
            if not modified_file.source_code:
                continue

            files_analyzed += 1
            
            # Header do arquivo com estilo similar ao cognitive_analysis
            console.print()
            console.print(f"[bold green]Arquivo:[/bold green] [yellow]{modified_file.filename}[/yellow]")
            console.print()

            smells = detect_code_smells(modified_file.source_code, modified_file.filename)

            if smells:
                total_smells_found += len(smells)
                
                # Agrupar por tipo de smell
                smells_by_type: Dict[str, List[Dict]] = {}
                for smell in smells:
                    smell_type = smell['smell_type']
                    if smell_type not in smells_by_type:
                        smells_by_type[smell_type] = []
                    smells_by_type[smell_type].append(smell)
                
                # Criar tabela com Rich
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Code Smell", style="cyan")
                table.add_column("Qtd", justify="center", style="bold")
                table.add_column("Detalhes", overflow="fold")
                
                # Adicionar linhas com separação visual entre tipos
                smell_types = list(smells_by_type.keys())
                for idx, (smell_type, smell_list) in enumerate(smells_by_type.items()):
                    # Formatar nome do smell
                    smell_names = {
                        'magic_number': 'Magic Numbers',
                        'long_parameter_list': 'Lista de Parâmetros Longa',
                        'large_class': 'God Class',
                        'dead_code': 'Código Morto',
                        'bad_variable_name': 'Nomes Ruins'
                    }
                    smell_name = smell_names.get(smell_type, smell_type.replace('_', ' ').title())
                    count = len(smell_list)
                    
                    # Cor baseada na quantidade
                    if count >= 10:
                        count_color = "red"
                    elif count >= 5:
                        count_color = "yellow"
                    else:
                        count_color = "green"
                    
                    # Mostrar primeiros exemplos de forma mais limpa
                    examples = []
                    for i, smell in enumerate(smell_list[:3]):
                        line_num = smell['line_number']
                        desc = smell['description']
                        if len(desc) > 50:
                            desc = desc[:47] + "..."
                        examples.append(f"• Linha {line_num}: {desc}")
                    
                    if len(smell_list) > 3:
                        examples.append(f"• ... e mais {len(smell_list) - 3} ocorrências")
                    
                    table.add_row(
                        smell_name,
                        f"[{count_color}]{count}[/{count_color}]",
                        "\n".join(examples)
                    )
                    
                    # Adicionar linha separadora horizontal se não for o último item
                    if idx < len(smell_types) - 1:
                        table.add_row("", "", "")
                        table.add_section()
                
                console.print(table)
            else:
                console.print("[green]Nenhum code smell detectado neste arquivo.[/green]")
            
            console.print()  # Linha em branco após cada arquivo
    
    # Summary final
    console.print()
    if files_analyzed > 0:
        if total_smells_found == 0:
            console.print("[bold green]Parabéns! Nenhum code smell detectado.[/bold green]")
        else:
            # Determinar cor baseado na quantidade
            if total_smells_found >= 20:
                summary_color = "red"
                status = "Atenção: muitos problemas detectados"
            elif total_smells_found >= 10:
                summary_color = "yellow" 
                status = "Alguns problemas encontrados"
            else:
                summary_color = "green"
                status = "Poucos problemas encontrados"
            
            console.print(Panel.fit(
                f"[bold]Resumo da Análise[/bold]\n\n"
                f"[bold]Arquivos analisados:[/bold] {files_analyzed}\n"
                f"[bold]Code smells encontrados:[/bold] [{summary_color}]{total_smells_found}[/{summary_color}]\n"
                f"[bold]Status:[/bold] [{summary_color}]{status}[/{summary_color}]",
                style=summary_color,
                title="[bold white]Resultados[/bold white]"
            ))
    else:
        console.print(Panel.fit(
            "Nenhum arquivo Python encontrado no commit.",
            style="yellow",
            title="[bold white]Aviso[/bold white]"
        ))

def detect_code_smells(source_code: str, filename: str) -> List[Dict]:
    """
    Detecta code smells no código fonte Python.

    Args:
        source_code: string com o codigo python completo a ser analisado.
        filename: nome do arquivo analisado, somente para clareza nos logs.
    Returns:
        Uma lista de dicionários com os code smells encontrados.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []
    
    smells = []
    
    # Detectar diferentes tipos de code smells
    smells.extend(detect_magic_numbers(tree, source_code, filename))
    smells.extend(detect_long_parameter_lists(tree, filename))
    smells.extend(detect_large_classes(tree, filename))
    smells.extend(detect_dead_code_comments(source_code, filename))
    smells.extend(detect_bad_variable_names(tree, filename))
    
    return smells

def detect_magic_numbers(tree: ast.AST, source_code: str, filename: str) -> List[Dict]:
    """Detecta números mágicos no código"""
    smells = []
    
    for node in ast.walk(tree):
        # Compatibilidade com Python 3.8+ (ast.Constant) e versões anteriores (ast.Num)
        if isinstance(node, (ast.Constant, ast.Num)):
            value = getattr(node, 'value', getattr(node, 'n', None))
            
            # Ignorar valores comuns que não são considerados magic numbers
            if isinstance(value, (int, float)) and value not in [0, 1, -1, 0.0, 1.0]:
                smells.append({
                    'smell_type': 'magic_number',
                    'line_number': node.lineno,
                    'description': f"Magic number {value}",
                    'file_path': filename
                })
    
    return smells

def detect_long_parameter_lists(tree: ast.AST, filename: str) -> List[Dict]:
    """Detecta funções com muitos parâmetros (>6)"""
    smells = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Contar parâmetros (excluindo *args e **kwargs)
            param_count = len(node.args.args) + len(getattr(node.args, 'posonlyargs', []))
            param_count += len(getattr(node.args, 'kwonlyargs', []))
            
            if param_count > 6:  # Mais restritivo que o comando params (que usa 5)
                smells.append({
                    'smell_type': 'long_parameter_list',
                    'line_number': node.lineno,
                    'description': f"Função '{node.name}' tem {param_count} parâmetros (recomendado: ≤6)",
                    'file_path': filename
                })
    
    return smells

def detect_large_classes(tree: ast.AST, filename: str) -> List[Dict]:
    """Detecta classes grandes (God Classes) com muitos métodos"""
    smells = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Contar métodos na classe
            method_count = 0
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_count += 1
            
            if method_count > 10:  # Limite para God Class
                smells.append({
                    'smell_type': 'large_class',
                    'line_number': node.lineno,
                    'description': f"Classe '{node.name}' tem {method_count} métodos (recomendado: ≤10) - possível God Class",
                    'file_path': filename
                })
    
    return smells

def detect_dead_code_comments(source_code: str, filename: str) -> List[Dict]:
    """Detecta possível código morto comentado"""
    smells = []
    lines = source_code.split('\n')
    
    for i, line in enumerate(lines, 1):
        stripped_line = line.strip()
        
        # Procurar por código comentado (linhas que começam com # seguido de código Python)
        if (stripped_line.startswith('#') and 
            len(stripped_line) > 2 and 
            not stripped_line.startswith('##') and  # Ignorar comentários de documentação
            any(keyword in stripped_line for keyword in ['def ', 'class ', 'import ', 'if ', 'for ', 'while ', 'return '])):
            
            smells.append({
                'smell_type': 'dead_code',
                'line_number': i,
                'description': f"Possível código morto comentado: {stripped_line[:50]}...",
                'file_path': filename
            })
    
    return smells

def detect_bad_variable_names(tree: ast.AST, filename: str) -> List[Dict]:
    """Detecta nomes de variáveis não descritivos"""
    smells = []
    
    # Nomes ruins comuns
    bad_names = ['data', 'info', 'temp', 'tmp', 'var', 'obj', 'item', 'thing', 'stuff']
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            name = node.id
            
            # Variáveis de uma letra (exceto convenções como i, j, k)
            if len(name) == 1 and name not in ['i', 'j', 'k', '_']:
                smells.append({
                    'smell_type': 'bad_variable_name',
                    'line_number': node.lineno,
                    'description': f"Variável de uma letra: '{name}' (não descritiva)",
                    'file_path': filename
                })
            
            # Nomes genéricos não descritivos
            elif name.lower() in bad_names:
                smells.append({
                    'smell_type': 'bad_variable_name',
                    'line_number': node.lineno,
                    'description': f"Nome não descritivo: '{name}' (considere um nome mais específico)",
                    'file_path': filename
                })
    
    return smells