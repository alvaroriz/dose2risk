import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, session
from flask_babel import Babel, gettext as _
from werkzeug.utils import secure_filename

# Configurações iniciais
CAMINHO_UPLOAD = 'uploads'
CAMINHO_SAIDA = 'saidas'
EXTENSOES_PERMITIDAS = {'txt'}

from datetime import datetime
import shutil
import uuid

# Criação das pastas, se não existirem
os.makedirs(CAMINHO_UPLOAD, exist_ok=True)
os.makedirs(CAMINHO_SAIDA, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'segredo_simples_para_flash'  # Necessário para mensagens flash

# --- Configuração do Babel para Internacionalização (i18n) ---
LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'pt_BR': 'Português'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'pt_BR'
app.config['LANGUAGES'] = LANGUAGES

def get_locale():
    """
    Determina o idioma a ser usado para a requisição.
    Primeiro, verifica se o idioma está definido na sessão do usuário.
    Caso contrário, tenta encontrar a melhor correspondência com base no cabeçalho Accept-Language do navegador.
    """
    try:
        # 1. Tenta obter o idioma da sessão do usuário
        lang = session.get('lang')
        if lang in app.config['LANGUAGES']:
            return lang
        # 2. Caso contrário, tenta usar o melhor idioma do navegador do usuário
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys())
    except RuntimeError:
        # Se estiver fora de um contexto de requisição, retorna o padrão
        return app.config['BABEL_DEFAULT_LOCALE']

babel = Babel(app, locale_selector=get_locale)

@app.context_processor
def inject_locale():
    """
    Injeta a função get_locale no contexto do template para que possa ser usada
    para determinar o idioma ativo.
    """
    return dict(get_locale=get_locale)

# Rota para definir o idioma
@app.route('/lang/<string:lang>')
def set_language(lang):
    """
    Define o idioma preferido do usuário na sessão.
    Redireciona o usuário de volta para a página de onde veio.
    """
    if lang in app.config['LANGUAGES']:
        session['lang'] = lang
        # flash(_('Idioma alterado com sucesso!'))
    else:
        flash(_('Idioma não suportado.'))
    # Redireciona para a página anterior, ou para a 'index' como fallback
    return redirect(request.referrer or url_for('index'))
# --- Fim da Configuração do Babel ---

# Função para verificar extensão permitida
def extensao_permitida(nome_arquivo):
    """
    Verifica se o arquivo possui extensão .txt
    """
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

@app.route('/')
def index():
    """
    Renderiza a página inicial com o formulário de upload.
    """
    return render_template('index.html')

@app.route('/sobre')
def sobre():
    """
    Renderiza a página 'Sobre'.
    """
    return render_template('sobre.html')


@app.route('/documentacao')
def documentacao():
    """
    Renderiza a página de 'Documentação'.
    """
    return render_template('documentacao.html')


@app.route('/privacidade')
def privacidade():
    """
    Renderiza a página de 'Política de Privacidade'.
    """
    return render_template('privacidade.html')


@app.route('/termos')
def termos():
    """
    Renderiza a página de 'Termos de Serviço'.
    """
    return render_template('termos.html')


@app.route('/suporte')
def suporte():
    """
    Renderiza a página de 'Suporte'.
    """
    return render_template('suporte.html')


@app.route('/contato')
def contato():
    """
    Renderiza a página de 'Contato'.
    """
    return render_template('contato.html')


def validar_arquivo_hotspot(stream):
    """
    Valida se o arquivo se parece com um arquivo de relatório HotSpot.
    Lê o início do arquivo para verificar a presença de palavras-chave essenciais.
    Retorna True se for válido, False caso contrário.
    """
    try:
        # Lê uma porção inicial do arquivo para verificação (4KB é suficiente)
        inicio_arquivo = stream.read(4096).decode('utf-8', errors='ignore')
        stream.seek(0)  # Reposiciona o ponteiro para o início do stream

        # Palavras-chave que devem estar presentes em um arquivo HotSpot válido.
        # Baseado na análise de arquivos de entrada de exemplo fornecidos pelo usuário.
        palavras_chave_obrigatorias = [
            "HotSpot",
            "Physical Stack Height",
            "Wind Speed",
            "Stability Class"
        ]

        # Verifica se todas as palavras-chave estão presentes (ignorando maiúsculas/minúsculas)
        texto_lower = inicio_arquivo.lower()
        if not all(palavra.lower() in texto_lower for palavra in palavras_chave_obrigatorias):
            return False

        # Se chegou até aqui, o arquivo é considerado válido
        return True

    except Exception as e:
        # Em caso de erro na leitura, assume que o arquivo é inválido
        # Em um ambiente de produção, seria ideal logar o erro.
        print(f"Erro durante a validação do arquivo: {e}")
        return False

