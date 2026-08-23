from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel 

app = FastAPI()

class TaskCreate(BaseModel):
    title:str | None = None

tasks = [
    {
        "id": 1,
        "title": "Complete assignment",
        "done": False
    },
    {
        "id": 2,
        "title": "Go for a walk",
        "done": False
    },
    {
        "id": 3,
        "title": "drink water",
        "done": True
    }
]



@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):

    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required and cannot be empty"
        )

    new_id = max(t["id"] for t in tasks) + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task
