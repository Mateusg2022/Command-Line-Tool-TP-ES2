# Minero - A Command-Line-Tool

Trabalho Prático da disciplina de Engenharia de Software 2

Professor: André Hora

UFMG

Integrantes do grupo:

- Gabriel Coelho dos Santos
- João Correia Costa
- Kayque Meira Siqueira
- Mateus Augusto Gomes

## Explicação do sistema e do objetivo

Este projeto consiste no desenvolvimento de uma ferramenta de linha de comando (CLI) para auxiliar na identificação de possíveis problemas de manutenção de software em repositórios de código Python.
Essa análise é feita em commits de plataformas de hospedagem de código (é necessário a url do repositorio e/ou a hash do commit).

Entre os indicadores analisados, estão:

- Funções Python que ultrapassam o valor de 200 linhas de código

- Funções Python que ultrapassam a quantidade de 5 parâmetros (valor padrão mas alterável)

- Complexidade Cognitiva (métrica quantitativa sobre a complexidade de ler e entender a lógica do código)

- Code Smells (sintomas de código possívelmente pouco legível e/ou difícil de manter)

O sistema poderá realizar avaliações automáticas sobre métricas de manutenção e evolução de software em commits. Pode ser útil como uma segunda verificação antes de, por exemplo, o usuário fazer uma aprovação de uma PR.

## Tecnologias utilizadas

- PyDriller
  - Facilita a extração de métricas de evolução de repositórios Git, como crescimento de linhas de código (LOC) e estatísticas de commits.

- Typer
  - Framework moderno para criar a interface de linha de comando (CLI) do projeto.

- Rich
  - Biblioteca python para adicionar cores, estilos e formatação para saídas de texto no terminal.

## Instalação

Para instalar e executar o software, siga os seguintes passos:

1. Clone o repositório na sua máquina:

    ```sh
    $ git clone https://github.com/Mateusg2022/Minero-cli.git
    ```

2. Instale a ferramenta com o comando abaixo:

    ```sh
    $ pip install .
    ```

3. Utilize o comando a seguir para entender as funcionalidades disponíveis e suas opções:

    ```sh
    $ minero --help
    ```
  
    Ele também pode ser utilizado com os subcomandos para entender seus parâmetros.

## Utilização

### `minero`

Ferramenta CLI para mineração de repositórios de software.

**Utilização**:

```console
$ minero [OPTIONS] COMMAND [ARGS]...
```

**Opções**:

* `--help`: Exibe a mensagem de ajuda.

**Comandos**:

* `generic`: Mostra informações genéricas de um repositório.
* `commits`: Mostra informações dos commits de um repositório.
* `loc`: Emite um alerta caso um arquivo .py de um commit tenha funções que excedam 200 linhas
* `params`: Analisa a quantidade de parâmetros das funções em um commit
* `cog-analysis`: Mostra a complexidade cognitiva das funções Python em um commit específico ou nos últimos 10 commits.
* `code-smells`: Detecta code smells relacionados à manutenção de software em um commit

### `minero generic`

Mostra informações genéricas de um repositório.

**Utilização**:

```console
$ minero generic [OPTIONS] REPO_URL
```

**Argumentos**:

* `REPO_URL`: URL do repositório a ser analisado.  [obrigatório]

**Opções**:

* `--help`: Exibe a mensagem de ajuda.

### `minero commits`

Mostra informações dos commits de um repositório.

**Utilização**:

```console
$ minero commits [OPTIONS] REPO_URL
```

**Arguments**:

* `REPO_URL`: URL do repositório a ser analisado.  [obrigatório]

**Opções**:

* `--help`: Exibe a mensagem de ajuda.

### `minero loc`

Emite um alerta caso um arquivo .py de um commit tenha funções que excedam 200 linhas

**Utilização**:

```console
$ minero loc [OPTIONS] REPO_URL COMMIT_HASH
```

**Arguments**:

* `REPO_URL`: URL do repositório a ser analisado.  [obrigatório]
* `COMMIT_HASH`: Hash do commit a ser analisado.  [obrigatório]

**Opções**:

* `--help`: Exibe a mensagem de ajuda.

### `minero params`

Analisa a quantidade de parâmetros das funções em um commit

**Utilização**:

```console
$ minero params [OPTIONS] REPO_URL COMMIT_HASH [PARAM_LIMIT]
```

**Arguments**:

* `REPO_URL`: URL do repositório a ser analisado.  [obrigatório]
* `COMMIT_HASH`: Hash do commit a ser analisado.  [obrigatório]
* `[PARAM_LIMIT]`: Limite do número de parâmetros a ser utilizado.  [padrão: 5]

**Opções**:

* `--help`: Exibe a mensagem de ajuda.

### `minero cog-analysis`

Mostra a complexidade cognitiva das funções Python em um commit específico ou nos últimos 10 commits.

**Utilização**:

```console
$ minero cog-analysis [OPTIONS] REPO_URL [COMMIT_HASH] [COMPLEXITY_LEVEL_THRESHOLD]
```

**Arguments**:

* `REPO_URL`: URL do repositório a ser analisado.  [obrigatório]
* `[COMMIT_HASH]`: Hash do commit a ser analisado, opcionalmente.
* `[COMPLEXITY_LEVEL_THRESHOLD]`: Limite de complexidade a ser considerado.  [padrão: 12]

**Opções**:

* `--help`: Exibe a mensagem de ajuda.

### `minero code-smells`

Detecta code smells relacionados à manutenção de software em um commit

**Utilização**:

```console
$ minero code-smells [OPTIONS] REPO_URL COMMIT_HASH
```

**Arguments**:

* `REPO_URL`: URL do repositório a ser analisado.  [obrigatório]
* `COMMIT_HASH`: Hash do commit a ser analisado.  [obrigatório]

**Opções**:

* `--help`: Exibe a mensagem de ajuda.


## Testes

Os testes automatizados neste projeto utilizam o `pytest` como framework. Para executá-los basta executar o seguinte comando:

```sh
pytest
```
