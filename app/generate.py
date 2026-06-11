import os
from mistralai import Mistral

MODEL_NAME = "mistral-small-latest"


def build_context(results):
    contexts = []

    for hit in results:
        text = hit.payload.get("text", "")
        source = hit.payload.get("source", "Inconnue")

        contexts.append(
            f"[SOURCE: {source}]\n{text}"
        )

    return "\n\n".join(contexts)


def build_prompt(question: str, context: str):
    return f"""
Tu es un assistant documentaire.

Règles :
- Réponds uniquement à partir du contexte fourni.
- Réponds en français.
- N'invente jamais d'information.
- Si l'information n'est pas présente dans le contexte, réponds exactement :
  "Information non trouvée dans la documentation."
- Cite les sources utilisées.

CONTEXTE :
{context}

QUESTION :
{question}
"""


def generate(question: str, results):

    if not results:
        return "Information non trouvée dans la documentation."

    context = build_context(results)
    prompt = build_prompt(question, context)

    client = Mistral(
        api_key=os.getenv("MISTRAL_API_KEY")
    )

    response = client.chat.complete(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content