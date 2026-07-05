# Projeto Extensionista — Visualização de Dados

## 👥 Grupo

- Ana Carolina Poletto  
- Bárbara Dapper  
- Louise Northfleet  
- Luiza Pasini  
- Rafaela Remião  

---

## 🤝 ONG Parceira

O projeto foi desenvolvido em parceria com a Fundação Pão dos Pobres, organização social que disponibilizou os dados utilizados nas análises e nas visualizações desenvolvidas ao longo do trabalho.

---

## 📌 Sobre o Projeto

Este projeto foi desenvolvido na disciplina de Visualização de Dados, com o objetivo de criar dashboards interativos que auxiliem a análise e a tomada de decisão da Fundação Pão dos Pobres.

A proposta busca explorar dados relacionados aos programas de acolhimento, aprendizagem profissional, saúde, educação, atividades institucionais e serviços de convivência da instituição. Para isso, foram aplicadas etapas de pré-processamento, organização, análise exploratória e construção de visualizações interativas.

As visualizações foram desenvolvidas com foco em responder perguntas de negócio relevantes para a Fundação, permitindo identificar padrões temporais, períodos críticos, variações nos indicadores e possíveis pontos de atenção para a gestão institucional.

---

## 🎯 Objetivos

- Entender e organizar as planilhas fornecidas pela instituição;
- Identificar indicadores relevantes para análise dos programas sociais;
- Aplicar técnicas de limpeza, transformação e integração de dados;
- Desenvolver dashboards interativos para análises temporais e comparativas;
- Permitir a exploração dos dados por meio de filtros e parâmetros;
- Apoiar a interpretação dos resultados obtidos;
- Aplicar conceitos e boas práticas de visualização de dados em um contexto real.

---

## 📊 Dashboards Desenvolvidos

A solução foi desenvolvida em **Streamlit** e organizada em seis dashboards interativos, acessíveis pelo menu lateral. Cada dashboard responde a uma dimensão de análise da Fundação Pão dos Pobres, utilizando diferentes formas de visualização para apoiar a exploração temporal, comparativa e institucional dos dados.

### 1. Evolução da demanda e sobrecarga

Este dashboard permite acompanhar a evolução mensal dos indicadores da Fundação ao longo dos anos analisados. O objetivo é identificar padrões de crescimento, redução ou concentração de demanda em diferentes períodos.

Principais recursos implementados:

- Filtro por ano;
- Filtro por categoria;
- Seleção dinâmica de indicadores;
- Indicadores sintéticos no topo da página;
- Gráficos de linha para análise temporal;
- Small multiples para comparar a evolução de diferentes indicadores;
- Heatmap mensal para identificar períodos de maior concentração.

Esse dashboard contribui para responder perguntas relacionadas à evolução da demanda institucional e aos possíveis períodos de sobrecarga nos atendimentos e serviços.

---

### 2. Desdobramentos técnicos

Este dashboard apresenta os encaminhamentos, interfaces e desdobramentos técnicos registrados na base. Ele permite analisar quais tipos de atendimento ou articulação técnica concentram maior volume de registros ao longo do tempo.

Principais recursos implementados:

- Filtro por ano;
- Filtro por categoria e indicador;
- Indicadores sintéticos;
- Gráficos de barras para comparação entre tipos de desdobramentos;
- Visualizações temporais para observar a evolução dos registros;
- Ranking dos desdobramentos com maior ocorrência.

Esse dashboard auxilia na compreensão das demandas técnicas mais recorrentes e na identificação das áreas que exigem maior articulação institucional.

---

### 3. Padrões sazonais e movimentação

Este dashboard tem como foco a análise de entradas, saídas, evasões, desligamentos e permanências. A proposta é identificar padrões sazonais e períodos críticos relacionados à movimentação dos acolhidos.

Principais recursos implementados:

- Filtro por ano;
- Seleção de indicadores de movimentação;
- Gráficos de barras por mês;
- Comparação entre anos;
- Heatmap de concentração mensal;
- Indicadores para resumir os principais volumes observados.

Esse dashboard permite observar em quais meses determinados tipos de movimentação ocorrem com maior intensidade, apoiando a análise de sazonalidade e planejamento institucional.

---

### 4. Estabilidade da permanência

