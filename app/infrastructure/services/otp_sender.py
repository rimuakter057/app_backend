from abc import ABC, abstractmethod


class OtpSender(ABC):
    @abstractmethod
    async def send(self, email: str, code: str) -> None: ...


class ConsoleOtpSender(OtpSender):
    """Dev-only sender that logs the OTP. Swap for a real email/SMS provider in production."""

    async def send(self, email: str, code: str) -> None:
        print(f"[OTP] {email} -> {code}")
