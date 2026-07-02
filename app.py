import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, Admin, Categoria

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Debes iniciar sesión para acceder al panel administrativo.'
    login_manager.login_message_category = 'error'

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    from routes.main import main_bp
    from routes.cart import cart_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        _crear_admin_default()
        _crear_categorias_default()

    return app


def _crear_admin_default():
    if not Admin.query.filter_by(username='cristhian').first():
        admin = Admin(username='cristhian')
        admin.set_password('cris190901')
        db.session.add(admin)
        db.session.commit()


def _crear_categorias_default():
    if Categoria.query.count() == 0:
        for nombre in ['Regalos Personalizados', 'Decoraci\u00f3n', 'Accesorios', 'Joyer\u00eda']:
            db.session.add(Categoria(nombre=nombre))
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug)
