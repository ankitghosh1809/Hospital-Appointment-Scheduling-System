import sys, os

# backend/ is the single source of truth for the app - import it instead of
# keeping a second copy in sync (see vercel.json's includeFiles for why
# this directory is actually present in the deployed function).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from app import app
