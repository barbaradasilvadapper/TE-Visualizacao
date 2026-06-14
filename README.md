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

As visualizações foram organizadas em três dashboards principais, cada um agrupando duas perguntas de negócio relacionadas.

### 1. Demanda e Sobrecarga Técnica

Este dashboard analisa a evolução dos atendimentos técnicos e dos desdobramentos técnicos ao longo dos anos. Ele permite identificar tendências, picos de demanda e possíveis períodos de maior sobrecarga para a equipe da Fundação.

Principais recursos:

- gráficos de linha;
- small multiples;
- heatmap de sobrecarga;
- ranking de períodos críticos;
- filtros por ano, categoria e indicador.

---

### 2. Movimentações e Permanência Institucional

Este dashboard analisa os indicadores de entrada, saída, evasão, desligamento e permanência das crianças e adolescentes na instituição. O objetivo é observar padrões sazonais, períodos críticos e possíveis mudanças na estabilidade institucional ao longo do tempo.

Principais recursos:

- gráfico de barras mensal;
- heatmap mês a mês;
- diagrama de fluxo;
- índice simples de estabilidade;
- filtros por período, ano e indicador.

---

### 3. Indicadores Institucionais e Atividades de 2025

Este dashboard analisa a relação entre o número de acolhidos e os indicadores de saúde mental, saúde clínica e educação. Também apresenta a distribuição das atividades culturais, capacitações e ações institucionais realizadas em 2025.

Principais recursos:

- gráfico combinado de barras e linhas;
- índice base 100;
- treemap;
- distribuição mensal das atividades;
- seleção dinâmica da métrica do treemap.

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