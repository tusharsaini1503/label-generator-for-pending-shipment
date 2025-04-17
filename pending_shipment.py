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
return_address = "M.A.GARMENTS (STYLEHUB.GARMENTS)\nBlock E 33, welcome, seelmpur\nNear Suresh Dhaba\nShahdara, Delhi, 110053"
courier = "Valmo"
hub_code = "KRH-R0"
sku = "WkheeeBT07"
size = "30"
qty = "1"
color = "White"

# Fonts - bold and larger
bold_font_path = "C:/Windows/Fonts/arialbd.ttf"
font = ImageFont.truetype(bold_font_path, 28)
small_font = ImageFont.truetype(bold_font_path, 22)
tiny_font = ImageFont.truetype(bold_font_path, 18)

# PDF setup
pdf = FPDF()

for idx, row in df.iterrows():
    img_width, img_height = 1300, 850
    border_thickness = 5
    padding = border_thickness + 5
    content_width = img_width - 2 * padding

    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)

    # Draw thick border
    draw.rectangle([2, 2, img_width, border_thickness], fill="black")
    draw.rectangle([0, img_height - border_thickness, img_width, img_height], fill="black")
    draw.rectangle([1, 1, border_thickness, img_height], fill="black")
    draw.rectangle([img_width - border_thickness, 1, img_width, img_height], fill="black")

    # Internal layout lines
    draw.line([(padding + content_width // 2, padding), (padding + content_width // 2, 440)], fill="black", width=5)
    draw.line([(padding, padding + 210), (padding + content_width // 2, padding + 210)], fill="black", width=3)
    draw.rectangle([padding, 440, img_width - padding, 550], outline="black", width=5)
    draw.line([(padding, 550), (img_width - padding, 550)], fill="black", width=3)

    # Address section
    draw.text((padding + 10, padding + 10),
              f"Customer Address\n{row['Consignee_Name']}\n{row['Destination_City']}, {row['Destination Pincode']}",
              font=font, fill='black')

    # Return address
    draw.text((padding + 10, padding + 230),
              f"If undelivered, return to:\n{return_address}",
              font=small_font, fill='black')

    # COD text with black background and white font
    cod_text = "COD: Check the payable amount on the app"
    cod_font = ImageFont.truetype(bold_font_path, 30)
    cod_text_bbox = draw.textbbox((0, 0), cod_text, font=cod_font)
    cod_text_width = cod_text_bbox[2] - cod_text_bbox[0]
    cod_text_height = cod_text_bbox[3] - cod_text_bbox[1]
    cod_x = padding + content_width // 2 + 15
    cod_y = padding

    draw.rectangle(
        [cod_x - 5, cod_y - 1, cod_x + cod_text_width + 5, cod_y + cod_text_height + 1],
        fill="black"
    )
    draw.text((cod_x, cod_y), cod_text, font=cod_font, fill="white")

    # Courier info
    draw.text((padding + content_width // 2 + 40, padding + 50), f"{courier}", font=font, fill='black')
    draw.text((padding + content_width // 2 + 40, padding + 100), hub_code, font=font, fill='black')

    # Pickup box (Black background with white text)
    pickup_font = ImageFont.truetype(bold_font_path, 22)
    pickup_text = "Pickup"
    pickup_box = (img_width - padding - 400, padding + 40, img_width - padding - 300, padding + 80)
    draw.rectangle(pickup_box, fill="black")

    pickup_text_bbox = draw.textbbox((0, 0), pickup_text, font=pickup_font)
    pickup_text_width = pickup_text_bbox[2] - pickup_text_bbox[0]
    pickup_text_height = pickup_text_bbox[3] - pickup_text_bbox[1]
    pickup_x = pickup_box[0] + (pickup_box[2] - pickup_box[0] - pickup_text_width) // 2
    pickup_y = pickup_box[1] + (pickup_box[3] - pickup_box[1] - pickup_text_height) // 2
    draw.text((pickup_x, pickup_y), pickup_text, font=pickup_font, fill='white')

    # QR code
    qr = qrcode.make(row['Waybill_No'])
    qr = qr.resize((180, 180))
    img.paste(qr, (img_width - padding - 200, padding + 50))

    # Barcode
    CODE128 = barcode.get_barcode_class('code128')
    code128 = CODE128(str(row['Waybill_No']), writer=ImageWriter())
    barcode_img = code128.render(writer_options={
        'write_text': False,
        'module_height': 20,
        'quiet_zone': 2
    })
    barcode_img = barcode_img.resize((600, 80))
    barcode_x = padding + content_width // 2 + 30
    barcode_y = padding + 320  # Shifted further down

    # Position the Waybill No above the barcode
    waybill_text = row['Waybill_No']
    text_bbox = draw.textbbox((0, 0), waybill_text, font=small_font)
    text_width = text_bbox[2] - text_bbox[0]
    waybill_x = barcode_x + (600 - text_width) // 2
    waybill_y = barcode_y - 30  # Positioned above the barcode

    draw.text((waybill_x, waybill_y), waybill_text, font=small_font, fill='black')

    # Paste barcode below the waybill number
    img.paste(barcode_img, (barcode_x, barcode_y))

    # Product details section
    order_no = f"{134127939703703744 + idx}_1"
    draw.text((padding + 20, 460), f"Product Details", font=font, fill='black')
    draw.text((padding + 20, 500), f"SKU     {sku}", font=small_font, fill='black')
    draw.text((padding + 300, 500), f"Size     {size}     Qty     {qty}     Color     {color}", font=small_font, fill='black')
    draw.text((padding + 750, 500), f"Order No.     {order_no}", font=small_font, fill='black')

    # Footer
    draw.text((padding + 400, 560), "TAX INVOICE       |       Original For Recipient", font=tiny_font, fill='black')

    # Save temp image
    temp_img_path = os.path.join(output_dir, f"label_{idx+1}.png")
    img.save(temp_img_path)

    # Add to PDF
    pdf.add_page()
    pdf.image(temp_img_path, x=5, y=5, w=200)

# Save PDF
pdf_path = os.path.join(output_dir, "All_Labels.pdf")
pdf.output(pdf_path)
print(f"✅ All labels saved to: {pdf_path}")
