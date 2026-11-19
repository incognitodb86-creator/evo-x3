"""TEST-ONLY stub detector. Never imported by any run-path script (static test)."""


def make(verdict=None, exc=None):
    def det(path):
        if exc:
            raise exc
        return verdict
    return det
