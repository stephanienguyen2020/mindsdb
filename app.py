import os
import asyncio
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from mongo.mongo import mongo_insert, init_mongo, get_answers
from flask_cors import CORS
import dotenv
dotenv.load_dotenv()

from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError



# Set the OpenAI API key
os.environ['OPENAI_API_KEY'] = ""

app = Flask(__name__)
CORS(app)

# Function to summarize text
async def summarize_text(text: str):
    summarize_template_txt = """Summarize the following text into a concise piece of text that contains the most 
        important pieces of information:
        ```{text_chunk}```
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    summarize_prompt = PromptTemplate.from_template(summarize_template_txt)
    chain = LLMChain(llm=llm, prompt=summarize_prompt)
    summary = chain.run(text_chunk=text, n_words=100)
    await init_mongo()
    await mongo_insert(summary)
    return summary

# Function to answer a question based on text
async def answer_question(question: str):
    print("does it even come here???????")
    answer_from_vectorDB = await get_answers(question=question)
    print(answer_from_vectorDB)
    txt = """You are Answer Bot, an AI designed to provide accurate and concise answers to user questions. You will be given a question along with a text passage from which you need to extract the most appropriate and relevant answer. Your responses should be clear, brief, and directly address the user's query.

        ----
        Example:

        User's Question:
        What is the capital of France?

        Text Passage:
        France, a country in Western Europe, is known for its cuisine, art, and fashion. The Eiffel Tower is one of its most famous landmarks, located in its capital city. Paris, the capital, is a major European city and a global center for art, fashion, and culture.

        Answer Bot's Response:
        The capital of France is Paris.
        ----

        Question:  ```{Question}```

        Text Passage : ```{Text}```

        If the answer to the user’s question is not available in the database, inform them that you don’t have the answer. Do not generate or provide information that is not factual or verified. Then, based on the context of their question, guide them to the appropriate team that might be able to assist. For instance, if they inquire about payroll, direct them to the HR department. If they ask about finding a place to nap at MindsDB, direct them to the Admin team.
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    summarize_prompt = PromptTemplate.from_template(txt)
    chain = LLMChain(llm=llm, prompt=summarize_prompt)
    answer = chain.run(Question=question, Text=answer_from_vectorDB, n_words=100)
    return answer

async def get_conversations():
    channel_id = "C0761TU0VNZ"
    slack_token = ""

    if not channel_id:
        return {"error": "channel_id parameter is required"}, 400
    if not slack_token:
        return {"error": "token parameter is required"}, 400

    try:
        client = WebClient(token=slack_token)

        # Fetch conversations from the specified channel
        try:
            history_response = client.conversations_history(
                channel=channel_id,
                limit=100  # Increase limit to fetch more messages
            )
            messages = history_response['messages']
            thread_messages = []

            # Check for threads
            for message in messages:
                if 'thread_ts' in message:
                    # Fetch thread messages
                    thread_response = client.conversations_replies(
                        channel=channel_id,
                        ts=message['thread_ts']
                    )
                    thread_messages.extend(thread_response['messages'])

            # Combine main messages and thread messages
            all_messages = messages + thread_messages

        except SlackApiError as e:
            print(f"Error fetching conversation history: {e.response['error']}")
            return {"error": e.response['error']}, 500

        return all_messages

    except SlackApiError as e:
        return {"error": e.response['error']}, 500

def messages_to_paragraph(messages):
    paragraph = ""
    for message in reversed(messages):  # Iterate over messages in reverse order
        if 'text' in message:
            paragraph += message['text'] + "\n"
    return paragraph

@app.route("/conversations", methods=["POST"])
def conversations_route():
    messages = asyncio.run(get_conversations())
    paragraph = messages_to_paragraph(messages)
    return jsonify(paragraph)

# API endpoints
@app.route("/summarize", methods=["POST"])
def get_summary():
    data = request.get_json()
    summary = asyncio.run(summarize_text(data['text']))
    return jsonify({"summary": summary})

@app.route("/answer", methods=["POST"])
def get_answer():
    data = request.get_json()
    answer = asyncio.run(answer_question(data['question']))
    print("answerrrrrr", answer)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

    # uvicorn.run("main:app", host="0.0.0.0", port=8080)
