from flask import Blueprint,render_template,flash,redirect,url_for,g,request,current_app
from flaskr.student_login import login_student_required
from flaskr.models import Session,Schedule,Payment,Exam,Student
import razorpay
from flaskr import csrf,db
from flaskr.student import due_fees
from werkzeug.security import check_password_hash,generate_password_hash
bp=Blueprint("studentIndex",__name__,url_prefix="/student-dashboard")


@bp.route("/",methods=['POST','GET'])
@login_student_required
def index():
    session=Session.query.filter_by(is_active=True).first()
    if request.method=='POST':
        old_password=request.form['old_password']
        new_password=request.form['new_password']
        confirm_password=request.form['confirm_password']
        if not check_password_hash(g.student.password,old_password):
            flash("Old password is not matching")
            return redirect(url_for('studentIndex.index'))
        if new_password!=confirm_password:
            flash('Password not match with confirm password')
            return redirect(url_for('studentIndex.index'))
        try:
            student=Student.query.get(g.student.id)
            student.password=generate_password_hash(confirm_password)
            db.session.commit()
            flash("Successfully changed password")
            return redirect(url_for('studentIndex.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"{e}")
            return redirect(url_for('studentIndex.index'))
    return render_template('student/body.html',session=session)

@bp.route("/profile")
@login_student_required
def student_profile():
    return render_template("student/profile.html")

@bp.route("/show-enroll-course")

def show_enroll_course():
    for enrollment in g.student.enrollment:
        for course in enrollment.course:
            print(course.course_name)
    return render_template('student/show_enroll.html')

@bp.route('/show-schedule')
def show_schedule():
    try:
        monday=Schedule.query.filter_by(is_active=True,sem_id=g.student.current_semester,dept_id=g.student.department_id).all()
    except Exception as e:
        flash(f"error: {e}")
        return redirect(url_for('studentIndex.index'))
    return render_template("student/schedule.html",schedule=monday)
@bp.route('/student-pay')
def student_pay():
    # custom_amount=request.args.get('custom_amount')
    # if int(custom_amount)<0:
    #     flash("Not negative")
    #     return redirect(url_for('studentIndex.student_pay'))
    fees=due_fees(g.student.id)
    payment=Payment.query.filter_by(student_id=g.student.id).all()
    return render_template('student/pay.html',fees=fees,payment=payment)
@bp.route('/pay-fees',methods=['POST','GET'])
def pay_fee():
    custom_amount=request.args.get('custom_amount',0)
    if not custom_amount.strip().isdigit() or int(custom_amount)<0:
        flash("Custom amount should not negative or blank")
        return redirect(url_for('studentIndex.student_pay'))
    fees=due_fees(g.student.id)
    if not fees or fees <= 0:
            return "No due fees to pay.", 400
    amount=int(custom_amount)
    data = { 
        "amount": amount * 100,  # Amount in paise
        "currency": "INR", 
    }
    client = razorpay.Client(auth=(current_app.config['KEY_ID'], current_app.config['KEY_SECRET']))
    payment = client.order.create(data=data)
    return render_template('student/pay_fee.html', payment=payment,custom_amount=custom_amount)

@bp.route('/payment-success', methods=['POST'])
@csrf.exempt
def payment_success():
    callback_data = request.form.to_dict()
    razorpay_payment_id = callback_data.get('razorpay_payment_id')
    razorpay_order_id = callback_data.get('razorpay_order_id')
    razorpay_signature = callback_data.get('razorpay_signature')
    client = razorpay.Client(auth=(current_app.config['KEY_ID'], current_app.config['KEY_SECRET']))
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        order = client.order.fetch(razorpay_order_id)
        if not order:
            return "Order not found",404
        
        amount=order['amount']//100
        payment = Payment.query.filter_by(order_id=razorpay_order_id).first()
        if not payment:
            payment = Payment(
                student_id=g.student.id,
                semester_id=g.student.current_semester,
                ammount_pay=amount,
                mode_of_payment="Online",
                order_id=razorpay_order_id
            )
            db.session.add(payment)
        payment.pay_id = razorpay_payment_id
        payment.signature = razorpay_signature
        payment.status = order['status']
        payment.is_verified == 'true'
        db.session.commit()
        flash("Payment successful and verified!")
        return render_template('student/success.html', callback_data=callback_data)

    except razorpay.errors.SignatureVerificationError as e:
        print("Signature verification failed:", str(e))
        flash("Payment verification failed!")
        return render_template('student/failure.html'), 400

@bp.route('/exam')
def exam():
    data=Exam.query.filter_by(dept_id=g.student.department_id,sem_id=g.student.current_semester)
    return render_template('student/exam.html') 
