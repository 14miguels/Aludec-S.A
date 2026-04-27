

"""Business-rule calculations for SDS Excel export.

These functions should only contain deterministic calculations/rules.
They must not call the LLM and must not extract new information from PDFs.
"""

import re
from typing import Any


def parse_number(value: Any) -> float | None:
    """Parse a number from strings such as '0.87', '1,014', '449 g/l' or '100,000'."""
    if value is None:
        return None

    if isinstance(value, int | float):
        return float(value)

    text = str(value).strip()

    if not text:
        return None

    match = re.search(r"[-+]?\d+(?:[.,]\d+)?", text)

    if not match:
        return None

    number_text = match.group(0).replace(",", ".")

    try:
        return float(number_text)
    except ValueError:
        return None


def format_decimal(value: float | None, digits: int = 3) -> str:
    """Format a decimal using comma as decimal separator for Portuguese Excel output."""
    if value is None:
        return ""

    return f"{value:.{digits}f}".replace(".", ",")


def default_cov_percent(cov_g_l: Any) -> str:
    """Return default VOC percentage.

    For this project, when a VOC value in g/L exists, the expected Excel rule is
    to treat COV % as 100%. This is a business rule, not a value extracted from
    the SDS.
    """
    cov_value = parse_number(cov_g_l)

    if cov_value is None:
        return ""

    return "100,00"


def compute_cov_t(consumption_kg: Any, cov_percent: Any) -> str:
    """Compute VOC quantity in tonnes.

    Formula:
        COV(t) = annual_consumption_kg / 1000 * cov_percent / 100
    """
    consumption = parse_number(consumption_kg)
    percent = parse_number(cov_percent)

    if consumption is None or percent is None:
        return ""

    cov_t = (consumption / 1000) * (percent / 100)

    return format_decimal(cov_t, digits=2)


def compute_max_quantity_t(storage_capacity_l: Any, density_g_cm3: Any) -> str:
    """Compute maximum stored quantity in tonnes.

    Formula:
        quantity(t) = storage_capacity_l * density_kg_l / 1000

    For liquids, density in g/cm³ is numerically equal to kg/L.
    """
    capacity_l = parse_number(storage_capacity_l)
    density = parse_number(density_g_cm3)

    if capacity_l is None or density is None:
        return ""

    quantity_t = (capacity_l * density) / 1000

    return format_decimal(quantity_t, digits=3)