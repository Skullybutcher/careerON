from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from api.routes import api
from database.db import Base, engine

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize rate limiter
    from api.limiter import init_app
    init_app(app)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
