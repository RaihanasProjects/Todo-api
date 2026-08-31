from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel 
import sqlite3  

app = FastAPI()

class TaskCreate(BaseModel):
    title:str | None = None
    done:bool | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None 

connection = sqlite3.connect("tasks.db", check_same_thread=False)

cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY, 
    title TEXT, 
    done BOOLEAN
)
""")
connection.commit()

cursor.execute("SELECT COUNT(*) FROM tasks")
task_count = cursor.fetchone()[0]

if task_count == 0:
    cursor.execute(""" 
    INSERT INTO tasks( id, title, done)
    VALUES (1, 'Complete assignment',0)
    """)

    cursor.execute(""" 
        INSERT INTO tasks( id, title, done)
        VALUES (2, 'Go for a walk',0)
        """)

    cursor.execute(""" 
            INSERT INTO tasks( id, title, done)
            VALUES (3, 'drink water',1)
            """)

    connection.commit()



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
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    return [
        { "id": row[0], "title": row[1], "done": bool(row[2])}
        for row in rows
    ]


@app.get("/tasks/{task_id}",description="Get the specified task by its ID")
def get_task(task_id: int):
    cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    row=cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }

@app.post("/tasks", status_code=201, description="Create a new task")
def create_task(task: TaskCreate):

    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required and cannot be empty"
        )
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?,?)", (task.title, False))
    connection.commit()

    new_id = cursor.lastrowid

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    return new_task

@app.put("/tasks/{task_id}",description="Update an existing task by its ID")
def update_task(task_id: int, task: TaskUpdate):

    if task.title is None and task.done is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field is required"
            )

    if task.title is not None and task.done is not None:
        cursor.execute(
            "UPDATE tasks SET title =?, done = ? WHERE id = ?",
            (task.title, task.done, task_id)
        )

    elif task.title is not None:
        cursor.execute(
            "UPDATE tasks SET title =? WHERE id =? ",
            (task.title, task_id)
        )

    elif task.done is not None:
        cursor.execute(
            "UPDATE tasks SET done = ? WHERE id = ?",
            (task.done, task_id)
        )

    if cursor.rowcount ==0:
        raise HTTPException(
            status_code=404,
            detail=f"task {task_id} not found"
        )

    connection.commit()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"task {task_id} not found"
        )

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }

@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task ")
def delete_task(task_id: int):
    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    if cursor.rowcount==0:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    connection.commit()
    return

