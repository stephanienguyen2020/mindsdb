import os
import asyncio
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from mongo.mongo import mongo_insert, init_mongo

import dotenv
dotenv.load_dotenv()

from langchain.prompts import ChatPromptTemplate

# Set the OpenAI API key
os.environ['OPENAI_API_KEY'] = "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"

# Function to summarize text and insert into MongoDB
async def summarize_and_insert(text: str):
    print("Starting summarize_and_insert function")  # Debug print
    summarize_template_txt = """Summarize the following text into a concise piece of text that contains the most 
        important pieces of information:
        ```{text_chunk}```
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    summarize_prompt = ChatPromptTemplate.from_template(summarize_template_txt)
    chain = LLMChain(llm=llm, prompt=summarize_prompt)
    
    print("Running the summarization chain")  # Debug print
    summary = chain.run(text_chunk=text, n_words=100)
    
    print("Summary:", summary)  # Debug print
    
    # Insert into MongoDB
    print("Inserting summary into MongoDB")  # Debug print
    await init_mongo()
    await mongo_insert(summary)

# Main function to execute the summarize and insert function

async def answer_to_question(question : str, text: str):
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
        """
    
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    summarize_prompt = ChatPromptTemplate.from_template(txt)
    chain = LLMChain(llm=llm, prompt=summarize_prompt)
    
    print("Running the summarization chain")  # Debug print
    summary = chain.run(Question = question, Text = text, n_words=100)
    
    print("answer:", summary)  # Debug print
    
    # # Insert into MongoDB
    # print("Inserting summary into MongoDB")  # Debug print
    # await init_mongo()
    # await mongo_insert(summary)
    
async def main():
    large_text = """
    ""Let’s goo \nOkay gotcha \nI think it will be easy to focus on Q&amp;A instead of more open ended  chats\nOkay sounds good then. \nI think customer support has a larger overlap with other possibilities\nUnless you think differently\nLet's focus on customer support first\nWhich would be better\nIs it for customer support or sales rep?\nThe project is building a chatbot for customer support\nHey what’s the project topic ?\n<@U075QCML64F> has joined the channel\n<@U076TKJDJ1E>\nHEy\n<@U076TKJDJ1E> has joined the channel\n<@U0767ANGF36> has joined the channel\nwait, what is the purpose of this new channel?\n<@U075Y6Y6SMU> has joined the channel\n<@U0761TL163F> has joined the channel\nHEy\nHey Deeps\n""
    """
    print("Starting main function")  # Debug print
    # await summarize_and_insert(large_text)
    await answer_to_question("What is the major topic they are discussing on?", "Here is relevant knowledge. use it to best answer the question: The text discusses focusing on Q&A for a chatbot project for customer support. Participants join a channel to discuss the project topic.")

if __name__ == "__main__":
    print("Running the main function")  # Debug print
    asyncio.run(main())
