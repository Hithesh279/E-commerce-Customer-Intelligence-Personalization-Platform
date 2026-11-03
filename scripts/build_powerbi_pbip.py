"""
scripts/build_powerbi_pbip.py
Constructs a valid, fully articulated Power BI Project (.pbip) folder structure
with typed Power Query M transformations, Star-Schema relationships,
and rock-solid DAX measures.
"""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\hithe\Downloads\E-commerce Customer Intelligence & Personalization Platform")
POWERBI_DIR = PROJECT_ROOT / "powerbi"
DATA_EXPORT_DIR = PROJECT_ROOT / "data" / "powerbi_export"

PBIP_FILE = POWERBI_DIR / "Ecommerce_Customer_Intelligence.pbip"
REPORT_DIR = POWERBI_DIR / "Ecommerce_Customer_Intelligence.Report"
MODEL_DIR = POWERBI_DIR / "Ecommerce_Customer_Intelligence.SemanticModel"

def build_pbip():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Main .pbip file
    pbip_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "Ecommerce_Customer_Intelligence.Report"
                }
            }
        ],
        "settings": {
            "enableAutoRecovery": True
        }
    }
    with open(PBIP_FILE, "w", encoding="utf-8") as f:
        json.dump(pbip_data, f, indent=2)

    # 2. Report definition.pbir
    pbir_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
        "version": "1.0",
        "datasetReference": {
            "byPath": {
                "path": "../Ecommerce_Customer_Intelligence.SemanticModel"
            },
            "byConnection": None
        }
    }
    with open(REPORT_DIR / "definition.pbir", "w", encoding="utf-8") as f:
        json.dump(pbir_data, f, indent=2)

    # 3. SemanticModel definition.pbism
    pbism_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "1.0"
    }
    with open(MODEL_DIR / "definition.pbism", "w", encoding="utf-8") as f:
        json.dump(pbism_data, f, indent=2)

    # Helper for typed CSV M partition expression
    def csv_m_expr(filename, cols_count, type_pairs):
        csv_path_escaped = str((DATA_EXPORT_DIR / filename).resolve()).replace("\\", "\\\\")
        type_str = ", ".join([f'{{\"{col}\", {t}}}' for col, t in type_pairs])
        return [
            "let",
            f'    Source = Csv.Document(File.Contents("{csv_path_escaped}"), [Delimiter=",", Columns={cols_count}, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
            f'    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {{{type_str}}})',
            "in",
            '    #"Changed Type"'
        ]

    # Tables definition
    tables = [
        {
            "name": "DimCustomer",
            "columns": [
                {"name": "customer_id", "dataType": "string", "sourceColumn": "customer_id"},
                {"name": "gender", "dataType": "string", "sourceColumn": "gender"},
                {"name": "age", "dataType": "int64", "sourceColumn": "age"},
                {"name": "city", "dataType": "string", "sourceColumn": "city"},
                {"name": "country", "dataType": "string", "sourceColumn": "country"},
                {"name": "membership_type", "dataType": "string", "sourceColumn": "membership_type"},
                {"name": "signup_date", "dataType": "string", "sourceColumn": "signup_date"},
                {"name": "customer_segment", "dataType": "string", "sourceColumn": "customer_segment"},
                {"name": "preferred_category", "dataType": "string", "sourceColumn": "preferred_category"}
            ],
            "partitions": [
                {
                    "name": "DimCustomer-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": csv_m_expr("DimCustomer.csv", 9, [
                            ("customer_id", "type text"),
                            ("gender", "type text"),
                            ("age", "Int64.Type"),
                            ("city", "type text"),
                            ("country", "type text"),
                            ("membership_type", "type text"),
                            ("signup_date", "type text"),
                            ("customer_segment", "type text"),
                            ("preferred_category", "type text")
                        ])
                    }
                }
            ]
        },
        {
            "name": "DimProduct",
            "columns": [
                {"name": "product_id", "dataType": "string", "sourceColumn": "product_id"},
                {"name": "product_name", "dataType": "string", "sourceColumn": "product_name"},
                {"name": "category", "dataType": "string", "sourceColumn": "category"},
                {"name": "subcategory", "dataType": "string", "sourceColumn": "subcategory"},
                {"name": "brand", "dataType": "string", "sourceColumn": "brand"},
                {"name": "price", "dataType": "double", "sourceColumn": "price"}
            ],
            "partitions": [
                {
                    "name": "DimProduct-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": csv_m_expr("DimProduct.csv", 6, [
                            ("product_id", "type text"),
                            ("product_name", "type text"),
                            ("category", "type text"),
                            ("subcategory", "type text"),
                            ("brand", "type text"),
                            ("price", "type number")
                        ])
                    }
                }
            ]
        },
        {
            "name": "DimCategory",
            "columns": [
                {"name": "category", "dataType": "string", "sourceColumn": "category"},
                {"name": "subcategory_count", "dataType": "int64", "sourceColumn": "subcategory_count"},
                {"name": "product_count", "dataType": "int64", "sourceColumn": "product_count"},
                {"name": "avg_category_price", "dataType": "double", "sourceColumn": "avg_category_price"}
            ],
            "partitions": [
                {
                    "name": "DimCategory-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": csv_m_expr("DimCategory.csv", 4, [
                            ("category", "type text"),
                            ("subcategory_count", "Int64.Type"),
                            ("product_count", "Int64.Type"),
                            ("avg_category_price", "type number")
                        ])
                    }
                }
            ]
        },
        {
            "name": "DimDate",
            "columns": [
                {"name": "date_key", "dataType": "int64", "sourceColumn": "date_key"},
                {"name": "full_date", "dataType": "string", "sourceColumn": "full_date"},
                {"name": "year", "dataType": "int64", "sourceColumn": "year"},
                {"name": "month", "dataType": "int64", "sourceColumn": "month"},
                {"name": "month_name", "dataType": "string", "sourceColumn": "month_name"},
                {"name": "quarter", "dataType": "string", "sourceColumn": "quarter"},
                {"name": "day_of_week", "dataType": "string", "sourceColumn": "day_of_week"}
            ],
            "partitions": [
                {
                    "name": "DimDate-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": csv_m_expr("DimDate.csv", 7, [
                            ("date_key", "Int64.Type"),
                            ("full_date", "type text"),
                            ("year", "Int64.Type"),
                            ("month", "Int64.Type"),
                            ("month_name", "type text"),
                            ("quarter", "type text"),
                            ("day_of_week", "type text")
                        ])
                    }
                }
            ]
        },
        {
            "name": "FactSales",
            "columns": [
                {"name": "transaction_id", "dataType": "string", "sourceColumn": "transaction_id"},
                {"name": "customer_id", "dataType": "string", "sourceColumn": "customer_id"},
                {"name": "product_id", "dataType": "string", "sourceColumn": "product_id"},
                {"name": "date_key", "dataType": "int64", "sourceColumn": "date_key"},
                {"name": "transaction_date", "dataType": "string", "sourceColumn": "transaction_date"},
                {"name": "quantity", "dataType": "int64", "sourceColumn": "quantity"},
                {"name": "unit_price", "dataType": "double", "sourceColumn": "unit_price"},
                {"name": "discount_percentage", "dataType": "double", "sourceColumn": "discount_percentage"},
                {"name": "discount_amount", "dataType": "double", "sourceColumn": "discount_amount"},
                {"name": "total_amount", "dataType": "double", "sourceColumn": "total_amount"},
                {"name": "payment_method", "dataType": "string", "sourceColumn": "payment_method"},
                {"name": "return_status", "dataType": "string", "sourceColumn": "return_status"},
                {"name": "is_returned", "dataType": "int64", "sourceColumn": "is_returned"},
                {"name": "net_sales_amount", "dataType": "double", "sourceColumn": "net_sales_amount"}
            ],
            "partitions": [
                {
                    "name": "FactSales-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": csv_m_expr("FactSales.csv", 14, [
                            ("transaction_id", "type text"),
                            ("customer_id", "type text"),
                            ("product_id", "type text"),
                            ("date_key", "Int64.Type"),
                            ("transaction_date", "type text"),
                            ("quantity", "Int64.Type"),
                            ("unit_price", "type number"),
                            ("discount_percentage", "type number"),
                            ("discount_amount", "type number"),
                            ("total_amount", "type number"),
                            ("payment_method", "type text"),
                            ("return_status", "type text"),
                            ("is_returned", "Int64.Type"),
                            ("net_sales_amount", "type number")
                        ])
                    }
                }
            ]
        },
        {
            "name": "FactReviews",
            "columns": [
                {"name": "review_id", "dataType": "string", "sourceColumn": "review_id"},
                {"name": "customer_id", "dataType": "string", "sourceColumn": "customer_id"},
                {"name": "product_id", "dataType": "string", "sourceColumn": "product_id"},
                {"name": "date_key", "dataType": "int64", "sourceColumn": "date_key"},
                {"name": "review_date", "dataType": "string", "sourceColumn": "review_date"},
                {"name": "rating", "dataType": "int64", "sourceColumn": "rating"},
                {"name": "sentiment", "dataType": "string", "sourceColumn": "sentiment"},
                {"name": "review_text", "dataType": "string", "sourceColumn": "review_text"}
            ],
            "partitions": [
                {
                    "name": "FactReviews-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": csv_m_expr("FactReviews.csv", 8, [
                            ("review_id", "type text"),
                            ("customer_id", "type text"),
                            ("product_id", "type text"),
                            ("date_key", "Int64.Type"),
                            ("review_date", "type text"),
                            ("rating", "Int64.Type"),
                            ("sentiment", "type text"),
                            ("review_text", "type text")
                        ])
                    }
                }
            ]
        },
        {
            "name": "FactInteractions",
            "columns": [
                {"name": "interaction_id", "dataType": "string", "sourceColumn": "interaction_id"},
                {"name": "customer_id", "dataType": "string", "sourceColumn": "customer_id"},
                {"name": "product_id", "dataType": "string", "sourceColumn": "product_id"},
                {"name": "date_key", "dataType": "int64", "sourceColumn": "date_key"},
                {"name": "timestamp", "dataType": "string", "sourceColumn": "timestamp"},
                {"name": "interaction_type", "dataType": "string", "sourceColumn": "interaction_type"},
                {"name": "interaction_weight", "dataType": "double", "sourceColumn": "interaction_weight"},
                {"name": "session_id", "dataType": "string", "sourceColumn": "session_id"}
            ],
            "partitions": [
                {
                    "name": "FactInteractions-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": csv_m_expr("FactInteractions.csv", 8, [
                            ("interaction_id", "type text"),
                            ("customer_id", "type text"),
                            ("product_id", "type text"),
                            ("date_key", "Int64.Type"),
                            ("timestamp", "type text"),
                            ("interaction_type", "type text"),
                            ("interaction_weight", "type number"),
                            ("session_id", "type text")
                        ])
                    }
                }
            ]
        },
        {
            "name": "_Measures",
            "columns": [
                {"name": "MeasureHolder", "dataType": "string", "sourceColumn": "MeasureHolder"}
            ],
            "partitions": [
                {
                    "name": "_Measures-Partition",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            '    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [MeasureHolder = _t])',
                            "in",
                            "    Source"
                        ]
                    }
                }
            ],
            "measures": [
                {
                    "name": "Total Gross Revenue",
                    "expression": "SUM(FactSales[total_amount])",
                    "formatString": "\\$#,##0.00"
                },
                {
                    "name": "Total Net Revenue",
                    "expression": "SUM(FactSales[net_sales_amount])",
                    "formatString": "\\$#,##0.00"
                },
                {
                    "name": "Total Orders",
                    "expression": "DISTINCTCOUNT(FactSales[transaction_id])",
                    "formatString": "#,##0"
                },
                {
                    "name": "Total Customers",
                    "expression": "DISTINCTCOUNT(DimCustomer[customer_id])",
                    "formatString": "#,##0"
                },
                {
                    "name": "Active Purchasing Customers",
                    "expression": "CALCULATE(DISTINCTCOUNT(FactSales[customer_id]), FactSales[return_status] <> \"Returned\")",
                    "formatString": "#,##0"
                },
                {
                    "name": "Average Order Value",
                    "expression": "DIVIDE([Total Net Revenue], [Total Orders], 0)",
                    "formatString": "\\$#,##0.00"
                },
                {
                    "name": "Return Rate %",
                    "expression": "DIVIDE(CALCULATE(COUNTROWS(FactSales), FactSales[return_status] = \"Returned\"), COUNTROWS(FactSales), 0)",
                    "formatString": "0.0%"
                },
                {
                    "name": "Net Sentiment Score",
                    "expression": "VAR TotalRev = COUNTROWS(FactReviews) VAR PosRev = CALCULATE(COUNTROWS(FactReviews), FactReviews[sentiment] = \"Positive\") VAR NegRev = CALCULATE(COUNTROWS(FactReviews), FactReviews[sentiment] = \"Negative\") RETURN DIVIDE(PosRev - NegRev, TotalRev, 0)",
                    "formatString": "+0.0%;-0.0%;0.0%"
                },
                {
                    "name": "Positive Review Share %",
                    "expression": "DIVIDE(CALCULATE(COUNTROWS(FactReviews), FactReviews[sentiment] = \"Positive\"), COUNTROWS(FactReviews), 0)",
                    "formatString": "0.0%"
                },
                {
                    "name": "Negative Review Share %",
                    "expression": "DIVIDE(CALCULATE(COUNTROWS(FactReviews), FactReviews[sentiment] = \"Negative\"), COUNTROWS(FactReviews), 0)",
                    "formatString": "0.0%"
                },
                {
                    "name": "Review Volume",
                    "expression": "COUNTROWS(FactReviews)",
                    "formatString": "#,##0"
                },
                {
                    "name": "Customer Lifetime Value",
                    "expression": "DIVIDE([Total Net Revenue], DISTINCTCOUNT(FactSales[customer_id]), 0)",
                    "formatString": "\\$#,##0.00"
                },
                {
                    "name": "Repeat Purchase Rate %",
                    "expression": "VAR CustCounts = ADDCOLUMNS(VALUES(FactSales[customer_id]), \"Orders\", CALCULATE(DISTINCTCOUNT(FactSales[transaction_id]), FactSales[return_status] <> \"Returned\")) VAR RepeatCust = COUNTROWS(FILTER(CustCounts, [Orders] >= 2)) VAR TotalCust = COUNTROWS(FILTER(CustCounts, [Orders] >= 1)) RETURN DIVIDE(RepeatCust, TotalCust, 0)",
                    "formatString": "0.0%"
                },
                {
                    "name": "High Sales Low Sentiment Risk SKU Count",
                    "expression": "CALCULATE(DISTINCTCOUNT(DimProduct[product_id]), FILTER(DimProduct, CALCULATE(SUM(FactSales[quantity])) >= 10 && CALCULATE(AVERAGE(FactReviews[rating])) < 3.2))",
                    "formatString": "#,##0"
                }
            ]
        }
    ]

    relationships = [
        {
            "name": "FactSales_DimCustomer",
            "fromTable": "FactSales",
            "fromColumn": "customer_id",
            "toTable": "DimCustomer",
            "toColumn": "customer_id"
        },
        {
            "name": "FactSales_DimProduct",
            "fromTable": "FactSales",
            "fromColumn": "product_id",
            "toTable": "DimProduct",
            "toColumn": "product_id"
        },
        {
            "name": "FactSales_DimDate",
            "fromTable": "FactSales",
            "fromColumn": "date_key",
            "toTable": "DimDate",
            "toColumn": "date_key"
        },
        {
            "name": "FactReviews_DimCustomer",
            "fromTable": "FactReviews",
            "fromColumn": "customer_id",
            "toTable": "DimCustomer",
            "toColumn": "customer_id"
        },
        {
            "name": "FactReviews_DimProduct",
            "fromTable": "FactReviews",
            "fromColumn": "product_id",
            "toTable": "DimProduct",
            "toColumn": "product_id"
        },
        {
            "name": "FactReviews_DimDate",
            "fromTable": "FactReviews",
            "fromColumn": "date_key",
            "toTable": "DimDate",
            "toColumn": "date_key"
        },
        {
            "name": "FactInteractions_DimCustomer",
            "fromTable": "FactInteractions",
            "fromColumn": "customer_id",
            "toTable": "DimCustomer",
            "toColumn": "customer_id"
        },
        {
            "name": "FactInteractions_DimProduct",
            "fromTable": "FactInteractions",
            "fromColumn": "product_id",
            "toTable": "DimProduct",
            "toColumn": "product_id"
        },
        {
            "name": "FactInteractions_DimDate",
            "fromTable": "FactInteractions",
            "fromColumn": "date_key",
            "toTable": "DimDate",
            "toColumn": "date_key"
        },
        {
            "name": "DimProduct_DimCategory",
            "fromTable": "DimProduct",
            "fromColumn": "category",
            "toTable": "DimCategory",
            "toColumn": "category"
        }
    ]

    model_bim = {
        "name": "Ecommerce_Customer_Intelligence",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "tables": tables,
            "relationships": relationships
        }
    }

    with open(MODEL_DIR / "model.bim", "w", encoding="utf-8") as f:
        json.dump(model_bim, f, indent=2)

    print("Power BI Project (.pbip) semantic model updated successfully at:", PBIP_FILE)

if __name__ == "__main__":
    build_pbip()
