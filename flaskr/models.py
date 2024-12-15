from flaskr import Base
from sqlalchemy import Column,Integer,String,ForeignKey,Boolean,Enum,Date
from sqlalchemy.orm import relationship

class Dept(Base):
    __tablename__="department"
    dept_id=Column(Integer,primary_key=True)
    dept_name=Column(String(100),nullable=False)
    staff = relationship('Staff', back_populates='department',cascade="all, delete-orphan")

class Staff(Base):
    __tablename__='staffs'
    staff_id=Column(Integer,primary_key=True)
    emp_id=Column(String(100),unique=True)
    name=Column(String(150))
    email=Column(String(150),unique=True)
    mobile_no=Column(Integer)
    date_of_birth=Column(Date)
    address=Column(String(200))
    gender=Column(Enum("Male","Female"),nullable=False)
    designation=Column(Enum("HOD","STAFF"))
    department_id=Column(Integer,ForeignKey("department.dept_id",ondelete="CASCADE"))
    qualification=Column(String(100))
    year_of_experience=Column(Integer)
    password=Column(String(100))
    department = relationship('Dept', back_populates='staff')

class User(Base):
    __tablename__="users"
    user_id=Column(Integer,primary_key=True)
    # user_slug=Column(String(50),unique=True)
    name=Column(String(100))
    email=Column(String(150),unique=True)
    password=Column(String(100))
    user_type=Column(Enum('admin','staff','finance',name="user_types"),nullable=False)
    is_active=Column(Boolean,default=False)

