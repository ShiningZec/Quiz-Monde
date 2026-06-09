import json
import os

from .contentBlock import ContentBlock
from .quiz import Quiz


def readBlock(data) -> list[ContentBlock]:
    if data.get("blocks") is None:
        return [ContentBlock(type="text", content=data.get("question", ""))]
    else:
        blocks = []
        for block in data.get("blocks", []):
            blocks.append(
                ContentBlock(
                    type=block.get("type", ""), content=block.get("content", "")
                )
            )
        return blocks


class QuizLoader:
    def __init__(self, dataset_dir: str):
        self.dataset_dir = dataset_dir

    def load_categories(self):
        # 返回 dataset 目录下的子文件夹列表；或 json 子文件
        if not os.path.isdir(self.dataset_dir):
            return []
        return [
            name
            for name in os.listdir(self.dataset_dir)
            if os.path.isdir(os.path.join(self.dataset_dir, name))
            or name.lower().endswith("json")
        ]

    def load_quizzes_from_json(self, filename: str) -> list[Quiz]:
        """
        Format:
            ```json
            {
                "category": "demo",
                "quizzes": [
                    {
                        "id": "1",
                        "type": "single_choice",
                        "content": {
                            "blocks": [
                                {
                                    "type": "text",
                                    "content": "1+1=?"
                                }
                            ]
                        },
                        "options": ["1", "2", "3"],
                        "answer": {"correct": 1}
                    }
                ]
            }
        ```
        """
        quizzes: list[Quiz] = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            cat = data.get("category", "")
            for quiz_raw in data.get("quizzes", []):
                qid = quiz_raw.get("id", "")
                qtype = quiz_raw.get("type", "")
                answer = quiz_raw.get("answer", "")
                blocks = readBlock(quiz_raw.get("content", {}))
                options = quiz_raw.get("options", [])
                quizzes.append(Quiz(qid, qtype, blocks, options, answer, cat))
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
        return quizzes

    def load_quizzes(self, categories: list):
        quizzes: list[Quiz] = []
        for cat in categories:
            cat_dir = os.path.join(self.dataset_dir, cat)
            if not os.path.isdir(cat_dir):
                qs: list[Quiz] = self.load_quizzes_from_json(cat_dir)
                quizzes.extend(qs)
                continue
            # dir: file by file
            for filename in os.listdir(cat_dir):
                if filename.lower().endswith(".json"):
                    path = os.path.join(cat_dir, filename)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        qid = data.get("id", "")
                        qtype = data.get("type", "")
                        answer = data.get("answer", "")
                        blocks = readBlock(data.get("content", {}))
                        options = data.get("options", [])
                        quizzes.append(Quiz(qid, qtype, blocks, options, answer, cat))
                    except Exception as e:
                        print(f"Failed to load {path}: {e}")
        return quizzes


def main():
    loader = QuizLoader("dataset")
    categories = loader.load_categories()
    print("Categories:", categories)
    quizzes = loader.load_quizzes(categories)
    for quiz in quizzes:
        print(quiz)


if __name__ == "__main__":
    main()
