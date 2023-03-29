from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

# Definindo a URL do Banco de Dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

# Cria uma instancia do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria uma sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Class Base criada para definir os modelos SQLALchemy
Base = declarative_base()

# Monta a tabela com suas colunas especificadas


class TodoModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    done = Column(Boolean, default=False)


# Cria a tabela no Banco de Dados
Base.metadata.create_all(bind=engine)


class Todo(BaseModel):
    """

    """
    title: str
    description: str
    done: bool = False


class TodoUpdate(BaseModel):
    """
    Model to update a ToDo status.
    """
    done: bool


@app.post("/todos/")
async def create_todo(todo: Todo):
    db_todo = TodoModel(
        title=todo.title, description=todo.description, done=todo.done)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.get("/todos/")
async def read_todos(skip: int = 0, limit: int = 100):
    """
    Read ToDos filtering by ID.
    e.g from index 0 to 2, return ids -> 1, 2, 3
    """
    todos = db.query(TodoModel).offset(skip).limit(limit).all()
    return todos


@app.get("/todos/{todo_id}")
async def read_todo_by_id(todo_id: int):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    return todo


@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo: TodoUpdate):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    db_todo.done = todo.done
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
