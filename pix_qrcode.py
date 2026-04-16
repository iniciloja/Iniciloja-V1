import qrcode
import io
import base64
from typing import Dict

def generate_pix_qrcode(
    pix_key: str,
    amount: float,
    transaction_id: str,
    merchant_name: str
) -> Dict[str, str]:
    pix_code = f"PIX|{pix_key}|{amount:.2f}|{transaction_id}|{merchant_name}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(pix_code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "pix_code": pix_code,
        "qr_code_base64": img_base64
    }
