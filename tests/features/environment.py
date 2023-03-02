import traceback
from unittest.mock import MagicMock

from context.base import CONTEXTS
from data.base import handle_data
from service.game import Service as GameService
from service.mudio import Service as MudIOService

def before_scenario(context, scenario):
    """Run before every step."""
    context.engine = handle_data(memory=True)
    GameService.restore_delays(MagicMock())
    mudio_service = MagicMock()
    mudio_service.contexts = {}
    MudIOService.load_contexts(mudio_service)


def after_scenario(context, scenario):
    """Run after every step."""
    engine = context.engine
    engine.destroy()
    engine.clear_cache()
