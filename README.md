# Gerenciador de Escopos

Este é um simples processador semântico implementado em Python para análise semântica de um conjunto de instruções fornecido em um arquivo. O processador utiliza a abordagem de gestão de escopo com pilha, onde cada bloco de código define um novo escopo. 

Ele lê um arquivo de texto contendo código numa linguagem fictícia, analisa o código e executa as instruções correspondentes.

## Características da Linguagem
O processador suporta as seguintes instruções:

- Declaração de variáveis: Você pode declarar variáveis usando as palavras-chave `NUMERO` para números e `CADEIA` para strings. Por exemplo, `NUMERO a = 10` declara uma variável numérica chamada `a` com o valor 10, e `CADEIA x = "Ola mundo"` declara uma variável de string chamada `x` com o valor "Ola mundo".

- Atribuição de variáveis: Você pode atribuir um valor a uma variável usando o operador `=`. Por exemplo, `x = a` atribui o valor da variável `a` à variável `x`.

- Blocos de código: Você pode criar blocos de código usando as palavras-chave `BLOCO` e `FIM`. Variáveis declaradas dentro de um bloco de código são locais para esse bloco e não são acessíveis fora dele.

- Impressão de variáveis: Você pode imprimir o valor de uma variável usando a palavra-chave `PRINT`. Por exemplo, `PRINT a` imprime o valor da variável `a`.

## Funcionalidades
- **Gestão de Escopo:** O processador suporta a criação e fechamento de blocos, mantendo uma tabela de símbolos para cada escopo.

- **Instruções Semânticas:** Suporta instruções semânticas, como declaração de variáveis, atribuições, e impressão de variáveis.

- **Tipos de Dados:** Lida com tipos de dados como números inteiros, números de ponto flutuante e strings.

- **Depuração:** Modos de depuração configuráveis para facilitar a identificação de erros e o rastreamento do fluxo do programa.

## Como Usar
**1. Clonar o repositório** 
```bash
git clone https://github.com/DStalkerBR/GerenciadorEscopo.git
cd GerenciadorEscopo
```

**2. Executar o Programa**
```bash
python main.py [-h] [-i ARQUIVO] [-d] [-id] [-w] [-l]
```


| Opção                   | Descrição                                             |
| ----------------------- | ----------------------------------------------------- |
| -h, --help              | Mostra a mensagem de ajuda e sai.                     |
| -i INPUT, --input INPUT | Executa o processador semântico no arquivo ARQUIVO.   |
| -d, --debug             | Ativa o modo de depuração.                            |
| -id, --info             | Ativa o modo de depuração com mensagens informativas. |
| -w, --warning           | Ativa o modo de depuração com mensagens de aviso.     |
| -l, --log               | Salva o log em um arquivo.                            |                                                    |

## Como funciona

O processador funciona em três etapas principais: análise, execução e gerenciamento de escopo.

Na etapa de análise, o processador lê o arquivo de código linha por linha e divide cada linha em tokens. Um token é uma unidade indivisível de código, como uma palavra-chave, um identificador de variável ou um valor.

Na etapa de execução, o processador percorre a lista de tokens e executa a instrução correspondente para cada um.

Na etapa de gerenciamento de escopo, o processador mantém uma tabela de símbolos que é atualizada a cada abertura e fechamento de escopo, bem como a cada declaração e atribuição de valores. A tabela de símbolos contém, para cada variável, seu lexema, valor e tipo.

O processador também gerencia escopos de variáveis. Cada vez que uma nova variável é declarada, ela é adicionada a um escopo. O escopo é uma estrutura de dados que mantém o controle de todas as variáveis que foram declaradas e seus valores atuais. Quando o processador encontra uma referência a uma variável, ele procura a variável no escopo atual.

Se uma variável é declarada dentro de um bloco de código , ela é adicionada a um novo escopo que é criado para esse bloco de código. Quando o bloco de código termina, o escopo é descartado e todas as variáveis que foram declaradas dentro dele são esquecidas.

O processador também verifica erros semânticos, como tipos incompatíveis e variáveis não declaradas. Quando um erro semântico é encontrado, o processador informa o erro e continua o processamento.

O código de exemplo `programa.cic` demonstra esses conceitos. Ele contém vários blocos de código, cada um com suas próprias variáveis. As variáveis são declaradas, atribuídas e impressas. Note que as variáveis declaradas dentro de um bloco de código não são acessíveis fora desse bloco. Por exemplo, a variável `a` declarada no bloco `_n1_` não é a mesma que a variável `a` declarada no bloco `_principal_`. Cada uma é local para seu próprio bloco e tem seu próprio valor.
