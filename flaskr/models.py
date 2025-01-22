from flaskr import Base
from sqlalchemy import Column,Integer,String,ForeignKey,Boolean,Enum,Date,DateTime,Table,Time,JSON,FLOAT,Float
from sqlalchemy.orm import relationship
from datetime import datetime
from flaskr import db
from werkzeug.security import generate_password_hash
class Dept(db.Model):
    __tablename__="department"
    dept_id=db.Column(Integer,primary_key=True)
    dept_name=db.Column(String(100),nullable=False)
    staff = db.relationship('Staff', back_populates='department',cascade="all, delete-orphan")
    student=db.relationship('Student',back_populates="department",cascade="all, delete-orphan")
    course=db.relationship('Course',back_populates="department",cascade="all, delete-orphan")
    enrollment=db.relationship("Enrollment",back_populates="department",cascade='all, delete-orphan')
    schedule=relationship("Schedule",back_populates="department",cascade="all, delete-orphan")
    exam=relationship('Exam',back_populates="department",cascade='all, delete-orphan')

class Staff(db.Model):
    __tablename__='staffs'
    staff_id=db.Column(Integer,primary_key=True)
    emp_id=db.Column(String(100),unique=True)
    name=db.Column(String(150))
    email=db.Column(String(150),unique=True)
    mobile_no=db.Column(Integer)
    date_of_birth=db.Column(Date)
    address=db.Column(String(200))
    gender=db.Column(Enum("Male","Female"),nullable=False)
    designation=db.Column(Enum("HOD","STAFF"))
    department_id=db.Column(Integer,ForeignKey("department.dept_id",ondelete="CASCADE"))
    qualification=db.Column(String(100))
    year_of_experience=db.Column(Integer)
    password=db.Column(String(100))
    is_active=db.Column(Boolean,default=False)
    department = relationship('Dept', back_populates='staff')
    schedule=relationship('Schedule',back_populates='staff')

class User(db.Model):
    __tablename__="users"
    user_id=db.Column(Integer,primary_key=True)
    name=db.Column(String(100))
    email=db.Column(String(150),unique=True)
    password=db.Column(String(100))
    is_active=db.Column(Boolean,default=False)
    role_id=db.Column(Integer,ForeignKey('role.id',ondelete='SET NULL'))
    
    role=relationship("Role",backref='users')
    exam=relationship("Exam",back_populates="user",cascade='all, delete-orphan')

role_permission_table=db.Table(
    "role_permission",
    db.Column("role_id",Integer,ForeignKey('role.id',ondelete='CASCADE'),primary_key=True),
    db.Column("permission_id",Integer,ForeignKey('permission.id',ondelete='CASCADE'),primary_key=True)
)

class Role(db.Model):
    __tablename__='role'
    id=db.Column(Integer,primary_key=True)
    name=db.Column(String(100),unique=True)
    description=db.Column(String(100))
    permission=relationship("Permission",secondary=role_permission_table,backref='role')
    
class Permission(db.Model):
    __tablename__='permission'
    id=db.Column(Integer,primary_key=True)
    name=db.Column(String(100),unique=True)

    
class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(Integer, primary_key=True)
    university_reg_no = db.Column(String(100),unique=True,nullable=False)
    university_roll_no = db.Column(String(100),unique=True,nullable=False)
    name = db.Column(String(100), nullable=False)
    email = db.Column(String(100), unique=True)
    password = db.Column(String(100), nullable=False)
    contact_number = db.Column(Integer)
    alternative_contact_number = db.Column(Integer)
    parent_contact_number=db.Column(Integer)
    father_name=db.Column(String(100),nullable=False)
    mother_name=db.Column(String(100),nullable=False)
    domicile_state=db.Column(String(100),nullable=False)
    permanent_address = db.Column(String(255), nullable=False)
    date_of_birth = db.Column(Date, nullable=False)
    blood_group=db.Column(String(50))
    religion=db.Column(String(100))
    caste=db.Column(String(100))
    gender = db.Column(Enum("Male","Female"), nullable=False)
    physically_challanged=db.Column(Enum("Yes",'No'))
    pan_card_no=db.Column(String(100))
    aadhar_card_no=db.Column(String(100))
    total_fees=db.Column(Integer,nullable=False)
    department_id=db.Column(Integer,ForeignKey('department.dept_id'))
    admission_date = db.Column(Date)
    admission_session=db.Column(Integer,ForeignKey("sessions.id"))
    current_session=db.Column(Integer,ForeignKey('sessions.id'))
    current_semester=db.Column(Integer)
    start_semester=db.Column(Integer)
    access_of_library=db.Column(Boolean,default=False)
    is_active=db.Column(Boolean,default=False)
    department=relationship("Dept",back_populates='student')
    admission_session_obj=relationship("Session",foreign_keys=[admission_session],backref='admitted_student')
    current_session_obj=relationship("Session",foreign_keys=[current_session],backref="current_students")
    enrollment=relationship("Enrollment",back_populates="student",cascade='all, delete-orphan')
    payment=relationship("Payment",back_populates='student',cascade='all, delete-orphan')
    
class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_semester=db.Column(Integer,nullable=False)
    is_active=db.Column(Boolean,default=False)
    semesters = db.relationship('Semester', backref='session', lazy=True, cascade="all, delete")
