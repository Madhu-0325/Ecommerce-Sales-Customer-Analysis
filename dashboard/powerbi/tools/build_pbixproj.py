"""Build the Power BI PbixProj sources for the e-commerce dashboard.

Run with: python dashboard/powerbi/tools/build_pbixproj.py
Then compile the generated folder with pbi-tools:
  pbi-tools compile dashboard/powerbi/EcommerceAnalytics <out>.pbit PBIT true
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
CSV_PATH = (PROJECT / "data" / "Ecommerce_sales.csv").as_posix()
OUTPUT = PROJECT / "dashboard" / "powerbi" / "EcommerceAnalytics"

THEME_FILE = "midnight-analytics.json"
SECTION_SIZE = (1280, 720)

COLORS = {
    "bg": "#0B1220",
    "panel": "#111C33",
    "panel_alt": "#0F1A2E",
    "border": "#1E293B",
    "text": "#E2E8F0",
    "muted": "#94A3B8",
    "white": "#F8FAFC",
    "blue": "#3B82F6",
    "cyan": "#22D3EE",
    "purple": "#A855F7",
    "amber": "#F59E0B",
    "green": "#10B981",
    "red": "#EF4444",
}


def json_write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def lit(value: str) -> dict:
    return {"expr": {"Literal": {"Value": value}}}


def string_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def text(value: str) -> dict:
    return lit(string_literal(value))


def solid(color: str) -> dict:
    return {"solid": {"color": {"expr": {"Literal": {"Value": string_literal(color)}}}}}


def stable_id(value: str, length: int = 20) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()[:length]


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

SOURCE_COLUMNS = [
    ("customer_id", "int64", "0", "none"),
    ("session_id", "int64", "0", "none"),
    ("visit_date", "dateTime", "Short Date", "none"),
    ("device_type", "int64", "0", "none"),
    ("user_type", "int64", "0", "none"),
    ("marketing_channel", "int64", "0", "none"),
    ("product_id", "int64", "0", "none"),
    ("product_category", "int64", "0", "none"),
    ("unit_price", "double", "#,0.00", "none"),
    ("quantity", "int64", "#,0", "sum"),
    ("discount_percent", "int64", "#,0", "none"),
    ("discount_amount", "double", "#,0.00", "sum"),
    ("revenue", "double", "#,0.00", "sum"),
    ("pages_viewed", "int64", "#,0", "sum"),
    ("time_on_site_sec", "int64", "#,0", "sum"),
    ("added_to_cart", "int64", "#,0", "sum"),
    ("purchased", "int64", "#,0", "sum"),
    ("cart_abandoned", "int64", "#,0", "sum"),
    ("rating", "int64", "0", "average"),
    ("review_text", "int64", "0", "none"),
    ("review_helpful_votes", "int64", "#,0", "sum"),
    ("payment_method", "int64", "0", "none"),
    ("visit_day", "int64", "0", "none"),
    ("visit_month", "int64", "0", "none"),
    ("visit_weekday", "int64", "0", "none"),
    ("visit_season", "int64", "0", "none"),
    ("session_duration_bucket", "string", None, "none"),
    ("revenue_normalized", "double", "#,0.0000", "none"),
    ("location", "int64", "0", "none"),
]


def build_model() -> None:
    model = OUTPUT / "Model"
    (model / "tables").mkdir(parents=True, exist_ok=True)

    (model / "database.tmdl").write_text(
        "database 'Ecommerce Analytics'\n\tcompatibilityLevel: 1550\n", encoding="utf-8"
    )

    (model / "expressions.tmdl").write_text(
        f'expression DataFile = "{CSV_PATH}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'
        "\n"
        "\tannotation PBI_ResultType = Text\n",
        encoding="utf-8",
    )

    (model / "model.tmdl").write_text(
        "model Model\n"
        "\tculture: en-US\n"
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
        "\tsourceQueryCulture: en-US\n"
        "\tdataAccessOptions\n"
        "\t\tlegacyRedirects\n"
        "\t\treturnErrorValuesAsNull\n"
        "\n"
        "annotation __PBI_TimeIntelligenceEnabled = 0\n"
        "\n"
        "annotation PBIDesktopVersion = 2.159.883.0 (25.08)\n"
        "\n"
        'annotation PBI_QueryOrder = ["DataFile","ecommerce_sales","Funnel Stages"]\n'
        "\n"
        "ref table ecommerce_sales\n"
        "ref table 'Funnel Stages'\n",
        encoding="utf-8",
    )

    lines: list[str] = ["table ecommerce_sales", ""]
    for name, dtype, fmt, summarize in SOURCE_COLUMNS:
        lines.append(f"\tcolumn {name}")
        lines.append(f"\t\tdataType: {dtype}")
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        lines.append(f"\t\tsummarizeBy: {summarize}")
        lines.append(f"\t\tsourceColumn: {name}")
        lines.append("")
        lines.append("\t\tannotation SummarizationSetBy = Automatic")
        lines.append("")

    calculated_columns = [
        (
            "Month Start",
            "DATE ( YEAR ( ecommerce_sales[visit_date] ), MONTH ( ecommerce_sales[visit_date] ), 1 )",
            "MMM YYYY",
            "none",
            None,
        ),
        (
            "Month",
            'FORMAT ( ecommerce_sales[visit_date], "MMM YYYY" )',
            None,
            "none",
            "Month Start",
        ),
        (
            "Category",
            '"Category " & FORMAT ( ecommerce_sales[product_category], "0" )',
            None,
            "none",
            None,
        ),
        (
            "Channel",
            '"Channel " & FORMAT ( ecommerce_sales[marketing_channel], "0" )',
            None,
            "none",
            None,
        ),
        (
            "Device",
            '"Device " & FORMAT ( ecommerce_sales[device_type], "0" )',
            None,
            "none",
            None,
        ),
        (
            "User Type",
            '"User Type " & FORMAT ( ecommerce_sales[user_type], "0" )',
            None,
            "none",
            None,
        ),
        (
            "Payment Method",
            '"Payment Method " & FORMAT ( ecommerce_sales[payment_method], "0" )',
            None,
            "none",
            None,
        ),
        (
            "Season",
            '"Season " & FORMAT ( ecommerce_sales[visit_season], "0" )',
            None,
            "none",
            None,
        ),
        (
            "Purchased Label",
            'IF ( ecommerce_sales[purchased] = 1, "Purchased", "Not Purchased" )',
            None,
            "none",
            None,
        ),
    ]

    for name, expr, fmt, summarize, sort_by in calculated_columns:
        lines.append(f"\tcolumn '{name}' = {expr}")
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        if sort_by:
            lines.append(f"\t\tsortByColumn: '{sort_by}'")
        lines.append(f"\t\tsummarizeBy: {summarize}")
        lines.append("")
        lines.append("\t\tannotation SummarizationSetBy = Automatic")
        lines.append("")

    customer_type_expr = """VAR PurchasesForCustomer =
    CALCULATE (
        SUM ( ecommerce_sales[purchased] ),
        ALLEXCEPT ( ecommerce_sales, ecommerce_sales[customer_id] )
    )
