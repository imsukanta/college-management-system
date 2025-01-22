from flask import Blueprint,render_template,g,request,redirect,url_for,flash
from flaskr.login import permission_required
from flaskr.models import Dept,Student,Session,Payment,Semester
from flaskr import db
from werkzeug.security import generate_password_hash
from datetime import datetime
import math
import pandas as pd
bp=Blueprint("student",__name__,url_prefix="/student")

# Calculate due fees of specific student
def due_fees(id):
    student = Student.query.get(id)
    total_semesters = int(student.admission_session_obj.total_semester) #8
    start_semester = int(student.start_semester) #1
    semester_fee = int(student.total_fees) // (total_semesters - start_semester + 1)
    payments = Payment.query.filter_by(student_id=id).all()
    if payments:
        fees_paid = sum(payment.ammount_pay for payment in payments)
    else:
        fees_paid = 0
    current_semester = int(student.current_semester)
    fees_due = semester_fee * (current_semester - (start_semester - 1)) - fees_paid
    return max(fees_due, 0)
# calculate fees_paid of specific student
def fees_paid(id):
    # student=Student.query.get(int(id))
    # total_semesters = int(student.admission_session_obj.total_semester)
    # start_semester = int(student.start_semester)
    # semester_fee = int(student.total_fees) // (total_semesters - start_semester + 1)
    payments = Payment.query.filter_by(student_id=id).all()
    fees_pay=sum(payment.ammount_pay for payment in payments)
    return max(fees_pay,0)

#view of student dashboard
@bp.route("/",methods=['POST','GET'])
@permission_required('student_dashboard')
def student_dashboard():
    filter=request.args.get('filter','')
    page=request.args.get('page',1,type=int)
    per_page=10
    if filter == 'az':
            students = Student.query.order_by(Student.name.asc()).paginate(page=page, per_page=per_page)
    elif filter == 'za':
            students = Student.query.order_by(Student.name.desc()).paginate(page=page, per_page=per_page)
    elif filter=='roll':
            students = Student.query.order_by(Student.university_roll_no.desc()).paginate(page=page, per_page=per_page)
    else:
        students=Student.query.paginate(page=page,per_page=per_page)
    return render_template("student.html",students=students,filter=filter)

#Add Student done Everything
@bp.route("/add-stuent",methods=['GET','POST'])
@permission_required('add_student')
def add_student():
    dept=db.session.execute(db.select(Dept)).scalars()
    sessionyear=Session.query.filter_by(is_active=True).first()
    sem=Semester.query.filter_by(is_active=True).all()
    if request.method=="POST":
        print(request.form)
        university_reg_no=request.form['university_reg_no']
        university_roll_no=request.form['university_roll_no']
        name=request.form['name']
        email=request.form['email']
        gender=request.form['gender']
        contact_no=request.form['contact_no']
        alternative_contact_number=request.form['alternative_contact_number']
        father_name=request.form['father_name']
        mother_name=request.form['mother_name']
        parent_contact_number=request.form['parent_contact_number']
        domicile_state=request.form['domicile_state']
        permanent_address=request.form['permanent_address']
        blood_group=request.form['blood_group']
        religion=request.form['religion']
        caste=request.form['caste']
        physically_challanged=request.form['physically_challanged']
        pan_card_no=request.form['pan_card_no']
        aadhar_card_no=request.form['aadhar_card_no']
        department=request.form['department']
        current_semester=request.form['current_semester']
        total_fees=request.form['total_fees']
        access_of_library=request.form.get('access_of_library')=='true'
        is_active=request.form.get('confirmation')=='true'
        if len(contact_no)!=10 or len(alternative_contact_number)!=10 or len(parent_contact_number)!=10:
            flash("Contact number should 10 digits only")
        if gender not in ['Male','Female']:
            flash("Gender should be either male or female")
            return redirect(url_for('student.add_student'))
        if physically_challanged not in ['Yes', 'No']:
            flash("Not yes or no")
            return redirect(url_for('student.add_student'))
        if int(current_semester)%2 ==0:
            flash("Start Semester should odd")
            return redirect(url_for('student.add_student'))
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        admission_date = datetime.strptime(request.form['admission_date'], '%Y-%m-%d').date()
        parsed_data=datetime.strptime(request.form['date_of_birth'],'%Y-%m-%d').date()
        password=parsed_data.strftime("%d%m%Y")
        admission_session=Session.query.filter_by(is_active=True).first()
        if not admission_session:
            flash('Not found any active session')
            return redirect(url_for('student.add_student'))
        try:
            student = Student(
                university_reg_no=university_reg_no,
                university_roll_no=university_roll_no,
                name=name,
                email=email,
                password=generate_password_hash(password),
                contact_number=contact_no,
                alternative_contact_number=alternative_contact_number,
                parent_contact_number=parent_contact_number,
                father_name=father_name,
                mother_name=mother_name,
                domicile_state=domicile_state,
                permanent_address=permanent_address,
                date_of_birth=date_of_birth,
                blood_group=blood_group,
                religion=religion,
                caste=caste,
                gender=gender,
                physically_challanged=physically_challanged,
                pan_card_no=pan_card_no,
                aadhar_card_no=aadhar_card_no,
                total_fees=total_fees,
                department_id=int(department),
                admission_date=admission_date,
                admission_session=int(admission_session.id),
                current_session=int(admission_session.id),
                current_semester=current_semester,
                start_semester=current_semester,
                access_of_library=access_of_library,
                is_active=is_active
            )
            db.session.add(student)
            db.session.commit()
            flash("Student successfully created")
            return redirect(url_for('student.student_dashboard'))
        except Exception as e:
            flash(f"Error Occured {e} ")
            return redirect(url_for('student.add_student'))
    return render_template('addfile/addStudent.html',dept=dept,session=sessionyear,sem=sem)

