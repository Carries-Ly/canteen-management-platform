from app.extensions import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    contact_person = db.Column(db.String(64))
    contact_phone = db.Column(db.String(32))
    address = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    customers = db.relationship("User", back_populates="company", lazy="dynamic")
    orders = db.relationship("Order", back_populates="company", lazy="dynamic")
