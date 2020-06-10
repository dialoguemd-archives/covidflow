from rasa.core.channels.channel import RestInput

# Running this in try/except to avoid error while training rasa models (structlog not found)
try:
    from .setup_structlog import setup_structlog

    setup_structlog()
except:
    pass

# This is a temporary solution.
# We need a hook to setup the logs in the proper format, and loading a channel is one of the first thing
# rasa does when it starts. So using this wrapped RestInput allows us to configure logging early.
class WrappedRestInput(RestInput):
    pass
