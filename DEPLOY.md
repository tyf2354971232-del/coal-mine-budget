# 部署指南 - 煤矿技改预算管控系统

## 一、部署方式概览

| 方式 | 适用场景 | 成本 | 数据持久化 |
|------|---------|------|-----------|
| 本地开发 | 开发调试 | 免费 | SQLite 本地文件 |
| Docker Compose | 内网/服务器部署 | 服务器费用 | SQLite 持久卷 |
| Render.com | 公网演示 | 免费（有限制） | 重启后重置 |

---

## 二、本地开发环境

### 后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

- 运行在 http://localhost:8001
- API 文档: http://localhost:8001/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

- 运行在 http://localhost:3000
- Vite 开发服务器自动将 `/api` 代理到 `http://localhost:8001`

---

## 三、Docker Compose 部署（内网/服务器）

### 前提条件

- 安装 Docker 和 Docker Compose

### 启动

```bash
docker-compose up -d --build
```

- 前端: http://服务器IP:80
- 后端: http://服务器IP:8001
- Nginx 自动将 `/api` 反向代理到后端

### 停止

```bash
docker-compose down
```

### 数据持久化

数据库文件保存在 `./data/coal_mine_budget.db`，通过 Docker Volume 挂载确保持久化。

---

## 四、Render.com 免费公网部署（推荐演示用）

### 4.1 前提条件

1. 注册 [Render.com](https://render.com) 账号（可用 GitHub 登录）
2. 将项目推送到 GitHub 仓库（参见下方 Git 初始化步骤）

### 4.2 推送代码到 GitHub

```bash
# 在项目根目录执行
git init
git add .
git commit -m "初始提交：煤矿技改预算管控系统"

# 在 GitHub 上创建新仓库后
git remote add origin https://github.com/你的用户名/coal-mine-budget.git
git branch -M main
git push -u origin main
```

### 4.3 部署后端（Web Service）

1. 登录 Render.com，点击 **New > Web Service**
2. 连接 GitHub 仓库
3. 配置如下:

| 配置项 | 值 |
|--------|-----|
| Name | coal-mine-backend |
| Root Directory | backend |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

4. 添加环境变量:

| 变量名 | 值 | 说明 |
|--------|-----|------|
| DATABASE_URL | `sqlite+aiosqlite:///./coal_mine_budget.db` | 数据库路径 |
| SECRET_KEY | `自定义一个复杂的随机字符串` | JWT 签名密钥 |
| CORS_ORIGINS | `https://你的前端域名.onrender.com` | 允许的前端域名 |

5. 点击 **Create Web Service**，等待部署完成
6. 记录后端公网地址，如 `https://coal-mine-backend.onrender.com`

### 4.4 部署前端（Static Site）

1. 在 Render.com 点击 **New > Static Site**
2. 连接同一个 GitHub 仓库
3. 配置如下:

| 配置项 | 值 |
|--------|-----|
| Name | coal-mine-frontend |
| Root Directory | frontend |
| Build Command | `npm install && npm run build` |
| Publish Directory | dist |

4. 添加环境变量:

| 变量名 | 值 | 说明 |
|--------|-----|------|
| VITE_API_BASE_URL | `https://coal-mine-backend.onrender.com/api` | 后端 API 地址 |

5. 添加 **Rewrite Rule**（用于 SPA 路由支持）:
   - Source: `/*`
   - Destination: `/index.html`
   - Action: Rewrite

6. 点击 **Create Static Site**

### 4.5 部署后验证

1. 访问前端地址: `https://coal-mine-frontend.onrender.com`
2. 使用演示账号登录: admin / admin123
3. 检查各页面数据是否正常加载

### 4.6 注意事项

- **休眠机制**: Render 免费层的 Web Service 在 15 分钟无请求后会自动休眠，首次唤醒需约 30-50 秒
- **数据重置**: 免费层每次重新部署后 SQLite 数据会重置为初始种子数据，适合演示用途
- **如需持久化**: 可升级到 Render 付费计划，或使用 Render PostgreSQL 数据库（将 DATABASE_URL 改为 PostgreSQL 连接串）

---

## 五、环境变量参考

### 后端环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| PORT | 8001 | 服务器端口（Render 自动注入） |
| DATABASE_URL | sqlite+aiosqlite:///./coal_mine_budget.db | 数据库连接 |
| SECRET_KEY | (...默认值) | JWT 签名密钥，生产环境务必修改 |
| CORS_ORIGINS | * | 允许的 CORS 来源，多个用逗号分隔 |
| ALERT_YELLOW_THRESHOLD | 0.80 | 预算黄灯预警阈值 |
| ALERT_RED_THRESHOLD | 0.90 | 预算红灯预警阈值 |

### 前端环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| VITE_API_BASE_URL | /api | 后端 API 基础地址 |

---

## 六、演示账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 全部功能 |
| 领导 | leader | leader123 | 查看 + 模拟分析 + 审批 |
| 工程部 | engineer | eng123 | 数据录入 + 全局查看 |
| 普通员工 | viewer | view123 | 只读查看 |
