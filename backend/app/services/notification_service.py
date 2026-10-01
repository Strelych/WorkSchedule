from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NotificationMessage:
    user_id: str
    text: str


class NotificationService:
    def __init__(self):
        self.messages: list[NotificationMessage] = []

    def send(self, user_id: str, text: str) -> NotificationMessage:
        message = NotificationMessage(user_id=user_id, text=text)
        self.messages.append(message)
        return message

    def broadcast(self, recipients: list[str], text: str) -> list[NotificationMessage]:
        return [self.send(user_id, text) for user_id in recipients]
