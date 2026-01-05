import json
from fastapi import APIRouter, Depends, Request, Query, UploadFile, File, HTTPException
from fastapi.responses import Response, StreamingResponse

from backend.database.connection import get_db
from backend.dependencies import get_or_create_session_id
from backend.services import save_and_load_service

# All paths start with /save_and_load
router = APIRouter(prefix="/save_and_load", tags=["Save and Load"])

@router.get("/export")
def export_session(
    format: str = Query(..., regex="^(json|csv|full_json)$"),
    request: Request = None,
    conn=Depends(get_db)
):
    session_id = get_or_create_session_id(request)
    
    if format == "csv":
        filename = "hinteval_session.csv"
        stream = save_and_load_service.export_session_csv_stream(conn, session_id)
        return StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    elif format == "full_json":
        filename = "hinteval_dataset_full.json"
        data = save_and_load_service.export_session_json(conn, session_id, full_export=True)
        json_str = json.dumps(data, indent=2)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    else:
        filename = "hinteval_session.json"
        data = save_and_load_service.export_session_json(conn, session_id, full_export=False)
        json_str = json.dumps(data, indent=2)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

@router.post("/import")
async def import_session(
    file: UploadFile = File(...),
    request: Request = None,
    conn=Depends(get_db)
):
    session_id = get_or_create_session_id(request)
    
    try:
        content = await file.read()
        filename = file.filename.lower()
        parsed_data = {}

        if filename.endswith(".json"):
            try:
                parsed_data = json.loads(content.decode('utf-8'))
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON file format.")
        elif filename.endswith(".csv"):
            try:
                parsed_data = save_and_load_service.parse_csv_to_dict(content)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"CSV Parsing Error: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use .json or .csv")

        save_and_load_service.clear_session_data(conn, session_id)
        result = save_and_load_service.insert_imported_data(conn, session_id, parsed_data)
        
        return {"status": "success", **result}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Import Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during import.")