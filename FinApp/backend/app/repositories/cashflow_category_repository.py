from sqlalchemy.orm import Session

from backend.app.models.cashflow_category import CashflowCategory
from backend.app.schemas.cashflow import CashflowCategoryCreate


class CashflowCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_active(self) -> list[CashflowCategory]:
        return (
            self.db.query(CashflowCategory)
            .filter(CashflowCategory.is_active == True)
            .order_by(CashflowCategory.priority.desc(), CashflowCategory.id.asc())
            .all()
        )

    def create(self, data: CashflowCategoryCreate) -> CashflowCategory:
        category = CashflowCategory(**data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def seed_defaults(self) -> None:
        if self.db.query(CashflowCategory).count() > 0:
            return

        defaults = [
            CashflowCategory(
                section="operating",
                direction="inflow",
                article="Выручка от продаж",
                keywords="оплата,оплата за,поступление от,эквайринг,продажа,yoomoney,юмани",
                account_type_filter="all",
                priority=10,
                is_active=True,
            ),
            CashflowCategory(
                section="operating",
                direction="inflow",
                article="Возврат от поставщиков",
                keywords="возврат,refund,возврат средств",
                account_type_filter="all",
                priority=9,
                is_active=True,
            ),
            CashflowCategory(
                section="operating",
                direction="outflow",
                article="Заработная плата",
                keywords="зарплата,оклад,заработная плата,выплата сотрудник,выплата зп",
                account_type_filter="all",
                priority=10,
                is_active=True,
            ),
            CashflowCategory(
                section="operating",
                direction="outflow",
                article="Налоги и взносы",
                keywords="налог,ндс,есн,страховые взносы,ифнс,фнс,пфр,фсс,усн,ндфл",
                account_type_filter="all",
                priority=10,
                is_active=True,
            ),
            CashflowCategory(
                section="operating",
                direction="outflow",
                article="Аренда офиса",
                keywords="аренда,арендная плата,субаренда",
                account_type_filter="all",
                priority=9,
                is_active=True,
            ),
            CashflowCategory(
                section="operating",
                direction="outflow",
                article="Маркетинг и реклама",
                keywords="реклама,маркетинг,продвижение,яндекс,vk,таргет",
                account_type_filter="all",
                priority=8,
                is_active=True,
            ),
            CashflowCategory(
                section="operating",
                direction="outflow",
                article="Сервисы и подписки",
                keywords="подписка,сервис,лицензия,saas,хостинг,домен",
                account_type_filter="all",
                priority=7,
                is_active=True,
            ),
            CashflowCategory(
                section="operating",
                direction="outflow",
                article="Закупка товаров и материалов",
                keywords="закупка,материал,сырье,сырьё,товар,поставка",
                account_type_filter="all",
                priority=8,
                is_active=True,
            ),
            CashflowCategory(
                section="operating",
                direction="outflow",
                article="Банковское обслуживание",
                keywords="комиссия банка,обслуживание счёта,обслуживание счета,банковская комиссия,смс-информ",
                account_type_filter="all",
                priority=6,
                is_active=True,
            ),
            CashflowCategory(
                section="financing",
                direction="inflow",
                article="Получение кредита",
                keywords="выдача кредита,кредитные средства,транш,кредит зачислен",
                account_type_filter="credit",
                priority=10,
                is_active=True,
            ),
            CashflowCategory(
                section="financing",
                direction="outflow",
                article="Погашение кредита",
                keywords="погашение кредита,погашение основного долга,возврат кредита",
                account_type_filter="credit",
                priority=10,
                is_active=True,
            ),
            CashflowCategory(
                section="financing",
                direction="outflow",
                article="Проценты по кредиту",
                keywords="проценты по кредиту,уплата процентов",
                account_type_filter="credit",
                priority=10,
                is_active=True,
            ),
            CashflowCategory(
                section="transfer",
                direction="inflow",
                article="Перевод между счетами",
                keywords="перевод на счёт,перевод на счет,пополнение счёта,пополнение счета,внутренний перевод",
                account_type_filter="all",
                priority=20,
                is_active=True,
            ),
            CashflowCategory(
                section="transfer",
                direction="outflow",
                article="Перевод между счетами",
                keywords="перевод на счёт,перевод на счет,перевод на карту,со счёта на счёт,со счета на счет",
                account_type_filter="all",
                priority=20,
                is_active=True,
            ),
        ]

        self.db.add_all(defaults)
        self.db.commit()