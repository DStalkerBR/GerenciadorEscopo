class Simbolo:
    def __init__(self, lexema, tipo, valor=None):
        self.lexema = lexema
        self.tipo = tipo
        self.valor = valor

class TabelaSimbolos:
    def __init__(self):
        self.simbolos = {}

    def adicionar_simbolo(self, simbolo):
        if simbolo.lexema not in self.simbolos:
            self.simbolos[simbolo.lexema] = simbolo

    def obter_tipo(self, lexema):
        if lexema in self.simbolos:
            return self.simbolos[lexema].tipo
        return None

    def atualizar_valor(self, lexema, novo_valor):
        if lexema in self.simbolos:
            self.simbolos[lexema].valor = novo_valor
    
    def tem_simbolo(self, lexema):
        return lexema in self.simbolos
    
    def substituir_simbolo(self, lexema, tipo, valor):
        self.simbolos[lexema] = Simbolo(lexema, tipo, valor)

class AnalisadorSemantico:
    def __init__(self):
        self.pilha_escopo = [TabelaSimbolos()]

    def abrir_escopo(self):
        nova_tabela = TabelaSimbolos()
        self.pilha_escopo.append(nova_tabela)

    def fechar_escopo(self):
        if len(self.pilha_escopo) > 1:
            self.pilha_escopo.pop()

    
    def adicionar_variavel(self, lexema, tipo, valor=None):
        escopo_atual = self.pilha_escopo[-1]

        if escopo_atual.tem_simbolo(lexema):
            print(f"ERRO SEMÂNTICO: Variável '{lexema}' já declarada neste escopo.")
            return False  

        simbolo = Simbolo(lexema, tipo, valor)
        escopo_atual.adicionar_simbolo(simbolo)
        return True 
   

    def verificar_tipo(self, lexema):
        # verifica o tipo no escopo atual, se nao existir procura nos anterires
        escopo_atual = self.pilha_escopo[-1]
        tipo = escopo_atual.obter_tipo(lexema)
        if tipo:
            return tipo
    
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
        escopo_atual = self.pilha_escopo[-1]
        if escopo_atual.tem_simbolo(lexema):
            return 1
        
        if any(tabela.tem_simbolo(lexema) for tabela in self.pilha_escopo[-2::-1]):
            return -1
        
        return 0

    def atualizar_valor(self, lexema, novo_valor):
        escopo_atual = self.pilha_escopo[-1]

        if lexema in escopo_atual.simbolos:
            return self._atualizar_valor_simbolo(escopo_atual.simbolos[lexema], novo_valor)
            

        for tabela in reversed(self.pilha_escopo[:-1]):
            if lexema in tabela.simbolos:
                return self._atualizar_valor_simbolo(tabela.simbolos[lexema], novo_valor)
    
    def _atualizar_valor_simbolo(self, simbolo, novo_valor):
        if simbolo.valor is None:
            simbolo.valor = novo_valor
        elif simbolo.tipo == 'NUMERO' and isinstance(novo_valor, (int, float)):
            simbolo.valor = novo_valor
        elif simbolo.tipo == 'CADEIA' and isinstance(novo_valor, str):
            simbolo.valor = novo_valor
        else:
            print(f"ERRO SEMÂNTICO: Tentativa de modificar o tipo da variável '{simbolo.lexema}'.")


    def processar_print(self, lexema):
        tipo = self.verificar_tipo(lexema)
        if tipo:
            valor = self.obter_valor(lexema)
            linha_separadora = "-" * 50
            print(linha_separadora)
            print(f"PRINT {lexema}:")
            print(f"   Tipo: {tipo}")
            print(f"   Valor: {valor}")
            print(linha_separadora)
        else:
            print(f"ERRO SEMÂNTICO: Variável '{lexema}' não declarada.")


    def obter_valor(self, lexema):
    # Obtem o valor no escopo atual, se não nos anteriores
        escopo_atual = self.pilha_escopo[-1]
        if escopo_atual.tem_simbolo(lexema) and escopo_atual.simbolos[lexema].valor is not None:
            return escopo_atual.simbolos[lexema].valor
        else:
            for tabela in self.pilha_escopo[-2::-1]:
                if tabela.tem_simbolo(lexema) and tabela.simbolos[lexema].valor is not None:
                    return tabela.simbolos[lexema].valor
        return None
    
