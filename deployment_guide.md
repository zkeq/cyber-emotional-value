# 夸夸网站部署教程

本文档提供了夸夸网站项目的完整部署指南，包括前端和后端的安装、配置和启动步骤。

## 项目结构

项目分为两个主要部分：
- `frontend`：基于Vue.js的前端项目
- `backend`：基于FastAPI和Redis的后端项目

## 环境要求

### 前端环境
- Node.js 14.0+
- npm 6.0+ 或 yarn 1.22+

### 后端环境
- Python 3.8+
- Redis 6.0+

## 后端部署

### 1. 安装Redis

#### Ubuntu/Debian系统
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### CentOS/RHEL系统
```bash
sudo yum install epel-release
sudo yum install redis
sudo systemctl enable redis
sudo systemctl start redis
```

#### macOS系统
```bash
brew install redis
brew services start redis
```

### 2. 配置后端环境

1. 进入后端目录
```bash
cd backend
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 创建环境变量文件
```bash
# 创建.env文件
touch .env
```

5. 编辑.env文件，添加以下配置（根据实际情况修改）
```
# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# DeepSeek API配置（如果有）
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=your_api_key_here

# 应用配置
THREAD_COUNT=10
MESSAGES_PER_SECOND=10
```

### 3. 启动后端服务

```bash
cd backend
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 开发环境启动
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 生产环境启动
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 前端部署

### 1. 安装依赖

```bash
cd frontend
npm install
# 或
yarn install
```

### 2. 配置前端环境

1. 创建环境变量文件
```bash
# 开发环境
touch .env.development
# 生产环境
touch .env.production
```

2. 编辑环境变量文件，添加后端API地址
```
# .env.development
VUE_APP_API_URL=http://localhost:8000
VUE_APP_WS_URL=ws://localhost:8000

# .env.production
VUE_APP_API_URL=http://your-server-ip:8000
VUE_APP_WS_URL=ws://your-server-ip:8000
```

### 3. 开发环境启动

```bash
cd frontend
npm run serve
# 或
yarn serve
```

### 4. 生产环境构建和部署

```bash
cd frontend
npm run build
# 或
yarn build
```

构建完成后，`dist`目录中的文件即为可部署的静态文件。

#### Nginx部署示例

1. 安装Nginx
```bash
sudo apt update
sudo apt install nginx
```

2. 配置Nginx
```bash
sudo nano /etc/nginx/sites-available/kuakua
```

添加以下配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或IP

    location / {
        root /path/to/frontend/dist;  # 替换为前端构建文件的实际路径
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. 启用站点配置
```bash
sudo ln -s /etc/nginx/sites-available/kuakua /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

## 使用Docker部署（可选）

如果你熟悉Docker，也可以使用Docker进行部署。

### 1. 后端Dockerfile

在backend目录创建Dockerfile：
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 前端Dockerfile

在frontend目录创建Dockerfile：
```dockerfile
FROM node:14-alpine as build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

在frontend目录创建nginx.conf：
```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Docker Compose配置

在项目根目录创建docker-compose.yml：
```yaml
version: '3'

services:
  redis:
    image: redis:6-alpine
    restart: always
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    restart: always
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
      - REDIS_PASSWORD=
      - DEEPSEEK_BASE_URL=https://api.deepseek.com
      - DEEPSEEK_API_KEY=your_api_key_here
      - THREAD_COUNT=10
      - MESSAGES_PER_SECOND=10

  frontend:
    build: ./frontend
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  redis_data:
```

### 4. 启动Docker服务

```bash
docker-compose up -d
```

## 常见问题

1. **WebSocket连接失败**
   - 检查后端服务是否正常运行
   - 确认前端环境变量中的WebSocket URL是否正确
   - 检查防火墙是否允许WebSocket连接

2. **Redis连接失败**
   - 确认Redis服务是否正常运行
   - 检查Redis连接配置是否正确
   - 尝试使用redis-cli测试连接

3. **前端页面样式异常**
   - 清除浏览器缓存
   - 确认构建过程是否正常完成
   - 检查浏览器控制台是否有错误信息

4. **DeepSeek API调用失败**
   - 确认API密钥是否正确
   - 检查网络连接是否正常
   - 查看后端日志了解详细错误信息

## 性能优化建议

1. **后端优化**
   - 增加uvicorn工作进程数量
   - 调整线程池大小
   - 配置Redis连接池

2. **前端优化**
   - 启用Gzip压缩
   - 配置浏览器缓存
   - 使用CDN加速静态资源

## 安全建议

1. 在生产环境中，务必设置Redis密码
2. 限制API访问频率，防止滥用
3. 使用HTTPS加密传输数据
4. 定期更新依赖包，修复安全漏洞