RETURN
    SWITCH (
        TRUE (),
        PurchasesForCustomer > 1, "Repeat Buyer",
        PurchasesForCustomer = 1, "One-Time Buyer",
        "Non-Buyer"
    )"""
    lines.append("\tcolumn 'Customer Type' = ```")
    for expr_line in customer_type_expr.splitlines():
        lines.append("\t\t\t" + expr_line)
    lines.append("\t\t\t```")
    lines.append("\t\tsummarizeBy: none")
    lines.append("")
    lines.append("\t\tannotation SummarizationSetBy = Automatic")
    lines.append("")

    measures = [
        ("Total Revenue", "SUM ( ecommerce_sales[revenue] )", "#,0.00"),
        ("Total Purchases", "SUM ( ecommerce_sales[purchased] )", "#,0"),
        ("Total Sessions", "COUNTROWS ( ecommerce_sales )", "#,0"),
        (
            "Conversion Rate",
            "DIVIDE ( [Total Purchases], [Total Sessions] )",
            "0.0%",
        ),
        (
            "Average Order Value",
            "DIVIDE ( [Total Revenue], [Total Purchases] )",
            "#,0.00",
        ),
        ("Unique Customers", "DISTINCTCOUNT ( ecommerce_sales[customer_id] )", "#,0"),
        (
            "Buying Customers",
            "CALCULATE ( DISTINCTCOUNT ( ecommerce_sales[customer_id] ), ecommerce_sales[purchased] = 1 )",
            "#,0",
        ),
        (
            "Repeat Customers",
            """VAR CustomerPurchases =
    ADDCOLUMNS (
        VALUES ( ecommerce_sales[customer_id] ),
        "@Purchases", CALCULATE ( SUM ( ecommerce_sales[purchased] ) )
    )
