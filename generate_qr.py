import qrcode
import os

# Folder jaha QR save honge
QR_FOLDER = "static/qr"

# Agar folder nahi hai to bana do
os.makedirs(QR_FOLDER, exist_ok=True)

BASE_URL = "http://192.168.1.107:5000/menu"

# Table 1 se 5 tak QR generate
for table_id in range(1, 6):
    url = f"{BASE_URL}/{table_id}"
    qr = qrcode.make(url)

    file_path = os.path.join(QR_FOLDER, f"table_{table_id}.png")
    qr.save(file_path)

    print(f"✅ QR generated: {file_path}")

print("🎉 All table QR codes generated successfully")
