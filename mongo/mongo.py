import asyncio
from typing import List

import together
from beanie import Document
from beanie import init_beanie
from flask import request, jsonify
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from pymongo import MongoClient
from quart import Quart

TOGETHER_API_KEY = '62584312b992b79e3e76c031ff115c6a10e72ab9d222a06266b7c2c55a6961e6'
MONGODB_URI = "mongodb+srv://hackers:aicampers@hackathon.zquobpp.mongodb.net/?retryWrites=true&w=majority&appName=hackathon"
mongodb_client = MongoClient(MONGODB_URI)


async def mongo_insert(content):
    embeddings = generate_embeddings([content])[0]
    vector = Vector(content=content, content_embeddings=embeddings)
    await vector.insert()


app = Quart(__name__)


@app.before_request
def initialize():
    if not hasattr(app, 'db_initialized'):
        asyncio.run(init_mongo())
        app.db_initialized = True


@app.route('/search', methods=['GET'])
async def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    results = await search_content(query)
    return jsonify({'results': results})


async def init_mongo():
    client = AsyncIOMotorClient(MONGODB_URI)

    db = client.Hackathon_DB

    await init_beanie(database=db, document_models=[Vector])


def generate_embeddings(input_texts: List[str]) -> List[List[float]]:
    """Generate embeddings from Together python library.

    Args:
        input_texts: a list of string input texts.
        model_api_string: str. An API string for a specific embedding model of your choice.

    Returns:
        embeddings_list: a list of embeddings. Each element corresponds to the each input text.
    """

    embedding_model_string = 'togethercomputer/m2-bert-80M-8k-retrieval'
    together_client = together.Together(api_key=TOGETHER_API_KEY)
    outputs = together_client.embeddings.create(
        input=input_texts,
        model=embedding_model_string,
    )
    return [x.embedding + x.embedding for x in outputs.data]


async def get_answers(question):
    results = await search_content(question)
    contents = [result["content"] for result in results]
    # todo filter "!" to remove practice entries
    block = '\n\n'.join(contents)
    return f"""Here is relevant knowledge. use it to best answer the question:\n\n{block}"""


async def search_content(content):
    await init_mongo()
    embeddings = generate_embeddings([content])[0]
    query = VectorSearchQuery(queryVector=embeddings)
    agg = [
        {
            '$vectorSearch': query.model_dump(),
        },
        {
            '$project': {
                '_id': 0,
                'content': 1,
                'score': {
                    '$meta': 'vectorSearchScore',
                },
            },
        }
    ]
    return await Vector.aggregate(agg).to_list()


class VectorView(BaseModel):
    content: str


class Vector(Document):
    content: str
    content_embeddings: List[float]

    class Settings:
        name = "Prompts"


class VectorSearchQuery(BaseModel):
    index: str = Field(default="vector_index")
    path: str = Field(default="content_embeddings")
    # filter: Optional[dict] = {}
    queryVector: List[float]
    numCandidates: int = Field(default=200)
    limit: int = Field(default=10)