Este dashboard analisa a composição das movimentações institucionais, com foco na relação entre permanência, entradas e saídas críticas. Ele busca apoiar a compreensão da estabilidade dos acolhidos ao longo dos anos.

Principais recursos implementados:

- Indicadores sintéticos sobre permanência e movimentações;
- Visualização de fluxo para representar a composição das movimentações;
- Comparações anuais;
- Gráficos de apoio para análise da estabilidade institucional.

Esse dashboard contribui para avaliar se os registros indicam maior estabilidade ou maior rotatividade no acolhimento, considerando os dados agregados disponíveis.

---

### 5. Acolhidos, saúde e educação

Este dashboard compara o volume de efetivos na casa com indicadores relacionados à saúde mental, saúde clínica e educação. O objetivo é observar a relação entre o número de acolhidos e a pressão exercida sobre diferentes áreas de atendimento.

Principais recursos implementados:

- Filtro por ano;
- Indicadores sintéticos;
- Gráfico combinado de barras e linhas;
- Comparação entre acolhidos, saúde e educação;
- Gráfico com índice base 100 para comparação proporcional entre indicadores de escalas diferentes.

Esse dashboard permite analisar se as demandas de saúde e educação acompanham, crescem ou se comportam de forma diferente em relação ao volume de acolhidos.

---

### 6. Eventos realizados em 2025

Este dashboard reúne uma análise específica dos eventos e atividades registrados em 2025. Ele permite identificar quais ações foram mais recorrentes, sua distribuição proporcional e os meses com maior concentração de registros.

Principais recursos implementados:

- Indicadores sintéticos no topo da página:
  - total de eventos realizados em 2025;
  - quantidade de atividades distintas;
  - evento mais recorrente;
- Treemap com a distribuição proporcional dos eventos;
- Ranking dos 10 eventos mais realizados;
- Gráfico de barras com a distribuição mensal dos eventos em 2025.

Esse dashboard facilita a identificação das atividades mais frequentes, como atendimentos individuais, saúde mental, atendimento familiar e efetivos na casa, além de mostrar a variação mensal do volume de eventos ao longo do ano.

---

## 🧭 Boas Práticas e Design Patterns

A construção dos dashboards considerou boas práticas de visualização de dados e padrões de design para dashboards, com base no material disponível em:

https://dashboarddesignpatterns.github.io/

Foram considerados principalmente os seguintes padrões:

- Multiple Page Dashboard: organização do projeto em diferentes dashboards temáticos;
- Parameterized Dashboard: uso de filtros, seletores e botões de opção para permitir exploração dinâmica;
- Grouped Layout: agrupamento de visualizações relacionadas dentro de uma mesma página;
- Detailed Charts: uso de gráficos com títulos claros, eixos nomeados, legendas e tooltips;
- Meta Information: inclusão de descrições e contexto para facilitar a interpretação;
- Detail on Demand: possibilidade de obter valores detalhados ao passar o cursor sobre os gráficos.

Essa organização busca tornar a navegação mais intuitiva e evitar excesso de informação em uma única tela.

---

## 🛠️ Tecnologias Utilizadas

- Python
- Pandas
- Plotly
- Streamlit
- Jupyter Notebook

---

## 📁 Estrutura do Projeto

text projeto/ │ ├── app.py ├── requirements.txt │ ├── dados_tratados/ │   └── lem_consolidado_2021_2025.csv │ ├── notebooks/ │   ├── pre_processamento.ipynb │   ├── analise_exploratoria.ipynb │   └── visualizacoes_teste.ipynb │ └── README.md 

---

## ▶️ Como Executar o Projeto

Primeiro, instale as dependências do projeto:

bash pip install -r requirements.txt 

Depois, execute o dashboard com o Streamlit:

bash streamlit run app.py 

Após executar o comando, o Streamlit abrirá o dashboard no navegador.

---

## 📌 Observações

Os dados utilizados neste projeto foram fornecidos pela Fundação Pão dos Pobres e tratados exclusivamente para fins acadêmicos.

O notebook foi utilizado inicialmente para testar e validar diferentes visualizações. Após essa etapa, as visualizações mais adequadas foram implementadas no Streamlit, compondo os dashboards finais do projeto
