from flask import Blueprint,render_template,request,flash,redirect,url_for
from flaskr.models import User
from werkzeug.security import generate_password_hash
from flaskr import db
from flaskr.login import login_required

bp=Blueprint("user",__name__,url_prefix="/user")
@bp.route("/")
@login_required('admin','staff')
def user_dashboard():
    page=request.args.get('page',1,type=int)
    per_page=10
    users=User.query.paginate(page=page,per_page=per_page)
    return render_template("user.html",users=users)

@bp.route("/add-user",methods=["GET","POST"])
# @login_required('admin')
def add_user():
    if request.method=="POST":
        # print(request.form)
        is_active = request.form.get('confirmation') == 'true'
        user_types=request.form["user_types"]
        if user_types not in ['admin','staff','finance']:
            return "Invalid user type", 400
        if request.form['name'] and request.form['email'] and request.form['password1'] and request.form['password2'] and request.form['password1']==request.form['password2'] and request.form['user_types']:
            user=User(name=request.form['name'],email=request.form['email'],password=generate_password_hash(request.form['password1']),user_type=user_types,is_active=is_active)
            db.session.add(user)
            db.session.commit()
            flash('Successfully added')
            return redirect(url_for('user.add_user'))
        else:
            db.session.rollback()
            flash("Oops error")
            return redirect(url_for('user.add_user'))
            
    return render_template("addfile/addUser.html")

@bp.route("/delete-user/<int:id>")
@login_required('admin')
def delete_user(id):
    try:
        # user=db.get_or_404(User,id)
        db.session.execute(db.delete(User).where(User.user_id==id))
        # db.session.delete(user)
        db.session.commit()
        flash("Delete Successfully")
    except:
        db.session.rollback()
        flash("Not Deleted")
    return redirect(url_for("user.user_dashboard"))

@bp.route('/update/<int:id>',methods=["POST","GET"])
@login_required('admin')
def update_user(id):
    user=db.get_or_404(User,id)
    if request.method=="POST":
        user_types=request.form['user_types']
        is_active = request.form.get('confirmation') == 'true'
        if user_types not in ['admin','staff','finance']:
            return "Invalid user type", 400
        if request.form['name'] and request.form['email']:
            name=request.form['name']
            email=request.form['email']
            db.session.execute(db.update(User).where(User.user_id==id).values(name=name,email=email,user_type=user_types,is_active=is_active))
            db.session.commit()
            flash("Successfully updated")
        else:
            db.session.rollback()
            flash("You must fill")
        return redirect(url_for('user.user_dashboard'))
    return render_template('updatefile/updateUser.html',user=user)