import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = "xoxb-8224814752917-8269744735600-4vxrRPIegM9KTHpL5vMlVrfm"
CHANNEL_ID = "C086PGK0DH9"

client = WebClient(token=SLACK_BOT_TOKEN)

try:
    response = client.chat_postMessage(
        channel=CHANNEL_ID,
        text="テストメッセージ: ボットトークンが正しく動作しています。"
    )
    print("メッセージを送信しました。")
except SlackApiError as e:
    print(f"Slack API エラー: {e.response['error']}")
