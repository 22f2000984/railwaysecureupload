from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import csv, io, os

app = FastAPI()

# ✅ CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)

# ✅ FORCE CORS on ALL errors (CRITICAL)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "*"},
    )

@app.options("/upload")
async def options_upload():
    return Response(
        status_code=200,
        headers={"Access-Control-Allow-Origin": "*"},
    )

MAX_SIZE = 91 * 1024
ALLOWED_EXT = {".csv", ".json", ".txt"}
TOKEN = "o16hrb3objnq5ic8"

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    x_upload_token_3056: str = Header(None)
):
    if x_upload_token_3056 != TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Invalid file type")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

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
