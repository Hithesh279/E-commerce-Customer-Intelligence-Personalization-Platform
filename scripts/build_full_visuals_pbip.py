"""
scripts/build_full_visuals_pbip.py
Generates full visualContainers for Power BI report.json, adding real KPI cards,
charts, and tables directly onto the canvas for the pages.
"""

import json
import uuid
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\hithe\Downloads\E-commerce Customer Intelligence & Personalization Platform")
POWERBI_DIR = PROJECT_ROOT / "powerbi"
DOWNLOADS_DIR = Path(r"c:\Users\hithe\Downloads\Ecommerce_PowerBI_Project")

def make_card_container(measure_name, x, y, width, height, z=1000):
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

def make_bar_chart(category_entity, category_col, measure_name, x, y, width, height, z=2000):
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

def make_donut_chart(category_entity, category_col, measure_name, x, y, width, height, z=3000):
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

def make_table_visual(cols_measures, x, y, width, height, z=4000):
    vis_id = str(uuid.uuid4())
    projections = []
    selects = []
    from_map = {}

    for item in cols_measures:
        entity, prop, is_meas = item
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

def build_full_report():
    # Page 1: Executive Overview Visuals
    p1_visuals = [
        make_card_container("Total Net Revenue", x=20, y=20, width=230, height=100, z=1000),
        make_card_container("Total Orders", x=270, y=20, width=230, height=100, z=1100),
        make_card_container("Average Order Value", x=520, y=20, width=230, height=100, z=1200),
        make_card_container("Return Rate %", x=770, y=20, width=230, height=100, z=1300),
        make_card_container("Net Sentiment Score", x=1020, y=20, width=230, height=100, z=1400),
        make_bar_chart("DimProduct", "category", "Total Net Revenue", x=20, y=140, width=600, height=270, z=2000),
        make_donut_chart("DimCustomer", "customer_segment", "Total Customers", x=640, y=140, width=610, height=270, z=2100),
        make_table_visual([
            ("DimProduct", "product_name", False),
            ("DimProduct", "category", False),
            ("_Measures", "Total Net Revenue", True),
            ("_Measures", "Return Rate %", True)
        ], x=20, y=430, width=1230, height=260, z=3000)
    ]

    # Page 2: Customer Intelligence & RFM
    p2_visuals = [
        make_card_container("Total Customers", x=20, y=20, width=290, height=100, z=1000),
        make_card_container("Active Purchasing Customers", x=330, y=20, width=290, height=100, z=1100),
        make_card_container("Customer Lifetime Value", x=640, y=20, width=290, height=100, z=1200),
        make_card_container("Repeat Purchase Rate %", x=950, y=20, width=290, height=100, z=1300),
        make_bar_chart("DimCustomer", "customer_segment", "Total Net Revenue", x=20, y=140, width=600, height=550, z=2000),
        make_table_visual([
            ("DimCustomer", "customer_id", False),
            ("DimCustomer", "customer_segment", False),
            ("DimCustomer", "membership_type", False),
            ("DimCustomer", "city", False),
            ("_Measures", "Total Net Revenue", True)
        ], x=640, y=140, width=610, height=550, z=3000)
    ]

    # Page 3: Product SKU Risk Matrix
    p3_visuals = [
        make_card_container("High Sales Low Sentiment Risk SKU Count", x=20, y=20, width=380, height=100, z=1000),
        make_card_container("Return Rate %", x=430, y=20, width=380, height=100, z=1100),
        make_card_container("Total Net Revenue", x=840, y=20, width=410, height=100, z=1200),
        make_bar_chart("DimProduct", "brand", "Total Net Revenue", x=20, y=140, width=580, height=550, z=2000),
        make_table_visual([
            ("DimProduct", "product_name", False),
            ("DimProduct", "category", False),
            ("DimProduct", "brand", False),
            ("_Measures", "Total Net Revenue", True),
            ("_Measures", "Return Rate %", True)
        ], x=620, y=140, width=630, height=550, z=3000)
    ]

    # Page 4: Voice of Customer & ABSA
    p4_visuals = [
        make_card_container("Review Volume", x=20, y=20, width=290, height=100, z=1000),
        make_card_container("Positive Review Share %", x=330, y=20, width=290, height=100, z=1100),
        make_card_container("Negative Review Share %", x=640, y=20, width=290, height=100, z=1200),
        make_card_container("Net Sentiment Score", x=950, y=20, width=290, height=100, z=1300),
        make_donut_chart("FactReviews", "sentiment", "Review Volume", x=20, y=140, width=500, height=550, z=2000),
        make_table_visual([
            ("FactReviews", "review_id", False),
            ("FactReviews", "product_id", False),
            ("FactReviews", "rating", False),
            ("FactReviews", "sentiment", False),
            ("FactReviews", "review_text", False)
        ], x=540, y=140, width=710, height=550, z=3000)
    ]

    # Page 5: Personalization Benchmarks
    p5_visuals = [
        make_card_container("Total Orders", x=20, y=20, width=380, height=100, z=1000),
        make_card_container("Active Purchasing Customers", x=430, y=20, width=380, height=100, z=1100),
        make_card_container("Total Net Revenue", x=840, y=20, width=410, height=100, z=1200),
        make_bar_chart("FactInteractions", "interaction_type", "Total Orders", x=20, y=140, width=580, height=550, z=2000),
        make_table_visual([
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

    # Write to powerbi repo
    target1 = POWERBI_DIR / "Ecommerce_Customer_Intelligence.Report" / "report.json"
    target2 = DOWNLOADS_DIR / "Ecommerce_Customer_Intelligence.Report" / "report.json"

    with open(target1, "w", encoding="utf-8") as f:
        json.dump(report_structure, f, indent=2)
    with open(target2, "w", encoding="utf-8") as f:
        json.dump(report_structure, f, indent=2)

    print(f"Successfully generated full visual containers for {len(report_structure['sections'])} pages!")
    for idx, s in enumerate(report_structure['sections'], 1):
        print(f"  Page {idx}: {s['displayName']} -> {len(s['visualContainers'])} visuals")

if __name__ == "__main__":
    build_full_report()
