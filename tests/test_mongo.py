import pytest

from mongo.mongo import VectorView, Vector, generate_embeddings, mongo_insert, init_mongo, search_content


def test_generate_embeddings():
    print(generate_embeddings('hello'))


@pytest.mark.asyncio
async def test_insert():
    await init_mongo()
    num = await Vector.count()
    await mongo_insert(f'Vector {num}!')
    print(await Vector.find().project(VectorView).to_list())


@pytest.mark.asyncio
async def test_find():
    await init_mongo()
    print(await Vector.find().to_list())


@pytest.mark.asyncio
async def test_search():
    await init_mongo()
    results = await search_content('prompt')
    print(results)


@pytest.mark.asyncio
async def test_agg():
    await init_mongo()
    size_aggregate = [{'$sample': {'size': 1}}]
    return print(await Vector.aggregate(size_aggregate).to_list())


@pytest.mark.asyncio
async def test_answers():
    await init_mongo()
    return print(await get_answers('What is the meaning of the life?'))


if __name__ == '__main__':
    pytest.main()
