from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from rembg import remove
from PIL import Image
import pillow_heif
import io

app = FastAPI(title="Arka Plan Kaldırma API'si")

# HEIF/HEIC desteği için register
pillow_heif.register_heif_opener()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'heic', 'heif'}

def is_valid_image(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # Dosya türü kontrolü
    if not is_valid_image(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Sadece PNG, JPG, JPEG, WEBP, HEIC ve HEIF formatları desteklenmektedir."
        )
    
    try:
        # Yüklenen dosyayı oku
        image_data = await file.read()
        
        # Bytes'ı PIL Image'a dönüştür
        input_image = Image.open(io.BytesIO(image_data))
        
        # Arka planı kaldır
        output_image = remove(input_image)
        
        # Çıktıyı PNG formatında bytes'a dönüştür
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(
            content=img_byte_arr, 
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=removed_bg_{file.filename.rsplit('.', 1)[0]}.png"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Görsel işlenirken bir hata oluştu: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)