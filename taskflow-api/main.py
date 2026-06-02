from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="TaskFlow API",
    description="A beginner-friendly FastAPI task management API.",
    version="0.1.0",
)


TaskStatus = Literal["todo", "doing", "done"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    status: TaskStatus | None = None


class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: TaskStatus = "todo"


tasks: list[Task] = []
next_task_id = 1


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(task_create: TaskCreate):
    global next_task_id

    task = Task(
        id=next_task_id,
        title=task_create.title,
        description=task_create.description,
    )
    tasks.append(task)
    next_task_id += 1

    return task


@app.get("/api/tasks", response_model=list[Task])
def list_tasks(status: TaskStatus | None = None, keyword: str | None = None):
    result = tasks

    if status is not None:
        result = [task for task in result if task.status == status]

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


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    return find_task(task_id)


@app.put("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    task = find_task(task_id)
    update_data = task_update.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        setattr(task, field_name, value)

    return task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)
    tasks.remove(task)
    return None


def find_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")
