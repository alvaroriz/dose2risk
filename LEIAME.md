# HotSpot BEIR V/VII - Estimativa de Risco de Câncer por Radiação

## Visão Geral
Este projeto realiza o processamento de dados de doses provenientes de simulações HotSpot, estimando o risco de câncer associado à exposição à radiação ionizante, utilizando os modelos epidemiológicos BEIR V e BEIR VII.

O sistema é focado em aplicações de radioproteção, emergências nucleares e análises de risco em áreas expostas a radionuclídeos, fornecendo resultados automatizados e transparentes para pesquisadores e profissionais da área.

## Estrutura do Projeto
```
Programa_Python/
├── hotspot_fluxo_unificado.py          # Script principal do pipeline
├── dados_referencia/                  # PDFs, tabelas e parâmetros de referência (ex: BEIR VII)
├── fonte_file_hotspot/                # Arquivos de entrada HotSpot (.txt)
├── output_dir/                        # Resultados gerados (CSV, logs)
```

## Funcionalidades
- **Extração automática** de dados de arquivos HotSpot.
- **Transposição e organização** dos dados para formato tabular.
- **Cálculo de risco de câncer** para diferentes órgãos e cenários, com base nos modelos BEIR V e BEIR VII.
- **Geração de relatórios** em CSV e logs detalhados do processamento.
- **Parâmetros personalizáveis**: idade de exposição, idade de avaliação, modelo de risco, etc.

## Modelos Epidemiológicos
- **BEIR VII**: Utiliza parâmetros beta, gamma e eta para cada órgão/sexo, ajustando o risco conforme idade de exposição e avaliação. Fórmula principal:
  
  `Risco Excedente = beta × ERR(e,a) × dose_Sv`
  
  Onde `ERR(e,a) = exp(gamma × e*) × (idade_avaliacao / 60)^eta`

- **BEIR V**: Modelo alternativo para doses muito elevadas, utilizando coeficientes alpha2, alpha3 e modificadores baseados no tempo desde a exposição.

## Como Executar
1. **Pré-requisitos:**
   - Python 3.8+
   - Bibliotecas: pandas, numpy

2. **Organize os diretórios:**
   - Coloque os arquivos HotSpot na pasta `fonte_file_hotspot`.
   - Certifique-se de que os arquivos de parâmetros e tabelas de referência estejam em `dados_referencia`.

---

## Execução via Interface Web (Flask)

Além do modo tradicional via linha de comando, este projeto oferece uma interface web moderna e amigável, permitindo o processamento dos arquivos HotSpot e geração dos riscos diretamente pelo navegador.

### Como usar a interface web

1. **Pré-requisitos:**
   - Python 3.8+
   - Instalar dependências: `pip install flask pandas numpy`

2. **Executando o servidor web:**
   - No terminal, acesse a pasta do projeto e execute:
     ```bash
     python app_web.py
     ```
   - O sistema estará disponível em `http://localhost:5000`.

3. **Fluxo de uso:**
   - **Upload:** Faça upload de um ou mais arquivos HotSpot `.txt` pela página inicial.
   - **Parâmetros:** Informe a idade na exposição e a idade atual no formulário exibido após o upload.
   - **Processamento:** O sistema executa o pipeline real e gera os arquivos de saída (CSV e LOG) para download.
   - **Reprocessamento:** É possível reprocessar os mesmos arquivos com outros parâmetros de idade, sem necessidade de novo upload.
   - **Download:** Baixe os arquivos de saída gerados diretamente pela interface.

4. **Isolamento de execuções:**
   - Cada upload cria uma pasta exclusiva para os arquivos enviados e para os resultados, permitindo múltiplos usuários e execuções simultâneas sem conflitos de nomes.

### Exemplo de uso

- Acesse `http://localhost:5000` no navegador.
- Envie seus arquivos `.txt` do HotSpot.
- Informe as idades solicitadas.
- Baixe os arquivos de resultado (CSV/LOG).
- Se desejar, clique em “Processar novamente com outras idades” para recalcular riscos usando os mesmos arquivos.

---

3. **Execute o pipeline:**
   ```bash
   python hotspot_fluxo_unificado.py --input_dir fonte_file_hotspot --exp_age 10 --att_age 15 --output_dir output_dir
   ```
   - `--input_dir`: Pasta com arquivos HotSpot (.txt)
   - `--exp_age`: Idade de exposição (anos)
   - `--att_age`: Idade de avaliação (anos)
   - `--output_dir`: Pasta para salvar os resultados

4. **Resultados:**
   - O arquivo CSV com os riscos estará em `output_dir/003_riscos_calculados_<timestamp>.csv`
   - O log detalhado estará em `output_dir/003_riscos_calculados_<timestamp>.log`

## Parâmetros de Entrada
- **Idade de exposição:** Idade da pessoa no momento da exposição à radiação.
- **Idade de avaliação:** Idade da pessoa na avaliação do risco.
- **Modelo:** O sistema seleciona automaticamente entre BEIR V e VII conforme a dose, mas pode ser forçado via parâmetro.

## Referências Científicas
- **BEIR VII (2006):** Health Risks from Exposure to Low Levels of Ionizing Radiation (National Academy of Sciences).
- **BEIR V (1990):** Health Effects of Exposure to Low Levels of Ionizing Radiation.

Consulte os PDFs em `dados_referencia/` para detalhes sobre fórmulas, parâmetros e tabelas utilizadas.

## Observações Importantes
- Os resultados dependem da qualidade dos dados de entrada e da correta parametrização.
- O sistema é voltado para fins acadêmicos e de pesquisa. Para uso regulatório, consulte especialistas e normas vigentes.
- Para dúvidas sobre os parâmetros dos modelos, consulte diretamente as tabelas do BEIR VII/V.

## Suporte
Para dúvidas, sugestões ou colaboração, entre em contato com o responsável pelo projeto ou abra uma issue neste repositório.

---

**Desenvolvido para aplicações em Radioproteção, Emergências Nucleares e Pesquisa Científica.**
