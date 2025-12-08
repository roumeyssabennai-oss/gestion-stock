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

