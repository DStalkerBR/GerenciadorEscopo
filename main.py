import logging
import sys
import argparse

class Simbolo:
    def __init__(self, lexema, tipo, valor=None):
        self.lexema = lexema
        self.tipo = tipo
        self.valor = valor

class TabelaSimbolos:
    def __init__(self):
        self.simbolos = {}

    def adicionar_simbolo(self, simbolo):
        """
        Adiciona um símbolo ao gerenciador de escopo.

        Args:
            simbolo: O símbolo a ser adicionado.

        Returns:
            None
        """
        if simbolo.lexema not in self.simbolos:
            self.simbolos[simbolo.lexema] = simbolo

    def obter_tipo(self, lexema):
        """
        Obtém o tipo de um símbolo na tabela de símbolos.

        Args:
            lexema: O lexema do símbolo.

        Returns:
            O tipo do símbolo, ou None se o símbolo não estiver na tabela.
        """
        if lexema in self.simbolos:
            return self.simbolos[lexema].tipo
        return None

    def atualizar_valor(self, lexema, novo_valor):
        """
        Atualiza o valor de um símbolo na tabela de símbolos.

        Args:
            lexema: O lexema do símbolo.
            novo_valor: O novo valor do símbolo.

        Returns:
            None
        """
        if lexema in self.simbolos:
            self.simbolos[lexema].valor = novo_valor
    
    def tem_simbolo(self, lexema):
        """
        Verifica se um símbolo está presente na tabela de símbolos.

        Args:
            lexema: O lexema do símbolo.

        Returns:
            True se o símbolo estiver presente, False caso contrário.
        """
        return lexema in self.simbolos
    
    def substituir_simbolo(self, lexema, tipo, valor):
        """
        Substitui um símbolo na tabela de símbolos.

        Args:
            lexema: O lexema do símbolo.
            tipo: O tipo do símbolo.
            valor: O valor do símbolo.

        Returns:
            None
        """
        self.simbolos[lexema] = Simbolo(lexema, tipo, valor)

