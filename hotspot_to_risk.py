import os
import argparse
import pandas as pd
import logging
from datetime import datetime
import re
import math

# =========================================
# Classe ExtratorHotspot
# =========================================
class ExtratorHotspot:
    """
    Classe responsável por extrair dados dos arquivos HotSpot (.txt) e gerar um CSV tabular.
    """
    def __init__(self, pasta_entrada, arquivo_saida):
        self.pasta_entrada = pasta_entrada
        self.arquivo_saida = arquivo_saida

    def parse_number(self, s):
        """
        Converte string numérica para float, aceitando vírgula e notação científica.
        """
        try:
            s = str(s).strip().replace(',', '.')
            s = re.sub(r'[^0-9.\+\-eE]', '', s)
            return float(s)
        except Exception as e:
            logging.error(f"Erro ao converter número: {s} - {e}")
            return float('nan')

    def parse_hotspot_file(self, path):
        """
        Lê e extrai dados estruturados de um arquivo HotSpot.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            text = ''.join(lines)
        except Exception as e:
            logging.error(f"Erro ao ler o arquivo {path}: {e}")
            return []

        header_patterns = {
            'physical_stack_height_m': r'Physical Stack Height\s*:\s*([^\s]+)\s*m',
            'stack_exit_velocity_m_s': r'Stack Exit Velocity\s*:\s*([^\s]+)\s*m/s',
            'stack_diameter_m': r'Stack Diameter\s*:\s*([^\s]+)\s*m',
            'stack_effluent_temp_deg_c': r'Stack Effluent Temp\.\s*:\s*([^\s]+)\s*deg C',
            'air_temperature_deg_c': r'Air Temperature\s*:\s*([^\s]+)\s*deg C',
            'effective_release_height_m': r'Effective Release Height\s*:\s*([^\s]+)\s*m',
            'wind_speed_h=10_m_m_s': r'Wind Speed \(h=10 m\)\s*:\s*([^\s]+)\s*m/s',
            'wind_direction_degrees': r'Wind Direction\s*:\s*([0-9]+,[0-9]+)\s*degrees',
            'wind_from_the': r'Wind Direction\s*:\s*[0-9]+,[0-9]+\s*degrees\s*Wind from the\s*([A-Za-z]+)',
            'wind_speed_h=h-eff_m_s': r'Wind Speed \(h=H-eff\)\s*:\s*([^\s]+)\s*m/s',
            'stability_class': r'Stability Class\s*:\s*([A-Za-z])',
            'receptor_height_m': r'Receptor Height\s*:\s*([^\s]+)\s*m',
            'inversion_layer_height': r'Inversion Layer Height\s*:\s*([^\s]+)',
            'sample_time_min': r'Sample Time\s*:\s*([^\s]+)\s*min',
            'breathing_rate_m3_sec': r'Breathing Rate\s*:\s*([^\s]+)\s*m3/sec',
            'distance_coordinates': r'Distance Coordinates\s*:\s*(\S+)',
            'maximum_dose_distance_km_': r'Maximum Dose Distance\s*:\s*([^\s]+)\s*km',
            'maximum_tede_sv': r'Maximum TEDE\s*:\s*([^\s]+)\s*Sv',
            'inner_contour_dose_sv': r'Inner\s*Contour Dose\s*:\s*([^\s]+)\s*Sv',
            'middle_contour_dose_sv': r'Middle Contour Dose\s*:\s*([^\s]+)\s*Sv',
            'outer_contour_dose_sv': r'Outer\s*Contour Dose\s*:\s*([^\s]+)\s*Sv',
            'exceeds_inner_dose_out_to_km': r'Exceeds Inner\s*Dose Out To\s*:\s*([^\s]+)\s*km',
            'exceeds_middle_dose_out_to_km': r'Exceeds Middle Dose Out To\s*:\s*([^\s]+)\s*km',
            'exceeds_outer_dose_out_to_km': r'Exceeds Outer Dose Out To\s*:\s*([^\s]+)\s*km',
        }
        header_vals = {}
        for key, pat in header_patterns.items():
            m = re.search(pat, text)
            if not m:
                header_vals[key] = None
            else:
                val = m.group(1).strip()
                if key in ('stability_class', 'inversion_layer_height', 'distance_coordinates', 'wind_from_the'):
                    header_vals[key] = val
                else:
                    header_vals[key] = self.parse_number(val)
        rows = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if re.match(r'^\s*\d+,\d+', line):
                tokens = re.split(r'\s+', line.strip())
                dist, tede, resp_int, ground_surf, ground_shine, arrival = tokens[:6]
                row = dict(header_vals)
                row.update({
                    'distance_km': self.parse_number(dist),
                    'tede_sv': self.parse_number(tede),
                    'respirable_time-integrated_air_concentration_bq-sec_m3': self.parse_number(resp_int),
                    'ground_surface_deposition_kbq_m2': self.parse_number(ground_surf),
                    'ground_shine_dose_rate_sv_hr': self.parse_number(ground_shine),
                    'arrival_time_hour:min': arrival.strip('<>'),
                })
                j = i + 1
                while j < len(lines) and '[' not in lines[j]:
                    j += 1
                while j < len(lines) and '[' in lines[j]:
                    for org, val in re.findall(r'([A-Za-z ]+?)\.+\[(.*?)\]', lines[j]):
                        col = org.strip().lower().replace(' ', '_')
                        row[col] = self.parse_number(val)
                    j += 1
                for label, colname in [
                    ('Inhalation', 'inhalation_plume_passage'),
                    ('Submersion', 'submersion_plume_passage'),
                    ('Ground Shine', 'ground_shine'),
                ]:
                    while j < len(lines) and label not in lines[j]:
                        j += 1
                    if j < len(lines):
                        m2 = re.search(rf'{label}\s*:\s*([^\s]+)', lines[j])
                        row[colname] = self.parse_number(m2.group(1)) if m2 else None
                    j += 1
                rows.append(row)
                i = j
            else:
                i += 1
        return rows

    def extrair(self):
        """
        Executa a extração dos arquivos da pasta de entrada e gera o CSV tabular.
        """
        try:
            todas_linhas = []
            for fn in sorted(os.listdir(self.pasta_entrada)):
                if fn.lower().endswith('.txt'):
                    todas_linhas.extend(self.parse_hotspot_file(os.path.join(self.pasta_entrada, fn)))
            colunas = [
                'physical_stack_height_m','stack_exit_velocity_m_s','stack_diameter_m',
                'stack_effluent_temp_deg_c','air_temperature_deg_c','effective_release_height_m',
                'wind_speed_h=10_m_m_s','wind_direction_degrees','wind_from_the',
                'wind_speed_h=h-eff_m_s','stability_class','receptor_height_m','inversion_layer_height',
                'sample_time_min','breathing_rate_m3_sec','distance_coordinates',
                'maximum_dose_distance_km_','maximum_tede_sv','inner_contour_dose_sv',
                'middle_contour_dose_sv','outer_contour_dose_sv','exceeds_inner_dose_out_to_km',
                'exceeds_middle_dose_out_to_km','exceeds_outer_dose_out_to_km',
                'distance_km','tede_sv','respirable_time-integrated_air_concentration_bq-sec_m3',
                'ground_surface_deposition_kbq_m2','ground_shine_dose_rate_sv_hr',
                'arrival_time_hour:min','skin','surface_bone','spleen','breast','uli_wall','thymus',
                'kidneys','pancreas','lung','red_marrow','ovaries','stomach_wall','lli_wall',
                'esophagus','testes','brain','thyroid','liver','adrenals','si_wall','bladder_wall',
                'muscle','uterus','inhalation_plume_passage','submersion_plume_passage','ground_shine'
            ]
            df = pd.DataFrame(todas_linhas, columns=colunas)
            df.to_csv(self.arquivo_saida, sep=';', index=False, decimal='.', float_format='%.2e')
            logging.info(f"Arquivo CSV tabular gerado: {self.arquivo_saida}")
        except Exception as e:
            logging.error(f"Erro na extração dos arquivos HotSpot: {e}")

# =========================================
# Classe TranspositorHotspot
# =========================================
class TranspositorHotspot:
    """
    Classe responsável por transpor o CSV tabular para o formato órgão x cenário.
    """
    def __init__(self, csv_entrada, csv_saida):
        self.csv_entrada = csv_entrada
        self.csv_saida = csv_saida

    def transpor(self):
        """
        Executa a transposição do CSV tabular.
        """
        try:
            df = pd.read_csv(self.csv_entrada, sep=';', decimal='.')
            static_cols = [
                'physical_stack_height_m','stack_exit_velocity_m_s','stack_diameter_m',
                'stack_effluent_temp_deg_c','air_temperature_deg_c','effective_release_height_m',
                'wind_speed_h=10_m_m_s','wind_direction_degrees','wind_from_the',
                'wind_speed_h=h-eff_m_s','stability_class','receptor_height_m',
                'inversion_layer_height','sample_time_min','breathing_rate_m3_sec',
                'distance_coordinates','maximum_dose_distance_km_','maximum_tede_sv',
                'inner_contour_dose_sv','middle_contour_dose_sv','outer_contour_dose_sv',
                'exceeds_inner_dose_out_to_km','exceeds_middle_dose_out_to_km',
                'exceeds_outer_dose_out_to_km','distance_km','tede_sv',
                'respirable_time-integrated_air_concentration_bq-sec_m3',
                'ground_surface_deposition_kbq_m2','ground_shine_dose_rate_sv_hr',
                'arrival_time_hour:min','inhalation_plume_passage',
                'submersion_plume_passage','ground_shine'
            ]
            organ_cols = [c for c in df.columns if c not in static_cols]
            df_long = df.melt(
                id_vars=['stability_class','distance_km'],
                value_vars=organ_cols,
                var_name='organ',
                value_name='dose'
            )
            df_pivot = df_long.pivot(
                index='organ',
                columns=['stability_class','distance_km'],
                values='dose'
            )
            df_pivot.columns = [f"{cls}_{dist}" for cls, dist in df_pivot.columns]
            df_pivot = df_pivot.reset_index().rename(
                columns={'organ': 'organ/stabiliy_class_dose_class_distance_km'}
            )
            df_pivot.to_csv(self.csv_saida, sep=';', index=False, decimal='.', float_format='%.2e')
            logging.info(f"Arquivo CSV transposto gerado: {self.csv_saida}")
        except Exception as e:
            logging.error(f"Erro na transposição do CSV: {e}")

# =========================================
# Classe CalculadoraRisco
# =========================================
class CalculadoraRisco:
    """
    Classe responsável por calcular os riscos a partir do CSV transposto.
    """
    def __init__(self, csv_entrada, params_csv, pasta_saida, idade_exposicao, idade_atual, modelo='auto', timestamp=None):
        self.csv_entrada = csv_entrada
        self.params_csv = params_csv
        self.pasta_saida = pasta_saida
        self.idade_exposicao = idade_exposicao
        self.idade_atual = idade_atual
        self.modelo = modelo
        self.timestamp = timestamp

    def err_factor(self, age_exp, age_att, gamma, eta):
        """
        Calcula o fator ERR(e,a) conforme o modelo BEIR VII para risco de câncer induzido por radiação.

        ERR(e,a) = exp(gamma * e*) * (idade_avaliacao / 60)^eta

            Onde:
        - e* = (idade_exposicao - 30) / 10, se idade_exposicao < 30 anos, caso contrário e* = 0
        - gamma e eta são parâmetros específicos para cada órgão e sexo, definidos nas tabelas do BEIR VII.
        - idade_avaliacao é a idade no momento da avaliação do risco.
        - O fator ERR ajusta o risco conforme a idade de exposição e avaliação, conforme recomendado pelo BEIR VII (pág. 291-292).

        Tratamento de erro:
        - Se algum parâmetro for inválido, retorna erro e loga a exceção.
        """
        e_star = (age_exp - 30) / 10.0 if age_exp < 30 else 0.0
        return math.exp(gamma * e_star) * (age_att / 60.0) ** eta

    def beir_vii_risk(self, beta, gamma, eta, dose_Sv, age_exp, age_att, baseline_rate=None):
        """
        Calcula o risco de câncer excedente (Excess Relative Risk - ERR) conforme o modelo BEIR VII.

        Fórmula:
        Risco excedente = beta * ERR(e,a) * dose_Sv

        Onde:
        - beta, gamma, eta são parâmetros do órgão e sexo (ver tabelas BEIR VII).
        - ERR(e,a) é calculado pelo método err_factor.
        - dose_Sv é a dose absorvida em Sievert.
        - baseline_rate (opcional) é a taxa de incidência basal para o órgão/população, podendo ser usada para calcular risco absoluto.

        Referência:
        - BEIR VII, National Academy of Sciences, Seção 12, páginas 291-294.

        Tratamento de erro:
        - Se algum parâmetro for inválido, retorna erro e loga a exceção.
        """
        excess = beta * self.err_factor(age_exp, age_att, gamma, eta) * dose_Sv
        return baseline_rate * (1 + excess) if baseline_rate is not None else excess

    def beir_v_risk(self, beta, dose_Sv, age_exp, age_att, baseline_rate=None):
        """
        Calcula o risco de câncer excedente conforme o modelo BEIR V.

        Fórmula:
        risco = r0(a,s) * [1 + (alpha2*D + alpha3*D^2) * modificador]

        Onde:
        - r0(a,s): taxa basal de incidência de câncer para a idade (a) e sexo (s), podendo ser informada por baseline_rate.
        - D: dose absorvida em Sievert.
        - alpha2 e alpha3: coeficientes de risco definidos pelo BEIR V (valores padrão: alpha2=0.243, alpha3=0.271).
        - modificador: fator que depende do tempo desde a exposição (t = idade_avaliacao - idade_exposicao) e parâmetros beta específicos do BEIR V.
        - beta: parâmetro de ajuste do modelo para diferentes faixas etárias e intervalos de tempo desde a exposição (ver tabelas BEIR V).

        O método aplica diferentes valores de beta conforme a idade de exposição e o tempo decorrido desde a exposição, seguindo as recomendações do BEIR V.

        Referência:
        - BEIR V, National Academy of Sciences, capítulo sobre modelos de risco, tabelas e fórmulas para cálculo de risco de câncer induzido por radiação.

        Tratamento de erro:
        - Se algum parâmetro for inválido, retorna erro e loga a exceção.
        """
        ALPHA2 = 0.243
        ALPHA3 = 0.271
        BETA_V_PARAMS = {1: 4.885, 2: 2.380, 3: 2.367, 4: 1.638}
        D = dose_Sv
        term = ALPHA2 * D + ALPHA3 * D ** 2
        t = age_att - age_exp
        if age_exp <= 20:
            if t <= 15:
                exp_term = math.exp(BETA_V_PARAMS[1])
            elif t <= 25:
                exp_term = math.exp(BETA_V_PARAMS[2])
            else:
                exp_term = None
        else:
            if t <= 25:
                exp_term = math.exp(BETA_V_PARAMS[3])
            elif t <= 30:
                exp_term = math.exp(BETA_V_PARAMS[4])
            else:
                exp_term = None
        factor = term * exp_term if exp_term is not None else term
        return baseline_rate * (1 + factor) if baseline_rate is not None else factor

    def calcular(self):
        """
        Executa o cálculo de riscos, gera CSV e log.
        """
        try:
            os.makedirs(self.pasta_saida, exist_ok=True)
            # Utiliza o mesmo timestamp do pipeline para manter rastreabilidade
            ts = self.timestamp if self.timestamp else datetime.now().strftime("%Y%m%d%H%M%S")
            base = f"3_calculated_risks_ee{int(self.idade_exposicao)}_ea{int(self.idade_atual)}_{ts}"
            base_log = f"4_execution_log_ee{int(self.idade_exposicao)}_ea{int(self.idade_atual)}_{ts}"
            out_csv = os.path.join(self.pasta_saida, base + ".csv")
            out_log = os.path.join(self.pasta_saida, base_log + ".log")
            # Remove todos os handlers existentes para garantir configuração correta do logging
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            logging.basicConfig(
                filename=out_log,
                filemode='w',
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            df_doses = pd.read_csv(self.csv_entrada, sep=';', decimal='.')
            df_params = pd.read_csv(self.params_csv, sep=';')
            csv_gamma = dict(zip(df_params['hotspot_organ'], df_params['gamma']))
            csv_eta = dict(zip(df_params['hotspot_organ'], df_params['eta']))
            baseline_vii = {}
            baseline_v = {}

            def calcular_riscos(df_doses, df_params, age_exp, age_att, model_choice, gamma_map, eta_map, baseline_vii, baseline_v):
                if 'organ/stabiliy_class_dose_class_distance_km' in df_doses.columns:
                    df_doses = df_doses.rename(columns={'organ/stabiliy_class_dose_class_distance_km': 'organ'})
                else:
                    raise KeyError("Coluna 'organ/stabiliy_class_dose_class_distance_km' não encontrada.")
                scenarios = [c for c in df_doses.columns if c != 'organ']
                resultados = []
                for sex in ['M', 'F']:
                    gender = 'male' if sex == 'M' else 'female'
                    df = df_doses.merge(
                        df_params[['hotspot_organ', 'beta_M', 'beta_F']],
                        left_on='organ', right_on='hotspot_organ',
                        how='left'
                    ).copy()
                    df['beta'] = df.apply(lambda r: r['beta_M'] if sex == 'M' else r['beta_F'], axis=1)
                    df.insert(0, 'age_after', int(age_att))
                    df.insert(0, 'age_in_exposition_years', int(age_exp))
                    df.insert(0, 'gender', gender)
                    for idx in df.index:
                        organ = df.at[idx, 'organ']
                        beta = df.at[idx, 'beta']
                        gamma = gamma_map.get(organ, 0.0)
                        eta = eta_map.get(organ, 0.0)
                        for cen in scenarios:
                            # dose_mSv = float(df.at[idx, cen])
                            # dose_Sv = dose_mSv / 1000.0
                            dose_Sv = float(df.at[idx, cen])
                            if model_choice == 'auto':
                                modelo = 'vii' if (dose_Sv*1000) < 100 else 'v'
                            else:
                                modelo = model_choice
                            if modelo == 'vii':
                                risco = self.beir_vii_risk(beta, gamma, eta, dose_Sv, age_exp, age_att)
                                modelo_nome = 'BEIR_VII'
                            else:
                                risco = self.beir_v_risk(beta, dose_Sv, age_exp, age_att)
                                modelo_nome = 'BEIR_V'
                            # Log detalhado conforme o script original
                            logging.info(
                                f"Sex:{gender},ExpAge:{age_exp},AttAge:{age_att},"
                                f"Organ:{organ},Scenario:{cen},DoseSv:{dose_Sv:.2e},"
                                f"Model:{modelo_nome},Beta:{beta:.2e},Gamma:{gamma},"
                                f"Eta:{eta},Risk:{risco:.2e}"
                            )
                            df.at[idx, cen] = risco
                    resultados.append(df)
                return pd.concat(resultados, ignore_index=True)
            df_risk = calcular_riscos(
                df_doses, df_params,
                self.idade_exposicao, self.idade_atual,
                self.modelo,
                csv_gamma, csv_eta,
                baseline_vii, baseline_v
            )
            df_risk.to_csv(out_csv, sep=';', index=False, decimal='.', float_format='%.2e')
            logging.info(f"Arquivo de riscos gerado: {out_csv}")
            print(f"Arquivo '{out_csv}' criado com sucesso.")
            print(f"Arquivo de log gerado em: {out_log}")
        except Exception as e:
            logging.error(f"Erro no cálculo de riscos: {e}")

# =========================================
# Classe HotspotPipeline
# =========================================
class HotspotPipeline:
    """
    Classe que orquestra todo o fluxo do processamento HotSpot.
    """
    def __init__(self, pasta_entrada, idade_exposicao, idade_atual, pasta_saida, params_csv):
        self.pasta_entrada = pasta_entrada
        self.idade_exposicao = idade_exposicao
        self.idade_atual = idade_atual
        self.pasta_saida = pasta_saida
        self.params_csv = params_csv

    def executar(self):
        """
        Executa todo o fluxo: extração, transposição e cálculo de risco.
        """
        try:
            os.makedirs(self.pasta_saida, exist_ok=True)
            # Gerar timestamp único para todos os arquivos deste processo
            agora = datetime.now()
            ts = agora.strftime("%Y%m%d%H%M%S") # Formato: YYYYMMDDHHmmSS 
            # Nomes dos arquivos com timestamp
            csv_tabular = os.path.join(self.pasta_saida,    f'1_hotspot_extract_ee{int(self.idade_exposicao)}_ea{int(self.idade_atual)}_{ts}.csv')
            csv_transposto = os.path.join(self.pasta_saida, f'2_hotspot_transpose_ee{int(self.idade_exposicao)}_ea{int(self.idade_atual)}_{ts}.csv')
            # Passar o caminho do arquivo tabular para o extrator
            extrator = ExtratorHotspot(self.pasta_entrada, csv_tabular)
            extrator.extrair()
            # Passar o caminho do arquivo transposto para o transpositor 
            transpositor = TranspositorHotspot(csv_tabular, csv_transposto)
            transpositor.transpor()
            # Passar o timestamp para o cálculo de risco
            calc = CalculadoraRisco(csv_transposto, self.params_csv, self.pasta_saida, self.idade_exposicao, self.idade_atual, timestamp=ts)
            calc.calcular()
            print('Fluxo completo executado com sucesso.')
        except Exception as e:
            logging.error(f"Erro no pipeline HotSpot: {e}")
            print(f"Erro ao executar o pipeline: {e}")

# =========================================
# Interface CLI
# =========================================
# def main():
#     """
#     Interface de linha de comando para o pipeline HotSpot.
#     """
#     parser = argparse.ArgumentParser(description='Pipeline unificado HotSpot: extração, transposição e cálculo de risco.')
#     parser.add_argument('--input_dir', help='Pasta com os arquivos .txt do HotSpot', default='fonte_file_hotspot')
#     parser.add_argument('--exp_age', type=float, required=True, help='Idade na data da exposição')
#     parser.add_argument('--att_age', type=float, required=True, help='Idade atual')
#     parser.add_argument('--output_dir', help='Pasta para salvar os arquivos de saída', default='output_dir')
#     parser.add_argument('--params_csv', help='CSV de parâmetros BEIR VII', default='dados_referencia/beirVII_hotspot_organ_equivalance_parameters.csv')
#     args = parser.parse_args()
#     pipeline = HotspotPipeline(
#         pasta_entrada=args.input_dir,
#         idade_exposicao=args.exp_age,
#         idade_atual=args.att_age,
#         pasta_saida=args.output_dir,
#         params_csv=args.params_csv
#     )
#     pipeline.executar()

# if __name__ == '__main__':
#     main()

# Para executar, rode o comando:
# python main.py --input_dir fonte_file_hotspot/Rocco --exp_age 10 --att_age 15 --output_dir output_dir