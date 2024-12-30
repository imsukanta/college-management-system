from flask import Blueprint,render_template,request,flash,redirect,url_for,session,g
from flaskr.models import User
from flaskr import db
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

# @bp.before_request
# def load_login_user():
#     user_id=session.get('username')
#     if user_id is None:
#         flash("You are not login")
#         g.user=None
#         return redirect(url_for('login.user_login'))
#     else:
#         g.user=db.session.execute(db.select(User).where(User.user_id==user_id)).scalar_one()
#     print(g.user)

# def is_admin(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('login.user_login'))
#         elif g.user.user_type!='admin':
#             return redirect(url_for('login.user_login'))
#         return view(**kwargs)
#     return wrapped_view

# def is_staff(*roles):
#     def decorator(view):
#         @wraps(view)
#         def wrapped_view(*args, **kwargs):
#             if g.user is None:
#                 flash("Please login")
#                 return redirect(url_for('login.user_login'))
            
#             if g.user.user_type not in roles:
#                 session.clear()
#                 flash("You are not allow")
#                 return redirect(url_for('login.user_login'))
#             if g.user.is_active==False:
#                 flash("You are not active")
#                 return redirect(url_for('login.user_login'))
#             return view(*args, **kwargs)
#         return wrapped_view
#     return decorator

def login_required(*usr):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.user is None:
                flash("You are not allow")
                return redirect(url_for('login.user_login'))
            if g.user.user_type not in usr:
                session.clear()
                flash("You are not allow")
                return redirect(url_for('login.user_login'))
            if g.user.is_active==False:
                flash("You are not allow")
                return redirect(url_for('login.user_login'))
            return func(*args, **kwargs)
        return wrapper
    return decorator