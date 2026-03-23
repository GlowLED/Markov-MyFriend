import tempfile
import uuid
from pathlib import Path

import gradio as gr

from src.markov_chain import MarkovChain
from src.corpus_loader import load_corpus
from src.tokenizer import get_tokenizer


GENERATION_HISTORY: list[str] = []


def read_file(file_obj):
    if file_obj is None:
        return None
    if isinstance(file_obj, (str, Path)):
        with open(file_obj, "rb") as f:
            return f.read()
    if hasattr(file_obj, "read"):
        return file_obj.read()
    if isinstance(file_obj, bytes):
        return file_obj
    if hasattr(file_obj, "__bytes__"):
        return bytes(file_obj)
    return file_obj


def train_model(corpus_file, n: int, tokenize: str):
    if corpus_file is None:
        return "请上传语料库文件", "", None, None

    try:
        file_data = read_file(corpus_file)
        if file_data is None:
            return "无法读取文件", "", None, None

        suffix = Path(corpus_file).suffix if hasattr(corpus_file, "suffix") else ".txt"
        temp_path = Path(tempfile.mktemp(suffix=suffix))
        with open(temp_path, "wb") as f:
            f.write(file_data)

        corpus = load_corpus(str(temp_path))
        temp_path.unlink()

        if len(corpus) == 0:
            return "语料库为空", "", None, None

        preview_texts = []
        test_tokenizer = get_tokenizer(tokenize)
        for msg in corpus[:3]:
            tokens = test_tokenizer(msg)
            preview_texts.append(f"原文: {msg}\n分词: {' '.join(tokens)}")
        preview = "\n\n".join(preview_texts)

        chain = MarkovChain(n=n, tokenize=tokenize)
        chain.train(corpus)

        transitions_count = len(chain.transitions)
        vocab = set()
        for trans in chain.transitions.values():
            vocab.update(trans.keys())
        for key in chain.transitions.keys():
            vocab.update(eval(key))
        vocab.discard("<bos>")
        vocab.discard("<eos>")
        vocab_size = len(vocab)

        stats = f"""训练完成！
- 语料数量: {len(corpus)}
- 转移状态数: {transitions_count}
- 词汇量: {vocab_size}
- n阶数: {n}
- 分词模式: {tokenize}"""

        model_path = (
            Path(tempfile.gettempdir()) / f"markov_model_{uuid.uuid4().hex[:8]}.json"
        )
        chain.save(str(model_path))

        return stats, preview, str(model_path), ""

    except Exception as e:
        return f"训练失败: {str(e)}", "", None, None


def generate_text(model_file, prefix: str, max_words: int, temperature: float):
    global GENERATION_HISTORY

    if model_file is None:
        return "请上传模型文件", "\n".join(
            GENERATION_HISTORY[-3:]
        ) if GENERATION_HISTORY else ""

    try:
        file_data = read_file(model_file)
        if file_data is None:
            return "无法读取模型文件", "\n".join(
                GENERATION_HISTORY[-3:]
            ) if GENERATION_HISTORY else ""

        temp_path = Path(tempfile.mktemp(suffix=".json"))
        with open(temp_path, "wb") as f:
            f.write(file_data)

        chain = MarkovChain.load(str(temp_path))
        temp_path.unlink()

        prefix_text = prefix if prefix.strip() else None
        result = chain.generate(
            start_prefix=prefix_text,
            max_words=max_words,
            temperature=temperature,
        )

        GENERATION_HISTORY.append(result)
        if len(GENERATION_HISTORY) > 10:
            GENERATION_HISTORY = GENERATION_HISTORY[-10:]

        history = "\n---\n".join(GENERATION_HISTORY[-3:]) if GENERATION_HISTORY else ""
        return result, history

    except Exception as e:
        return f"生成失败: {str(e)}", "\n".join(
            GENERATION_HISTORY[-3:]
        ) if GENERATION_HISTORY else ""


def build_webui():
    with gr.Blocks(title="Markov-MyFriend") as demo:
        gr.Markdown("# Markov-MyFriend\n> 将你的朋友压缩成Markov模型")
        gr.Markdown("---")

        with gr.Tabs():
            with gr.TabItem("训练模型"):
                with gr.Row():
                    with gr.Column():
                        corpus_file = gr.File(
                            label="语料库文件",
                            file_types=[".json", ".jsonl", ".csv", ".txt"],
                        )
                        n = gr.Slider(
                            minimum=1, maximum=5, step=1, value=2, label="n阶数"
                        )
                        tokenize = gr.Dropdown(
                            choices=["word", "char"],
                            value="word",
                            label="分词模式",
                            info="word: 按词分词(中文用jieba)；char: 按字符分词",
                        )
                        train_btn = gr.Button("开始训练", variant="primary")

                    with gr.Column():
                        preview = gr.Textbox(
                            label="分词预览", lines=5, interactive=False
                        )
                        stats = gr.Textbox(label="模型统计", lines=5, interactive=False)
                        train_output = gr.Textbox(
                            label="训练状态", lines=2, interactive=False
                        )
                        model_download = gr.File(label="下载模型")

                train_btn.click(
                    fn=train_model,
                    inputs=[corpus_file, n, tokenize],
                    outputs=[stats, preview, model_download, train_output],
                )

            with gr.TabItem("生成文本"):
                with gr.Row():
                    with gr.Column():
                        gen_model_file = gr.File(
                            label="模型文件",
                            file_types=[".json"],
                        )
                        prefix = gr.Textbox(
                            label="起始前缀",
                            placeholder="输入前缀（可选，不输入则从<bos>开始）",
                        )
                        max_words = gr.Slider(
                            minimum=10, maximum=200, step=10, value=50, label="最大词数"
                        )
                        temperature = gr.Slider(
                            minimum=0.1, maximum=3.0, step=0.1, value=1.0, label="温度"
                        )
                        gen_btn = gr.Button("生成", variant="primary")

                    with gr.Column():
                        gen_result = gr.Textbox(
                            label="生成结果", lines=3, interactive=False
                        )
                        history = gr.Textbox(
                            label="历史记录（最近3条）", lines=5, interactive=False
                        )

                gen_btn.click(
                    fn=generate_text,
                    inputs=[gen_model_file, prefix, max_words, temperature],
                    outputs=[gen_result, history],
                )

    return demo


if __name__ == "__main__":
    demo = build_webui()
    demo.launch(server_name="0.0.0.0", server_port=7860)
