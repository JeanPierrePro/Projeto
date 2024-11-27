from flask import Flask
import os

app = Flask(__name__, 
            static_folder='static',  # define a pasta de arquivos estáticos
            static_url_path='/static')  # define o prefixo da URL para arquivos estáticos
app.secret_key = 'sua_chave_secreta'

# Defina o diretório para armazenar as imagens
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Certifique-se de que este diretório exista

# Crie o diretório se ele não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Importar e configurar as rotas
from rotas import configurar_rotas
configurar_rotas(app)

if __name__ == '__main__':
    app.run(debug=True)
