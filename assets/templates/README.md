# Templates de Layout (Power BI)

> Conjunto de layouts visuais customizados em formato vetorial SVG, desenvolvidos especificamente para as páginas analíticas do relatório no Power BI / Microsoft Fabric.

[Português](README.md) | [English](README.en.md)

---

## Visão Geral

Esta pasta reúne os arquivos de tela de fundo (*canvas background*) utilizados no relatório **Marketing Budget Optimization**. Em vez de compor contornos, cartões e divisórias utilizando dezenas de formas geométricas nativas dentro do Power BI, o relatório utiliza **templates vetoriais em SVG**.

### Vantagens do uso de Templates SVG:
1. **Performance e Renderização Otimizada:** Reduz o Document Object Model (DOM) interno do Power BI ao consolidar dezenas de elementos visuais de fundo em uma única camada vetorial, acelerando a renderização das consultas DirectLake.
2. **Nitidez Vetorial Absoluta:** O formato SVG mantém linhas, contornos e proporções nítidas em qualquer resolução de tela (Full HD, 2K, 4K) sem pixelização.
3. **Leveza de Armazenamento:** Arquivos extremamente leves (menos de 10 KB cada), otimizando a distribuição e o versionamento do projeto via Git.
4. **Padronização Visual:** Garante consistência rigorosa de espaçamento, hierarquia e paleta cromática (*Dark Mode*) em todas as páginas.

---

## Catálogo de Arquivos

| Arquivo | Página Correspondente | Resolução Recomendada | Descrição |
|:---|:---|:---:|:---|
| `template-pagina-1-executivo.svg` | **1. Executivo** | 1920 x 2160 px (Rolagem vertical) | Estrutura para KPIs consolidados no topo, 4 blocos analíticos centrais de retorno/custo e gráfico temporal no rodapé. |
| `template-pagina-2-campanhas.svg` | **2. Campanhas** | 1920 x 2160 px (Rolagem vertical) | Grade de performance com cartões superiores de taxas (Conversão, CTR), matrizes de posicionamento e tabela de detalhamento tático. |
| `template-pagina-3-orcamento.svg` | **3. Orçamento** | 1920 x 2160 px (Rolagem vertical) | Layout focado em tomada de decisão: alocação por eficiência, identificação de desvios e matriz de redistribuição de investimento publicitário. |

---

## Instruções de Aplicação no Power BI Desktop

Siga o passo a passo abaixo para aplicar os templates com o enquadramento e a rolagem corretos:

1. **Configurar as dimensões da página:**
   - Selecione a página do relatório.
   - Abra o painel lateral **Formatar página de relatório** > **Configurações de tela**.
   - No campo **Tipo**, escolha **Personalizado**.
   - Defina as dimensões: **Largura: 1920 px** e **Altura: 2160 px**.

2. **Configurar o modo de exibição (Rolagem vertical):**
   - No menu superior do Power BI Desktop, vá na guia **Exibição**.
   - No botão **Ajuste de Página**, selecione **Ajustar à largura** (*Fit to width*). Isso ativará a navegação suave com rolagem vertical.

3. **Aplicar a imagem de fundo:**
   - No painel **Formatar página de relatório**, abra a seção **Tela de fundo** (*Canvas background*).
   - Clique em **Procurar** no campo de imagem e selecione o arquivo correspondente da pasta `assets/templates/`.
   - Em **Ajuste da imagem**, selecione **Ajustar** (*Fit*) ou **Preencher** (*Fill*).
   - Ajuste a **Transparência obrigatoriamente para 0%** (o padrão do Power BI é 100%, o que deixa a imagem transparente).

4. **Transparência dos visuais:**
   - Para que o design e as molduras do template apareçam perfeitamente, selecione cada cartão, gráfico ou tabela e certifique-se de que a tela de fundo do visual (*Visual background*) esteja desativada ou com **transparência em 100%**.

---

[Voltar para o Repositório Principal](../../README.md)
