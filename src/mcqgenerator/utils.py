import os
import PyPDF2
import json
import traceback


def read_file(file):
    if file.name.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise ValueError("Error reading PDF file")

    elif file.name.endswith('.txt'):
        return file.read().decode('utf-8')

    else:
        raise Exception(
            "Unsupported file format. Please upload a .pdf or .txt file.")


def get_table_data(quiz_str):
    try:
        # Handle both string and dict inputs
        if isinstance(quiz_str, str):
            try:
                quiz_dict = json.loads(quiz_str)
            except json.JSONDecodeError:
                # If it's not valid JSON, try to evaluate it as a Python literal
                import ast
                quiz_dict = ast.literal_eval(quiz_str)
        else:
            quiz_dict = quiz_str

        quiz_table_data = []
        
        # iterate through the quiz_dict to get the required data
        for key, value in quiz_dict.items():
            mcq = value.get('mcq', '')
            options = value.get('options', {})
            correct = value.get('correct', '')
            
            # Format options with line breaks for better readability
            options_str = "\n".join(
                [f"{option}) {opt_value}" for option, opt_value in options.items()]
            ) if options else ""
            
            quiz_table_data.append({
                "Question": mcq,
                "Options": options_str,
                "Answer": correct.upper()  # Capitalize the answer letter
            })
        
        return quiz_table_data if quiz_table_data else None
    except Exception as e:
        print(f"Error processing quiz data: {str(e)}")
        traceback.print_exception(type(e), e, e.__traceback__)
        return None
