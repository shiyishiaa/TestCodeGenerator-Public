import base64
from pathlib import Path


class SupportedImage(Path):

    @property
    def base64(self) -> str:
        if not self.is_file():
            raise FileNotFoundError(f"File {self.name} not found")
        return base64.b64encode(self.read_bytes()).decode('utf-8')

    def is_supported(self):
        return self.is_file() and self.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp")
