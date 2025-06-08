import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from src.mcqgenerator.logger import logging
from src.mcqgenerator.utils import read_file, get_table_data
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain

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
            
            # Generate MCQs and track token usage
            with get_openai_callback() as cb:
                response = generate_evaluate_chain(
                    text=text,
                    number=mcq_count,
                    subject=subject,
                    tone=tone,
                    response_json=RESPONSE_JSON
                )
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            logging.error(f"Error during MCQ generation: {str(e)}")
            st.error("An error occurred while generating MCQs. Please try again.")
        else:
            if isinstance(response, dict):
                # Extract quiz from response
                quiz = response.get("quiz", None)
                if quiz is not None:
                    table_data = get_table_data(quiz)
                    if table_data:
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1
                        st.table(df)
                        
                        # Display review
                        st.subheader("Review")
                        st.text_area(label="", value=response["review"], height=200)
                        
                        # Display token usage
                        st.divider()
                        st.markdown("### Token Usage Information")
                        st.write(f"Total Tokens Used: {cb.total_tokens}")
                        st.write(f"Prompt Tokens: {cb.prompt_tokens}")
                        st.write(f"Completion Tokens: {cb.completion_tokens}")
                        st.write(f"Total Cost (USD): ${cb.total_cost:.4f}")
                    else:
                        st.error("Failed to process the quiz data. Please try again.")
                else:
                    st.error("No quiz was generated. Please check your inputs and try again.")
            else:
                st.error("Received an invalid response format. Please try again.")
elif button:
    if uploaded_file is None:
        st.warning("Please upload a file first.")
    if not subject:
        st.warning("Please enter a subject.")
    if not tone:
        st.warning("Please enter a complexity level.")