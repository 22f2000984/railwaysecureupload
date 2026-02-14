from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response
import csv, io, os

app = FastAPI()

# 🔒 Constants
MAX_SIZE = 91 * 1024
ALLOWED_EXT = {".csv", ".json", ".txt"}
TOKEN = "o16hrb3objnq5ic8"

# ✅ Add CORS headers to EVERY response
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# ✅ OPTIONS preflight (REQUIRED)
@app.options("/upload")
async def options_upload():
    return Response(status_code=200)

# ✅ Force CORS on ALL errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "*"},
    )

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    x_upload_token_3056: str = Header(None)
):
    # Auth
    if x_upload_token_3056 != TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Invalid file type")

    data = await file.read()

    # Size
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # CSV processing
    if ext == ".csv":
        reader = csv.DictReader(io.StringIO(data.decode("utf-8")))
        rows = list(reader)

        total = 0.0
        counts = {}
        for r in rows:
            total += float(r.get("value", 0))
            c = r.get("category")
            if c:
                counts[c] = counts.get(c, 0) + 1

        return {
            "email": "22f2000984@ds.study.iitm.ac.in",
            "filename": file.filename,
            "rows": len(rows),
            "columns": reader.fieldnames,
            "totalValue": round(total, 2),
            "categoryCounts": counts
        }

    return {"message": "File accepted"}
