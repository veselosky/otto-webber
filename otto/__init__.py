"""
Root namespace for Otto Webber.

"""
__version__ = '0.0.1'

# Ensure the env has an otto key for settings
from fabric.api import env
if not env.get("otto"):
    env.otto = {}

