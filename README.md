# Busca de Processos Judiciais

## Descrição
Este projeto busca nos tribunais os processos listados em uma tabela Excel e faz requisições pela API DataJud do 
Conselho Nacional de Justiça (CNJ) para retornar o último andamento registrado de cada processo.
Por padrão e por conta de testes esta pesquisando pelo Tribunal de Justiça de São Paulo, é só trocar a sigla pelo 
tribunal correspondente.

## Funcionalidades
- **Leitura de Tabela Excel**: Importa uma tabela Excel contendo os números dos processos.
- **Consulta API DataJud**: Faz requisições à API DataJud para obter o último andamento registrado de cada processo.
- **Atualização Automática**: A cada vez que o código funciona, cria uma tabela nova com os andamentos atuais e se usar
  o mesmo nome é só substituir o arquivo original.

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/LeMorelli-py/Autom.-Juridica

Caso nao tenha uma dessas bibliotecas:

instale com:

ex: pip install nome_da_biblioteca

## Bibliotecas necessárias
- pandas
- requests
- json
- tkinter
    - file dialog, messagebox, ttk
- ttkthemes
- sys
- warnings
- concurrent.futures


Autor: Leandro Coneglian Morelli
