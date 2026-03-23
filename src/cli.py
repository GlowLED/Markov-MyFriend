import argparse
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from src.markov_chain import MarkovChain
from src.corpus_loader import load_corpus


def cmd_train(args):
    corpus = load_corpus(args.input)
    print(f"Loaded {len(corpus)} messages from {args.input}")

    chain = MarkovChain(n=args.n, tokenize=args.tokenize)
    chain.train(corpus)
    print(f"Trained model with n={args.n}, tokenize={args.tokenize}")

    chain.save(args.output)
    print(f"Model saved to {args.output}")


def cmd_generate(args):
    chain = MarkovChain.load(args.model)

    text = chain.generate(
        start_prefix=args.prefix if args.prefix else None,
        max_words=args.max_words,
        temperature=args.temperature,
    )
    print(text)


def cmd_interactive(args):
    chain = MarkovChain.load(args.model)
    print(
        "Interactive mode. Enter a prefix (or press Enter to start from <bos>). Type 'quit' to exit.\n"
    )

    while True:
        try:
            user_input = input("> ")
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if user_input.strip().lower() == "quit":
            print("Bye!")
            break

        prefix = user_input if user_input.strip() else None
        text = chain.generate(
            start_prefix=prefix, max_words=args.max_words, temperature=args.temperature
        )
        print(text)


def main():
    parser = argparse.ArgumentParser(description="N阶马尔可夫链语言生成模型")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    train_parser = subparsers.add_parser("train", help="训练模型")
    train_parser.add_argument("-i", "--input", required=True, help="语料库文件路径")
    train_parser.add_argument("-o", "--output", required=True, help="模型输出路径")
    train_parser.add_argument(
        "-n", "--n", type=int, default=2, help="马尔可夫链阶数 (默认: 2)"
    )
    train_parser.add_argument(
        "--tokenize",
        choices=["word", "char"],
        default="word",
        help="分词模式: word=按词分词(默认), char=按字符分词",
    )

    gen_parser = subparsers.add_parser("generate", help="生成句子")
    gen_parser.add_argument("-m", "--model", required=True, help="模型文件路径")
    gen_parser.add_argument("-p", "--prefix", help="起始前缀 (可选)")
    gen_parser.add_argument(
        "-w", "--max-words", type=int, default=50, help="最大词数 (默认: 50)"
    )
    gen_parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=1.0,
        help="采样温度，控制随机性 (默认: 1.0，>1更随机，<1更确定)",
    )

    inter_parser = subparsers.add_parser("interactive", help="交互模式")
    inter_parser.add_argument("-m", "--model", required=True, help="模型文件路径")
    inter_parser.add_argument(
        "-w", "--max-words", type=int, default=50, help="最大词数 (默认: 50)"
    )
    inter_parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=1.0,
        help="采样温度，控制随机性 (默认: 1.0，>1更随机，<1更确定)",
    )

    args = parser.parse_args()

    if args.command == "train":
        cmd_train(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "interactive":
        cmd_interactive(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
