from database.database import (
    save_summary,
    get_summaries,
)


class SummaryTool:

    def save(self, input_text, summary):

        save_summary(input_text, summary)

    def get_all(self):

        return get_summaries()