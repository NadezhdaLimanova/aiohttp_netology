import asyncio
import aiohttp

async def main():
    client = aiohttp.ClientSession()
    #
    response = await client.post(
        "http://127.0.0.1:8080/user",
        json={"name": "user_1", "email": "wer@rty.com", "password": "password1"}
        ,)

    print(response.status)
    print(await response.json())



    with open('token.txt', 'r') as file:
        token = file.read().strip()
    headers = {'Authorization': token}

    #
    # response = await client.patch(
    #     "http://127.0.0.1:8080/user",
    #     json={"name": "user_2", "email": "wer@rty.com", "password": "passhghhh1"}
    #     , headers=headers,)
    #
    # print(response.status)
    # print(await response.json())


    # response = await client.post(
    #     "http://127.0.0.1:8080/login",
    #     json={
    #         "name": "user_1",
    #         "email": "wer@rty.com",
    #         "password": "password1",
    #     },
    # )
    #
    # print(response.status)
    # print(await response.json())


    response = await client.get(
        "http://127.0.0.1:8080/user"
        ,
    headers=headers,
    )

    print(response.status)
    print(await response.json())

    # response = await client.get(
    #     "http://127.0.0.1:8080/users/1"
    #     ,)
    #
    # print(response.status)
    # print(await response.json())
    #
    #
    # response = await client.patch(
    #     "http://127.0.0.1:8080/users/1",
    #     json={"name": "user_2"}
    #     ,)
    #
    # print(response.status)
    # print(await response.json())
    #
    # response = await client.delete(
    #     "http://127.0.0.1:8080/users/1"
    #     ,)
    #
    # print(response.status)
    # print(await response.json())
    #
    # response = await client.get(
    #     "http://127.0.0.1:8080/users/1"
    #     ,)
    #
    # print(response.status)
    # print(await response.json())

    await client.close()


asyncio.run(main())