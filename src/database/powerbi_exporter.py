"""
src/database/powerbi_exporter.py
Automated Power BI Project (.pbip) Generator.
Generates a complete, publication-grade Power BI dashboard project including
semantic models (model.bim), typed Power Query M partitions, Star-Schema relationships,
16 DAX measures, and all 30 visual containers (KPI cards, bar charts, donut charts, tables)
matching whatever data is currently active in the platform.
"""

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.utils.config import POWERBI_DATA_DIR, PROJECT_ROOT

logger = logging.getLogger("powerbi_exporter")


def _make_card_container(measure_name: str, x: float, y: float, width: float, height: float, z: int = 1000) -> Dict[str, Any]:
    vis_id = str(uuid.uuid4())
    config_dict = {
        "name": vis_id,
        "layouts": [
            {
                "id": 0,
                "position": {
                    "x": float(x),
                    "y": float(y),
                    "z": float(z),
                    "width": float(width),
                    "height": float(height),
                    "tabOrder": z
                }
            }
        ],
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [
                    {
                        "queryRef": f"_Measures.{measure_name}"
                    }
                ]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {
                        "Name": "m",
                        "Entity": "_Measures",
                        "Type": 0
                    }
                ],
                "Select": [
                    {
                        "Measure": {
                            "Expression": {
                                "SourceRef": {
                                    "Source": "m"
                                }
                            },
                            "Property": measure_name
                        },
                        "Name": f"_Measures.{measure_name}",
                        "NativeReferenceName": measure_name
                    }
                ]
            },
            "drillFilterOtherVisuals": True,
            "hasDefaultSort": True
        }
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": float(z),
        "width": float(width),
        "height": float(height),
        "config": json.dumps(config_dict)
    }


