import logging
from typing import Any, Dict

logger = logging.getLogger("transactions_service.events")


def publish_transaction_created(event: Dict[str, Any]) -> None:
    """
    Stub publisher for TransactionCreated events.
    For ora logga l'evento; in futuro può inviare a Kafka/Rabbit/etc.
    """
    logger.info("TransactionCreated event", extra={"event": event})
