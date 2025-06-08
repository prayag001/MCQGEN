import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from src.mcqgenerator.logger import logging
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.MCQGenerator import process_mcq_generation

# Load environment variables
load_dotenv()

# Load response JSON template
with open("Response.json", "r") as file:
    RESPONSE_JSON = json.load(file)
    
st.title("MCQ Generator App")

# Create form for user inputs
with st.form("user_inputs"):
    # File upload
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
    
    # MCQ count input
    mcq_count = st.number_input("Number of MCQs to generate", min_value=3, max_value=50, value=5)
    
    # Subject input
    subject = st.text_input("Input Subject", max_chars=50)
    
    # Complexity level input
    tone = st.text_input("Complexity Level of Questions", max_chars=20, placeholder="Simple") 
    
    # Submit button
    button = st.form_submit_button("Generate MCQs")

# Process when button is clicked
if button and uploaded_file is not None and mcq_count and subject and tone:
    with st.spinner("Generating MCQs..."):
        try:
            # Read the uploaded file
            text = read_file(uploaded_file)
            
            try:
                response = process_mcq_generation(
                    text=text,
                    number=mcq_count,
                    subject=subject,
                    tone=tone,
                    response_json=RESPONSE_JSON
                )
            except Exception as e:
                if "Error processing quiz response" in str(e):
                    st.error("⚠️ The MCQ generation produced invalid output. Retrying...")
                    # Retry once with the same parameters
                    response = process_mcq_generation(
                        text=text,
                        number=mcq_count,
                        subject=subject,
                        tone=tone,
                        response_json=RESPONSE_JSON
                    )
                else:
                    raise e
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            if "Error processing quiz response" in str(e):
                st.error("The quiz output format was invalid. Please try again.")
            logging.error(f"Error during MCQ generation: {str(e)}")
            st.stop()
        else:
            if isinstance(response, dict):
                # Extract quiz from response
                quiz = response.get("quiz", None)
                if quiz is not None:
                    try:
                        # Quiz is already validated at this point
                        table_data = get_table_data(quiz)
                        if table_data:
                            st.subheader("Generated MCQs")
                            # Create DataFrame and set column names explicitly
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            
                            # Rename columns for better display
                            df.columns = ['Question', 'Options', 'Answer']
                            
                            # Apply custom styling to the table
                            st.markdown("""
                                <style>
                                    .dataframe {width: 100% !important}
                                    .dataframe td {text-align: left !important; white-space: normal !important;}
                                    .dataframe th {text-align: left !important;}
                                </style>
                            """, unsafe_allow_html=True)
                            
                            st.table(df)
                            
                            # Display review
                            st.subheader("Review")
                            st.text_area(label="", value=response["review"], height=200)
                            
                        else:
                            st.error("Failed to process the quiz data.")
                            st.write("Debug: Quiz structure received:")
                            st.json(quiz)
                    except Exception as e:
                        st.error(f"Error displaying quiz: {str(e)}")
                        st.write("Debug info:")
                        st.write(f"Quiz type: {type(quiz)}")
                        st.write("Quiz content:")
                        st.code(quiz)
                else:
                    st.error("No quiz data found in the response.")
            else:
                st.error("Received an invalid response format. Please try again.")
elif button:
    if uploaded_file is None:
        st.warning("Please upload a file first.")
    if not subject:
        st.warning("Please enter a subject.")
    if not tone:
        st.warning("Please enter a complexity level.")