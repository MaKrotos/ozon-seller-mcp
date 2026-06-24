"""
Communication related tools for Ozon MCP.
"""
from typing import Any, Dict, List, Optional
from ..client import OzonClient
from ..utils import format_json_res

async def register_communication_tools(mcp, ozon: OzonClient):

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

    @mcp.tool()
    async def rating_summary() -> str:
        """Get current seller rating summary."""
        return format_json_res(await ozon.post("/v1/rating/summary", {}))

    @mcp.tool()
    async def rating_history(date_from: str, date_to: str) -> str:
        """Get seller rating for a period."""
        return format_json_res(await ozon.post("/v1/rating/history", {"date_from": date_from, "date_to": date_to}))
