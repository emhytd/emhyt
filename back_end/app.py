from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import jwt
import datetime
import re
from datetime import timezone
from datetime import datetime as dt 
app = Flask(__name__)
# "https://emhyt.top", 
# 配置 CORS
CORS(app, resources={r"/*": {
    "origins": ["https://emhyt.top","http://localhost:5173"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True,
    "expose_headers": ["Content-Type"]
}})

# 初始化数据库配置
from mysql_connect import init_db, db, Course,Admin, Teacher, Class, Student, CourseSelection, Teaching, Test,Deadline,Semester

# 初始化数据库连接
init_db(app)

# JWT 配置
SECRET_KEY = '123456'  # 密钥
JWT_ALGORITHM = 'HS256'  # 加密算法
JWT_EXP_DELTA_SECONDS = 3600  # Token 过期时间为 1 小时

def generate_jwt(user_id, role):
    expiration = datetime.datetime.now(timezone.utc) + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': expiration  # 设置过期时间
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)  # 生成Token
    return token

@app.route('/login', methods=['POST'])
def login():
    # 检查是否为预检请求
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    if not data or 'name' not in data or 'password' not in data or 'role' not in data:
        return jsonify({'error': '缺少用户名、密码或角色'}), 400

    # 根据角色判断查询用户
    role = data['role']
    username = data['name']
    password = data['password']
    
    user = None
    
    if role == 'teacher':
        # 教师使用数字ID登录
        try:
            user_id = int(username)
            user = Teacher.query.filter_by(teacher_id=user_id).first()
        except ValueError:
            return jsonify({'error': '教师ID必须是数字'}), 400
            
    elif role == 'student':
        # 学生使用数字ID登录
        try:
            user_id = int(username)
            user = Student.query.filter_by(student_id=user_id).first()
        except ValueError:
            return jsonify({'error': '学生ID必须是数字'}), 400
            
    elif role == 'admin':
        # 管理员使用用户名登录
        user = Admin.query.filter_by(username=username).first()
        
    else:
        return jsonify({'error': '无效的角色类型'}), 400

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    # 验证密码
    if user.password != password:
        return jsonify({'error': '用户名或密码错误'}), 401

    # 生成JWT Token
    if role == 'admin':
        user_id = user.id  # 管理员使用自增ID
    else:
        user_id = user.teacher_id if role == 'teacher' else user.student_id
        
    token = generate_jwt(user_id, role)
    return jsonify({'status': 'success', 'token': token}), 200

@app.route('/check_login/', methods=['GET'])
def check_login():
    if request.method == 'OPTIONS':
        return '', 200

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401

    # 提取Token的部分
    token = token.split(' ')[1] if ' ' in token else token

    try:
        # 解码JWT Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 根据角色返回不同的用户信息
        role = payload['role']
        user_id = payload['user_id']
        
        if role == 'teacher':
            user = Teacher.query.filter_by(teacher_id=user_id).first()
        elif role == 'student':
            user = Student.query.filter_by(student_id=user_id).first()
        elif role == 'admin':
            user = Admin.query.get(user_id)
        else:
            return jsonify({'status': 'failed', 'error': '无效的用户角色'}), 401
            
        if not user:
            return jsonify({'status': 'failed', 'error': '用户不存在'}), 404
            
        # 返回用户信息
        user_data = {
            'user_id': user_id,
            'role': role,
            'name': user.teacher_name if role == 'teacher' else 
                    user.student_name if role == 'student' else 
                    user.username
        }
        
        return jsonify({
            'status': 'success',
            'user': user_data
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    
@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'status': 'success', 'message': '已注销登录'}), 200


# @app.route('/admin')
# def admin_dashboard():
#     # 验证管理员权限
#     token = request.headers.get('Authorization')
#     if not token:
#         return jsonify({'error': '未提供token'}), 401
        
#     try:
#         token = token.split(' ')[1] if ' ' in token else token
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
#         if payload['role'] != 'admin':
#             return jsonify({'error': '权限不足'}), 403
            
#         # 管理员仪表板逻辑
#         return jsonify({'message': '欢迎访问管理员仪表板'})
        
#     except jwt.ExpiredSignatureError:
#         return jsonify({'error': 'Token已过期'}), 401
#     except jwt.InvalidTokenError:
#         return jsonify({'error': '无效的Token'}), 401