RETURN
    COUNTROWS ( FILTER ( CustomerPurchases, [@Purchases] > 1 ) )""",
            "#,0",
        ),
        (
            "Repeat Customer Rate",
            "DIVIDE ( [Repeat Customers], [Buying Customers] )",
            "0.0%",
        ),
        ("Add to Cart Sessions", "SUM ( ecommerce_sales[added_to_cart] )", "#,0"),
        ("Abandoned Carts", "SUM ( ecommerce_sales[cart_abandoned] )", "#,0"),
        (
            "Cart Abandonment Rate",
            "DIVIDE ( [Abandoned Carts], [Add to Cart Sessions] )",
            "0.0%",
        ),
        (
            "Cart Purchase Rate",
            "DIVIDE ( [Total Purchases], [Add to Cart Sessions] )",
            "0.0%",
        ),
        (
            "Avg Time on Site (min)",
            "DIVIDE ( AVERAGE ( ecommerce_sales[time_on_site_sec] ), 60 )",
            "#,0.0",
        ),
        ("Avg Pages Viewed", "AVERAGE ( ecommerce_sales[pages_viewed] )", "#,0.00"),
        (
            "Avg Pages Buyers",
            "CALCULATE ( AVERAGE ( ecommerce_sales[pages_viewed] ), ecommerce_sales[purchased] = 1 )",
            "#,0.00",
        ),
        (
            "Avg Pages Non-Buyers",
            "CALCULATE ( AVERAGE ( ecommerce_sales[pages_viewed] ), ecommerce_sales[purchased] = 0 )",
            "#,0.00",
        ),
        (
            "Units Sold",
            "CALCULATE ( SUM ( ecommerce_sales[quantity] ), ecommerce_sales[purchased] = 1 )",
            "#,0",
        ),
        (
            "Total Discount",
            "CALCULATE ( SUM ( ecommerce_sales[discount_amount] ), ecommerce_sales[purchased] = 1 )",
            "#,0.00",
        ),
        (
            "Avg Discount %",
            "DIVIDE ( CALCULATE ( AVERAGE ( ecommerce_sales[discount_percent] ), ecommerce_sales[purchased] = 1 ), 100 )",
            "0.0%",
        ),
        (
            "Avg Rating (Purchases)",
            "CALCULATE ( AVERAGE ( ecommerce_sales[rating] ), ecommerce_sales[purchased] = 1 )",
            "#,0.0",
        ),
        (
            "Low Rating Share",
            """DIVIDE (
    CALCULATE ( COUNTROWS ( ecommerce_sales ), ecommerce_sales[purchased] = 1, ecommerce_sales[rating] <= 2 ),
    CALCULATE ( COUNTROWS ( ecommerce_sales ), ecommerce_sales[purchased] = 1 )
)""",
            "0.0%",
        ),
        (
            "Revenue per Session",
            "DIVIDE ( [Total Revenue], [Total Sessions] )",
            "#,0.00",
        ),
        (
            "Avg Revenue per Buyer",
            "DIVIDE ( [Total Revenue], [Buying Customers] )",
            "#,0.00",
        ),
        (
            "Sessions per Customer",
            "DIVIDE ( [Total Sessions], [Unique Customers] )",
            "#,0.00",
        ),
        (
            "Funnel Value",
            """SWITCH (
    SELECTEDVALUE ( 'Funnel Stages'[Stage] ),
    "Sessions", [Total Sessions],
    "Added to Cart", [Add to Cart Sessions],
    "Purchased", [Total Purchases]
)""",
            "#,0",
        ),
    ]

    for name, expr, fmt in measures:
        if "\n" in expr:
            lines.append(f"\tmeasure '{name}' = ```")
            for expr_line in expr.splitlines():
                lines.append("\t\t\t" + expr_line)
            lines.append("\t\t\t```")
        else:
            lines.append(f"\tmeasure '{name}' = {expr}")
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        lines.append("")

    lines.extend(
        [
            "\tpartition ecommerce_sales = m",
            "\t\tmode: import",
            "\t\tsource =",
            "\t\t\t\tlet",
            "\t\t\t\t    Source = Csv.Document(File.Contents(DataFile), [Delimiter=\",\", Columns=29, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),",
            "\t\t\t\t    #\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
            "\t\t\t\t    #\"Changed Type\" = Table.TransformColumnTypes(#\"Promoted Headers\",{",
            "\t\t\t\t        {\"customer_id\", Int64.Type}, {\"session_id\", Int64.Type}, {\"visit_date\", type text}, {\"device_type\", Int64.Type}, {\"user_type\", Int64.Type}, {\"marketing_channel\", Int64.Type}, {\"product_id\", Int64.Type}, {\"product_category\", Int64.Type}, {\"unit_price\", type number}, {\"quantity\", Int64.Type}, {\"discount_percent\", Int64.Type}, {\"discount_amount\", type number}, {\"revenue\", type number}, {\"pages_viewed\", Int64.Type}, {\"time_on_site_sec\", Int64.Type}, {\"added_to_cart\", Int64.Type}, {\"purchased\", Int64.Type}, {\"cart_abandoned\", Int64.Type}, {\"rating\", Int64.Type}, {\"review_text\", Int64.Type}, {\"review_helpful_votes\", Int64.Type}, {\"payment_method\", Int64.Type}, {\"visit_day\", Int64.Type}, {\"visit_month\", Int64.Type}, {\"visit_weekday\", Int64.Type}, {\"visit_season\", Int64.Type}, {\"session_duration_bucket\", type text}, {\"revenue_normalized\", type number}, {\"location\", Int64.Type}",
            "\t\t\t\t    }),",
            "\t\t\t\t    #\"Added Parsed Date\" = Table.AddColumn(#\"Changed Type\", \"visit_date_parsed\", each Date.FromText([visit_date], [Format=\"dd-MM-yyyy\", Culture=\"en-GB\"]), type date),",
            "\t\t\t\t    #\"Removed Text Date\" = Table.RemoveColumns(#\"Added Parsed Date\",{\"visit_date\"}),",
            "\t\t\t\t    #\"Renamed Parsed Date\" = Table.RenameColumns(#\"Removed Text Date\",{{\"visit_date_parsed\", \"visit_date\"}})",
            "\t\t\t\tin",
            "\t\t\t\t    #\"Renamed Parsed Date\"",
            "",
            "\tannotation PBI_ResultType = Table",
            "",
        ]
    )

    (model / "tables" / "ecommerce_sales.tmdl").write_text("\n".join(lines), encoding="utf-8")

    funnel_lines = [
        "table 'Funnel Stages'",
        "",
        "\tcolumn Stage",
        "\t\tdataType: string",
        "\t\tsortByColumn: 'Sort Order'",
        "\t\tsummarizeBy: none",
        "\t\tisNameInferred",
        "\t\tsourceColumn: [Stage]",
        "",
        "\t\tannotation SummarizationSetBy = Automatic",
        "",
        "\tcolumn 'Sort Order'",
        "\t\tdataType: int64",
        "\t\tisHidden",
        "\t\tformatString: 0",
        "\t\tsummarizeBy: none",
        "\t\tisNameInferred",
        "\t\tsourceColumn: [Sort Order]",
        "",
        "\t\tannotation SummarizationSetBy = Automatic",
        "",
        "\tpartition 'Funnel Stages' = calculated",
        "\t\tmode: import",
        '\t\tsource = DATATABLE ( "Stage", STRING, "Sort Order", INTEGER, { { "Sessions", 1 }, { "Added to Cart", 2 }, { "Purchased", 3 } } )',
        "",
        "\tannotation PBI_ResultType = Table",
        "",
    ]
    (model / "tables" / "Funnel Stages.tmdl").write_text(
        "\n".join(funnel_lines), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------


def col(prop: str, entity: str = "ecommerce_sales", source: str = "f") -> dict:
    return {
        "Column": {"Expression": {"SourceRef": {"Source": source}}, "Property": prop},
        "Name": f"{entity}.{prop}",
    }


def measure(prop: str, entity: str = "ecommerce_sales", source: str = "f") -> dict:
    return {
        "Measure": {"Expression": {"SourceRef": {"Source": source}}, "Property": prop},
        "Name": f"{entity}.{prop}",
    }


def qr(prop: str, entity: str = "ecommerce_sales") -> str:
    return f"{entity}.{prop}"


def visual_query(
    fields: list[dict],
    projections: dict,
    order_by: list[tuple[dict, int]] | None = None,
    entity: str = "ecommerce_sales",
    source: str = "f",
) -> tuple[dict, dict]:
    query = {
        "Version": 2,
        "From": [{"Name": source, "Entity": entity, "Type": 0}],
        "Select": fields,
    }
    if order_by:
        query["OrderBy"] = [
            {
                "Direction": direction,
                "Expression": {
                    key: value[key] for key in value
                },
            }
            for value, direction in order_by
        ]
    return projections, query


def object_map(kind: str) -> dict:
    base = {
        "labels": [
            {
                "properties": {
                    "show": lit("true"),
                    "color": solid(COLORS["text"]),
                    "fontSize": lit("8D"),
                }
            }
        ],
        "categoryAxis": [
            {
                "properties": {
                    "show": lit("true"),
                    "labelColor": solid(COLORS["muted"]),
                    "fontSize": lit("8D"),
                    "showAxisTitle": lit("false"),
                }
            }
        ],
        "valueAxis": [
            {
                "properties": {
                    "show": lit("true"),
                    "labelColor": solid(COLORS["muted"]),
                    "fontSize": lit("8D"),
                    "showAxisTitle": lit("false"),
                    "gridlineColor": solid(COLORS["border"]),
                }
            }
        ],
        "legend": [
            {
                "properties": {
                    "show": lit("false"),
                    "labelColor": solid(COLORS["muted"]),
                    "fontSize": lit("8D"),
                }
            }
        ],
    }

    if kind in {"bar", "column", "line"}:
        base["dataPoint"] = [
            {
                "properties": {
                    "fill": solid(
                        COLORS["blue"] if kind != "line" else COLORS["cyan"]
                    ),
                    "showAllDataPoints": lit("true"),
                }
            }
        ]
    if kind == "line":
        base["markers"] = [
            {
                "properties": {
                    "show": lit("true"),
                    "size": lit("4D"),
                    "color": solid(COLORS["cyan"]),
                }
            }
        ]
    if kind == "donut":
        base["legend"] = [
            {
                "properties": {
                    "show": lit("true"),
                    "position": lit("'Right'"),
                    "labelColor": solid(COLORS["muted"]),
                    "fontSize": lit("8D"),
                }
            }
        ]
        base.pop("categoryAxis", None)
        base.pop("valueAxis", None)
    if kind == "table":
        base = {
            "values": [
                {
                    "properties": {
                        "fontColor": solid(COLORS["text"]),
                        "backColor": solid(COLORS["panel"]),
                        "fontSize": lit("8D"),
                    }
                }
            ],
            "columnHeaders": [
                {
                    "properties": {
                        "fontColor": solid(COLORS["muted"]),
                        "backColor": solid(COLORS["panel_alt"]),
                        "fontSize": lit("8D"),
                        "fontFamily": lit("'Segoe UI Semibold'"),
                    }
                }
            ],
            "grid": [
                {
                    "properties": {
                        "gridHorizontal": lit("true"),
                        "gridHorizontalColor": solid(COLORS["border"]),
                        "gridVertical": lit("false"),
                        "rowPadding": lit("3D"),
                    }
                }
            ],
        }
    if kind == "card":
        base = {
            "labels": [
                {
                    "properties": {
                        "color": solid(COLORS["white"]),
                        "fontSize": lit("24D"),
                        "fontFamily": lit("'Segoe UI Semibold'"),
                    }
                }
            ],
            "categoryLabels": [
                {
                    "properties": {
                        "show": lit("false"),
                    }
                }
            ],
        }
    if kind == "funnel":
        base = {
            "labels": [
                {
                    "properties": {
                        "show": lit("true"),
                        "color": solid(COLORS["text"]),
                        "fontSize": lit("9D"),
                    }
                }
            ],
            "dataPoint": [
                {
                    "properties": {
                        "fill": solid(COLORS["blue"]),
                    }
                }
            ],
            "legend": [
                {
                    "properties": {
                        "show": lit("false"),
                    }
                }
            ],
        }
    return base


def visual_container_objects(title: str | None, panel: bool = True) -> dict:
    objects = {
        "visualHeader": [
            {
                "properties": {
                    "show": lit("false"),
                }
            }
        ],
        "visualTooltip": [{"properties": {"show": lit("true")}}],
        "dropShadow": [
            {
                "properties": {
                    "show": lit("true"),
                    "preset": lit("'Custom'"),
                    "color": solid("#000000"),
                    "transparency": lit("80D"),
                    "shadowBlur": lit("12D"),
                    "shadowDistance": lit("4D"),
                    "angle": lit("90D"),
                }
            }
        ],
    }
    if panel:
        objects["background"] = [
            {
                "properties": {
                    "show": lit("true"),
                    "color": solid(COLORS["panel"]),
                    "transparency": lit("0D"),
                }
            }
        ]
        objects["border"] = [
            {
                "properties": {
                    "show": lit("true"),
                    "color": solid(COLORS["border"]),
                    "radius": lit("10D"),
                }
            }
        ]
    if title:
        objects["title"] = [
            {
                "properties": {
                    "show": lit("true"),
                    "text": text(title),
                    "fontColor": solid(COLORS["text"]),
                    "background": solid(COLORS["panel"]),
                    "fontSize": lit("11D"),
                    "fontFamily": lit("'Segoe UI Semibold'"),
                    "alignment": lit("'left'"),
                }
            }
        ]
    return objects


def build_section(
    folder: str,
    display_name: str,
    ordinal: int,
    visuals: list[dict],
) -> dict:
    section_id = "ReportSection" + stable_id(folder)
    section_dir = OUTPUT / "Report" / "sections" / folder
    (section_dir / "visualContainers").mkdir(parents=True, exist_ok=True)

    json_write(
        section_dir / "section.json",
        {
            "displayName": display_name,
            "displayOption": 1,
            "height": SECTION_SIZE[1],
            "name": section_id,
            "ordinal": ordinal,
            "width": SECTION_SIZE[0],
        },
    )
    json_write(
        section_dir / "config.json",
        {
            "objects": {
                "background": [
                    {
                        "properties": {
                            "transparency": lit("0D"),
                            "color": solid(COLORS["bg"]),
                        }
                    }
                ]
            },
            "visibility": 1,
            "filterSortOrder": 3,
        },
    )
    json_write(section_dir / "filters.json", [])

    for index, visual in enumerate(visuals, start=1):
        safe_name = "".join(
            character if character.isalnum() or character in " _-" else "-"
            for character in visual["name"]
        ).strip()
        name = f"{index:05d}_{safe_name}"
        visual_dir = section_dir / "visualContainers" / name
        visual_dir.mkdir(parents=True, exist_ok=True)
        config = visual.pop("config")
        json_write(visual_dir / "config.json", config)
        json_write(visual_dir / "filters.json", [])
        json_write(
            visual_dir / "visualContainer.json",
            {
                "height": visual["height"],
                "id": int(stable_id(folder + name, 8), 16),
                "width": visual["width"],
                "x": visual["x"],
                "y": visual["y"],
                "z": visual["z"],
            },
        )

    return {"name": section_id, "displayName": display_name}


def make_visual(
    name: str,
    visual_type: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z: int,
    fields: list[dict] | None = None,
    projections: dict | None = None,
    order_by: list[tuple[dict, int]] | None = None,
    objects: dict | None = None,
    vc_objects: dict | None = None,
    entity: str = "ecommerce_sales",
    source: str = "f",
    tab_order: int | None = None,
) -> dict:
    if projections is not None and fields is not None:
        projections, query = visual_query(
            fields, projections, order_by, entity=entity, source=source
        )
    else:
        query = None

    single = {
        "visualType": visual_type,
        "drillFilterOtherVisuals": True,
    }
    if query is not None:
        single["projections"] = projections
        single["prototypeQuery"] = query
    if objects is not None:
        single["objects"] = objects
    single["vcObjects"] = vc_objects if vc_objects is not None else {}

    return {
        "name": name,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "z": z,
        "config": {
            "name": stable_id(name),
            "layouts": [
                {
                    "id": 0,
                    "position": {
                        "x": x,
                        "y": y,
                        "z": z,
                        "width": width,
                        "height": height,
                        "tabOrder": tab_order if tab_order is not None else z,
                    },
                }
            ],
            "singleVisual": single,
        },
    }


def add_textbox(
    visuals: list[dict],
    name: str,
    value: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z: int,
    font_size: str,
    color: str,
    bold: bool = False,
) -> None:
    style = {
        "fontSize": font_size,
        "color": color,
        "fontFamily": "Segoe UI Semibold" if bold else "Segoe UI",
    }
    if bold:
        style["fontWeight"] = "bold"
    config = {
        "name": stable_id(name),
        "layouts": [
            {
                "id": 0,
                "position": {
                    "x": x,
                    "y": y,
                    "z": z,
                    "width": width,
                    "height": height,
                    "tabOrder": z,
                },
            }
        ],
        "singleVisual": {
            "visualType": "textbox",
            "drillFilterOtherVisuals": True,
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": value,
                                            "textStyle": style,
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
            "vcObjects": {
                "background": [
                    {"properties": {"show": lit("false")}}
                ],
                "visualHeader": [
                    {"properties": {"show": lit("false")}}
                ],
            },
        },
    }
    visuals.append(
        {
            "name": name,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": z,
            "config": config,
        }
    )


def add_shape(
    visuals: list[dict],
    name: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z: int,
    color: str,
    outline: bool = False,
    radius: int = 0,
) -> None:
    objects = {
        "shape": [
            {"properties": {"tileShape": lit("'rectangle'")}}
        ],
        "fill": [
            {
                "properties": {"fillColor": solid(color)},
                "selector": {"id": "default"},
            }
        ],
    }
    if outline:
        objects["outline"] = [
            {
                "properties": {
                    "lineColor": solid(COLORS["border"]),
                    "weight": lit("1D"),
                },
                "selector": {"id": "default"},
            }
        ]
    config = {
        "name": stable_id(name),
        "layouts": [
            {
                "id": 0,
                "position": {
                    "x": x,
                    "y": y,
                    "z": z,
                    "width": width,
                    "height": height,
                    "tabOrder": z,
                },
            }
        ],
        "singleVisual": {
            "visualType": "shape",
            "drillFilterOtherVisuals": True,
            "objects": objects,
            "vcObjects": {
                "visualHeader": [
                    {"properties": {"show": lit("false")}}
                ],
                "title": [
                    {"properties": {"show": lit("false")}}
                ],
            },
        },
    }
    visuals.append(
        {
            "name": name,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "z": z,
            "config": config,
        }
    )


def add_card(
    visuals: list[dict],
    title: str,
    measure_name: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z: int,
) -> None:
    fields = [measure(measure_name)]
    projections = {"Values": [{"queryRef": qr(measure_name)}]}
    visuals.append(
        make_visual(
            f"KPI {title}",
            "card",
            x,
            y,
            width,
            height,
            z,
            fields=fields,
            projections=projections,
            objects=object_map("card"),
            vc_objects=visual_container_objects(title),
        )
    )


def add_chart(
    visuals: list[dict],
    name: str,
    visual_type: str,
    title: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z: int,
    dimension: str | None,
    value: str,
    order_value: str | None = None,
    dimension_entity: str = "ecommerce_sales",
    dimension_source: str = "f",
) -> None:
    fields: list[dict] = []
    projections: dict = {}
    order_by: list[tuple[dict, int]] = []
    if dimension:
        fields.append(col(dimension, entity=dimension_entity, source=dimension_source))
        projections["Category"] = [
            {"queryRef": qr(dimension, entity=dimension_entity), "active": True}
        ]
    fields.append(measure(value))
    projections["Y"] = [{"queryRef": qr(value)}]
    if order_value:
        order_by.append((measure(order_value), 2))
    visuals.append(
        make_visual(
            name,
            visual_type,
            x,
            y,
            width,
            height,
            z,
            fields=fields,
            projections=projections,
            order_by=order_by,
            objects=object_map(
                "line"
                if visual_type == "lineChart"
                else "donut"
                if visual_type == "donutChart"
                else "funnel"
                if visual_type == "funnel"
                else "bar"
                if visual_type == "barChart"
                else "column"
            ),
            vc_objects=visual_container_objects(title),
            entity="ecommerce_sales",
            source="f",
        )
    )


def add_table(
    visuals: list[dict],
    name: str,
    title: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z: int,
    fields_spec: list[tuple[str, str]],
    order_value: str | None = None,
) -> None:
    fields = []
    values = []
    for kind, prop in fields_spec:
        if kind == "col":
            fields.append(col(prop))
        else:
            fields.append(measure(prop))
        values.append({"queryRef": qr(prop)})
    order_by = [(measure(order_value), 2)] if order_value else None
    visuals.append(
        make_visual(
            name,
            "tableEx",
            x,
            y,
            width,
            height,
            z,
            fields=fields,
            projections={"Values": values},
            order_by=order_by,
            objects=object_map("table"),
            vc_objects=visual_container_objects(title),
        )
    )


def add_slicer(
    visuals: list[dict],
    title: str,
    column_name: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z: int,
) -> None:
    fields = [col(column_name)]
    projections = {"Values": [{"queryRef": qr(column_name), "active": True}]}
    objects = {
        "data": [
            {
                "properties": {
                    "mode": lit("'Dropdown'"),
                    "selection": lit("'Single'"),
                }
            }
        ],
        "header": [
            {
                "properties": {
                    "show": lit("true"),
                    "text": text(title.upper()),
                    "fontColor": solid(COLORS["cyan"]),
                    "textSize": lit("8D"),
                    "background": solid(COLORS["panel_alt"]),
                }
            }
        ],
        "items": [
            {
                "properties": {
                    "fontColor": solid(COLORS["text"]),
                    "background": solid(COLORS["panel_alt"]),
                    "textSize": lit("8D"),
                }
            }
        ],
    }
    visuals.append(
        make_visual(
            f"Slicer {title}",
            "slicer",
            x,
            y,
            width,
            height,
            z,
            fields=fields,
            projections=projections,
            objects=objects,
            vc_objects=visual_container_objects(None),
        )
    )


def add_page_chrome(
    visuals: list[dict],
    page_title: str,
    subtitle: str,
    slicer_column: str,
    slicer_title: str,
) -> None:
    add_shape(visuals, "Header Background", 0, 0, 1280, 88, 1000, COLORS["panel_alt"])
    add_shape(visuals, "Header Accent", 0, 86, 1280, 2, 1001, COLORS["blue"])
    add_shape(visuals, "Header Accent Cyan", 0, 88, 427, 2, 1002, COLORS["cyan"])
    add_shape(visuals, "Header Accent Purple", 853, 88, 427, 2, 1003, COLORS["purple"])
    add_textbox(
        visuals,
        "Eyebrow",
        "ECOMMERCE ANALYTICS  /  FY 2024",
        32,
        10,
        620,
        16,
        1100,
        "8pt",
        COLORS["cyan"],
        bold=True,
    )
    add_textbox(
        visuals,
        "Page Title",
        page_title,
        32,
        25,
        680,
        34,
        1101,
        "21pt",
        COLORS["white"],
        bold=True,
    )
    add_textbox(
        visuals,
        "Page Subtitle",
        subtitle,
        32,
        61,
        720,
        18,
        1102,
        "8.5pt",
        COLORS["muted"],
    )
    add_slicer(visuals, slicer_title, slicer_column, 994, 16, 254, 58, 1200)
    add_textbox(
        visuals,
        "Footer",
        "Source: Ecommerce_sales.csv  |  25,000 sessions  |  Jan 1 - Dec 30, 2024",
        32,
        696,
        760,
        16,
        1300,
        "7.5pt",
        "#64748B",
    )


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def build_report() -> list[dict]:
    sections: list[dict] = []

    # Page 1 -----------------------------------------------------------------
    v: list[dict] = []
    add_page_chrome(
        v,
        "Sales Performance",
        "Revenue, order volume and channel contribution across the year.",
        "Month",
        "Month",
    )
    cards = [
        ("TOTAL REVENUE", "Total Revenue"),
        ("PURCHASES", "Total Purchases"),
        ("CONVERSION RATE", "Conversion Rate"),
        ("AVG ORDER VALUE", "Average Order Value"),
    ]
    for i, (label, metric) in enumerate(cards):
        add_card(v, label, metric, 32 + i * 304, 104, 288, 96, 2000 + i)

    add_chart(
        v,
        "Revenue Trend",
        "lineChart",
        "REVENUE TREND",
        32,
        216,
        754,
        266,
        3000,
        "Month",
        "Total Revenue",
    )
    add_chart(
        v,
        "Revenue by Category",
        "barChart",
        "REVENUE BY PRODUCT CATEGORY",
        802,
        216,
        446,
        266,
        3001,
        "Category",
        "Total Revenue",
        order_value="Total Revenue",
    )
    add_chart(
        v,
        "Revenue by Channel",
        "donutChart",
        "REVENUE BY MARKETING CHANNEL",
        32,
        498,
        370,
        192,
        3002,
        "Channel",
        "Total Revenue",
    )
    add_table(
        v,
        "Category Performance",
        "CATEGORY PERFORMANCE",
        418,
        498,
        830,
        192,
        3003,
        [
            ("col", "Category"),
            ("measure", "Total Revenue"),
            ("measure", "Total Purchases"),
            ("measure", "Average Order Value"),
        ],
        order_value="Total Revenue",
    )
    sections.append(build_section("001_Sales Performance", "Sales Performance", 0, v))

    # Page 2 -----------------------------------------------------------------
    v = []
    add_page_chrome(
        v,
        "Customer Analysis",
        "Who buys, how often they return and where value concentrates.",
        "User Type",
        "User Type",
    )
    cards = [
        ("UNIQUE CUSTOMERS", "Unique Customers"),
        ("BUYING CUSTOMERS", "Buying Customers"),
        ("REPEAT CUSTOMERS", "Repeat Customers"),
        ("REPEAT CUSTOMER RATE", "Repeat Customer Rate"),
    ]
    for i, (label, metric) in enumerate(cards):
        add_card(v, label, metric, 32 + i * 304, 104, 288, 96, 2000 + i)

    add_chart(
        v,
        "Buyers by User Type",
        "barChart",
        "BUYING CUSTOMERS BY USER TYPE",
        32,
        216,
        446,
        266,
        3000,
        "User Type",
        "Buying Customers",
        order_value="Buying Customers",
    )
    add_chart(
        v,
        "Revenue by Customer Type",
        "donutChart",
        "REVENUE BY CUSTOMER TYPE",
        494,
        216,
        360,
        266,
        3001,
        "Customer Type",
        "Total Revenue",
    )
    add_chart(
        v,
        "Repeat Rate by Channel",
        "barChart",
        "REPEAT RATE BY CHANNEL",
        870,
        216,
        378,
        266,
        3002,
        "Channel",
        "Repeat Customer Rate",
        order_value="Repeat Customer Rate",
    )
    add_table(
        v,
        "Location Performance",
        "LOCATION PERFORMANCE",
        32,
        498,
        600,
        192,
        3003,
        [
            ("col", "Location"),
            ("measure", "Buying Customers"),
            ("measure", "Total Revenue"),
            ("measure", "Average Order Value"),
            ("measure", "Repeat Customer Rate"),
        ],
        order_value="Total Revenue",
    )
    add_chart(
        v,
        "Avg Revenue per Buyer by User Type",
        "barChart",
        "AVG REVENUE PER BUYER BY USER TYPE",
        648,
        498,
        600,
        192,
        3004,
        "User Type",
        "Avg Revenue per Buyer",
        order_value="Avg Revenue per Buyer",
    )
    sections.append(build_section("002_Customer Analysis", "Customer Analysis", 1, v))

    # Page 3 -----------------------------------------------------------------
    v = []
    add_page_chrome(
        v,
        "Customer Behaviour",
        "From first visit to checkout: engagement, intent and friction.",
        "Device",
        "Device",
    )
    cards = [
        ("AVG TIME ON SITE", "Avg Time on Site (min)"),
        ("AVG PAGES VIEWED", "Avg Pages Viewed"),
        ("ADD TO CART SESSIONS", "Add to Cart Sessions"),
        ("CART ABANDONMENT", "Cart Abandonment Rate"),
    ]
    for i, (label, metric) in enumerate(cards):
        add_card(v, label, metric, 32 + i * 304, 104, 288, 96, 2000 + i)

    fields = [col("Stage", entity="Funnel Stages", source="fs"), measure("Funnel Value")]
    projections = {
        "Category": [
            {"queryRef": qr("Stage", entity="Funnel Stages"), "active": True}
        ],
        "Y": [{"queryRef": qr("Funnel Value")}],
    }
    v.append(
        make_visual(
            "Conversion Funnel",
            "funnel",
            32,
            216,
            446,
            474,
            3000,
            fields=fields,
            projections=projections,
            objects=object_map("funnel"),
            vc_objects=visual_container_objects("CONVERSION FUNNEL"),
            entity="Funnel Stages",
            source="fs",
        )
    )
    add_chart(
        v,
        "Conversion by Device",
        "clusteredColumnChart",
        "CONVERSION RATE BY DEVICE",
        494,
        216,
        360,
        224,
        3001,
        "Device",
        "Conversion Rate",
        order_value="Conversion Rate",
    )
    add_chart(
        v,
        "Abandonment by Device",
        "clusteredColumnChart",
        "CART ABANDONMENT BY DEVICE",
        870,
        216,
        378,
        224,
        3002,
        "Device",
        "Cart Abandonment Rate",
        order_value="Cart Abandonment Rate",
    )
    add_chart(
        v,
        "Pages by Purchase Status",
        "clusteredColumnChart",
        "AVG PAGES BY PURCHASE STATUS",
        494,
        456,
        360,
        234,
        3003,
        "Purchased Label",
        "Avg Pages Viewed",
        order_value="Avg Pages Viewed",
    )
    add_chart(
        v,
        "Sessions by Duration",
        "donutChart",
        "SESSIONS BY DURATION BUCKET",
        870,
        456,
        378,
        234,
        3004,
        "session_duration_bucket",
        "Total Sessions",
    )
    sections.append(
        build_section("003_Customer Behaviour", "Customer Behaviour", 2, v)
    )

    # Page 4 -----------------------------------------------------------------
    v = []
    add_page_chrome(
        v,
        "Marketing & Product",
        "Channel efficiency, product mix and commercial quality signals.",
        "Channel",
        "Channel",
    )
    cards = [
        ("REVENUE / SESSION", "Revenue per Session"),
        ("AVG DISCOUNT", "Avg Discount %"),
        ("UNITS SOLD", "Units Sold"),
        ("AVG RATING", "Avg Rating (Purchases)"),
    ]
    for i, (label, metric) in enumerate(cards):
        add_card(v, label, metric, 32 + i * 304, 104, 288, 96, 2000 + i)

    add_chart(
        v,
        "Revenue by Channel",
        "barChart",
        "REVENUE BY CHANNEL",
        32,
        216,
        600,
        250,
        3000,
        "Channel",
        "Total Revenue",
        order_value="Total Revenue",
    )
    add_chart(
        v,
        "Conversion by Channel",
        "clusteredColumnChart",
        "CONVERSION RATE BY CHANNEL",
        648,
        216,
        600,
        250,
        3001,
        "Channel",
        "Conversion Rate",
        order_value="Conversion Rate",
    )
    add_table(
        v,
        "Product Category Scorecard",
        "PRODUCT CATEGORY SCORECARD",
        32,
        482,
        900,
        208,
        3002,
        [
            ("col", "Category"),
            ("measure", "Total Revenue"),
            ("measure", "Units Sold"),
            ("measure", "Average Order Value"),
            ("measure", "Avg Discount %"),
            ("measure", "Avg Rating (Purchases)"),
        ],
        order_value="Total Revenue",
    )
    add_chart(
        v,
        "Revenue by Payment Method",
        "donutChart",
        "REVENUE BY PAYMENT METHOD",
        948,
        482,
        300,
        208,
        3003,
        "Payment Method",
        "Total Revenue",
    )
    sections.append(
        build_section("004_Marketing and Product", "Marketing & Product", 3, v)
    )

    return sections


def build_theme() -> None:
    theme = {
        "name": "Midnight Analytics",
        "dataColors": [
            COLORS["blue"],
            COLORS["cyan"],
            COLORS["purple"],
            COLORS["amber"],
            COLORS["green"],
            COLORS["red"],
            "#6366F1",
            "#14B8A6",
        ],
        "background": COLORS["bg"],
        "foreground": COLORS["text"],
        "tableAccent": COLORS["blue"],
        "textClasses": {
            "title": {
                "fontFace": "Segoe UI Semibold",
                "fontSize": 14,
                "color": COLORS["text"],
            },
            "header": {
                "fontFace": "Segoe UI Semibold",
                "fontSize": 11,
                "color": COLORS["text"],
            },
            "label": {
                "fontFace": "Segoe UI",
                "fontSize": 9,
                "color": COLORS["muted"],
            },
            "callout": {
                "fontFace": "Segoe UI Semibold",
                "fontSize": 28,
                "color": COLORS["white"],
            },
        },
    }
    json_write(
        OUTPUT / "StaticResources" / "RegisteredResources" / THEME_FILE,
        theme,
    )


def build_project_files(sections: list[dict]) -> None:
    now = datetime.now(timezone.utc).astimezone().isoformat()
    json_write(
        OUTPUT / ".pbixproj.json",
        {
            "version": "1.0",
            "created": now,
            "lastModified": now,
            "settings": {"model": {"serializationMode": "Tmdl"}},
        },
    )
    (OUTPUT / "Version.txt").write_text("1.25", encoding="utf-8")
    json_write(
        OUTPUT / "ReportMetadata.json",
        {
            "Version": 5,
            "AutoCreatedRelationships": [],
            "CreatedFrom": "Desktop",
            "CreatedFromRelease": "2025.08",
        },
    )
    json_write(
        OUTPUT / "ReportSettings.json",
        {
            "Version": 2,
            "ReportSettings": {
                "ShowHiddenFields": True,
                "IsQnaEnabledForLiveConnect": False,
                "IsQnaEnabledForThisFile": False,
            },
            "QueriesSettings": {
                "TypeDetectionEnabled": True,
                "RelationshipImportEnabled": True,
                "RunBackgroundAnalysis": True,
                "Version": "2.159.883.0",
            },
        },
    )
    json_write(
        OUTPUT / "DiagramLayout.json",
        {
            "version": "1.1.0",
            "diagrams": [
                {
                    "ordinal": 0,
                    "scrollPosition": {"x": 0, "y": 0},
                    "nodes": [
                        {
                            "location": {"x": 80, "y": 80},
                            "nodeIndex": "ecommerce_sales",
                            "size": {"height": 320, "width": 260},
                            "zIndex": 1,
                        },
                        {
                            "location": {"x": 400, "y": 80},
                            "nodeIndex": "Funnel Stages",
                            "size": {"height": 120, "width": 240},
                            "zIndex": 2,
                        },
                    ],
                    "name": "All tables",
                    "zoomValue": 90,
                    "pinKeyFieldsToTop": False,
                    "showExtraHeaderInfo": False,
                    "hideKeyFieldsWhenCollapsed": False,
                }
            ],
            "selectedDiagram": "All tables",
            "defaultDiagram": "All tables",
        },
    )
    json_write(OUTPUT / "Connections.json", {"Version": 3, "RemoteArtifacts": []})

    pods = []
    for index, section in enumerate(sections):
        pods.append(
            {
                "boundSection": section["name"],
                "config": "{}",
                "id": 64520000 + index,
                "name": f"Pod{index}",
                "objectId": f"00000000-0000-0000-0000-{64520000 + index:012d}",
                "type": 1,
            }
        )

    json_write(
        OUTPUT / "Report" / "report.json",
        {
            "id": 64520000,
            "layoutOptimization": 0,
            "pods": pods,
            "publicCustomVisuals": [],
            "reportId": 64520001,
            "resourcePackages": [
                {
                    "resourcePackage": {
                        "id": 64520002,
                        "items": [
                            {
                                "id": 64520003,
                                "name": THEME_FILE,
                                "path": THEME_FILE,
                                "resourcePackageId": 64520002,
                                "resourcePackageItemBlobInfoId": 64520004,
                                "type": 100,
                            }
                        ],
                        "name": "RegisteredResources",
                        "reportId": 64520001,
                        "type": 1,
                    }
                }
            ],
            "theme": THEME_FILE,
        },
    )
    json_write(
        OUTPUT / "Report" / "filters.json",
        [],
    )
    json_write(
        OUTPUT / "Report" / "config.json",
        {
            "version": "5.25",
            "themeCollection": {
                "customTheme": {
                    "name": THEME_FILE,
                    "version": "5.22",
                    "type": 1,
                }
            },
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True,
            "settings": {
                "useStylableVisualContainerHeader": True,
                "exportDataMode": 1,
                "useNewFilterPaneExperience": True,
                "allowChangeFilterTypes": True,
                "allowDataPointLassoSelect": True,
            },
            "objects": {
                "outspacePane": [
                    {
                        "properties": {
                            "expanded": lit("false"),
                            "visible": lit("false"),
                        }
                    }
                ]
            },
        },
    )


def clean() -> None:
    if OUTPUT.exists():
        import shutil

        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    clean()
    build_model()
    build_theme()
    sections = build_report()
    build_project_files(sections)
    print(f"Built PbixProj sources at {OUTPUT}")
    print(f"CSV source: {CSV_PATH}")


if __name__ == "__main__":
    main()


