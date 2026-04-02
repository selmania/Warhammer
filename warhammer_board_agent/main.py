"""Entry point for the Warhammer Board Design Agent."""

from .agent import BoardAgent


def main() -> None:
    agent = BoardAgent()
    agent.run()


if __name__ == "__main__":
    main()
