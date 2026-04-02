from setuptools import setup, find_packages

setup(
    name="warhammer-board-agent",
    version="1.0.0",
    description="Interactive agent for designing custom Warhammer tabletop boards",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "rich>=13.7.0",
        "prompt_toolkit>=3.0.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "warhammer-board=warhammer_board_agent.main:main",
        ],
    },
)
