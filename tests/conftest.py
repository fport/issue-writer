import random

import pytest


@pytest.fixture
def rng():
    return random.Random(20260904)


@pytest.fixture(scope="session")
def small_dataset():
    """Kucuk bir veri seti uretir; uretim hattinin tamamini kapsar."""
    import build
    return build.build(target=400, seed=7)
