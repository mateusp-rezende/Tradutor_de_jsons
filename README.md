# 🌐 Sistema de Tradução e Curadoria de JSON

Sistema automatizado para **tradução de arquivos JSON** com foco em **qualidade, padronização e escala**, utilizando a **Google Cloud Translation API**, **glossários técnicos** e **curadoria humana assistida**.

Projetado para cenários corporativos (ex.: sistemas industriais, MES, Opcenter), onde a **estrutura do JSON não pode ser alterada** e a **terminologia deve ser consistente**.

---

## 📌 Visão Geral

O sistema permite:

- Traduzir grandes volumes de textos JSON
- Manter IDs e estrutura intactos
- Aplicar glossários técnicos com prioridade
- Evoluir o glossário automaticamente via curadoria
- Reduzir custo e retrabalho ao longo do tempo

---

## 🏗️ Arquitetura da Solução

```text
en.json (original)
   ↓
Script de Tradução (Google Translate API)
   ↓
pt-BR.json / es.json
   ↓
Script de Curadoria
   ↓
Glossário Técnico Atualizado
   ↓
Traduções futuras mais corretas e baratas
````

---

## 📁 Estrutura do Projeto

```text
.
├── en.json
├── pt-BR.json
├── es.json
├── glossario_pt.json
├── glossario_es.json
├── tradutor3.py
├── curadoria_glossario.py
└── README.md
```

---

## ⚙️ Pré-requisitos

* Python 3.9 ou superior
* Biblioteca `requests`
* Projeto no Google Cloud
* API **Cloud Translation** habilitada
* Faturamento ativo
* API Key válida

Instalação da dependência:

```bash
pip install requests
```

---

## 🔑 Configuração da API

No script `tradutor3.py`, configure sua API Key:

```python
API_KEY = "SUA_API_KEY_AQUI"
```

A API utilizada é:

```
https://translation.googleapis.com/language/translate/v2
```

---

## 🚀 Como Usar

### 1️⃣ Tradução dos arquivos

1. Coloque o arquivo original:

```text
en.json
```

2. Garanta que os glossários existam:

```text
glossario_pt.json
glossario_es.json
```

3. Execute o tradutor:

```bash
python tradutor3.py
```

4. Arquivos gerados:

```text
pt-BR.json
es.json
```

---

### 2️⃣ Curadoria e Evolução do Glossário

Após a tradução, execute:

```bash
python curadoria_glossario.py
```

O script:

* Compara `en.json` com o arquivo traduzido
* Identifica termos técnicos curtos
* Sugere novos termos para o glossário
* Permite validação humana

#### Opções durante a curadoria:

* `y` → Aprovar termo
* `n` → Ignorar
* `e` → Editar tradução
* `a` → Aprovar todos
* `s` → Sair salvando progresso

---

## 📘 Glossários Técnicos

Formato dos glossários (`glossario_pt.json`, `glossario_es.json`):

```json
{
  "work order": "Ordem de Trabalho",
  "as planned": "Como Planejado"
}
```

### Regras importantes:

* Glossário tem **prioridade sobre o Google**
* Chaves sempre em **minúsculo**
* Valores são livres (tradução final desejada)

---

## 🧠 Regras de Negócio Aplicadas

Após a tradução automática, o sistema aplica correções fixas para padronização:

| Tradução Automática | Correção Final    |
| ------------------- | ----------------- |
| conforme planejado  | Como Planejado    |
| Pedido de Trabalho  | Ordem de Trabalho |
| /SN                 | /NS               |

---

## ⚡ Performance e Limites

* Tradução em **lotes (batch)**
* Máximo de **128 textos por requisição** (limite da API)
* Configuração padrão segura: `chunk_size = 100`
* Tradução de milhares de textos em poucos minutos

---

## 💰 Custos

* Cobrança por **caractere traduzido**
* Glossário reduz chamadas à API
* Custo previsível e controlado
* Sem risco de bloqueio (API oficial)

---

## 🔒 Segurança

* Uso exclusivo da API oficial Google
* Sem scraping
* Sem automação não autorizada
* API Key pode ser restringida por IP ou serviço

---

## 📈 Benefícios

* ✅ Alta qualidade de tradução
* ✅ Padronização terminológica
* ✅ Redução de retrabalho
* ✅ Escalável para grandes volumes
* ✅ Evolução contínua do glossário

---

## 🧩 Diferencial

> Não é apenas tradução automática.
> É um **sistema corporativo de tradução com aprendizado contínuo**.

Cada execução melhora:

* o glossário
* a qualidade
* o custo

---

## 🔮 Evoluções Futuras

* Tradução para novos idiomas
* Processamento em lote de pastas
* Relatório de custo por arquivo
* Integração com CI/CD
* Validação automática de termos críticos

---

## 👤 Autor

Projeto desenvolvido para automação e padronização de traduções técnicas em ambiente corporativo.

---

## 📄 Licença

Uso interno / corporativo.


