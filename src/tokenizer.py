import re
from typing import Callable, List

import jieba


def tokenize_word(text: str) -> List[str]:
    pattern = re.compile(
        r"[a-zA-Z]+|[\u4e00-\u9fff]+|[0-9.]+|[^\sa-zA-Z\u4e00-\u9fff0-9.]+"
    )
    tokens = []

    for match in pattern.finditer(text):
        part = match.group()
        if re.match(r"[a-zA-Z]+", part):
            tokens.append(part)
        elif re.match(r"[\u4e00-\u9fff]+", part):
            tokens.extend(jieba.lcut(part, cut_all=False))
        elif re.match(r"[0-9.]+", part):
            tokens.append(part)
        else:
            sub_tokens = [
                t.strip()
                for t in re.split(r"([a-zA-Z0-9\u4e00-\u9fff]+)", part)
                if t.strip()
            ]
            tokens.extend(sub_tokens)

    return tokens


def tokenize_char(text: str) -> List[str]:
    return list(text)


def detokenize(tokens: List[str]) -> str:
    return "".join(tokens)


def get_tokenizer(mode: str = "word") -> Callable[[str], List[str]]:
    if mode == "word":
        return tokenize_word
    elif mode == "char":
        return tokenize_char
    else:
        return tokenize_word
