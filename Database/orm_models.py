"""
ORM Models – SQLAlchemy declarative models mapped to the local SQLite schema.

Every model mirrors a table defined in models.py (TABLES_SQL) so both the
raw-SQL helpers (DatabaseManager) and the ORM layer operate on the same file.

Usage example
-------------
from Database.orm_session import get_session
from Database.orm_models import Company

with get_session() as session:
    company = session.get(Company, some_id)
    company.name = "New Name"
    session.commit()
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _new_uuid() -> str:
    return str(uuid.uuid4())


def _utc_now() -> str:
    return datetime.utcnow().isoformat()


# ─── Base ─────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ─── Mixin for audit columns shared by most entities ─────────────────────────

class AuditMixin:
    """Columns present on every 'full' entity (mirrors BaseEntity.cs)."""

    id = Column(String, primary_key=True, default=_new_uuid)
    created_on = Column(String, nullable=False, default=_utc_now)
    modified_on = Column(String, nullable=True)
    created_by = Column(String, nullable=False, default="")
    modified_by = Column(String, nullable=False, default="")
    authorized = Column(Integer, default=0)
    authorized_by = Column(String, default="")
    authorized_on = Column(String, nullable=True)
    is_deleted = Column(Integer, default=0)
    deleted_by = Column(String, default="")
    deleted_on = Column(String, nullable=True)
    row_version = Column(String, nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
# Company
# ─────────────────────────────────────────────────────────────────────────────

class Company(AuditMixin, Base):
    __tablename__ = "company"

    name = Column(String, nullable=False, default="")
    address = Column(String, default="")
    city = Column(String, default="")
    state = Column(String, nullable=False, default="")
    state_code = Column(String, nullable=False, default="")
    gstin = Column(String, nullable=False, default="")
    zip_code = Column(String, default="")
    country = Column(String, nullable=False, default="")
    phone = Column(String, default="")
    email = Column(String, nullable=False, default="")
    website = Column(String, default="")
    tax_id = Column(String, default="")
    logo_url = Column(String, nullable=False, default="")
    currency = Column(String, nullable=False, default="INR")
    starting_financial_year_date = Column(String, nullable=True)

    bank_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    account_holder_name = Column(String, nullable=True)
    branch_name = Column(String, nullable=True)
    swift_code = Column(String, nullable=True)

    terms_and_conditions = Column(Text, nullable=True)

    billing_address = Column(String, nullable=True)
    billing_city = Column(String, nullable=True)
    billing_state = Column(String, nullable=True)
    billing_state_code = Column(String, nullable=True)
    billing_zip_code = Column(String, nullable=True)
    billing_country = Column(String, nullable=True)

    # Relationships
    financial_years = relationship("FinancialYear", back_populates="company", lazy="select")
    ledgers = relationship("Ledger", back_populates="company", lazy="select")
    products = relationship("Product", back_populates="company", lazy="select")
    taxes = relationship("Tax", back_populates="company", lazy="select")
    attributes = relationship("Attribute", back_populates="company", lazy="select")
    company_roles = relationship("CompanyRole", back_populates="company", lazy="select")
    company_recharges = relationship("CompanyRecharge", back_populates="company", lazy="select")
    transactions = relationship("Transaction", back_populates="company", lazy="select")
    transaction_type_settings = relationship("TransactionTypeSettings", back_populates="company", lazy="select")
    user_companies = relationship("UserCompany", back_populates="company", lazy="select")


# ─────────────────────────────────────────────────────────────────────────────
# Financial Year
# ─────────────────────────────────────────────────────────────────────────────

class FinancialYear(AuditMixin, Base):
    __tablename__ = "financial_year"

    company_id = Column(String, ForeignKey("company.id"), nullable=False)
    year_label = Column(String, nullable=False, default="")
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    is_active = Column(Integer, default=1)

    company = relationship("Company", back_populates="financial_years")
    ledger_opening_balances = relationship("LedgerOpeningBalance", back_populates="financial_year", lazy="select")
    product_opening_stocks = relationship("ProductOpeningStock", back_populates="financial_year", lazy="select")
    transactions = relationship("Transaction", back_populates="financial_year", lazy="select")


Index("idx_financial_year_company", FinancialYear.company_id)


# ─────────────────────────────────────────────────────────────────────────────
# Company Feature
# ─────────────────────────────────────────────────────────────────────────────

class CompanyFeature(Base):
    __tablename__ = "company_feature"

    id = Column(String, primary_key=True, default=_new_uuid)
    name = Column(String, nullable=False, default="")
    code = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")
    category = Column(String, nullable=False, default="")
    is_system_feature = Column(Integer, default=0)
    is_enabled = Column(Integer, default=1)
    created_on = Column(String, nullable=False, default=_utc_now)

    role_features = relationship("CompanyRoleFeature", back_populates="feature", lazy="select")


# ─────────────────────────────────────────────────────────────────────────────
# Company Role
# ─────────────────────────────────────────────────────────────────────────────

class CompanyRole(Base):
    __tablename__ = "company_role"

    id = Column(String, primary_key=True, default=_new_uuid)
    company_id = Column(String, ForeignKey("company.id"), nullable=False)
    name = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")
    is_system_role = Column(Integer, default=0)
    created_on = Column(String, nullable=False, default=_utc_now)
    modified_on = Column(String, nullable=True)

    company = relationship("Company", back_populates="company_roles")
    role_features = relationship("CompanyRoleFeature", back_populates="role", lazy="select")
    user_companies = relationship("UserCompany", back_populates="role_obj", lazy="select")


Index("idx_company_role_company", CompanyRole.company_id)


# ─────────────────────────────────────────────────────────────────────────────
# Company Role Feature
# ─────────────────────────────────────────────────────────────────────────────

class CompanyRoleFeature(Base):
    __tablename__ = "company_role_feature"

    id = Column(String, primary_key=True, default=_new_uuid)
    role_id = Column(String, ForeignKey("company_role.id"), nullable=False)
    feature_id = Column(String, ForeignKey("company_feature.id"), nullable=False)
    company_id = Column(String, nullable=False)
    can_create = Column(Integer, default=0)
    can_read = Column(Integer, default=0)
    can_update = Column(Integer, default=0)
    can_delete = Column(Integer, default=0)
    can_authorize = Column(Integer, default=0)
    created_on = Column(String, nullable=False, default=_utc_now)

    role = relationship("CompanyRole", back_populates="role_features")
    feature = relationship("CompanyFeature", back_populates="role_features")
    user_role_features = relationship("UserCompanyRoleFeature", back_populates="company_role_feature", lazy="select")


# ─────────────────────────────────────────────────────────────────────────────
# User Company Role Feature
# ─────────────────────────────────────────────────────────────────────────────

class UserCompanyRoleFeature(Base):
    __tablename__ = "user_company_role_feature"

    id = Column(String, primary_key=True, default=_new_uuid)
    company_role_feature_id = Column(String, ForeignKey("company_role_feature.id"), nullable=False)
    user_company_id = Column(String, ForeignKey("user_company.id"), nullable=False)
    created_on = Column(String, nullable=False, default=_utc_now)

    company_role_feature = relationship("CompanyRoleFeature", back_populates="user_role_features")
    user_company = relationship("UserCompany", back_populates="role_features")


# ─────────────────────────────────────────────────────────────────────────────
# User Company
# ─────────────────────────────────────────────────────────────────────────────

class UserCompany(Base):
    __tablename__ = "user_company"

    id = Column(String, primary_key=True, default=_new_uuid)
    user_id = Column(String, nullable=False)
    company_id = Column(String, ForeignKey("company.id"), nullable=False)
    role_id = Column(String, ForeignKey("company_role.id"), nullable=True)
    role = Column(String, nullable=True)

    company = relationship("Company", back_populates="user_companies")
    role_obj = relationship("CompanyRole", back_populates="user_companies", foreign_keys=[role_id])
    role_features = relationship("UserCompanyRoleFeature", back_populates="user_company", lazy="select")


Index("idx_user_company_company", UserCompany.company_id)


# ─────────────────────────────────────────────────────────────────────────────
# Company Recharge
# ─────────────────────────────────────────────────────────────────────────────

class CompanyRecharge(AuditMixin, Base):
    __tablename__ = "company_recharge"

    company_id = Column(String, ForeignKey("company.id"), nullable=False)
    amount = Column(Float, nullable=False)
    period = Column(Integer, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    recharge_status = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    transaction_id = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    paid_on = Column(String, nullable=True)
    paid_by = Column(String, nullable=True)
    is_active = Column(Integer, default=1)

    company = relationship("Company", back_populates="company_recharges")


Index("idx_company_recharge_company", CompanyRecharge.company_id)


# ─────────────────────────────────────────────────────────────────────────────
# Ledger
# ─────────────────────────────────────────────────────────────────────────────

class Ledger(AuditMixin, Base):
    __tablename__ = "ledger"

    name = Column(String, nullable=False, default="")
    type = Column(String, nullable=False, default="")
    root_category = Column(String, nullable=False, default="")
    code = Column(String, default="")
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)
    is_group = Column(Integer, default=0)
    is_registered = Column(Integer, nullable=True)
    tax_class = Column(String, nullable=True)
    tax_rate = Column(Float, nullable=True)
    is_credit_allowed = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    return_form_number = Column(String, nullable=True)
    tax_entity_id = Column(String, ForeignKey("tax.id"), nullable=True)
    receivable_ledger_id = Column(String, nullable=True)
    payable_ledger_id = Column(String, nullable=True)
    account_holder_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    parent_id = Column(String, ForeignKey("ledger.id"), nullable=True)
    company_id = Column(String, ForeignKey("company.id"), nullable=False)

    company = relationship("Company", back_populates="ledgers")
    tax_entity = relationship("Tax", back_populates="ledgers", foreign_keys=[tax_entity_id])
    parent = relationship("Ledger", remote_side="Ledger.id", foreign_keys=[parent_id], lazy="select")
    children = relationship("Ledger", back_populates="parent", foreign_keys=[parent_id], lazy="select")
    opening_balances = relationship("LedgerOpeningBalance", back_populates="ledger", lazy="select")
    transaction_ledgers = relationship("TransactionLedger", back_populates="ledger", lazy="select")


Index("idx_ledger_company", Ledger.company_id)
Index("idx_ledger_parent", Ledger.parent_id)
Index("idx_ledger_type", Ledger.type)


# ─────────────────────────────────────────────────────────────────────────────
# Ledger Opening Balance
# ─────────────────────────────────────────────────────────────────────────────

class LedgerOpeningBalance(AuditMixin, Base):
    __tablename__ = "ledger_opening_balance"

    ledger_id = Column(String, ForeignKey("ledger.id"), nullable=False)
    financial_year_id = Column(String, ForeignKey("financial_year.id"), nullable=False)
    opening_date = Column(String, nullable=False)
    opening_balance = Column(Float, nullable=False)
    balance_type = Column(String, nullable=False, default="")

    ledger = relationship("Ledger", back_populates="opening_balances")
    financial_year = relationship("FinancialYear", back_populates="ledger_opening_balances")


Index("idx_ledger_opening_balance_ledger", LedgerOpeningBalance.ledger_id)


# ─────────────────────────────────────────────────────────────────────────────
# Tax
# ─────────────────────────────────────────────────────────────────────────────

class Tax(AuditMixin, Base):
    __tablename__ = "tax"

    name = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")
    category = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    is_composite = Column(Integer, default=0)
    default_rate = Column(Float, nullable=False, default=0)
    hsn_code = Column(String, nullable=True)
    section_code = Column(String, nullable=True)
    is_reverse_charge_applicable = Column(Integer, default=0)
    is_deductible_at_source = Column(Integer, default=0)
    is_collected_at_source = Column(Integer, default=0)
    return_form_number = Column(String, nullable=True)
    company_id = Column(String, ForeignKey("company.id"), nullable=False)

    company = relationship("Company", back_populates="taxes")
    components = relationship("TaxComponent", back_populates="tax", lazy="select")
    rates = relationship("TaxRate", back_populates="tax", lazy="select")
    ledgers = relationship("Ledger", back_populates="tax_entity", foreign_keys="Ledger.tax_entity_id", lazy="select")


Index("idx_tax_company", Tax.company_id)


# ─────────────────────────────────────────────────────────────────────────────
# Tax Component
# ─────────────────────────────────────────────────────────────────────────────

class TaxComponent(AuditMixin, Base):
    __tablename__ = "tax_component"

    name = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")
    type = Column(String, nullable=False)
    rate = Column(Float, nullable=False, default=0)
    ledger_code = Column(String, nullable=False, default="")
    is_credit_allowed = Column(Integer, default=0)
    return_form_number = Column(String, nullable=True)
    tax_id = Column(String, ForeignKey("tax.id"), nullable=False)
    ledger_id = Column(String, ForeignKey("ledger.id"), nullable=False)
    receivable_ledger_id = Column(String, nullable=True)
    payable_ledger_id = Column(String, nullable=True)
    is_active = Column(Integer, default=1)

    tax = relationship("Tax", back_populates="components")
    ledger = relationship("Ledger", foreign_keys=[ledger_id])


Index("idx_tax_component_tax", TaxComponent.tax_id)


# ─────────────────────────────────────────────────────────────────────────────
# Tax Rate
# ─────────────────────────────────────────────────────────────────────────────

class TaxRate(AuditMixin, Base):
    __tablename__ = "tax_rate"

    tax_id = Column(String, ForeignKey("tax.id"), nullable=False)
    rate = Column(Float, nullable=False, default=0)
    name = Column(String, nullable=False, default="")
    hsn_code = Column(String, nullable=True)
    min_amount = Column(Float, nullable=True)
    max_amount = Column(Float, nullable=True)
    effective_from = Column(String, nullable=False)
    effective_to = Column(String, nullable=True)
    is_active = Column(Integer, default=1)

    tax = relationship("Tax", back_populates="rates")


Index("idx_tax_rate_tax", TaxRate.tax_id)


# ─────────────────────────────────────────────────────────────────────────────
# Attribute
# ─────────────────────────────────────────────────────────────────────────────

class Attribute(AuditMixin, Base):
    __tablename__ = "attribute"

    name = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")
    is_required = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    company_id = Column(String, ForeignKey("company.id"), nullable=False)

    company = relationship("Company", back_populates="attributes")
    options = relationship("AttributeOption", back_populates="attribute", lazy="select")
    product_attributes = relationship("ProductAttribute", back_populates="attribute", lazy="select")
    product_variant_attributes = relationship("ProductVariantAttribute", back_populates="attribute", lazy="select")


Index("idx_attribute_company", Attribute.company_id)


# ─────────────────────────────────────────────────────────────────────────────
# Attribute Option
# ─────────────────────────────────────────────────────────────────────────────

class AttributeOption(AuditMixin, Base):
    __tablename__ = "attribute_option"

    value = Column(String, nullable=False, default="")
    display_name = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")
    is_active = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    attribute_id = Column(String, ForeignKey("attribute.id"), nullable=False)
    company_id = Column(String, ForeignKey("company.id"), nullable=False)

    attribute = relationship("Attribute", back_populates="options")
    product_variant_attributes = relationship("ProductVariantAttribute", back_populates="attribute_option", lazy="select")


Index("idx_attribute_option_attr", AttributeOption.attribute_id)


# ─────────────────────────────────────────────────────────────────────────────
# Product
# ─────────────────────────────────────────────────────────────────────────────

class Product(AuditMixin, Base):
    __tablename__ = "product"

    product_code = Column(String, nullable=False, default="")
    name = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")
    purchase_price = Column(Float, nullable=False, default=0)
    selling_price = Column(Float, nullable=False, default=0)
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Integer, default=0)
    sku = Column(String, nullable=False, default="")
    barcode = Column(String, nullable=False, default="")
    unit = Column(String, nullable=False, default="")
    parent_id = Column(String, ForeignKey("product.id"), nullable=True)
    company_id = Column(String, ForeignKey("company.id"), nullable=False)

    company = relationship("Company", back_populates="products")
    parent = relationship("Product", remote_side="Product.id", foreign_keys=[parent_id], lazy="select")
    children = relationship("Product", back_populates="parent", foreign_keys=[parent_id], lazy="select")
    variants = relationship("ProductVariant", back_populates="product", lazy="select")
    product_attributes = relationship("ProductAttribute", back_populates="product", lazy="select")
    opening_stocks = relationship("ProductOpeningStock", back_populates="product", lazy="select")
    transaction_items = relationship("TransactionItem", back_populates="product", lazy="select")


Index("idx_product_company", Product.company_id)
Index("idx_product_parent", Product.parent_id)


# ─────────────────────────────────────────────────────────────────────────────
# Product Attribute
# ─────────────────────────────────────────────────────────────────────────────

class ProductAttribute(AuditMixin, Base):
    __tablename__ = "product_attribute"

    product_id = Column(String, ForeignKey("product.id"), nullable=False)
    attribute_id = Column(String, ForeignKey("attribute.id"), nullable=False)
    company_id = Column(String, nullable=False)
    is_active = Column(Integer, default=1)

    product = relationship("Product", back_populates="product_attributes")
    attribute = relationship("Attribute", back_populates="product_attributes")


Index("idx_product_attribute_product", ProductAttribute.product_id)


# ─────────────────────────────────────────────────────────────────────────────
# Product Variant
# ─────────────────────────────────────────────────────────────────────────────

class ProductVariant(AuditMixin, Base):
    __tablename__ = "product_variant"

    variant_code = Column(String, nullable=False, default="")
    name = Column(String, nullable=False, default="")
    description = Column(String, nullable=False, default="")
    purchase_price = Column(Float, nullable=False, default=0)
    selling_price = Column(Float, nullable=False, default=0)
    stock_quantity = Column(Integer, nullable=False, default=0)
    min_stock_level = Column(Integer, nullable=False, default=0)
    max_stock_level = Column(Integer, nullable=False, default=0)
    is_active = Column(Integer, default=1)
    sku = Column(String, nullable=False, default="")
    barcode = Column(String, nullable=False, default="")
    weight = Column(Float, nullable=False, default=0)
    unit = Column(String, nullable=False, default="")
    image_url = Column(String, nullable=False, default="")
    sort_order = Column(Integer, default=0)
    product_id = Column(String, ForeignKey("product.id"), nullable=False)
    company_id = Column(String, nullable=False)

    product = relationship("Product", back_populates="variants")
    variant_attributes = relationship("ProductVariantAttribute", back_populates="product_variant", lazy="select")
    transaction_item_variants = relationship("TransactionItemVariant", back_populates="product_variant", lazy="select")


Index("idx_product_variant_product", ProductVariant.product_id)


# ─────────────────────────────────────────────────────────────────────────────
# Product Variant Attribute
# ─────────────────────────────────────────────────────────────────────────────

class ProductVariantAttribute(AuditMixin, Base):
    __tablename__ = "product_variant_attribute"

    product_variant_id = Column(String, ForeignKey("product_variant.id"), nullable=False)
    attribute_id = Column(String, ForeignKey("attribute.id"), nullable=False)
    attribute_option_id = Column(String, ForeignKey("attribute_option.id"), nullable=False)
    company_id = Column(String, nullable=False)
    custom_value = Column(String, nullable=False, default="")
    is_active = Column(Integer, default=1)

    product_variant = relationship("ProductVariant", back_populates="variant_attributes")
    attribute = relationship("Attribute", back_populates="product_variant_attributes")
    attribute_option = relationship("AttributeOption", back_populates="product_variant_attributes")


Index("idx_product_variant_attribute_variant", ProductVariantAttribute.product_variant_id)


# ─────────────────────────────────────────────────────────────────────────────
# Product Opening Stock
# ─────────────────────────────────────────────────────────────────────────────

class ProductOpeningStock(AuditMixin, Base):
    __tablename__ = "product_opening_stock"

    product_id = Column(String, ForeignKey("product.id"), nullable=False)
    financial_year_id = Column(String, ForeignKey("financial_year.id"), nullable=False)
    opening_date = Column(String, nullable=False)
    quantity = Column(Float, nullable=False, default=0)
    rate = Column(Float, nullable=False, default=0)
    value_amount = Column(Float, nullable=False, default=0)

    product = relationship("Product", back_populates="opening_stocks")
    financial_year = relationship("FinancialYear", back_populates="product_opening_stocks")


Index("idx_product_opening_stock_product", ProductOpeningStock.product_id)


# ─────────────────────────────────────────────────────────────────────────────
# Transaction   (quoted because "transaction" is an SQL reserved word)
# ─────────────────────────────────────────────────────────────────────────────

class Transaction(AuditMixin, Base):
    __tablename__ = "transaction"

    transaction_number = Column(String, nullable=False, default="")
    invoice_number = Column(String, nullable=True)
    transaction_date = Column(String, nullable=False)
    form_type = Column(String, nullable=False, default="")
    type = Column(String, nullable=False)
    journal_entry_type = Column(String, nullable=True)
    nature_of_transaction = Column(String, nullable=True)
    due_date = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    sub_total = Column(Float, nullable=False, default=0)
    tax_rate = Column(Float, nullable=False, default=0)
    tax_amount = Column(Float, nullable=False, default=0)
    discount = Column(Float, nullable=False, default=0)
    discount_amount = Column(Float, nullable=False, default=0)
    freight = Column(Float, nullable=False, default=0)
    is_freight_included = Column(Integer, default=0)
    round_off = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False, default=0)
    paid_amount = Column(Float, nullable=True)
    is_paid = Column(Integer, default=0)
    status = Column(String, nullable=False, default="Draft")
    payment_status = Column(String, nullable=False, default="Credit")
    reference_number = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    is_paid_with_transaction = Column(Integer, default=0)
    company_id = Column(String, ForeignKey("company.id"), nullable=True)
    financial_year_id = Column(String, ForeignKey("financial_year.id"), nullable=True)

    company = relationship("Company", back_populates="transactions")
    financial_year = relationship("FinancialYear", back_populates="transactions")
    transaction_ledgers = relationship("TransactionLedger", back_populates="transaction", lazy="select")
    transaction_items = relationship("TransactionItem", back_populates="transaction", lazy="select")
    transaction_taxes = relationship("TransactionTax", back_populates="transaction", lazy="select")
    payments_made = relationship(
        "TransactionPayment",
        back_populates="payment_transaction",
        foreign_keys="TransactionPayment.payment_transaction_id",
        lazy="select",
    )
    payments_received = relationship(
        "TransactionPayment",
        back_populates="invoice_transaction",
        foreign_keys="TransactionPayment.invoice_transaction_id",
        lazy="select",
    )
    links_from = relationship(
        "TransactionLink",
        back_populates="from_transaction",
        foreign_keys="TransactionLink.from_transaction_id",
        lazy="select",
    )
    links_to = relationship(
        "TransactionLink",
        back_populates="to_transaction",
        foreign_keys="TransactionLink.to_transaction_id",
        lazy="select",
    )


Index("idx_transaction_company", Transaction.company_id)
Index("idx_transaction_fy", Transaction.financial_year_id)
Index("idx_transaction_type", Transaction.type)
Index("idx_transaction_date", Transaction.transaction_date)


# ─────────────────────────────────────────────────────────────────────────────
# Transaction Ledger
# ─────────────────────────────────────────────────────────────────────────────

class TransactionLedger(Base):
    __tablename__ = "transaction_ledger"

    id = Column(String, primary_key=True, default=_new_uuid)
    serial_number = Column(Integer, default=0)
    transaction_id = Column(String, ForeignKey("transaction.id"), nullable=False)
    ledger_id = Column(String, ForeignKey("ledger.id"), nullable=False)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False, default=0)
    description = Column(Text, nullable=True)
    is_main_entry = Column(Integer, nullable=True)
    is_system_entry = Column(Integer, nullable=True)

    transaction = relationship("Transaction", back_populates="transaction_ledgers")
    ledger = relationship("Ledger", back_populates="transaction_ledgers")


Index("idx_transaction_ledger_tx", TransactionLedger.transaction_id)
Index("idx_transaction_ledger_ledger", TransactionLedger.ledger_id)


# ─────────────────────────────────────────────────────────────────────────────
# Transaction Item
# ─────────────────────────────────────────────────────────────────────────────

class TransactionItem(Base):
    __tablename__ = "transaction_item"

    id = Column(String, primary_key=True, default=_new_uuid)
    transaction_id = Column(String, ForeignKey("transaction.id"), nullable=False)
    product_id = Column(String, ForeignKey("product.id"), nullable=False)
    description = Column(String, nullable=False, default="")
    quantity = Column(Float, nullable=False, default=0)
    unit_price = Column(Float, nullable=False, default=0)
    tax_rate = Column(Float, nullable=False, default=0)
    tax_amount = Column(Float, nullable=False, default=0)
    discount_rate = Column(Float, nullable=False, default=0)
    discount_amount = Column(Float, nullable=False, default=0)
    line_total = Column(Float, nullable=False, default=0)
    current_quantity = Column(Float, nullable=False, default=0)
    serial_number = Column(Integer, default=0)
    system_quantity = Column(Float, nullable=True)
    physical_quantity = Column(Float, nullable=True)
    adjustment_reason = Column(Text, nullable=True)

    transaction = relationship("Transaction", back_populates="transaction_items")
    product = relationship("Product", back_populates="transaction_items")
    item_variants = relationship("TransactionItemVariant", back_populates="transaction_item", lazy="select")


Index("idx_transaction_item_tx", TransactionItem.transaction_id)


# ─────────────────────────────────────────────────────────────────────────────
# Transaction Item Variant
# ─────────────────────────────────────────────────────────────────────────────

class TransactionItemVariant(Base):
    __tablename__ = "transaction_item_variant"

    id = Column(String, primary_key=True, default=_new_uuid)
    transaction_item_id = Column(String, ForeignKey("transaction_item.id"), nullable=False)
    product_variant_id = Column(String, ForeignKey("product_variant.id"), nullable=False)
    variant_code = Column(String, nullable=False, default="")
    variant_name = Column(String, nullable=False, default="")
    quantity = Column(Float, nullable=False, default=0)
    unit_price = Column(Float, nullable=False, default=0)
    selling_price = Column(Float, nullable=False, default=0)
    current_quantity = Column(Float, nullable=False, default=0)
    serial_number = Column(Integer, default=0)
    description = Column(Text, nullable=True)

    transaction_item = relationship("TransactionItem", back_populates="item_variants")
    product_variant = relationship("ProductVariant", back_populates="transaction_item_variants")


# ─────────────────────────────────────────────────────────────────────────────
# Transaction Tax
# ─────────────────────────────────────────────────────────────────────────────

class TransactionTax(Base):
    __tablename__ = "transaction_tax"

    id = Column(String, primary_key=True, default=_new_uuid)
    transaction_id = Column(String, ForeignKey("transaction.id"), nullable=False)
    tax_ledger_id = Column(String, ForeignKey("ledger.id"), nullable=False)
    taxable_amount = Column(Float, nullable=False, default=0)
    tax_amount = Column(Float, nullable=False, default=0)
    calculation_method = Column(String, nullable=False, default="ItemSubtotal")
    is_applied = Column(Integer, default=0)
    applied_date = Column(String, nullable=True)
    reference_number = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    serial_number = Column(Integer, default=0)

    transaction = relationship("Transaction", back_populates="transaction_taxes")
    tax_ledger = relationship("Ledger", foreign_keys=[tax_ledger_id])


Index("idx_transaction_tax_tx", TransactionTax.transaction_id)


# ─────────────────────────────────────────────────────────────────────────────
# Transaction Payment
# ─────────────────────────────────────────────────────────────────────────────

class TransactionPayment(AuditMixin, Base):
    __tablename__ = "transaction_payment"

    payment_transaction_id = Column(String, ForeignKey("transaction.id"), nullable=False)
    invoice_transaction_id = Column(String, ForeignKey("transaction.id"), nullable=False)
    payment_ledger_id = Column(String, ForeignKey("ledger.id"), nullable=True)
    amount = Column(Float, nullable=False, default=0)
    payment_date = Column(String, nullable=False)
    payment_method = Column(String, nullable=True)
    payment_gateway = Column(String, nullable=True)
    transaction_utr_number = Column(String, nullable=True)
    cheque_number = Column(String, nullable=True)
    cheque_date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(String, nullable=False, default=_utc_now)

    payment_transaction = relationship(
        "Transaction",
        back_populates="payments_made",
        foreign_keys=[payment_transaction_id],
    )
    invoice_transaction = relationship(
        "Transaction",
        back_populates="payments_received",
        foreign_keys=[invoice_transaction_id],
    )
    payment_ledger = relationship("Ledger", foreign_keys=[payment_ledger_id])


Index("idx_transaction_payment_pay", TransactionPayment.payment_transaction_id)
Index("idx_transaction_payment_inv", TransactionPayment.invoice_transaction_id)


# ─────────────────────────────────────────────────────────────────────────────
# Transaction Link
# ─────────────────────────────────────────────────────────────────────────────

class TransactionLink(Base):
    __tablename__ = "transaction_link"

    id = Column(String, primary_key=True, default=_new_uuid)
    from_transaction_id = Column(String, ForeignKey("transaction.id"), nullable=False)
    to_transaction_id = Column(String, ForeignKey("transaction.id"), nullable=False)
    linked_on = Column(String, nullable=False)
    notes = Column(Text, nullable=True)

    from_transaction = relationship(
        "Transaction",
        back_populates="links_from",
        foreign_keys=[from_transaction_id],
    )
    to_transaction = relationship(
        "Transaction",
        back_populates="links_to",
        foreign_keys=[to_transaction_id],
    )


Index("idx_transaction_link_from", TransactionLink.from_transaction_id)
Index("idx_transaction_link_to", TransactionLink.to_transaction_id)


# ─────────────────────────────────────────────────────────────────────────────
# Transaction Type Settings
# ─────────────────────────────────────────────────────────────────────────────

class TransactionTypeSettings(AuditMixin, Base):
    __tablename__ = "transaction_type_settings"

    company_id = Column(String, ForeignKey("company.id"), nullable=False)
    transaction_type = Column(String, nullable=False)
    auto_generate_invoice = Column(Integer, default=1)
    allow_duplicate_invoice_number = Column(Integer, default=0)
    show_billing_address = Column(Integer, default=1)
    show_shipping_address = Column(Integer, default=1)
    require_billing_address = Column(Integer, default=0)
    require_shipping_address = Column(Integer, default=0)
    invoice_number_prefix = Column(String, nullable=True)
    invoice_number_suffix = Column(String, nullable=True)
    invoice_number_length = Column(Integer, default=6)
    next_invoice_number = Column(Integer, default=1)
    copy_billing_to_shipping = Column(Integer, default=0)
    copy_shipping_to_billing = Column(Integer, default=0)

    company = relationship("Company", back_populates="transaction_type_settings")


Index("idx_transaction_type_settings_company", TransactionTypeSettings.company_id)


# ─────────────────────────────────────────────────────────────────────────────
# Sync Log
# Maps to the local SQLite `sync_log` table.
# Cloud counterpart: PostgreSQL `SyncLogs` table (see Entities/SyncLog.cs).
# ─────────────────────────────────────────────────────────────────────────────

class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(String, primary_key=True, default=_new_uuid)
    table_name = Column(String, nullable=False)
    record_id = Column(String, nullable=False)
    action = Column(String, nullable=False)          # INSERT | UPDATE | SOFT_DELETE | HARD_DELETE
    changed_data = Column(Text, nullable=True)       # JSON snapshot of changed fields
    created_on = Column(String, nullable=False, default=_utc_now)
    is_synced = Column(Integer, default=0)
    synced_on = Column(String, nullable=True)
    sync_error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)


Index("idx_sync_log_is_synced", SyncLog.is_synced)
Index("idx_sync_log_table", SyncLog.table_name)
Index("idx_sync_log_record", SyncLog.record_id)
