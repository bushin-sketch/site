import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import Address, db, Product, User
from models import Coupon

app = Flask(__name__)

# Configurações de Banco e Segurança
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SECRET_KEY'] = 'vulcan_industrial_2026'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Garante que a pasta de fotos exista
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Inicialização das extensões
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- INICIALIZAÇÃO DO BANCO ---
with app.app_context():
    db.create_all() 
    if not User.query.filter_by(email='admin@vulcan.com').first():
        admin = User(username='Admin Vulcan', email='admin@vulcan.com', 
                     password=generate_password_hash('admin123'), is_admin=True)
        db.session.add(admin)
        db.session.commit()

# --- ROTAS PRINCIPAIS ---

@app.route('/')
def index():
    produtos = Product.query.all()
    return render_template('index.html', produtos=produtos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('perfil_admin' if user.is_admin else 'index'))
        flash('Erro de login.')
    return render_template('cadastro_login/login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Verifica se o usuário já existe para evitar erro de integridade
        if User.query.filter_by(email=request.form.get('email')).first():
            flash('E-mail já cadastrado.')
            return redirect(url_for('cadastro'))
            
        novo = User(username=request.form.get('username'), 
                    email=request.form.get('email'), 
                    password=generate_password_hash(request.form.get('password')))
        db.session.add(novo)
        db.session.commit()
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('login'))
    return render_template('cadastro_login/cadastro.html')

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if current_user.is_admin: 
        return redirect(url_for('perfil_admin'))
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.endereco = request.form.get('endereco')
        db.session.commit()
        flash('Perfil atualizado!')
    return render_template('perfil.html')

