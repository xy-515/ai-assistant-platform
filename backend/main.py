"""FastAPI main application with all API endpoints."""
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from openai import OpenAI

from database import engine, get_db, Base
from models import User, History, Dataset, DataItem
from auth import hash_password, verify_password, create_access_token, get_current_user

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Assistant Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── LLM Client ──────────────────────────────────────────

def get_llm_client():
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com"),
    )


def call_llm(system_prompt: str, user_content: str) -> str:
    client = get_llm_client()
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "deepseek-chat"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


# ── Schemas ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class PaperRequest(BaseModel):
    content: str
    function: str  # polish / outline / review


class CodeRequest(BaseModel):
    code: str
    error: str = ""
    function: str  # review / generate_test / fix


class DatasetCreateRequest(BaseModel):
    name: str
    type: str  # "paper" | "code"
    source: str
    description: str = ""
    items: list[dict] = []  # [{input_text, reference, metadata_json}]


class DatasetListResponse(BaseModel):
    id: int
    name: str
    type: str
    source: str
    item_count: int
    created_at: str


# ── AUTH Endpoints ──────────────────────────────────────

@app.post("/api/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(400, "Username already exists")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "Email already exists")

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.username)
    return {"token": token, "user": {"id": user.id, "username": user.username, "email": user.email}}


@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Invalid username or password")
    token = create_access_token(user.id, user.username)
    return {"token": token, "user": {"id": user.id, "username": user.username, "email": user.email}}


