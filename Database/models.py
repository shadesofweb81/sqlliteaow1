import uuid
from datetime import datetime


def new_uuid():
    return str(uuid.uuid4())


def utc_now():
    return datetime.utcnow().isoformat()


# ─── Enums ───────────────────────────────────────────────────────────────────

class TaxCategory:
    GST = "GST"
    INCOME_TAX = "IncomeTax"
    CUSTOMS_DUTY = "CustomsDuty"
    CESS = "Cess"
    SERVICE_TAX = "ServiceTax"
    VAT = "VAT"
    OTHER = "Other"


class TaxType:
    CGST = "CGST"
    SGST = "SGST"
    IGST = "IGST"
    UTGST = "UTGST"
    COMPENSATION_CESS = "CompensationCess"
    TDS = "TDS"
    TCS = "TCS"
    ADVANCE_TAX = "AdvanceTax"
    SELF_ASSESSMENT_TAX = "SelfAssessmentTax"
    BASIC_CUSTOMS_DUTY = "BasicCustomsDuty"
    COUNTERVAILING_DUTY = "CountervailingDuty"
    ANTI_DUMPING_DUTY = "AntiDumpingDuty"
    SAFEGUARD_DUTY = "SafeguardDuty"
    EDUCATION_CESS = "EducationCess"
    HIGHER_EDUCATION_CESS = "HigherEducationCess"
    SWACHH_BHARAT_CESS = "SwachhBharatCess"
    KRISHI_KALYAN_CESS = "KrishiKalyanCess"
    ROAD_CESS = "RoadCess"
    PROFESSIONAL_TAX = "ProfessionalTax"
    STAMP_DUTY = "StampDuty"
    OTHER = "Other"


class TransactionType:
    SALE_QUOTATION = "SaleQuotation"
    SALE_ORDER = "SaleOrder"
    SALE_INVOICE = "SaleInvoice"
    SALE_RETURN = "SaleReturn"
    PURCHASE_QUOTATION = "PurchaseQuotation"
    PURCHASE_ORDER = "PurchaseOrder"
    PURCHASE_BILL = "PurchaseBill"
    PURCHASE_RETURN = "PurchaseReturn"
    BANK_PAYMENT = "BankPayment"
    BANK_RECEIPT = "BankReceipt"
    CASH_PAYMENT = "CashPayment"
    CASH_RECEIPT = "CashReceipt"
    JOURNAL_ENTRY = "JournalEntry"
    PHYSICAL_STOCK = "PhysicalStock"


class JournalEntryType:
    JOURNAL_ENTRY = "JournalEntry"
    OPENING_BALANCE = "OpeningBalance"
    SALE_QUOTATION = "SaleQuotation"
    SALE_ORDER = "SaleOrder"
    SALE_INVOICE = "SaleInvoice"
    SALE_RETURN = "SaleReturn"
    PURCHASE_QUOTATION = "PurchaseQuotation"
    PURCHASE_ORDER = "PurchaseOrder"
    PURCHASE_BILL = "PurchaseBill"
    PURCHASE_RETURN = "PurchaseReturn"
    BANK_PAYMENT = "BankPayment"
    BANK_RECEIPT = "BankReceipt"
    CASH_PAYMENT = "CashPayment"
    CASH_RECEIPT = "CashReceipt"


class NatureOfTransaction:
    NOT_APPLICABLE = "NotApplicable"
    REGISTERED_EXPENSE = "RegisteredExpense"
    UNREGISTERED_EXPENSE = "UnregisteredExpense"
    RCM_EXPENSE = "RCMExpense"
    EXEMPT_EXPENSE = "ExemptExpense"
    NON_GST_EXPENSE = "NonGSTExpense"
    TAX_ADJUSTMENT = "TaxAdjustment"
    ADVANCE_PAYMENT = "AdvancePayment"
    TDS_PAYMENT = "TDSPayment"
    TCS_PAYMENT = "TCSPayment"
    RCM_PAYMENT = "RCMPayment"
    PAYMENT_TO_GOVERNMENT = "PaymentToGovernment"


class TransactionStatus:
    DRAFT = "Draft"
    POSTED = "Posted"
    APPROVED = "Approved"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class PaymentStatusType:
    PENDING = "Pending"
    PAID = "Paid"
    PARTIAL = "Partial"
    CREDIT = "Credit"


class TransactionLedgerType:
    DEBIT = "Debit"
    CREDIT = "Credit"


class RechargePeriod:
    DAILY = 0
    MONTHLY = 1
    QUARTERLY = 3
    HALF_YEARLY = 6
    YEARLY = 12