#show profile in admin section
@bp.route('/show-profile/<int:id>')
@permission_required('student_show_profile')
def show_profile(id):
    student=Student.query.get(id)
    fee_pay=fees_paid(id)
    return render_template('profile/student_profile.html',student=student,fee_pay=fee_pay)

#delete profile
@bp.route('/delete-profile/<int:id>')
@permission_required('delete_student_profile')
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
@permission_required('student_update_profile')
def update_profile(id):
    sem=Semester.query.filter_by(is_active=True).all()
    dept=Dept.query.all()
    student=Student.query.get(id)
    sessionyear=Session.query.filter_by(is_active=True).all()
    if request.method=="POST":
        university_reg_no=request.form['university_reg_no']
        university_roll_no=request.form['university_roll_no']
        name=request.form['name']
        email=request.form['email']
        gender=request.form['gender']
        contact_no=request.form['contact_no']
        alternative_contact_number=request.form['alternative_contact_number']
        father_name=request.form['father_name']
        mother_name=request.form['mother_name']
        parent_contact_number=request.form['parent_contact_number']
        domicile_state=request.form['domicile_state']
        permanent_address=request.form['permanent_address']
        blood_group=request.form['blood_group']
        religion=request.form['religion']
        caste=request.form['caste']
        physically_challanged=request.form['physically_challanged']
        pan_card_no=request.form['pan_card_no']
        aadhar_card_no=request.form['aadhar_card_no']
        department=request.form['department']
        current_semester=request.form['current_semester']
        total_fees=request.form['total_fees']
        access_of_library=request.form.get('access_of_library')=='true'
        is_active=request.form.get('confirmation')=='true'
        if len(contact_no)!=10 or len(alternative_contact_number)!=10 or len(parent_contact_number)!=10:
            flash("Contact number should 10 digits only")
            return redirect(url_for('student.update_profile',id=id))
        if gender not in ['Male','Female']:
            flash("Gender should be either male or female")
            return redirect(url_for('student.update_profile',id=id))
        if physically_challanged not in ['Yes', 'No']:
            flash("Not yes or no")
            return redirect(url_for('student.update_profile',id=id))
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        admission_date = datetime.strptime(request.form['admission_date'], '%Y-%m-%d').date()
        student.university_reg_no=university_reg_no
        student.university_roll_no=university_roll_no
        student.name=name
        student.email=email
        student.contact_number=contact_no
        student.alternative_contact_number=alternative_contact_number
        student.parent_contact_number=parent_contact_number
        student.father_name=father_name
        student.mother_name=mother_name
        student.domicile_state=domicile_state
        student.permanent_address=permanent_address
        # student.date_of_birth=date_of_birth
        student.date_of_birth = date_of_birth
        student.admission_date = admission_date
        student.blood_group=blood_group
        student.religion=religion
        student.caste=caste
        student.gender=gender
        student.physically_challanged=physically_challanged
        student.pan_card_no=pan_card_no
        student.aadhar_card_no=aadhar_card_no
        student.total_fees=total_fees
        student.department_id=int(department)
        # student.admission_date=admission_date
        student.current_semester=current_semester
        student.access_of_library=access_of_library
        student.is_active=is_active
        db.session.commit()
        return redirect(url_for('student.show_profile',id=id))
    return render_template('updatefile/updateStudent.html',student=student,dept=dept,session=sessionyear,sem=sem)

@bp.route('/payments/student-<int:student_id>')
@permission_required('student_show_payment')
def show_payment(student_id):
    student=Student.query.get(student_id)
    fees_due=due_fees(student_id)
    page=request.args.get('page',1,type=int)
    per_page=8
    payment = Payment.query.filter_by(student_id=student_id).paginate(page=page, per_page=per_page)
    return render_template("profile/show_student_pay.html",payment=payment,student=student,fees_due=fees_due)
@bp.route('/add-payment/<int:id>',methods=['GET','POST'])
@permission_required('student_add_payment')
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
            return redirect(url_for('student.show_payment',student_id=id))
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
@permission_required('student_payment_details_show')
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

#add student data from excel:
@bp.route('/add-student-excel',methods=['GET','POST'])
def add_student_excel():
    if request.method=='POST':
        file=request.files.get('file')
        if not file:
            flash("File not found")
            return redirect(url_for('student.add_student_excel'))
        excel_file=pd.read_excel(file)
        if excel_file.empty:
            flash("File is empty")
            return redirect(url_for('student.add_student_excel'))
        excel_file.dropna(inplace=True)
        print(excel_file.to_string())
    return render_template('addfile/addExcel.html')