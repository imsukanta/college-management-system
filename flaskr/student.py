from flask import Blueprint,render_template,g,request,redirect,url_for,flash
from flaskr.login import login_required
from flaskr.models import Dept,Student,Session,Payment,Semester
from flaskr import db
from werkzeug.security import generate_password_hash
from datetime import datetime
import math
bp=Blueprint("student",__name__,url_prefix="/student")

def due_fees(id):
    student = Student.query.get(id)
    total_semesters = int(student.admission_session_obj.total_semester)
    start_semester = int(student.start_semester)
    semester_fee = int(student.total_fees) // (total_semesters - start_semester + 1)
    payments = Payment.query.filter_by(student_id=id).all()
    if payments:
        fees_paid = sum(payment.ammount_pay for payment in payments)
    else:
        fees_paid = 0
    current_semester = int(student.current_semester)
    fees_due = semester_fee * (current_semester - (start_semester - 1)) - fees_paid
    return max(fees_due, 0)

@bp.route("/")
@login_required('staff','admin')
def student_dashboard():
    page=request.args.get('page',1,type=int)
    per_page=10
    students=Student.query.paginate(page=page,per_page=per_page)
    return render_template("student.html",students=students)

#Add Student done Everything
@bp.route("/add-stuent",methods=['GET','POST'])
@login_required('admin')
def add_student():
    dept=db.session.execute(db.select(Dept)).scalars()
    sessionyear=Session.query.filter_by(is_active=True).first()
    sem=Semester.query.filter_by(is_active=True).all()
    if request.method=="POST":
        first_name=request.form['first_name']
        last_name=request.form['last_name']
        email=request.form['email']
        mobile_no=request.form['mobile_no']
        emergency_contact_name=request.form['emergency_contact_name']
        emergency_contact_number=request.form['emergency_contact_number']
        date_of_birth=request.form['date_of_birth']
        nationality=request.form['nationality']
        current_address=request.form['current_address']
        permanent_address=request.form['permanent_address']
        gender=request.form['gender']
        makaut_roll_no=request.form['makaut_roll_no']
        previous_qualifications=request.form['previous_qualifications']
        department=request.form['department']
        admission_date=request.form['admission_date']
        mode_of_admission=request.form['mode_of_admission']
        current_semester=request.form['current_semester']
        total_fees=request.form['total_fees']
        if int(current_semester)%2 ==0:
            flash("Start Semester should odd")
            return redirect(url_for('student.add_student'))
        if len(mobile_no)!=10:
            flash("Mobile No Should be 10 digits")
            return redirect(url_for('student.add_student'))
        if len(emergency_contact_number)!=10:
            flash("Emergency No Should be 10 digits")
            return redirect(url_for('student.add_student'))
        if gender not in ['Male','Female']:
            flash("Gender should be either male or female")
            return redirect(url_for('student.add_student'))
        if mode_of_admission not in ["entrance_exam","direct_admission"]:
            flash("Mode Of Admission Wrong")
            return redirect(url_for('student.add_student'))
        dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        dpt=db.session.execute(db.select(Dept).where(Dept.dept_id==department)).scalar_one()
        admit_date = datetime.strptime(admission_date, '%Y-%m-%d').date()
        is_active=request.form.get('confirmation')=='true'
        access_of_library=request.form.get('access_of_library')=='true'
        password=date_of_birth.replace("-","")
        try:
            student=Student(makaut_roll_no=makaut_roll_no,first_name=first_name,last_name=last_name,date_of_birth=dob,gender=gender,permanent_address=permanent_address,current_address=current_address,contact_number=mobile_no,email=email,nationality=nationality,emergency_contact_name=emergency_contact_name,emergency_contact_number=emergency_contact_number,previous_qualifications=previous_qualifications,department_id=dpt.dept_id,admission_date=admit_date,mode_of_admission=mode_of_admission,password=generate_password_hash(password),access_of_library=access_of_library,is_active=is_active,admission_session=sessionyear.id,current_semester=current_semester,current_session=sessionyear.id,start_semester=current_semester,total_fees=total_fees)
            db.session.add(student)
            db.session.commit()
            return redirect(url_for('student.student_dashboard'))
        except Exception as e:
            flash(f"Error Occured {e} ")
            return redirect(url_for('student.add_student'))
    return render_template('addfile/addStudent.html',dept=dept,session=sessionyear,sem=sem)

#show profile in admin section
@bp.route('/show-profile/<int:id>')
@login_required('admin')
def show_profile(id):
    student=Student.query.get(id)
    semester=int(student.total_fees)//(int(student.admission_session_obj.total_semester)-int(student.start_semester)+1)
    payment=Payment.query.filter_by(student_id=id).all()
    if payment:
        fees_paid=sum(payment.ammount_pay for payment in payment)
        fees_due=semester*(int(student.current_semester)-(int(student.start_semester)-1))-(fees_paid)
    else:
        fees_due=semester*(int(student.current_semester)-(int(student.start_semester)-1))
    print(fees_due)
    return render_template('profile/student_profile.html',student=student)

