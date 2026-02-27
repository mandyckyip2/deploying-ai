AI Therapy Chat Application

Overview

This project implements an AI-powered mental wellness support chatbot using the OpenAI Responses API and Gradio.

The system integrates:
	•	An inspirational quote service
	•	A structured 9-question preliminary mental health intake
	•	Cosine similarity search over a depression dataset
	•	Supportive conversational guidance

This project is for educational purposes only and does not provide medical diagnosis.

Features

1. Quote Service

Retrieves a health-related inspirational quote at the start of each session.

2. Preliminary Assessment

Collects:
	•	Name
	•	9 structured mental health intake questions

3. Dataset Similarity Search
	•	Uses TF-IDF vectorization
	•	Computes cosine similarity between user responses and a depression dataset
	•	Returns the closest matching entry and similarity score

The similarity score is used as a reference signal, not a diagnosis.

4. Conversational Support

Provides:
	•	Reflective listening
	•	Gentle follow-up questions
	•	Basic coping suggestions

Tech Stack
	•	Python
	•	OpenAI Responses API
	•	Gradio
	•	pandas
	•	scikit-learn (TF-IDF + cosine similarity)
	•	requests

How It Works
	1.	Session begins with a quote.
	2.	User completes preliminary intake questions.
	3.	User responses are summarized and compared to the depression dataset.
	4.	The assistant provides supportive, non-diagnostic feedback.

Running the Application

1. Set environment variables

Create a .env or .secrets file:

OPENAI_MODEL=gpt-4
API_GATEWAY_KEY=your_key_here

3. Start the app

python -m assignment_chat.app

The app will run locally via Gradio.

Limitations
	•	The similarity score is not a clinical assessment.
	•	External quote API may fail due to network or SSL issues.
	•	The system does not replace professional mental health services.

Disclaimer

This project is for academic purposes only.
It does not provide medical or psychological diagnosis or treatment.