import os

from dotenv import load_dotenv
from groq import Groq
from cerebras.cloud.sdk import Cerebras


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

AI_ROUTER_ENABLED = os.getenv(
    "AI_ROUTER_ENABLED",
    "true"
).lower() == "true"

DEFAULT_AI_MODEL = os.getenv(
    "DEFAULT_AI_MODEL",
    "groq"
).lower()


# --------------------------------------------------
# AI CLIENTS
# --------------------------------------------------

groq_client = None
cerebras_client = None


if GROQ_API_KEY:
    groq_client = Groq(
        api_key=GROQ_API_KEY
    )


if CEREBRAS_API_KEY:
    cerebras_client = Cerebras(
        api_key=CEREBRAS_API_KEY
    )


# --------------------------------------------------
# AI ROUTER
# --------------------------------------------------

def choose_model(question):

    question_lower = question.lower()

    complex_keywords = [
        "compare",
        "comparison",
        "recommend",
        "recommendation",
        "best",
        "which one",
        "difference",
        "better",
        "why",
        "explain",
        "analyze"
    ]

    for keyword in complex_keywords:

        if keyword in question_lower:
            return "cerebras"

    return "groq"


# --------------------------------------------------
# GROQ
# --------------------------------------------------

def ask_groq(prompt):

    if not groq_client:
        raise RuntimeError(
            "Groq API key is not configured."
        )

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ShopMind AI, "
                    "an ecommerce shopping assistant. "
                    "Give accurate, concise and helpful "
                    "answers based only on the provided "
                    "product information."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# --------------------------------------------------
# CEREBRAS
# --------------------------------------------------

def ask_cerebras(prompt):

    if not cerebras_client:
        raise RuntimeError(
            "Cerebras API key is not configured."
        )

    response = cerebras_client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ShopMind AI, "
                    "an ecommerce shopping assistant. "
                    "Help customers compare products "
                    "and make useful recommendations."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# --------------------------------------------------
# MAIN AI FUNCTION
# --------------------------------------------------

def ask_ai(prompt):

    if AI_ROUTER_ENABLED:
        selected_model = choose_model(prompt)
    else:
        selected_model = DEFAULT_AI_MODEL


    # ----------------------------------------------
    # CEREBRAS
    # ----------------------------------------------

    if selected_model == "cerebras":

        try:

            answer = ask_cerebras(prompt)

            return {
                "answer": answer,
                "model": "cerebras",
                "route": "complex"
            }

        except Exception as error:

            if groq_client:

                answer = ask_groq(prompt)

                return {
                    "answer": answer,
                    "model": "groq",
                    "route": "fallback"
                }

            raise error


    # ----------------------------------------------
    # GROQ
    # ----------------------------------------------

    try:

        answer = ask_groq(prompt)

        return {
            "answer": answer,
            "model": "groq",
            "route": "simple"
        }

    except Exception as error:

        if cerebras_client:

            answer = ask_cerebras(prompt)

            return {
                "answer": answer,
                "model": "cerebras",
                "route": "fallback"
            }

        raise error