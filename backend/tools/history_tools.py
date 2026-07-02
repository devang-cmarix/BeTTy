from bson import ObjectId


async def get_task_history(
    db,
    task_id: str
):

    history = await db.task_history.find(

        {
            "task_id": task_id
        }

    ).to_list(None)

    return history


async def get_replacement_history(
    db,
    journey_id: str
):

    history = await db.task_history.find(

        {

            "journey_id": journey_id

        }

    ).sort(

        "replaced_at",
        -1

    ).to_list(None)

    return history


async def get_total_replacements(
    db,
    journey_id: str
):

    return await db.task_history.count_documents(

        {

            "journey_id": journey_id

        }

    )


async def get_recent_replacements(
    db,
    journey_id: str,
    limit: int = 5
):

    history = await db.task_history.find(

        {

            "journey_id": journey_id

        }

    ).sort(

        "replaced_at",
        -1

    ).limit(limit).to_list(None)

    return history


async def get_most_replaced_tasks(
    db,
    journey_id: str
):

    pipeline = [

        {

            "$match": {

                "journey_id": journey_id

            }

        },

        {

            "$group": {

                "_id": "$task_id",

                "count": {

                    "$sum": 1

                },

                "last_title": {

                    "$last": "$new_title"

                }

            }

        },

        {

            "$sort": {

                "count": -1

            }

        }

    ]

    return await db.task_history.aggregate(
        pipeline
    ).to_list(None)