# Função para processar o código de um arquivo
def processar_codigo_arquivo(nome_arquivo):
    analisador = AnalisadorSemantico()
    
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        for linha in arquivo:
            processar_linha(analisador, linha)

class ProcessadorSemantico:
    def __init__(self, debug=False):
        self.analisador = AnalisadorSemantico()
        self.debug = debug
    
    def processar_codigo_arquivo(self, nome_arquivo):
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                self.processar_linha(linha)
    
    def processar_linha(self, linha):
        if linha.strip() == "":
            return
        
        if self.debug:
            print("---->Linha: ", linha.strip(" "), end="")
        
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
        partes = linha.split()
        if len(partes) == 2:
            nome_bloco = partes[1]
            if self.debug:
                print(f"Abrindo bloco: {nome_bloco}")
            self.analisador.abrir_escopo()
        else:
            print("ERRO: Formato inválido para BLOCO.")
    
    def processar_fim(self, linha):
        if self.debug:
            self.imprimir_tabela_simbolos()
        
        partes = linha.split()
        if len(partes) == 2:
            nome_bloco = partes[1]
            if self.debug:
                print(f"Fechando bloco: {nome_bloco}")
            self.analisador.fechar_escopo()
        else:
            print("ERRO: Formato inválido para FIM.")
    
    def processar_print(self, linha):
        lexema = linha.split()[1]
        self.analisador.processar_print(lexema)
        
    def processar_atribuicao(self, linha):
        if (linha.startswith("NUMERO") or linha.startswith("CADEIA")):
            partes = linha.split(maxsplit=1)
            tipo_declarado = partes[0]
            tipo = tipo_declarado
            declaracoes = partes[1]
            declaracoes = declaracoes.split(",") 
        else:
            # Tratando declaração sem tipo ou possivel atribuiçao sem declaraçao
            declaracoes = linha.split(",")
            tipo = None
            tipo_declarado = None
            
        for declaracao in declaracoes:
            if "=" in declaracao:
                lexema, valor = declaracao.split("=") 
                lexema = lexema.strip()
                valor = valor.strip()               
                # Tratando o valor
                # Se numero pode ser números inteiros ou reais (ex: 10, 10.0, +10, -1.345) 
                # Se estiver cercado por aspas é uma cadeia                
                if (valor.startswith('"') and valor.endswith('"')):
                    valor = valor.strip('"')
                elif (valor.translate(str.maketrans({'-':'', '+':'', '.':''})).isdigit()):
                     valor = float(valor) if '.' in valor else int(valor)  
                else:
                    valor = self.analisador.obter_valor(valor) 
                
                if (tipo_declarado is not None): # -> Tem tipo declarado?
                    # Se variavel existe no escopo atual: Da erro
                    if (self.analisador.verificar_declaracao(lexema) == 1):
                        print(f"ERRO SEMÂNTICO: Variável '{lexema}' já declarada neste escopo.")
                    # Se não, Se Variavel existe em algum escopo anterior: Cria uma variavel local 
                    else:
                        self.analisador.adicionar_variavel(lexema, tipo_declarado, valor)
                else: # -> Não tem tipo declarado
                    # Se variavel existe no escopo atual: Atualiza valor
                    if (self.analisador.verificar_declaracao(lexema) == 1):
                        self.analisador.atualizar_valor(lexema, valor)
                    # Se não, Se Variavel existe em algum escopo anterior: Cria uma variavel local 
                    elif (self.analisador.verificar_declaracao(lexema) == -1): # Atualiza localmente a variavel tendo o tipo da variavel global 
                        self.analisador.atualizar_valor(lexema, valor)
                    else: # Se não, cria uma variavel local e inferir o tipo
                        if (isinstance(valor, str)):
                            tipo = "CADEIA"
                        elif (isinstance(valor, (int, float))):
                            tipo = "NUMERO"
                        self.analisador.adicionar_variavel(lexema, tipo, valor) 
        
    def processar_declaracao(self, linha):
        # Adicionando variaveis sem atribuiçao
        partes = linha.split()
        tipo = partes[0]
        declaracoes = " ".join(partes[1:])
        declaracoes = declaracoes.replace(" ", "")
        declaracoes = declaracoes.split(",")
        for declaracao in declaracoes:
            self.analisador.adicionar_variavel(declaracao, tipo)
    
    def imprimir_tabela_simbolos(self):
        print("-"*50)
        print (f"Tabela de simbolos do bloco que esta sendo fechado")
        for chave, simbolo in self.analisador.pilha_escopo[-1].simbolos.items():
            conteudo_lexema = simbolo.lexema
            tipo = simbolo.tipo
            valor = simbolo.valor

            # Agora você pode usar ou imprimir esses valores conforme necessário
            print(f"Chave: {chave}, Lexema: {conteudo_lexema}, Tipo: {tipo}, Valor: {valor}")
        print("-"*50)

    
     
            
