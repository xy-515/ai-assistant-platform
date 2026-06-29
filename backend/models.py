"""Database models."""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    histories = relationship("History", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")


class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(20), nullable=False)  # "paper" or "code"
    title = Column(String(200), nullable=False)
    function = Column(String(50), nullable=False)  # polish/outline/review for paper; review/generate/fix for code
    input_content = Column(Text, nullable=False)
    output_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="histories")


# ── Dataset Models ──────────────────────────────────────

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False)  # "paper" | "code"
    source = Column(String(100), nullable=False)  # "arxiv" | "cnki" | "github" | "self_built" | "stackoverflow" | "injected"
    description = Column(Text, default="")
    item_count = Column(Integer, default=0)
    file_path = Column(String(500), default="")
    schema_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("DataItem", back_populates="dataset", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="dataset", cascade="all, delete-orphan")


class DataItem(Base):
    __tablename__ = "data_items"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    input_text = Column(Text, nullable=False)
    reference = Column(Text, default="")
    metadata_json = Column(Text, default="{}")
    index = Column(Integer, default=0)  # 在数据集中的序号

    dataset = relationship("Dataset", back_populates="items")
    eval_results = relationship("EvalResult", back_populates="data_item", cascade="all, delete-orphan")


# ── Experiment Models ───────────────────────────────────

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    model_name = Column(String(50), nullable=False, default="deepseek-chat")
    prompt_template = Column(Text, default="")
    function_type = Column(String(20), nullable=False)  # "polish"|"outline"|"review"|"code_review"|"fix"|"generate_test"
    status = Column(String(20), default="pending")  # "pending"|"running"|"done"|"failed"
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship("Dataset", back_populates="experiments")
    results = relationship("EvalResult", back_populates="experiment", cascade="all, delete-orphan")


class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    data_item_id = Column(Integer, ForeignKey("data_items.id"), nullable=False)
    llm_output = Column(Text, default="")
    bleu_score = Column(Float, nullable=True)
    rouge_l_score = Column(Float, nullable=True)
    readability = Column(Float, nullable=True)
    semantic_sim = Column(Float, nullable=True)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("Experiment", back_populates="results")
    data_item = relationship("DataItem", back_populates="eval_results")


# ── Feedback Model ──────────────────────────────────────

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    eval_result_id = Column(Integer, ForeignKey("eval_results.id"), nullable=True)
    function_type = Column(String(20), nullable=False)
    usefulness = Column(Integer, default=3)  # 1-5 Likert
    accuracy = Column(Integer, default=3)
    ease_of_use = Column(Integer, default=3)
    speed = Column(Integer, default=3)
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")