@app.get("/api/auth/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at.isoformat()}


# ── PAPER Assistant Endpoint ────────────────────────────

PAPER_PROMPTS = {
    "polish": "你是一个学术论文润色专家。请润色以下论文内容，保持原意的同时提升表达的学术性和流畅度。用 Markdown 格式输出润色结果，标注主要修改。",
    "outline": "你是一个学术论文写作导师。请根据以下描述生成一个详细的论文大纲，包含章节标题和每节要点。用 Markdown 格式输出。",
    "review": "你是一个学术论文审稿人。请评审以下论文内容，指出结构、逻辑、技术描述、语言表达方面的问题，给出具体修改建议。用 Markdown 格式输出。",
}


@app.post("/api/paper")
def paper_assistant(req: PaperRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.function not in PAPER_PROMPTS:
        raise HTTPException(400, f"Invalid function: {req.function}")

    system_prompt = PAPER_PROMPTS[req.function]
    result = call_llm(system_prompt, req.content)

    # Save history
    title = req.content[:80].replace("\n", " ")
    history = History(
        user_id=user.id,
        type="paper",
        title=title,
        function=req.function,
        input_content=req.content,
        output_content=result,
    )
    db.add(history)
    db.commit()

    return {"result": result, "id": history.id}


# ── CODE Assistant Endpoint ─────────────────────────────

CODE_PROMPTS = {
    "review": "你是一个资深代码审查专家。请审查以下代码，找出 bug、性能问题、安全隐患、代码风格问题，给出具体修复建议。用 Markdown 格式输出。",
    "generate_test": "你是一个测试工程师。请为以下代码生成全面的单元测试用例（Python + pytest）。覆盖正常情况、边界条件和异常情况。用 Markdown 格式输出完整可运行的测试代码。",
    "fix": "你是一个代码修复专家。以下代码存在 bug 或报错。请分析问题并给出修复后的完整代码。用 Markdown 格式输出，包含问题分析和修复代码。",
}


@app.post("/api/code")
def code_assistant(req: CodeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.function not in CODE_PROMPTS:
        raise HTTPException(400, f"Invalid function: {req.function}")

    system_prompt = CODE_PROMPTS[req.function]
    user_content = f"代码:\n```python\n{req.code}\n```"
    if req.error:
        user_content += f"\n\n报错信息:\n{req.error}"

    result = call_llm(system_prompt, user_content)

    title = req.code[:80].replace("\n", " ")
    history = History(
        user_id=user.id,
        type="code",
        title=title,
        function=req.function,
        input_content=f"{req.code}\n\n-- error: {req.error}" if req.error else req.code,
        output_content=result,
    )
    db.add(history)
    db.commit()

    return {"result": result, "id": history.id}


# ── HISTORY Endpoints ───────────────────────────────────

@app.get("/api/history/paper")
def paper_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(History).filter(History.user_id == user.id, History.type == "paper")
    total = query.count()
    items = query.order_by(History.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [{"id": h.id, "title": h.title, "function": h.function,
                    "input_content": h.input_content, "output_content": h.output_content,
                    "created_at": h.created_at.isoformat()} for h in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@app.get("/api/history/code")
def code_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(History).filter(History.user_id == user.id, History.type == "code")
    total = query.count()
    items = query.order_by(History.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [{"id": h.id, "title": h.title, "function": h.function,
                    "input_content": h.input_content, "output_content": h.output_content,
                    "created_at": h.created_at.isoformat()} for h in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@app.delete("/api/history/{history_id}")
def delete_history(history_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = db.query(History).filter(History.id == history_id, History.user_id == user.id).first()
    if not h:
        raise HTTPException(404, "History not found")
    db.delete(h)
    db.commit()
    return {"status": "ok"}


# ── DATASET Endpoints ────────────────────────────────────


@app.post("/api/datasets")
def create_dataset(req: DatasetCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.type not in ("paper", "code"):
        raise HTTPException(400, "type must be 'paper' or 'code'")

    dataset = Dataset(
        name=req.name,
        type=req.type,
        source=req.source,
        description=req.description,
        item_count=len(req.items),
    )
    db.add(dataset)
    db.flush()  # get dataset.id

    for i, item_data in enumerate(req.items):
        item = DataItem(
            dataset_id=dataset.id,
            input_text=item_data.get("input_text", ""),
            reference=item_data.get("reference", ""),
            metadata_json=json.dumps(item_data.get("metadata", {})),
            index=i + 1,
        )
        db.add(item)

    db.commit()
    db.refresh(dataset)
    return {
        "id": dataset.id,
        "name": dataset.name,
        "type": dataset.type,
        "source": dataset.source,
        "item_count": dataset.item_count,
        "created_at": dataset.created_at.isoformat(),
    }


@app.get("/api/datasets")
def list_datasets(
    type: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Dataset)
    if type:
        query = query.filter(Dataset.type == type)
    datasets = query.order_by(Dataset.created_at.desc()).all()
    return {
        "items": [
            {
                "id": d.id, "name": d.name, "type": d.type,
                "source": d.source, "item_count": d.item_count,
                "created_at": d.created_at.isoformat(),
            }
            for d in datasets
        ]
    }


@app.get("/api/datasets/{dataset_id}")
def get_dataset(dataset_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(404, "Dataset not found")
    return {
        "id": ds.id, "name": ds.name, "type": ds.type,
        "source": ds.source, "description": ds.description,
        "item_count": ds.item_count, "file_path": ds.file_path,
        "schema_json": ds.schema_json,
        "created_at": ds.created_at.isoformat(),
    }


@app.get("/api/datasets/{dataset_id}/items")
def list_dataset_items(
    dataset_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(404, "Dataset not found")

    query = db.query(DataItem).filter(DataItem.dataset_id == dataset_id)
    total = query.count()
    items = query.order_by(DataItem.index).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": it.id, "input_text": it.input_text,
                "reference": it.reference, "index": it.index,
                "metadata": json.loads(it.metadata_json) if it.metadata_json else {},
            }
            for it in items
        ],
        "total": total, "page": page, "page_size": page_size,
    }


@app.delete("/api/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(404, "Dataset not found")
    db.delete(ds)
    db.commit()
    return {"status": "ok"}


@app.get("/api/datasets/{dataset_id}/export")
def export_dataset(dataset_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(404, "Dataset not found")
    items = db.query(DataItem).filter(DataItem.dataset_id == dataset_id).order_by(DataItem.index).all()
    return {
        "name": ds.name, "type": ds.type, "source": ds.source,
        "items": [
            {
                "index": it.index, "input_text": it.input_text,
                "reference": it.reference,
                "metadata": json.loads(it.metadata_json) if it.metadata_json else {},
            }
            for it in items
        ],
    }


@app.get("/api/health")
def health():
    return {"status": "running"}
