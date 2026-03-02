"""Value Objects for the Accounting domain."""

from __future__ import annotations
import re
from decimal import Decimal, InvalidOperation
from typing import Any, TYPE_CHECKING, Union, Callable
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from stdnum.exceptions import ValidationError as StdnumValidationError
import stdnum.eu.vat
import stdnum.gb.vat
import stdnum.us.ein
import stdnum.au.abn


_TAX_ID_VALIDATORS: list[Callable[[str], str]] = [
    stdnum.eu.vat.validate,
    stdnum.gb.vat.validate,
    stdnum.us.ein.validate,
    stdnum.au.abn.validate,
]


class Money:
    """Money Value Object avoiding primitive obsession with floats.

    Internally uses decimal.Decimal to avoid rounding errors.
    """

    def __init__(
        self, amount: Decimal | str | float | int, currency: str = "USD"
    ) -> None:
        if isinstance(amount, (str, float, int)):
            self._amount = self._parse_amount(amount)
        else:
            self._amount = amount
        self._currency = currency.upper()

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> str:
        return self._currency

    def _parse_amount(self, value: str | int | float) -> Decimal:
        """Parse various input formats including regional settings."""
        if isinstance(value, (int, float)):
            return Decimal(str(value))

        if not isinstance(value, str):
            raise ValueError(f"Cannot parse {type(value)} as Money")

        # Clean string from whitespace
        clean_val = value.strip()

        # Rule-based regional parsing:
        # If both '.' and ',' exist, we assume the last one is the decimal separator.
        # Example: 1.234,56 -> 1234.56
        # Example: 1,234.56 -> 1234.56
        if "," in clean_val and "." in clean_val:
            comma_idx = clean_val.rfind(",")
            point_idx = clean_val.rfind(".")
            if comma_idx > point_idx:
                # Comma is decimal separator: 1.234,56
                clean_val = clean_val.replace(".", "").replace(",", ".")
            else:
                # Point is decimal separator: 1,234.56
                clean_val = clean_val.replace(",", "")
        elif "," in clean_val:
            # Only comma exists. Is it a decimal or thousand separator?
            # If there's only one comma and it's followed by exactly 2 or 3 digits
            # it's ambiguous. We'll treat it as a decimal separator for now
            # as is common in many regions.
            clean_val = clean_val.replace(",", ".")

        try:
            return Decimal(clean_val)
        except InvalidOperation:
            raise ValueError(f"Invalid format for Money: {value}")

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency='{self.currency}')"

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def __float__(self) -> float:
        return float(self.amount)

    def __bool__(self) -> bool:
        return bool(self.amount)

    # Comparison
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Money):
            return self.amount == other.amount and self.currency == other.currency
        if isinstance(other, (Decimal, float, int)):
            return self.amount == Decimal(str(other))
        return False

    def __lt__(self, other: "Money" | Decimal | float | int) -> bool:
        if not isinstance(other, Money):
            other = Money(other, self.currency)
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )
        return self.amount < other.amount

    def __le__(self, other: "Money" | Decimal | float | int) -> bool:
        if not isinstance(other, Money):
            other = Money(other, self.currency)
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )
        return self.amount <= other.amount

    def __gt__(self, other: "Money" | Decimal | float | int) -> bool:
        if not isinstance(other, Money):
            other = Money(other, self.currency)
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )
        return self.amount > other.amount

    def __ge__(self, other: "Money" | Decimal | float | int) -> bool:
        if not isinstance(other, Money):
            other = Money(other, self.currency)
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )
        return self.amount >= other.amount

    def __format__(self, format_spec: str) -> str:
        return self.amount.__format__(format_spec)

    # Arithmetic
    def __add__(self, other: Money | Decimal | float | int) -> Money:
        if not isinstance(other, Money):
            other = Money(other, self.currency)
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money | Decimal | float | int) -> Money:
        if not isinstance(other, Money):
            other = Money(other, self.currency)
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot subtract different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | Decimal | float) -> Money:
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __rmul__(self, factor: int | Decimal | float) -> Money:
        return self.__mul__(factor)

    # Pydantic Integration
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                when_used="always",
            ),
        )

    @classmethod
    def _serialize(cls, instance: "Money") -> str:
        return str(instance.amount)

    @classmethod
    def _validate(cls, value: Any) -> "Money":
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except (ValueError, InvalidOperation) as e:
            raise ValueError(str(e)) from e

    if TYPE_CHECKING:
        Input = Union["Money", str, Decimal, float, int]


class TaxId:
    """Tax Identification Number (e.g., EIN, VAT, TIC, ABN).

    Provides universal validation via python-stdnum and fails fast
    if the format is invalid. Avoids primitive obsession.
    """

    def __init__(self, value: str | "TaxId") -> None:
        if isinstance(value, TaxId):
            self._value = value.value
            return

        if not isinstance(value, str):
            raise ValueError(f"Cannot parse {type(value)} as TaxId")

        clean_val = value.strip().upper()
        if not clean_val:
            raise ValueError("TaxId cannot be empty")

        self._value = self._validate_and_normalize(clean_val)

    def _validate_and_normalize(self, value: str) -> str:
        """Try each known validator in order; fall back to a generic regex."""
        for validate in _TAX_ID_VALIDATORS:
            try:
                return validate(value)
            except StdnumValidationError:
                continue

        # Fallback: strict alphanumeric structural check for unknown formats
        if not re.match(r"^[A-Z0-9\- \.]{5,30}$", value):
            raise ValueError(f"Invalid Tax ID format: {value}")

        return value

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"TaxId('{self._value}')"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TaxId):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                when_used="always",
            ),
        )

    @classmethod
    def _validate(cls, value: Any) -> "TaxId":
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError as e:
            raise ValueError(str(e)) from e

    @classmethod
    def _serialize(cls, instance: "TaxId") -> str:
        return instance.value

    if TYPE_CHECKING:
        Input = Union["TaxId", str]


if not TYPE_CHECKING:
    Money.Input = Union[Money, str, Decimal, float, int]
    TaxId.Input = Union[TaxId, str]
