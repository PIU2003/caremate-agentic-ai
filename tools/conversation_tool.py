from database.database import (
    save_conversation,
    get_conversations,
)


class ConversationTool:

    def save(self, user, assistant):

        save_conversation(user, assistant)

    def get_all(self):

        return get_conversations()