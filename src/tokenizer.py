import re
from typing import Callable, List

import jieba


def tokenize_chinese(text: str) -> List[str]:
    return jieba.lcut(text, cut_all=False)


def tokenize_mixed(text: str) -> List[str]:
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


def detokenize(tokens: List[str]) -> str:
    result = []
    for i, token in enumerate(tokens):
        if i > 0:
            prev = tokens[i - 1]
            if re.match(r"[\u4e00-\u9fff]", token) and re.match(
                r"[\u4e00-\u9fff]", prev
            ):
                result.append(" ")
            elif re.match(r"[a-zA-Z]", token) and re.match(r"[\u4e00-\u9fff]", prev):
                result.append(" ")
            elif re.match(r"[\u4e00-\u9fff]", prev) and re.match(r"[a-zA-Z]", token):
                result.append(" ")
        result.append(token)
    return "".join(result)


DEFAULT_TOKENIZER = tokenize_mixed


def get_tokenizer(
    use_jieba: bool = True, mode: str = "mixed"
) -> Callable[[str], List[str]]:
    if not use_jieba:
        return lambda text: text.split()

    if mode == "chinese":
        return tokenize_chinese
    elif mode == "mixed":
        return tokenize_mixed
    else:
        return lambda text: text.split()
