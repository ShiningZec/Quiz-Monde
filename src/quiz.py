from dataclasses import dataclass


@dataclass
class Quiz:
    id: str
    type: str
    content_blocks: list
    options: list
    answer: str
    category: str

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "content": {"blocks": [block.to_dict() for block in self.content_blocks]},
            "answer": self.answer,
            "category": self.category
        }


@dataclass
class QuizRequest:
    count: int
    category: str
    topic: str
    difficulty: str



if __name__ == "__main__":
    # Example usage
    quiz = Quiz(
        id="1",
        type="single_choice",
        content_blocks=[{"type": "text", "content": "What is the capital of France?"}],
        options=["A. Paris", "B. London", "C. Berlin", "D. Madrid"],
        answer="A. Paris",
        category="Geography"
    )
    print(quiz)