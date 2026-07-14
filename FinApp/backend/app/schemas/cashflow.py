from pydantic import BaseModel


class CashflowCategoryCreate(BaseModel):
    section: str
    direction: str
    article: str
    keywords: str
    account_type_filter: str = "all"
    priority: int = 0
    is_active: bool = True


class CashflowCategoryRead(CashflowCategoryCreate):
    id: int

    model_config = {"from_attributes": True}


class CashflowReportLine(BaseModel):
    section: str
    direction: str
    article: str
    total: float
    checking: float
    credit: float
    personal: float


class CashflowReportResponse(BaseModel):
    period_from: str
    period_to: str
    lines: list[CashflowReportLine]
    total_inflow: float
    total_outflow: float
    net_cashflow: float
    net_cashflow_checking: float
    net_cashflow_credit: float
    net_cashflow_personal: float
    unclassified_count: int