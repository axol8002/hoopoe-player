from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hoopoe-player",
    version="0.1.2",
    description="Play any video as colorful ASCII art in your terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Adriel Molina",
    author_email="adrielmolinacaceres@gmail.com",
    url="https://github.com/axol8002/hoopoe-player",
    packages=find_packages(),
    install_requires=[
        "yt-dlp",
        "yt-dlp-ejs",
        "opencv-python",
    ],
    entry_points={
        "console_scripts": [
            "hoopoe=hoopoe.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Topic :: Multimedia :: Video",
    ],
    keywords="ascii art terminal video youtube player cli hoopoe",
)
