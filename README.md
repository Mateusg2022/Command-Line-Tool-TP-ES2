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

    ```shell
    git clone https://github.com/Mateusg2022/Minero-cli.git
    ```

2. Instale a ferramenta com o comando abaixo:

    ```shell
    pip install .
    ```

3. Utilize o comando a seguir para entender as funcionalidades disponíveis e suas opções:

    ```shell
    minero --help
    ```

## Testes

Os testes automatizados neste projeto utilizam o `pytest` como framework. Para executá-los basta executar o seguinte comando:

```shell
pytest
```
