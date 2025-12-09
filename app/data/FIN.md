## FIN – عقود التمويل / التمويل الإسلامي / المصرفية

```text
FIN
│
├── spec.FIN.facility_and_limit
│     ├── spec.FIN.facility.type   (مرابحة، قرض، تسهيل ائتماني...)
│     ├── spec.FIN.facility.limit_and_drawdown
│     └── spec.FIN.facility.purpose
│
├── spec.FIN.pricing_and_profit
│     ├── spec.FIN.pricing.interest_or_profit_rate
│     ├── spec.FIN.pricing.fees_and_charges
│     └── spec.FIN.pricing.repricing_or_review
│
├── spec.FIN.repayment_and_prepayment
│     ├── spec.FIN.repayment.schedule
│     ├── spec.FIN.repayment.prepayment_rights
│     └── spec.FIN.repayment.prepayment_fees
│
├── spec.FIN.security_and_guarantees
│     ├── spec.FIN.security.collateral_description
│     ├── spec.FIN.security.perfection_and_ranking
│     └── spec.FIN.security.guarantees_and_support
│
├── spec.FIN.representations_and_covenants
│     ├── spec.FIN.rep.borrower_representations
│     ├── spec.FIN.rep.financial_covenants
│     └── spec.FIN.rep.information_covenants
│
├── spec.FIN.events_of_default
│     ├── spec.FIN.eod.payment_default
│     ├── spec.FIN.eod.insolvency
│     ├── spec.FIN.eod.breach_of_covenants
│     └── spec.FIN.eod.cross_default
│
├── spec.FIN.islamic_specifics
│     ├── spec.FIN.islamic.asset_purchase_and_sale   (مرابحة)
│     ├── spec.FIN.islamic.ijara_terms
│     └── spec.FIN.islamic.sharia_board_approval
│
└── spec.FIN.mitigation_and_remedies
       ├── spec.FIN.mitigation.acceleration
       ├── spec.FIN.mitigation.setoff
       └── spec.FIN.mitigation.restructuring_options

```