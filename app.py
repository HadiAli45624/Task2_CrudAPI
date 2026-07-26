from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()

def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT,
            done BOOLEAN
        )
            """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    result = cursor.fetchone()
    count = result[0]

    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)" , ("Learn Backend", False))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)" , ("Complete Data Structures Course", False))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)" , ("Get Healthier", True))

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def home():
    return JSONResponse({"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}, status_code=200)


@app.get("/health")
def check():
    return JSONResponse({"status": "ok"}, status_code=200)


@app.get("/tasks")
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return JSONResponse(tasks, status_code=200)


@app.get("/tasks/{id}")
def get_tasknum(id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return JSONResponse({'error': f"Task {id} not found"}, status_code=404)

    task = dict(row)
    return JSONResponse(task, status_code=200)



@app.post("/tasks")
async def create_task(request: Request):
    data = await request.json()

    if not data or "title" not in data or not data['title']:
        return JSONResponse({"error": "Task Title does not exist"}, status_code=400)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (data["title"], False))
    conn.commit()

    new_id = cursor.lastrowid
    conn.close()

    task = {"id": new_id, "title": data["title"], "done": False}

    return JSONResponse(task, status_code=200)



@app.put("/tasks/{id}")
async def update_task(id: int, request: Request):
    data = await request.json()

    if not data or "title" not in data or not data["title"]:
        return JSONResponse({'error': 'Empty/Invalid Body'}, status_code=400)


    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (data["title"], id))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return JSONResponse({'error': 'Unknown ID'}, status_code=404)

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id, ))
    task = cursor.fetchone()

    task = dict(task)

    conn.close()

    return JSONResponse(task, status_code=200)


@app.delete('/tasks/{id}')
def delete_task(id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return JSONResponse({'error': 'Unknown ID'}, status_code=404)

    conn.close()
    return Response(status_code=204)


if __name__ == '__main__':
    init_db()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)