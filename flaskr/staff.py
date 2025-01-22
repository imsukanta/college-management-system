from flask import Blueprint,render_template,request,redirect,url_for,flash
from flaskr.models import Dept,Staff
from flaskr import db
from datetime import datetime
import random 
import string
from flaskr.login import permission_required
from werkzeug.security import generate_password_hash
bp=Blueprint('staff',__name__,url_prefix='/staff')

def generate_employee_id(prefix="MIT", length=6):
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(characters, k=length))
    employee_id = f"{prefix}-{random_part}"
    return employee_id

@bp.route("/")
@permission_required('staff_dashboard_show')
def staff_dashboard():
    page=request.args.get('page',1,type=int)
    per_page=10
    staff=Staff.query.paginate(page=page,per_page=per_page)
    return render_template('staff.html',staff=staff)

@bp.route('/add-staff',methods=['POST','GET'])
@permission_required('add_staff')
def add_staff():
    dept=db.session.execute(db.select(Dept)).scalars()
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        mobile_no=request.form['mobile_no']
        dob=request.form['date_of_birth']
        address=request.form['address']
        gender=request.form['gender']
        designation=request.form['designation']
        department=request.form['department']
        qualification=request.form['qualification']
        year_of_experience=request.form['year_of_experience']
        is_active=request.form.get('is_active')=='true'
        if len(mobile_no)!=10:
            flash('Mobile no atleast 10 digits')
            return redirect(url_for('staff.add_staff'))
        if gender not in ["Male","Female"]:
            flash("Gender Mistake")
            return redirect(url_for('staff.add_staff'))
        date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
        password=dob.replace("-","")
        print(password)
        dpt=db.session.execute(db.select(Dept).where(Dept.dept_id==department)).scalar_one()
        staff=Staff(emp_id=generate_employee_id(),name=name,email=email,mobile_no=mobile_no,date_of_birth=date_of_birth,address=address,gender=gender,designation=designation,department_id=dpt.dept_id,qualification=qualification,year_of_experience=year_of_experience,password=generate_password_hash(password),is_active=is_active)
        db.session.add(staff)
        db.session.commit()
        return redirect(url_for('staff.staff_dashboard'))
    return render_template('addfile/addStaff.html',dept=dept)

#delete staff
@bp.route('/delete/<int:id>')
@permission_required('delete_staff')
def delete_staff(id):
    try:
        db.session.execute(db.delete(Staff).where(Staff.staff_id==id))
        db.session.commit()
    except:
        db.session.rollback()
        flash("Got Error")
    return redirect(url_for('staff.staff_dashboard'))
@bp.route('/update/<int:id>',methods=['GET','POST'])
@permission_required('update_staff')
def update_staff(id):
    staff=db.session.execute(db.select(Staff).where(Staff.staff_id==id)).scalar_one_or_none()
    dept=db.session.execute(db.select(Dept)).scalars()
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        mobile_no=request.form['mobile_no']
        dob=request.form['date_of_birth']
        address=request.form['address']
        gender=request.form['gender']
        designation=request.form['designation']
        department=request.form['department']
        qualification=request.form['qualification']
        year_of_experience=request.form['year_of_experience']
        is_active=request.form.get('is_active')=='true'
        
        if len(mobile_no)!=10:
            flash('Mobile no atleast 10 digits')
            return redirect(url_for('staff.add_staff'))
        if gender not in ["Male","Female"]:
            flash("Gender Mistake")
            return redirect(url_for('staff.add_staff'))
        date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
        dpt=db.session.execute(db.select(Dept).where(Dept.dept_id==department)).scalar_one()
        db.session.execute(db.update(Staff).where(Staff.staff_id==id).values(name=name,email=email,mobile_no=mobile_no,date_of_birth=date_of_birth,address=address,gender=gender,designation=designation,department_id=dpt.dept_id,qualification=qualification,year_of_experience=year_of_experience,is_active=is_active))
        db.session.commit()
        return redirect(url_for("staff.staff_dashboard"))
    return render_template('updatefile/updateStaff.html',staff=staff,dept=dept)

@bp.route('/show-staff/<int:id>')
@permission_required('show_staff')
def show_staff(id):
    try:
        staff=db.session.execute(db.select(Staff).where(Staff.staff_id==id)).scalar_one_or_none()
    except:
        flash("Data Cannot Fetch")
        return redirect(url_for('staff.staff_dashboard'))
    return render_template("profile/teacher_profile.html",staff=staff)