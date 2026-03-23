import json
import random
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Tuple

from tokenize import DEFAULT_TOKENIZER, detokenize, get_tokenizer


class MarkovChain:
    BOS_TOKEN = "<bos>"
    EOS_TOKEN = "<eos>"

    def __init__(
        self, n: int = 2, use_jieba: bool = True, tokenize_mode: str = "mixed"
    ):
        if n < 1:
            raise ValueError("n must be at least 1")
        self.n = n
        self.use_jieba = use_jieba
        self.tokenize_mode = tokenize_mode
        self.tokenizer: Callable[[str], List[str]] = get_tokenizer(
            use_jieba, tokenize_mode
        )
        self.transitions: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    def train(self, corpus: List[str]) -> None:
        if not corpus:
            raise ValueError("Corpus cannot be empty")

        for message in corpus:
            words = self.tokenizer(message)
            words = [self.BOS_TOKEN] * self.n + words + [self.EOS_TOKEN]

            for i in range(self.n, len(words)):
                prefix = tuple(words[i - self.n : i])
                next_word = words[i]
                key = self._prefix_to_key(prefix)
                if key not in self.transitions:
                    self.transitions[key] = defaultdict(int)
                self.transitions[key][next_word] += 1

    def _prefix_to_key(self, prefix: Tuple[str, ...]) -> str:
        return json.dumps(prefix, ensure_ascii=False)

    def _key_to_prefix(self, key: str) -> Tuple[str, ...]:
        return tuple(json.loads(key))

    def generate(
        self,
        start_prefix: Optional[str] = None,
        max_words: int = 50,
        eos_token: Optional[str] = None,
    ) -> str:
        if not self.transitions:
            raise ValueError("Model has not been trained or loaded")

        if eos_token is None:
            eos_token = self.EOS_TOKEN

        if start_prefix is None:
            prefix = tuple([self.BOS_TOKEN] * self.n)
        else:
            words = self.tokenizer(start_prefix)
            if len(words) >= self.n:
                prefix = tuple(words[-self.n :])
            else:
                prefix = tuple([self.BOS_TOKEN] * (self.n - len(words))) + tuple(words)

        result = list(prefix)

        for _ in range(max_words):
            key = self._prefix_to_key(prefix)
            next_words = self.transitions.get(key)

            if not next_words:
                for backoff_n in range(self.n - 1, 0, -1):
                    backoff_prefix = tuple(result[-backoff_n:])
                    if backoff_prefix:
                        key = self._prefix_to_key(backoff_prefix)
                        next_words = self.transitions.get(key)
                        if next_words:
                            prefix = backoff_prefix
                            break
                if not next_words:
                    break

            words_list = list(next_words.keys())
            weights = list(next_words.values())
            chosen = random.choices(words_list, weights=weights, k=1)[0]

            if chosen == eos_token:
                break

            result.append(chosen)
            prefix = tuple(result[-self.n :])

        result = [w for w in result if w != self.BOS_TOKEN]
        return detokenize(result)

    def save(self, path: str) -> None:
        transitions_serializable = {
            key: dict(value) for key, value in self.transitions.items()
        }
        data = {
            "n": self.n,
            "use_jieba": self.use_jieba,
            "tokenize_mode": self.tokenize_mode,
            "transitions": transitions_serializable,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "MarkovChain":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chain = cls(
            n=data["n"],
            use_jieba=data.get("use_jieba", True),
            tokenize_mode=data.get("tokenize_mode", "mixed"),
        )
        chain.transitions = {k: dict(v) for k, v in data["transitions"].items()}
        return chain
