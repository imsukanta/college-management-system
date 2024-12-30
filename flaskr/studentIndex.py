from flask import Blueprint,render_template,flash,redirect,url_for,g,request
from flaskr.student_login import login_student_required
from flaskr.models import Enrollment,Schedule,Fees,Payment
import razorpay
import math
from flaskr import csrf,db
bp=Blueprint("studentIndex",__name__,url_prefix="/student-dashboard")


@bp.route("/")
@login_student_required
def index():
    return render_template('student/body.html')

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

@bp.route('/pay-fees',methods=['POST','GET'])
def pay_fee():
    fees=Fees.query.filter_by(student_id=g.student.id).first()
    if not fees or fees.fees_due <= 0:
            return "No due fees to pay.", 400
    amount=int(fees.fees_due)
    data = { 
        "amount": amount * 100,  # Amount in paise
        "currency": "INR", 
        "receipt": "order_rcptid_11"
    }
    client = razorpay.Client(auth=("ID", "SECRET"))
    payment = client.order.create(data=data)
    return render_template('student/pay.html', payment=payment)

@bp.route('/payment-success', methods=['POST'])
@csrf.exempt
def payment_success():
    callback_data = request.form.to_dict()
    razorpay_payment_id = callback_data.get('razorpay_payment_id')
    razorpay_order_id = callback_data.get('razorpay_order_id')
    razorpay_signature = callback_data.get('razorpay_signature')
    client = razorpay.Client(auth=("ID", "SECRET"))
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
        fees = Fees.query.filter_by(student_id=g.student.id).first()
        if fees:
            fees.fees_due = max(0, fees.fees_due - payment.ammount_pay)
            fees.fees_paid += payment.ammount_pay
            db.session.commit()
        flash("Payment successful and verified!")
        return render_template('student/success.html', callback_data=callback_data)

    except razorpay.errors.SignatureVerificationError as e:
        print("Signature verification failed:", str(e))
        flash("Payment verification failed!")
        return render_template('student/failure.html'), 400
