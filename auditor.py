import json
import sys
from typing import Dict, List, Any, Tuple, Set


class AuditoriaJson:
    def __init__(self, caminho_original: str, caminho_traduzido: str):
        self.caminho_original = caminho_original
        self.caminho_traduzido = caminho_traduzido
        self.termos_proibidos: List[str] = ["ComprarDesconto", "Pedido de Trabalho"]

    def carregar_arquivos(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Lê os arquivos do disco. 
        Retorna uma Tupla contendo dois Dicionários
        """
        try:
            with open(self.caminho_original, 'r', encoding='utf-8') as arquivo:
                dados_originais = json.load(arquivo)
            
            with open(self.caminho_traduzido, 'r', encoding='utf-8') as arquivo:
                dados_traduzidos = json.load(arquivo)
                
            return dados_originais, dados_traduzidos
            
        except FileNotFoundError as erro:
            print(f"[ERRO]Erro: Arquivo não encontrado - {erro}")
            sys.exit(1)
        except json.JSONDecodeError as erro:
            print(f"[ERRO] Erro: JSON mal formatado - {erro}")
            sys.exit(1)

    def buscar_erros_estruturais(self, original: Dict[str, Any], traduzido: Dict[str, Any], caminho_atual: str = "") -> List[str]:
        """
        Compara recursivamente as chaves e tipos dos dois dicionários.
        Equivalente a percorrer uma árvore de objetos.
        """
        lista_de_erros: List[str] = []
        
       
        chaves_originais: Set[str] = set(original.keys())
        chaves_traduzidas: Set[str] = set(traduzido.keys())

        if chaves_originais != chaves_traduzidas:
            faltando = chaves_originais - chaves_traduzidas
            extras = chaves_traduzidas - chaves_originais
            
            if faltando:
                lista_de_erros.append(f"[ERRO]Chaves Faltando em '{caminho_atual}': {faltando}")
            if extras:
                lista_de_erros.append(f"[ERRO] Chaves Extras (Erro Grave) em '{caminho_atual}': {extras}")

        
        for chave, valor_original in original.items():
            if chave not in traduzido:
                continue

            valor_traduzido = traduzido[chave]
            novo_caminho = f"{caminho_atual}.{chave}" if caminho_atual else chave

            
            if isinstance(valor_original, dict):
                if not isinstance(valor_traduzido, dict):
                    lista_de_erros.append(f"[ERRO] Tipo errado em '{novo_caminho}': Esperava Objeto, recebeu {type(valor_traduzido).__name__}")
                else:
                    
                    erros_filhos = self.buscar_erros_estruturais(valor_original, valor_traduzido, novo_caminho)
                    lista_de_erros.extend(erros_filhos)
            
         
            elif isinstance(valor_original, str):
                self._validar_texto(valor_original, valor_traduzido, novo_caminho)

        return lista_de_erros

    def _validar_texto(self, texto_original: str, texto_traduzido: Any, caminho: str) -> None:
        """Método auxiliar (privado) para validar regras de string."""
        if not isinstance(texto_traduzido, str):
            print(f"[ERRO] Tipo errado em '{caminho}': Esperava String.")
            return

       
        if texto_original == texto_traduzido and len(texto_original) > 10:
            print(f"[INFO] Aviso: Texto não traduzido (igual ao inglês): {caminho}")
        
      
        for termo in self.termos_proibidos:
            if termo.lower() in texto_traduzido.lower():
                print(f"[INFO]  Alerta: Termo proibido '{termo}' encontrado em {caminho}")

    def contar_total_chaves(self, dados: Any) -> int:
        """Conta quantos nós existem na árvore JSON (profundidade total)."""
        contador = 0
        if isinstance(dados, dict):
            for valor in dados.values():
                contador += 1
                contador += self.contar_total_chaves(valor)
        elif isinstance(dados, list):
            for item in dados:
                contador += self.contar_total_chaves(item)
        return contador


if __name__ == "__main__":
    print("Inicio")
    
    
    auditor = AuditoriaJson('en.json', 'pt-BR.json')
    

    json_original, json_traduzido = auditor.carregar_arquivos()
    
    erros = auditor.buscar_erros_estruturais(json_original, json_traduzido)
    
    if erros:
        print(f"\n[Alert] Foram encontrados {len(erros)} erros estruturais:")
        for erro in erros:
            print(erro)
    else:
        print("\n Estrutura aprovada.")

    
    total_en = auditor.contar_total_chaves(json_original)
    total_pt = auditor.contar_total_chaves(json_traduzido)
    
    print(f"\n Nós Originais: {total_en} | Nós Traduzidos: {total_pt}")
    
    if total_en != total_pt or erros:
        sys.exit(1) 
    
    sys.exit(0) 