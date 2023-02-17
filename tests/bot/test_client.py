import pytest

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse
from todolist.settings import TEST_BOT_TOKEN


@pytest.mark.django_db
class TestBotClient:

    def test_get_url(self, tg_client):
        assert tg_client.get_url('Method') == f'https://api.telegram.org/bot{TEST_BOT_TOKEN}/Method'

    def test_get_updates(self, tg_client):
        assert tg_client.get_updates(offset=0, timeout=60) == GetUpdatesResponse(ok=True, result=[])

    def test_send_message(self, tg_client, bot_id):
        assert tg_client.send_message(chat_id=433806299, text='text') == SendMessageResponse
