# TaskFlow API

一个用于学习 Python 后端开发的最小 FastAPI 项目。

## 功能

- 健康检查
- 创建任务
- 查询任务列表
- 查询任务详情
- 更新任务
- 删除任务
- 按任务状态筛选
- 按关键词搜索

## 启动方式

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

启动后访问 Swagger 文档：

```text
http://127.0.0.1:8000/docs
```

## 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| POST | `/api/tasks` | 创建任务 |
| GET | `/api/tasks` | 查询任务列表 |
| GET | `/api/tasks/{task_id}` | 查询任务详情 |
| PUT | `/api/tasks/{task_id}` | 更新任务 |
| DELETE | `/api/tasks/{task_id}` | 删除任务 |

## 示例请求

创建任务：

```json
{
  "title": "学习 FastAPI",
  "description": "完成 TaskFlow API 的第一版"
}
```

更新任务：

```json
{
  "status": "doing"
}
```

任务状态只能是：

- `todo`
- `doing`
- `done`

## 当前限制

现在的数据保存在内存中，服务重启后任务会消失。下一步可以接入 SQLite 或 PostgreSQL，把任务持久化到数据库。
