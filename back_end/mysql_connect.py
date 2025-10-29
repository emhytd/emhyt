# mysql_connect.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    """初始化数据库连接"""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://yjs:fbjYfDipa6bNDiCz@129.28.107.32:3306/yjs?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return db

# 学期表模型
class Semester(db.Model):
    __tablename__ = 'semester'
    semester_id = db.Column(db.Integer, primary_key=True)
    semester_name = db.Column(db.String(100), nullable=False, unique=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    
    # 关系
    teachings = db.relationship('Teaching', backref='semester_ref', lazy=True)
    course_selections = db.relationship('CourseSelection', backref='semester_ref', lazy=True)

    def to_dict(self):
        return {
            'semester_id': self.semester_id,
            'semester_name': self.semester_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current
        }

# 课程表模型（保持不变）
class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    course_type = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'course_type': self.course_type
        }

# 教师表模型（保持不变）
class Teacher(db.Model):
    __tablename__ = 'teacher'
    teacher_id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(255), nullable=False)
    teacher_title = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    # ！！！以下是需要新增的字段，与Student表保持一致！！！
    birth_date = db.Column(db.Date)  # 出生日期
    ethnicity = db.Column(db.String(50))  # 民族
    id_number = db.Column(db.String(50), unique=True)  # 证件号，唯一
    native_place = db.Column(db.String(255))  # 籍贯
    birthplace = db.Column(db.String(255))  # 出生地
    home_address = db.Column(db.Text)  # 家庭住址
    political_status = db.Column(db.String(50))  # 政治面貌
    blood_type = db.Column(db.String(10))  # 血型
    weight = db.Column(db.DECIMAL(5, 2))  # 体重，单位：kg
    height = db.Column(db.DECIMAL(5, 2))  # 身高，单位：cm
    specialty = db.Column(db.Text)  # 特长
    phone_number = db.Column(db.String(20))  # 手机号
    email = db.Column(db.String(100))  # 邮箱
    current_residence = db.Column(db.Text)  # 现居住地

    def to_dict(self):
        # 在返回值中添加新增的字段
        return {
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher_name,
            'teacher_title': self.teacher_title,
            # ... 其他原有字段 ...
            # 新增字段添加到返回字典中
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'ethnicity': self.ethnicity,
            'id_number': self.id_number,
            'native_place': self.native_place,
            'birthplace': self.birthplace,
            'home_address': self.home_address,
            'political_status': self.political_status,
            'blood_type': self.blood_type,
            'weight': float(self.weight) if self.weight else None,
            'height': float(self.height) if self.height else None,
            'specialty': self.specialty,
            'phone_number': self.phone_number,
            'email': self.email,
            'current_residence': self.current_residence
        }
class Class(db.Model):
    __tablename__ = 'class'
    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(255), nullable=False)
    student_count = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id')) 
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.semester_id'), nullable=False, default=1)  # 新增学期ID字段
    
    teacher = db.relationship('Teacher', backref='classes', lazy=True)
    
    def to_dict(self):
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'student_count': self.student_count,
            'teacher_id': self.teacher_id,
            'semester_id': self.semester_id  # 新增字段
        }

# 学生表模型（保持不变）
class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(255), nullable=False)
    student_gender = db.Column(db.String(10), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.class_id'), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    # 新增字段
    birth_date = db.Column(db.Date)  # 出生日期
    ethnicity = db.Column(db.String(50))  # 民族
    id_number = db.Column(db.String(50), unique=True)  # 证件号，唯一
    native_place = db.Column(db.String(255))  # 籍贯
    birthplace = db.Column(db.String(255))  # 出生地
    home_address = db.Column(db.Text)  # 家庭住址
    political_status = db.Column(db.String(50))  # 政治面貌
    blood_type = db.Column(db.String(10))  # 血型
    weight = db.Column(db.DECIMAL(5, 2))  # 体重，单位：kg
    height = db.Column(db.DECIMAL(5, 2))  # 身高，单位：cm
    specialty = db.Column(db.Text)  # 特长
    phone_number = db.Column(db.String(20))  # 手机号
    email = db.Column(db.String(100))  # 邮箱
    current_residence = db.Column(db.Text)  # 现居住地

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'student_name': self.student_name,
            'student_gender': self.student_gender,
            'class_id': self.class_id,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'ethnicity': self.ethnicity,
            'id_number': self.id_number,
            'native_place': self.native_place,
            'birthplace': self.birthplace,
            'home_address': self.home_address,
            'political_status': self.political_status,
            'blood_type': self.blood_type,
            'weight': float(self.weight) if self.weight else None,
            'height': float(self.height) if self.height else None,
            'specialty': self.specialty,
            'phone_number': self.phone_number,
            'email': self.email,
            'current_residence': self.current_residence
        }

# 选课表模型（更新）
class CourseSelection(db.Model):
    __tablename__ = 'course_selection'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 新增自增主键
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.semester_id'), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    
    # 添加唯一约束，确保同一个学生在同一个学期不能重复选同一门课
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', 'semester_id', name='uq_student_course_semester'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'semester_id': self.semester_id,
            'grade': self.grade
        }
# 授课表模型（更新）
class Teaching(db.Model):
    __tablename__ = 'teaching'
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'), primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.semester_id'), primary_key=True)

  

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'teacher_id': self.teacher_id,
            'semester_id': self.semester_id
        }

# 测试表模型（保持不变）
class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'password': self.password
        }
class Deadline(db.Model):
    __tablename__ = 'deadline'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deadline_date = db.Column(db.DateTime, nullable=False)  # 修改为DateTime类型

    def to_dict(self):
        return {
            'id': self.id,
            'deadline_date': self.deadline_date.isoformat() if self.deadline_date else None
        }
# 在 mysql_connect.py 中添加 Admin 模型
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    last_login = db.Column(db.TIMESTAMP)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }