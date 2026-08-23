from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel 

app = FastAPI()

class TaskCreate(BaseModel):
    title:str | None = None
    done:bool | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None 

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



@app.get("/",description="Get information about the task API")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health",description="check whether the API is running")
def health_check():
    return {
        "status": "ok"
    }
@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}",description="Get the specified task by its ID")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )

@app.post("/tasks", status_code=201, description="Create a new task")
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

@app.put("/tasks/{task_id}",description="Update an existing task by its ID")
def update_task(task_id: int, task: TaskUpdate):

    if task.title is None and task.done is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field is required"
            )
        
    for existing_task in tasks:
        if existing_task["id"] == task_id:
            if task.title is not None:
                existing_task["title"]=task.title

            if task.done is not None:
                existing_task["done"]=task.done 

            return existing_task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )

@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task ")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )

