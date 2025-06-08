import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.logger import logging
from src.mcqgenerator.utils import read_file, get_table_data

# importing necessary packages from langchain
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.chains.llm import LLMChain

# load environment variables
load_dotenv()

key = os.getenv("OPENAI_API_KEY")
if not key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

llm = ChatOpenAI(
    openai_api_key=key,
    model="gpt-3.5-turbo",
    temperature=0.7)

TEMPLATE = """
Text:{text}
You are an expert MCQ maker, Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone}.
Make sure the questions are not repeated and check all the questions to be conforming to the text as well.
Make sure to format your response like RESPONSE_JSON and use it as a guide.\
Ensure to make {number} MCQs
###Response JSON
{response_json}
"""

quiz_generator_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=TEMPLATE)

quiz_chain = LLMChain(
    llm=llm,
    prompt=quiz_generator_prompt,
    output_key="quiz",
    verbose=True
)

TEMPLATE2 = """
You are an expert English grammar checker and writer. Give a multiple choice quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity check. \
If there are quiz questions which need to be changed, modify the tone such that it is proper for student abilities. \
Quiz_MCQs:
{quiz}

Check from an expert English writer of the above quiz:
"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=TEMPLATE2
)

review_chain = LLMChain(
    llm=llm,
    prompt=quiz_evaluation_prompt,
    output_key="review",
    verbose=True)

generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["text", "number", "subject", "tone", "response_json"],
    output_variables=["quiz", "review"],
    verbose=True
)