def _make_bar_chart(category_entity: str, category_col: str, measure_name: str, x: float, y: float, width: float, height: float, z: int = 2000) -> Dict[str, Any]:
    vis_id = str(uuid.uuid4())
    config_dict = {
        "name": vis_id,
        "layouts": [
            {
                "id": 0,
                "position": {
                    "x": float(x),
                    "y": float(y),
                    "z": float(z),
                    "width": float(width),
                    "height": float(height),
                    "tabOrder": z
                }
            }
        ],
        "singleVisual": {
            "visualType": "barChart",
            "projections": {
                "Category": [
                    {
                        "queryRef": f"{category_entity}.{category_col}",
                        "active": True
                    }
                ],
                "Y": [
                    {
                        "queryRef": f"_Measures.{measure_name}"
                    }
                ]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {
                        "Name": "c",
                        "Entity": category_entity,
                        "Type": 0
                    },
                    {
                        "Name": "m",
                        "Entity": "_Measures",
                        "Type": 0
                    }
                ],
                "Select": [
                    {
                        "Column": {
                            "Expression": {
                                "SourceRef": {
                                    "Source": "c"
                                }
                            },
                            "Property": category_col
                        },
                        "Name": f"{category_entity}.{category_col}",
                        "NativeReferenceName": category_col
                    },
                    {
                        "Measure": {
                            "Expression": {
                                "SourceRef": {
                                    "Source": "m"
                                }
                            },
                            "Property": measure_name
                        },
                        "Name": f"_Measures.{measure_name}",
                        "NativeReferenceName": measure_name
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": float(z),
        "width": float(width),
        "height": float(height),
        "config": json.dumps(config_dict)
    }


def _make_donut_chart(category_entity: str, category_col: str, measure_name: str, x: float, y: float, width: float, height: float, z: int = 3000) -> Dict[str, Any]:
    vis_id = str(uuid.uuid4())
    config_dict = {
        "name": vis_id,
        "layouts": [
            {
                "id": 0,
                "position": {
                    "x": float(x),
                    "y": float(y),
                    "z": float(z),
                    "width": float(width),
                    "height": float(height),
                    "tabOrder": z
                }
            }
        ],
        "singleVisual": {
            "visualType": "donutChart",
            "projections": {
                "Category": [
                    {
                        "queryRef": f"{category_entity}.{category_col}",
                        "active": True
                    }
                ],
                "Y": [
                    {
                        "queryRef": f"_Measures.{measure_name}"
                    }
                ]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {
                        "Name": "c",
                        "Entity": category_entity,
                        "Type": 0
                    },
                    {
                        "Name": "m",
                        "Entity": "_Measures",
                        "Type": 0
                    }
                ],
                "Select": [
                    {
                        "Column": {
                            "Expression": {
                                "SourceRef": {
                                    "Source": "c"
                                }
                            },
                            "Property": category_col
                        },
                        "Name": f"{category_entity}.{category_col}",
                        "NativeReferenceName": category_col
                    },
                    {
                        "Measure": {
                            "Expression": {
                                "SourceRef": {
                                    "Source": "m"
                                }
                            },
                            "Property": measure_name
                        },
                        "Name": f"_Measures.{measure_name}",
                        "NativeReferenceName": measure_name
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": float(z),
        "width": float(width),
        "height": float(height),
        "config": json.dumps(config_dict)
    }


def _make_table_visual(cols_measures: List[Tuple[str, str, bool]], x: float, y: float, width: float, height: float, z: int = 4000) -> Dict[str, Any]:
    vis_id = str(uuid.uuid4())
    projections = []
    selects = []
    from_map = {}

    for item in cols_measures:
        entity, prop, _ = item
        if entity not in from_map:
            alias = f"src_{len(from_map)}"
            from_map[entity] = alias

    from_list = [{"Name": alias, "Entity": entity, "Type": 0} for entity, alias in from_map.items()]

    for item in cols_measures:
        entity, prop, is_meas = item
        alias = from_map[entity]
        query_ref = f"{entity}.{prop}"
        projections.append({"queryRef": query_ref})
        if is_meas:
            selects.append({
                "Measure": {
                    "Expression": {
                        "SourceRef": {
                            "Source": alias
                        }
                    },
                    "Property": prop
                },
                "Name": query_ref,
                "NativeReferenceName": prop
            })
        else:
            selects.append({
                "Column": {
                    "Expression": {
                        "SourceRef": {
                            "Source": alias
                        }
                    },
                    "Property": prop
                },
                "Name": query_ref,
                "NativeReferenceName": prop
            })

    config_dict = {
        "name": vis_id,
        "layouts": [
            {
                "id": 0,
                "position": {
                    "x": float(x),
                    "y": float(y),
                    "z": float(z),
                    "width": float(width),
                    "height": float(height),
                    "tabOrder": z
                }
            }
        ],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": {
                "Values": projections
            },
            "prototypeQuery": {
                "Version": 2,
                "From": from_list,
                "Select": selects
            },
            "drillFilterOtherVisuals": True
        }
    }
    return {
        "x": float(x),
        "y": float(y),
        "z": float(z),
        "width": float(width),
        "height": float(height),
        "config": json.dumps(config_dict)
    }


def generate_complete_powerbi_pbip_project(data_dir: Optional[Path] = None, output_dir: Optional[Path] = None) -> Path:
    """
    Generate or update a complete Power BI Project (.pbip) folder matching the active dataset.
    Writes:
      - Ecommerce_Customer_Intelligence.pbip
      - Ecommerce_Customer_Intelligence.Report/definition.pbir & report.json (with 30 visual containers)
      - Ecommerce_Customer_Intelligence.SemanticModel/definition.pbism & model.bim (typed tables & measures)
    """
    data_dir = Path(data_dir or POWERBI_DATA_DIR).resolve()
    output_dir = Path(output_dir or (PROJECT_ROOT / "powerbi")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    report_dir = output_dir / "Ecommerce_Customer_Intelligence.Report"
    model_dir = output_dir / "Ecommerce_Customer_Intelligence.SemanticModel"
    pbip_file = output_dir / "Ecommerce_Customer_Intelligence.pbip"

    report_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

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
    with open(pbip_file, "w", encoding="utf-8") as f:
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
    with open(report_dir / "definition.pbir", "w", encoding="utf-8") as f:
        json.dump(pbir_data, f, indent=2)

    # 3. SemanticModel definition.pbism
    pbism_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "1.0"
    }
    with open(model_dir / "definition.pbism", "w", encoding="utf-8") as f:
        json.dump(pbism_data, f, indent=2)

    # Helper for typed CSV M partition expression
    def csv_m_expr(filename: str, cols_count: int, type_pairs: List[Tuple[str, str]]) -> List[str]:
        csv_path_escaped = str((data_dir / filename).resolve()).replace("\\", "\\\\")
        type_str = ", ".join([f'{{\"{col}\", {t}}}' for col, t in type_pairs])
        return [
            "let",
            f'    Source = Csv.Document(File.Contents("{csv_path_escaped}"), [Delimiter=",", Columns={cols_count}, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
            '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
            f'    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {{{type_str}}})',
            "in",
            '    #"Changed Type"'
        ]

    # Tables definition with strict typed columns matching Star Schema
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

    with open(model_dir / "model.bim", "w", encoding="utf-8") as f:
        json.dump(model_bim, f, indent=2)

    # 4. Generate all 30 visual containers across all 5 report pages
    p1_visuals = [
        _make_card_container("Total Net Revenue", x=20, y=20, width=230, height=100, z=1000),
        _make_card_container("Total Orders", x=270, y=20, width=230, height=100, z=1100),
        _make_card_container("Average Order Value", x=520, y=20, width=230, height=100, z=1200),
        _make_card_container("Return Rate %", x=770, y=20, width=230, height=100, z=1300),
        _make_card_container("Net Sentiment Score", x=1020, y=20, width=230, height=100, z=1400),
        _make_bar_chart("DimProduct", "category", "Total Net Revenue", x=20, y=140, width=600, height=270, z=2000),
        _make_donut_chart("DimCustomer", "customer_segment", "Total Customers", x=640, y=140, width=610, height=270, z=2100),
        _make_table_visual([
            ("DimProduct", "product_name", False),
            ("DimProduct", "category", False),
            ("_Measures", "Total Net Revenue", True),
            ("_Measures", "Return Rate %", True)
        ], x=20, y=430, width=1230, height=260, z=3000)
    ]

    p2_visuals = [
        _make_card_container("Total Customers", x=20, y=20, width=290, height=100, z=1000),
        _make_card_container("Active Purchasing Customers", x=330, y=20, width=290, height=100, z=1100),
        _make_card_container("Customer Lifetime Value", x=640, y=20, width=290, height=100, z=1200),
        _make_card_container("Repeat Purchase Rate %", x=950, y=20, width=290, height=100, z=1300),
        _make_bar_chart("DimCustomer", "customer_segment", "Total Net Revenue", x=20, y=140, width=600, height=550, z=2000),
        _make_table_visual([
            ("DimCustomer", "customer_id", False),
            ("DimCustomer", "customer_segment", False),
            ("DimCustomer", "membership_type", False),
            ("DimCustomer", "city", False),
            ("_Measures", "Total Net Revenue", True)
        ], x=640, y=140, width=610, height=550, z=3000)
    ]

    p3_visuals = [
        _make_card_container("High Sales Low Sentiment Risk SKU Count", x=20, y=20, width=380, height=100, z=1000),
        _make_card_container("Return Rate %", x=430, y=20, width=380, height=100, z=1100),
        _make_card_container("Total Net Revenue", x=840, y=20, width=410, height=100, z=1200),
        _make_bar_chart("DimProduct", "brand", "Total Net Revenue", x=20, y=140, width=580, height=550, z=2000),
        _make_table_visual([
            ("DimProduct", "product_name", False),
            ("DimProduct", "category", False),
            ("DimProduct", "brand", False),
            ("_Measures", "Total Net Revenue", True),
            ("_Measures", "Return Rate %", True)
        ], x=620, y=140, width=630, height=550, z=3000)
    ]

    p4_visuals = [
        _make_card_container("Review Volume", x=20, y=20, width=290, height=100, z=1000),
        _make_card_container("Positive Review Share %", x=330, y=20, width=290, height=100, z=1100),
        _make_card_container("Negative Review Share %", x=640, y=20, width=290, height=100, z=1200),
        _make_card_container("Net Sentiment Score", x=950, y=20, width=290, height=100, z=1300),
        _make_donut_chart("FactReviews", "sentiment", "Review Volume", x=20, y=140, width=500, height=550, z=2000),
        _make_table_visual([
            ("FactReviews", "review_id", False),
            ("FactReviews", "product_id", False),
            ("FactReviews", "rating", False),
            ("FactReviews", "sentiment", False),
            ("FactReviews", "review_text", False)
        ], x=540, y=140, width=710, height=550, z=3000)
    ]

    p5_visuals = [
        _make_card_container("Total Orders", x=20, y=20, width=380, height=100, z=1000),
        _make_card_container("Active Purchasing Customers", x=430, y=20, width=380, height=100, z=1100),
        _make_card_container("Total Net Revenue", x=840, y=20, width=410, height=100, z=1200),
        _make_bar_chart("FactInteractions", "interaction_type", "Total Orders", x=20, y=140, width=580, height=550, z=2000),
        _make_table_visual([
            ("FactInteractions", "interaction_id", False),
            ("FactInteractions", "customer_id", False),
            ("FactInteractions", "product_id", False),
            ("FactInteractions", "interaction_type", False),
            ("FactInteractions", "interaction_weight", False)
        ], x=620, y=140, width=630, height=550, z=3000)
    ]

    inner_config = {
        "version": "5.50",
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU02",
                "version": "5.50",
                "type": 2
            }
        }
    }

    report_structure = {
        "config": json.dumps(inner_config),
        "layoutOptimization": 0,
        "sections": [
            {
                "displayName": "Executive Overview",
                "name": "ReportSection1",
                "ordinal": 0,
                "width": 1280.0,
                "height": 720.0,
                "displayOption": 1,
                "visualContainers": p1_visuals
            },
            {
                "displayName": "Customer Intelligence & RFM",
                "name": "ReportSection2",
                "ordinal": 1,
                "width": 1280.0,
                "height": 720.0,
                "displayOption": 1,
                "visualContainers": p2_visuals
            },
            {
                "displayName": "Product SKU Risk Matrix",
                "name": "ReportSection3",
                "ordinal": 2,
                "width": 1280.0,
                "height": 720.0,
                "displayOption": 1,
                "visualContainers": p3_visuals
            },
            {
                "displayName": "Voice of Customer & ABSA",
                "name": "ReportSection4",
                "ordinal": 3,
                "width": 1280.0,
                "height": 720.0,
                "displayOption": 1,
                "visualContainers": p4_visuals
            },
            {
                "displayName": "Personalization Benchmarks",
                "name": "ReportSection5",
                "ordinal": 4,
                "width": 1280.0,
                "height": 720.0,
                "displayOption": 1,
                "visualContainers": p5_visuals
            }
        ]
    }

    with open(report_dir / "report.json", "w", encoding="utf-8") as f:
        json.dump(report_structure, f, indent=2)

    logger.info(f"Generated complete Power BI Project (.pbip) at: {pbip_file}")
    return pbip_file
