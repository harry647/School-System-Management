"""
QR Code Generator Utility

This module provides functionality for generating QR codes for various
purposes in the school system, such as student IDs, book barcodes, etc.
"""

import qrcode
import io
from typing import Optional, Union
from PIL import Image


class QRGenerator:
    """A utility class for generating QR codes."""

    def __init__(self, version: int = 1, box_size: int = 10, border: int = 4):
        """
        Initialize the QRGenerator.

        Args:
            version: QR code version (1-40)
            box_size: Size of each box in pixels
            border: Border size in boxes
        """
        self.version = version
        self.box_size = box_size
        self.border = border

    def generate_qr_code(
        self, 
        data: str, 
        file_path: Optional[str] = None,
        fill_color: str = "black",
        back_color: str = "white"
    ) -> Union[str, io.BytesIO]:
        """
        Generate a QR code from the given data.

        Args:
            data: The data to encode in the QR code
            file_path: Optional path to save the QR code image
            fill_color: Foreground color of the QR code
            back_color: Background color of the QR code

        Returns:
            If file_path is provided, returns the file path.
            Otherwise, returns a BytesIO object containing the QR code image.
        """
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.box_size,
            border=self.border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        if file_path:
            img.save(file_path)
            return file_path
        else:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes

    def generate_qr_code_with_logo(
        self, 
        data: str,
        logo_path: str,
        file_path: Optional[str] = None,
        logo_size: int = 100
    ) -> Union[str, io.BytesIO]:
        """
        Generate a QR code with an embedded logo.

        Args:
            data: The data to encode in the QR code
            logo_path: Path to the logo image file
            file_path: Optional path to save the QR code image
            logo_size: Size of the logo in pixels

        Returns:
            If file_path is provided, returns the file path.
            Otherwise, returns a BytesIO object containing the QR code image.
        """
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=self.box_size,
            border=self.border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        logo = Image.open(logo_path)
        
        # Calculate position for the logo
        pos = ((qr_img.size[0] - logo_size) // 2, (qr_img.size[1] - logo_size) // 2)
        
        # Resize logo and paste it onto the QR code
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        qr_img.paste(logo, pos)
        
        if file_path:
            qr_img.save(file_path)
            return file_path
        else:
            img_bytes = io.BytesIO()
            qr_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes
