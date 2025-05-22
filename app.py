from flask import Flask, request, render_template, jsonify
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure the API key for Google Generative AI
genai.configure(api_key=api_key)

# Initialize the Generative Model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Function to count words in the input text
def count_words(text):
    return len(text.split())

# Define the prompt function for analyzing cyberbullying
def analyze_cyberbullying(text):
    total_words = count_words(text)
    prompt = (
        "Classify the given sentence into one or more of the following cyberbullying CATEGORY: Race/Ethnicity, Gender/Sexual, Religion, Harassment, Flaming/Trolling, Dissing;"
        "IF the CATEGORY is Race/Ethnicity, Gender/Sexual or Religion, then write the TYPE as Identity-based;"
        "IF the CATEGORY is Harassment, Flaming/Trolling, or Dissing, then write the TYPE as Behavioral-based;"
        "Write CATEGORY first, then TYPE on separate lines;"
        "If the sentence is not cyberbullying, write CATEGORY as 'Not Cyberbullying';"
        "If the sentence falls under more than one category, display all the most appropriate categories only;"
        "HARMFUL CONTENT: Display only the individual harmful words from the sentence as a list, each marked with ⚠️ in the beginning. Do not include phrases, explanations, or additional text;"
        "If the sentence is not cyberbullying, write HARMFUL CONTENT as 'Not applicable';"
        "REASON:  Briefly explain why each harmful word listed in HARMFUL CONTENT is flagged, with simple language and no extra explanation;"
        f"TOTAL WORDS: {total_words};"
        "FLAGGED PERCENTAGE: Display the percentage along with the breakdown like this: 20% (Harmful = 2 / Total = 10);"
        "SUGGESTED ALTERNATIVES: Understand the emotion and intent of the input sentence and suggest exactly 2 neutral/safer ways to express it, avoiding vagueness or placeholders; no extra explanation. Use numbering;"
        f"Sentence: {text}"
    )
    
    # Get the response from the AI model
    response = model.generate_content([prompt])
    cleaned_output = re.sub(r'\*\*|\*|## |"', '', response.text)
    return cleaned_output.strip()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.form['text']

    # Call the analyze_cyberbullying function
    final_output = analyze_cyberbullying(text)

    # Combine user input and result for display
    result = f"INPUT SENTENCE: {text}\n\n{final_output}"
    
    # Parse the result to structure it for display
    result_lines = result.split('\n')
    result_dict = {
        'input': text,
        'result': result
    }
    return jsonify(result_dict)

if __name__ == '__main__':
    app.run(debug=True)
