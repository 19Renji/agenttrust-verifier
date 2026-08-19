"""Policy evaluation logic."""


class Policy:
    """Placeholder policy container."""

    def __init__(self, rules=None):
        self.rules = rules or {}

    def evaluate(self, context):
        """Evaluate policy against the provided context."""
        return self.rules, context
