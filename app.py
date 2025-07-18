from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from api.routes import api
from database.db import Base, engine
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize rate limiter
    from api.limiter import init_app
    init_app(app)
    
    # Enable CORS with explicit configuration to allow frontend origin and methods
    CORS(app, origins=["http://localhost:8080"], supports_credentials=True, 
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
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
