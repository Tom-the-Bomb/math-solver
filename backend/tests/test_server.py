from ..app import app

__all__ = ('test_solve',)

async def test_solve() -> None:
    equation = '16x^2 - 64'

    client = app.test_client()
    response = await client.post("/solve", json={'equation': equation})
    data = await response.get_json()
    print(f'\n{data}')