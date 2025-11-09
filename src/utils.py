__all__ = ["pasta_to_markdown"]


def pasta_to_markdown(pasta: str) -> str:
    if len(pasta) < 80 and "\n" not in pasta:
        return f"`{pasta}`"
    return f"```База\n{pasta}\n```"
