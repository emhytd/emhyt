# 学生成绩管理系统

## 项目简介
这是一个基于前后端分离架构的学生成绩管理系统，提供课程管理、教师管理、学生管理、成绩录入与查询等功能。

## 技术栈

### 后端
- **框架**: Flask 3.1.2
- **数据库**: MySQL (使用 SQLAlchemy ORM)
- **认证**: JWT (JSON Web Token)
- **跨域支持**: Flask-CORS

### 前端
- **框架**: Vue 3
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图表**: Chart.js
- **其他**: FontAwesome, XLSX等

## 系统功能

### 后端主要功能
- 用户认证（教师、学生、管理员）
- 课程管理
- 学生信息管理
- 教师信息管理
- 班级管理
- 选课管理
- 成绩录入与查询
- 截止日期设置
- 学期管理

### 前端主要功能
- 用户登录界面
- 各角色的管理控制台
- 数据可视化展示
- 表单数据录入
- 文件导入导出

## 项目结构

```
├── back_end/              # 后端应用
│   ├── app.py             # 主应用入口
│   ├── mysql_connect.py   # 数据库连接和模型定义
│   └── requirements.txt   # Python依赖
├── font_end/              # 前端应用
│   ├── src/               # 源代码
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── router/        # 路由配置
│   │   ├── plugins/       # 插件
│   │   └── main.js        # 前端入口
│   ├── package.json       # NPM依赖
│   └── vite.config.js     # Vite配置
└── README.md              # 项目说明文档
```

## 安装与运行

### 后端环境配置

1. 安装Python依赖：
```bash
cd back_end
pip install -r requirements.txt
```

2. 配置数据库连接：
编辑 `mysql_connect.py` 文件中的数据库连接配置。

3. 运行后端服务：
```bash
python app.py
```
后端服务默认运行在 `http://localhost:5000`。

### 前端环境配置

1. 安装Node.js依赖：
```bash
cd font_end
npm install
```

2. 开发环境运行：
```bash
npm run dev
```
前端开发服务器默认运行在 `http://localhost:5173`。

3. 生产环境构建：
```bash
npm run build
```
构建后的文件将输出到 `dist` 目录。

## 数据库配置
系统使用MySQL数据库，数据库连接配置位于 `back_end/mysql_connect.py` 文件中：

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://用户名:密码@服务器地址:端口/数据库名?charset=utf8mb4'
```

## 认证机制
系统使用JWT进行身份认证，支持三种角色：
- **管理员(admin)**: 拥有系统全部权限
- **教师(teacher)**: 可以管理课程、录入成绩等
- **学生(student)**: 可以查询成绩、选课等

## 部署说明

### 后端部署
1. 使用Gunicorn或uWSGI作为WSGI服务器
2. 配置Nginx作为反向代理
3. 设置环境变量存储敏感信息

### 前端部署
1. 构建前端项目：`npm run build`
2. 将构建产物部署到静态文件服务器（如Nginx、Apache）
3. 配置反向代理指向后端API

## 测试

### 后端测试
使用Postman或curl测试API接口。

### 前端测试
在开发模式下访问 `http://localhost:5173` 进行功能测试。

## 注意事项
1. 确保数据库连接配置正确
2. 生产环境中修改JWT密钥为安全的随机字符串
3. 配置适当的CORS策略
4. 定期备份数据库

## 许可证
保留所有权利。