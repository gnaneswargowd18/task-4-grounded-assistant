from pathlib import Path
import csv
import string
from datetime import datetime


UNSAFE_KEYWORDS = [
    "steal password",
    "steal someone's password",
    "hack someone's account",
    "hack an account",
    "make a bomb",
    "build a bomb",
    "make a weapon",
    "create malware",
]


AI_TOPICS = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "python",
    "natural language processing",
    "retrieval-augmented generation",
    "guardrails",
    "evaluation",
    "tokens",
    "token",
    "embeddings",
    "embedding",
]


def load_document():
    file_path = Path("documents") / "AI_Notes.txt"

    if not file_path.exists():
        print("Error: AI_Notes.txt was not found.")
        return []

    text = file_path.read_text(encoding="utf-8")

    titles = [
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning",
        "Python",
        "Natural Language Processing",
        "Retrieval-Augmented Generation",
        "AI Guardrails",
        "Evaluation",
        "Tokens",
        "Embeddings",
    ]

    sections = []
    current_title = ""
    current_content = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line in titles:
            if current_title:
                sections.append({
                    "title": current_title,
                    "content": " ".join(current_content),
                })

            current_title = line
            current_content = []
        else:
            current_content.append(line)

    if current_title:
        sections.append({
            "title": current_title,
            "content": " ".join(current_content),
        })

    return sections


def check_guardrails(question):
    question_lower = question.lower()

    for phrase in UNSAFE_KEYWORDS:
        if phrase in question_lower:
            return "unsafe"

    if not any(topic in question_lower for topic in AI_TOPICS):
        return "off_topic"

    return "allowed"


def search_document(question, sections):
    question = question.lower()
    question = question.translate(
        str.maketrans("", "", string.punctuation)
    )

    question_words = set(question.split())

    stop_words = {
        "what", "is", "are", "the", "a", "an", "of",
        "in", "to", "and", "how", "does", "do", "explain",
        "tell", "me", "about", "please", "define",
        "can", "you", "for", "use", "used",
    }

    question_words -= stop_words

    best_section = None
    best_score = 0

    for section in sections:
        searchable_text = (
            section["title"] + " " + section["content"]
        ).lower()

        score = sum(
            1 for word in question_words
            if word in searchable_text
        )

        if score > best_score:
            best_score = score
            best_section = section

    if best_score == 0:
        return None

    return best_section


def estimate_tokens(text):
    if not text:
        return 0

    # Rough estimate only; not an actual model tokenizer.
    return max(1, (len(text) + 3) // 4)


def log_usage(question, status, retrieved_text):
    log_file = Path("usage_log.csv")
    file_exists = log_file.exists()

    question_tokens = estimate_tokens(question)
    retrieved_tokens = estimate_tokens(retrieved_text)

    total_estimated_tokens = question_tokens + retrieved_tokens

    with log_file.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "question",
                "status",
                "question_estimated_tokens",
                "retrieved_estimated_tokens",
                "total_estimated_tokens",
                "external_api_cost_inr",
            ])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            question,
            status,
            question_tokens,
            retrieved_tokens,
            total_estimated_tokens,
            0,
        ])

    return total_estimated_tokens


def main():
    print("================================")
    print("     GROUNDED AI ASSISTANT")
    print("================================")

    sections = load_document()

    if not sections:
        print("No knowledge sections were loaded.")
        return

    print("Knowledge document loaded successfully.")
    print("Loaded sections:", len(sections))
    print("Guardrails enabled.")
    print("Estimated token logging enabled.")
    print("Type exit to stop.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Assistant: Goodbye!")
            break

        if not question:
            print("Assistant: Please enter a question.")
            continue

        guardrail_result = check_guardrails(question)
        retrieved_text = ""
        status = guardrail_result

        if guardrail_result == "unsafe":
            print(
                "Assistant: I cannot help with unsafe or harmful requests."
            )

        elif guardrail_result == "off_topic":
            print(
                "Assistant: I can answer questions about AI "
                "and the topics in my knowledge document."
            )

        else:
            result = search_document(question, sections)

            if result:
                retrieved_text = (
                    result["title"] + " " + result["content"]
                )
                status = "answered"
                print("Assistant:", result["title"])
                print(result["content"])
            else:
                status = "not_found"
                print(
                    "Assistant: I could not find a relevant answer "
                    "in my knowledge document."
                )

        total_tokens = log_usage(
            question,
            status,
            retrieved_text,
        )

        print("Estimated tokens for this interaction:", total_tokens)
        print("External API cost: Rs. 0 (no external API used)")
        print()


if __name__ == "__main__":
    main()