from abc import ABC, abstractmethod

# ==========================================
# Task 1: Advanced OOP Concepts (Managers & Singletons)
# - Abstract Base Classes, Strategy Pattern, Singleton
# ==========================================

class AbstractNotifier(ABC):
    """Abstraction: Abstract base class acting as an Interface/Strategy for notification services."""
    def __init__(self, service_name: str):
        self._service_name = service_name  # Encapsulation

    @property
    def service_name(self):
        return self._service_name

    @abstractmethod
    def send_notification(self, user, message: str) -> str:
        """Polymorphism: Overridden by specific notification strategies."""
        pass


class EmailNotifier(AbstractNotifier):
    """Inheritance: Concrete class realizing the Notifier abstraction."""
    def __init__(self):
        super().__init__("EmailService")

    def send_notification(self, user, message: str) -> str:
        """Polymorphism: Concrete implementation."""
        email = getattr(user, 'contact_info', 'Unknown Email')
        return f"[{self.service_name}] 📧 Email sent to {email}: {message}"


class SMSNotifier(AbstractNotifier):
    """Inheritance: Another Concrete class realizing the Notifier strategy."""
    def __init__(self):
        super().__init__("SMSService")

    def send_notification(self, user, message: str) -> str:
        """Polymorphism: Different concrete behavior."""
        phone = getattr(user, 'contact_info', 'Unknown Phone')
        return f"[{self.service_name}] 📱 SMS sent to {phone}: {message}"


class NotificationManager:
    """Singleton Manager to handle composed lists of notification strategies."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Singleton setup: Ensure only one NotificationManager is ever created
            cls._instance = super(NotificationManager, cls).__new__(cls)
            cls._instance._notifiers = []
        return cls._instance

    def add_notifier(self, notifier: AbstractNotifier):
        """Strategy & Composition pattern: Add various notifiers."""
        self._notifiers.append(notifier)
        return self

    def notify_all(self, user, message: str) -> list:
        # Utilize Polymorphism to send regardless of actual Notifier type
        results = []
        for notifier in self._notifiers:
            results.append(notifier.send_notification(user, message))
        return results
