"""Application configuration.

Keep environment-sensitive values (credentials, API keys) out of this module —
load them from the environment when Phase 2 introduces real integrations.
"""


class AppConfig:
    business_name_default = "SwiftPOS"
    currency_default = "UGX"
    low_stock_default = 5
    vat_rate_default = 0
    use_demo_sales = True  # Switch to False once checkout/POS reporting is live


config = AppConfig()