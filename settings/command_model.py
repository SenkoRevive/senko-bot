from dataclasses import dataclass


@dataclass
class Comamnd:
    plugin: str
    command: str

    @property
    def path(self) -> str:
        return f"{self.plugin}.{self.command}"