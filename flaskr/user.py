from flask import Blueprint,render_template,request,flash,redirect,url_for
from flaskr.models import User,Role
from werkzeug.security import generate_password_hash
from flaskr import db
import click
from flaskr.login import permission_required

bp=Blueprint("user",__name__,url_prefix="/user")
@bp.route("/")
@permission_required('show_user_dashboard')
def user_dashboard():
    page=request.args.get('page',1,type=int)
    per_page=10
    users=User.query.paginate(page=page,per_page=per_page)
    return render_template("user.html",users=users)

@bp.route("/add-user",methods=["GET","POST"])
@permission_required('add_user')
def add_user():
    role=Role.query.all()
    if request.method=="POST":
        is_active = request.form.get('confirmation') == 'true'
        role=request.form['role']
        role_id=Role.query.get(int(role))
        if role_id.name=="superuser":
            flash("You can't create superuser")
            return redirect(url_for('user.add_user'))
        if request.form['name'] and request.form['email'] and request.form['password1'] and request.form['password2'] and request.form['password1']==request.form['password2'] and role:
            user=User(name=request.form['name'],email=request.form['email'],password=generate_password_hash(request.form['password1']),is_active=is_active,role=role_id)
            db.session.add(user)
            db.session.commit()
            flash('Successfully added')
            return redirect(url_for('user.add_user'))
        else:
            db.session.rollback()
            flash("Oops error")
            return redirect(url_for('user.add_user'))
            
    return render_template("addfile/addUser.html",role=role)

@bp.route("/delete-user/<int:id>")
@permission_required('delete_user')
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
@permission_required('update_user')
def update_user(id):
    user=db.get_or_404(User,id)
    new_role=Role.query.all()
    if request.method=="POST":
        is_active = request.form.get('confirmation') == 'true'
        role=request.form['role']
        role_id=Role.query.get(int(role))
        if request.form['name'] and request.form['email']:
            name=request.form['name']
            email=request.form['email']
            db.session.execute(db.update(User).where(User.user_id==id).values(name=name,email=email,is_active=is_active,role_id=role_id.id))
            db.session.commit()
            flash("Successfully updated")
        else:
            db.session.rollback()
            flash("You must fill")
        return redirect(url_for('user.user_dashboard'))
    return render_template('updatefile/updateUser.html',user=user,new_role=new_role)

#create an superuser using command line interface
def create_superuser():
    name=click.prompt("Enter your name: ",type=str)
    email=click.prompt("Enter your email: ",type=str)
    password=click.prompt("Enter your password: ",type=str)
    role=Role.query.filter_by(name="superuser").first()
    check_email=User.query.filter_by(email=email).first()
    if check_email:
        print("Email already exists")
        exit()
    if not role:
        role_add=Role(name="superuser",description="Superuser can access everything")
        db.session.add(role_add)
        db.session.flush()
    user_add=User(name=name,email=email,password=generate_password_hash(password),is_active=True,role=role)
    db.session.add(user_add)
    db.session.commit()
    print(f"Superuser successfully created")