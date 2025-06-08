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

TEMPLATE = '''
Text:{text}
You are an expert MCQ maker. Given the above text, create a quiz of {number} multiple choice questions for {subject} students with {tone} difficulty level.
Make sure the questions are not repeated and check all the questions to be conforming to the text as well.

CRITICAL: Your response must be ONLY a valid JSON object with NO additional text or explanations.
Format your response EXACTLY like this example (maintaining all quotes and commas):

{{
    "1": {{
        "mcq": "What is the question?",
        "options": {{
            "a": "First option",
            "b": "Second option",
            "c": "Third option",
            "d": "Fourth option"
        }},
        "correct": "a"
    }},
    "2": {{
        "mcq": "Second question?",
        "options": {{
            "a": "First option",
            "b": "Second option",
            "c": "Third option",
            "d": "Fourth option"
        }},
        "correct": "b"
    }}
}}

Rules:
1. Start your response with {{ and end with }}
2. Use double quotes (") for ALL strings, never single quotes
3. Add commas after EVERY key-value pair EXCEPT the last one in each object
4. Add commas after EVERY object EXCEPT the last one
5. DO NOT add any text before or after the JSON
6. DO NOT add any explanations or comments
7. Make sure each question number is a string (e.g. "1" not 1)
8. Make exactly {number} questions
9. Format exactly like the example above

Input your questions into this exact format:
{response_json}
'''

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

def clean_and_validate_json(json_str):
    """Clean and validate JSON string"""
    try:
        # If it's already a dict, return it
        if isinstance(json_str, dict):
            return json_str
            
        # Remove any leading/trailing whitespace and newlines
        json_str = json_str.strip()
        
        # Remove any text before the first { and after the last }
        start = json_str.find('{')
        end = json_str.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON object found in response")
        json_str = json_str[start:end]
        
        # Clean the string
        json_str = (
            json_str
            .replace('\n', '')  # Remove newlines
            .replace('\r', '')  # Remove carriage returns
            .replace('\t', '')  # Remove tabs
            .replace('\\', '')  # Remove backslashes
            .replace('"{', '{')  # Fix escaped JSON
            .replace('}"', '}')
            .replace("'", '"')  # Replace single quotes with double quotes
        )
        
        # Parse the JSON
        try:
            quiz_dict = json.loads(json_str)
        except json.JSONDecodeError:
            # If that fails, try ast.literal_eval as a fallback
            import ast
            quiz_dict = ast.literal_eval(json_str)
            # Convert to proper JSON structure
            quiz_dict = json.loads(json.dumps(quiz_dict))
        
        # Validate structure
        if not isinstance(quiz_dict, dict):
            raise ValueError("Quiz must be a dictionary/object")
            
        for key, value in quiz_dict.items():
            if not isinstance(value, dict):
                raise ValueError(f"Question {key} must be an object")
            if not all(k in value for k in ["mcq", "options", "correct"]):
                raise ValueError(f"Question {key} missing required fields")
            if not isinstance(value["options"], dict):
                raise ValueError(f"Options for question {key} must be an object")
            if not all(opt in value["options"] for opt in ['a', 'b', 'c', 'd']):
                raise ValueError(f"Question {key} missing some options")
            if value["correct"] not in ['a', 'b', 'c', 'd']:
                raise ValueError(f"Question {key} has invalid correct answer")
                
        return quiz_dict
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}\nResponse was: {json_str}")
    except Exception as e:
        raise ValueError(f"Error validating quiz format: {str(e)}\nResponse was: {json_str}")

def process_mcq_generation(text, number, subject, tone, response_json):
    """Process MCQ generation with improved error handling"""
    try:
        # Call the chain with a dictionary of inputs
        response = generate_evaluate_chain({
            "text": text,
            "number": number,
            "subject": subject,
            "tone": tone,
            "response_json": json.dumps(response_json, indent=2)
        })
        
        # Clean and validate the quiz JSON
        if isinstance(response.get("quiz"), (str, dict)):
            response["quiz"] = clean_and_validate_json(response["quiz"])
        else:
            raise ValueError("No quiz data in response")
            
        return response
    except Exception as e:
        raise Exception(f"Error generating quiz: {str(e)}")

