import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from docxtpl import DocxTemplate
import datetime

app = Flask(__name__)

invoice_list = []
invoice_details = {}  # To store user details temporarily

def generate_invoice_docx(name, phone, invoice_list, subtotal, salestax, total):
    doc = DocxTemplate("invoice_template.docx")
    doc.render({
        "name": name,
        "phone": phone,
        "invoice_list": invoice_list,
        "subtotal": subtotal,
        "salestax": f"{salestax*100}%",
        "total": total
    })
    doc_name = f"invoice_{name}_{datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')}.docx"
    doc.save(doc_name)
    return doc_name

@app.route('/', methods=['GET', 'POST'])
def index():
    global invoice_list, invoice_details
    if request.method == 'POST':
        if 'add_item' in request.form:
            # Ensure the form fields are filled before adding items
            if 'first_name' in invoice_details and 'last_name' in invoice_details and 'phone' in invoice_details:
                qty = int(request.form['qty'])
                desc = request.form['desc']
                price = float(request.form['price'])
                line_total = qty * price
                invoice_item = [qty, desc, price, line_total]
                invoice_list.append(invoice_item)
                return redirect(url_for('index'))
            else:
                return render_template('index.html', invoice_list=invoice_list, error="Please fill out all required fields before adding items.")

        elif 'generate_invoice' in request.form:
            if 'first_name' in invoice_details and 'last_name' in invoice_details and 'phone' in invoice_details:
                name = f"{invoice_details['first_name']} {invoice_details['last_name']}"
                phone = invoice_details['phone']
                subtotal = sum(item[3] for item in invoice_list)
                salestax = 0.1
                total = subtotal * (1 + salestax)
                doc_name = generate_invoice_docx(name, phone, invoice_list, subtotal, salestax, total)
                invoice_list.clear()
                invoice_details.clear()
                return send_file(doc_name, as_attachment=True)
            else:
                return render_template('index.html', invoice_list=invoice_list, error="Please fill out all required fields before generating the invoice.")

        elif 'new_invoice' in request.form:
            invoice_list.clear()
            invoice_details.clear()
            return redirect(url_for('index'))

        elif 'save_details' in request.form:
            # Save details from the form to invoice_details
            invoice_details = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'phone': request.form['phone']
            }
            return redirect(url_for('index'))

    return render_template('index.html', invoice_list=invoice_list, invoice_details=invoice_details)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
