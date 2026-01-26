from app.extensions import db


class Logistics(db.Model):
    __tablename__ = "logistics"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), unique=True)

    stage_prepare_loaded = db.Column(db.Boolean, default=False)
    time_prepare_loaded = db.Column(db.DateTime)

    stage_shipping = db.Column(db.Boolean, default=False)
    time_shipping = db.Column(db.DateTime)

    stage_arrived = db.Column(db.Boolean, default=False)
    time_arrived = db.Column(db.DateTime)

    stage_recycled = db.Column(db.Boolean, default=False)
    time_recycled = db.Column(db.DateTime)

    order = db.relationship("Order", back_populates="logistics")
