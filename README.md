# Markov-MyFriend

N阶马尔可夫链语言生成模型

## 安装

```bash
pip install -e .
```

## 使用方法

```bash
# 训练
markov train -i corpus.json -o model.json -n 2

# 生成句子
markov generate -m model.json -w 30

# 交互模式
markov interactive -m model.json -w 30
```

### Python API

```python
from src.markov_chain import MarkovChain

chain = MarkovChain(n=2)
chain.train(["今天天气真好", "我们去吃饭吧"])
chain.save("model.json")

chain = MarkovChain.load("model.json")
print(chain.generate(max_words=20))
print(chain.generate(start_prefix="今天", max_words=20))
```

## 语料库格式

支持 `.json`, `.jsonl`, `.csv`, `.txt` 格式
