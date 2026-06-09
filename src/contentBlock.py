from dataclasses import dataclass


@dataclass
class ContentBlock:
    type: str
    content: str

    def to_dict(self):
        return {"type": self.type, "content": self.content}


if __name__ == "__main__":
    # Example usage
    block = ContentBlock(type="text", content="This is a sample content block.")
    print(block)
