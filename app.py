from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. SETUP ET CONFIGURATIONs ---
app = Flask(name)
app.config['SECRET_KEY'] = 'UNE_CLE_SECRETE_A_MODIFIER_EN_PROD'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- 2. MODÈLES DE DONNÉES ---

# Modèle Utilisateur (SCRUM-17 & SCRUM-18)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128)) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modèle Produit (SCRUM-9 & SCRUM-11)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Fonction de chargement pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- 3. ROUTES DE L'APPLICATION ---

@app.route('/')
def index():
    return render_template('index.html', title='Accueil')

# SCRUM-17: Connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
        if user and user.check_password(password):
            login_user(user)
            flash('Connexion réussie!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    return render_template('login.html', title='Connexion')

# SCRUM-17: Inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà pris.', 'danger')
            return redirect(url_for('register'))
        if not username or not password or len(password) < 6:
            flash('Veuillez fournir des informations valides (mot de passe 6+).', 'danger')
            return redirect(url_for('register'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Compte créé avec succès.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Inscription')

# SCRUM-18: Déconnexion sécurisée
@app.route('/logout')
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

# SCRUM-9: Afficher la liste des produits
@app.route('/products')
@login_required 
def product_list():
    products = db.session.execute(db.select(Product).order_by(Product.name)).scalars().all()
    return render_template('products.html', products=products, title='Liste des produits')
    # SCRUM-11: Ajouter un nouveau produit
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        try:
            price = float(request.form.get('price'))
            quantity = int(request.form.get('quantity'))
        except (ValueError, TypeError):
            flash('Le prix et la quantité doivent être des nombres valides.', 'danger')
            return redirect(url_for('add_product'))

        new_product = Product(name=name, price=price, quantity=quantity)
        db.session.add(new_product)
        db.session.commit()

        flash(f'Le produit "{name}" a été ajouté avec succès.', 'success')
        return redirect(url_for('product_list'))

    return render_template('add_product.html', title='Ajouter un produit')


if name == 'main':
    with app.app_context():
        # Crée les tables User et Product
        db.create_all() 
    app.run(debug=True)

