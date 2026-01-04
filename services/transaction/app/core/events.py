import logging
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger("transactions_service.events")


@dataclass(frozen=True)
class DomainEvent:
    name: str
    payload: Dict[str, Any]


class InMemoryEventBus:
    def __init__(self) -> None:
        self._events: List[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self._events.append(event)
        logger.info("event_published", extra={"event_name": event.name, "payload": event.payload})

    def list_events(self) -> List[DomainEvent]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()


event_bus = InMemoryEventBus()


def publish_transaction_created(event: Dict[str, Any]) -> None:
    domain_event = DomainEvent(name="TransactionCreated", payload=event)
    event_bus.publish(domain_event)


def publish_transaction_deleted(event: Dict[str, Any]) -> None:
    domain_event = DomainEvent(name="TransactionDeleted", payload=event)
    event_bus.publish(domain_event)