class RechargeStatus:
    PENDING = 0
    PAID = 1
    EXPIRED = 2
    CANCELLED = 3


# ─── SQL Table Definitions ──────────────────────────────────────────────────

TABLES_SQL = """

-- ─── Company ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS company (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    name TEXT NOT NULL DEFAULT '',
    address TEXT DEFAULT '',
    city TEXT DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    state_code TEXT NOT NULL DEFAULT '',
    gstin TEXT NOT NULL DEFAULT '',
    zip_code TEXT DEFAULT '',
    country TEXT NOT NULL DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    website TEXT DEFAULT '',
    tax_id TEXT DEFAULT '',
    logo_url TEXT NOT NULL DEFAULT '',
    currency TEXT NOT NULL DEFAULT 'INR',
    starting_financial_year_date TEXT,

    bank_name TEXT,
    account_number TEXT,
    ifsc_code TEXT,
    account_holder_name TEXT,
    branch_name TEXT,
    swift_code TEXT,

    terms_and_conditions TEXT,

    billing_address TEXT,
    billing_city TEXT,
    billing_state TEXT,
    billing_state_code TEXT,
    billing_zip_code TEXT,
    billing_country TEXT
);

-- ─── Financial Year ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS financial_year (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    company_id TEXT NOT NULL,
    year_label TEXT NOT NULL DEFAULT '',
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,

    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Company Feature ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS company_feature (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    code TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT '',
    is_system_feature INTEGER DEFAULT 0,
    is_enabled INTEGER DEFAULT 1,
    created_on TEXT NOT NULL
);

-- ─── Company Role ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS company_role (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    is_system_role INTEGER DEFAULT 0,
    created_on TEXT NOT NULL,
    modified_on TEXT,

    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Company Role Feature ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS company_role_feature (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    feature_id TEXT NOT NULL,
    company_id TEXT NOT NULL,
    can_create INTEGER DEFAULT 0,
    can_read INTEGER DEFAULT 0,
    can_update INTEGER DEFAULT 0,
    can_delete INTEGER DEFAULT 0,
    can_authorize INTEGER DEFAULT 0,
    created_on TEXT NOT NULL,

    FOREIGN KEY (role_id) REFERENCES company_role(id),
    FOREIGN KEY (feature_id) REFERENCES company_feature(id)
);

-- ─── User Company Role Feature ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_company_role_feature (
    id TEXT PRIMARY KEY,
    company_role_feature_id TEXT NOT NULL,
    user_company_id TEXT NOT NULL,
    created_on TEXT NOT NULL,

    FOREIGN KEY (company_role_feature_id) REFERENCES company_role_feature(id),
    FOREIGN KEY (user_company_id) REFERENCES user_company(id)
);

-- ─── User Company ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_company (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    company_id TEXT NOT NULL,
    role_id TEXT,
    role TEXT,

    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (role_id) REFERENCES company_role(id)
);

-- ─── Company Recharge ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS company_recharge (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    company_id TEXT NOT NULL,
    amount REAL NOT NULL,
    period INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    recharge_status INTEGER NOT NULL,
    description TEXT,
    transaction_id TEXT,
    payment_method TEXT,
    paid_on TEXT,
    paid_by TEXT,
    is_active INTEGER DEFAULT 1,

    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Ledger ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ledger (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    name TEXT NOT NULL DEFAULT '',
    type TEXT NOT NULL DEFAULT '',
    root_category TEXT NOT NULL DEFAULT '',
    code TEXT DEFAULT '',
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    tax_id TEXT,
    is_group INTEGER DEFAULT 0,
    is_registered INTEGER,

    tax_class TEXT,
    tax_rate REAL,
    is_credit_allowed INTEGER DEFAULT 0,
    description TEXT,
    return_form_number TEXT,
    tax_entity_id TEXT,
    receivable_ledger_id TEXT,
    payable_ledger_id TEXT,

    account_holder_name TEXT,
    account_number TEXT,
    bank_name TEXT,
    branch TEXT,
    ifsc_code TEXT,

    parent_id TEXT,
    company_id TEXT NOT NULL,

    FOREIGN KEY (parent_id) REFERENCES ledger(id),
    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (tax_entity_id) REFERENCES tax(id)
);

-- ─── Ledger Opening Balance ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ledger_opening_balance (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    ledger_id TEXT NOT NULL,
    financial_year_id TEXT NOT NULL,
    opening_date TEXT NOT NULL,
    opening_balance REAL NOT NULL,
    balance_type TEXT NOT NULL DEFAULT '',

    FOREIGN KEY (ledger_id) REFERENCES ledger(id),
    FOREIGN KEY (financial_year_id) REFERENCES financial_year(id)
);

-- ─── Tax ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tax (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    is_composite INTEGER DEFAULT 0,
    default_rate REAL NOT NULL DEFAULT 0,
    hsn_code TEXT,
    section_code TEXT,
    is_reverse_charge_applicable INTEGER DEFAULT 0,
    is_deductible_at_source INTEGER DEFAULT 0,
    is_collected_at_source INTEGER DEFAULT 0,
    return_form_number TEXT,
    company_id TEXT NOT NULL,

    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Tax Component ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tax_component (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    type TEXT NOT NULL,
    rate REAL NOT NULL DEFAULT 0,
    ledger_code TEXT NOT NULL DEFAULT '',
    is_credit_allowed INTEGER DEFAULT 0,
    return_form_number TEXT,
    tax_id TEXT NOT NULL,
    ledger_id TEXT NOT NULL,
    receivable_ledger_id TEXT,
    payable_ledger_id TEXT,
    is_active INTEGER DEFAULT 1,

    FOREIGN KEY (tax_id) REFERENCES tax(id),
    FOREIGN KEY (ledger_id) REFERENCES ledger(id)
);

-- ─── Tax Rate ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tax_rate (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    tax_id TEXT NOT NULL,
    rate REAL NOT NULL DEFAULT 0,
    name TEXT NOT NULL DEFAULT '',
    hsn_code TEXT,
    min_amount REAL,
    max_amount REAL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    is_active INTEGER DEFAULT 1,

    FOREIGN KEY (tax_id) REFERENCES tax(id)
);

-- ─── Attribute ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attribute (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    is_required INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    company_id TEXT NOT NULL,

    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Attribute Option ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attribute_option (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    value TEXT NOT NULL DEFAULT '',
    display_name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    is_active INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    attribute_id TEXT NOT NULL,
    company_id TEXT NOT NULL,

    FOREIGN KEY (attribute_id) REFERENCES attribute(id),
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Product ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS product (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    product_code TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    purchase_price REAL NOT NULL DEFAULT 0,
    selling_price REAL NOT NULL DEFAULT 0,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER DEFAULT 0,
    sku TEXT NOT NULL DEFAULT '',
    barcode TEXT NOT NULL DEFAULT '',
    unit TEXT NOT NULL DEFAULT '',
    parent_id TEXT,
    company_id TEXT NOT NULL,

    FOREIGN KEY (parent_id) REFERENCES product(id),
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Product Attribute ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS product_attribute (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    product_id TEXT NOT NULL,
    attribute_id TEXT NOT NULL,
    company_id TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,

    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (attribute_id) REFERENCES attribute(id),
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Product Variant ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS product_variant (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    variant_code TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    purchase_price REAL NOT NULL DEFAULT 0,
    selling_price REAL NOT NULL DEFAULT 0,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    min_stock_level INTEGER NOT NULL DEFAULT 0,
    max_stock_level INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    sku TEXT NOT NULL DEFAULT '',
    barcode TEXT NOT NULL DEFAULT '',
    weight REAL NOT NULL DEFAULT 0,
    unit TEXT NOT NULL DEFAULT '',
    image_url TEXT NOT NULL DEFAULT '',
    sort_order INTEGER DEFAULT 0,
    product_id TEXT NOT NULL,
    company_id TEXT NOT NULL,

    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Product Variant Attribute ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS product_variant_attribute (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    product_variant_id TEXT NOT NULL,
    attribute_id TEXT NOT NULL,
    attribute_option_id TEXT NOT NULL,
    company_id TEXT NOT NULL,
    custom_value TEXT NOT NULL DEFAULT '',
    is_active INTEGER DEFAULT 1,

    FOREIGN KEY (product_variant_id) REFERENCES product_variant(id),
    FOREIGN KEY (attribute_id) REFERENCES attribute(id),
    FOREIGN KEY (attribute_option_id) REFERENCES attribute_option(id),
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Product Opening Stock ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS product_opening_stock (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    product_id TEXT NOT NULL,
    financial_year_id TEXT NOT NULL,
    opening_date TEXT NOT NULL,
    quantity REAL NOT NULL DEFAULT 0,
    rate REAL NOT NULL DEFAULT 0,
    value_amount REAL NOT NULL DEFAULT 0,

    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (financial_year_id) REFERENCES financial_year(id)
);

-- ─── Transaction ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "transaction" (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    transaction_number TEXT NOT NULL DEFAULT '',
    invoice_number TEXT,
    transaction_date TEXT NOT NULL,
    form_type TEXT NOT NULL DEFAULT '',
    type TEXT NOT NULL,
    journal_entry_type TEXT,
    nature_of_transaction TEXT,
    due_date TEXT NOT NULL,
    notes TEXT,
    sub_total REAL NOT NULL DEFAULT 0,
    tax_rate REAL NOT NULL DEFAULT 0,
    tax_amount REAL NOT NULL DEFAULT 0,
    discount REAL NOT NULL DEFAULT 0,
    discount_amount REAL NOT NULL DEFAULT 0,
    freight REAL NOT NULL DEFAULT 0,
    is_freight_included INTEGER DEFAULT 0,
    round_off REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL DEFAULT 0,
    paid_amount REAL,
    is_paid INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Draft',
    payment_status TEXT NOT NULL DEFAULT 'Credit',
    reference_number TEXT,
    payment_method TEXT,
    is_paid_with_transaction INTEGER DEFAULT 0,
    company_id TEXT,
    financial_year_id TEXT,

    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (financial_year_id) REFERENCES financial_year(id)
);

-- ─── Transaction Ledger ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transaction_ledger (
    id TEXT PRIMARY KEY,
    serial_number INTEGER DEFAULT 0,
    transaction_id TEXT NOT NULL,
    ledger_id TEXT NOT NULL,
    type TEXT NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    description TEXT,
    is_main_entry INTEGER,
    is_system_entry INTEGER,

    FOREIGN KEY (transaction_id) REFERENCES "transaction"(id),
    FOREIGN KEY (ledger_id) REFERENCES ledger(id)
);

-- ─── Transaction Item ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transaction_item (
    id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    quantity REAL NOT NULL DEFAULT 0,
    unit_price REAL NOT NULL DEFAULT 0,
    tax_rate REAL NOT NULL DEFAULT 0,
    tax_amount REAL NOT NULL DEFAULT 0,
    discount_rate REAL NOT NULL DEFAULT 0,
    discount_amount REAL NOT NULL DEFAULT 0,
    line_total REAL NOT NULL DEFAULT 0,
    current_quantity REAL NOT NULL DEFAULT 0,
    serial_number INTEGER DEFAULT 0,
    system_quantity REAL,
    physical_quantity REAL,
    adjustment_reason TEXT,

    FOREIGN KEY (transaction_id) REFERENCES "transaction"(id),
    FOREIGN KEY (product_id) REFERENCES product(id)
);

-- ─── Transaction Item Variant ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transaction_item_variant (
    id TEXT PRIMARY KEY,
    transaction_item_id TEXT NOT NULL,
    product_variant_id TEXT NOT NULL,
    variant_code TEXT NOT NULL DEFAULT '',
    variant_name TEXT NOT NULL DEFAULT '',
    quantity REAL NOT NULL DEFAULT 0,
    unit_price REAL NOT NULL DEFAULT 0,
    selling_price REAL NOT NULL DEFAULT 0,
    current_quantity REAL NOT NULL DEFAULT 0,
    serial_number INTEGER DEFAULT 0,
    description TEXT,

    FOREIGN KEY (transaction_item_id) REFERENCES transaction_item(id),
    FOREIGN KEY (product_variant_id) REFERENCES product_variant(id)
);

-- ─── Transaction Tax ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transaction_tax (
    id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    tax_ledger_id TEXT NOT NULL,
    taxable_amount REAL NOT NULL DEFAULT 0,
    tax_amount REAL NOT NULL DEFAULT 0,
    calculation_method TEXT NOT NULL DEFAULT 'ItemSubtotal',
    is_applied INTEGER DEFAULT 0,
    applied_date TEXT,
    reference_number TEXT,
    description TEXT,
    serial_number INTEGER DEFAULT 0,

    FOREIGN KEY (transaction_id) REFERENCES "transaction"(id),
    FOREIGN KEY (tax_ledger_id) REFERENCES ledger(id)
);

-- ─── Transaction Payment ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transaction_payment (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    payment_transaction_id TEXT NOT NULL,
    invoice_transaction_id TEXT NOT NULL,
    payment_ledger_id TEXT,
    amount REAL NOT NULL DEFAULT 0,
    payment_date TEXT NOT NULL,
    payment_method TEXT,
    payment_gateway TEXT,
    transaction_utr_number TEXT,
    cheque_number TEXT,
    cheque_date TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,

    FOREIGN KEY (payment_transaction_id) REFERENCES "transaction"(id),
    FOREIGN KEY (invoice_transaction_id) REFERENCES "transaction"(id),
    FOREIGN KEY (payment_ledger_id) REFERENCES ledger(id)
);

-- ─── Transaction Link ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transaction_link (
    id TEXT PRIMARY KEY,
    from_transaction_id TEXT NOT NULL,
    to_transaction_id TEXT NOT NULL,
    linked_on TEXT NOT NULL,
    notes TEXT,

    FOREIGN KEY (from_transaction_id) REFERENCES "transaction"(id),
    FOREIGN KEY (to_transaction_id) REFERENCES "transaction"(id)
);

-- ─── Transaction Type Settings ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transaction_type_settings (
    id TEXT PRIMARY KEY,
    created_on TEXT NOT NULL,
    modified_on TEXT,
    created_by TEXT NOT NULL DEFAULT '',
    modified_by TEXT NOT NULL DEFAULT '',
    authorized INTEGER DEFAULT 0,
    authorized_by TEXT DEFAULT '',
    authorized_on TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_by TEXT DEFAULT '',
    deleted_on TEXT,
    row_version TEXT,

    company_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    auto_generate_invoice INTEGER DEFAULT 1,
    allow_duplicate_invoice_number INTEGER DEFAULT 0,
    show_billing_address INTEGER DEFAULT 1,
    show_shipping_address INTEGER DEFAULT 1,
    require_billing_address INTEGER DEFAULT 0,
    require_shipping_address INTEGER DEFAULT 0,
    invoice_number_prefix TEXT,
    invoice_number_suffix TEXT,
    invoice_number_length INTEGER DEFAULT 6,
    next_invoice_number INTEGER DEFAULT 1,
    copy_billing_to_shipping INTEGER DEFAULT 0,
    copy_shipping_to_billing INTEGER DEFAULT 0,

    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- ─── Indexes ────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_financial_year_company ON financial_year(company_id);
CREATE INDEX IF NOT EXISTS idx_ledger_company ON ledger(company_id);
CREATE INDEX IF NOT EXISTS idx_ledger_parent ON ledger(parent_id);
CREATE INDEX IF NOT EXISTS idx_ledger_type ON ledger(type);
CREATE INDEX IF NOT EXISTS idx_product_company ON product(company_id);
CREATE INDEX IF NOT EXISTS idx_product_parent ON product(parent_id);
CREATE INDEX IF NOT EXISTS idx_tax_company ON tax(company_id);
CREATE INDEX IF NOT EXISTS idx_tax_component_tax ON tax_component(tax_id);
CREATE INDEX IF NOT EXISTS idx_tax_rate_tax ON tax_rate(tax_id);
CREATE INDEX IF NOT EXISTS idx_transaction_company ON "transaction"(company_id);
CREATE INDEX IF NOT EXISTS idx_transaction_fy ON "transaction"(financial_year_id);
CREATE INDEX IF NOT EXISTS idx_transaction_type ON "transaction"(type);
CREATE INDEX IF NOT EXISTS idx_transaction_date ON "transaction"(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transaction_ledger_tx ON transaction_ledger(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_ledger_ledger ON transaction_ledger(ledger_id);
CREATE INDEX IF NOT EXISTS idx_transaction_item_tx ON transaction_item(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_tax_tx ON transaction_tax(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_payment_pay ON transaction_payment(payment_transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_payment_inv ON transaction_payment(invoice_transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_link_from ON transaction_link(from_transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_link_to ON transaction_link(to_transaction_id);
CREATE INDEX IF NOT EXISTS idx_attribute_company ON attribute(company_id);
CREATE INDEX IF NOT EXISTS idx_attribute_option_attr ON attribute_option(attribute_id);
CREATE INDEX IF NOT EXISTS idx_product_variant_product ON product_variant(product_id);
CREATE INDEX IF NOT EXISTS idx_product_attribute_product ON product_attribute(product_id);
CREATE INDEX IF NOT EXISTS idx_product_variant_attribute_variant ON product_variant_attribute(product_variant_id);
CREATE INDEX IF NOT EXISTS idx_ledger_opening_balance_ledger ON ledger_opening_balance(ledger_id);
CREATE INDEX IF NOT EXISTS idx_product_opening_stock_product ON product_opening_stock(product_id);
CREATE INDEX IF NOT EXISTS idx_transaction_type_settings_company ON transaction_type_settings(company_id);
CREATE INDEX IF NOT EXISTS idx_user_company_company ON user_company(company_id);
CREATE INDEX IF NOT EXISTS idx_company_role_company ON company_role(company_id);
CREATE INDEX IF NOT EXISTS idx_company_recharge_company ON company_recharge(company_id);
"""
