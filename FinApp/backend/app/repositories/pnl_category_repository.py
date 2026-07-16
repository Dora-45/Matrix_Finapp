from sqlalchemy.orm import Session

from backend.app.models.pnl_category import PnlCategory


class PnlCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_active(self) -> list[PnlCategory]:
        return (
            self.db.query(PnlCategory)
            .filter(PnlCategory.is_active == True)
            .order_by(PnlCategory.priority.desc(), PnlCategory.id.asc())
            .all()
        )

    def seed_defaults(self) -> None:
        if self.db.query(PnlCategory).count() > 0:
            return

        defaults = [
            PnlCategory(
                direction="inflow",
                pnl_sign="income",
                pnl_group="revenue",
                pnl_article="Выручка",
                keywords="оплата,оплата за,поступление от,эквайринг,продажа,yoomoney,юмани",
                account_type_filter="all",
                priority=10,
                is_active=True,
            ),
            PnlCategory(
                direction="inflow",
                pnl_sign="income",
                pnl_group="other_income",
                pnl_article="Прочие доходы",
                keywords="refund,возврат,возврат средств",
                account_type_filter="all",
                priority=7,
                is_active=True,
            ),
            PnlCategory(
                direction="outflow",
                pnl_sign="expense",
                pnl_group="cogs",
                pnl_article="Себестоимость",
                keywords="закупка,материал,сырье,сырьё,товар,поставка",
                account_type_filter="all",
                priority=10,
                is_active=True,
            ),
            PnlCategory(
                direction="outflow",
                pnl_sign="expense",
                pnl_group="operating_expenses",
                pnl_article="Заработная плата",
                keywords="зарплата,оклад,заработная плата,выплата сотрудник,выплата зп",
                account_type_filter="all",
                priority=10,
                is_active=True,
            ),
            PnlCategory(
                direction="outflow",
                pnl_sign="expense",
                pnl_group="operating_expenses",
                pnl_article="Аренда",
                keywords="аренда,арендная плата,субаренда",
                account_type_filter="all",
                priority=9,
                is_active=True,
            ),
            PnlCategory(
                direction="outflow",
                pnl_sign="expense",
                pnl_group="operating_expenses",
                pnl_article="Маркетинг и реклама",
                keywords="реклама,маркетинг,продвижение,яндекс,vk,таргет",
                account_type_filter="all",
                priority=8,
                is_active=True,
            ),
            PnlCategory(
                direction="outflow",
                pnl_sign="expense",
                pnl_group="operating_expenses",
                pnl_article="Сервисы и подписки",
                keywords="подписка,сервис,лицензия,saas,хостинг,домен",
                account_type_filter="all",
                priority=7,
                is_active=True,
            ),
            PnlCategory(
                direction="outflow",
                pnl_sign="expense",
                pnl_group="operating_expenses",
                pnl_article="Банковские расходы",
                keywords="комиссия банка,обслуживание счёта,обслуживание счета,банковская комиссия,смс-информ",
                account_type_filter="all",
                priority=7,
                is_active=True,
            ),
            PnlCategory(
                direction="outflow",
                pnl_sign="expense",
                pnl_group="taxes",
                pnl_article="Налоги",
                keywords="налог,ндс,есн,страховые взносы,ифнс,фнс,пфр,фсс,усн,ндфл",
                account_type_filter="all",
                priority=10,
                is_active=True,
            ),
            PnlCategory(
                direction="outflow",
                pnl_sign="expense",
                pnl_group="other_expenses",
                pnl_article="Проценты по кредиту",
                keywords="проценты по кредиту,уплата процентов",
                account_type_filter="credit",
                priority=10,
                is_active=True,
            ),
        ]

        self.db.add_all(defaults)
        self.db.commit()