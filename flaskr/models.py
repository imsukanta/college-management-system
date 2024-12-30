from flaskr import Base
from sqlalchemy import Column,Integer,String,ForeignKey,Boolean,Enum,Date,DateTime,Table,Time,JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from flaskr import db

class Dept(db.Model):
    __tablename__="department"
    dept_id=db.Column(Integer,primary_key=True)
    dept_name=db.Column(String(100),nullable=False)
    staff = db.relationship('Staff', back_populates='department',cascade="all, delete-orphan")
    student=db.relationship('Student',back_populates="department",cascade="all, delete-orphan")
    course=db.relationship('Course',back_populates="department",cascade="all, delete-orphan")
    enrollment=db.relationship("Enrollment",back_populates="department",cascade='all, delete-orphan')
    schedule=relationship("Schedule",back_populates="department",cascade="all, delete-orphan")

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
    user_id=Column(Integer,primary_key=True)
    name=Column(String(100))
    email=Column(String(150),unique=True)
    password=Column(String(100))
    user_type=Column(Enum('admin','staff','finance',name="user_types"),nullable=False)
    is_active=Column(Boolean,default=False)


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(Integer, primary_key=True)
    makaut_roll_no = db.Column(String(100),unique=True)
    first_name = db.Column(String(100), nullable=False)
    last_name = db.Column(String(100), nullable=False)
    date_of_birth = db.Column(Date, nullable=False)
    gender = db.Column(String(10), nullable=False)
    permanent_address = db.Column(String(255), nullable=False)
    current_address = db.Column(String(255))
    contact_number = db.Column(Integer)
    email = db.Column(String(100), unique=True, nullable=False)
    nationality = db.Column(String(50), nullable=False)
    emergency_contact_name = db.Column(String(100), nullable=False)
    emergency_contact_number = db.Column(Integer)
    previous_qualifications = db.Column(String(255))
    department_id=db.Column(Integer,ForeignKey('department.dept_id'))
    admission_date = db.Column(Date, nullable=False)
    admission_session=db.Column(Integer,ForeignKey("sessionyear.id"))
    course_duration=db.Column(Integer)
    current_year=db.Column(Integer)
    current_semester=db.Column(Integer)
    mode_of_admission = db.Column(Enum("entrance_exam","direct_admission",name="mode_of_admission"),nullable=False)
    password = db.Column(String(100), nullable=False)
    access_of_library=db.Column(Boolean,default=False)
    is_active=db.Column(Boolean,default=False)
    department=relationship("Dept",back_populates='student')
    session=relationship("SessionYear",back_populates="student")
    enrollment=relationship("Enrollment",back_populates="student",cascade='all, delete-orphan')
    fees=relationship("Fees",back_populates='student',cascade='all, delete-orphan')
    payment=relationship("Payment",back_populates='student',cascade='all, delete-orphan')
    

class Fees(db.Model):
    __tablename__='fees'
    id=db.Column(Integer,primary_key=True)
    student_id=db.Column(Integer,ForeignKey('student.id',ondelete='CASCADE'))
    total_fees=db.Column(Integer)
    fees_paid=db.Column(Integer,default=0)
    fees_due=db.Column(Integer,default=0)
    student=relationship('Student',back_populates='fees')

class SessionYear(db.Model):
    __tablename__ = 'sessionyear'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100))
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date, nullable=False)
    is_active = db.Column(Boolean, default=True)
    semester = relationship(
        "Semester",
        back_populates="session",
        cascade="all, delete-orphan",  # Ensure cascade delete behavior
    )
    student=relationship('Student',back_populates="session")

class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(Integer, primary_key=True)
    session_id = db.Column(Integer, ForeignKey('sessionyear.id',ondelete="cascade"))
    name = db.Column(String(100))
    sem=db.Column(Integer)
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date, nullable=False)
    is_active = db.Column(Boolean, default=False)
    session = relationship('SessionYear', back_populates="semester")
    enrollment=relationship("Enrollment",back_populates="semester",cascade="all, delete-orphan")
    schedule=relationship("Schedule",back_populates='semester',cascade='all, delete-orphan')
    payment=relationship("Payment",back_populates="semester",cascade='all, delete-orphan')


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
    semester_id=db.Column(Integer,ForeignKey('semester.sem',ondelete="CASCADE"))
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
    sem_id=db.Column(Integer,ForeignKey("semester.sem",ondelete='CASCADE'),nullable=False)
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
    dept_id=db.Column(Integer,ForeignKey('department.dept_id'))
    sem_id=db.Column(Integer,ForeignKey('semester.id'))
    created_by=db.Column(Integer,ForeignKey('users.user_id'))
    total_marks=db.Column(Integer)
    duration=db.Column(Integer)
    start_date=db.Column(Date)
    end_date=db.Column(Date)
    is_active=db.Column(Boolean,default=False)

class Question(db.Model):
    __tablename__='question'
    question_id=db.Column(Integer,primary_key=True)
    exam_id=db.Column(Integer,ForeignKey('exam.exam_id'))
    question_text=db.Column(String(200),nullable=False)
    options=db.Column(String(250))
    marks=db.Column(Integer)
    correct_answer=db.Column(Integer)

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