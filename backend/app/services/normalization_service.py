"""Value, unit, currency, and temporal normalization service."""
import re
from typing import Optional, Tuple
from dateutil import parser as date_parser
from app.schemas.normalization import NormalizedValue, NormalizedTimePeriod
from app.core.logging import logger


class NormalizationService:
    """
    Standardizes numeric scales (k, M, B, lakh, crore, %), currencies, units, and dates
    while strictly preserving the raw extracted representation.
    """

    # Currency mappings
    CURRENCY_SYMBOLS = {
        "$": "USD",
        "USD": "USD",
        "usd": "USD",
        "US$": "USD",
        "₹": "INR",
        "Rs": "INR",
        "Rs.": "INR",
        "INR": "INR",
        "inr": "INR",
        "€": "EUR",
        "EUR": "EUR",
        "eur": "EUR",
        "£": "GBP",
        "GBP": "GBP",
        "gbp": "GBP",
        "¥": "JPY",
        "JPY": "JPY",
    }

    # Scale multipliers
    SCALES = [
        (re.compile(r"(?:\b|(?<=\d))(trillions?|tn|t)\b", re.IGNORECASE), 1e12, "trillion"),
        (re.compile(r"(?:\b|(?<=\d))(billions?|bn|b)\b", re.IGNORECASE), 1e9, "billion"),
        (re.compile(r"(?:\b|(?<=\d))(crores?|cr|crs)\b", re.IGNORECASE), 1e7, "crore"),
        (re.compile(r"(?:\b|(?<=\d))(millions?|mn|m)\b", re.IGNORECASE), 1e6, "million"),
        (re.compile(r"(?:\b|(?<=\d))(lakhs?|lacs?|lac|l)\b", re.IGNORECASE), 1e5, "lakh"),
        (re.compile(r"(?:\b|(?<=\d))(thousands?|k)\b", re.IGNORECASE), 1e3, "thousand"),
    ]

    def normalize_value(self, raw_value_str: Optional[str]) -> NormalizedValue:
        """
        Parses raw values like '₹8,142 Cr', '$383.29 billion', '15.4%', '(500)', '(₹25 Lakh)'
        into canonical numeric values, scale multipliers, units, and formatted strings,
        without performing currency conversion.
        """
        if not raw_value_str or not raw_value_str.strip():
            return NormalizedValue(raw=raw_value_str or "")

        raw = raw_value_str.strip()
        is_estimated = bool(re.search(r"\b(approx|approx\.|approximately|estimated|est\.|around|about|~)\b", raw, re.IGNORECASE))

        # Check for negative values: parenthetical e.g. (500), ($50M), or leading minus sign
        is_negative = False
        clean_raw = raw
        if re.match(r"^\s*\((.*)\)\s*$", raw):
            is_negative = True
            clean_raw = re.sub(r"^\s*\((.*)\)\s*$", r"\1", raw).strip()
        elif re.match(r"^\s*[-−–]\s*", raw):
            is_negative = True
            clean_raw = re.sub(r"^\s*[-−–]\s*", "", raw).strip()

        # 1. Detect Currency
        currency = None
        for sym, curr_code in self.CURRENCY_SYMBOLS.items():
            if sym in clean_raw or re.search(rf"\b{re.escape(sym)}\b", clean_raw, re.IGNORECASE):
                currency = curr_code
                break

        # 2. Detect Unit / Percent
        unit = currency
        is_percent = bool(re.search(r"(%|\bpercent\b|\bpercentage\b)", clean_raw, re.IGNORECASE))
        if is_percent:
            unit = "%"
            currency = None

        # 3. Detect Scale Multiplier
        multiplier = 1.0
        detected_scale = "absolute"
        for pattern, mult_val, scale_name in self.SCALES:
            if pattern.search(clean_raw):
                multiplier = mult_val
                detected_scale = scale_name
                break

        if is_percent:
            detected_scale = "percent"

        # 4. Extract Numbers
        num_clean = clean_raw
        if currency:
            for s in ["$", "₹", "€", "£", "¥", "Rs.", "Rs", "USD", "INR", "EUR", "GBP", "JPY", "US$"]:
                num_clean = num_clean.replace(s, " ")
        if is_percent:
            num_clean = num_clean.replace("%", " ")

        # Match numbers with commas and decimals
        match = re.search(r"[-+]?\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?", num_clean)
        numeric_value = None
        formatted_str = None

        if match:
            num_str = match.group(0).replace(" ", "").replace(",", "")
            try:
                base_float = float(num_str)
                if is_negative and base_float > 0:
                    base_float = -base_float
                numeric_value = base_float * multiplier

                # Format human readable canonical string
                formatted_str = self._format_normalized_string(numeric_value, currency, unit, is_percent, detected_scale, base_float)
            except ValueError:
                logger.warning(f"Could not parse numeric float from: {num_str}")

        return NormalizedValue(
            raw=raw,
            numeric_value=numeric_value,
            formatted_value=formatted_str,
            unit=unit,
            currency=currency,
            scale=detected_scale,
            is_estimated=is_estimated,
            is_negative=is_negative
        )

    def _format_normalized_string(
        self,
        numeric_value: float,
        currency: Optional[str],
        unit: Optional[str],
        is_percent: bool,
        scale: str,
        base_float: float
    ) -> str:
        abs_val = abs(numeric_value)
        sign = "-" if numeric_value < 0 else ""

        if is_percent:
            return f"{sign}{abs(base_float):.2f}%" if base_float % 1 != 0 else f"{sign}{int(abs(base_float))}%"

        if currency == "INR":
            if abs_val >= 1e9:
                return f"{sign}₹{abs_val / 1e9:.2f} billion"
            elif abs_val >= 1e7:
                return f"{sign}₹{abs_val / 1e7:.2f} Cr"
            elif abs_val >= 1e5:
                return f"{sign}₹{abs_val / 1e5:.2f} Lakh"
            else:
                return f"{sign}₹{abs_val:,.2f}"

        if currency == "USD":
            if abs_val >= 1e9:
                return f"{sign}${abs_val / 1e9:.2f} billion"
            elif abs_val >= 1e6:
                return f"{sign}${abs_val / 1e6:.2f} million"
            elif abs_val >= 1e3:
                return f"{sign}${abs_val / 1e3:.2f} thousand"
            else:
                return f"{sign}${abs_val:,.2f}"

        if currency == "EUR":
            if abs_val >= 1e9:
                return f"{sign}€{abs_val / 1e9:.2f} billion"
            elif abs_val >= 1e6:
                return f"{sign}€{abs_val / 1e6:.2f} million"
            else:
                return f"{sign}€{abs_val:,.2f}"

        if scale in ["million", "billion", "thousand", "crore", "lakh"]:
            if base_float.is_integer():
                return f"{sign}{int(abs(base_float))} {scale}"
            return f"{sign}{abs(base_float):.2f} {scale}"

        if numeric_value.is_integer():
            formatted = f"{sign}{int(abs_val):,}"
        else:
            formatted = f"{sign}{abs_val:,.2f}"

        if unit:
            formatted += f" {unit}"
        return formatted

    def normalize_time_period(self, raw_period_str: Optional[str]) -> NormalizedTimePeriod:
        """
        Parses temporal expressions like 'FY2023', 'FY24', 'FY2025', 'Q4 2023', '2023-Q4', 'December 31, 2023'
        into standardized period identifiers, fiscal years, quarters, and ISO dates.
        """
        if not raw_period_str or not raw_period_str.strip():
            return NormalizedTimePeriod(raw=raw_period_str or "", standard_period="")

        raw = raw_period_str.strip()
        standard_period = raw
        fiscal_year = None
        quarter = None
        period_type = "UNKNOWN"
        start_date = None
        end_date = None

        # 1. Quarters (e.g. Q1 2023, 2023-Q4, Q3 FY24, Q1 FY23, Q2 FY2025, fourth quarter 2023)
        quarter_match = re.search(
            r"\b(Q[1-4]|first quarter|second quarter|third quarter|fourth quarter)\b.*?\b(?:FY\s*)?(\d{4}|\d{2})\b",
            raw,
            re.IGNORECASE
        )
        if quarter_match:
            q_raw = quarter_match.group(1).upper()
            q_num = "Q1" if "1" in q_raw or "FIRST" in q_raw else \
                    "Q2" if "2" in q_raw or "SECOND" in q_raw else \
                    "Q3" if "3" in q_raw or "THIRD" in q_raw else "Q4"
            
            y_raw = quarter_match.group(2)
            year = int(f"20{y_raw}" if len(y_raw) == 2 else y_raw)
            quarter = q_num
            fiscal_year = f"FY{year}"
            standard_period = f"{year}-{q_num}"
            period_type = "QUARTER"
            return NormalizedTimePeriod(
                raw=raw,
                standard_period=standard_period,
                fiscal_year=fiscal_year,
                quarter=quarter,
                period_type=period_type
            )

        # 2. Fiscal Year (e.g. FY2023, FY 2024, FY2025, FY23, FY24, FY25)
        fy_match = re.search(r"\bFY\s*(\d{2,4})\b", raw, re.IGNORECASE)
        if fy_match:
            year_digits = fy_match.group(1)
            full_year = int(f"20{year_digits}" if len(year_digits) == 2 else year_digits)
            standard_period = f"FY{full_year}"
            fiscal_year = f"FY{full_year}"
            period_type = "FISCAL_YEAR"
            return NormalizedTimePeriod(
                raw=raw,
                standard_period=standard_period,
                fiscal_year=fiscal_year,
                start_date=f"{full_year-1}-04-01",
                end_date=f"{full_year}-03-31",
                period_type=period_type
            )

        # 3. Exact Date Parsing with months/days (e.g. "December 31, 2023", "2023-12-31", "31/12/2023")
        month_pattern = r"\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec|ended|as of|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"
        has_date_indicator = bool(re.search(month_pattern, raw, re.IGNORECASE))
        if has_date_indicator:
            try:
                parsed_dt = date_parser.parse(raw, fuzzy=True)
                iso_date = parsed_dt.strftime("%Y-%m-%d")
                return NormalizedTimePeriod(
                    raw=raw,
                    standard_period=iso_date,
                    start_date=iso_date,
                    end_date=iso_date,
                    fiscal_year=f"FY{parsed_dt.year}",
                    period_type="EXACT_DATE"
                )
            except Exception:
                pass

        # 4. Standalone 4-digit Year (e.g. "2023", "in 2024", "2025")
        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", raw)
        if year_match:
            year = year_match.group(1)
            standard_period = year
            fiscal_year = f"FY{year}"
            period_type = "YEAR"
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            return NormalizedTimePeriod(
                raw=raw,
                standard_period=standard_period,
                fiscal_year=fiscal_year,
                start_date=start_date,
                end_date=end_date,
                period_type=period_type
            )

        # Fallback date parsing attempt
        try:
            parsed_dt = date_parser.parse(raw, fuzzy=True)
            iso_date = parsed_dt.strftime("%Y-%m-%d")
            return NormalizedTimePeriod(
                raw=raw,
                standard_period=iso_date,
                start_date=iso_date,
                end_date=iso_date,
                fiscal_year=f"FY{parsed_dt.year}",
                period_type="EXACT_DATE"
            )
        except Exception:
            pass

        return NormalizedTimePeriod(
            raw=raw,
            standard_period=standard_period,
            period_type=period_type
        )
