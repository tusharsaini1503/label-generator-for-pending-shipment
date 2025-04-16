import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
import barcode
from barcode.writer import ImageWriter
from fpdf import FPDF
import os

# Load data
csv_path = "Pending_shipment.csv"
df = pd.read_csv(csv_path)

# Output directory
output_dir = "labels"
os.makedirs(output_dir, exist_ok=True)

# Static values
return_address = "M.A.GARMENTS (STYLEHUB.GARMENTS)\nBlock E 33 welcome seelmpur Near Suresh Dhaba, Delhi, Pincode 110053\nNear Suresh Dhaba\nShahdara, Delhi, 110053"
courier = "Valmo"
hub_code = "KRH-R0"
sku = "WkheeeBT07"
size = "30"
qty = "1"
color = "White"

# Fonts
font_path = "C:/Windows/Fonts/arial.ttf"
font = ImageFont.truetype(font_path, 20)
small_font = ImageFont.truetype(font_path, 16)
tiny_font = ImageFont.truetype(font_path, 14)

# PDF setup
pdf = FPDF()

for idx, row in df.iterrows():
    img = Image.new('RGB', (1000, 600), color='white')
    draw = ImageDraw.Draw(img)

    # Borders
    draw.rectangle([10, 10, 990, 590], outline="black", width=2)  # Outer border
    draw.line([(500, 10), (500, 370)], fill="black", width=2)     # Vertical split
    draw.line([(10, 180), (500, 180)], fill="black", width=1)     # Horizontal split in left
    draw.rectangle([10, 370, 990, 460], outline="black", width=2)  # Product details box
    draw.line([(10, 460), (990, 460)], fill="black", width=1)     # Footer line under product details

    # Address section
    draw.text((20, 20), f"Customer Address\n{row['Consignee_Name']}\n{row['Destination_City']}, {row['Destination Pincode']}", font=font, fill='black')
    draw.text((20, 190), f"If undelivered, return to:\n{return_address}", font=small_font, fill='black')

    # Courier section
    draw.text((520, 30), f"{courier}", font=font, fill='black')
    draw.text((520, 70), hub_code, font=font, fill='black')

    # QR code
    qr = qrcode.make(row['Waybill_No'])
    qr = qr.resize((150, 150))
    img.paste(qr, (800, 30))

    # Barcode
    CODE128 = barcode.get_barcode_class('code128')
    code128 = CODE128(str(row['Waybill_No']), writer=ImageWriter())
    barcode_img = code128.render(writer_options={'module_height': 15, 'text_distance': 1})
    barcode_img = barcode_img.resize((350, 80))
    barcode_x = 620
    barcode_y = 230
    img.paste(barcode_img, (barcode_x, barcode_y))

    # Tracking number under barcode
    draw.text((barcode_x + 20, barcode_y + 85), row['Waybill_No'], font=small_font, fill='black')

    # Product details
    order_no = f"{134127939703703744 + idx}_1"
    draw.text((30, 380), f"Product Details", font=font, fill='black')
    draw.text((30, 410), f"SKU     {sku}", font=small_font, fill='black')
    draw.text((300, 410), f"Size     {size}     Qty     {qty}     Color     {color}", font=small_font, fill='black')
    draw.text((700, 410), f"Order No.     {order_no}", font=small_font, fill='black')

    # Footer
    draw.text((400, 470), "TAX INVOICE       |       Original For Recipient", font=tiny_font, fill='black')

    # Save temp image
    temp_img_path = os.path.join(output_dir, f"label_{idx+1}.png")
    img.save(temp_img_path)

    # Add to PDF
    pdf.add_page()
    pdf.image(temp_img_path, x=10, y=10, w=190)

# Save PDF
pdf_path = os.path.join(output_dir, "All_Labels.pdf")
pdf.output(pdf_path)
print(f"✅ All labels saved to: {pdf_path}")
