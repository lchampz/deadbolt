# METRIC.md — métrica congelada

**Congelada em:** 2026-08-29T16:30:00Z (fim do S2, antes de existir qualquer solução)
**Regra R5:** depois deste timestamp, métrica, taxonomia, regra de casamento e
corpus **não mudam**. Alteração exige abort declarado por escrito neste arquivo,
com motivo e data.

---

## 1. A tarefa

Dado um arquivo-fonte Python e sua suíte de testes, prever **onde a suíte é
cega**: as linhas cuja mutação a suíte não detecta.

Ground truth: `mutmut 3.7.0` sobre `python-slugify @ 7b6d5d96`. Gerado em S1,
**antes** de existir solução, por uma ferramenta externa ao sistema avaliado.

## 2. Corpus congelado

| Conjunto | Módulos | Mutantes | Killed | Survived | Frac. | Linhas com sobrevivente (G) | Linhas só com mortos (K) |
|---|---|---:|---:|---:|---:|---:|---:|
| **DEV** | `slugify/slugify.py`, `slugify/special.py` | 216 | 170 | 46 | 0.213 | 17 | 49 |
| **HOLDOUT** | `slugify/__main__.py` | 288 | 189 | 99 | 0.344 | 30 | 39 |

**Regra de holdout.** O conteúdo dos sobreviventes do HOLDOUT não é lido durante
S3–S6. Ele é olhado uma única vez, em S7, e o número reportado é o dessa única
leitura. Se um ajuste feito olhando DEV melhorar o HOLDOUT, isso **não é vitória**
— é o sinal de contaminação que matou a medição do projeto anterior.

`__main__.py` é CLI/argparse; `slugify.py` é processamento de string. Perfis
diferentes de propósito: o HOLDOUT mede **transferência**, não só generalização.

## 3. Schema de saída da predição (congelado)

```json
{
  "file": "slugify/slugify.py",
  "line_range": [115, 115],
  "blind_spot_type": "error_path",
  "evidence_quote": "text = str(text, 'utf-8', 'ignore')",
  "confidence": 0.72,
  "rationale": "nenhum teste passa bytes; o ramo de decodificação nunca executa"
}
```

- `line_range` — par `[início, fim]`, 1-based, **inclusivo**.
- `evidence_quote` — trecho literal que deve aparecer no arquivo dentro do range.
- `confidence` — float em `[0, 1]`.
- `blind_spot_type` — um dos 6 da taxonomia abaixo.

## 4. Taxonomia de ponto cego (congelada, 6 tipos)

Derivada de teoria de teste (design de casos e operadores de mutação),
**não** do conteúdo dos sobreviventes deste corpus.

| Tipo | Definição |
|---|---|
| `unasserted_branch` | o ramo executa, mas nenhum teste distingue seu resultado do ramo oposto |
| `default_argument` | o valor default nunca é exercitado, ou só ele é, e os overrides não |
| `boundary_condition` | limite/comparação (`<` vs `<=`, off-by-one, vazio, zero) testado só no interior |
| `error_path` | guarda, exceção ou fallback que nenhum teste dispara |
| `output_shape` | o valor é produzido mas conferido de forma frouxa (verdade, tamanho, substring) |
| `dead_config` | constante, flag ou tabela cuja variação nenhum teste distingue |

## 5. Métrica primária (congelada)

Universo: as linhas `1..N` do arquivo alvo.

- **G** = linhas com ≥ 1 mutante **sobrevivente**
- **K** = linhas com mutante, todos **mortos**
- **P** = união das linhas cobertas por `line_range`, recortada em `[1, N]`

```
precisão = |P ∩ G| / |P|          (0 se |P| = 0)
recall   = |P ∩ G| / |G|
F1       = 2·p·r / (p + r)        (0 se p + r = 0)
```

**Regra de casamento:** sobreposição de linha, mesmo arquivo. Sem tolerância de
±1 linha. Sem crédito parcial.

**Por que é à prova de jogo.** Prever o arquivo inteiro (244 linhas no DEV) dá
recall 1.000 e precisão 0.070 → **F1 0.130**. A única forma de subir F1 é acertar
onde a cegueira está, não onde ela poderia estar.

## 6. Métricas secundárias (congeladas)

| Métrica | Definição | Por que importa |
|---|---|---|
| `near_miss_rate` | \|P ∩ K\| / \|P\| | FP em linha mutável — o preditor achou código, errou o veredito |
| `noise_rate` | \|P \ (G ∪ K)\| / \|P\| | FP em linha sem mutante — comentário, `def`, linha em branco |
| `mutant_recall` | mutantes sobreviventes cuja linha ∈ P, sobre o total de sobreviventes | pondera linhas com muitos sobreviventes |
| `evidence_valid_rate` | predições cujo `evidence_quote` aparece literalmente dentro do `line_range` | mede alucinação de âncora |
| `type_validity_rate` | predições cujo `blind_spot_type` está na taxonomia | mede aderência ao schema |
| `cost_usd`, `wall_seconds`, `n_predictions` | custo, tempo e volume por módulo | FinOps + honestidade do volume |

