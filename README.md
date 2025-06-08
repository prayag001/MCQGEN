# MCQ Generator

A Streamlit-based application that automatically generates multiple-choice questions (MCQs) from text or PDF documents using OpenAI's GPT model.

## Features

- Generate MCQs from PDF or TXT files
- Customize number of questions (3-50)
- Set subject and complexity level
- Automatic answer validation
- Response evaluation and complexity analysis
- Token usage tracking

## Prerequisites

- Python 3.10 or higher
- Conda (recommended for environment management)
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MCQGEN
```

2. Create and activate Conda environment:
```bash
conda env create -f environment.yml
conda activate ./env
```

3. Set up environment variables:
Create a `.env` file in the root directory and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Project Structure

```
├── data.txt                # Sample input file
├── Response.json           # Response template
├── StreamlitAPP.py        # Main Streamlit application
├── src/
│   └── mcqgenerator/
│       ├── MCQGenerator.py # Core MCQ generation logic
│       ├── utils.py       # Utility functions
│       └── logger.py      # Logging configuration
└── requirements.txt       # Python dependencies
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run StreamlitAPP.py
```

2. Upload a PDF or TXT file containing the text you want to generate questions from.

3. Configure the generation parameters:
   - Number of MCQs (3-50)
   - Subject
   - Complexity Level (e.g., Simple, Moderate, Complex)

4. Click "Generate MCQs" to create questions

5. View the generated questions and their analysis

## Features in Detail

- **File Support**: Handles both PDF and TXT files
- **Customizable Output**: Generate between 3 to 50 questions
- **Quality Control**: Includes an expert review system for question quality
- **Cost Tracking**: Monitors token usage and associated costs
- **Error Handling**: Robust error handling with detailed logging

## Logs

The application generates detailed logs in the `logs/` directory with timestamps for debugging and monitoring.

## Dependencies

Major dependencies include:
- streamlit
- langchain
- openai
- python-dotenv
- PyPDF2
- pandas

## Error Handling

The application includes comprehensive error handling for:
- File reading issues
- API failures
- Invalid inputs
- Response parsing errors

## Contributing

Feel free to submit issues and enhancement requests!
