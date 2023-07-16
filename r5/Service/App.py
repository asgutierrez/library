from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from r5.Service.Config import Service


app = Flask(__name__)
db = SQLAlchemy(app)


def init_app():
    """Create Flask App"""
    # Enable Cors
    CORS(app, supports_credentials=True)

    app.config.from_object(Service)

    @app.errorhandler(400)
    def e400(_err):
        """Bad request"""
        return jsonify(), 400

    @app.errorhandler(404)
    def e404(_err):
        """Page not found"""
        return jsonify(), 404

    @app.errorhandler(Exception)
    def e500(_err):
        """Page not found"""
        app.log_exception(_err)
        return jsonify(), 500

    # Enable JWT
    JWTManager(app)

    # Set Database
    db.init_app(app)

    return app
