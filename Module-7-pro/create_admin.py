from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash


app = create_app()

with app.app_context():

    email = "admin@gmail.com"
    password = "admin123"

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        print("Admin user already exists!")
    else:
        admin = User(
            name="Admin",
            email=email,
            password=generate_password_hash(password),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("✅ Admin user created successfully!")
        print("Email:", email)
        print("Password:", password)