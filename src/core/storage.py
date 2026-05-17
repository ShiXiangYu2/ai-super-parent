"""JSON 文件存储层 — 轻量级持久化"""
import json
import os
import threading
from typing import Any, Optional

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data"))

_lock = threading.Lock()


def _data_path(name: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{name}.json")


def _load(name: str) -> list[dict]:
    path = _data_path(name)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(name: str, data: list[dict]) -> None:
    path = _data_path(name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_all(collection: str) -> list[dict]:
    """列出集合中所有记录。"""
    return _load(collection)


def get_by_id(collection: str, record_id: str) -> Optional[dict]:
    """按 ID 获取单条记录。"""
    for item in _load(collection):
        if item.get("id") == record_id:
            return item
    return None


def query(collection: str, **kwargs) -> list[dict]:
    """按字段精确匹配查询。"""
    items = _load(collection)
    result = items
    for key, value in kwargs.items():
        result = [item for item in result if item.get(key) == value]
    return result


def insert(collection: str, record: dict) -> dict:
    """插入一条记录。"""
    with _lock:
        items = _load(collection)
        items.append(record)
        _save(collection, items)
    return record


def update(collection: str, record_id: str, updates: dict) -> Optional[dict]:
    """更新一条记录，返回更新后的记录。"""
    with _lock:
        items = _load(collection)
        for i, item in enumerate(items):
            if item.get("id") == record_id:
                items[i].update(updates)
                _save(collection, items)
                return items[i]
    return None


def delete(collection: str, record_id: str) -> bool:
    """删除一条记录。"""
    with _lock:
        items = _load(collection)
        new_items = [item for item in items if item.get("id") != record_id]
        if len(new_items) == len(items):
            return False
        _save(collection, new_items)
        return True


def count(collection: str) -> int:
    """统计记录数。"""
    return len(_load(collection))
