import requests
from flask import Flask, render_template, request , jsonify
import time
import uuid
import serial
import time

# ser = serial.Serial('COM7', 9600)#setup arduino
time.sleep(2)

# app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')



@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/create_order', methods=['POST'])
def order_pay():
    amount = float(request.form['order_amount'])
    print(amount)
    order_id = str(uuid.uuid4())

    create_order_url = "https://sandbox.cashfree.com/pg/orders"
    create_order_payload = {
        "customer_details": {
            "customer_id": "7112AAA812234",
            "customer_phone": "9908734801"
        },
        "order_amount": float(amount),
        "order_currency": "INR",
        "order_id": order_id
    }
    create_order_headers = {
        "accept": "application/json",
        "x-client-id": "TEST4143386d2b7e9c0c011a9417ce833414",
        "x-client-secret": "TEST587b737b29c61d5a7cbc570808bf193103f2e576",
        "x-api-version": "2022-09-01",
        "content-type": "application/json"
    }

    create_order_response = requests.post(create_order_url, json=create_order_payload, headers=create_order_headers)
    create_order_data = create_order_response.json()

    if create_order_response.status_code == 200:
        payment_session_id = create_order_data.get("payment_session_id")
        if payment_session_id:
            session_url = "https://sandbox.cashfree.com/pg/orders/sessions"
            session_payload = {
                "payment_method": {
                    "upi": {
                        "channel": "qrcode"
                    }
                },
                "payment_session_id": payment_session_id,
                "order_amount": float(amount),
                "order_currency": "INR",
            }
            session_headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "x-api-version": "2022-09-01",
            }

            session_response = requests.post(session_url, json=session_payload, headers=session_headers)
            session_data = session_response.json()

            if session_response.status_code == 200:
                qr_code_data = session_data['data']['payload']['qrcode']
                return render_template('order_pay.html', qr_code_data=qr_code_data , order_id=order_id)
            else:
                return "Failed to retrieve QR code. Error: " + session_response.text
        else:
            return "Payment Session ID not found in response."
    else:
        return f"Error creating order: {create_order_response.text}"

@app.route('/check_payment_status')
def check_payment_status():
    order_id = request.args.get('order_id')
    url = f"https://sandbox.cashfree.com/pg/orders/{order_id}/payments"
    headers = {
        "x-client-id": "TEST4143386d2b7e9c0c011a9417ce833414",
        "x-client-secret": "TEST587b737b29c61d5a7cbc570808bf193103f2e576",
        "x-api-version": "2021-05-21"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            payment_status = result[0].get("payment_status")
            if payment_status == "SUCCESS":
                return jsonify({"payment_status": "PAID"})
            elif payment_status == "FAILED":
                return jsonify({"payment_status": "FAILED"})
            else:
                return jsonify({"payment_status": "NOT_PAID"})
        else:
            return jsonify({"payment_status": "NOT_FOUND"})
    else:
        return jsonify({"payment_status": "ERROR"})
    
# @app.route('/payment_success')
# def payment_success():
#     ser.write(b'69') #send code to arduino
#     return render_template('success.html')

@app.route('/payment_success')
def payment_success():
    stacks = [
        {"stack": 1, "quantity": 2},
        {"stack": 2, "quantity": 1},
        {"stack": 3, "quantity": 3}
        # Add more stacks as needed
    ]

    commands = ""
    for stack in stacks:
        commands += f'{stack["stack"]} {stack["quantity"]} '

    print(commands.encode())
    return render_template('success.html')


    
@app.route('/payment_failure')
def payment_failure():
    return render_template('failure.html')
    
if __name__ == '__main__':
    app.run()
