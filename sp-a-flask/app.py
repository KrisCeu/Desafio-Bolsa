import os
import json
from flask import Flask, url_for, session, redirect, render_template_string
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_para_sessao' 

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# Permite rodar OIDC sem HTTPS (apenas para localhost/dev)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configuração do OAuth
oauth = OAuth(app)
oauth.register(
    name='keycloak',
    client_id='sp-a-client',
   
    client_secret='OqkS52LJK8NSUKX8f763z9T9Bi8LSqwQ', 
    
    # URL interna do Docker ou Host? 
    # Como o Python está rodando no seu PC (não no Docker ainda), 
    # ele consegue acessar o endereço que definimos no /etc/hosts
    server_metadata_url='http://idp.dominio-a.local:8081/realms/realm-a/.well-known/openid-configuration',
    
    client_kwargs={
        'scope': 'openid profile email'
    }
)

# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def home():
    user = session.get('user')
    if user:
        return f'''
            <h1>Olá, {user.get('name')}! 👋</h1>
            <p>Você está logado no SP-A.</p>
            <a href="/private"><button>Ver Auditoria (Área Segura)</button></a>
            <br><br>
            <a href="/logout">Sair</a>
        '''
    return '''
        <h1>Sistema SP-A (Público)</h1>
        <p>Você não está logado.</p>
        <a href="/login"><button>Login com Keycloak (Domínio A)</button></a>
    '''

@app.route('/login')
def login():
    # Manda o usuário para o Keycloak
    # O redirect_uri deve bater EXATAMENTE com o que configuramos no Keycloak
    redirect_uri = url_for('callback', _external=True)
    return oauth.keycloak.authorize_redirect(redirect_uri)

@app.route('/callback')
def callback():
    # O usuário voltou do Keycloak. Vamos trocar o código pelo token.
    try:
        token = oauth.keycloak.authorize_access_token()
        session['user'] = token.get('userinfo')
        session['token_full'] = token
        return redirect('/')
    except Exception as e:
        return f"<h1>Erro no login:</h1> <p>{e}</p>"

@app.route('/private')
def private():
    user = session.get('user')
    if not user:
        return redirect('/')
    
    # REQUISITO DO DESAFIO: Auditoria
    # Mostramos o 'sub' (quem é) e o 'iss' (quem emitiu/domínio)
    token_data = session.get('token_full')
    
    return render_template_string('''
        <h1>🔐 Dados de Auditoria</h1>
        <p><strong>Usuário (sub):</strong> {{ user.sub }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <p><strong>Origem (iss):</strong> {{ token.userinfo.iss }}</p>
        <hr>
        <h3>Token Completo (JSON):</h3>
        <pre>{{ dump }}</pre>
        <a href="/">Voltar</a>
    ''', user=user, token=token_data, dump=json.dumps(token_data, indent=2))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('token_full', None)
    return redirect('/')

if __name__ == '__main__':
    # host='0.0.0.0' é OBRIGATÓRIO para o Docker conseguir acessar o Flask
    app.run(debug=True, port=5000, host='0.0.0.0')

    