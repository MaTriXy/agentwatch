import os
import sys
from multiprocessing import current_process

from spyllm.core import initialize


def _safe_to_start() -> bool:
    # Only run on original script execution, not in subprocess or interpreter bootstrapping
    return current_process().name == "MainProcess" \
        and not hasattr(sys, '_called_from_spawn') \
        and os.environ.get('SPYLLM_INTERNAL') is None \
        and "PYTEST_VERSION" not in os.environ

if _safe_to_start():
    initialize()