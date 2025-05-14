from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from django.utils import timezone

def generate_contract_pdf(contract):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, height-2*cm, "AVTOMOBIL IJARASI SHARTNOMASI")
    
    # Contract details
    p.setFont("Helvetica", 12)
    y = height-4*cm
    
    details = [
        f"Shartnoma raqami: {contract.id}",
        f"Sana: {timezone.localtime(contract.created_at).strftime('%d.%m.%Y %H:%M')}",
        "",
        "IJARA BERUVCHI:",
        "Car Rental Company",
        "",
        "IJARACHI:",
        f"F.I.O: {contract.user.get_full_name()}",
        f"Telefon: {contract.user.phone_number}",
        "",
        "AVTOMOBIL MA'LUMOTLARI:",
        f"Brend va Model: {contract.car.brand.name} {contract.car.model}",
        f"Ishlab chiqarilgan yil: {contract.car.year}",
        f"Rangi: {contract.car.color}",
        "",
        "IJARA MUDDATI:",
        f"Boshlanish sanasi: {contract.start_date.strftime('%d.%m.%Y')}",
        f"Tugash sanasi: {contract.end_date.strftime('%d.%m.%Y')}",
        f"Kunlar soni: {(contract.end_date - contract.start_date).days}",
        "",
        "TO'LOV MA'LUMOTLARI:",
        f"Kunlik ijara narxi: {contract.car.price_per_day:,.0f} so'm",
        f"Umumiy summa: {contract.total_price:,.0f} so'm"
    ]
    
    for line in details:
        p.drawString(2*cm, y, line)
        y -= 0.7*cm
    
    # Signatures
    y -= cm
    p.line(2*cm, y, 7*cm, y)
    p.line(width-7*cm, y, width-2*cm, y)
    y -= 0.5*cm
    p.drawString(2*cm, y, "Ijara beruvchi")
    p.drawString(width-7*cm, y, "Ijarachi")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
