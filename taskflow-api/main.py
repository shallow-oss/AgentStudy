from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# app 是整个 FastAPI 后端应用的入口。
# 后面所有 @app.get、@app.post 这样的装饰器，都是在给这个应用注册接口。
app = FastAPI(
    title="TaskFlow API",
    description="A beginner-friendly FastAPI task management API.",
    version="0.1.0",
)


# Literal 用来限制字段只能取指定值。
# 这里表示任务状态只能是 todo、doing、done 三种之一。
TaskStatus = Literal["todo", "doing", "done"]


# Pydantic 模型：描述“创建任务”时客户端需要传入的数据格式。
# FastAPI 会自动根据这个模型校验请求 Body，并生成 Swagger 文档。
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


# Pydantic 模型：描述“更新任务”时允许传入的数据。
# 所有字段都是可选的，因为用户可能只想改 title、description 或 status 中的一项。
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    status: TaskStatus | None = None


# Pydantic 模型：描述后端返回给客户端的完整任务结构。
# response_model=Task 时，FastAPI 会按照这个结构整理接口返回结果。
class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: TaskStatus = "todo"


# 这是一个内存版“数据库”。
# 服务重启后这里的数据会清空；后面学习数据库时，会把它替换成 SQLAlchemy + 数据库表。
tasks: list[Task] = []
next_task_id = 1


# 健康检查接口，常用于确认服务是否正常启动。
@app.get("/health")
def health_check():
    return {"status": "ok"}


# POST 通常用于创建资源。
# status_code=201 表示创建成功；response_model=Task 表示返回一个完整任务对象。
@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(task_create: TaskCreate):
    # 因为要修改全局变量 next_task_id，所以这里需要声明 global。
    global next_task_id

    task = Task(
        id=next_task_id,
        title=task_create.title,
        description=task_create.description,
    )

    # 把新任务保存到内存列表中，并准备下一个任务 id。
    tasks.append(task)
    next_task_id += 1

    return task


# GET 通常用于查询资源。
# status 和 keyword 是查询参数，例如：/api/tasks?status=todo&keyword=FastAPI
@app.get("/api/tasks", response_model=list[Task])
def list_tasks(status: TaskStatus | None = None, keyword: str | None = None):
    result = tasks

    # 如果传了 status，就只返回对应状态的任务。
    if status is not None:
        result = [task for task in result if task.status == status]

    # 如果传了 keyword，就在标题和描述中做一个简单的关键词搜索。
    if keyword is not None:
        keyword_lower = keyword.lower()
        result = [
            task
            for task in result
            if keyword_lower in task.title.lower()
            or (
                task.description is not None
                and keyword_lower in task.description.lower()
            )
        ]

    return result


# {task_id} 是路径参数，例如：/api/tasks/1。
@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    return find_task(task_id)


# PUT 通常用于更新资源。
@app.put("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    task = find_task(task_id)

    # exclude_unset=True 表示只取用户真正传入的字段。
    # 例如用户只传 {"status": "done"}，就不会把 title、description 改成 None。
    update_data = task_update.model_dump(exclude_unset=True)

    # 根据用户传入的字段，动态更新任务对象。
    for field_name, value in update_data.items():
        setattr(task, field_name, value)

    return task


# DELETE 通常用于删除资源。
# 204 表示删除成功且响应体为空。
@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)
    tasks.remove(task)
    return None


# 公共辅助函数：根据 id 查找任务。
# 如果找不到，就抛出 404，FastAPI 会自动把它转换成 JSON 错误响应。
def find_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")
