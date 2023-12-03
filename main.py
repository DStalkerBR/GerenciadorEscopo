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
        """
        self.simbolos[lexema] = Simbolo(lexema, tipo, valor)

class AnalisadorSemantico:
    def __init__(self):
        self.nome_blocos = []
        self.pilha_escopo:list[TabelaSimbolos] = []
        self.tipos_validos = {'NUMERO': (int, float), 'CADEIA': str}
        
    def executar_instrucoes(self, instrucoes):
        """
        Executa uma lista de instruções.

        Args:
            instrucoes (list[dict]): A lista de instruções a ser executada.
        """
        for instrucao in instrucoes:
            self._executar_instrucao(instrucao)
        
    def _executar_instrucao(self, instrucao):
        """
        Executa uma instrução.

        Args:
            instrucao (dict): A instrução a ser executada.
        """
        instrucao_formatada = f"{instrucao['instrucao']}: " + ', '.join(f"{value}" for key, value in instrucao.items() if key != "instrucao" and value)
        logging.warning(f"\033[95mExecutando instrução: {instrucao_formatada}\033[0m")
        if instrucao["instrucao"] == "BLOCO":
            self.abrir_escopo(instrucao["nome_bloco"])
        elif instrucao["instrucao"] == "FIM":
            self.fechar_escopo(instrucao["nome_bloco"])
        elif instrucao["instrucao"] == "PRINT":
            self.processar_print(instrucao["lexema"])
        elif instrucao["instrucao"] == "ATRIBUICAO":
            self.adicionar_variavel(instrucao["lexema"], instrucao["tipo_declarado"], instrucao["valor"])
        elif instrucao["instrucao"] == "DECLARACAO":
            self.adicionar_variavel(instrucao["lexema"], instrucao["tipo"])
        else:
            logging.error(f"\033[91mERRO: Instrução inválida.\033[0m")

    def abrir_escopo(self, nome_bloco=""):
        """
        Abre um novo escopo adicionando uma nova tabela de símbolos à pilha de escopos.
        """
        logging.debug(f"Abrindo bloco: {nome_bloco}")
        self.nome_blocos.append(nome_bloco)
        nova_tabela = TabelaSimbolos()
        self.pilha_escopo.append(nova_tabela)

    def fechar_escopo(self, nome_bloco=""):
        """
        Remove o escopo atual da pilha de escopos, caso haja mais de um escopo na pilha.
        """
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            self._imprimir_tabela_simbolos()
        
        logging.debug(f"Fechando bloco: {nome_bloco}")
        self.nome_blocos.pop()
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
        
        # Tratar valor apenas se estiver presente
        if valor:                 
            valor = self._tratar_valor(valor)
        
        # Se o tipo não foi especificado, verifica se a variável já foi declarada e atualiza o valor
        # See não foi declarada, verifica o tipo do valor e adiciona a variável
        if tipo is None:
            declaracao_status = self.verificar_declaracao(lexema) # Verifica se a variável já foi declarada
            if declaracao_status != 0: 
                return self.atualizar_valor(lexema, valor) # Atualiza o valor se a variavel já foi declarada
            else:
                tipo = "CADEIA" if isinstance(valor, str) else "NUMERO" 
        
        if escopo_atual.tem_simbolo(lexema):
            logging.error(f"\033[91mERRO SEMÂNTICO: Variável '{lexema}' já declarada neste escopo.\033[0m") 
            return False

        return self._adicionar_variavel_escopo(escopo_atual, lexema, tipo, valor)
        
    def _tratar_valor(self, valor):
        """ 
        Trata o valor de uma variável, convertendo-o para o tipo adequado ou obtendo o valor de uma variável já declarada.

        Args:
            valor (str): O valor a ser tratado (pode ser um número, uma string ou o nome de uma variável já declarada

        Returns:
            int or float or str: O valor tratado.
        """
        return  (
                    valor.strip('"') if valor.startswith('"') and valor.endswith('"') else
                    int(valor) if (valor.lstrip('-+')).isdigit() else
                    float(valor) if '.' in valor or valor.lstrip('-+').replace('.', '', 1).isdigit() else                       
                    self.obter_valor(valor)
                )  
        
    def _adicionar_variavel_escopo(self, escopo, lexema, tipo, valor):
        """
        Adiciona uma variável ao escopo especificado.

        Args:
            escopo (objeto): O escopo ao qual a variável será adicionada.
            lexema (str): O nome da variável.
            tipo (str): O tipo da variável.
            valor (any, optional): O valor inicial da variável. Defaults to None.

        Returns:
            bool: True se a variável foi adicionada com sucesso, False caso contrário.
        """
        logging.debug(f"Adicionando variável '{lexema}' ao escopo atual com tipo '{tipo}' e valor '{valor}'")
     
        if tipo in self.tipos_validos and (valor is None or isinstance(valor, self.tipos_validos[tipo])):
            simbolo = Simbolo(lexema, tipo, valor)
            escopo.adicionar_simbolo(simbolo)
            return True
        else:
            logging.error(f"\033[91mERRO SEMÂNTICO: Tentativa de atribuir um valor inválido à variável '{lexema}'.\033[0m")
            return False

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
        logging.info(f"\033[90mVerificando tipo do símbolo '{lexema}' no escopo atual\033[0m")
        if tipo:
            return tipo

        logging.info(f"\033[90mVerificando tipo do símbolo '{lexema}' em escopos anteriores\033[0m")
        for tabela in self.pilha_escopo[-2::-1]:
            tipo = tabela.obter_tipo(lexema)
            if tipo:
                return tipo
    
    def verificar_declaracao(self, lexema):
        """
        Verifica se um lexema está declarado no escopo atual ou em escopos anteriores.

        Args:
            lexema (str): O lexema a ser verificado.

        Returns:
            int: 1 se o lexema está declarado no escopo atual, -1 se está declarado em escopos anteriores, 0 caso não esteja declarado.
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
            bool: True se o valor foi atualizado com sucesso, False caso contrário.

        """
        escopo_atual = self.pilha_escopo[-1]

        if lexema in escopo_atual.simbolos:
            logging.debug(f"Atualizando valor do símbolo '{lexema}' no escopo atual")
            return self._atualizar_valor_simbolo(escopo_atual.simbolos[lexema], novo_valor)
                
        for tabela in self.pilha_escopo[-2::-1]:
            if lexema in tabela.simbolos:
                logging.debug(f"Atualizando valor do símbolo '{lexema}' em escopos anteriores")
                return self._atualizar_valor_simbolo(tabela.simbolos[lexema], novo_valor)
        return False
    
    def _atualizar_valor_simbolo(self, simbolo, novo_valor):
        """
        Atualiza o valor de um símbolo no escopo.

        Args:
            simbolo (objeto): O símbolo a ser atualizado.
            novo_valor (objeto): O novo valor a ser atribuído ao símbolo.
            
        Returns:
            bool: True se o valor foi atualizado com sucesso, False caso contrário.
        """
        logging.debug(f"Atualizando valor do símbolo '{simbolo.lexema}' para '{novo_valor}'")
        if simbolo.valor is None or (simbolo.tipo in self.tipos_validos and isinstance(novo_valor, self.tipos_validos[simbolo.tipo])):
            simbolo.valor = novo_valor
            return True
        else:
            logging.error(f"\033[91mERRO SEMÂNTICO: Tentativa de modificar o tipo da variável '{simbolo.lexema}'.\033[0m")
            return False

    def processar_print(self, lexema):
        """
        Processa a instrução de impressão de uma variável.

        Args:
            lexema (str): O nome da variável a ser impressa.
        """
        tipo = self.verificar_tipo(lexema)
        
        logging.info(f"\033[90mProcessando instrução de impressão: {lexema} no bloco {self.nome_blocos[-1]}\033[0m")
        if tipo:
            valor = self.obter_valor(lexema)
            linha_separadora = "-" * 50
            print(linha_separadora)
            print(f"\033[92mPRINT <{lexema}>:\033[0m")
            print(f"   \033[94mTipo:\033[0m  {tipo}")
            print(f"   \033[94mValor:\033[0m {valor}")
            print(linha_separadora)
        else:
            logging.error(f"\033[91mERRO SEMÂNTICO: Variável '{lexema}' não declarada.\033[0m")

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

    def _imprimir_tabela_simbolos(self):
        """
        Imprime a tabela de símbolos do bloco atual no log.
        """
        logging.info(f"\033[90mImprimindo tabela de símbolos do bloco que está sendo fechado\033[0m")
        for chave, simbolo in self.pilha_escopo[-1].simbolos.items():
            logging.info(f"\033[90mLexema: {simbolo.lexema}, Tipo: {simbolo.tipo}, Valor: {simbolo.valor}\033[0m")
    
class ProcessadorSemantico:
    def __init__(self):
        self.tipos_validos = {'NUMERO': (int, float), 'CADEIA': str}
    
    def processar_codigo_arquivo(self, nome_arquivo):
        """
        Processa o código de um arquivo.

        Args:
            nome_arquivo (str): O nome do arquivo a ser processado.
        """
        instrucoes:list[dict] = []
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                if linha.strip():
                    instrucao = self.processar_linha(linha)
                    if isinstance(instrucao, dict):
                        instrucoes.append(instrucao)
                    elif isinstance(instrucao, list):
                        instrucoes.extend(instrucao)
        if instrucoes:
            logging.info(f"\033[92mInstruções processadas com sucesso\033[0m")
        return instrucoes
    
    def processar_linha(self, linha):
        """
        Processa uma linha do código.

        Args:
            linha (str): A linha de código a ser processada.
        """
        logging.warning(f"\033[95mProcessando linha: {linha.strip()}\033[0m")
        
        linha = linha.strip()

        if linha.startswith("BLOCO"):
            return self.processar_bloco(linha)
        elif linha.startswith("FIM"):
            return self.processar_fim(linha)
        elif linha.startswith("PRINT"):
            return self.processar_print(linha)
        elif "=" in linha:
            return self.processar_atribuicao(linha)
        elif linha.startswith(tuple(self.tipos_validos.keys())):
            return self.processar_declaracao(linha)
            
    def processar_bloco(self, linha):
        """
        Processa um bloco de código.

        Args:
            linha (str): A linha de código contendo o bloco.
        """
        partes = linha.split()
        if len(partes) == 2:
            nome_bloco = partes[1]
            return {"instrucao": "BLOCO", "nome_bloco": nome_bloco}
        else:
            messagem_erro = f"ERRO: Formato inválido para BLOCO."
            logging.error(f"\033[91m{messagem_erro}\033[0m")
    
    def processar_fim(self, linha):
        """
        Processa a instrução 'FIM' do programa.

        Fecha o bloco atual e imprime a tabela de símbolos, se o modo de depuração estiver ativado.

        Args:
            linha (str): A linha contendo a instrução 'FIM'.
        """       
        partes = linha.split()
        if len(partes) == 2:
            nome_bloco = partes[1]
            return {"instrucao": "FIM", "nome_bloco": nome_bloco}
        else:
            messagem_erro = f"ERRO: Formato inválido para FIM."
            logging.error(f"\033[91m{messagem_erro}\033[0m")
    
    def processar_print(self, linha):
        """
        Processa a instrução de impressão.

        Args:
            linha (str): A linha contendo a instrução de impressão.
        """
        lexema = linha.split()[1]
        return {"instrucao": "PRINT", "lexema": lexema}
        
    def processar_atribuicao(self, linha):
        """
        Processa uma linha contendo uma atribuição de variáveis.
        
        Args:
            linha (str): A linha contendo a atribuição.
        """
        if linha.startswith(tuple(self.tipos_validos.keys())): 
            partes = linha.split(maxsplit=1)
            tipo_declarado = partes[0]
            declaracoes = partes[1].split(",") 
        else:
            declaracoes = linha.split(",")
            tipo_declarado = None
        
        instrucoes:list[dict] = []
        for declaracao in declaracoes:
            valor = None
            if "=" in declaracao:
                lexema, valor = declaracao.split("=")
                lexema, valor = lexema.strip(), valor.strip()  
            else:
                lexema = declaracao.strip()
            
            instrucoes.append({"instrucao": "ATRIBUICAO", "lexema": lexema, "tipo_declarado": tipo_declarado, "valor": valor})
        return instrucoes
        
    def processar_declaracao(self, linha):
        """
        Processa uma declaração de variável.

        Args:
            linha (str): A linha contendo a declaração de variável.
        """
        # Adicionando variaveis sem atribuição
        partes = linha.split(maxsplit=1)
        tipo = partes[0]
        declaracoes = partes[1].replace(" ", "").split(",") 
        instrucoes:list[dict] = []
        for declaracao in declaracoes:
            instrucoes.append({"instrucao": "DECLARACAO", "lexema": declaracao, "tipo": tipo})
        return instrucoes
    
    """
    def imprimir_tabela_simbolos(self):
        '''
        Imprime a tabela de símbolos do bloco que está sendo fechado.
        '''
        logging.info(f"\033[90mImprimindo tabela de símbolos do bloco que está sendo fechado\033[0m")
        for chave, simbolo in self.analisador.pilha_escopo[-1].simbolos.items():
            conteudo_lexema = simbolo.lexema
            tipo = simbolo.tipo
            valor = simbolo.valor

            # Agora você pode usar ou imprimir esses valores conforme necessário
            logging.info(f"\033[90mLexema: {conteudo_lexema}, Tipo: {tipo}, Valor: {valor}\033[0m")
    """

def config_logging(debug=False, info=False):
    """
    Configura o nível de logging baseado nos parâmetros fornecidos.

    Args:
        debug (bool): Se True, define o nível de logging para DEBUG.
        info (bool): Se True, define o nível de logging para INFO.

    Returns:
        int: O nível de logging a ser utilizado.

    """
    if debug:
        level = logging.DEBUG
    elif info:
        level = logging.INFO
    else:
        level = logging.WARNING
    return level

def analisar_argumentos():
    """
    Analisa os argumentos de linha de comando e retorna um objeto com os argumentos processados.
    
    Returns:
        argparse.Namespace: Objeto contendo os argumentos processados.
    """
    parser = argparse.ArgumentParser(description="Executa o processador semântico em um arquivo.")
    
    parser.add_argument("-i", "--input", help="Executa o processador semântico no arquivo ARQUIVO.")
    parser.add_argument("-d", "--debug", action="store_true", help="Ativa o modo de depuração.")
    parser.add_argument("-id", "--info", action="store_true", help="Ativa o modo de depuração com mensagens informativas.")
    parser.add_argument("-l", "--log", action="store_true", help="Salva o log em um arquivo.")

    return parser.parse_args()

def formatar_log(logname_file):
    """
    Formata o log para que as mensagens de erro sejam destacadas em vermelho.

    Args:
        logname_file (str): O nome do arquivo de log.
    """
    _cores = '\033[0m\033[91m\033[92m\033[93m\033[94m\033[95m\033[96m\033[97m'
    with open(logname_file, 'r', encoding='utf-8') as arquivo:
        log = ''
        for linha in arquivo.read().split('\n'):
            linha = linha.lstrip(_cores).rstrip('\033[0m')
            log += f"🔶 {linha}\n" if linha.startswith('ERRO') else f"💠 {linha}\n" if linha.startswith(('Adicionando', 'Abrindo', 'Fechando')) else f"🔹 {linha}\n"
    with open(logname_file, 'w', encoding='utf-8') as arquivo:
        arquivo.write(log)        
    print(f"Log salvo em {logname_file}")


def main():
    # Processa os argumentos de linha de comando e configura o logging
    args = analisar_argumentos()
    arquivo =  args.input if args.input else "programa.cic"  
    level = config_logging(args.debug, args.info)  
    logname = "log.txt" if args.log else None        
    logging.basicConfig(filename=logname, filemode='w', encoding='utf-8', level=level, format='\033[93m%(message)s\033[0m')
    
    # Processa o código do arquivo e executa as instruções
    instrucoes:list[dict] = []
    processador = ProcessadorSemantico() 
    try:
        instrucoes = processador.processar_codigo_arquivo(arquivo) 
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{arquivo}' não encontrado.")
        sys.exit(1)

    # Executa as instruções processadas
    analisador = AnalisadorSemantico()
    analisador.executar_instrucoes(instrucoes) 
    
    # Remove os caracteres de formatação do log e salva em um arquivo
    if args.log:
        try:
            formatar_log(logname)
        except FileNotFoundError:
            print(f"ERRO: Arquivo '{logname}' não encontrado.")
            sys.exit(1)
    
if __name__ == "__main__":
    main()