# Função para processar cada linha do código
def processar_linha___(analisador:AnalisadorSemantico, linha:str):
    #verificar se a linha esta vazia
    if linha.strip() == "":
        return
    print("---->Linha: ", linha.strip(" "), end="")
    linha = linha.strip()
    if linha.startswith("BLOCO"):
        partes = linha.split()
        if len(partes) == 2:
            nome_bloco = partes[1]
            print(f"Abrindo bloco: {nome_bloco}")
            analisador.abrir_escopo()
        else:
            print("ERRO: Formato inválido para BLOCO.")
    elif linha.startswith("FIM"):
        # imprimir o conteudo das variaveis
        print("-"*50)
        print (f"Tabela de simbolos do bloco que esta sendo fechado")
        for chave, simbolo in analisador.pilha_escopo[-1].simbolos.items():
            conteudo_lexema = simbolo.lexema
            tipo = simbolo.tipo
            valor = simbolo.valor

            # Agora você pode usar ou imprimir esses valores conforme necessário
            print(f"Chave: {chave}, Lexema: {conteudo_lexema}, Tipo: {tipo}, Valor: {valor}")
        print("-"*50)
        
        partes = linha.split()
        if len(partes) == 2:
            nome_bloco = partes[1]
            print(f"Fechando bloco: {nome_bloco}")
            analisador.fechar_escopo()
        else:
            print("ERRO: Formato inválido para FIM.")
    elif linha.startswith("PRINT"):
        lexema = linha.split()[1]
        analisador.processar_print(lexema)
    elif "=" in linha:
        # Aqui so trata as possiveis atribuiçoes
        # Gramatica de declaração
        # DEC -> TIPO LIST AT 
        # LIST -> AT , 
        # LIST -> 
        # AT -> ID 
        # AT -> ID = CONST 
        # ID -> tk_identificador 
        # CONST -> tk_numero 
        # CONST -> tk_cadeia 
        # TIPO -> NUMERO 
        # TIPO -> CADEIA
        
        # Exemplos de declaração
        # NUMERO a = 10
        # NUMERO a
        # NUMERO a = 10, b = 20 
        # CADEIA x = "Ola mundo"
        # CADEIA x
        # x= "Ola mundo"
        # x = a (Onde a é outra variavel)     
        if (linha.startswith("NUMERO") or linha.startswith("CADEIA")):
            partes = linha.split(maxsplit=1)
            tipo_declarado = partes[0]
            tipo = tipo_declarado
            declaracoes = partes[1]
            declaracoes = declaracoes.split(",") 
        else:
            # Tratando declaração sem tipo ou possivel atribuiçao sem declaraçao
            declaracoes = linha.split(",")
            tipo = None
            tipo_declarado = None
            
        for declaracao in declaracoes:
            if "=" in declaracao:
                lexema, valor = declaracao.split("=") 
                lexema = lexema.strip()
                valor = valor.strip()               
                # Tratando o valor
                # Se numero pode ser números inteiros ou reais (ex: 10, 10.0, +10, -1.345) 
                # Se estiver cercado por aspas é uma cadeia                
                if (valor.startswith('"') and valor.endswith('"')):
                    valor = valor.strip('"')
                elif (valor.translate(str.maketrans({'-':'', '+':'', '.':''})).isdigit()):
                     valor = float(valor) if '.' in valor else int(valor)  
                else:
                    valor = analisador.obter_valor(valor) 
                
                if (tipo_declarado is not None): # -> Tem tipo declarado?
                    # Se variavel existe no escopo atual: Da erro
                    if (analisador.verificar_declaracao(lexema) == 1):
                        print(f"ERRO SEMÂNTICO: Variável '{lexema}' já declarada neste escopo.")
                    # Se não, Se Variavel existe em algum escopo anterior: Cria uma variavel local 
                    else:
                        analisador.adicionar_variavel(lexema, tipo_declarado, valor)
                else: # -> Não tem tipo declarado
                    # Se variavel existe no escopo atual: Atualiza valor
                    if (analisador.verificar_declaracao(lexema) == 1):
                        analisador.atualizar_valor(lexema, valor)
                    # Se não, Se Variavel existe em algum escopo anterior: Cria uma variavel local 
                    elif (analisador.verificar_declaracao(lexema) == -1): # Atualiza localmente a variavel tendo o tipo da variavel global 
                        analisador.atualizar_valor(lexema, valor)
                    else: # Se não, cria uma variavel local e inferir o tipo
                        if (isinstance(valor, str)):
                            tipo = "CADEIA"
                        elif (isinstance(valor, (int, float))):
                            tipo = "NUMERO"
                        analisador.adicionar_variavel(lexema, tipo, valor) 
 
    elif linha.startswith("NUMERO") or linha.startswith("CADEIA"):
            # Adicionando variaveis sem atribuiçao
            partes = linha.split()
            tipo = partes[0]
            declaracoes = " ".join(partes[1:])
            declaracoes = declaracoes.replace(" ", "")
            declaracoes = declaracoes.split(",")
            for declaracao in declaracoes:
                analisador.adicionar_variavel(declaracao, tipo)

