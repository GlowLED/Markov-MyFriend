import argparse
import sys

from src.markov_chain import MarkovChain
from src.corpus_loader import load_corpus


def cmd_train(args):
    corpus = load_corpus(args.input)
    print(f"Loaded {len(corpus)} messages from {args.input}")

    chain = MarkovChain(
        n=args.n,
        use_jieba=not args.no_jieba,
        tokenize_mode=args.tokenize_mode,
    )
    chain.train(corpus)
    print(
        f"Trained model with n={args.n}, use_jieba={not args.no_jieba}, mode={args.tokenize_mode}"
    )

    chain.save(args.output)
    print(f"Model saved to {args.output}")


def cmd_generate(args):
    chain = MarkovChain.load(args.model)

    text = chain.generate(
        start_prefix=args.prefix if args.prefix else None,
        max_words=args.max_words,
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
        text = chain.generate(start_prefix=prefix, max_words=args.max_words)
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
        "--no-jieba",
        action="store_true",
        help="禁用jieba分词，使用空格分词",
    )
    train_parser.add_argument(
        "--tokenize-mode",
        choices=["mixed", "chinese"],
        default="mixed",
        help="分词模式: mixed=中英文混合, chinese=纯中文 (默认: mixed)",
    )

    gen_parser = subparsers.add_parser("generate", help="生成句子")
    gen_parser.add_argument("-m", "--model", required=True, help="模型文件路径")
    gen_parser.add_argument("-p", "--prefix", help="起始前缀 (可选)")
    gen_parser.add_argument(
        "-w", "--max-words", type=int, default=50, help="最大词数 (默认: 50)"
    )

    inter_parser = subparsers.add_parser("interactive", help="交互模式")
    inter_parser.add_argument("-m", "--model", required=True, help="模型文件路径")
    inter_parser.add_argument(
        "-w", "--max-words", type=int, default=50, help="最大词数 (默认: 50)"
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
