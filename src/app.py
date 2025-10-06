from flask import Flask
from flask_cors import CORS
from .routes.forum_routes import bp as forum_bp
from .routes.profile_routes import bp as profile_bp
from .routes.breakroom_routes import bp as breakrooms_bp  # 👈 ADD THIS
from .service.forum_service import ForumService
from .service.profile_service import ProfileService
from .auth import init_cognito
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["FORUM_SERVICE"] = ForumService()
    app.config["PROFILE_SERVICE"] = ProfileService()
    app.config.update(
        COGNITO_REGION="eu-north-1",
        COGNITO_USER_POOL_ID="eu-north-1_LRB1Cr2sA",
        COGNITO_APP_CLIENT_ID="c2377oft10p8nb7isiemn2hg2"
    )
    init_cognito(app)

    app.register_blueprint(forum_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(breakrooms_bp)

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    @app.get("/health")
    def health(): 
        return {"ok": True}, 200
    
    return app

app = create_app()
