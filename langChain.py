from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader


import os
os.environ['OPENAI_API_KEY'] = ''

import dotenv
dotenv.load_dotenv()


from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
summarize_template_txt = """Summarize the following text into a concise piece of text that contains the most 
    important pieces of information:
    ```{text_chunk}```
"""
large_text = """
""Let’s goo \nOkay gotcha \nI think it will be easy to focus on Q&amp;A instead of more open ended  chats\nOkay sounds good then. \nI think customer support has a larger overlap with other possibilities\nUnless you think differently\nLet's focus on customer support first\nWhich would be better\nIs it for customer support or sales rep?\nThe project is building a chatbot for customer support\nHey what’s the project topic ?\n<@U075QCML64F> has joined the channel\n<@U076TKJDJ1E>\nHEy\n<@U076TKJDJ1E> has joined the channel\n<@U0767ANGF36> has joined the channel\nwait, what is the purpose of this new channel?\n<@U075Y6Y6SMU> has joined the channel\n<@U0761TL163F> has joined the channel\nHEy\nHey Deeps\n""
"""
llm = ChatOpenAI(model="gpt-3.5-turbo")
summarize_prompt = ChatPromptTemplate.from_template(summarize_template_txt)
chain = LLMChain(llm=llm, prompt=summarize_prompt)
print(chain.run(text_chunk=large_text, n_words=100))