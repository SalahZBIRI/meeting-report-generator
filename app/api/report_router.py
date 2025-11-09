from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.report_service import generate_report
import tempfile, shutil, os

router = APIRouter(prefix="/report", tags=["Report Generator"])
#POST endpoint to generate a meeting report from an uploaded audio file
@router.post("/generate")
async def generate_meeting_report(file: UploadFile = File(...)):
    # Validate the file extension (only supported audio formats)
    allowed_extensions = (".wav", ".mp3", ".m4a", ".ogg")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed extensions: {', '.join(allowed_extensions)}"
        )

    tmp = None
    try:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            shutil.copyfileobj(file.file, tmp)
            audio_path = tmp.name

        # generate report
        result = generate_report(audio_path)

        # check the output
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "summary": result.get("summary", "Summary not available."),
            "pdf_path": result.get("pdf_path", None),
            "language": result.get("language", "unknown"),
        }

    except HTTPException:
        raise
    except Exception as e:
        # Catch any unexpected error during processing
        print(f"Error during report generation: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"Internal error : {e}")
    finally:
        if tmp and os.path.exists(tmp.name):
            try:
                os.remove(tmp.name)
            except Exception as cleanup_err:
                print(f"Could not remove temporary file: {cleanup_err}", flush=True)