class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    semester_level = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    created_at=db.Column(DateTime,default=datetime.now())
    enrollment=relationship("Enrollment",back_populates="semester",cascade="all, delete-orphan")
    schedule=relationship("Schedule",back_populates='semester',cascade='all, delete-orphan')
    payment=relationship("Payment",back_populates="semester",cascade='all, delete-orphan')
    exam=relationship("Exam",back_populates="semester",cascade="all, delete-orphan")
    # fees=relationship("Fees",back_populates="semester",cascade='all, delete')

association_table=db.Table('association_table',db.Model.metadata,db.Column("course_id",db.ForeignKey('course.id'),primary_key=True),db.Column("enroll_id",db.ForeignKey("enrollment.id"),primary_key=True))

class Course(db.Model):
    __tablename__='course'
    id=db.Column(Integer,primary_key=True)
    course_id=db.Column(String(100))
    course_name=db.Column(String(100))
    semester=db.Column(Integer)
    department_id=db.Column(Integer,ForeignKey('department.dept_id',ondelete="CASCADE"))
    is_active=db.Column(Boolean,default=False)
    department=relationship("Dept",back_populates="course")
    enroll=relationship("Enrollment",secondary=association_table,back_populates="course")
    schedule=relationship('Schedule',back_populates='course')

class Enrollment(db.Model):
    __tablename__='enrollment'
    id=db.Column(Integer,primary_key=True)
    student_id=db.Column(Integer,ForeignKey('student.id',ondelete="CASCADE"))
    semester_id=db.Column(Integer,ForeignKey('semester.id',ondelete="CASCADE"))
    department_id=db.Column(Integer,ForeignKey('department.dept_id',ondelete='CASCADE'))
    enrollment_date=db.Column(DateTime,default=datetime.now())
    status=db.Column(Enum('Active','Completed'))

    student=relationship('Student',back_populates="enrollment")
    semester=relationship("Semester",back_populates='enrollment')
    department=relationship("Dept",back_populates='enrollment')
    course=relationship("Course",secondary=association_table,back_populates="enroll")

class Schedule(db.Model):
    __tablename__='schedule'
    id=db.Column(Integer,primary_key=True)
    day=db.Column(Enum("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"),nullable=False)
    dept_id=db.Column(Integer,ForeignKey('department.dept_id'),nullable=False)
    sem_id=db.Column(Integer,ForeignKey("semester.semester_level",ondelete='CASCADE'),nullable=False)
    staff_id=db.Column(Integer,ForeignKey('staffs.staff_id'))
    start_time=db.Column(Time,nullable=False)
    course_id=db.Column(Integer,ForeignKey('course.id'))
    is_active=db.Column(Boolean,default=False)

    semester=relationship("Semester",back_populates="schedule")
    staff=relationship("Staff",back_populates="schedule")
    course=relationship('Course',back_populates='schedule')
    department=relationship("Dept",back_populates='schedule')


class Exam(db.Model):
    __tablename__='exam'
    exam_id=db.Column(Integer,primary_key=True)
    exam_name=db.Column(String(100))
    description=db.Column(String(200))
    dept_id=db.Column(Integer,ForeignKey('department.dept_id',ondelete='CASCADE'))
    sem_id=db.Column(Integer,ForeignKey('semester.semester_level',ondelete='CASCADE'))
    created_by=db.Column(Integer,ForeignKey('users.user_id',ondelete='CASCADE'))
    total_marks=db.Column(Integer)
    duration=db.Column(Integer)
    start_date=db.Column(Date)
    end_date=db.Column(Date)
    is_active=db.Column(Boolean,default=False)
    department=relationship('Dept',back_populates='exam')
    semester=relationship('Semester',back_populates='exam')
    user=relationship('User',back_populates='exam')
    question=relationship('Question',back_populates='exam',cascade='all,delete-orphan')

class Question(db.Model):
    __tablename__='question'
    question_id=db.Column(Integer,primary_key=True)
    exam_id=db.Column(Integer,ForeignKey('exam.exam_id',ondelete='CASCADE'))
    question_text=db.Column(String(200),nullable=False)
    options=db.Column(String(250))
    marks=db.Column(Integer)
    correct_answer=db.Column(Integer)
    exam=relationship('Exam',back_populates='question')

class Answer(db.Model):
    __tablename__='answer'
    answer_id=db.Column(Integer,primary_key=True)
    exam_id=db.Column(Integer,ForeignKey('exam.exam_id'))
    question_id=db.Column(Integer,ForeignKey('question.question_id'))
    student_id=db.Column(Integer,ForeignKey('student.id'))
    selected_answer=db.Column(JSON,nullable=False)
    submission_time=db.Column(DateTime,default=datetime.now())

class Payment(db.Model):
    __tablename__='payment'
    payment_id=db.Column(Integer,primary_key=True)
    student_id=db.Column(Integer,ForeignKey('student.id',ondelete='CASCADE'))
    semester_id=db.Column(Integer,ForeignKey('semester.id',ondelete='CASCADE'))
    ammount_pay=db.Column(Integer)
    mode_of_payment=db.Column(Enum("Online","Cash"))
    pay_id=db.Column(String(100))
    order_id=db.Column(String(200))
    signature=db.Column(String(200))
    is_verified=db.Column(Boolean,default=False)
    status=db.Column(String(50))
    created_at=db.Column(DateTime,default=datetime.now())
    semester=relationship('Semester',back_populates='payment')
    student=relationship('Student',back_populates='payment')

# class Attendance(db.Model):
#     attendance_id=db.Column(Integer,primary_key=True)
#     student_id=db.Column(Integer,ForeignKey('student.id'))
#     course_id=db.Column(Integer,ForeignKey('course.id'))