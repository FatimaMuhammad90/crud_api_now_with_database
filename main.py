
from fastapi import Depends, FastAPI, HTTPException 
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker, Session


class TaskCreate(BaseModel):
  title: str = Field(..., min_length=1)

class TaskUpdate(BaseModel):
  title: Optional[str] = Field(None, min_length=1)
  done: Optional[bool] = None

app = FastAPI()

engine = create_engine("sqlite:///tasks.db", connect_args={"check_same_thread":False})
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    # it was supposed to have two underroots on both sides

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    done = Column(Boolean, nullable=False)
# nullable means it cannot be empty

Base.metadata.create_all(engine)
#this creates the engine

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

get_db()


@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"] 
    }

@app.get("/health")
def health():
    return {"status": "OK"}

@app.get("/tasks")
def read(db: Session = Depends(get_db)):
    return db.query(Task).all()




@app.post("/tasks", status_code=201)
def create(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(title=task.title, done=False) # passing the parameters to the task class
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task



@app.get("/tasks/{id}")
def search_with_id(id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# @app.put("/tasks/{id}")

# def update(id: int, task: TaskUpdate):
#     if id not in tasks:
#          raise HTTPException(status_code=404, detail="Task not found")
#     if task.title is None and task.done is None:
#         raise HTTPException(status_code=400, detail="No fields to update")
#     if task.title is not None:
#         tasks[id]["title"] = task.title
#     if task.done is not None:
#         tasks[id]["done"] = task.done
#     return {"message": f"Updated task with ID {id}."}


# @app.delete("/tasks/{id}", status_code=204)
# def delete(id: int):
#     if id not in tasks:
#          raise HTTPException(status_code=404, detail="Task not found")
#     del tasks[id]
#     return {}

# @app.get("/stats")
# def stats():
#     total_count = len(tasks)
#     completed_count = sum(1 for task in tasks.values() if task.get("done"))
#     non_completed_count = total_count - completed_count
#     return {
#         "total_count": total_count,
#         "completed_count": completed_count,
#         "non_completed_count": non_completed_count,
#     }

# @app.get("/tasks/search")
# def search_with_words(search : str):
#     result = {}
#     for id, task in tasks.items():
#         if search.lower() in task["title"].lower():
#             result[id] = task
#     return result