@app.route('/upload', methods=['POST'])
def upload_arquivos():
    """
    Recebe múltiplos arquivos .txt, valida o conteúdo e salva os válidos
    em uma subpasta única para a execução.
    """
    try:
        if 'arquivos' not in request.files:
            flash(_('Nenhum campo de arquivo na requisição.'), 'error')
            return redirect(request.url)

        arquivos = request.files.getlist('arquivos')
        
        if not arquivos or all(not f.filename for f in arquivos):
            flash(_('Nenhum arquivo selecionado. Por favor, escolha um ou mais arquivos.'), 'warning')
            return redirect(url_for('index'))

        nomes_validos = []
        nomes_invalidos = []
        
        id_execucao = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + str(uuid.uuid4())[:8]
        pasta_upload = os.path.join(CAMINHO_UPLOAD, id_execucao)
        
        for arquivo in arquivos:
            if not arquivo.filename:
                continue

            nome_seguro = secure_filename(arquivo.filename)
            if extensao_permitida(nome_seguro) and validar_arquivo_hotspot(arquivo.stream):
                if not os.path.exists(pasta_upload):
                    os.makedirs(pasta_upload, exist_ok=True)
                
                caminho = os.path.join(pasta_upload, nome_seguro)
                arquivo.save(caminho)
                nomes_validos.append(nome_seguro)
            else:
                nomes_invalidos.append(nome_seguro)

        if nomes_invalidos:
            msg = _('Os seguintes arquivos foram rejeitados por não serem arquivos HotSpot válidos ou por terem extensão não permitida: %(files)s', files=', '.join(nomes_invalidos))
            flash(msg, 'error')

        if not nomes_validos:
            if os.path.exists(pasta_upload):
                shutil.rmtree(pasta_upload)
            if not nomes_invalidos:
                 flash(_('Nenhum arquivo válido foi enviado. Verifique o formato e a extensão (.txt).'), 'error')
            return redirect(url_for('index'))

        return redirect(url_for('processar', id_execucao=id_execucao))

    except Exception as e:
        flash(_('Ocorreu um erro inesperado durante o upload: %(error)s', error=str(e)), 'error')
        return redirect(url_for('index'))

@app.route('/processar', methods=['GET', 'POST'])
def processar():
    """
    Solicita idades e executa o processamento real dos arquivos da execução.
    Usa subpastas únicas para uploads e saídas.
    """
    try:
        # Recupera id_execucao da query string ou do form
        id_execucao = request.args.get('id_execucao') or request.form.get('id_execucao')
        if not id_execucao:
            flash('Execução não identificada.')
            return redirect(url_for('index'))
        pasta_upload = os.path.join(CAMINHO_UPLOAD, id_execucao)
        pasta_saida = os.path.join(CAMINHO_SAIDA, id_execucao)
        os.makedirs(pasta_upload, exist_ok=True)
        os.makedirs(pasta_saida, exist_ok=True)
        if request.method == 'GET':
            # Formulário recebe id_execucao oculto
            return render_template('form_idades.html', id_execucao=id_execucao)
        # POST: processar
        idade_exposicao = request.form.get('idade_exposicao', type=float)
        idade_atual = request.form.get('idade_atual', type=float)
        if idade_exposicao is None or idade_atual is None:
            flash('Informe as idades corretamente.')
            return redirect(url_for('processar', id_execucao=id_execucao))
        arquivos_entrada = os.listdir(pasta_upload)
        if not arquivos_entrada:
            flash('Nenhum arquivo para processar.')
            return redirect(url_for('index'))
        # Importa pipeline
        from hotspot_to_risk import HotspotPipeline
        params_csv = os.path.join('dados_referencia', 'beirVII_hotspot_organ_equivalance_parameters.csv')
        # Limpa a pasta de saída da execução antes de processar
        for f in os.listdir(pasta_saida):
            try:
                os.remove(os.path.join(pasta_saida, f))
            except Exception:
                pass
        # Executa pipeline
        pipeline = HotspotPipeline(
            pasta_entrada=pasta_upload,
            idade_exposicao=idade_exposicao,
            idade_atual=idade_atual,
            pasta_saida=pasta_saida,
            params_csv=params_csv
        )
        pipeline.executar()
        # Lista arquivos de saída da execução
        arquivos_saida = sorted([f for f in os.listdir(pasta_saida) if f.endswith('.csv') or f.endswith('.log')], reverse=True)
        if not arquivos_saida:
            flash('Nenhum arquivo de saída gerado.')
            return redirect(url_for('index'))
        return render_template('resultado.html', arquivos_saida=arquivos_saida, id_execucao=id_execucao)
    except Exception as e:
        flash(f'Erro no processamento: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download/<id_execucao>/<nome_arquivo>')
def download_arquivo(id_execucao, nome_arquivo):
    """
    Disponibiliza o download de um arquivo da pasta de saída da execução.
    """
    try:
        pasta_saida = os.path.join(CAMINHO_SAIDA, id_execucao)
        return send_from_directory(pasta_saida, nome_arquivo, as_attachment=True)
    except Exception as e:
        flash(f'Erro ao baixar arquivo: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
