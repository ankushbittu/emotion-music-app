from flask import Flask
from flask_cors import CORS
from extensions import db, jwt

def create_app():
    app = Flask(__name__)
    
    # Configuring the SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT configuration (set a strong secret key in production)
    app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this for production
    
    # Initialize the database and JWT manager with the app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Import routes here to avoid circular imports
    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Create tables within app context
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)