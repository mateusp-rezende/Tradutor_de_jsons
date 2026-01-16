
# Documentação Técnica

## Funcionamento Interno do Tradutor Automático de JSON
## LINKS IMPORTANTES QUE UTILIZEI
* https://www.datacamp.com/pt/tutorial/depth-first-search-in-python
* https://www.educative.io/answers/how-to-implement-depth-first-search-in-python
* https://cloud.google.com/translate/docs/reference/rest/v2/translate
* https://cloud.google.com/docs/authentication/api-keys

### 1. Visão Geral da Arquitetura

O Tradutor Automático de JSON foi projetado para traduzir conteúdos textuais de arquivos JSON complexos **sem alterar, quebrar ou reorganizar a estrutura original**.
O sistema é **estruturalmente não destrutivo**, atuando exclusivamente sobre valores textuais (`string`) e preservando integralmente:

* Chaves (keys)
* Hierarquia de objetos
* Ordem e índices de listas
* Tipos de dados não textuais
* Relacionamentos entre nós

A arquitetura separa claramente **estrutura** e **conteúdo**, garantindo segurança e previsibilidade.

---

### 2. Princípio Fundamental: Separação entre Estrutura e Conteúdo

O código nunca trabalha diretamente sobre o JSON como um todo durante a tradução.
Em vez disso, ele aplica um modelo em três fases:

1. **Leitura e mapeamento estrutural**
2. **Tradução isolada do conteúdo**
3. **Remontagem controlada**

Essa separação impede que qualquer modificação estrutural ocorra acidentalmente.

---

### 3. Extração Recursiva Baseada em Caminhos (Path-Based Traversal)

A extração dos textos é feita por um método recursivo que percorre toda a árvore JSON.

#### Estratégia:

* Cada valor textual encontrado é armazenado juntamente com o **caminho completo até ele**
* O caminho funciona como um endereço absoluto dentro do JSON

#### Exemplo de caminho:

```python
["screens", 3, "labels", "title"]
```

Esse caminho indica exatamente:

* Qual objeto
* Qual lista
* Qual índice
* Qual chave

O caminho é armazenado como uma lista ordenada de chaves e índices, o que garante navegação determinística.

---

### 4. Tipos de Nós Processados

Durante a recursão, o código trata cada tipo de nó explicitamente:

* **dict** → percorre cada par chave/valor
* **list** → percorre cada índice
* **str** → candidato à tradução
* Outros tipos (int, float, bool, null) → ignorados

Somente valores do tipo `string` e não vazios entram no pipeline de tradução.

---

### 5. Preservação da Estrutura Original

A estrutura original nunca é modificada diretamente.

Antes da remontagem:

* É criada uma **cópia profunda (deep copy)** do JSON original
* Todas as substituições acontecem **apenas nessa cópia**

Isso garante:

* Imutabilidade do JSON de entrada
* Possibilidade de reprocessamento
* Segurança contra corrupção de dados

---

### 6. Aplicação de Glossários com Prioridade Máxima

Antes de qualquer chamada à API externa, cada texto passa por um mecanismo de resolução local via glossário.

#### Funcionamento:

* O texto é normalizado (`lowercase + trim`)
* O glossário é consultado
* Se houver correspondência exata:

  * A tradução é aplicada imediatamente
  * O texto **não é enviado para a API**

#### Benefícios técnicos:

* Consistência terminológica
* Redução de custos
* Redução de latência
* Controle semântico corporativo

---

### 7. Tradução via Google Translate (HTTP API)

Somente textos não resolvidos pelo glossário são enviados para tradução automática.

#### Estratégia de Lotes:

* Os textos são agrupados em lotes controlados
* O tamanho do lote respeita o limite máximo da API (128 segmentos por requisição)
* Evita erros do tipo `Too many text segments`

Cada requisição é independente, permitindo:

* Recuperação de falhas
* Monitoramento de progresso
* Escalabilidade

---

### 8. Pós-processamento e Regras de Negócio

Após a tradução, o texto passa por uma camada de regras fixas.

Essas regras permitem:

* Padronização de termos técnicos
* Correção de traduções indesejadas
* Substituição controlada de siglas
* Adequação ao domínio do negócio

Essa etapa atua como uma **validação semântica final**, sem impactar a estrutura.

---

### 9. Remontagem Controlada do JSON

A remontagem é feita usando os caminhos capturados na fase de extração.

#### Processo:

1. Parte-se da cópia profunda do JSON original
2. Para cada item traduzido:

   * Navega-se pelo caminho armazenado
   * Substitui-se apenas o valor final (`string`)
3. Nenhum outro nó é alterado

#### Garantias:

* Chaves nunca são renomeadas
* Arrays nunca são reordenados
* Nenhum nó é criado ou removido

A fidelidade estrutural é total.

---

### 10. Garantias Técnicas do Sistema

O código garante explicitamente que:

* Não altera IDs
* Não altera chaves técnicas
* Não modifica hierarquia
* Não muda tipos de dados
*  Não interfere em valores não textuais

✔ Atua **somente** sobre strings
✔ Atua **somente** nos caminhos originalmente existentes

---

### 11. Robustez e Segurança Operacional

O sistema:

* Falha de forma controlada em erros de API
* Permite retomada do processo
* Não corrompe arquivos de entrada
* É adequado para arquivos críticos de configuração e i18n

---

### 12. Conclusão Técnica

Este tradutor foi projetado com foco em:

* Segurança estrutural
* Escalabilidade
* Controle terminológico
* Uso corporativo

A abordagem baseada em **caminhos estruturais** garante que a tradução seja aplicada de forma precisa, previsível e segura, mesmo em JSONs grandes, profundamente aninhados e críticos para o sistema.