@app.route('/perfil_admin', methods=['GET', 'POST'])
@login_required
def perfil_admin():
    if not current_user.is_admin: 
        abort(403)
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        if request.form.get('password'):
            current_user.password = generate_password_hash(request.form.get('password'))
        db.session.commit()
        flash('Dados do Admin atualizados!')
    return render_template('admin/perfil_admin.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin: 
        abort(403)
        
    if request.method == 'POST':
        file = request.files.get('imagem')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Persistência de estoque completa (resolvendo o problema de dados vazios)
            novo_p = Product(
                name=request.form.get('nome'), 
                price=float(request.form.get('preco') or 0), 
                category=request.form.get('categoria'),
                description=request.form.get('descricao'),
                image=filename,
                stock_p=int(request.form.get('p') or 0),
                stock_m=int(request.form.get('m') or 0),
                stock_g=int(request.form.get('g') or 0),
                stock_gg=int(request.form.get('gg') or 0)
            )
            
            db.session.add(novo_p)
            db.session.commit()
            flash('Produto publicado com sucesso!')
            return redirect(url_for('index'))
            
    return render_template('admin/admin.html')

@app.route('/product/<int:id>')
def product_detail(id):
    produto = Product.query.get_or_404(id)
    return render_template('product_detail.html', produto=produto)

# --- SISTEMA DE CARRINHO BLINDADO ---

@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    tamanho = request.form.get('size')
    if not tamanho:
        flash("Por favor, selecione um tamanho.")
        return redirect(url_for('product_detail', id=id))

    if 'cart' not in session:
        session['cart'] = []

    # Criar uma cópia da lista para garantir que a sessão perceba a mudança
    cart = list(session['cart'])
    cart.append({'id': id, 'tamanho': tamanho})
    session['cart'] = cart
    session.modified = True 
    
    flash("Produto adicionado ao carrinho!")
    return redirect(url_for('carrinho'))

@app.route('/carrinho')
def carrinho():
    itens_no_carrinho = []
    total = 0.0
    
    cart = session.get('cart', [])
    
    for item in cart:
        produto = Product.query.get(item['id'])
        if produto:
            itens_no_carrinho.append({
                'produto': produto,
                'tamanho': item['tamanho']
            })
            total += produto.price
            
    return render_template('carrinho/carrinho.html', itens=itens_no_carrinho, total=total)

@app.route('/limpar_carrinho')
def limpar_carrinho():
    session.pop('cart', None)
    flash("Carrinho limpo.")
    return redirect(url_for('index'))

@app.route('/institucional/<page>')
def institucional(page):
    try:
        return render_template(f'institucional/{page}.html')
    except:
        abort(404)

@app.route('/logout')
def logout():
    logout_user()
    flash("Sessão encerrada.")
    return redirect(url_for('index'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', [])
    if not cart: return redirect(url_for('index'))

    total = sum(Product.query.get(item['id']).price for item in cart if Product.query.get(item['id']))
    desconto = 0
    cupom_codigo = request.args.get('cupom') # Pega o cupom da URL via AJAX ou Refresh

    if cupom_codigo:
        cp = Coupon.query.filter_by(code=cupom_codigo.upper(), active=True).first()
    if cp:
        if total >= cp.min_purchase: # Valida se atingiu o mínimo
            desconto = (total * cp.discount_percent) / 100
            flash(f"Cupom {cp.code} aplicado!")
        else:
            flash(f"Este cupom só vale para compras acima de R$ {cp.min_purchase:.2f}")
    else:
        flash("Cupom inválido.")

    total_final = total - desconto

    if request.method == 'POST':
        session.pop('cart', None)
        return render_template('carrinho/sucesso.html')

    return render_template('carrinho/checkout.html', total=total, desconto=desconto, total_final=total_final)

@app.route('/admin/delete/<int:id>')
@login_required
def delete_product(id):
    if not current_user.is_admin: abort(403)
    p = Product.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Produto removido do drop.')
    return redirect(url_for('perfil_admin'))

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if not current_user.is_admin: abort(403)
    p = Product.query.get_or_404(id)
    if request.method == 'POST':
        p.name = request.form.get('nome')
        p.price = float(request.form.get('preco'))
        p.promo_price = float(request.form.get('promo_price') or 0)
        p.category = request.form.get('categoria')
        p.stock_p = int(request.form.get('p', 0))
        # ... atualizar outros tamanhos ...
        db.session.commit()
        return redirect(url_for('perfil_admin'))
    return render_template('admin/edit_product.html', p=p)

@app.route('/adicionar_endereco', methods=['POST'])
@login_required
def adicionar_endereco():
    novo_end = Address(
        cep=request.form.get('cep'),
        rua=request.form.get('rua'),
        numero=request.form.get('numero'),
        bairro=request.form.get('bairro'),
        cidade=request.form.get('cidade'),
        estado=request.form.get('estado'),
        user_id=current_user.id
    )
    db.session.add(novo_end)
    db.session.commit()
    flash('Endereço adicionado!')
    return redirect(url_for('perfil'))

@app.route('/deletar_endereco/<int:id>')
@login_required
def deletar_endereco(id):
    end = Address.query.get_or_404(id)
    if end.user_id == current_user.id:
        db.session.delete(end)
        db.session.commit()
        flash('Endereço removido.')
    return redirect(url_for('perfil'))

@app.route('/admin/cupons', methods=['GET', 'POST'])
@login_required
def admin_cupons():
    if not current_user.is_admin: 
        abort(403)
    
    # Toda a lógica de criação DEVE estar dentro deste if
    if request.method == 'POST':
        codigo_raw = request.form.get('codigo')
        desconto_raw = request.form.get('desconto')
        valor_min_raw = request.form.get('valor_min') or 0

        if codigo_raw and desconto_raw:
            codigo = codigo_raw.upper()
            desconto = int(desconto_raw)
            valor_min = float(valor_min_raw)

            # Primeiro verificamos se existe, DEPOIS criamos
            existente = Coupon.query.filter_by(code=codigo).first()
            
            if existente:
                flash(f'Erro: O cupom {codigo} já existe!')
            else:
                novo_cupom = Coupon(
                    code=codigo, 
                    discount_percent=desconto, 
                    min_purchase=valor_min
                )
                db.session.add(novo_cupom)
                db.session.commit()
                flash(f'Cupom {codigo} criado com sucesso!')
        else:
            flash("Preencha todos os campos corretamente.")

    # Esta parte roda tanto no GET quanto no POST para atualizar a lista
    cupons = Coupon.query.all()
    return render_template('admin/cupons.html', cupons=cupons)

@app.route('/admin/cupons/delete/<int:id>')
@login_required
def delete_coupon(id):
    if not current_user.is_admin: abort(403)
    cupom = Coupon.query.get_or_404(id)
    db.session.delete(cupom)
    db.session.commit()
    flash('Cupom removido.')
    return redirect(url_for('admin_cupons'))

if __name__ == '__main__':
    app.run(debug=True)