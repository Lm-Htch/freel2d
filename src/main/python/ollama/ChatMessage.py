class ChatMessage:
    def __init__(self, role: str, content: str, images: str = None):
        self.role = role
        self.content = content
        self.images = images or ""

    def __str__(self):
        return f"{self.role}: [ {self.content} ]\nImages: {self.images}"

    def toDict(self):
        if self.images:
            return {"role": self.role, "content": self.content, "images": self.images}
        else:
            return {"role": self.role, "content": self.content}
