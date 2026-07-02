from bson import ObjectId

from datetime import datetime

from models.conversation_model import (
    ConversationMessage
)


async def load_memory(

    db,

    journey_id: str

):

    conversation = await db.chat_memory.find_one(

        {

            "journey_id": journey_id

        }

    )

    if conversation is None:

        return {

            "messages": [],

            "summary": ""

        }

    return {

        "messages": conversation.get(

            "messages",

            []

        ),

        "summary": conversation.get(

            "summary",

            ""

        )

    }


async def save_user_message(

    db,

    journey_id: str,

    message: str

):

    msg = ConversationMessage(

        role="user",

        content=message

    ).model_dump()

    await db.chat_memory.update_one(

        {

            "journey_id": journey_id

        },

        {

            "$push": {

                "messages": msg

            },

            "$set": {

                "updated_at": datetime.utcnow()

            }

        },

        upsert=True

    )


async def save_assistant_message(

    db,

    journey_id: str,

    message: str,

    intent: dict,

    tools: list

):

    msg = ConversationMessage(

        role="assistant",

        content=message,

        intent=intent,

        tools=tools

    ).model_dump()

    await db.chat_memory.update_one(

        {

            "journey_id": journey_id

        },

        {

            "$push": {

                "messages": msg

            },

            "$set": {

                "updated_at": datetime.utcnow()

            }

        },

        upsert=True

    )


async def get_recent_messages(

    db,

    journey_id: str,

    limit: int = 20

):

    memory = await load_memory(

        db,

        journey_id

    )

    return memory["messages"][-limit:]


async def update_summary(

    db,

    journey_id: str,

    summary: str

):

    await db.chat_memory.update_one(

        {

            "journey_id": journey_id

        },

        {

            "$set": {

                "summary": summary,

                "updated_at": datetime.utcnow()

            }

        }

    )


async def clear_memory(

    db,

    journey_id: str

):

    await db.chat_memory.delete_one(

        {

            "journey_id": journey_id

        }

    )