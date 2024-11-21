# rotas.py
from flask import render_template, request, redirect, url_for, session, flash, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

# Conexão com o banco de dados
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def configurar_rotas(app):
    # Rota para a página inicial
    @app.route('/')
    def index():
        conn = get_db_connection()
        produtos = conn.execute('SELECT * FROM produtos').fetchall()
        conn.close()
        return render_template('index.html', produtos=produtos)

    # Rota para registro de usuários
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            tipo = request.form['tipo']

            if not nome or not email or not senha:
                flash('Todos os campos são obrigatórios.', 'danger')
                return redirect(url_for('register'))

            conn = get_db_connection()
            if conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone():
                flash('Email já está em uso.', 'danger')
                conn.close()
                return redirect(url_for('register'))

            senha_hash = generate_password_hash(senha)
            conn.execute('INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)',
                         (nome, email, senha_hash, tipo))
            conn.commit()
            conn.close()
            flash('Registro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    # Rota para login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            senha = request.form['senha']

            conn = get_db_connection()
            usuario = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
            conn.close()

            if usuario and check_password_hash(usuario['senha'], senha):
                session['user_id'] = usuario['id']
                session['user_type'] = usuario['tipo']
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Email ou senha incorretos.', 'danger')
        return render_template('login.html')

    # Rota para o painel do vendedor
    @app.route('/seller_dashboard', methods=['GET', 'POST'])
    def seller_dashboard():
        if 'user_id' not in session or session['user_type'] != 'vendedor':
            flash('Acesso negado. Apenas vendedores podem acessar esta página.')
            return redirect(url_for('index'))

        if request.method == 'POST':
            nome = request.form['nome']
            descricao = request.form['descricao']
            preco = request.form['preco']
            unidade = request.form['unidade']
            vendedor_id = session['user_id']

            # Lidar com o upload da imagem
            imagem = request.files['imagem']
            if imagem:
                # Salvar a imagem no diretório especificado
                imagem_filename = secure_filename(imagem.filename)
                imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], imagem_filename))
                imagem_path = os.path.join('uploads', imagem_filename)  # Caminho relativo para o banco de dados

                # Inserir o produto no banco de dados
                conn = get_db_connection()
                conn.execute('INSERT INTO produtos (vendedor_id, nome, descricao, preco, unidade, imagem) VALUES (?, ?, ?, ?, ?, ?)',
                             (vendedor_id, nome, descricao, preco, unidade, imagem_path))
                conn.commit()
                conn.close()
                flash('Produto adicionado com sucesso!')
                return redirect(url_for('seller_dashboard'))

        return render_template('seller_dashboard.html')

    # Rota para adicionar produtos ao carrinho
    @app.route('/add_to_cart/<int:produto_id>', methods=['POST'])
    def add_to_cart(produto_id):
        if 'user_id' not in session:
            flash('Você precisa estar logado para adicionar produtos ao carrinho.')
            return redirect(url_for('login'))

        usuario_id = session['user_id']
        quantidade = request.form['quantidade']

        conn = get_db_connection()
        conn.execute('INSERT INTO carrinho (usuario_id, produto_id, quantidade) VALUES (?, ?, ?)',
                     (usuario_id, produto_id, quantidade))
        conn.commit()
        conn.close()
        flash('Produto adicionado ao carrinho com sucesso!')
        return redirect(url_for('index'))

    # Rota para visualizar o carrinho de compras
    @app.route('/cart')
    def cart():
        if 'user_id' not in session:
            flash('Você precisa estar logado para ver o carrinho.')
            return redirect(url_for('login'))

        usuario_id = session['user_id']
        conn = get_db_connection()
        itens_carrinho = conn.execute('''
            SELECT p.nome, p.preco, c.quantidade
            FROM carrinho c
            JOIN produtos p ON c.produto_id = p.id
            WHERE c.usuario_id = ?
        ''', (usuario_id,)).fetchall()
        conn.close()

        return render_template('cart.html', itens=itens_carrinho)

    # Rota para finalizar a compra
    @app.route('/checkout')
    def checkout():
        # Aqui você pode implementar a lógica para finalizar a compra
        return render_template('checkout.html')

    # Rota para processar o pagamento
    @app.route('/process_payment', methods=['POST'])
    def process_payment():
        card_number = request.form['card_number']
        card_name = request.form['card_name']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']

        # Aqui você pode adicionar a lógica para processar o pagamento
        # Por exemplo, você pode integrar com uma API de pagamento

        flash('Pagamento processado com sucesso! Obrigado pela sua compra.')
        return redirect(url_for('index'))