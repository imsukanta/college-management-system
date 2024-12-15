from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_wtf.csrf import CSRFProtect
csrf=CSRFProtect()
class Base(DeclarativeBase):
    pass
db=SQLAlchemy(model_class=Base)
def create_app():
    app=Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile("config.py",silent=True)
    app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///college_db.db"
    # app.config['SQLALCHEMY_DATABASE_URI']="mysql+pymysql://root:@localhost/college_db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

    csrf.init_app(app)
    db.init_app(app)
    #register all models here
    import flaskr.models
    # import flaskr.create_role
    with app.app_context():
        db.create_all()
    from . import index
    from . import student
    from . import login
    from . import user
    from . import dept
    from . import staff
    app.register_blueprint(dept.bp)
    app.register_blueprint(index.bp)
    app.register_blueprint(login.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(staff.bp)
    return app