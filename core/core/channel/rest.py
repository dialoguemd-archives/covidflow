from rasa.core.channels import RestInput


# This is a temporary solution about logging. Here is some context.
# We want to :
#   1) avoid having multi-line logging statement (ie. rasa debug multiline messages,
#      and stacktraces)
#   2) format our logging in json, for complience with datadog.
#
# To do so, we need a hook (when Rasa starts) to setup the logs in the proper format.
# It seems that loading a channel is one of the first thing rasa does when it starts.
#
# Wrapping and adding this channel in the credentials.yml file allows us to configure
# logging early. See __init__.py file of the local package for logging initialization.
class WrappedRestInput(RestInput):
    pass