**Limitação declarada agora, não depois.** Não existe ground truth de *tipo* por
linha — `mutmut` classifica mutante, não intenção de teste. Logo `blind_spot_type`
é avaliado apenas quanto à **validade de schema**, nunca quanto à correção
semântica. Nenhum número deste relatório afirma que o tipo previsto está certo.

## 7. O que este número NÃO diz

- Mutante equivalente (mutação semanticamente idêntica ao original) conta como
  sobrevivente no ground truth. Parte de G é intocável por qualquer preditor.
  Não foi feita triagem manual de equivalência — declarado, não corrigido.
- 10 mutantes do HOLDOUT saíram com status "sem teste" e **não** aparecem em
  `mutmut results --all`; o ground truth do HOLDOUT tem 288 dos 298 gerados.
- Domínio: uma lib Python pura de manipulação de string e sua CLI. Nada aqui
  sustenta claim sobre código com I/O, concorrência ou framework.

---

## 8. Correção declarada — 2026-08-29, pós-medição

R5 diz que o artefato congelado só muda com **abort declarado por escrito, com
motivo**. Este é o registro desse abort. Nada foi ajustado em silêncio.

### O que estava errado

O construtor do ground truth reconhecia um único esquema de nome de mutante
(`x_<funcao>`) e descartava tudo que não casasse — **sem erro, sem aviso**. Duas
consequências:

1. **Status de duas palavras eram jogados fora.** Os 10 mutantes `no tests` do
   HOLDOUT nunca entraram no JSON. O conjunto congelado tinha 288 dos 298
   gerados — isso estava declarado no § 7 original como limitação, mas eu tratei
   como propriedade do `mutmut`, e era bug meu.
2. **Métodos de classe eram jogados fora.** `mutmut` nomeia método como
   `xǁClasseǁmetodoǁ__mutmut_N` (U+01C1). Num terceiro corpus de teste (`toolz`),
   isso descartou **301 de 534 mutantes** em silêncio, com
   `parse_errors: 0, line_mismatches: 0` — tudo aparentemente limpo.

### A correção de classificação, que muda um número medido

`no tests` significa que **nenhum teste executa aquela linha**. Isso é a forma
mais pura de ponto cego, e a métrica o classificava como *linha coberta* (`K`).
Um preditor que acertasse aquelas linhas era penalizado por acertar.

São **6 linhas** do `main()` de `slugify/__main__.py` (87–94), nenhuma delas já
contada como cega. O HOLDOUT passa de **|G| = 30 para |G| = 36**.

### O que muda e o que não muda

| Conjunto | Antes | Depois |
|---|---|---|
| DEV | 216 mutantes, 46 sobreviventes, \|G\|=17 | **idêntico** — `slugify.py` e `special.py` não têm classe nem mutante sem teste |
| HOLDOUT | 288 mutantes, 99 sobreviventes, \|G\|=30 | 298 mutantes, 109 cegos, **\|G\|=36** |

**Os números do DEV publicados antes desta correção permanecem válidos e não
foram recalculados.** Os do HOLDOUT foram **remedidos sobre as mesmas gravações**
— nenhuma chamada nova de modelo, nenhuma predição alterada. Só o gabarito foi
corrigido. As duas tabelas ficam no changelog, lado a lado.

### A defesa que faltava, agora instalada

`eval/build_ground_truth.py` compara o total de mutantes listados pelo `mutmut`
com o total que o parser reconheceu, e **sai com erro** se diferirem. Era a
assertiva que faltava na fronteira entre ferramenta externa e métrica própria —
a mesma lição do § "offset silencioso", que eu já tinha aprendido uma vez e não
generalizei.

---

## 9. Conjunto TRANSFER — adicionado em 2026-08-29, declarado antes de medir

Um terceiro conjunto, num **repositório diferente**: `toolz @ 1.1.0`, módulo
`toolz/functoolz.py` (1049 linhas), 534 mutantes, 118 sobreviventes (22.1%),
**|G| = 50 linhas cegas**. Ground truth gerado pelo mesmo `mutmut 3.7.0`, com o
construtor já corrigido (534/534 parseados, 0 erros, 0 mismatches).

**Isto NÃO altera DEV nem HOLDOUT.** Nenhum número já publicado é recalculado por
causa deste conjunto. Ele é reportado à parte, com o próprio piso e o próprio teto.

**O que ele responde que o HOLDOUT não responde.** O HOLDOUT é outro módulo do
*mesmo* repositório, com a *mesma* suíte. O TRANSFER é outro projeto, outros
autores, outro estilo de teste, e código com classes e decoradores — que o DEV
não tem. É generalização entre repositórios, não entre módulos.

**Escopo declarado antes de rodar:** só os estágios de arquivo inteiro —
`baseline`, `s4` e `s5`. O `s6` (varredura por função) fica **de fora**:
`functoolz.py` tem 45 funções e métodos, o que seriam 45 chamadas para um único
conjunto opcional. É corte por orçamento, declarado aqui, não resultado omitido.

**Compromisso:** o número que sair é reportado, seja qual for. Se o TRANSFER
ficar abaixo do piso trivial dele, isso entra na tabela e no changelog do mesmo
jeito que o resultado do HOLDOUT entrou.