#delete profile
@bp.route('/delete-profile/<int:id>')
@login_required('admin')
def delete_profile(id):
    try:
        student=Student.query.get(id)
        db.session.delete(student)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Not Deleted")
    return redirect(url_for('student.student_dashboard'))

@bp.route("/update-profile/<int:id>",methods=['GET','POST'])
@login_required('admin')
def update_profile(id):
    sem=Semester.query.filter_by(is_active=True).all()
    dept=db.session.execute(db.select(Dept)).scalars()
    student=db.session.execute(db.select(Student).where(Student.id==id)).scalar_one_or_none()
    sessionyear=Session.query.filter_by(is_active=True).all()
    if request.method=="POST":
        first_name=request.form['first_name']
        last_name=request.form['last_name']
        email=request.form['email']
        mobile_no=request.form['mobile_no']
        emergency_contact_name=request.form['emergency_contact_name']
        emergency_contact_number=request.form['emergency_contact_number']
        date_of_birth=request.form['date_of_birth']
        nationality=request.form['nationality']
        gender=request.form['gender']
        previous_qualifications=request.form['previous_qualifications']
        department=request.form['department']
        mode_of_admission=request.form['mode_of_admission']
        current_semester=request.form['current_semester']
        total_fees=request.form['total_fees']
        if len(mobile_no)!=10:
            flash("Mobile No Should be 10 digits")
            return redirect(url_for('student.add_student'))
        if len(emergency_contact_number)!=10:
            flash("Emergency No Should be 10 digits")
            return redirect(url_for('student.add_student'))
        if gender not in ['Male','Female']:
            flash("Gender should be either male or female")
            return redirect(url_for('student.add_student'))
        if mode_of_admission not in ["entrance_exam","direct_admission"]:
            flash("Mode Of Admission Wrong")
            return redirect(url_for('student.add_student'))
        dpt=db.session.execute(db.select(Dept).where(Dept.dept_id==department)).scalar_one_or_none()
        print(dpt.dept_id)
        is_active=request.form.get('confirmation')=='true'
        access_of_library=request.form.get('access_of_library')=='true'
        db.session.execute(db.update(Student).where(Student.id==id).values(first_name=first_name,last_name=last_name,email=email,contact_number=mobile_no,nationality=nationality,emergency_contact_name=emergency_contact_name,emergency_contact_number=emergency_contact_number,previous_qualifications=previous_qualifications,department_id=dpt.dept_id,mode_of_admission=mode_of_admission,access_of_library=access_of_library,is_active=is_active,current_semester=current_semester,total_fees=total_fees))
        db.session.commit()
        return redirect(url_for('student.show_profile',id=student.id))
    return render_template('updatefile/updateStudent.html',student=student,dept=dept,session=sessionyear,sem=sem)

@bp.route('/payments/student-<int:student_id>')
def show_payment(student_id):
    student=Student.query.get(student_id)
    fees_due=due_fees(student_id)
    page=request.args.get('page',1,type=int)
    per_page=8
    payment = Payment.query.filter_by(student_id=student_id).paginate(page=page, per_page=per_page)
    return render_template("profile/show_student_pay.html",payment=payment,student=student,fees_due=fees_due)
@bp.route('/add-payment/<int:id>',methods=['GET','POST'])
def add_payment(id):
    sem=Semester.query.filter_by(is_active=True).all()
    # fee=Fees.query.filter_by(student_id=id).first()
    student=Student.query.get(id)
    fees_due=due_fees(student.id)
    print(fees_due)
    if request.method=="POST":
        amount=request.form['amount']
        is_verify=request.form.get('confirmation')=='true'
        semester=request.form['semester']
        
        if fees_due==0:
            flash("You Have No due")
            return redirect(url_for('student.show_payment',id=id))
        if amount and semester:
            payment=Payment(student_id=id,semester_id=int(semester),ammount_pay=amount,mode_of_payment="Cash",is_verified=is_verify)
            db.session.add(payment)
            db.session.commit()
            flash("Money Successful added")
            return redirect(url_for('student.show_payment',student_id=id))
        else:
            flash("Error Find")
            return redirect(url_for('student.add_payment',id=id))
    return render_template("addfile/addPayment.html",sem=sem,fees_due=fees_due)

@bp.route('/show-payment-details/<int:id>/<int:pay_id>',methods=['GET','POST'])
def payment_details(id,pay_id):
    payment=Payment.query.filter_by(student_id=id,payment_id=pay_id).first()
    if not payment:
        return "Not payment Details",404
    if request.method=="POST":
        is_verified=request.form.get('confirmation')=='true'
        payment.is_verified=is_verified
        db.session.commit()
        return redirect(url_for('student.show_payment',student_id=id))
    return render_template('profile/payment_profile.html',payment=payment)