@app.route('/get_user_name', methods=['GET'])
def get_user_name():
    if request.method == 'OPTIONS':
        return '', 200

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401

    # 提取Token的部分
    try:
        token = token.split(' ')[1]  # 只取出 "Bearer <token>" 中的 token 部分
    except IndexError:
        return jsonify({'status': 'failed', 'error': '无效的Token格式'}), 401

    try:
        # 解码JWT Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        print('Decoded payload:', payload)  # 输出解码后的payload，用于调试
        
        # 从payload中获取用户ID和角色
        user_id = payload.get('user_id')
        role = payload.get('role')
        
        if not user_id or not role:
            return jsonify({'status': 'failed', 'error': 'Token缺少必要信息'}), 401
        
        # 根据角色查询用户名
        if role == 'teacher':
            teacher = Teacher.query.filter_by(teacher_id=user_id).first()
            if teacher:
                return jsonify({
                    'status': 'success',
                    'name': teacher.teacher_name
                }), 200
            else:
                return jsonify({'status': 'failed', 'error': '教师信息不存在'}), 404
                
        elif role == 'student':
            student = Student.query.filter_by(student_id=user_id).first()
            if student:
                return jsonify({
                    'status': 'success',
                    'name': student.student_name
                }), 200
            else:
                return jsonify({'status': 'failed', 'error': '学生信息不存在'}), 404
                
        else:
            return jsonify({'status': 'failed', 'error': '无效的用户角色'}), 400
            
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        print(f"获取用户名错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '服务器内部错误'}), 500


@app.route('/student_check', methods=['POST'])
def student_check():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 1. 检查截止日期
    deadline = Deadline.query.first()
    if not deadline:
        return jsonify({'status': 'failed', 'error': '未设置截止日期'}), 400
    
    current_date = datetime.datetime.now()
    if current_date > deadline.deadline_date:
        return jsonify({'status': 'failed', 'error': '已超过查询截止日期'}), 403
    
    # 2. 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 检查角色是否为学生
        if payload['role'] != 'student':
            return jsonify({'status': 'failed', 'error': '无权限访问'}), 403
            
        student_id = payload['user_id']
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': 'Token解析错误'}), 401
    
    # 3. 获取前端传递的JSON数据
    data = request.get_json()
    if not data or 'semester_id' not in data:
        return jsonify({'status': 'failed', 'error': '未提供学期ID'}), 400
    
    try:
        semester_id = int(data['semester_id'])
    except ValueError:
        return jsonify({'status': 'failed', 'error': '学期ID格式错误'}), 400
    
    # 4. 查询学生选课信息
    try:
        # 查询学生信息
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'status': 'failed', 'error': '学生不存在'}), 404
        
        # 查询学期信息
        semester = Semester.query.get(semester_id)
        if not semester:
            return jsonify({'status': 'failed', 'error': '学期不存在'}), 404
        
        # 查询该学生在指定学期的所有选课记录
        course_selections = CourseSelection.query.filter_by(
            student_id=student_id, 
            semester_id=semester_id
        ).all()
        
        # 如果没有选课记录
        if not course_selections:
            return jsonify({
                'status': 'success',
                'message': '该学期没有选课记录',
                'data': [],
                'student_info': {
                    'student_id': student.student_id,
                    'student_name': student.student_name,
                    'class_id': student.class_id
                },
                'semester_info': semester.to_dict()
            }), 200
        
        # 构建返回数据
        result_data = []
        for selection in course_selections:
            # 获取课程信息
            course = Course.query.get(selection.course_id)
            if not course:
                continue
                
            # 获取授课老师信息
            teaching = Teaching.query.filter_by(
                course_id=selection.course_id,
                semester_id=semester_id
            ).first()
            
            teacher = None
            if teaching:
                teacher = Teacher.query.get(teaching.teacher_id)
            
            # 添加到结果列表
            result_data.append({
                'course_id': course.course_id,
                'course_name': course.course_name,
                'course_type': course.course_type,
                'teacher_name': teacher.teacher_name if teacher else '未分配',
                'teacher_title': teacher.teacher_title if teacher else '',
                'semester_name': semester.semester_name,
                'grade': selection.grade,
                'student_name': student.student_name,
                'student_id': student.student_id
            })
        
        return jsonify({
            'status': 'success',
            'data': result_data,
            'student_info': {
                'student_id': student.student_id,
                'student_name': student.student_name,
                'class_id': student.class_id
            },
            'semester_info': semester.to_dict()
        }), 200
        
    except Exception as e:
        print(f"查询错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500



@app.route('/semesters', methods=['GET'])
def get_all_semesters():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色，检查角色是否为学生
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有学生可以访问
        if role != 'student' and role != 'teacher' and role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限学生'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': 'Token解析错误'}), 401
    
    try:
        # 查询所有学期信息
        semesters = Semester.query.all()
        
        # 构建简化的学期列表，只包含id和name
        semester_list = [{
            'semester_id': semester.semester_id,
            'semester_name': semester.semester_name
        } for semester in semesters]
        
        # 返回学期列表
        return jsonify({
            'status': 'success',
            'data': semester_list
        }), 200
        
    except Exception as e:
        print(f"查询错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500


@app.route('/student_info', methods=['GET'])
def get_student_info():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有学生可以访问自己的信息
        if role != 'student':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限学生'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': 'Token解析错误'}), 401
    
    try:
        # 根据token中的user_id查询学生信息
        student = Student.query.get(user_id)
        if not student:
            return jsonify({'status': 'failed', 'error': '学生信息不存在'}), 404
        
        # 获取班级信息
        class_info = Class.query.get(student.class_id)
        class_name = class_info.class_name if class_info else '未知班级'
        
        # 构建完整的学生信息
        student_data = student.to_dict()
        student_data['class_name'] = class_name
        
        # 返回学生信息
        return jsonify({
            'status': 'success',
            'data': student_data
        }), 200
        
    except Exception as e:
        print(f"查询错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500



@app.route('/check_deadline', methods=['GET'])
def check_deadline():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有教师可以访问
        if role != 'teacher' and  role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限教师'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': 'Token解析错误'}), 401
    
    try:
        # 查询截止日期表的第一条记录
        deadline = Deadline.query.order_by(Deadline.id.asc()).first()
        
        if not deadline:
            return jsonify({'status': 'failed', 'error': '未设置截止日期'}), 404
        
        # 返回截止日期信息
        return jsonify({
            'status': 'success',
            'data': deadline.to_dict()
        }), 200
        
    except Exception as e:
        print(f"查询错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500



@app.route('/set_deadline', methods=['POST'])
def set_deadline():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有教师可以设置截止日期
        if role != 'teacher'and  role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限教师'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': 'Token解析错误'}), 401
    
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'deadline' not in data:
            return jsonify({'status': 'failed', 'error': '缺少截止日期参数'}), 400
        
        deadline_str = data['deadline']
        
        # 验证日期格式 (YYYY-MM-DD)
        if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', deadline_str):
            return jsonify({'status': 'failed', 'error': '日期时间格式错误，请使用YYYY-MM-DD HH:mm:ss格式'}), 400
        
        # 查询是否存在ID为1的截止日期记录
        deadline = Deadline.query.get(1)
        
        if deadline:
            # 使用 dt 别名解析日期时间
            deadline.deadline_date = dt.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
        else:
            # 使用 dt 别名创建新记录
            deadline = Deadline(
                id=1, 
                deadline_date=dt.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
            )
            db.session.add(deadline)
        
        # 提交到数据库
        db.session.commit()
        
        # 返回成功响应
        return jsonify({
            'status': 'success',
            'message': '截止日期设置成功',
            'data': deadline.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"设置截止日期错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '设置截止日期失败'}), 500

@app.route('/teacher_check', methods=['POST'])
def teacher_check():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有教师可以访问
        if role != 'teacher':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限教师'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': 'Token解析错误'}), 401
    
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'message_check' not in data or 'semester_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少必要参数'}), 400
        
        message_check = data['message_check']
        semester_id = data['semester_id']
        teacher_id = user_id  # 从JWT中获取教师ID
        
        if message_check == "class":
            # 查询老师所在班级的所有学生的所有学科成绩
            # 1. 先找到老师管理的班级
            classes = Class.query.filter_by(teacher_id=teacher_id).all()
            if not classes:
                return jsonify({'status': 'failed', 'error': '未找到您管理的班级'}), 404
            
            # 2. 构建返回数据 - 按班级组织
            result = []
            for class_obj in classes:
                # 找到该班级的所有学生
                students = Student.query.filter_by(class_id=class_obj.class_id).all()
                if not students:
                    continue
                
                student_ids = [s.student_id for s in students]
                
                # 找到这些学生在指定学期的所有选课记录
                course_selections = CourseSelection.query.filter(
                    CourseSelection.student_id.in_(student_ids),
                    CourseSelection.semester_id == semester_id
                ).all()
                
                if not course_selections:
                    continue
                
                # 获取所有课程信息
                course_ids = list(set([cs.course_id for cs in course_selections]))
                courses = Course.query.filter(Course.course_id.in_(course_ids)).all()
                course_dict = {c.course_id: c for c in courses}
                
                # 构建班级数据 - 添加班主任信息
                class_data = {
                    'class_id': class_obj.class_id,
                    'class_name': class_obj.class_name,
                    'student_count': class_obj.student_count,
                    'class_teacher': {  # 添加班主任信息
                        'teacher_id': class_obj.teacher_id,
                        'teacher_name': class_obj.teacher.teacher_name if class_obj.teacher else '未知教师'
                    },
                    'students': []
                }
                
                # 为每个学生添加成绩信息
                for student in students:
                    student_data = {
                        'student_id': student.student_id,
                        'student_name': student.student_name,
                        'courses': []
                    }
                    
                    # 获取该学生在指定学期的所有课程成绩
                    for cs in course_selections:
                        if cs.student_id == student.student_id and cs.course_id in course_dict:
                            course = course_dict[cs.course_id]
                            
                            # 获取该课程的授课教师信息
                            teaching_info = Teaching.query.filter_by(
                                course_id=course.course_id,
                                semester_id=semester_id
                            ).first()
                            
                            course_teacher_info = {}
                            if teaching_info:
                                course_teacher = Teacher.query.filter_by(teacher_id=teaching_info.teacher_id).first()
                                if course_teacher:
                                    course_teacher_info = {
                                        'teacher_id': course_teacher.teacher_id,
                                        'teacher_name': course_teacher.teacher_name
                                    }
                            else:
                                # 如果没有找到授课信息，使用当前教师作为默认
                                course_teacher_info = {
                                    'teacher_id': teacher_id,
                                    'teacher_name': class_obj.teacher.teacher_name if class_obj.teacher else '未知教师'
                                }
                            
                            student_data['courses'].append({
                                'course_id': course.course_id,
                                'course_name': course.course_name,
                                'course_type': course.course_type,
                                'grade': cs.grade,
                                'course_teacher': course_teacher_info  # 添加授课教师信息
                            })
                    
                    class_data['students'].append(student_data)
                
                result.append(class_data)
            
            if not result:
                return jsonify({'status': 'failed', 'error': '本学期没有选课'}), 404
            
            return jsonify({
                'status': 'success',
                'data': result
            }), 200
            
        elif message_check == "teaching":
            # 查询老师所教课程的所有学生的所有学科成绩
            # 1. 找到老师所教的课程
            teachings = Teaching.query.filter_by(
                teacher_id=teacher_id,
                semester_id=semester_id
            ).all()
            
            if not teachings:
                return jsonify({'status': 'failed', 'error': '未找到您教授的课程'}), 404
            
            teacher_course_ids = [t.course_id for t in teachings]
            
            # 获取当前教师信息
            current_teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
            if not current_teacher:
                return jsonify({'status': 'failed', 'error': '教师信息不存在'}), 404
            
            # 2. 找到这些课程的所有选课记录
            course_selections = CourseSelection.query.filter(
                CourseSelection.course_id.in_(teacher_course_ids),
                CourseSelection.semester_id == semester_id
            ).all()
            
            if not course_selections:
                return jsonify({'status': 'failed', 'error': '本学期没有选课'}), 404
            
            # 3. 找到所有相关学生
            student_ids = list(set([cs.student_id for cs in course_selections]))
            students = Student.query.filter(Student.student_id.in_(student_ids)).all()
            student_dict = {s.student_id: s for s in students}
            
            # 4. 获取所有课程信息
            courses = Course.query.filter(Course.course_id.in_(teacher_course_ids)).all()
            course_dict = {c.course_id: c for c in courses}
            
            # 5. 获取所有相关班级信息
            class_ids = list(set([s.class_id for s in students]))
            classes = Class.query.filter(Class.class_id.in_(class_ids)).all()
            class_dict = {c.class_id: c for c in classes}
            
            # 6. 构建返回数据 - 按课程组织
            result = []
            for course_id in teacher_course_ids:
                if course_id not in course_dict:
                    continue
                    
                course = course_dict[course_id]
                course_data = {
                    'course_id': course.course_id,
                    'course_name': course.course_name,
                    'course_type': course.course_type,
                    'course_teacher': {  # 添加授课教师信息
                        'teacher_id': teacher_id,
                        'teacher_name': current_teacher.teacher_name
                    },
                    'students': []
                }
                
                # 找到该课程的所有选课记录
                course_cs = [cs for cs in course_selections if cs.course_id == course_id]
                
                for cs in course_cs:
                    if cs.student_id in student_dict:
                        student = student_dict[cs.student_id]
                        class_info = class_dict.get(student.class_id)
                        
                        # 获取学生所在班级的班主任信息
                        class_teacher_info = {}
                        if class_info and class_info.teacher:
                            class_teacher_info = {
                                'teacher_id': class_info.teacher_id,
                                'teacher_name': class_info.teacher.teacher_name
                            }
                        else:
                            class_teacher_info = {
                                'teacher_id': None,
                                'teacher_name': '未知班主任'
                            }
                        
                        course_data['students'].append({
                            'student_id': student.student_id,
                            'student_name': student.student_name,
                            'class_id': student.class_id,
                            'class_name': class_info.class_name if class_info else '未知班级',
                            'grade': cs.grade,
                            'class_teacher': class_teacher_info  # 添加班主任信息
                        })
                
                if course_data['students']:
                    result.append(course_data)
            
            if not result:
                return jsonify({'status': 'failed', 'error': '本学期没有选课'}), 404
            
            return jsonify({
                'status': 'success',
                'data': result
            }), 200
            
        else:
            return jsonify({'status': 'failed', 'error': '无效的message_check参数'}), 400
        
    except Exception as e:
        print(f"查询错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500


@app.route('/update_grades', methods=['POST'])
def update_grades():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有教师可以访问
        if role != 'teacher':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限教师'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': 'Token解析错误'}), 401
    
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'status': 'failed', 'error': '缺少请求数据'}), 400
        
        updates = data.get('updates', [])
        deletions = data.get('deletions', [])
        additions = data.get('additions', [])
        
        # 处理更新
        for update in updates:
            course_selection = CourseSelection.query.filter_by(
                student_id=update['student_id'],
                course_id=update['course_id'],
                semester_id=update['semester_id']
            ).first()
            
            if course_selection:
                course_selection.grade = update['grade']
            else:
                return jsonify({
                    'status': 'failed',
                    'error': f'未找到学生{update["student_id"]}在课程{update["course_id"]}的成绩记录'
                }), 404
        
        # 处理删除
        for deletion in deletions:
            course_selection = CourseSelection.query.filter_by(
                student_id=deletion['student_id'],
                course_id=deletion['course_id'],
                semester_id=deletion['semester_id']
            ).first()
            
            if course_selection:
                db.session.delete(course_selection)
            else:
                return jsonify({
                    'status': 'failed',
                    'error': f'未找到学生{deletion["student_id"]}在课程{deletion["course_id"]}的成绩记录'
                }), 404
        
        # 处理新增
        for addition in additions:
            # 检查是否已存在记录
            existing = CourseSelection.query.filter_by(
                student_id=addition['student_id'],
                course_id=addition['course_id'],
                semester_id=addition['semester_id']
            ).first()
            
            if existing:
                return jsonify({
                    'status': 'failed',
                    'error': f'学生{addition["student_id"]}在课程{addition["course_id"]}的成绩记录已存在'
                }), 400
            
            # 创建新记录
            new_selection = CourseSelection(
                student_id=addition['student_id'],
                course_id=addition['course_id'],
                semester_id=addition['semester_id'],
                grade=addition['grade']
            )
            db.session.add(new_selection)
        
        # 提交所有更改
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'成功更新{len(updates)}条记录，删除{len(deletions)}条记录，新增{len(additions)}条记录'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"成绩更新错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '成绩更新失败'}), 500



