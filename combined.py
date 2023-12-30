import requests
from flask import Flask, render_template, request , jsonify, session
import time
import uuid
import serial
import time
import json

# ser = serial.Serial('COM5', 9600)#setup arduino
time.sleep(2)

# app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')
app.secret_key = '9999'  # Set a secret key for session security



@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/create_order', methods=['POST'])
def order_pay():
    amount = float(request.form['order_amount'])
    cart_data = request.form.get('cart_data')

    # Convert the JSON string to a Python dictionary
    cart_data_dict = json.loads(cart_data)

    # Store cart_data_dict in the session
    session['cart_data'] = cart_data_dict

    # Log session ID for demonstration purposes
    # print(f"Session ID in order_pay: {session.sid}")


    # Now you can use cart_data_dict in your logic
    for product_title, product_quantity in cart_data_dict.items():
        print(f"Product: {product_title}, Quantity: {product_quantity}")
        
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

    cart_data = session.get('cart_data', {})

    # Print keys and values for verification
    for product_title, product_quantity in cart_data.items():
        print(f"Product during success: {product_title}, Quantity during success: {product_quantity}")

    # Define the mapping of product titles to stack numbers
    stack_mapping = {
            "GALINA CAIPIRA": 1,
            "VERY VEGGIE": 2,
            "SPICY EPICE": 3,
            # Add more mappings as needed
        }
    

    # Initialize quantities for each stack
    stack_quantities = {stack_number: 0 for stack_number in range(1, 4)}  # Assuming 3 stacks

    # Update quantities based on cart data
    for product_title, product_quantity in cart_data.items():
        stack_number = stack_mapping.get(product_title)
        if stack_number:
            stack_quantities[stack_number] = product_quantity

    # Format the data as needed (product_title stack no,quantity)

    # Format the data as needed (1 2,2 1,3 2)
    formatted_data = ' '.join([f"{stack_number} {product_quantity}" for stack_number, product_quantity in stack_quantities.items()])




    print("Info to be sent to Arduino after Success:")
    print(formatted_data)

    # Convert the formatted_data string to bytes before sending to Arduino
    encoded_data = formatted_data.encode('utf-8')

    try:
        # Send the encoded data to Arduino
        ser.write(encoded_data)
        print("Data sent to Arduino successfully")
    except Exception as e:
        print(f"Error sending data to Arduino: {str(e)}")

    return render_template('success.html')


    
@app.route('/payment_failure')
def payment_failure():
    return render_template('failure.html')
    
if __name__ == '__main__':
    app.run()
