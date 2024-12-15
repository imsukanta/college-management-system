from flaskr import Role, User, db

def create_roles():
    admin = Role(role_id=1, name='Admin')
    teacher = Role(role_id=2, name='Teacher')
    staff = Role(role_id=3, name='Staff')
    student = Role(role_id=4, name='Student')

    db.session.add(admin)
    db.session.add(teacher)
    db.session.add(staff)
    db.session.add(student)

    db.session.commit()
    print("Roles created successfully!")