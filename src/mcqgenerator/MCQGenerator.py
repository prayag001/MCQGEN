import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from src.mcqgenerator.logger import logging

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

TEMPLATE = '''
Text:{text}
You are an expert MCQ maker. Given the above text, create a quiz of {number} multiple choice questions for {subject} students with {tone} difficulty level.
Make sure the questions are not repeated and check all the questions to be conforming to the text as well.

CRITICAL: Your response must be ONLY a valid JSON object with NO additional text or explanations.
Format your response EXACTLY like this example (maintaining all quotes and commas):

{response_json}

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
'''

TEMPLATE2 = """
You are an expert English grammar checker and writer. Give a multiple choice quiz for {subject} students.
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity check.
If there are quiz questions which need to be changed, modify the tone such that it is proper for student abilities.
Quiz_MCQs:
{quiz}

Check from an expert English writer of the above quiz:
"""

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
            .strip()           # Remove leading/trailing whitespace again
        )
        
        # Try to parse the JSON
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Error processing quiz response: {str(e)}")

def generate_mcq(text, number, subject, tone, response_json):
    """Generate MCQs using Gemini"""
    try:
        # Format the prompt
        prompt = TEMPLATE.format(
            text=text,
            number=number,
            subject=subject,
            tone=tone,
            response_json=json.dumps(response_json, indent=2)
        )
        
        # Generate MCQs
        response = model.generate_content(prompt)
        quiz_json = clean_and_validate_json(response.text)
        
        # Generate review
        review_prompt = TEMPLATE2.format(
            subject=subject,
            quiz=json.dumps(quiz_json, indent=2)
        )
        review_response = model.generate_content(review_prompt)
        
        return {
            "quiz": quiz_json,
            "review": review_response.text
        }
    except Exception as e:
        raise Exception(f"Error generating quiz: {str(e)}")

def process_mcq_generation(text, number, subject, tone, response_json):
    """Process MCQ generation with error handling"""
    try:
        response = generate_mcq(
            text=text,
            number=number,
            subject=subject,
            tone=tone,
            response_json=response_json
        )
        return response
    except Exception as e:
        raise Exception(f"Error generating quiz: {str(e)}")

