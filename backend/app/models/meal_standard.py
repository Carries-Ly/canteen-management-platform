from app.extensions import db


class MealStandard(db.Model):
    __tablename__ = "meal_standards"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    meal_type = db.Column(db.String(32), nullable=False)  # breakfast/lunch/dinner
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(16), default="enabled")  # enabled/disabled
    description = db.Column(db.String(256))
