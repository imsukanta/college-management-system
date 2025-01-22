from flask import Blueprint,render_template,request,flash,redirect,url_for,g
from flaskr.models import Role,Permission,User
from flaskr import db
from flaskr.login import permission_required
bp=Blueprint("role",__name__,url_prefix='/role')

@bp.route('/')
@permission_required('show_role_dashboard')
def role_dashboard():
    role=Role.query.all()
    return render_template('role_dashboard.html',role=role)

@bp.route('/add-role',methods=['POST','GET'])
@permission_required('add_role')
def add_role():
    if request.method=='POST':
        role_name=request.form['role_name']
        role_desc=request.form['role_desc']
        if not role_name and role_desc:
            flash("You should fill up all the form")
            return redirect(url_for('role.add_role'))
        new_role=Role(name=role_name,description=role_desc)
        db.session.add(new_role)
        db.session.commit()
        flash("Role successfully created")
        return redirect(url_for('role.role_dashboard'))
    return render_template('addfile/addRole.html')
@bp.route('/update-role/<int:id>',methods=['POST','GET'])
@permission_required('update_role')
def update_role(id):
    new_role=Role.query.get(id)#2
    user_role=User.query.get(g.user.user_id)
    permission=Permission.query.all()
    if g.user.role.name=='superuser':
        permission = Permission.query.all()
    else:
        permission = user_role.role.permission
    if request.method=='POST':
        role_name=request.form['role_name']
        role_desc=request.form['role_desc']
        permit=request.form.getlist('permit')
        new_role.permission=[]
        for permit in permit:
            add_permission=Permission.query.get(int(permit))
            new_role.permission.append(add_permission)
        db.session.commit()
        if not role_name and role_desc:
            flash("You should fill up all the form")
            return redirect(url_for('role.add_role'))
        if new_role.name != 'superuser':
            new_role.name=role_name
            new_role.description=role_desc
            try:
                db.session.commit()
                flash("Role and Permission successfully updated")
            except Exception as e:
                flash(f"Error: {e}")
        else:
            flash("Superuser can't update")
        return redirect(url_for('role.role_dashboard'))
    return render_template('updatefile/updateRole.html',role=new_role,permission=permission)

@bp.route('/delete-role/<int:id>')
@permission_required('delete_role')
def delete_role(id):
    role=Role.query.get(id)
    if role.name !='superuser':
        db.session.delete(role)
        db.session.commit()
        flash("Successfully deleted")
    else:
        flash("Superuser can't deleted")
    return redirect(url_for('role.role_dashboard'))