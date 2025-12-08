# --- Modèles de Base de Données (ORM) ---

class User(UserMixin, db.Model):
    """ Modèle pour les utilisateurs (authentification). """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Relation pour que l'utilisateur puisse accéder à ses produits
    products = relationship('Product', backref='owner', lazy=True)

    def set_password(self, password):
        """ Génère le hash du mot de passe. """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Vérifie le mot de passe hashé. """
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    """ Charge l'utilisateur depuis l'ID de session. """
    return db.session.get(User, int(user_id))

# Modèle de données pour les produits
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

from flask_login import login_required # Assurez-vous d'avoir cette importation

# ROUTE POUR AFFICHER LES PRODUITS
@app.route('/products')
@login_required # Sécurité : seule les utilisateurs connectés peuvent voir la liste
def product_list():
    # Récupère tous les produits triés par nom
    products = db.session.execute(db.select(Product).order_by(Product.name)).scalars().all()
    return render_template('products.html', products=products, title='Liste des produits')


# ROUTE POUR AJOUTER UN PRODUIT
@app.route('/add_product', methods=['GET', 'POST'])
@login_required # Oblige l'utilisateur à être connecté
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        
        # Validation des données numériques
        try:
            price = float(request.form.get('price'))
            quantity = int(request.form.get('quantity'))
        except (ValueError, TypeError):
            flash('Le prix et la quantité doivent être des nombres valides.', 'danger')
            return redirect(url_for('add_product'))

        # Création et ajout du nouveau produit
        new_product = Product(name=name, price=price, quantity=quantity)
        db.session.add(new_product)
        db.session.commit()

        flash(f'Le produit "{name}" a été ajouté avec succès.', 'success')
        return redirect(url_for('product_list')) # Redirige vers la liste des produits

    return render_template('add_product.html', title='Ajouter un produit')

