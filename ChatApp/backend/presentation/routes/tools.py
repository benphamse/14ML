from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/api/tools")
async def list_tools(request: Request):
    use_case = request.app.state.list_tools_use_case
    return {"tools": use_case.execute()}
