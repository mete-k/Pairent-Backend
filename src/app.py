from flask import Flask
from routes.forum_routes import bp as forum_bp
from di import build_forum_service_local

def create_app():
    app = Flask(__name__)
    app.config["FORUM_SVC"] = build_forum_service_local()
    app.register_blueprint(forum_bp)

    @app.get("/health")
    def health():
        return {"ok": True}, 200

    return app

app = create_app()
