from flask import Blueprint,render_template,request,flash,redirect,url_for,session,g
from flaskr.models import User,Permission,Role
from flaskr import db
from flaskr.permission import ALL_PERMISSION
from functools import wraps
from werkzeug.security import check_password_hash
bp=Blueprint("login",__name__)

@bp.before_app_request
def load_user():
    if "username" in session:
        user_id=session.get('username')
        g.user=db.session.execute(db.select(User).where(User.user_id==user_id)).scalar_one()
    else:
        g.user=None
@bp.route("/admin-login",methods=['GET','POST'])
def user_login():
    if request.method=='POST':
        if request.form['username'] =="" and request.form['password']=="":
            flash("You should feel all the form")
        user=db.session.execute(db.select(User).where(User.email==request.form['username'])).scalar_one_or_none()
        if user is None:
            flash("You are not register")
            return redirect(url_for('login.user_login'))
        elif not check_password_hash(user.password,request.form['password']):
            flash("Password mismatch")
            return redirect(url_for('login.user_login'))
        else:
            session.clear()
            session['username']=user.user_id
            flash("Successfully Login")
            return redirect(url_for('index.dashboard'))
    # print(g.user)
    return render_template("login/admin_login.html")

@bp.route('/logout')
def logout():
    session.pop('username',None)
    flash("Successfully Logout")
    return redirect(url_for('login.user_login'))


def ensure_permission_exists():
    for all_permission in ALL_PERMISSION:
        permission=Permission.query.filter_by(name=all_permission['name']).first()
        if not permission:
            new_permission=Permission(name=all_permission['name'])
            db.session.add(new_permission)
    try:
        db.session.commit()
    except Exception as e:
        flash(f"{e}")
        return redirect(url_for('login.user_login'))

def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ensure_permission_exists()
            if g.user is None:
                flash("You are not allow")
                return redirect(url_for('login.user_login'))
            if g.user.is_active==False:
                flash("You are not active user")
                return redirect(url_for('login.user_login'))
            if g.user.role is None:
                flash("You have no permission")
                return redirect(url_for('login.user_login'))
            user_permission=[permission.name for permission in g.user.role.permission]
            if g.user.role.name !='superuser' and permission_name not in user_permission:
                session.clear()
                flash("You are not allow")
                return redirect(url_for('login.user_login'))
            return func(*args, **kwargs)
        return wrapper
    return decorator


# def login_required(*usr):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             if g.user is None:
#                 flash("You are not allow")
#                 return redirect(url_for('login.user_login'))
#             if g.user.user_type not in usr:
#                 session.clear()
#                 flash("You are not allow")
#                 return redirect(url_for('login.user_login'))
#             if g.user.is_active==False:
#                 flash("You are not allow")
#                 return redirect(url_for('login.user_login'))
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator