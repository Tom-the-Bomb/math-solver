from ..app import app

__all__ = ('test_post_solve',)

async def test_post_solve() -> None:
    equation = '5 + 4'

    client = app.test_client()
    response = await client.post("/solve", json={'equation': equation})
    data = await response.get_json()
    print(f'\n{data}')