import sys
import os
from flask import Flask, render_template, session, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path to reach backend_logic.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import warm_up as db_warm_up

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = os.environ.get('SECRET_KEY', 'clb-the-thao-secret-key-2024')
    
    CORS(app, supports_credentials=True)
    db_warm_up()

    # Register Consolidated API Blueprint
    from app.routes import register_routes
    register_routes(app)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):
        return render_template('index.html')

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    print("CLB The Thao Web App dang chay tai: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
