import pytest


@pytest.mark.asyncio
async def test_search_detailed(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/genre')

    assert response.status == 200
