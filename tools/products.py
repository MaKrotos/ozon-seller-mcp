"""
Product related tools for Ozon MCP.
"""
from typing import Any, Dict, List, Optional
from ..client import OzonClient
from ..utils import format_json_res

async def register_products_tools(mcp, ozon: OzonClient):
    
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