def main():
    procesador = ProcessadorSemantico(debug=False)
    procesador.processar_codigo_arquivo("programa.cic")
    
if __name__ == "__main__":
    main()

        
        


"""
# Exemplo de uso
analisador = AnalisadorSemantico()
analisador.abrir_escopo()

# Bloco _principal_
print('Bloco principal')
analisador.adicionar_variavel('a', 'NUMERO', 10)
analisador.adicionar_variavel('b', 'NUMERO', 20)
analisador.adicionar_variavel('x', 'CADEIA')

analisador.processar_print('b')
analisador.processar_print('a')

analisador.atualizar_valor('x', 'Ola mundo')
analisador.atualizar_valor('x', analisador.obter_valor('a'))
analisador.processar_print('x')

# Bloco _n1_
print('Bloco n1')
analisador.abrir_escopo()
analisador.adicionar_variavel('a', 'CADEIA', 'Compiladores')
analisador.adicionar_variavel('c', 'NUMERO', -0.45)
analisador.processar_print('b')
analisador.processar_print('c')
analisador.fechar_escopo()

# Bloco _n2_
print('Bloco n2')
analisador.abrir_escopo()
analisador.adicionar_variavel('b', 'CADEIA', 'Compiladores')
analisador.processar_print('a')
analisador.processar_print('b')
analisador.atualizar_valor('a', 11)
analisador.adicionar_variavel('a', 'CADEIA', 'Bloco2')
analisador.processar_print('a')
analisador.processar_print('c')  # Erro: Variável 'c' não declarada neste escopo
analisador.abrir_escopo()

# Bloco _n3_
print('Bloco n3')
analisador.adicionar_variavel('a', 'NUMERO', -0.28)
analisador.adicionar_variavel('c', 'NUMERO', -0.28)
analisador.processar_print('a')
analisador.processar_print('b')
analisador.processar_print('c')
analisador.adicionar_variavel('d', 'CADEIA', 'Compiladores')
analisador.processar_print('d')
analisador.adicionar_variavel('e', 'CADEIA', analisador.obter_valor('d'))
analisador.processar_print('e')

analisador.fechar_escopo()  # Fecha _n3_
analisador.fechar_escopo()  # Fecha _n2_

analisador.processar_print('c')
analisador.processar_print('a')

analisador.fechar_escopo()  # Fecha _principal_
"""