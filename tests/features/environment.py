import traceback
from unittest.mock import MagicMock

from context.base import CONTEXTS
from data.base import handle_data
from service.mudio import Service

def before_scenario(context, scenario):
    """Run before every step."""
    service = MagicMock()
    service.contexts = {}
    Service.load_contexts(service)
    context.engine = handle_data(memory=True)


def after_scenario(context, scenario):
    """Run after every step."""
    engine = context.engine
    engine.destroy()
    engine.clear_cache()
