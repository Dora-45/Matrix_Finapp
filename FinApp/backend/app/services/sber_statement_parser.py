from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd


def detect_account_type(account_number: str, payment_purpose: str) -> str:
    purpose = (payment_purpose or "").lower()

    if "выдача кредита" in purpose or "кредит" in purpose:
        return "credit"

    return "checking"


def clean_multiline_cell(value) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    while "  " in text:
        text = text.replace("  ", " ")
    return text


def extract_first_line(value) -> str:
    if value is None:
        return ""
    return str(value).split("\n")[0].strip()


def extract_third_line_name(value) -> str:
    if value is None:
        return ""
    parts = [part.strip() for part in str(value).split("\n") if part.strip()]
    if len(parts) >= 3:
        return parts[2]
    if len(parts) >= 2:
        return parts[1]
    if len(parts) >= 1:
        return parts[0]
    return ""


def find_header_row(df: pd.DataFrame) -> int | None:
    for index in range(min(len(df), 25)):
        row_values = " | ".join(df.iloc[index].astype(str).tolist()).lower()
        if "дата проводки" in row_values and "назначение платежа" in row_values:
            return index
    return None


def parse_sber_statement(file_path: str) -> list[dict]:
    xls = pd.ExcelFile(file_path)
    normalized_rows: list[dict] = []

    for sheet_name in xls.sheet_names:
        raw_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        header_row_index = find_header_row(raw_df)

        if header_row_index is None:
            continue

        header_row = raw_df.iloc[header_row_index].fillna("")
        data_start_index = header_row_index + 2

        working_df = raw_df.iloc[data_start_index:].copy()
        working_df.columns = [str(col).strip() for col in header_row.tolist()]
        working_df = working_df.fillna("")

        for _, row in working_df.iterrows():
            operation_date = row.get("Дата проводки", "")
            payment_purpose = row.get("Назначение платежа", "")

            if not operation_date or not payment_purpose:
                continue

            debit_cell = row.get("Сумма по дебету", "")
            credit_cell = row.get("Сумма по кредиту", "")

            debit_value = str(debit_cell).replace(",", ".").strip() if debit_cell != "" else ""
            credit_value = str(credit_cell).replace(",", ".").strip() if credit_cell != "" else ""

            amount = None
            direction = None

            if debit_value not in {"", "0", "0.0", "0.00"}:
                amount = Decimal(debit_value)
                direction = "outflow"
            elif credit_value not in {"", "0", "0.0", "0.00"}:
                amount = Decimal(credit_value)
                direction = "inflow"
            else:
                continue

            own_account_raw = row.get("Счет", "")
            debit_account = row.get("Дебет", "")
            credit_account = row.get("Кредит", "")

            if direction == "outflow":
                account_number = extract_first_line(debit_account) or sheet_name
                counterparty_account = extract_first_line(credit_account)
                counterparty_name = extract_third_line_name(credit_account)
            else:
                account_number = extract_first_line(credit_account) or sheet_name
                counterparty_account = extract_first_line(debit_account)
                counterparty_name = extract_third_line_name(debit_account)

            operation_datetime = pd.to_datetime(operation_date).to_pydatetime()
            payment_purpose_clean = clean_multiline_cell(payment_purpose)
            bank_name = clean_multiline_cell(row.get("Банк (БИК и наименование)", ""))
            document_number = clean_multiline_cell(row.get("№ документа", ""))
            operation_code = clean_multiline_cell(row.get("ВО", ""))

            account_type = detect_account_type(account_number, payment_purpose_clean)

            normalized_rows.append({
                "operation_datetime": operation_datetime,
                "account_number": account_number or str(sheet_name),
                "account_type": account_type,
                "direction": direction,
                "amount": amount,
                "currency": "RUB",
                "counterparty_account": counterparty_account,
                "counterparty_name": counterparty_name,
                "bank_name": bank_name,
                "document_number": document_number,
                "operation_code": operation_code,
                "payment_purpose": payment_purpose_clean,
                "source_file": Path(file_path).name,
                "source_sheet": str(sheet_name),
                "article": None,
                "project": None,
                "is_manual": "no",
            })

    return normalized_rows