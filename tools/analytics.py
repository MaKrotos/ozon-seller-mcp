"""
Analytics, Finance, and Inventory tools for Ozon MCP.
"""
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from ..client import OzonClient
from ..utils import format_json_res

async def register_analytics_tools(mcp, ozon: OzonClient):

    @mcp.tool()
    async def prices_info(
        product_id_filter: Optional[List[int]] = None,
        offer_id_filter: Optional[List[str]] = None,
        limit: int = 100,
        last_id: str = "",
    ) -> str:
        """Get prices, commissions, and marketing data."""
        body = {"limit": limit}
        filt = {}
        if product_id_filter: filt["product_id"] = product_id_filter
        if offer_id_filter: filt["offer_id"] = offer_id_filter
        if filt: body["filter"] = filt
        if last_id: body["last_id"] = last_id
        return format_json_res(await ozon.post("/v5/product/info/prices", body))

    @mcp.tool()
    async def prices_update(prices: List[Dict[str, Any]]) -> str:
        """Update product prices. Max 1000 items."""
        return format_json_res(await ozon.post("/v1/product/import/prices", {"prices": prices}))

    @mcp.tool()
    async def stocks_info(
        product_id_filter: Optional[List[int]] = None,
        offer_id_filter: Optional[List[str]] = None,
        limit: int = 100,
        last_id: str = "",
    ) -> str:
        """Get FBS/rFBS stock levels."""
        body = {"limit": limit}
        filt = {}
        if product_id_filter: filt["product_id"] = product_id_filter
        if offer_id_filter: filt["offer_id"] = offer_id_filter
        if filt: body["filter"] = filt
        if last_id: body["last_id"] = last_id
        return format_json_res(await ozon.post("/v4/product/info/stocks", body))

    @mcp.tool()
    async def stocks_update(stocks: List[Dict[str, Any]]) -> str:
        """Update stock quantities."""
        return format_json_res(await ozon.post("/v2/products/stocks", {"stocks": stocks}))

    @mcp.tool()
    async def stocks_by_warehouse_fbs(sku: List[int]) -> str:
        """Get FBS stock by warehouse for given SKUs."""
        return format_json_res(await ozon.post("/v1/product/info/stocks-by-warehouse/fbs", {"sku": sku}))

    @mcp.tool()
    async def warehouse_list() -> str:
        """List seller's warehouses."""
        return format_json_res(await ozon.post("/v1/warehouse/list", {}))

    @mcp.tool()
    async def warehouse_fbo_list() -> str:
        """List FBO warehouses."""
        return format_json_res(await ozon.post("/v1/warehouse/fbo/list", {}))

    @mcp.tool()
    async def analytics_data(
        date_from: str,
        date_to: str,
        metrics: List[str],
        dimension: List[str],
        limit: int = 100,
        offset: int = 0,
        sort: Optional[List[Dict[str, Any]]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Get analytical data. Metrics: revenue, ordered_units, etc."""
        body = {
            "date_from": date_from,
            "date_to": date_to,
            "metrics": metrics,
            "dimension": dimension,
            "limit": limit,
            "offset": offset,
        }
        if sort: body["sort"] = sort
        if filters: body["filters"] = filters
        return format_json_res(await ozon.post("/v1/analytics/data", body))

    @mcp.tool()
    async def analytics_stocks(limit: int = 100, offset: int = 0, warehouse_type: str = "") -> str:
        """Get stock on warehouses report."""
        body = {"limit": limit, "offset": offset}
        if warehouse_type: body["warehouse_type"] = warehouse_type
        return format_json_res(await ozon.post("/v2/analytics/stock_on_warehouses", body))

    @mcp.tool()
    async def finance_transactions(
        date_from: str,
        date_to: str,
        operation_type: Optional[List[str]] = None,
        posting_number: str = "",
        transaction_type: str = "all",
        page: int = 1,
        page_size: int = 50,
    ) -> str:
        """Get detailed financial transactions."""
        body = {
            "filter": {
                "date": {"from": f"{date_from}T00:00:00.000Z", "to": f"{date_to}T23:59:59.999Z"},
                "transaction_type": transaction_type,
            },
            "page": page,
            "page_size": page_size,
        }
        if operation_type: body["filter"]["operation_type"] = operation_type
        if posting_number: body["filter"]["posting_number"] = posting_number
        return format_json_res(await ozon.post("/v3/finance/transaction/list", body))

    @mcp.tool()
    async def finance_totals(date_from: str, date_to: str) -> str:
        """Get aggregated financial totals for a period."""
        body = {
            "date": {
                "from": f"{date_from}T00:00:00.000Z",
                "to": f"{date_to}T23:59:59.999Z",
            }
        }
        return format_json_res(await ozon.post("/v3/finance/transaction/totals", body))

    @mcp.tool()
    async def finance_realization(date: str) -> str:
        """Get monthly sales/returns report. date: YYYY-MM."""
        return format_json_res(await ozon.post("/v2/finance/realization", {"date": date}))

    @mcp.tool()
    async def returns_report_create(filter_type: str = "all", delivery_schema: str = "fbs") -> str:
        """Generate a returns report."""
        body = {"filter": {"filter_type": filter_type, "delivery_schema": delivery_schema}}
        return format_json_res(await ozon.post("/v2/report/returns/create", body))

    @mcp.tool()
    async def inventory_analysis_report() -> str:
        """
        Perform a comprehensive inventory analysis:
        1. Collects FBO stocks and recent FBO orders.
        2. Calculates sales velocity (burn rate) based on recent activity.
        3. Estimates stock longevity (days remaining) per warehouse and overall.
        4. Provides restocking recommendations.
        Lests a formatted text report.
        """
        stocks_raw = await analytics_stocks(warehouse_type="FBO")
        try:
            stocks_data = json.loads(stocks_raw)
            fbo_rows = stocks_data.get("result", {}).get("rows", [])
        except:
            return "Error parsing stocks data"

        since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        orders_raw = await fbo_posting_list(since=since_date)
        try:
            orders_data = json.loads(orders_raw)
            fbo_orders = orders_data.get("result", [])
        except:
            fbo_orders = []

        inventory = {}
        for row in fbo_rows:
            sku = row["sku"]
            warehouse = row.get("warehouse_name", "Unknown Warehouse")
            if sku not in inventory:
                inventory[sku] = {
                "name": row.get("item_name", "Unknown"),
                "item_code": row.get("item_code", "Unknown"),
                "stocks": {},
            }
            inventory[sku]["stocks"][warehouse] = inventory[sku]["stocks"].get(warehouse, 0) + row.get("free_to_sell_amount", 0)

        sku_orders_recent = {}
        for order in fbo_orders:
            for prod in order.get("products", []):
                sku = prod.get("sku")
                qty = prod.get("quantity", 0)
                if sku:
                    sku_orders_recent[sku] = sku_orders_recent.get(sku, 0) + qty

        report = []
        report.append("--- Ozon Inventory Analysis Report by Warehouse ---")
        report.append(f"{'SKU':<12} | {'Name':<30} | {'Warehouse':<20} | {'Stock (Free)':<12} | {'Recent Orders':<15} | {'Velocity':<10}")
        report.append("-" * 110)

        for sku, info in inventory.items():
            recent_sales = sku_orders_recent.get(sku, 0)
            daily_velocity = recent_sales / 7.0 if recent_sales > 0 else 0.1
            total_free = sum(info["stocks"].values())
            longevity = total_free / daily_velocity if daily_velocity > 0 else float('inf')
            
            for warehouse, qty in info["stocks"].items():
                line = f"{sku:<12} | {info['name'][:30]:<30} | {warehouse[:20]:<20} | {qty:<12} | {recent_sales:<15} | {daily_velocity:<10.2f}"
                report.append(line)
            
            if longevity < 14: rec = "URGENT RESTOCK"
            elif longevity < 30: rec = "PLAN RESTOCK"
            else: rec = "Sufficient"
            
            report.append(f"   -> Total Stock: {total_free} | Longevity: {longevity:.1f} days | Recommendation: {rec}")
            report.append("-" * 110)

        return "\n".join(report)
