import json
import os
import copy
import requests
import time

from typing import Dict, List, Any, Tuple


# =========================================================
# CONFIGURAÇÃO GOOGLE TRANSLATE API (HTTP)
# =========================================================

API_KEY = "AIzaSyCc36fCwLeH4ddwE_GCL2-6-bglLX19R2U"

GOOGLE_TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"


class TradutorJsonService:

    def __init__(self, arq_glossario_pt: str, arq_glossario_es: str):
        self.arq_glossario_pt = arq_glossario_pt
        self.arq_glossario_es = arq_glossario_es

        print("[INFO] Carregando glossários externos...")
        self.glossario_pt = self._carregar_glossario_seguro(self.arq_glossario_pt)
        self.glossario_es = self._carregar_glossario_seguro(self.arq_glossario_es)

        self.correcoes_fixas: Dict[str, str] = {
            "conforme planejado": "Como Planejado",
            "Conforme planejado": "Como Planejado",
            "BOP conforme planejado": "BOP Como Planejado",
            "Pedido de Trabalho": "Ordem de Trabalho",
            "ComprarDesconto": "Aprovação (Buy-off)",
            "/SN": "/NS",
            " SN ": " NS ",
            "(SN)": "(NS)",
            "Eu ia": "ID",
            "Eu fosse": "ID"
        }

    # =========================================================
    # UTILITÁRIOS
    # =========================================================

    def _carregar_glossario_seguro(self, caminho: str) -> Dict[str, str]:
        if not os.path.exists(caminho):
            print(f"[AVISO] Glossário não encontrado: {caminho}")
            return {}

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return {k.lower().strip(): v for k, v in dados.items()}
        except Exception as e:
            print(f"[ERRO] Glossário inválido '{caminho}': {e}")
            return {}

    def carregar_json(self, caminho: str) -> Dict[str, Any]:
        if not os.path.exists(caminho):
            print(f"[AVISO] Arquivo de entrada não encontrado: {caminho}")
            return {}

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRO] Falha ao ler JSON '{caminho}': {e}")
            return {}

    def salvar_json(self, dados: Any, caminho: str) -> None:
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            print(f"[INFO] Arquivo salvo: {caminho}")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar '{caminho}': {e}")

    # =========================================================
    # EXTRAÇÃO / REMONTAGEM
    # =========================================================

    def extrair_textos_recursivo(
        self, dados: Any, caminho_atual: List[Any] = None
    ) -> List[Tuple[List[Any], str]]:

        if caminho_atual is None:
            caminho_atual = []

        lista_nos: List[Tuple[List[Any], str]] = []

        if isinstance(dados, dict):
            for k, v in dados.items():
                lista_nos.extend(
                    self.extrair_textos_recursivo(v, caminho_atual + [k])
                )

        elif isinstance(dados, list):
            for i, item in enumerate(dados):
                lista_nos.extend(
                    self.extrair_textos_recursivo(item, caminho_atual + [i])
                )

        elif isinstance(dados, str) and dados.strip():
            lista_nos.append((caminho_atual, dados))

        return lista_nos

    def remontar_json(
        self,
        estrutura_original: Dict[str, Any],
        lista_traduzida: List[Tuple[List[Any], str]]
    ) -> Dict[str, Any]:

        novo_json = copy.deepcopy(estrutura_original)

        for caminho, texto_novo in lista_traduzida:
            ref = novo_json
            for chave in caminho[:-1]:
                ref = ref[chave]
            ref[caminho[-1]] = texto_novo

        return novo_json

    # =========================================================
    # REGRAS DE NEGÓCIO
    # =========================================================

    def _aplicar_regras_negocio(self, texto: str) -> str:
        for errado, certo in self.correcoes_fixas.items():
            if errado in texto:
                texto = texto.replace(errado, certo)
        return texto

    # =========================================================
    # GOOGLE TRANSLATE API (HTTP + API KEY)
    # =========================================================

    def _traduzir_lote_google(self, lote: List[str], target: str) -> List[str]:
        params = {
            "key": API_KEY
        }

        payload = {
            "q": lote,
            "target": target,
            "format": "text"
        }

        response = requests.post(
            GOOGLE_TRANSLATE_URL,
            params=params,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Erro Google API {response.status_code}: {response.text}"
            )

        data = response.json()
        return [t["translatedText"] for t in data["data"]["translations"]]

    # =========================================================
    # EXECUÇÃO PRINCIPAL
    # =========================================================

    def executar_traducao(
        self,
        arquivo_entrada: str,
        configuracao_saida: Dict[str, str]
    ) -> None:

        print("[INFO] Iniciando tradução...")

        json_original = self.carregar_json(arquivo_entrada)
        if not json_original:
            return

        itens_para_processar = self.extrair_textos_recursivo(json_original)
        print(f"[INFO] Total de nós para processar: {len(itens_para_processar)}")

        for lang_code, arquivo_saida in configuracao_saida.items():
            print("--------------------------------------------------")
            print(f"[INFO] Processando idioma: {lang_code.upper()}")

            target_lang = "pt" if lang_code == "pt" else "es"
            glossario_ativo = self.glossario_pt if lang_code == "pt" else self.glossario_es

            caminhos_para_traducao = []
            textos_para_traducao = []
            itens_resolvidos = []

            contador_glossario = 0

            for caminho, texto_original in itens_para_processar:
                chave = texto_original.lower().strip()
                termo = glossario_ativo.get(chave)

                if termo:
                    itens_resolvidos.append((caminho, termo))
                    contador_glossario += 1
                else:
                    caminhos_para_traducao.append(caminho)
                    textos_para_traducao.append(texto_original)

            print(f"[INFO] Resolvido via Glossário: {contador_glossario}")
            print(f"[INFO] Enviando para Google: {len(textos_para_traducao)} itens")

            traducoes_google = []
            chunk_size = 120
            total = len(textos_para_traducao)

            for i in range(0, total, chunk_size):
                lote = textos_para_traducao[i:i + chunk_size]
                resultados = self._traduzir_lote_google(lote, target_lang)
                traducoes_google.extend(resultados)
                print(f"[DEBUG] Google: {len(traducoes_google)}/{total}", end="\r")
                time.sleep(0.2)

            print("")

            todos_itens = list(zip(caminhos_para_traducao, traducoes_google)) + itens_resolvidos
            itens_finais = []

            for caminho, texto in todos_itens:
                texto_limpo = self._aplicar_regras_negocio(texto)
                itens_finais.append((caminho, texto_limpo))

            json_final = self.remontar_json(json_original, itens_finais)
            self.salvar_json(json_final, arquivo_saida)

        print("[INFO] Processo finalizado.")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    ARQUIVO_ENTRADA = "en.json"
    ARQUIVO_GLOSSARIO_PT = "glossario_pt.json"
    ARQUIVO_GLOSSARIO_ES = "glossario_es.json"

    CONFIG_SAIDA = {
        "pt": "pt-BR.json",
        "es": "es.json"
    }

    servico = TradutorJsonService(
        ARQUIVO_GLOSSARIO_PT,
        ARQUIVO_GLOSSARIO_ES
    )

    servico.executar_traducao(ARQUIVO_ENTRADA, CONFIG_SAIDA)
