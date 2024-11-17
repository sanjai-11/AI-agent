from flask import Flask, render_template, request, redirect
import google.generativeai as genai
import os
import json
from database import init_db, fetch_records, backend  # Import database functions
from difflib import get_close_matches

app = Flask(__name__)

# Function to correct typos
def correct_typo(word, possibilities):
    if not word:  # If word is None or empty, return it as is
        return word
    matches = get_close_matches(word.lower(), possibilities, n=1, cutoff=0.8)
    return matches[0] if matches else word


# Function to sanitize inputs
def sanitize_input(input_string):
    # Remove unnecessary quotes around keys and values
    if isinstance(input_string, str):
        return input_string.strip('"\' ')  # Remove double, single quotes, and spaces
    return input_string

class BackendAgent:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')

    def process_gemini_output(self, output):
        valid_actions = ["insert", "update", "delete"]

        if isinstance(output, dict):  # Single operation
            action = sanitize_input(output.get('action'))
            key = sanitize_input(output.get('key'))
            value = sanitize_input(output.get('value'))

            action = correct_typo(action, valid_actions)
            backend(action, key, value)

        elif isinstance(output, list):  # Multiple operations
            for operation in output:
                action = sanitize_input(operation.get('action'))
                key = sanitize_input(operation.get('key'))
                value = sanitize_input(operation.get('value'))

                # Ensure typo correction and process each operation
                action = correct_typo(action, valid_actions) if action else action
                backend(action, key, value)


    @staticmethod
    @app.route('/', methods=['GET', 'POST'])
    def index():
        agent = BackendAgent()  # Create an instance of BackendAgent
        if request.method == 'POST':
            # Get natural language prompt from user
            prompt = request.form['prompt']

            # Generate structured output from Gemini model
            total_prompt = f"""
            Please extract the action word, key, and value from the following input. Provide the output exactly in the JSON format specified and do not include any additional information.
            Input: {prompt}"""
            response = agent.model.generate_content(total_prompt)

            json_text = response.text  # Get the response from the model
            if json_text.startswith("```json"):
                json_text = json_text.lstrip("```json").rstrip("```").strip()

            try:
                json_object = json.loads(json_text)
                agent.process_gemini_output(json_object)  # Process the structured JSON output
            except json.JSONDecodeError as e:
                print("JSONDecodeError:", e)
                print("Invalid JSON:", json_text)
                return redirect('/')
            
            """total_prompt = f"""
            #Please extract the action word, key, and value from the following input. Provide the output exactly in the JSON file specified and do not include any additional information.

            #Input: {prompt}
            """
            response = agent.model.generate_content(total_prompt)

            json_text = response.text  # Replace this with your actual response

            if json_text.startswith("```json"):
                json_text = json_text.lstrip("```json").rstrip("```").strip()

            try:
                json_object = json.loads(json_text)
            except json.JSONDecodeError as e:
                print("JSONDecodeError:", e)
                print("Invalid JSON:", json_text)
                return redirect('/')"""

            print(json_object)
            agent.process_gemini_output(json_object)

            return redirect('/')

        # Fetch and display records
        records = fetch_records()
        return render_template('home.html', records=records)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
