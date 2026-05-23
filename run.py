from app.database import init_db
from app.producer import app
from app.threads import threads_bp

app.register_blueprint(threads_bp)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)