import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Product, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SECRET_KEY'] = 'chave_mestra_compton'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

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
            return redirect(url_for('index'))
        flash('E-mail ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        novo_usuario = User(
            username=request.form.get('username'),
            email=request.form.get('email'),
            password=generate_password_hash(request.form.get('password')),
            is_admin=False 
        )
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        if request.form.get('password'):
            current_user.password = generate_password_hash(request.form.get('password'))
        db.session.commit()
        flash('Perfil atualizado!', 'success')
        return redirect(url_for('perfil'))
    return render_template('perfil.html')

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
            novo_p = Product(
                name=request.form.get('nome'), 
                price=float(request.form.get('preco')), 
                category=request.form.get('categoria'),
                image=filename,
                stock_p=int(request.form.get('p') or 0),
                stock_m=int(request.form.get('m') or 0),
                stock_g=int(request.form.get('g') or 0),
                stock_gg=int(request.form.get('gg') or 0)
            )
            db.session.add(novo_p)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)