class AnalisadorSemantico:
    def __init__(self):
        self.pilha_escopo = [TabelaSimbolos()]

    def abrir_escopo(self):
        """
        Abre um novo escopo adicionando uma nova tabela de símbolos à pilha de escopos.
        """
        nova_tabela = TabelaSimbolos()
        self.pilha_escopo.append(nova_tabela)

    def fechar_escopo(self):
        """
        Remove o escopo atual da pilha de escopos, caso haja mais de um escopo na pilha.
        """
        if len(self.pilha_escopo) > 1:
            self.pilha_escopo.pop()

    
    def adicionar_variavel(self, lexema, tipo, valor=None):
        """
        Adiciona uma variável ao escopo atual.

        Args:
            lexema (str): O nome da variável.
            tipo (str): O tipo da variável.
            valor (any, optional): O valor inicial da variável. Defaults to None.

        Returns:
            bool: True se a variável foi adicionada com sucesso, False caso contrário.
        """
        escopo_atual = self.pilha_escopo[-1]

        if escopo_atual.tem_simbolo(lexema):
            print(f"ERRO SEMÂNTICO: Variável '{lexema}' já declarada neste escopo.")
            return False  

        logging.debug(f"Adicionando variável '{lexema}' ao escopo atual com tipo '{tipo}' e valor '{valor}'")
        simbolo = Simbolo(lexema, tipo, valor)
        escopo_atual.adicionar_simbolo(simbolo)
        return True
   

    def verificar_tipo(self, lexema):
        """
        Verifica o tipo de um lexema no escopo atual e nos escopos anteriores.

        Args:
            lexema (str): O lexema a ser verificado.

        Returns:
            str or None: O tipo do lexema, se encontrado. Caso contrário, retorna None.
        """
        escopo_atual = self.pilha_escopo[-1]
        tipo = escopo_atual.obter_tipo(lexema)
        # cinza
        logging.info(f"\033[90mVerificando tipo do símbolo '{lexema}' no escopo atual\033[0m")
        if tipo:
            return tipo

        logging.info(f"\033[90mVerificando tipo do símbolo '{lexema}' em escopos anteriores\033[0m")
        for tabela in self.pilha_escopo[-2::-1]:
            tipo = tabela.obter_tipo(lexema)
            if tipo:
                return tipo

        return None
    
    def verificar_declaracao(self, lexema):
        """
        Verifica se um lexema está declarado no escopo atual ou em escopos anteriores.

        Args:
            lexema (str): O lexema a ser verificado.

        Returns:
            int: 1 se o lexema está declarado no escopo atual, -1 se está declarado em escopos anteriores, 0 caso contrário.
        """
        logging.debug(f"\033[90mVerificando declaração do símbolo '{lexema}' no escopo atual\033[0m")
        escopo_atual = self.pilha_escopo[-1]
        if escopo_atual.tem_simbolo(lexema):
            return 1
        
        logging.debug(f"\033[90mVerificando declaração do símbolo '{lexema}' em escopos anteriores\033[0m")
        if any(tabela.tem_simbolo(lexema) for tabela in self.pilha_escopo[-2::-1]):
            return -1
        
        return 0

    def atualizar_valor(self, lexema, novo_valor):
        """
        Atualiza o valor de um símbolo no escopo atual ou em escopos anteriores.

        Args:
            lexema (str): O lexema do símbolo a ser atualizado.
            novo_valor: O novo valor a ser atribuído ao símbolo.

        Returns:
            O resultado da atualização do valor do símbolo.

        """
        escopo_atual = self.pilha_escopo[-1]

        if lexema in escopo_atual.simbolos:
            logging.debug(f"Atualizando valor do símbolo '{lexema}' no escopo atual")
            return self._atualizar_valor_simbolo(escopo_atual.simbolos[lexema], novo_valor)
                

        for tabela in reversed(self.pilha_escopo[:-1]):
            if lexema in tabela.simbolos:
                logging.debug(f"Atualizando valor do símbolo '{lexema}' em escopos anteriores")
                return self._atualizar_valor_simbolo(tabela.simbolos[lexema], novo_valor)
    
    def _atualizar_valor_simbolo(self, simbolo, novo_valor):
        """
        Atualiza o valor de um símbolo no escopo.

        Args:
            simbolo (objeto): O símbolo a ser atualizado.
            novo_valor (objeto): O novo valor a ser atribuído ao símbolo.

        Returns:
            None
        """
        # if self.debug:
        logging.debug(f"Atualizando valor do símbolo '{simbolo.lexema}' para '{novo_valor}'")
            # print(f"\033[93mAtualizando valor do símbolo '{simbolo.lexema}' para '{novo_valor}'\033[0m")
        if simbolo.valor is None:
            simbolo.valor = novo_valor
        elif simbolo.tipo == 'NUMERO' and isinstance(novo_valor, (int, float)):
            simbolo.valor = novo_valor
        elif simbolo.tipo == 'CADEIA' and isinstance(novo_valor, str):
            simbolo.valor = novo_valor
        else:
            mensagem_erro = f"ERRO SEMÂNTICO: Tentativa de modificar o tipo da variável '{simbolo.lexema}'."
            print(f"\033[91m{mensagem_erro}\033[0m")


    def processar_print(self, lexema):
        """
        Processa a instrução de impressão de uma variável.

        Args:
            lexema (str): O nome da variável a ser impressa.

        Returns:
            None
        """
        tipo = self.verificar_tipo(lexema)
        if tipo:
            valor = self.obter_valor(lexema)
            linha_separadora = "-" * 50
            print(linha_separadora)
            print(f"\033[92mPRINT <{lexema}>:\033[0m")
            print(f"   \033[94mTipo:\033[0m  {tipo}")
            print(f"   \033[94mValor:\033[0m {valor}")
            print(linha_separadora)
        else:
            messagem_erro = f"ERRO SEMÂNTICO: Variável '{lexema}' não declarada."
            print(f"\033[91m{messagem_erro}\033[0m")

    def obter_valor(self, lexema):
        """
        Obtém o valor de um símbolo no escopo atual ou nos escopos anteriores.

        Args:
            lexema (str): O lexema do símbolo a ser obtido.

        Returns:
            O valor do símbolo, se encontrado. Caso contrário, retorna None.
        """
        escopo_atual = self.pilha_escopo[-1]
        logging.info(f"\033[90mObtendo valor do símbolo '{lexema}' no escopo atual\033[0m")
        if escopo_atual.tem_simbolo(lexema) and escopo_atual.simbolos[lexema].valor is not None:
            return escopo_atual.simbolos[lexema].valor
        else:
            logging.info(f"\033[90mObtendo valor do símbolo '{lexema}' em escopos anteriores\033[0m")
            for tabela in self.pilha_escopo[-2::-1]:
                if tabela.tem_simbolo(lexema) and tabela.simbolos[lexema].valor is not None:
                    return tabela.simbolos[lexema].valor
        return None
    
