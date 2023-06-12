import json

import pytest

from ..app import app

__all__ = ('test_post_solve',)

@pytest.mark.skip(reason='helper function')
async def _request(**data) -> None:
    client = app.test_client()
    response = await client.post('/solve', **data)

    data = await response.get_json()
    data = json.dumps(data, indent=4, ensure_ascii=False)
    print(f'\n[{response.status}]\n\n{data}')

async def test_post_solve() -> None:
    await _request(
        json={
            'equation': '2P(x) + 14x - 2c',
            'functions': ['P(x) = x^2'],
            'constants': {'c': 60.0},
        }
    )
    await _request(
        json={
            'equation': 'a + 2 - b',
            'constants': {'a': 0.1, 'b': 0.2},
        }
    )

async def test_post_graph() -> None:
    client = app.test_client()
    response = await client.post('/graph', json={
        'equation': 'x',
    })

    assert response.status_code == 200
    assert isinstance(await response.get_data(), bytes)