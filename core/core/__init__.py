# Running this in try/except to avoid error while training rasa models (structlog not found)
try:
    from .setup_structlog import setup_structlog

    setup_structlog()
except:
    pass
