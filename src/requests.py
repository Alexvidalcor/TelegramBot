# Python libraries
import openai

# Custom modules
from main import *
from src.permissions import UsersFirewall
from src.modules.app_support import openaiToken
from src.db import InsertUserMessage, InsertAsistantMessage, GetUserMessagesToReply
from src.stats import StatsNumTokens

# Get OpenAI token
openai.api_key = openaiToken


def FormatCompletionMessages(cur, username, identity, promptUser):

    userLogger.info(f'{username} sent a message')

    results = GetUserMessagesToReply()

    conversationFormatted = [{"role": "system", "content": identity}]
    for row in results:
        conversationFormatted.append({"role": "user", "content": row[2]})
        conversationFormatted.append({"role": row[4], "content": row[5]})
    conversationFormatted.append({"role": "user", "content": promptUser})

    StatsNumTokens(username, conversationFormatted)
    userLogger.info('Jepetobot replied a message')

    return conversationFormatted


def GenerateResponse(username, prompt, identity, temp):
    # Import latest connection object
    from src.db import con, cur

    InsertUserMessage(username, prompt)
    messagesFormatted = FormatCompletionMessages(
        cur, username, identity, prompt)

    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messagesFormatted,
        max_tokens=maxTokensResponse,
        n=1,
        stop=None,
        temperature=float(temp),
    )

    answerProvided = completions["choices"][0]["message"]["content"]

    InsertAsistantMessage(username, answerProvided)

    return answerProvided


@UsersFirewall
async def AiReply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Reply the user message.
    await update.message.reply_text(GenerateResponse(update.message.from_user.username, update.message.text, settings["Identity"], settings["Temperature"]))


@UsersFirewall
async def AiReplyInline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Handle the inline query. This is run when you type: @botusername <query>"""

    query = update.inline_query.query

    if query == "":
        return

    results = [

        InlineQueryResultArticle(
            id="1",
            title="ReplyInline",
            description="Click here to get an answer",
            thumbnail_url="https://raw.githubusercontent.com/Alexvidalcor/jepetobot/master/src/images/Readme-logo2.jpg",
            input_message_content=InputTextMessageContent(query),
        )
    ]

    await update.inline_query.answer(results)
