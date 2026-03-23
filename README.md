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

支持 `.json`, `.jsonl`, `.csv`, `.txt` 四种格式。

每条消息是一个完整的句子，程序会自动使用jieba分词处理。

### JSON (.json)

JSON数组，每项为字符串：

```json
[
  "今天天气真好",
  "明天要下雨，记得带伞",
  "晚上一起吃饭吗"
]
```

### JSONL (.jsonl)

每行一个JSON字符串（适合大语料库）：

```json
{"msg": "今天天气真好"}
{"msg": "明天要下雨，记得带伞"}
{"msg": "晚上一起吃饭吗"}
```

也支持简单字符串格式：

```json
"今天天气真好"
"明天要下雨，记得带伞"
"晚上一起吃饭吗"
```

### CSV (.csv)

逗号分隔，第一列为消息内容：

```csv
今天天气真好
明天要下雨，记得带伞
晚上一起吃饭吗
```

### TXT (.txt)

每行一条消息：

```
今天天气真好
明天要下雨，记得带伞
晚上一起吃饭吗
```

## 分词说明

程序使用jieba分词处理中文，支持中英文混合语料。

**示例**：输入 `"我想学Python编程"`
分词结果：`["我", "想学", "Python", "编程"]`

### 分词模式

- `--tokenize-mode mixed` (默认): 中英文混合分词
- `--tokenize-mode chinese`: 纯中文分词
- `--no-jieba`: 禁用jieba，按空格分词

## 模型格式

模型以JSON格式存储，可视化友好：

```json
{
  "n": 2,
  "use_jieba": true,
  "tokenize_mode": "mixed",
  "transitions": {
    "[\"<bos>\", \"<bos>\"]": {
      "今天天气": 1,
      "明天": 1
    }
  }
}
```

## 特殊Token

- `<bos>`: 句子开始标记
- `<eos>`: 句子结束标记
