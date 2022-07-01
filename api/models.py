from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Quote(db.Model):
    user_id = db.Column(db.String(21), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)