from sqlalchemy.exc import IntegrityError

@app.route('/bulkimport', methods=['POST'])
def bulk_import():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有教师可以访问
        if role != 'teacher' and role!='admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限教师'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': 'Token解析错误'}), 401
    
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'status': 'failed', 'error': '缺少请求数据'}), 400
        
        # 初始化结果统计
        results = {
            'total': len(data),
            'success': 0,
            'errors': []
        }
        
        # 处理每条记录
        for idx, record in enumerate(data):
            try:
                # 验证必要字段
                required_fields = ['student_id', 'course_id', 'score', 'semester_name']
                for field in required_fields:
                    if field not in record or not record[field]:
                        raise ValueError(f"缺少必要字段: {field}")
                
                # 查询学期
                semester = Semester.query.filter_by(semester_name=record['semester_name']).first()
                if not semester:
                    raise ValueError(f"学期 '{record['semester_name']}' 不存在")
                
                # 查询学生 - 使用推荐的 Session.get() 方法
                student = db.session.get(Student, record['student_id'])
                if not student:
                    raise ValueError(f"学生ID '{record['student_id']}' 不存在")
                
                # 查询课程 - 使用推荐的 Session.get() 方法
                course = db.session.get(Course, record['course_id'])
                if not course:
                    raise ValueError(f"课程ID '{record['course_id']}' 不存在")
                
                # 检查是否已有选课记录（同一个学生、课程、学期）
                existing_selection = CourseSelection.query.filter_by(
                    student_id=record['student_id'],
                    course_id=record['course_id'],
                    semester_id=semester.semester_id
                ).first()
                
                if existing_selection:
                    # 如果已有成绩记录
                    if existing_selection.grade is not None:
                        raise ValueError(f"学生 {record['student_id']} 在课程 {record['course_id']} 已有成绩记录")
                    else:
                        # 更新已有记录的成绩
                        existing_selection.grade = float(record['score'])
                        db.session.commit()
                        results['success'] += 1
                else:
                    # 创建新记录
                    new_selection = CourseSelection(
                        student_id=record['student_id'],
                        course_id=record['course_id'],
                        semester_id=semester.semester_id,
                        grade=float(record['score'])
                    )
                    db.session.add(new_selection)
                    db.session.commit()
                    results['success'] += 1
                    
            except IntegrityError as e:
                db.session.rollback()
                # 处理唯一约束冲突错误
                if "Duplicate entry" in str(e) and "uq_student_course_semester" in str(e):
                    error_msg = f"学生 {record.get('student_id', '')} 在课程 {record.get('course_id', '')} 的选课记录已存在（学期: {record.get('semester_name', '')}）"
                else:
                    error_msg = f"数据库完整性错误: {str(e)}"
                
                results['errors'].append({
                    'row': idx + 1,
                    'student_id': record.get('student_id', ''),
                    'course_id': record.get('course_id', ''),
                    'semester_name': record.get('semester_name', ''),
                    'error': error_msg
                })
                    
            except Exception as e:
                db.session.rollback()
                # 记录错误信息
                results['errors'].append({
                    'row': idx + 1,
                    'student_id': record.get('student_id', ''),
                    'course_id': record.get('course_id', ''),
                    'semester_name': record.get('semester_name', ''),
                    'error': str(e)
                })
        
        # 返回处理结果
        return jsonify({
            'status': 'success',
            'message': f'成功导入 {results["success"]}/{results["total"]} 条记录',
            'details': results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"批量导入错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '批量导入失败'}), 500




@app.route('/admin_check', methods=['POST'])
def admin_check():
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户角色
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': 'Token解析错误'}), 401
    
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'message_check' not in data or 'semester_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少必要参数'}), 400
        
        message_check = data['message_check']
        semester_id = data['semester_id']
        
        # 记录原始请求内容
        original_request = {
            'message_check': message_check,
            'semester_id': semester_id
        }
        
        if message_check == "class":
            # 查询指定学期的所有班级
            classes = Class.query.filter_by(semester_id=semester_id).all()  # 修改：根据semester_id过滤班级
            if not classes:
                return jsonify({'status': 'failed', 'error': f'在学期 {semester_id} 中未找到任何班级'}), 404
            
            # 2. 构建返回数据 - 按班级组织
            result = []
            for class_obj in classes:
                # 找到该班级的所有学生
                students = Student.query.filter_by(class_id=class_obj.class_id).all()
                if not students:
                    # 即使没有学生，也返回班级基本信息
                    class_teacher = Teacher.query.filter_by(teacher_id=class_obj.teacher_id).first()
                    class_data = {
                        'class_id': class_obj.class_id,
                        'class_name': class_obj.class_name,
                        'teacher_id': class_obj.teacher_id,
                        'teacher_name': class_teacher.teacher_name if class_teacher else '未知教师',
                        'student_count': 0,
                        'students': []
                    }
                    result.append(class_data)
                    continue
                
                student_ids = [s.student_id for s in students]
                
                # 找到这些学生在指定学期的所有选课记录
                course_selections = CourseSelection.query.filter(
                    CourseSelection.student_id.in_(student_ids),
                    CourseSelection.semester_id == semester_id
                ).all()
                
                # 获取所有课程ID
                course_ids = list(set([cs.course_id for cs in course_selections]))
                
                # 获取课程信息
                courses = Course.query.filter(Course.course_id.in_(course_ids)).all()
                course_dict = {c.course_id: c for c in courses}
                
                # 获取所有授课关系
                teachings = Teaching.query.filter(
                    Teaching.course_id.in_(course_ids),
                    Teaching.semester_id == semester_id
                ).all()
                
                # 构建课程ID到教师ID的映射
                course_teacher_map = {t.course_id: t.teacher_id for t in teachings}
                
                # 获取所有教师信息
                teacher_ids = list(set(course_teacher_map.values()))
                teachers = Teacher.query.filter(Teacher.teacher_id.in_(teacher_ids)).all()
                teacher_dict = {t.teacher_id: t for t in teachers}
                
                # 获取班级班主任信息
                class_teacher = Teacher.query.filter_by(teacher_id=class_obj.teacher_id).first()
                
                # 构建班级数据
                class_data = {
                    'class_id': class_obj.class_id,
                    'class_name': class_obj.class_name,
                    'teacher_id': class_obj.teacher_id,
                    'teacher_name': class_teacher.teacher_name if class_teacher else '未知教师',
                    'student_count': len(students),
                    'students': []
                }
                
                # 为每个学生添加成绩信息
                for student in students:
                    student_data = {
                        'student_id': student.student_id,
                        'student_name': student.student_name,
                        'courses': []
                    }
                    
                    # 获取该学生在指定学期的所有课程成绩
                    student_cs = [cs for cs in course_selections if cs.student_id == student.student_id]
                    
                    for cs in student_cs:
                        course = course_dict.get(cs.course_id)
                        if not course:
                            continue
                            
                        teacher_id = course_teacher_map.get(cs.course_id)
                        teacher = teacher_dict.get(teacher_id) if teacher_id else None
                        
                        student_data['courses'].append({
                            'course_id': course.course_id,
                            'course_name': course.course_name,
                            'course_type': course.course_type,
                            'teacher_id': teacher_id,
                            'teacher_name': teacher.teacher_name if teacher else '未知教师',
                            'grade': cs.grade
                        })
                    
                    class_data['students'].append(student_data)
                
                result.append(class_data)
            
            if not result:
                return jsonify({'status': 'failed', 'error': '本学期没有选课数据'}), 404
            
            # 返回结果，包含原始请求内容和处理后的数据
            return jsonify({
                'status': 'success',
                'original_request': original_request,
                'data': result
            }), 200
            
        elif message_check == "teaching":
            # 查询所有教师的教学数据
            # 1. 获取所有教师
            teachers = Teacher.query.all()
            if not teachers:
                return jsonify({'status': 'failed', 'error': '未找到任何教师'}), 404
            
            # 2. 构建返回数据 - 按教师组织
            result = []
            for teacher in teachers:
                # 获取该教师的所有教学任务
                teachings = Teaching.query.filter_by(
                    teacher_id=teacher.teacher_id,
                    semester_id=semester_id
                ).all()
                
                if not teachings:
                    continue
                
                teacher_course_ids = [t.course_id for t in teachings]
                
                # 获取这些课程的所有选课记录
                course_selections = CourseSelection.query.filter(
                    CourseSelection.course_id.in_(teacher_course_ids),
                    CourseSelection.semester_id == semester_id
                ).all()
                
                if not course_selections:
                    continue
                
                # 获取所有课程信息
                courses = Course.query.filter(Course.course_id.in_(teacher_course_ids)).all()
                course_dict = {c.course_id: c for c in courses}
                
                # 获取所有学生ID
                student_ids = list(set([cs.student_id for cs in course_selections]))
                students = Student.query.filter(Student.student_id.in_(student_ids)).all()
                student_dict = {s.student_id: s for s in students}
                
                # 获取所有班级信息
                class_ids = list(set([s.class_id for s in students]))
                classes = Class.query.filter(Class.class_id.in_(class_ids)).all()
                class_dict = {c.class_id: c for c in classes}
                
                # 获取所有班级的班主任信息
                class_teacher_ids = list(set([c.teacher_id for c in classes]))
                class_teachers = Teacher.query.filter(Teacher.teacher_id.in_(class_teacher_ids)).all()
                class_teacher_dict = {t.teacher_id: t for t in class_teachers}
                
                # 构建教师数据
                teacher_data = {
                    'teacher_id': teacher.teacher_id,
                    'teacher_name': teacher.teacher_name,
                    'courses': []
                }
                
                # 为每门课程添加学生成绩
                for course_id in teacher_course_ids:
                    if course_id not in course_dict:
                        continue
                        
                    course = course_dict[course_id]
                    course_data = {
                        'course_id': course.course_id,
                        'course_name': course.course_name,
                        'course_type': course.course_type,
                        'students': []
                    }
                    
                    # 找到该课程的所有选课记录
                    course_cs = [cs for cs in course_selections if cs.course_id == course_id]
                    
                    for cs in course_cs:
                        student = student_dict.get(cs.student_id)
                        if not student:
                            continue
                            
                        class_info = class_dict.get(student.class_id)
                        class_teacher_info = None
                        if class_info and class_info.teacher_id:
                            class_teacher = class_teacher_dict.get(class_info.teacher_id)
                            class_teacher_info = {
                                'teacher_id': class_info.teacher_id,
                                'teacher_name': class_teacher.teacher_name if class_teacher else '未知教师'
                            }
                        
                        course_data['students'].append({
                            'student_id': student.student_id,
                            'student_name': student.student_name,
                            'class_id': student.class_id,
                            'class_name': class_info.class_name if class_info else '未知班级',
                            'grade': cs.grade,
                            'class_teacher': class_teacher_info  # 添加班主任信息
                        })
                    
                    if course_data['students']:
                        teacher_data['courses'].append(course_data)
                
                if teacher_data['courses']:
                    result.append(teacher_data)
            
            if not result:
                return jsonify({'status': 'failed', 'error': '本学期没有教学数据'}), 404
            
            # 返回结果，包含原始请求内容和处理后的数据
            return jsonify({
                'status': 'success',
                'original_request': original_request,
                'data': result
            }), 200
            
        else:
            return jsonify({'status': 'failed', 'error': '无效的message_check参数'}), 400
        
    except Exception as e:
        print(f"管理员查询错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500


@app.route('/admin/student_info', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def admin_student_info():
    """学生信息管理（管理员权限）"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': f'Token解析错误: {str(e)}'}), 401
    
    try:
        # GET - 获取所有学生信息
        if request.method == 'GET':
            return get_all_students()
        
        # POST - 添加新学生
        elif request.method == 'POST':
            return add_new_student()
        
        # PUT - 更新学生信息
        elif request.method == 'PUT':
            return update_student_info()
        
        # DELETE - 删除学生
        elif request.method == 'DELETE':
            return delete_student()
            
    except Exception as e:
        app.logger.error(f"学生信息管理操作时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '操作失败'}), 500

def get_all_students():
    """获取所有班级的所有学生详细信息"""
    try:
        # 查询所有班级信息，并预加载教师关系
        all_classes = Class.query.options(db.joinedload(Class.teacher)).all()
        
        # 构建响应数据
        response_data = []
        
        for class_info in all_classes:
            # 查询该班级的所有学生
            students = Student.query.filter_by(class_id=class_info.class_id).all()
            
            # 构建班级的教师信息
            class_teacher_info = {}
            if class_info.teacher:
                class_teacher_info = {
                    'teacher_id': class_info.teacher.teacher_id,
                    'teacher_name': class_info.teacher.teacher_name,
                    'teacher_title': class_info.teacher.teacher_title
                }
            else:
                class_teacher_info = {
                    'teacher_id': None,
                    'teacher_name': '未分配班主任',
                    'teacher_title': '未知'
                }
            
            # 为每个班级构建数据结构
            class_data = {
                'class_id': class_info.class_id,
                'class_name': class_info.class_name,
                'student_count': class_info.student_count,
                'class_teacher': class_teacher_info,  # 添加班主任信息
                'students': []
            }
            
            # 为每个学生添加详细信息
            for student in students:
                student_dict = student.to_dict()
                
                # 获取学生的课程和成绩信息
                course_selections = CourseSelection.query.filter_by(student_id=student.student_id).all()
                
                # 获取所有相关课程信息
                course_ids = [cs.course_id for cs in course_selections]
                courses = Course.query.filter(Course.course_id.in_(course_ids)).all() if course_ids else []
                course_dict = {c.course_id: c for c in courses}
                
                # 获取所有授课信息
                teachings = Teaching.query.filter(Teaching.course_id.in_(course_ids)).all() if course_ids else []
                course_teacher_map = {t.course_id: t.teacher_id for t in teachings}
                
                # 获取所有教师信息
                teacher_ids = list(set(course_teacher_map.values()))
                teachers = Teacher.query.filter(Teacher.teacher_id.in_(teacher_ids)).all() if teacher_ids else []
                teacher_dict = {t.teacher_id: t for t in teachers}
                
                # 构建学生的课程成绩信息
                student_courses = []
                valid_grades = []  # 只包含有效成绩的列表
                
                for cs in course_selections:
                    course = course_dict.get(cs.course_id)
                    if not course:
                        continue
                    
                    teacher_id = course_teacher_map.get(cs.course_id)
                    teacher = teacher_dict.get(teacher_id) if teacher_id else None
                    
                    course_info = {
                        'course_id': course.course_id,
                        'course_name': course.course_name,
                        'course_type': course.course_type,
                        'teacher_id': teacher_id,
                        'teacher_name': teacher.teacher_name if teacher else '未知教师',
                        'grade': cs.grade,
                        'semester_id': cs.semester_id
                    }
                    student_courses.append(course_info)
                    
                    # 只添加有效成绩（非None）到计算列表
                    if cs.grade is not None:
                        valid_grades.append(cs.grade)
                
                # 计算学生平均分 - 只计算有效成绩
                if valid_grades:
                    average_grade = sum(valid_grades) / len(valid_grades)
                else:
                    average_grade = 0
                
                # 添加课程信息到学生数据
                student_dict['courses'] = student_courses
                student_dict['average_grade'] = round(average_grade, 2)
                student_dict['course_count'] = len(student_courses)
                student_dict['valid_grade_count'] = len(valid_grades)  # 有效成绩数量
                
                class_data['students'].append(student_dict)
            
            response_data.append(class_data)
        
        return jsonify({
            'status': 'success',
            'data': response_data
        }), 200
        
    except Exception as e:
        app.logger.error(f"查询学生信息时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500
def add_new_student():
    """添加新学生"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['class_id', 'student_name', 'student_gender']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'status': 'failed', 'error': f'缺少必要字段: {field}'}), 400
        
        # 生成新学号（当前最大学生ID + 1）
        max_student = Student.query.order_by(Student.student_id.desc()).first()
        new_student_id = max_student.student_id + 1 if max_student else 1001
        
        # 验证班级是否存在
        class_info = Class.query.get(data['class_id'])
        if not class_info:
            return jsonify({'status': 'failed', 'error': '班级不存在'}), 400
        
        # 获取班级班主任信息
        class_teacher = Teacher.query.get(class_info.teacher_id)
        class_teacher_info = {}
        if class_teacher:
            class_teacher_info = {
                'teacher_id': class_teacher.teacher_id,
                'teacher_name': class_teacher.teacher_name,
                'teacher_title': class_teacher.teacher_title
            }
        
        # 创建新学生记录
        new_student = Student(
            student_id=new_student_id,
            student_name=data['student_name'],
            student_gender=data['student_gender'],
            class_id=data['class_id'],
            password=str(new_student_id),  # 默认密码为学号
            
            # 可选字段
            birth_date=datetime.datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            ethnicity=data.get('ethnicity'),
            id_number=data.get('id_number'),
            native_place=data.get('native_place'),
            birthplace=data.get('birthplace'),
            home_address=data.get('home_address'),
            political_status=data.get('political_status'),
            blood_type=data.get('blood_type'),
            weight=data.get('weight'),
            height=data.get('height'),
            specialty=data.get('specialty'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            current_residence=data.get('current_residence')
        )
        
        db.session.add(new_student)
        
        # 更新班级学生人数
        class_info.student_count = Student.query.filter_by(class_id=data['class_id']).count() + 1
        
        db.session.commit()
        
        app.logger.info(f"成功添加学生: {new_student_id} - {data['student_name']}")
        
        # 返回添加的学生信息，包含班级和教师信息
        return jsonify({
            'status': 'success',
            'message': '学生添加成功',
            'student_id': new_student_id,
            'student_info': {
                'student_id': new_student_id,
                'student_name': data['student_name'],
                'student_gender': data['student_gender'],
                'class_id': data['class_id'],
                'class_name': class_info.class_name,
                'class_teacher': class_teacher_info
            }
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        app.logger.error(f"数据格式错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '数据格式错误'}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"添加学生时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '添加失败'}), 500

def update_student_info():
    """更新学生信息"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'student_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少学生ID'}), 400
        
        # 查找学生
        student = Student.query.get(data['student_id'])
        if not student:
            return jsonify({'status': 'failed', 'error': '学生不存在'}), 404
        
        # 记录原始班级ID
        original_class_id = student.class_id
        
        # 更新字段
        updatable_fields = [
            'student_name', 'student_gender', 'class_id', 'birth_date', 
            'ethnicity', 'id_number', 'native_place', 'birthplace', 
            'home_address', 'political_status', 'blood_type', 'weight', 
            'height', 'specialty', 'phone_number', 'email', 'current_residence'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'birth_date' and data[field]:
                    setattr(student, field, datetime.datetime.strptime(data[field], '%Y-%m-%d').date())
                else:
                    setattr(student, field, data[field])
        
        # 如果更改了班级，需要更新两个班级的学生人数和教师信息
        if 'class_id' in data and data['class_id'] != student.class_id:
            old_class_id = original_class_id
            new_class_id = data['class_id']
            
            # 验证新班级是否存在
            new_class = Class.query.get(new_class_id)
            if not new_class:
                return jsonify({'status': 'failed', 'error': '新班级不存在'}), 400
            
            # 获取新班级的班主任信息
            new_class_teacher = Teacher.query.get(new_class.teacher_id)
            new_class_teacher_info = {}
            if new_class_teacher:
                new_class_teacher_info = {
                    'teacher_id': new_class_teacher.teacher_id,
                    'teacher_name': new_class_teacher.teacher_name,
                    'teacher_title': new_class_teacher.teacher_title
                }
            
            # 更新旧班级学生人数
            old_class = Class.query.get(old_class_id)
            if old_class:
                old_class.student_count = Student.query.filter_by(class_id=old_class_id).count() - 1
            
            # 更新新班级学生人数
            new_class.student_count = Student.query.filter_by(class_id=new_class_id).count() + 1
        
        db.session.commit()
        
        app.logger.info(f"成功更新学生信息: {data['student_id']}")
        
        # 获取更新后的班级和教师信息
        current_class = Class.query.get(student.class_id)
        class_teacher = Teacher.query.get(current_class.teacher_id) if current_class else None
        class_teacher_info = {}
        if class_teacher:
            class_teacher_info = {
                'teacher_id': class_teacher.teacher_id,
                'teacher_name': class_teacher.teacher_name,
                'teacher_title': class_teacher.teacher_title
            }
        
        return jsonify({
            'status': 'success',
            'message': '学生信息更新成功',
            'student_info': {
                'student_id': student.student_id,
                'student_name': student.student_name,
                'student_gender': student.student_gender,
                'class_id': student.class_id,
                'class_name': current_class.class_name if current_class else '未知班级',
                'class_teacher': class_teacher_info
            }
        }), 200
        
    except ValueError as e:
        db.session.rollback()
        app.logger.error(f"数据格式错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '数据格式错误'}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新学生信息时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '更新失败'}), 500

def delete_student():
    """删除学生"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'student_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少学生ID'}), 400
        
        student_id = data['student_id']
        
        # 查找学生
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'status': 'failed', 'error': '学生不存在'}), 404
        
        class_id = student.class_id
        
        # 获取班级和教师信息（用于返回）
        class_info = Class.query.get(class_id)
        class_teacher = Teacher.query.get(class_info.teacher_id) if class_info else None
        class_teacher_info = {}
        if class_teacher:
            class_teacher_info = {
                'teacher_id': class_teacher.teacher_id,
                'teacher_name': class_teacher.teacher_name,
                'teacher_title': class_teacher.teacher_title
            }
        
        # 先删除相关的选课记录
        CourseSelection.query.filter_by(student_id=student_id).delete()
        
        # 删除学生
        db.session.delete(student)
        
        # 更新班级学生人数
        if class_info:
            class_info.student_count = Student.query.filter_by(class_id=class_id).count() - 1
        
        db.session.commit()
        
        app.logger.info(f"成功删除学生: {student_id}")
        
        return jsonify({
            'status': 'success',
            'message': '学生删除成功',
            'deleted_student': {
                'student_id': student_id,
                'student_name': student.student_name,
                'class_id': class_id,
                'class_name': class_info.class_name if class_info else '未知班级',
                'class_teacher': class_teacher_info
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除学生时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '删除失败'}), 500




@app.route('/admin/teacher_info', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def admin_teacher_info():
    """老师信息管理（管理员权限）"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': f'Token解析错误: {str(e)}'}), 401
    
    try:
        # GET - 获取所有老师信息
        if request.method == 'GET':
            return get_all_teachers()
        
        # POST - 添加新老师
        elif request.method == 'POST':
            return add_new_teacher()
        
        # PUT - 更新老师信息
        elif request.method == 'PUT':
            return update_teacher_info()
        
        # DELETE - 删除老师
        elif request.method == 'DELETE':
            return delete_teacher()
            
    except Exception as e:
        app.logger.error(f"老师信息管理操作时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '操作失败'}), 500

def get_all_teachers():
    """获取所有老师的详细信息"""
    try:
        # 查询所有老师信息，包括关联的班级信息[1,2](@ref)
        teachers = Teacher.query.all()
        
        # 构建响应数据
        teacher_list = []
        for teacher in teachers:
            teacher_data = teacher.to_dict()
            
            # 查询该老师负责的班级[1](@ref)
            classes = Class.query.filter_by(teacher_id=teacher.teacher_id).all()
            teacher_data['classes'] = [{
                'class_id': cls.class_id,
                'class_name': cls.class_name,
                'student_count': cls.student_count
            } for cls in classes]
            
            # 查询该老师的授课信息[1](@ref)
            teachings = Teaching.query.filter_by(teacher_id=teacher.teacher_id).all()
            teacher_data['teachings'] = [{
                'course_id': teaching.course_id,
                'semester_id': teaching.semester_id
            } for teaching in teachings]
            
            teacher_list.append(teacher_data)
        
        return jsonify({
            'status': 'success',
            'data': teacher_list,
            'total': len(teacher_list)
        }), 200
        
    except Exception as e:
        app.logger.error(f"查询老师信息时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500

def add_new_teacher():
    """添加新老师[4](@ref)"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['teacher_name', 'teacher_title']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'status': 'failed', 'error': f'缺少必要字段: {field}'}), 400
        
        # 生成新老师ID（当前最大老师ID + 1）
        max_teacher = Teacher.query.order_by(Teacher.teacher_id.desc()).first()
        new_teacher_id = max_teacher.teacher_id + 1 if max_teacher else 1001
        
        # 检查老师姓名是否已存在[8](@ref)
        existing_teacher = Teacher.query.filter_by(teacher_name=data['teacher_name']).first()
        if existing_teacher:
            return jsonify({'status': 'failed', 'error': '老师姓名已存在'}), 400
        
        # 创建新老师记录[6](@ref)
        new_teacher = Teacher(
            teacher_id=new_teacher_id,
            teacher_name=data['teacher_name'],
            teacher_title=data['teacher_title'],
            password=data.get('password', str(new_teacher_id)),  # 默认密码为老师ID
            
            # 详细信息字段[1](@ref)
            birth_date=datetime.datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            ethnicity=data.get('ethnicity'),
            id_number=data.get('id_number'),
            native_place=data.get('native_place'),
            birthplace=data.get('birthplace'),
            home_address=data.get('home_address'),
            political_status=data.get('political_status'),
            blood_type=data.get('blood_type'),
            weight=data.get('weight'),
            height=data.get('height'),
            specialty=data.get('specialty'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            current_residence=data.get('current_residence')
        )
        
        db.session.add(new_teacher)
        db.session.commit()
        
        app.logger.info(f"成功添加老师: {new_teacher_id} - {data['teacher_name']}")
        
        return jsonify({
            'status': 'success',
            'message': '老师添加成功',
            'teacher_id': new_teacher_id
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        app.logger.error(f"数据格式错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '数据格式错误，请检查日期格式(YYYY-MM-DD)'}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"添加老师时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '添加失败'}), 500

def update_teacher_info():
    """更新老师信息[6](@ref)"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'teacher_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少老师ID'}), 400
        
        # 查找老师
        teacher = Teacher.query.get(data['teacher_id'])
        if not teacher:
            return jsonify({'status': 'failed', 'error': '老师不存在'}), 404
        
        # 检查老师姓名是否与其他老师重复[8](@ref)
        if 'teacher_name' in data and data['teacher_name'] != teacher.teacher_name:
            existing_teacher = Teacher.query.filter_by(teacher_name=data['teacher_name']).first()
            if existing_teacher and existing_teacher.teacher_id != teacher.teacher_id:
                return jsonify({'status': 'failed', 'error': '老师姓名已存在'}), 400
        
        # 更新字段[6](@ref)
        updatable_fields = [
            'teacher_name', 'teacher_title', 'birth_date', 'ethnicity', 
            'id_number', 'native_place', 'birthplace', 'home_address', 
            'political_status', 'blood_type', 'weight', 'height', 
            'specialty', 'phone_number', 'email', 'current_residence'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'birth_date' and data[field]:
                    setattr(teacher, field, datetime.datetime.strptime(data[field], '%Y-%m-%d').date())
                else:
                    setattr(teacher, field, data[field])
        
        # 更新密码（如果有提供）
        if 'password' in data and data['password']:
            teacher.password = data['password']
        
        db.session.commit()
        
        app.logger.info(f"成功更新老师信息: {data['teacher_id']}")
        
        return jsonify({
            'status': 'success',
            'message': '老师信息更新成功'
        }), 200
        
    except ValueError as e:
        db.session.rollback()
        app.logger.error(f"数据格式错误: {str(e)}")
        return jsonify({'status': 'failed', 'error': '数据格式错误，请检查日期格式(YYYY-MM-DD)'}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新老师信息时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '更新失败'}), 500

def delete_teacher():
    """删除老师[3](@ref)"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'teacher_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少老师ID'}), 400
        
        teacher_id = data['teacher_id']
        
        # 查找老师
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'status': 'failed', 'error': '老师不存在'}), 404
        
        # 检查老师是否有关联的班级[1](@ref)
        classes = Class.query.filter_by(teacher_id=teacher_id).all()
        if classes:
            class_names = [cls.class_name for cls in classes]
            return jsonify({
                'status': 'failed', 
                'error': f'该老师负责班级{", ".join(class_names)}，无法删除'
            }), 400
        
        # 检查老师是否有关联的授课记录[1](@ref)
        teachings = Teaching.query.filter_by(teacher_id=teacher_id).all()
        if teachings:
            return jsonify({
                'status': 'failed', 
                'error': '该老师有授课记录，无法删除'
            }), 400
        
        # 删除老师
        db.session.delete(teacher)
        db.session.commit()
        
        app.logger.info(f"成功删除老师: {teacher_id}")
        
        return jsonify({
            'status': 'success',
            'message': '老师删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除老师时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '删除失败'}), 500


@app.route('/test', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def test():
    return jsonify("success")


@app.route('/admin/class_info', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def admin_class_info():
    """班级信息管理（管理员权限）"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]  # 取出 "Bearer <token>" 中的 token 部分
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': f'Token解析错误: {str(e)}'}), 401
    
    try:
        # GET - 获取所有班级信息
        if request.method == 'GET':
            return get_all_classes()
        
        # POST - 添加新班级
        elif request.method == 'POST':
            return add_new_class()
        
        # PUT - 更新班级信息
        elif request.method == 'PUT':
            return update_class_info()
        
        # DELETE - 删除班级
        elif request.method == 'DELETE':
            return delete_class()
            
    except Exception as e:
        app.logger.error(f"班级信息管理操作时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '操作失败'}), 500

def get_all_classes():
    """获取所有班级信息"""
    try:
        # 查询所有班级信息，并预加载教师关系
        all_classes = Class.query.options(db.joinedload(Class.teacher)).all()
        
        # 构建响应数据
        response_data = []
        
        for class_info in all_classes:
            class_dict = class_info.to_dict()
            
            # 添加教师信息
            if class_info.teacher:
                class_dict['teacher_name'] = class_info.teacher.teacher_name
                class_dict['teacher_title'] = class_info.teacher.teacher_title
            else:
                class_dict['teacher_name'] = None
                class_dict['teacher_title'] = None
            
            response_data.append(class_dict)
        
        return jsonify({
            'status': 'success',
            'data': response_data
        }), 200
        
    except Exception as e:
        app.logger.error(f"查询班级信息时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500

def add_new_class():
    """添加新班级"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['class_name', 'student_count', 'semester_id']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'status': 'failed', 'error': f'缺少必要字段: {field}'}), 400
        
        # 验证学期是否存在
        semester = Semester.query.get(data['semester_id'])
        if not semester:
            return jsonify({'status': 'failed', 'error': '学期不存在'}), 400
        
        # 验证班主任是否存在（如果提供了）
        if data.get('teacher_id'):
            teacher = Teacher.query.get(data['teacher_id'])
            if not teacher:
                return jsonify({'status': 'failed', 'error': '班主任不存在'}), 400
        
        # 生成新班级ID（当前最大班级ID + 1）
        max_class = Class.query.order_by(Class.class_id.desc()).first()
        new_class_id = max_class.class_id + 1 if max_class else 1001
        
        # 创建新班级记录
        new_class = Class(
            class_id=new_class_id,
            class_name=data['class_name'],
            student_count=data['student_count'],
            teacher_id=data.get('teacher_id'),
            semester_id=data['semester_id']
        )
        
        db.session.add(new_class)
        db.session.commit()
        
        app.logger.info(f"成功添加班级: {new_class_id} - {data['class_name']}")
        
        # 返回添加的班级信息
        return jsonify({
            'status': 'success',
            'message': '班级添加成功',
            'class_id': new_class_id,
            'class_info': new_class.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"添加班级时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '添加失败'}), 500

def update_class_info():
    """更新班级信息"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'class_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少班级ID'}), 400
        
        # 查找班级
        class_info = Class.query.get(data['class_id'])
        if not class_info:
            return jsonify({'status': 'failed', 'error': '班级不存在'}), 404
        
        # 更新字段
        updatable_fields = ['class_name', 'student_count', 'teacher_id', 'semester_id']
        
        for field in updatable_fields:
            if field in data:
                setattr(class_info, field, data[field])
        
        db.session.commit()
        
        app.logger.info(f"成功更新班级信息: {data['class_id']}")
        
        return jsonify({
            'status': 'success',
            'message': '班级信息更新成功',
            'class_info': class_info.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新班级信息时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '更新失败'}), 500

def delete_class():
    """删除班级"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'class_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少班级ID'}), 400
        
        class_id = data['class_id']
        
        # 查找班级
        class_info = Class.query.get(class_id)
        if not class_info:
            return jsonify({'status': 'failed', 'error': '班级不存在'}), 404
        
        # 检查班级是否有学生
        student_count = Student.query.filter_by(class_id=class_id).count()
        if student_count > 0:
            return jsonify({'status': 'failed', 'error': '该班级还有学生，无法删除'}), 400
        
        # 删除班级
        db.session.delete(class_info)
        db.session.commit()
        
        app.logger.info(f"成功删除班级: {class_id}")
        
        return jsonify({
            'status': 'success',
            'message': '班级删除成功',
            'deleted_class': class_info.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除班级时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '删除失败'}), 500

@app.route('/admin/semester_info', methods=['GET', 'OPTIONS'])
def admin_semester_info():
    """获取学期信息"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': f'Token解析错误: {str(e)}'}), 401
    
    try:
        # 获取所有学期
        semesters = Semester.query.all()
        semester_data = [semester.to_dict() for semester in semesters]
        
        return jsonify({
            'status': 'success',
            'data': semester_data
        }), 200
        
    except Exception as e:
        app.logger.error(f"查询学期信息时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500


# 添加课程成绩管理的路由
@app.route('/admin/course_selection_info', methods=['PUT', 'OPTIONS'])
def admin_course_selection_info():
    """课程成绩管理（管理员权限）"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token（与之前相同的验证逻辑）
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户ID和角色
        user_id = payload['user_id']
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': f'Token解析错误: {str(e)}'}), 401
    
    try:
        # PUT - 更新课程成绩
        if request.method == 'PUT':
            return update_course_grade()
            
    except Exception as e:
        app.logger.error(f"课程成绩管理操作时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '操作失败'}), 500

def update_course_grade():
    """更新课程成绩"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['student_id', 'course_id', 'semester_id', 'grade']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'failed', 'error': f'缺少必要字段: {field}'}), 400
        
        # 查找选课记录
        course_selection = CourseSelection.query.filter_by(
            student_id=data['student_id'],
            course_id=data['course_id'],
            semester_id=data['semester_id']
        ).first()
        
        if not course_selection:
            return jsonify({'status': 'failed', 'error': '选课记录不存在'}), 404
        
        # 更新成绩
        course_selection.grade = data['grade']
        db.session.commit()
        
        app.logger.info(f"成功更新成绩: 学生{data['student_id']} 课程{data['course_id']} 成绩{data['grade']}")
        
        return jsonify({
            'status': 'success',
            'message': '成绩更新成功',
            'updated_grade': {
                'student_id': data['student_id'],
                'course_id': data['course_id'],
                'semester_id': data['semester_id'],
                'grade': data['grade']
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新成绩时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '更新失败'}), 500

# 在现有后端代码中添加完整的选课管理接口

@app.route('/admin/course_selection_management', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def admin_course_selection_management():
    """选课信息管理（管理员权限）- 完整CRUD"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户角色
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': f'Token解析错误: {str(e)}'}), 401
    
    try:
        # GET - 获取所有选课信息
        if request.method == 'GET':
            return get_all_course_selections()
        
        # POST - 添加新选课记录
        elif request.method == 'POST':
            return add_course_selection()
        
        # PUT - 更新选课记录
        elif request.method == 'PUT':
            return update_course_selection()
        
        # DELETE - 删除选课记录
        elif request.method == 'DELETE':
            return delete_course_selection()
            
    except Exception as e:
        app.logger.error(f"选课管理操作时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '操作失败'}), 500

def get_all_course_selections():
    """获取所有选课记录，包含学生、课程、学期信息"""
    try:
        # 查询所有选课记录，并关联学生、课程、学期信息
        selections = db.session.query(
            CourseSelection, Student, Course, Semester, Class
        ).join(
            Student, CourseSelection.student_id == Student.student_id
        ).join(
            Course, CourseSelection.course_id == Course.course_id
        ).join(
            Semester, CourseSelection.semester_id == Semester.semester_id
        ).join(
            Class, Student.class_id == Class.class_id
        ).all()
        
        # 构建返回数据
        result = []
        for selection, student, course, semester, class_info in selections:
            # 获取授课教师信息
            teaching = Teaching.query.filter_by(
                course_id=course.course_id,
                semester_id=semester.semester_id
            ).first()
            
            teacher_name = '未分配'
            teacher_id = None
            if teaching:
                teacher = Teacher.query.get(teaching.teacher_id)
                teacher_name = teacher.teacher_name if teacher else '未分配'
                teacher_id = teaching.teacher_id
            
            result.append({
                'selection_id': selection.id,
                'student_id': student.student_id,
                'student_name': student.student_name,
                'class_id': student.class_id,
                'class_name': class_info.class_name,
                'course_id': course.course_id,
                'course_name': course.course_name,
                'course_type': course.course_type,
                'semester_id': semester.semester_id,
                'semester_name': semester.semester_name,
                'teacher_id': teacher_id,
                'teacher_name': teacher_name,
                'grade': selection.grade,
                'created_at': selection.created_at.isoformat() if hasattr(selection, 'created_at') and selection.created_at else None
            })
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        app.logger.error(f"查询选课信息时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500

def add_course_selection():
    """添加新选课记录"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['student_id', 'course_id', 'semester_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'status': 'failed', 'error': f'缺少必要字段: {field}'}), 400
        
        # 验证学生是否存在
        student = Student.query.get(data['student_id'])
        if not student:
            return jsonify({'status': 'failed', 'error': '学生不存在'}), 400
        
        # 验证课程是否存在
        course = Course.query.get(data['course_id'])
        if not course:
            return jsonify({'status': 'failed', 'error': '课程不存在'}), 400
        
        # 验证学期是否存在
        semester = Semester.query.get(data['semester_id'])
        if not semester:
            return jsonify({'status': 'failed', 'error': '学期不存在'}), 400
        
        # 检查是否已存在相同的选课记录
        existing_selection = CourseSelection.query.filter_by(
            student_id=data['student_id'],
            course_id=data['course_id'],
            semester_id=data['semester_id']
        ).first()
        
        if existing_selection:
            return jsonify({'status': 'failed', 'error': '该学生在此学期已选此课程'}), 400
        
        # 验证成绩范围
        if 'grade' in data and data['grade'] is not None:
            try:
                grade = float(data['grade'])
                if grade < 0 or grade > 100:
                    return jsonify({'status': 'failed', 'error': '成绩必须在0-100之间'}), 400
            except ValueError:
                return jsonify({'status': 'failed', 'error': '成绩格式错误'}), 400
        
        # 创建新选课记录
        new_selection = CourseSelection(
            student_id=data['student_id'],
            course_id=data['course_id'],
            semester_id=data['semester_id'],
            grade=data.get('grade')
        )
        
        db.session.add(new_selection)
        db.session.commit()
        
        # 获取新创建的选课记录的完整信息
        new_selection_full = db.session.query(
            CourseSelection, Student, Course, Semester, Class
        ).join(
            Student, CourseSelection.student_id == Student.student_id
        ).join(
            Course, CourseSelection.course_id == Course.course_id
        ).join(
            Semester, CourseSelection.semester_id == Semester.semester_id
        ).join(
            Class, Student.class_id == Class.class_id
        ).filter(CourseSelection.id == new_selection.id).first()
        
        selection, student, course, semester, class_info = new_selection_full
        
        # 获取授课教师信息
        teaching = Teaching.query.filter_by(
            course_id=course.course_id,
            semester_id=semester.semester_id
        ).first()
        
        teacher_name = '未分配'
        if teaching:
            teacher = Teacher.query.get(teaching.teacher_id)
            teacher_name = teacher.teacher_name if teacher else '未分配'
        
        selection_data = {
            'selection_id': selection.id,
            'student_id': student.student_id,
            'student_name': student.student_name,
            'class_id': student.class_id,
            'class_name': class_info.class_name,
            'course_id': course.course_id,
            'course_name': course.course_name,
            'course_type': course.course_type,
            'semester_id': semester.semester_id,
            'semester_name': semester.semester_name,
            'teacher_name': teacher_name,
            'grade': selection.grade
        }
        
        app.logger.info(f"成功添加选课记录: 学生{data['student_id']} 课程{data['course_id']} 学期{data['semester_id']}")
        
        return jsonify({
            'status': 'success',
            'message': '选课记录添加成功',
            'data': selection_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"添加选课记录时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '添加失败'}), 500

def update_course_selection():
    """更新选课记录"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'selection_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少选课记录ID'}), 400
        
        # 查找选课记录
        selection = CourseSelection.query.get(data['selection_id'])
        if not selection:
            return jsonify({'status': 'failed', 'error': '选课记录不存在'}), 404
        
        # 验证成绩范围
        if 'grade' in data:
            if data['grade'] is not None:
                try:
                    grade = float(data['grade'])
                    if grade < 0 or grade > 100:
                        return jsonify({'status': 'failed', 'error': '成绩必须在0-100之间'}), 400
                    selection.grade = grade
                except (ValueError, TypeError):
                    return jsonify({'status': 'failed', 'error': '成绩格式错误'}), 400
            else:
                selection.grade = None
        
        db.session.commit()
        
        app.logger.info(f"成功更新选课记录: {data['selection_id']}")
        
        return jsonify({
            'status': 'success',
            'message': '选课记录更新成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新选课记录时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '更新失败'}), 500

def delete_course_selection():
    """删除选课记录"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'selection_id' not in data:
            return jsonify({'status': 'failed', 'error': '缺少选课记录ID'}), 400
        
        selection_id = data['selection_id']
        
        # 查找选课记录
        selection = CourseSelection.query.get(selection_id)
        if not selection:
            return jsonify({'status': 'failed', 'error': '选课记录不存在'}), 404
        
        # 记录删除前的信息用于返回
        deleted_info = {
            'selection_id': selection.id,
            'student_id': selection.student_id,
            'course_id': selection.course_id,
            'semester_id': selection.semester_id
        }
        
        # 删除选课记录
        db.session.delete(selection)
        db.session.commit()
        
        app.logger.info(f"成功删除选课记录: {selection_id}")
        
        return jsonify({
            'status': 'success',
            'message': '选课记录删除成功',
            'deleted_selection': deleted_info
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除选课记录时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '删除失败'}), 500

@app.route('/admin/course_selection_base_data', methods=['GET'])
def get_course_selection_base_data():
    """获取选课管理所需的基础数据（学生、课程、学期列表）"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户角色
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': f'Token解析错误: {str(e)}'}), 401
    
    try:
        # 获取所有学生（包含班级信息）
        students = db.session.query(Student, Class).join(Class, Student.class_id == Class.class_id).all()
        student_list = [{
            'student_id': s.student_id,
            'student_name': s.student_name,
            'class_id': s.class_id,
            'class_name': c.class_name
        } for s, c in students]
        
        # 获取所有课程
        courses = Course.query.all()
        course_list = [{
            'course_id': c.course_id,
            'course_name': c.course_name,
            'course_type': c.course_type
        } for c in courses]
        
        # 获取所有学期
        semesters = Semester.query.all()
        semester_list = [{
            'semester_id': s.semester_id,
            'semester_name': s.semester_name
        } for s in semesters]
        
        # 获取所有班级
        classes = Class.query.all()
        class_list = [{
            'class_id': c.class_id,
            'class_name': c.class_name
        } for c in classes]
        
        # 获取所有教师（用于授课信息）
        teachers = Teacher.query.all()
        teacher_list = [{
            'teacher_id': t.teacher_id,
            'teacher_name': t.teacher_name
        } for t in teachers]
        
        return jsonify({
            'status': 'success',
            'data': {
                'students': student_list,
                'courses': course_list,
                'semesters': semester_list,
                'classes': class_list,
                'teachers': teacher_list
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"获取基础数据时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '获取基础数据失败'}), 500

# 批量导入选课记录
@app.route('/admin/course_selection_bulk_import', methods=['POST'])
def bulk_import_course_selections():
    """批量导入选课记录"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户角色
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': f'Token解析错误: {str(e)}'}), 401
    
    try:
        data = request.get_json()
        if not data or 'selections' not in data:
            return jsonify({'status': 'failed', 'error': '缺少选课数据'}), 400
        
        selections = data['selections']
        results = {
            'total': len(selections),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for idx, selection_data in enumerate(selections):
            try:
                # 验证必要字段
                required_fields = ['student_id', 'course_id', 'semester_id']
                for field in required_fields:
                    if field not in selection_data or not selection_data[field]:
                        raise ValueError(f"缺少必要字段: {field}")
                
                # 验证学生是否存在
                student = Student.query.get(selection_data['student_id'])
                if not student:
                    raise ValueError(f"学生ID {selection_data['student_id']} 不存在")
                
                # 验证课程是否存在
                course = Course.query.get(selection_data['course_id'])
                if not course:
                    raise ValueError(f"课程ID {selection_data['course_id']} 不存在")
                
                # 验证学期是否存在
                semester = Semester.query.get(selection_data['semester_id'])
                if not semester:
                    raise ValueError(f"学期ID {selection_data['semester_id']} 不存在")
                
                # 检查是否已存在相同的选课记录
                existing_selection = CourseSelection.query.filter_by(
                    student_id=selection_data['student_id'],
                    course_id=selection_data['course_id'],
                    semester_id=selection_data['semester_id']
                ).first()
                
                if existing_selection:
                    # 如果存在，更新成绩（如果提供了成绩）
                    if 'grade' in selection_data and selection_data['grade'] is not None:
                        try:
                            grade = float(selection_data['grade'])
                            if 0 <= grade <= 100:
                                existing_selection.grade = grade
                                db.session.commit()
                                results['success'] += 1
                            else:
                                raise ValueError("成绩必须在0-100之间")
                        except (ValueError, TypeError):
                            raise ValueError("成绩格式错误")
                    else:
                        results['failed'] += 1
                        results['errors'].append({
                            'index': idx,
                            'student_id': selection_data['student_id'],
                            'course_id': selection_data['course_id'],
                            'error': '选课记录已存在'
                        })
                    continue
                
                # 验证成绩范围
                if 'grade' in selection_data and selection_data['grade'] is not None:
                    try:
                        grade = float(selection_data['grade'])
                        if grade < 0 or grade > 100:
                            raise ValueError("成绩必须在0-100之间")
                    except (ValueError, TypeError):
                        raise ValueError("成绩格式错误")
                
                # 创建新选课记录
                new_selection = CourseSelection(
                    student_id=selection_data['student_id'],
                    course_id=selection_data['course_id'],
                    semester_id=selection_data['semester_id'],
                    grade=selection_data.get('grade')
                )
                
                db.session.add(new_selection)
                db.session.commit()
                results['success'] += 1
                
            except Exception as e:
                db.session.rollback()
                results['failed'] += 1
                results['errors'].append({
                    'index': idx,
                    'student_id': selection_data.get('student_id'),
                    'course_id': selection_data.get('course_id'),
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'message': f'批量导入完成，成功 {results["success"]} 条，失败 {results["failed"]} 条',
            'results': results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"批量导入选课记录时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '批量导入失败'}), 500


# 在现有后端代码中添加老师授课管理接口

@app.route('/admin/teaching_management', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def admin_teaching_management():
    """老师授课信息管理（管理员权限）- 完整CRUD"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 验证JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'failed', 'error': '未提供token'}), 401
    
    try:
        token = token.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 获取用户角色
        role = payload['role']
        
        # 只有管理员可以访问
        if role != 'admin':
            return jsonify({'status': 'failed', 'error': '无权限访问，仅限管理员'}), 403
        
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'failed', 'error': 'Token已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'failed', 'error': '无效的Token'}), 401
    except Exception as e:
        return jsonify({'status': 'failed', 'error': f'Token解析错误: {str(e)}'}), 401
    
    try:
        # GET - 获取所有授课信息
        if request.method == 'GET':
            return get_all_teachings()
        
        # POST - 添加新授课记录
        elif request.method == 'POST':
            return add_teaching()
        
        # PUT - 更新授课记录
        elif request.method == 'PUT':
            return update_teaching()
        
        # DELETE - 删除授课记录
        elif request.method == 'DELETE':
            return delete_teaching()
            
    except Exception as e:
        app.logger.error(f"授课管理操作时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '操作失败'}), 500

def get_all_teachings():
    """获取所有授课记录，包含老师、课程、学期信息"""
    try:
        # 查询所有授课记录，并关联老师、课程、学期信息
        teachings = db.session.query(
            Teaching, Teacher, Course, Semester
        ).join(
            Teacher, Teaching.teacher_id == Teacher.teacher_id
        ).join(
            Course, Teaching.course_id == Course.course_id
        ).join(
            Semester, Teaching.semester_id == Semester.semester_id
        ).all()
        
        # 构建返回数据
        result = []
        for teaching, teacher, course, semester in teachings:
            # 获取该授课记录的学生数量
            student_count = CourseSelection.query.filter_by(
                course_id=course.course_id,
                semester_id=semester.semester_id
            ).count()
            
            result.append({
                'teaching_id': f"{teaching.course_id}_{teaching.teacher_id}_{teaching.semester_id}",
                'teacher_id': teacher.teacher_id,
                'teacher_name': teacher.teacher_name,
                'teacher_title': teacher.teacher_title,
                'course_id': course.course_id,
                'course_name': course.course_name,
                'course_type': course.course_type,
                'semester_id': semester.semester_id,
                'semester_name': semester.semester_name,
                'student_count': student_count
            })
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        app.logger.error(f"查询授课信息时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '查询失败'}), 500

def add_teaching():
    """添加新授课记录"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['teacher_id', 'course_id', 'semester_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'status': 'failed', 'error': f'缺少必要字段: {field}'}), 400
        
        # 验证老师是否存在
        teacher = Teacher.query.get(data['teacher_id'])
        if not teacher:
            return jsonify({'status': 'failed', 'error': '老师不存在'}), 400
        
        # 验证课程是否存在
        course = Course.query.get(data['course_id'])
        if not course:
            return jsonify({'status': 'failed', 'error': '课程不存在'}), 400
        
        # 验证学期是否存在
        semester = Semester.query.get(data['semester_id'])
        if not semester:
            return jsonify({'status': 'failed', 'error': '学期不存在'}), 400
        
        # 检查是否已存在相同的授课记录
        existing_teaching = Teaching.query.filter_by(
            teacher_id=data['teacher_id'],
            course_id=data['course_id'],
            semester_id=data['semester_id']
        ).first()
        
        if existing_teaching:
            return jsonify({'status': 'failed', 'error': '该老师在此学期已教授此课程'}), 400
        
        # 创建新授课记录
        new_teaching = Teaching(
            teacher_id=data['teacher_id'],
            course_id=data['course_id'],
            semester_id=data['semester_id']
        )
        
        db.session.add(new_teaching)
        db.session.commit()
        
        # 获取新创建的授课记录的完整信息
        new_teaching_full = db.session.query(
            Teaching, Teacher, Course, Semester
        ).join(
            Teacher, Teaching.teacher_id == Teacher.teacher_id
        ).join(
            Course, Teaching.course_id == Course.course_id
        ).join(
            Semester, Teaching.semester_id == Semester.semester_id
        ).filter(
            Teaching.teacher_id == data['teacher_id'],
            Teaching.course_id == data['course_id'],
            Teaching.semester_id == data['semester_id']
        ).first()
        
        teaching, teacher, course, semester = new_teaching_full
        
        # 获取该授课记录的学生数量
        student_count = CourseSelection.query.filter_by(
            course_id=course.course_id,
            semester_id=semester.semester_id
        ).count()
        
        teaching_data = {
            'teaching_id': f"{teaching.course_id}_{teaching.teacher_id}_{teaching.semester_id}",
            'teacher_id': teacher.teacher_id,
            'teacher_name': teacher.teacher_name,
            'teacher_title': teacher.teacher_title,
            'course_id': course.course_id,
            'course_name': course.course_name,
            'course_type': course.course_type,
            'semester_id': semester.semester_id,
            'semester_name': semester.semester_name,
            'student_count': student_count
        }
        
        app.logger.info(f"成功添加授课记录: 老师{data['teacher_id']} 课程{data['course_id']} 学期{data['semester_id']}")
        
        return jsonify({
            'status': 'success',
            'message': '授课记录添加成功',
            'data': teaching_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"添加授课记录时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '添加失败'}), 500

def update_teaching():
    """更新授课记录"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['teacher_id', 'course_id', 'semester_id', 'new_teacher_id', 'new_course_id', 'new_semester_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'failed', 'error': f'缺少必要字段: {field}'}), 400
        
        # 查找授课记录
        teaching = Teaching.query.filter_by(
            teacher_id=data['teacher_id'],
            course_id=data['course_id'],
            semester_id=data['semester_id']
        ).first()
        
        if not teaching:
            return jsonify({'status': 'failed', 'error': '授课记录不存在'}), 404
        
        # 验证新老师是否存在
        new_teacher = Teacher.query.get(data['new_teacher_id'])
        if not new_teacher:
            return jsonify({'status': 'failed', 'error': '新老师不存在'}), 400
        
        # 验证新课程是否存在
        new_course = Course.query.get(data['new_course_id'])
        if not new_course:
            return jsonify({'status': 'failed', 'error': '新课程不存在'}), 400
        
        # 验证新学期是否存在
        new_semester = Semester.query.get(data['new_semester_id'])
        if not new_semester:
            return jsonify({'status': 'failed', 'error': '新学期不存在'}), 400
        
        # 检查是否已存在相同的授课记录
        existing_teaching = Teaching.query.filter_by(
            teacher_id=data['new_teacher_id'],
            course_id=data['new_course_id'],
            semester_id=data['new_semester_id']
        ).first()
        
        if existing_teaching:
            return jsonify({'status': 'failed', 'error': '该老师在此学期已教授此课程'}), 400
        
        # 更新授课记录
        teaching.teacher_id = data['new_teacher_id']
        teaching.course_id = data['new_course_id']
        teaching.semester_id = data['new_semester_id']
        
        db.session.commit()
        
        app.logger.info(f"成功更新授课记录: 老师{data['teacher_id']}->{data['new_teacher_id']} 课程{data['course_id']}->{data['new_course_id']} 学期{data['semester_id']}->{data['new_semester_id']}")
        
        return jsonify({
            'status': 'success',
            'message': '授课记录更新成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新授课记录时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '更新失败'}), 500

def delete_teaching():
    """删除授课记录"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['teacher_id', 'course_id', 'semester_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'failed', 'error': f'缺少必要字段: {field}'}), 400
        
        # 查找授课记录
        teaching = Teaching.query.filter_by(
            teacher_id=data['teacher_id'],
            course_id=data['course_id'],
            semester_id=data['semester_id']
        ).first()
        
        if not teaching:
            return jsonify({'status': 'failed', 'error': '授课记录不存在'}), 404
        
        # 记录删除前的信息用于返回
        deleted_info = {
            'teacher_id': teaching.teacher_id,
            'course_id': teaching.course_id,
            'semester_id': teaching.semester_id
        }
        
        # 删除授课记录
        db.session.delete(teaching)
        db.session.commit()
        
        app.logger.info(f"成功删除授课记录: 老师{data['teacher_id']} 课程{data['course_id']} 学期{data['semester_id']}")
        
        return jsonify({
            'status': 'success',
            'message': '授课记录删除成功',
            'deleted_teaching': deleted_info
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除授课记录时出错: {str(e)}")
        return jsonify({'status': 'failed', 'error': '删除失败'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
