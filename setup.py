from setuptools import setup, find_packages

setup(
    name="mcqgenerator",
    version="0.0.1",
    author="Prayag Sonar",
    author_email="prayagsonar001@gmail.com",
    install_requires=["openai", "langchain",
                      "streamlit", "python-dotenv", "PyPDF2"],
    packages=find_packages())
