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
        # convert the quiz from a str to a dict
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []

        # iterate through the quiz_dict to get the required data
        for key, value in quiz_dict.items():
            mcq = value['mcq']
            options = " || ".join(
                [f"{option}->{option_value}" for option,
                    option_value in value['options'].items()]
            )
            correct = value["correct"]
            quiz_table_data.append(
                {"MCQ": mcq,
                 "Choices": options,
                 "Correct": correct}
            )
        return quiz_table_data
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
