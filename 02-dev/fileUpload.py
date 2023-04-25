import io
import requests
from fastapi import FastAPI, UploadFile, File
from weaviate import Client
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from pdfminer import high_level
from pdfminer import layout
from pdfminer.pdfpage import PDFPage

app = FastAPI(
    title="API To Upload Credit Documents",
    description="API To Upload Credit Documents",
    version="0.0.1",
    contact={"name": "Rahul Kiran Gaddam", "email": "gaddam.rahul@gmail.com"},
    license_info={"name": "Apache 2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0.html"},
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

def read_pdf(file):
    result = []
    with io.BytesIO(file) as data:
        laparams = pdfminer.layout.LAParams()
        with pdfminer.high_level.PDFResourceManager() as mgr:
            with pdfminer.high_level.PDFPageInterpreter(mgr) as interp:
                with pdfminer.pdfpage.PDFPage.get_pages(data, caching=True, check_extractable=True) as pages:
                    for page in pages:
                        interp.process_page(page)
                        layout = interp.get_result()
                        text = ''
                        for lt_obj in layout:
                            if isinstance(lt_obj, pdfminer.layout.LTTextBoxHorizontal):
                                text += lt_obj.get_text()
                        result.append({'text': text})
    return result

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    text = read_pdf(contents)
    client = Client("http://localhost:8080")
    # client.auth.create_token(username="admin", password="password")
    client.data_object.create({"text": text}, "PDF", ["PDF"])
    return {"status": "success"}

@app.get("/docs", response_class=HTMLResponse)
async def get_documentation():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>API Documentation</title>
            <!-- import Swagger UI CSS -->
            <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css">
        </head>
        <body>
            <!-- add Swagger UI container -->
            <div id="swagger-ui"></div>
            <!-- import Swagger UI JS -->
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-standalone-preset.js"></script>  <!-- Add this line to import the Standalone preset -->
            <script>
                // Build a system
                const ui = SwaggerUIBundle({
                    url: "/api/v1/openapi.json",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset   <!-- Update this line to use the Standalone preset -->
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout"
                })
            </script>
        </body>
    </html>
    """