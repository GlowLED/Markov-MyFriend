# Markov-MyFriend

> 将你的朋友压缩成仅仅使用几KB JSON文件即可表示的Markov模型，让他/她/它永远陪伴你。

N阶马尔可夫链语言生成模型

## 安装

```bash
pip install -e .
```

## 命令行使用

### train - 训练模型

```bash
markov train -i corpus.json -o model.json -n 2
```

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `-i, --input` | 是 | - | 语料库文件路径 |
| `-o, --output` | 是 | - | 模型输出文件路径 |
| `-n, --n` | 否 | 2 | 马尔可夫链阶数 |
| `--tokenize` | 否 | word | 分词模式：`word` 或 `char` |

### generate - 生成句子

```bash
markov generate -m model.json -w 30 -t 1.0
```

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `-m, --model` | 是 | - | 模型文件路径 |
| `-p, --prefix` | 否 | None | 起始前缀，如不指定则从 `<bos>` 开始 |
| `-w, --max-words` | 否 | 50 | 最大生成词数 |
| `-t, --temperature` | 否 | 1.0 | 采样温度，控制随机性 |

### interactive - 交互模式

```bash
markov interactive -m model.json -w 30 -t 1.0
```

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `-m, --model` | 是 | - | 模型文件路径 |
| `-w, --max-words` | 否 | 50 | 最大生成词数 |
| `-t, --temperature` | 否 | 1.0 | 采样温度，控制随机性 |

交互模式下：
- 输入前缀并回车生成句子
- 直接回车从 `<bos>` 开始生成
- 输入 `quit` 退出

## 温度采样说明

温度（temperature）参数控制生成时的随机性：

| 温度值 | 效果 |
|--------|------|
| `0 < t < 1` | 更确定性，倾向于选择高频词 |
| `t = 1` | 标准加权随机（默认） |
| `t > 1` | 更随机，低频词也有机会被选中 |

**示例**：

```bash
# 高随机性，可能产生更多样化的句子
markov generate -m model.json -t 2.0

# 低随机性，更倾向于生成常见搭配
markov generate -m model.json -t 0.5
```

## Python API

```python
from src.markov_chain import MarkovChain

# 创建模型
chain = MarkovChain(n=2)
chain.train(["今天天气真好", "我们去吃饭吧"])
chain.save("model.json")

# 加载模型
chain = MarkovChain.load("model.json")

# 生成句子
print(chain.generate(max_words=20))
print(chain.generate(start_prefix="今天", max_words=20))
print(chain.generate(start_prefix="今天", max_words=20, temperature=0.5))
```

### MarkovChain 类参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `n` | 2 | 马尔可夫链阶数 |
| `tokenize` | "word" | 分词模式："word" 或 "char" |

### generate() 方法参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `start_prefix` | None | 起始前缀字符串 |
| `max_words` | 50 | 最大生成词数 |
| `temperature` | 1.0 | 采样温度 |

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

程序支持两种分词模式。

| 模式 | 中文处理 | 英文处理 | 示例 |
|------|----------|----------|------|
| `word` (默认) | jieba分词 | 保留为独立词 | `"我想学Python"` → `["我", "想学", "Python"]` |
| `char` | 按字符分 | 按字符分 | `"我想学Python"` → `["我", "想", "学", "P", "y", "t", "h", "o", "n"]` |

### 分词模式

- `--tokenize word` (默认): 按词分词，中文使用jieba，英文保留完整单词
- `--tokenize char`: 按字符分词，所有字符都分开

## 模型格式

模型以JSON格式存储，可视化友好：

```json
{
  "n": 2,
  "tokenize": "word",
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

## Web UI

使用 Gradio 构建的图形化界面。

### 安装与运行

```bash
# 安装依赖
pip install -e .

# 运行 Web UI
python webui.py

# 或使用 uv
uv run python webui.py
```

Web UI 将在 `http://localhost:7860` 启动。

### 页面功能

#### 训练模型

| 组件 | 说明 |
|------|------|
| 语料库文件 | 上传 json/jsonl/csv/txt 格式的语料库 |
| n阶数 | 滑动条选择 1-5 |
| 分词模式 | 选择 word/char |
| 分词预览 | 显示语料库前3条的分词效果 |
| 模型统计 | 显示转移状态数、词汇量等 |
| 下载模型 | 训练完成后可下载模型文件 |

#### 生成文本

| 组件 | 说明 |
|------|------|
| 模型文件 | 上传模型 |
| 起始前缀 | 输入生成前缀（可选） |
| 最大词数 | 滑动条 10-200 |
| 温度 | 滑动条 0.1-3.0 |
| 生成结果 | 显示当前生成的文本 |
| 历史记录 | 显示最近3条生成结果 |
