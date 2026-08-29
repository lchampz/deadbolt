# Hot Takes e Falhas

> Matéria-prima dos 5 pts de "Hot Take" e do "experimento removido" do vídeo.
> Formato: **falha observada** (com evidência) → **causa** → **lição**.

## O offset silencioso (2026-08-29, S1)

- **Falha evitada:** `mutmut show` emite diff da **função extraída**, não do
  arquivo. O hunk do mutante `x_slugify__mutmut_15` diz `@@ -38,7 @@`, mas a
  linha real no arquivo é a **115**. Quem lê o número do hunk como número de
  linha erra por 74 linhas e não recebe nenhum erro.
- **Causa:** ferramenta de mutação raciocina em unidade de função; a métrica
  raciocina em unidade de arquivo. A fronteira entre as duas é muda.
- **Detecção:** o construtor do ground truth reabre o arquivo original e afirma
  que a linha que ele alega mutar contém aquele texto. `line_mismatches: 0` nos
  216 mutantes e nos 288 do holdout.
- **Lição:** todo mapeamento entre ferramenta externa e métrica própria precisa
  de uma asserção que falhe alto. Sem ela, o pipeline inteiro roda, produz
  números plausíveis, e está deslocado. Esta é a versão S1 do mesmo erro que
  matou o Apura: **o número parecia certo**.

## O piso trivial não é zero (2026-08-29, S2)

- **Falha observada:** o primeiro `--sanity` no holdout reprovou. Não porque o
  harness estava quebrado — porque prever o arquivo `__main__.py` **inteiro** dá
  precisão 0.306, recall 1.000, **F1 0.469**.
- **Causa:** o holdout tem 30 linhas cegas em 98. Densidade de 30.6%. Meu limiar
  de sanidade (`F1 < 0.25`) fora calibrado na densidade do DEV (7%) e aplicado
  cegamente ao outro conjunto.
- **Lição:** um piso trivial é uma propriedade **do conjunto**, não do harness.
  Reportar F1 0.55 no holdout soaria bom e seria pior que dizer "prevejo tudo".
  `eval/report.py` agora imprime piso e teto em toda tabela — não como cortesia,
  como defesa. **Número sem piso não é resultado.**

## A chamada morta que virou cache (2026-08-29, primeira tentativa de S3)

- **Falha observada:** a primeira chamada real morreu com `400 ... credit balance
  is too low`. O `finally` do cliente gravou a chamada assim mesmo, com
  `response: ""`, `input_tokens: 0`, dentro de `recordings/` — o mesmo diretório
  que alimenta o modo replay.
- **Causa:** eu usei `try/except/finally` para garantir que o erro virasse
  artefato (o brief pede histórico de falha). O `finally` não distingue "gravar
  para auditoria" de "gravar para reuso". São dois destinos, escrevi um.
- **Por que é grave:** uma gravação com resposta vazia é **indistinguível** de um
  modelo que respondeu vazio. A execução seguinte em replay serviria o vazio
  como se fosse resultado, com o erro de saldo apagado do caminho. O número
  sairia — e sairia errado, por um motivo que não aparece em lugar nenhum.
- **Correção:** falha vai para `recordings/failed/<key>-<timestamp>.json`, nunca
  para o cache. Teste de regressão `test_chamada_que_falha_nunca_vira_cache`
  afirma as duas metades: nada no cache, e o replay seguinte continua quebrando.
- **Lição:** "registrar o erro" e "guardar a resposta" parecem a mesma escrita e
  não são. Todo cache que também serve de log precisa de dois destinos, porque
  um deles alimenta uma métrica. É o mesmo modo de falha que o projeto audita —
  agente que declara sucesso sem verificar — e ele apareceu no meu código antes
  de aparecer no do modelo.

## Risco declarado do harness desta sessão

O plano previa três papéis separados: Claude pensa, Cursor executa, Claude
revisa. Nesta sessão os três são o mesmo agente — a separação que pegaria
auto-engano está ausente por construção.

Mitigação adotada, não perfeita: R2 ao pé da letra. Todo veredito em
[[03 - Cartões de Hipótese]] cita output cru colado em [[04 - Diário de Bordo]],
e os controles do S2 (fabricada errada, aleatório, oráculo) existem para que o
harness discorde de mim sozinho. **Isso reduz o risco; não o elimina.**
Declarado aqui em vez de omitido.
