"""
MCP server for Ozon Seller API (api-seller.ozon.ru).
Refactored version with modular client and structured data handling.
"""

import os
import json
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP

# --- Constants & Config ---
BASE_URL = "https://api-seller.ozon.ru"

class OzonClient:
    """
    Dedicated client for interacting with Ozon Seller API.
    Handles authentication and request execution.
    """
    def __init__(self):
        self.client_id = os.environ.get("OZON_CLIENT_ID")
        self.api_key = os.environ.get("OZON_API_KEY")
        
        if not self.client_id or not self.api_key:
            raise ValueError("OZON_CLIENT_ID and OZON_API_KEY environment variables are required")
        
        self._http_client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Singleton pattern for httpx client to reuse connections."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                base_url=BASE_URL,
                headers={
                    "Client-Id": self.client_id,
                    "Api-Key": self.api_key,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._http_client

    async def post(self, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generic POST request handler with structured error reporting."""
        client = await self.get_client()
        try:
            resp = await client.post(path, json=body or {})
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}", "detail": e.response.text}
        except Exception as e:
            return {"error": "RequestException", "detail": str(e)}

# Initialize MCP and Client
mcp = Fast uma = FastMCP("ozon-seller")
ozon = OzonClient()

def format_json_res(data: Any) -> str:
    """Utility to ensure consistent JSON output for MCP tools."""
    return json.dumps(data, ensure_ascii=False, indent=2)

# ── Products Tools ───────────────────────────────────────────────────────────

@mcp.tool()
async def product_list(
    limit: int = 100,
    last_id: str = "",
    offer_id_filter: Optional[List[str]] = None,
    product_id_filter: Optional[List[int]] = None,
    visibility: str = "ALL",
) -> str:
    """List seller's products. Visibility options include ALL, VISIBLE, INVISIBLE, etc."""
    body = {"limit": limit, "visibility": visibility}
    if last_id: body["last_id"] = last_id
    
    filt = {}
    if offer_id_filter: filt["offer_id"] = offer_id_filter
    if product_id_filter: filt["product_id"] = product_id_filter
    if filt: body["filter"] = filt
    
    return format_json_res(await ozon.post("/v3/product/list", body))

@mcp.tool()
async def product_info(product_id: int = 0, offer_id: str = "", sku: int = 0) -> str:
    """Get detailed info about a single product."""
    body = {}
    if product_id: body["product_id"] = product_id
    if offer_id: body["offer_id"] = offer_id
    if sku: body["sku"] = sku
    return format_json_res(await ozon.post("/v2/product/info", body))

@mcp.tool()
async def product_info_list(product_id: Optional[List[int]] = None, offer_id: Optional[List[str]] = None) -> str:
    """Get detailed info for multiple products."""
    body = {}
    if product_id: body["product_id"] = product_id
    if offer_id: body["offer_id"] = offer_id
    return format_json_res(await ozon.post("/v3/product/info/list", body))

@mcp.tool()
async def product_info_attributes(
    product_id: Optional[List[int]] = None,
    offer_id: Optional[List[str]] = None,
    limit: int = 100,
    last_id: str = "",
    sort_by: str = "",
    sort_dir: str = "ASC",
) -> str:
    """Get product attributes/characteristics."""
    body = {"limit": limit}
    filt = {}
    if product_id: filt["product_id"] = product_id
    if offer_id: filt["offer_id"] = offer_id
    if filt: body["filter"] = filt
    if last_id: body["last_id"] = last_id
    if sort_by:
        body["sort_by"] = sort_by
        body["sort_dir"] = sort_dir
    return format_json_res(await ozon.post("/v4/product/info/attributes", body))

@mcp.tool()
async def product_import(items: List[Dict[str, Any]]) -> str:
    """Import/create/update products. Max 100 items."""
    return format_json_res(await ozon.post("/v3/product/import", {"items": items}))

@mcp.tool()
async def product_import_info(task_id: int) -> str:
    """Check status of a product import task."""
    return format_json_res(await ozon.post("/v1/product/import/info", {"task_id": task_id}))

@mcp.tool()
async def product_archive(product_id: List[int]) -> str:
    """Archive products."""
    return format_json_res(await ozon.post("/v1/product/archive", {"product_id": product_id}))

@mcp.tool()
async def product_unarchive(product_id: List[int]) -> str:
    """Unarchive products."""
    return format_json_res(await ozon.post("/v1/product/unarchive", {"product_id": product_id}))

@mcp.tool()
async def product_delete(product_id: List[int]) -> str:
    """Delete products not yet assigned an SKU."""
    return format_json_res(await ozon.post("/v2/products/delete", {"product_id": product_id}))

@mcp.tool()
async def product_description(product_id: int = 0, offer_id: str = "") -> str:
    """Get product description."""
    body = {}
    if product_id: body["product_id"] = product_id
    if offer_id: body["offer_id"] = offer_id
    return format_json_res(await ozon.post("/v1/product/info/description", body))

@mcp.tool()
async def product_attributes_update(items: List[Dict[str, Any]]) -> str:
    """Update product attributes."""
    return format_json_res(await ozon.post("/v1/product/attributes/update", {"items": items}))

@mcp.tool()
async def product_pictures_import(product_id: int, images: List[str]) -> str:
    """Upload product images by URLs."""
    return format_json_res(await ozon.post("/v1/product/pictures/import", {"product_id": product_id, "images": images}))

# ── Pricing Tools ────────────────────────────────────────────────────────────

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

# ── Stock Tools ──────────────────────────────────────────────────────────────

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

# ── FBS Orders Tools ────────────────────────────────────────────────────────

@mcp.tool()
async def fbs_unfulfilled_list(
    limit: int = 50,
    offset: int = 0,
    status: str = "",
    sort_by: str = "created_at",
    sort_dir: str = "ASC",
    cutoff_from: str = "",
    cutoff_to: str = "",
    delivering_date_from: str = "",
    delivering_date_to: str = "",
) -> str:
    """List unprocessed FBS shipments."""
    body = {"limit": limit, "offset": offset, "dir": sort_dir, "sort_by": sort_by}
    filt = {}
    if status: filt["status"] = status
    if cutoff_from: filt["cutoff_from"] = cutoff_from
    if cutoff_to: filt["cutoff_to"] = cutoff_to
    if delivering_date_from: filt["delivering_date_from"] = delivering_date_from
    if delivering_date_to: filt["delivering_date_to"] = delivering_date_to
    if filt: body["filter"] = filt
    return format_json_res(await ozon.post("/v3/posting/fbs/unfulfilled/list", body))

@mcp.tool()
async def fbs_posting_list(
    limit: int = 50,
    offset: int = 0,
    since: str = "",
    to: str = "",
    status: str = "",
    sort_by: str = "created_at",
    sort_dir: str = "ASC",
) -> str:
    """List FBS shipments with filters."""
    body = {"limit": limit, "offset": offset, "dir": sort_dir}
    filt = {}
    if since: filt["since"] = since
    if to: filt["to"] = to
    if status: filt["status"] = status
    if filt: body["filter"] = filt
    return format_json_res(await ozon.post("/v3/posting/fbs/list", body))

@mcp.tool()
async def fbs_posting_get(posting_number: str) -> str:
    """Get detailed info about a single FBS shipment."""
    return format_json_res(await ozon.post("/v3/posting/fbs/get", {"posting_number": posting_number}))

@mcp.tool()
async def fbs_ship(posting_number: str, packages: List[Dict[str, Any]]) -> str:
    """Pack and confirm FBS shipment."""
    return format_json_res(await ozon.post("/v2/posting/fbs/ship", {"posting_number": posting_number, "packages": packages}))

@mcp.tool()
async def fbs_cancel(posting_number: str, cancel_reason_id: int, cancel_reason_message: str = "") -> str:
    """Cancel an FBS shipment."""
    body = {"posting_number": posting_number, "cancel_reason_id": cancel_reason_id}
    if cancel_reason_message: body["cancel_reason_message"] = cancel_reason_message
    return format_json_res(await ozon.post("/v2/posting/fbs/cancel", body))

@mcp.tool()
async def fbs_cancel_reasons() -> str:
    """Get list of available cancellation reasons."""
    return format_json_res(await ozon.post("/v1/posting/fbs/cancel-reason", {}))

@mcp.tool()
async def fbs_package_label(posting_number: List[str]) -> str:
    """Generate PDF shipping labels for FBS."""
    return format_json_res(await ozon.post("/v2/posting/fbs/package-label", {"posting_number": posting_number}))

@mcp.tool()
async def fbs_set_tracking_number(posting_number: str, tracking_number: str) -> str:
    """Set tracking number for an FBS shipment."""
    return format_json_res(await ozon.post("/v2/posting/fbs/tracking-number/set", {"posting_number": posting_number, "tracking_number": tracking_number}))

@mcp.tool()
async def fbs_act_create(delivery_method_id: int, departure_date: str) -> str:
    """Create a transfer certificate (act)."""
    return format_json_res(await ozon.post("/v2/posting/fbs/act/create", {"delivery_method_id": delivery_method_id, "departure_date": departure_date}))

@mcp.tool()
async def fbs_act_check_status(id: int) -> str:
    """Check status of a transfer certificate."""
    return format_json_res(await ozon.post("/v2/posting/fbs/act/check-status", {"id": id}))

# ── FBO Orders Tools ─────────────────────────────────────────────────────────

@mcp.tool()
async def fbo_posting_list(
    limit: int = 50,
    cursor: str = "",
    filter: Optional[Dict[str, Any]] = None,
    sort_dir: str = "ASC",
    translit: bool = False,
    with_data: Optional[Dict[str, Any]] = None,
) -> str:
    """List FBO shipments."""
    body = {"limit": limit, "cursor": cursor, "sort_dir": sort_dir, "translit": translit}
    if filter: body["filter"] = filter
    if with_data: body["with"] = with_data
    return format_json_res(await ozon.post("/v3/posting/fbo/list", body))

@mcp.tool()
async def fbo_posting_get(posting_number: str, translit: bool = False, with_data: Optional[Dict[str, Any]] = None) -> str:
    """Get detailed info about a single FBO shipment."""
    body = {"posting_number": posting_number, "translit": translit}
    if with_data: body["with"] = with_data
    return format_json_res(await ozon.post("/v2/posting/fbo/get", body))

@mcp.tool()
async def fbo_cancel_reason_list() -> str:
    """List cancellation reasons for FBO."""
    return format_json_res(await ozon.post("/v1/posting/fbo/cancel-reason/list", {}))

# ── Warehouse Tools ───────────────────────────────────────────────────────────

@mcp.tool()
async def warehouse_list() -> str:
    """List seller's warehouses."""
    return format_json_res(await ozon.post("/v1/warehouse/list", {}))

@mcp.tool()
async def warehouse_fbo_list() -> str:
    """List FBO warehouses."""
    return format_json_res(await ozon.post("/v1/warehouse/fbo/list", {}))

# ── Category Tools ───────────────────────────────────────────────────────────

@mcp.tool()
async def category_tree(category_id: int = 0, language: str = "DEFAULT") -> str:
    """Get product category tree."""
    body = {"language": language}
    if category_id: body["category_id"] = category_id
    return format_json_res(await ozon.post("/v1/category/tree", body))

@mcp.tool()
async def category_attributes(category_id: int, attribute_type: str = "ALL", language: str = "DEFAULT") -> str:
    """Get attributes for a product category."""
    body = {
        "category_id": [category_id],
        "attribute_type": attribute_type,
        "language": language,
    }
    return format_json_res(await ozon.post("/v1/category/attribute", body))

@mcp.tool()
async def category_attribute_values(category_id: int, attribute_id: int, limit: int = 100, last_value_id: int = 0) -> str:
    """Get dictionary values for a category attribute."""
    body = {"category_id": category_id, "attribute_id": attribute_id, "limit": limit}
    if last_value_id: body["last_value_id"] = last_value_id
    return format_json_res(await ozon.post("/v1/category/attribute/values", body))

# ── Analytics Tools ──────────────────────────────────────────────────────────

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

# ── Finance Tools ────────────────────────────────────────────────────────────

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

# ── Return Tools ─────────────────────────────────────────────────────────────

@mcp.tool()
async def returns_report_create(filter_type: str = "all", delivery_schema: str = "fbs") -> str:
    """Generate a returns report."""
    body = {"filter": {"filter_type": filter_type, "delivery_schema": delivery_schema}}
    return format_json_res(await ozon.post("/v2/report/returns/create", body))

# ── Chat Tools ───────────────────────────────────────────────────────────────

@mcp.tool()
async def chat_list(limit: int = 30, offset: int = 0, unread_only: bool = False) -> str:
    """List chats with buyers."""
    body = {"limit": limit, "offset": offset}
    if unread_only: body["filter"] = {"unread_only": True}
    return format_json_res(await ozon.post("/v1/chat/list", body))

@mcp.tool()
async def chat_history(chat_id: str, limit: int = 50, from_message_id: int = 0) -> str:
    """Get chat message history."""
    body = {"chat_id": chat_id, "limit": limit}
    if from_message_id: body["from_message_id"] = from_message_id
    return format_json_res(await ozon.post("/v1/chat/history", body))

@mcp.tool()
async def chat_send_message(chat_id: str, text: str) -> str:
    """Send a message in a chat."""
    return format_json_res(await ozon.post("/v1/chat/send/message", {"chat_id": chat_id, "text": text}))

@mcp.tool()
async def chat_start(posting_number: str) -> str:
    """Start a new chat by posting number."""
    return format_json_res(await ozon.post("/v1/chat/start", {"posting_number": posting_number}))

@mcp.tool()
async def chat_mark_read(chat_id: str) -> str:
    """Mark chat as read."""
    return format_json_res(await ozon.post("/v1/chat/updates", {"chat_id": chat_id}))

# ── Question Tools ───────────────────────────────────────────────────────────

@mcp.tool()
async def question_list(status: str = "NEW", sku: Optional[List[int]] = None, page: int = 1, page_size: int = 10) -> str:
    """List questions from buyers."""
    body = {"filter": {"status": status}, "page": page, "page_size": page_size}
    if sku: body["filter"]["sku"] = sku
    return format_json_res(await ozon.post("/v1/question/list", body))

@mcp.tool()
async def question_answer_list(question_id: Optional[int] = None, sku: Optional[int] = None, page: int = 1, page_size: int = 10) -> str:
    """List answers to questions."""
    body = {"page": page, "page_size": page_size}
    filt = {}
    if question_id: filt["question_id"] = question_id
    if sku: filt["sku"] = sku
    if filt: body["filter"] = filt
    return format_json_res(await ozon.post("/v1/question/answer/list", body))

@mcp.tool()
async def question_answer(question_id: int, text: str) -> str:
    """Send an answer to a question."""
    return format_json_res(await ozon.post("/v1/question/answer", {"question_id": question_id, "text": text}))

@mcp.tool()
async def question_skip(question_id: int) -> str:
    """Skip/hide a question."""
    return format_json_res(await ozon.post("/v1/question/skip", {"question_id": question_id}))

# ── Review Tools ────────────────────────────────────────────────────────────

@mcp.tool()
async def review_list(limit: int = 20, sort_dir: str = "DESC", last_id: str = "", is_answered: Optional[bool] = None) -> str:
    """List product reviews."""
    body = {"limit": limit, "sort_dir": sort_dir}
    if last_id: body["last_id"] = last_id
    if is_answered is not None: body["filter"] = {"is_answered": is_answered}
    return format_json_res(await ozon.post("/v1/review/list", body))

@mcp.tool()
async def review_info(review_id: str) -> str:
    """Get review details."""
    return format_json_res(await ozon.post("/v1/review/info", {"review_id": review_id}))

@mcp.tool()
async def review_reply(review_id: str, text: str) -> str:
    """Reply to a review."""
    return format_json_res(await ozon.post("/v1/review/comment/create", {"review_id": review_id, "text": text}))

# ── Rating Tools ───────────────────────────────────────────────────────────

@mcp.tool()
async def rating_summary() -> str:
    """Get current seller rating summary."""
    return format_json_res(await ozon.post("/v1/rating/summary", {}))

@mcp.tool()
async def rating_history(date_from: str, date_to: str) -> str:
    """Get seller rating for a period."""
    return format_json_res(await ozon.post("/v1/rating/history", {"date_from": date_from, "date_to": date_to}))

# ── Promotions Tools ─────────────────────────────────────────────────────────

@mcp.tool()
async def promotions_list() -> str:
    """List available promotions."""
    client = await ozon.get_client()
    try:
        resp = await client.get("/v1/actions")
        resp.raise_for_status()
        return format_json_res(resp.json())
    except Exception as e:
        return format_json_res({"error": str(e)})

@mcp.tool()
async def promotion_candidates(action_id: int, limit: int = 100, offset: int = 0) -> str:
    """Find products eligible for a promotion."""
    return format_json_res(await ozon.post("/v1/actions/candidates", {"action_id": action_id, "limit": limit, "offset": offset}))

@mcp.tool()
async def promotion_products(action_id: int, limit: int = 100, offset: int = 0) -> str:
    """Get products already in a promotion."""
    return format_json_res(await ozon.post("/v1/actions/products", {"action_id": action_id, "limit": limit, "offset": offset}))

@mcp.tool()
async def promotion_activate(action_id: int, products: List[Dict[str, Any]]) -> str:
    """Add products to a promotion."""
    return format_json_res(await ozon.post("/v1/actions/products/activate", {"action_id": action_id, "products": products}))

@mcp.tool()
async def promotion_deactivate(action_id: int, product_ids: List[int]) -> str:
    """Remove products from a promotion."""
    return format_json_res(await ozon.post("/v1/actions/products/deactivate", {"action_id": action_id, "product_ids": product_ids}))

# ── Custom Analysis Tools ────────────────────────────────────────────────────

@mcp.tool()
async def inventory_analysis_report() -> str:
    """
    Perform a comprehensive inventory analysis:
    1. Collects FBO stocks and recent FBO orders.
    2. Calculates sales velocity (burn rate) based on recent activity.
    3. Estimates stock longevity (days remaining) per warehouse and overall.
    4. Provides restocking recommendations.
    """
    # 1. Gather Data
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

    # 2. Process Inventory mapping
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

    # 3. Calculate Recent Orders per SKU
    sku_orders_recent = {}
    for order in fbo_orders:
        for prod in order.get("products", []):
            sku = prod.get("sku")
            qty = prod.get("quantity", 0)
            if sku:
                sku_orders_recent[sku] = sku_orders_recent.get(sku, 0) + qty

    # 4. Build the Report
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

# ── Execution ───────────────────────────────────────────────────────────────

def main():
    asyncio.run(_run())

async def _run():
    await mcp.run_stdio_async()

if __name__ == "__main__":
    main()
