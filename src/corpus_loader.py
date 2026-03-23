import csv
import json
from pathlib import Path
from typing import List


def load_corpus(path: str) -> List[str]:
    path_obj = Path(path)
    suffix = path_obj.suffix.lower()

    if suffix == ".json":
        return _load_json(path)
    elif suffix == ".jsonl":
        return _load_jsonl(path)
    elif suffix == ".csv":
        return _load_csv(path)
    elif suffix == ".txt":
        return _load_txt(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def _load_json(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return [str(item) for item in data]
    else:
        raise ValueError("JSON file must contain an array of strings")


def _load_jsonl(path: str) -> List[str]:
    messages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                obj = json.loads(line)
                if isinstance(obj, str):
                    messages.append(obj)
                elif isinstance(obj, dict):
                    for value in obj.values():
                        if isinstance(value, str):
                            messages.append(value)
                            break
    return messages


def _load_csv(path: str) -> List[str]:
    messages = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                messages.append(row[0])
    return messages


def _load_txt(path: str) -> List[str]:
    messages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                messages.append(line)
    return messages
