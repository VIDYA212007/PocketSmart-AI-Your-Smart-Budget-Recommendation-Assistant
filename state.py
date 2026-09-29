# Shared application state
# Keyed by username so each user only ever sees their own recommendation history.
from collections import defaultdict

recommendation_history = defaultdict(list)
