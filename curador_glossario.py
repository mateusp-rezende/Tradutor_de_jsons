import json
import os
import sys


ARQUIVO_EN      = 'en.json'         # (Texto Original)
ARQUIVO_PT      = 'pt-BR.json'      # Tradução
GLOSSARIO_PT    = 'glossario_pt.json' # Destino

ARQUIVO_ES      = 'es.json'
GLOSSARIO_ES    = 'glossario_es.json'

MAX_PALAVRAS = 10 # Máximo de palavras para considerar um termo no glossário

def carregar_json(caminho):
    if not os.path.exists(caminho):
        return {}
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

def salvar_json(dados, caminho):
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"[SALVO] {caminho}")
    except Exception as e:
        print(f"[ERRO] {e}")

def extrair_pares_recursivo(obj_en, obj_trad, lista_pares):
    """
    Navega nos dois arquivos simultaneamente.
    Ignora as chaves (IDs). Foca no CONTEÚDO.
    """
    if isinstance(obj_en, dict) and isinstance(obj_trad, dict):
        for k, v_en in obj_en.items():
            if k in obj_trad:
                extrair_pares_recursivo(v_en, obj_trad[k], lista_pares)
                
    elif isinstance(obj_en, list) and isinstance(obj_trad, list):
        tamanho = min(len(obj_en), len(obj_trad))
        for i in range(tamanho):
            extrair_pares_recursivo(obj_en[i], obj_trad[i], lista_pares)
            
    elif isinstance(obj_en, str) and isinstance(obj_trad, str):
        texto_ingles = obj_en.strip()
        texto_traducao = obj_trad.strip()
        
      
        if (texto_ingles and 
            not texto_ingles.isnumeric() and 
            len(texto_ingles.split()) <= MAX_PALAVRAS and
            texto_ingles != texto_traducao): 
            
           
            lista_pares.append((texto_ingles, texto_traducao))

def processar_curadoria(nome_idioma, arq_trad, arq_glossario, json_en):
    print(f"\n{'='*60}")
    print(f"   CURADORIA: {nome_idioma.upper()}")
    print(f"   Mapeando: '{ARQUIVO_EN}' + '{arq_trad}' -> '{arq_glossario}'")
    print(f"{'='*60}")

    json_trad = carregar_json(arq_trad)
    if not json_trad:
        print(f"Arquivo {arq_trad} não encontrado.")
        return

  
    pares_encontrados = []
    extrair_pares_recursivo(json_en, json_trad, pares_encontrados)
    

    glossario = carregar_json(arq_glossario)
    
    
    glossario_keys = set(k.lower() for k in glossario.keys())
    
    novos_candidatos = []
    
   
    for ingles, traducao in pares_encontrados:
        chave_lower = ingles.lower()
        
       
        if chave_lower not in glossario_keys:
         
            if not any(x[0].lower() == chave_lower for x in novos_candidatos):
                novos_candidatos.append((ingles, traducao))
        else:
           
            traducao_existente = glossario.get(chave_lower, "")
            if traducao_existente.lower() != traducao.lower():
                
                pass

    total = len(novos_candidatos)
    if total == 0:
        print(">> Glossário já contém todos os termos encontrados.")
        return

    print(f">> {total} novos termos identificados (Inglês -> Tradução).")
    print(">> Comandos: [y]Sim | [n]Não | [e]Editar | [a]Aprovar Resto | [s]Sair\n")

    aprovados = 0
    modo_turbo = False

    for i, (ingles, traducao) in enumerate(novos_candidatos):
        if modo_turbo:
            glossario[ingles.lower()] = traducao
            aprovados += 1
            print(f"[{i+1}/{total}]'{ingles}' -> '{traducao}'")
            continue

        print("-" * 50)
        print(f"ITEM [{i+1}/{total}]")
        print(f"   INGLÊS:    {ingles}")
        print(f"   TRADUÇÃO:  {traducao}")
        
        while True:
            op = input("   Adicionar ao Glossário? ").lower().strip()
            
            if op == 'y' or op == '':
                glossario[ingles.lower()] = traducao
                aprovados += 1
                print(" OK.")
                break
            elif op == 'n':
                print(" Ignorado.")
                break
            elif op == 'e':
                nova = input(f"   Corrigir tradução para '{ingles}': ").strip()
                if nova:
                    glossario[ingles.lower()] = nova
                    aprovados += 1
                    print(f"  Salvo: {nova}")
                break
            elif op == 'a':
                modo_turbo = True
                glossario[ingles.lower()] = traducao
                aprovados += 1
                print(" Aprovando tudo...")
                break
            elif op == 's':
                if aprovados > 0: salvar_json(glossario, arq_glossario)
                sys.exit()
            else:
                print("Opção inválida.")

    if aprovados > 0:
        salvar_json(glossario, arq_glossario)


if __name__ == "__main__":
    json_en = carregar_json(ARQUIVO_EN)
    if not json_en:
        print(f"Erro crítico: {ARQUIVO_EN} não encontrado.")
        sys.exit()

    processar_curadoria('Português', ARQUIVO_PT, GLOSSARIO_PT, json_en)
    
    resp = input("\nProcessar Espanhol? (s/n): ")
    if resp.lower() == 's':
        processar_curadoria('Espanhol', ARQUIVO_ES, GLOSSARIO_ES, json_en)