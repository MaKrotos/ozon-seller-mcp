"""MCP server for Ozon Seller API (api-seller.ozon.ru)."""

import os
import json
import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ozon-seller")

BASE_URL = "https://api-seller.ozon.ru"
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        client_id = os.environ.get("OZON_CLIENT_ID", "")
        api_key = os.environ.get("OZON_API_KEY", "")
        if not client_id or not api_key:
            raise ValueError(
                "OZON_CLIENT_ID and OZON_API_KEY environment variables are required"
            )
        _client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={
                "Client-Id": client_id,
                "Api-Key": api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
    return _client


async def _post(path: str, body: dict | None = None) -> str:
    """Make a POST request to Ozon Seller API and return JSON string."""
    client = _get_client()
    try:
        resp = await client.post(path, json=body or {})
        resp.raise_for_status()
        return json.dumps(resp.json(), ensure_ascii=False, indent=2)
    except httpx.HTTPStatusError as e:
        error_body = e.response.text
        return json.dumps(
            {"error": f"HTTP {e.response.status_code}", "detail": error_body},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Products ─────────────────────────────────────────────────────────────────


@mcp.tool()
async def product_list(
    limit: int = 100,
    last_id: str = "",
    offer_id_filter: list[str] | None = None,
    product_id_filter: list[int] | None = None,
    visibility: str = "ALL",
) -> str:
    """List seller's products. Visibility: ALL, VISIBLE, INVISIBLE, EMPTY_STOCK, NOT_MODERATED, MODERATED, DISABLED, STATE_FAILED, READY_TO_SUPPLY, VALIDATION_STATE_PENDING, VALIDATION_STATE_FAIL, VALIDATION_STATE_SUCCESS, TO_SUPPLY, IN_SALE, REMOVED_FROM_SALE, BAN_REASON_DUPLICATE_DESCRIPTION, BAN_REASON_MANUAL, BAN_REASON_LEGAL."""
    body: dict = {"limit": limit, "visibility": visibility}
    if last_id:
        body["last_id"] = last_id
    filt: dict = {}
    if offer_id_filter:
        filt["offer_id"] = offer_id_filter
    if product_id_filter:
        filt["product_id"] = product_id_filter
    if filt:
        body["filter"] = filt
    return await _post("/v3/product/list", body)


@mcp.tool()
async def product_info(product_id: int = 0, offer_id: str = "", sku: int = 0) -> str:
    """Get detailed info about a single product by product_id, offer_id, or sku."""
    body: dict = {}
    if product_id:
        body["product_id"] = product_id
    if offer_id:
        body["offer_id"] = offer_id
    if sku:
        body["sku"] = sku
    return await _post("/v2/product/info", body)


@mcp.tool()
async def product_info_list(product_id: list[int] | None = None, offer_id: list[str] | None = None) -> str:
    """Get detailed info for multiple products (prices, barcode, moderation status). Provide product_id list or offer_id list."""
    body: dict = {}
    if product_id:
        body["product_id"] = product_id
    if offer_id:
        body["offer_id"] = offer_id
    return await _post("/v3/product/info/list", body)


@mcp.tool()
async def product_info_attributes(
    product_id: list[int] | None = None,
    offer_id: list[str] | None = None,
    limit: int = 100,
    last_id: str = "",
    sort_by: str = "",
    sort_dir: str = "ASC",
) -> str:
    """Get product attributes/characteristics."""
    body: dict = {"limit": limit}
    filt: dict = {}
    if product_id:
        filt["product_id"] = product_id
    if offer_id:
        filt["offer_id"] = offer_id
    if filt:
        body["filter"] = filt
    if last_id:
        body["last_id"] = last_id
    if sort_by:
        body["sort_by"] = sort_by
        body["sort_dir"] = sort_dir
    return await _post("/v4/product/info/attributes", body)


@mcp.tool()
async def product_import(items: list[dict]) -> str:
    """Import/create/update products. Each item dict should contain: name, offer_id, category_id, price, vat, attributes, etc. Returns task_id for async tracking. Max 100 items."""
    return await _post("/v3/product/import", {"items": items})


@mcp.tool()
async def product_import_info(task_id: int) -> str:
    """Check the status of a product import task by task_id."""
    return await _post("/v1/product/import/info", {"task_id": task_id})


@mcp.tool()
async def product_archive(product_id: list[int]) -> str:
    """Archive products by their IDs."""
    return await _post("/v1/product/archive", {"product_id": product_id})


@mcp.tool()
async def product_unarchive(product_id: list[int]) -> str:
    """Unarchive products by their IDs."""
    return await _post("/v1/product/unarchive", {"product_id": product_id})


@mcp.tool()
async def product_delete(product_id: list[int]) -> str:
    """Delete products that haven't been assigned an SKU yet."""
    return await _post("/v2/products/delete", {"product_id": product_id})


@mcp.tool()
async def product_description(product_id: int = 0, offer_id: str = "") -> str:
    """Get product description."""
    body: dict = {}
    if product_id:
        body["product_id"] = product_id
    if offer_id:
        body["offer_id"] = offer_id
    return await _post("/v1/product/info/description", body)


@mcp.tool()
async def product_attributes_update(items: list[dict]) -> str:
    """Update product attributes. Each item: {product_id, attributes: [{id, values: [{value, dictionary_value_id}]}]}."""
    return await _post("/v1/product/attributes/update", {"items": items})


@mcp.tool()
async def product_pictures_import(product_id: int, images: list[str]) -> str:
    """Upload product images by URLs. images is a list of image URLs."""
    return await _post(
        "/v1/product/pictures/import",
        {"product_id": product_id, "images": images},
    )


# ── Prices ───────────────────────────────────────────────────────────────────


@mcp.tool()
async def prices_info(
    product_id_filter: list[int] | None = None,
    offer_id_filter: list[str] | None = None,
    limit: int = 100,
    last_id: str = "",
) -> str:
    """Get prices, commissions, and marketing data for products."""
    body: dict = {"limit": limit}
    filt: dict = {}
    if product_id_filter:
        filt["product_id"] = product_id_filter
    if offer_id_filter:
        filt["offer_id"] = offer_id_filter
    if filt:
        body["filter"] = filt
    if last_id:
        body["last_id"] = last_id
    return await _post("/v5/product/info/prices", body)


@mcp.tool()
async def prices_update(prices: list[dict]) -> str:
    """Update product prices. Each item: {product_id, price, old_price, min_price, auto_action_enabled, currency_code}. Max 1000 items. Rate limit: 10 updates/hour per product."""
    return await _post("/v1/product/import/prices", {"prices": prices})


# ── Stocks ───────────────────────────────────────────────────────────────────


@mcp.tool()
async def stocks_info(
    product_id_filter: list[int] | None = None,
    offer_id_filter: list[str] | None = None,
    limit: int = 100,
    last_id: str = "",
) -> str:
    """Get FBS/rFBS stock levels for products."""
    body: dict = {"limit": limit}
    filt: dict = {}
    if product_id_filter:
        filt["product_id"] = product_id_filter
    if offer_id_filter:
        filt["offer_id"] = offer_id_filter
    if filt:
        body["filter"] = filt
    if last_id:
        body["last_id"] = last_id
    return await _post("/v4/product/info/stocks", body)


@mcp.tool()
async def stocks_update(stocks: list[dict]) -> str:
    """Update stock quantities. Each item: {offer_id, product_id, stock, warehouse_id}. Max 100 items. Rate limit: 80 req/min."""
    return await _post("/v2/products/stocks", {"stocks": stocks})


@mcp.tool()
async def stocks_by_warehouse_fbs(sku: list[int]) -> str:
    """Get FBS stock by warehouse for given SKUs."""
    return await _post("/v1/product/info/stocks-by-warehouse/fbs", {"sku": sku})


# ── FBS Orders (Fulfilled by Seller) ────────────────────────────────────────


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
    """List unprocessed FBS shipments. Status: awaiting_packaging, awaiting_deliver, arbitration, delivering, driver_pickup, delivered, cancelled."""
    body: dict = {"limit": limit, "offset": offset, "dir": sort_dir, "sort_by": sort_by}
    filt: dict = {}
    if status:
        filt["status"] = status
    if cutoff_from:
        filt["cutoff_from"] = cutoff_from
    if cutoff_to:
        filt["cutoff_to"] = cutoff_to
    if delivering_date_from:
        filt["delivering_date_from"] = delivering_date_from
    if delivering_date_to:
        filt["delivering_date_to"] = delivering_date_to
    if filt:
        body["filter"] = filt
    return await _post("/v3/posting/fbs/unfulfilled/list", body)


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
    """List FBS shipments with filters. Dates in RFC3339 format (2024-01-01T00:00:00Z)."""
    body: dict = {"limit": limit, "offset": offset, "dir": sort_dir}
    filt: dict = {}
    if since:
        filt["since"] = since
    if to:
        filt["to"] = to
    if status:
        filt["status"] = status
    if filt:
        body["filter"] = filt
    return await _post("/v3/posting/fbs/list", body)


@mcp.tool()
async def fbs_posting_get(posting_number: str) -> str:
    """Get detailed info about a single FBS shipment by posting number."""
    return await _post("/v3/posting/fbs/get", {"posting_number": posting_number})


@mcp.tool()
async def fbs_ship(posting_number: str, packages: list[dict]) -> str:
    """Pack and confirm FBS shipment. packages: [{products: [{product_id, quantity}]}]."""
    return await _post(
        "/v2/posting/fbs/ship",
        {"posting_number": posting_number, "packages": packages},
    )


@mcp.tool()
async def fbs_cancel(posting_number: str, cancel_reason_id: int, cancel_reason_message: str = "") -> str:
    """Cancel an FBS shipment."""
    body: dict = {
        "posting_number": posting_number,
        "cancel_reason_id": cancel_reason_id,
    }
    if cancel_reason_message:
        body["cancel_reason_message"] = cancel_reason_message
    return await _post("/v2/posting/fbs/cancel", body)


@mcp.tool()
async def fbs_cancel_reasons() -> str:
    """Get list of available cancellation reasons for FBS."""
    return await _post("/v1/posting/fbs/cancel-reason")


@mcp.tool()
async def fbs_package_label(posting_number: list[str]) -> str:
    """Generate PDF shipping labels for FBS postings. Returns base64-encoded PDF. Max 20 postings."""
    return await _post("/v2/posting/fbs/package-label", {"posting_number": posting_number})


@mcp.tool()
async def fbs_set_tracking_number(posting_number: str, tracking_number: str) -> str:
    """Set tracking number for an FBS shipment."""
    return await _post(
        "/v2/posting/fbs/tracking-number/set",
        {"posting_number": posting_number, "tracking_number": tracking_number},
    )


@mcp.tool()
async def fbs_act_create(delivery_method_id: int, departure_date: str) -> str:
    """Create a transfer certificate (act) for FBS delivery."""
    return await _post(
        "/v2/posting/fbs/act/create",
        {"delivery_method_id": delivery_method_id, "departure_date": departure_date},
    )


@mcp.tool()
async def fbs_act_check_status(id: int) -> str:
    """Check status of a transfer certificate generation."""
    return await _post("/v2/posting/fbs/act/check-status", {"id": id})


# ── FBO Postings ────────────────────────────────────────────────────────────

@mcp.tool()
async def fbo_posting_list(
    limit: int = 50,
    cursor: str = "",
    filter: dict | None = None,
    sort_dir: str = "ASC",
    translit: bool = False,
    with_data: dict | None = None,
) -> str:
    """List FBO shipments. Use filter for since, to, statuses, and posting_numbers. Dates in RFC3339 format."""
    body: dict = {"limit": limit, "cursor": cursor, "sort_dir": sort_dir, "translit": translit}
    if filter:
        body["filter"] = filter
    if with_data:
        body["with"] = with_data
    return await _post("/v3/posting/fbo/list", body)


@mcp.tool()
async def fbo_posting_get(posting_number: str, translit: bool = False, with_data: dict | None = None) -> str:
    """Get detailed info about a single FBO shipment by posting number."""
    body: dict = {"posting_number": posting_number, "translit": translit}
    if with_data:
        body["with"] = with_data
    return await _post("/v2/posting/fbo/get", body)


@mcp.tool()
async def fbo_cancel_reason_list() -> str:
    """Get list of cancellation reasons for FBO shipments."""
    return await _post("/v1/posting/fbo/cancel-reason/list")


# ── Warehouses ───────────────────────────────────────────────────────────────


@mcp.tool()
async def warehouse_list() -> str:
    """List seller's warehouses."""
    return await _post("/v1/warehouse/list")


@mcp.tool()
async def warehouse_fbo_list() -> str:
    """List FBO (Ozon) warehouses."""
    return await _post("/v1/warehouse/fbo/list")


# ── Categories ───────────────────────────────────────────────────────────────


@mcp.tool()
async def category_tree(category_id: int = 0, language: str = "DEFAULT") -> str:
    """Get the product category tree. Optionally specify parent category_id."""
    body: dict = {"language": language}
    if category_id:
        body["category_id"] = category_id
    return await _post("/v1/category/tree", body)


@mcp.tool()
async def category_attributes(
    category_id: int, attribute_type: str = "ALL", language: str = "DEFAULT"
) -> str:
    """Get attributes for a product category."""
    return await _post(
        "/v1/category/attribute",
        {
            "category_id": [category_id],
            "attribute_type": attribute_type,
            "language": language,
        },
    )


@mcp.tool()
async def category_attribute_values(
    category_id: int, attribute_id: int, limit: int = 100, last_value_id: int = 0
) -> str:
    """Get dictionary values for a category attribute."""
    body: dict = {
        "category_id": category_id,
        "attribute_id": attribute_id,
        "limit": limit,
    }
    if last_value_id:
        body["last_value_id"] = last_value_id
    return await _post("/v1/category/attribute/values", body)


# ── Analytics ────────────────────────────────────────────────────────────────


@mcp.tool()
async def analytics_data(
    date_from: str,
    date_to: str,
    metrics: list[str],
    dimension: list[str],
    limit: int = 100,
    offset: int = 0,
    sort: list[dict] | None = None,
    filters: list[dict] | None = None,
) -> str:
    """Get analytical data. Metrics: revenue, ordered_units, hits_view, hits_tocart, session_view, conv_tocart_percent, returns, cancellations, delivered_units, adv_sum_all, position_category. Dimensions: sku, spu, day, week, month, year, category1-4, brand."""
    body: dict = {
        "date_from": date_from,
        "date_to": date_to,
        "metrics": metrics,
        "dimension": dimension,
        "limit": limit,
        "offset": offset,
    }
    if sort:
        body["sort"] = sort
    if filters:
        body["filters"] = filters
    return await _post("/v1/analytics/data", body)


@mcp.tool()
async def analytics_stocks(limit: int = 100, offset: int = 0, warehouse_type: str = "") -> str:
    """Get stock on warehouses report."""
    body: dict = {"limit": limit, "offset": offset}
    if warehouse_type:
        body["warehouse_type"] = warehouse_type
    return await _post("/v2/analytics/stock_on_warehouses", body)


# ── Finance ──────────────────────────────────────────────────────────────────


@mcp.tool()
async def finance_transactions(
    date_from: str,
    date_to: str,
    operation_type: list[str] | None = None,
    posting_number: str = "",
    transaction_type: str = "all",
    page: int = 1,
    page_size: int = 50,
) -> str:
    """Get detailed financial transactions. Max 1-month window. Dates: YYYY-MM-DD. operation_type: OperationAgentDeliveredToCustomer, OperationReturnGoodsToSeller, etc."""
    body: dict = {
        "filter": {
            "date": {"from": f"{date_from}T00:00:00.000Z", "to": f"{date_to}T23:59:59.999Z"},
            "transaction_type": transaction_type,
        },
        "page": page,
        "page_size": page_size,
    }
    if operation_type:
        body["filter"]["operation_type"] = operation_type
    if posting_number:
        body["filter"]["posting_number"] = posting_number
    return await _post("/v3/finance/transaction/list", body)


@mcp.tool()
async def finance_totals(date_from: str, date_to: str) -> str:
    """Get aggregated financial transaction totals for a period. Dates: YYYY-MM-DD."""
    return await _post(
        "/v3/finance/transaction/totals",
        {
            "date": {
                "from": f"{date_from}T00:00:00.000Z",
                "to": f"{date_to}T23:59:59.999Z",
            }
        },
    )


@mcp.tool()
async def finance_realization(date: str) -> str:
    """Get monthly sales/returns report. date: YYYY-MM (year-month)."""
    return await _post("/v2/finance/realization", {"date": date})


# ── Returns ──────────────────────────────────────────────────────────────────


@mcp.tool()
async def returns_report_create(
    filter_type: str = "all", delivery_schema: str = "fbs"
) -> str:
    """Generate a returns report. filter_type: all, created, received, completed. delivery_schema: fbs, fbo."""
    return await _post(
        "/v2/report/returns/create",
        {"filter": {"filter_type": filter_type, "delivery_schema": delivery_schema}},
    )


# ── Chats ────────────────────────────────────────────────────────────────────


@mcp.tool()
async def chat_list(limit: int = 30, offset: int = 0, unread_only: bool = False) -> str:
    """List chats with buyers."""
    body: dict = {"limit": limit, "offset": offset}
    if unread_only:
        body["filter"] = {"unread_only": True}
    return await _post("/v1/chat/list", body)


@mcp.tool()
async def chat_history(chat_id: str, limit: int = 50, from_message_id: int = 0) -> str:
    """Get chat message history."""
    body: dict = {"chat_id": chat_id, "limit": limit}
    if from_message_id:
        body["from_message_id"] = from_message_id
    return await _post("/v1/chat/history", body)


@mcp.tool()
async def chat_send_message(chat_id: str, text: str) -> str:
    """Send a message in a chat with a buyer."""
    return await _post("/v1/chat/send/message", {"chat_id": chat_id, "text": text})


@mcp.tool()
async def chat_start(posting_number: str) -> str:
    """Start a new chat with a buyer by posting number."""
    return await _post("/v1/chat/start", {"posting_number": posting_number})


@mcp.tool()
async def chat_mark_read(chat_id: str) -> str:
    """Mark chat as read."""
    return await _post("/v1/chat/updates", {"chat_id": chat_id})


# ── Questions ────────────────────────────────────────────────────────────────


@mcp.tool()
async def question_list(
    status: str = "NEW",
    sku: list[int] | None = None,
    page: int = 1,
    page_size: int = 10,
) -> str:
    """List questions from buyers. Status: NEW, ANSWERED, PROCESSED, SKIPPED."""
    body: dict = {
        "filter": {"status": status},
        "page": page,
        "page_size": page_size,
    }
    if sku:
        body["filter"]["sku"] = sku
    return await _post("/v1/question/list", body)


@mcp.tool()
async def question_answer_list(
    question_id: int | None = None,
    sku: int | None = None,
    page: int = 1,
    page_size: int = 10,
) -> str:
    """List answers to questions."""
    body: dict = {
        "page": page,
        "page_size": page_size,
    }
    filt: dict = {}
    if question_id:
        filt["question_id"] = question_id
    if sku:
        filt["sku"] = sku
    if filt:
        body["filter"] = filt
    return await _post("/v1/question/answer/list", body)


@mcp.tool()
async def question_answer(question_id: int, text: str) -> str:
    """Send an answer to a specific question."""
    return await _post(
        "/v1/question/answer",
        {"question_id": question_id, "text": text},
    )


@mcp.tool()
async def question_skip(question_id: int) -> str:
    """Skip/hide a question (e.g., spam or incorrect)."""
    return await _post(
        "/v1/question/skip",
        {"question_id": question_id},
    )


# ── Reviews ──────────────────────────────────────────────────────────────────


@mcp.tool()
async def review_list(
    limit: int = 20,
    sort_dir: str = "DESC",
    last_id: str = "",
    is_answered: bool | None = None,
) -> str:
    """List product reviews."""
    body: dict = {"limit": limit, "sort_dir": sort_dir}
    if last_id:
        body["last_id"] = last_id
    if is_answered is not None:
        body["filter"] = {"is_answered": is_answered}
    return await _post("/v1/review/list", body)


@mcp.tool()
async def review_info(review_id: str) -> str:
    """Get details of a single review."""
    return await _post("/v1/review/info", {"review_id": review_id})


@mcp.tool()
async def review_reply(review_id: str, text: str) -> str:
    """Reply to a product review."""
    return await _post(
        "/v1/review/comment/create", {"review_id": review_id, "text": text}
    )


# ── Rating ────────────────────────────────────────────────────────────────S


@mcp.tool()
async def rating_summary() -> str:
    """Get current seller rating summary."""
    return await _post("/v1/rating/summary")


@mcp.tool()
async def rating_history(date_from: str, date_to: str) -> str:
    """Get seller rating for a period. Dates: YYYY-MM-DD."""
    return await _post(
        "/v1/rating/history",
        {"date_from": date_from, "date_to": date_to},
    )


# ── Promotions ───────────────────────────────────────────────────────────────


@mcp.tool()
async def promotions_list() -> str:
    """List available promotions."""
    client = _get_client()
    try:
        resp = await client.get("/v1/actions")
        resp.raise_for_status()
        return json.dumps(resp.json(), ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
async def promotion_candidates(action_id: int, limit: int = 100, offset: int = 0) -> str:
    """Find products eligible for a promotion."""
    return await _post(
        "/v1/actions/candidates",
        {"action_id": action_id, "limit": limit, "offset": offset},
    )


@mcp.tool()
async def promotion_products(action_id: int, limit: int = 100, offset: int = 0) -> str:
    """Get products already in a promotion."""
    return await _post(
        "/v1/actions/products",
        {"action_id": action_id, "limit": limit, "offset": offset},
    )


@mcp.tool()
async def promotion_activate(action_id: int, products: list[dict]) -> str:
    """Add products to a promotion. products: [{product_id, action_price}]."""
    return await _post(
        "/v1/actions/products/activate",
        {"action_id": action_id, "products": products},
    )


@mcp.tool()
async def promotion_deactivate(action_id: int, product_ids: list[int]) -> str:
    """Remove products from a promotion."""
    return await _post(
        "/v1/actions/products/deactivate",
        {"action_id": action_id, "product_ids": product_ids},
    )


# ── Entry point ──────────────────────────────────────────────────────────────


@mcp.tool()
async def inventory_analysis_report() -> str:
    """
    Perform a comprehensive inventory analysis:
    1. Collects FBO stocks and recent FBO orders.
    2. Calculates sales velocity (burn rate) based on recent activity.
    3. Estimates stock longevity (days remaining).
    4. Provides restocking recommendations (URGENT, PLAN, or Sufficient).
    Returns a formatted text report.
    """
    # 1. Gather Data
    # Stocks
    stocks_res = await analytics_stocks(warehouse_type="FBO")
    try:
        stocks_data = json.loads(stocks_res)
        fbo_rows = stocks_data.get("result", {}).get("rows", [])
    except:
        return "Error parsing stocks data"

    # Recent Orders (Last 7 days)
    from datetime import datetime, timedelta
    since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    orders_res = await fbo_posting_list(since=since_date)
    try:
        orders_data = json.loads(orders_res)
        fbo_orders = orders_data.get("result", [])
    except:
        fbo_orders = []

    # 2. Process Inventory
    inventory = {}
    for row in fbo_rows:
        sku = row["sku"]
        warehouse = row.get("warehouse_name", "Unknown Warehouse")
        if sku not in inventory:
            inventory[sku] = {
                "name": row.get("item_name", "Unknown"),
                "item_code": row.get("item_code", "Unknown"),
                "stocks": {}, # Dictionary to store stocks per warehouse
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

    # 4. Generate Report
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
        
        # Recommendations based on total stock
        if longevity < 14:
            rec = "URGENT RESTOCK"
        elif longevity < 30:
            rec = "PLAN RESTOCK"
        else:
            rec = "Sufficient"
        
        report.append(f"   -> Total Stock: {total_free} | Longevity: {longevity:.1f} days | Recommendation: {rec}")
        report.append("-" * 110)

    return "\n".join(report)



def main():
    import asyncio
    asyncio.run(_run())


async def _run():
    await mcp.run_stdio_async()


if __name__ == "__main__":
    main()