class ProcessadorSemantico:
    def __init__(self):
        self.analisador = AnalisadorSemantico()
        self.bloco_atual = None
    
    def processar_codigo_arquivo(self, nome_arquivo):
        """
        Processa o código de um arquivo.

        Args:
            nome_arquivo (str): O nome do arquivo a ser processado.

        Returns:
            None
        """
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                self.processar_linha(linha)
    
    def processar_linha(self, linha):
        """
        Processa uma linha do código.

        Args:
            linha (str): A linha de código a ser processada.

        Returns:
            None
        """
        if linha.strip() == "":
            return
        
        logging.warning(f"\033[95mProcessando linha: {linha.strip()}\033[0m")
        
        linha = linha.strip()

        if linha.startswith("BLOCO"):
            self.processar_bloco(linha)
        elif linha.startswith("FIM"):
            self.processar_fim(linha)
        elif linha.startswith("PRINT"):
            self.processar_print(linha)
        elif "=" in linha:
            self.processar_atribuicao(linha)
        elif linha.startswith("NUMERO") or linha.startswith("CADEIA"):
            self.processar_declaracao(linha)
            
    def processar_bloco(self, linha):
        """
        Processa um bloco de código.

        Args:
            linha (str): A linha de código contendo o bloco.

        Returns:
            None
        """
        partes = linha.split()
        if len(partes) == 2:
            nome_bloco = partes[1]
            logging.debug(f"Abrindo bloco: {nome_bloco}")
            self.bloco_atual = nome_bloco
            self.analisador.abrir_escopo()
        else:
            messagem_erro = f"ERRO: Formato inválido para BLOCO."
            print(f"\033[91m{messagem_erro}\033[0m")
    
    def processar_fim(self, linha):
        """
        Processa a instrução 'FIM' do programa.

        Fecha o bloco atual e imprime a tabela de símbolos, se o modo de depuração estiver ativado.

        Args:
            linha (str): A linha contendo a instrução 'FIM'.

        Returns:
            None
        """
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            self.imprimir_tabela_simbolos()
        
        partes = linha.split()
        if len(partes) == 2:
            nome_bloco = partes[1]
            logging.debug(f"Fechando bloco: {nome_bloco}")
            self.analisador.fechar_escopo()
        else:
            messagem_erro = f"ERRO: Formato inválido para FIM."
            print(f"\033[91m{messagem_erro}\033[0m")
    
    def processar_print(self, linha):
        """
        Processa a instrução de impressão.

        Args:
            linha (str): A linha contendo a instrução de impressão.

        Returns:
            None
        """
        lexema = linha.split()[1]
        logging.info(f"\033[90mProcessando instrução de impressão: {lexema}\033[0m")
        self.analisador.processar_print(lexema)
        
    def processar_atribuicao(self, linha):
        """
        Processa uma linha contendo uma atribuição de variáveis.
        
        Args:
            linha (str): A linha contendo a atribuição.
        """
        if linha.startswith(("NUMERO", "CADEIA")):
            partes = linha.split(maxsplit=1)
            tipo_declarado = partes[0]
            declaracoes = partes[1].split(",") 
        else:
            declaracoes = linha.split(",")
            tipo_declarado = None
        
        for declaracao in declaracoes:
            if "=" in declaracao:
                lexema, valor = declaracao.split("=")
                lexema, valor = lexema.strip(), valor.strip()

                # Tratando o valor                  
                valor = (
                        valor.strip('"') if valor.startswith('"') and valor.endswith('"') else
                        int(valor) if (valor.lstrip('-+')).isdigit() else
                        float(valor) if '.' in valor or valor.lstrip('-+').replace('.', '', 1).isdigit() else                       
                        self.analisador.obter_valor(valor)
                )

                # Verificar declaração e tipo
                declaracao_status = self.analisador.verificar_declaracao(lexema) # Verifica se a variável já foi declarada
                if tipo_declarado:  # Se o tipo foi declarado
                    if declaracao_status == 1: # Se a variável já foi declarada neste escopo
                        mensagem_erro = f"ERRO SEMÂNTICO: Variável '{lexema}' já declarada neste escopo."
                        print(f"\033[91m{mensagem_erro}\033[0m")
                    else: # Se a variável não foi declarada neste escopo
                        self.analisador.adicionar_variavel(lexema, tipo_declarado, valor)
                else: # Se o tipo não foi declarado
                    if declaracao_status != 0: # Se a variável já foi declarada no escopo atual ou em escopos anteriores
                        self.analisador.atualizar_valor(lexema, valor) # Atualiza o valor da variável
                    else: # Se a variável não foi declarada
                        tipo = "CADEIA" if isinstance(valor, str) else "NUMERO" # Define o tipo da variável
                        self.analisador.adicionar_variavel(lexema, tipo, valor) # Adiciona a variável ao escopo

        
    def processar_declaracao(self, linha):
        """
        Processa uma declaração de variável.

        Args:
            linha (str): A linha contendo a declaração de variável.
        """
        # Adicionando variaveis sem atribuição
        partes = linha.split()
        tipo = partes[0]
        declaracoes = " ".join(partes[1:])
        declaracoes = declaracoes.replace(" ", "")
        declaracoes = declaracoes.split(",")
        for declaracao in declaracoes:
            self.analisador.adicionar_variavel(declaracao, tipo)
    
    def imprimir_tabela_simbolos(self):
        """
        Imprime a tabela de símbolos do bloco que está sendo fechado.
        """
        print("-"*50)
        print (f"Tabela de simbolos do bloco que esta sendo fechado")
        for chave, simbolo in self.analisador.pilha_escopo[-1].simbolos.items():
            conteudo_lexema = simbolo.lexema
            tipo = simbolo.tipo
            valor = simbolo.valor

            # Agora você pode usar ou imprimir esses valores conforme necessário
            print(f"Chave: {chave}, Lexema: {conteudo_lexema}, Tipo: {tipo}, Valor: {valor}")
        print("-"*50)  

def config_logging(debug=False, info=False):
    if debug:
        level = logging.DEBUG
    elif info:
        level = logging.INFO
    else:
        level = logging.WARNING
    return level

def analisar_argumentos():
    parser = argparse.ArgumentParser(description="Executa o processador semântico em um arquivo.")
    
    parser.add_argument("-i", "--input", help="Executa o processador semântico no arquivo ARQUIVO.")
    parser.add_argument("-d", "--debug", action="store_true", help="Ativa o modo de depuração.")
    parser.add_argument("-id", "--info", action="store_true", help="Ativa o modo de depuração com mensagens informativas.")

    return parser.parse_args()


def main():
    args = analisar_argumentos()
    config_logging(args.debug, args.info)
    arquivo =  args.input if args.input else "programa.cic"  
    level = config_logging(args.debug, args.info)  
        
    logging.basicConfig(level=level, format='\033[93m%(message)s\033[0m')    
    
    procesador = ProcessadorSemantico() # Instancia o processador semântico
    try:
        procesador.processar_codigo_arquivo(arquivo) # Processa o código do arquivo
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{arquivo}' não encontrado.")
        sys.exit(1)
    
if __name__ == "__main__":
    main()