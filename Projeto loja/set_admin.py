from app import app, db, User
with app.app_context():
    user = User.query.filter_by(email='SEU_EMAIL_AQUI').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print("Bem vindo {name}!")