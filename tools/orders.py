"""
Order related tools for Ozon MCP.
"""
from typing import Any, Dict, List, Optional
from ..client import OzonClient
from ..utils import format_json_res

async def register_orders_tools(mcp, ozon: OzonClient):

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
