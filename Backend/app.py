import datetime
import re
import socket
import struct
import time
from flask import Flask, Response, render_template, send_from_directory
import threading
import json
from py_vollib.black_scholes_merton.implied_volatility import implied_volatility
from flask_cors import CORS
import os



app = Flask(__name__)
CORS(app)

HOST = 'localhost'
PORT = 8102

data_dict = {}  # Dictionary to store received data
previous_dict = {}
data_lock = threading.Lock()  # Lock to ensure thread-safe access to data_dict
transmit_data = False  # Flag to indicate when to transmit the data
batch_timestamp = None  # Timestamp of the batch received
first_time_data = True  # Flag to indicate if data is being sent for the first time

data_dict_indexes = {
    'MAINIDX': {
        'LTP': 18563.05
    },
    'FINANCIALS': {
        'LTP': 19408.6
    },
    'ALLBANKS': {
        'LTP': 43994.6
    },
    'MIDCAPS': {
        'LTP': 7862.05
    }
}


@app.route("/data_stream")
def event_stream():
    def generate_data():
        global transmit_data, previous_dict
        while True:
            # diff = DeepDiff(data_dict,previous_dict)
            previous_dict = data_dict
            # print(diff)
            if transmit_data:
                transmit_data = False
            yield f"data:{json.dumps(data_dict)}\n\n"
            time.sleep(1)

    return Response(generate_data(), mimetype='text/event-stream')

# @app.route("/data_stream")
# def event_stream():
#     def generate_data():
#         global transmit_data, previous_dict
#         while True:
#             for trading_symbol, symbol_data in data_dict.items():
#                 if trading_symbol not in previous_dict:
#                         # New trading symbol, add all inner details
#                     data_dict[trading_symbol] = symbol_data
#                     data_dict[trading_symbol]['difference'] = '='
#                 else:
#                     prev_symbol_data = previous_dict[trading_symbol]
#                     prev_ltp = prev_symbol_data['data']['ltp']
#                     current_ltp = symbol_data['data']['ltp']
#                     difference = current_ltp - prev_ltp
#                     if difference > 0:
#                         data_dict[trading_symbol] = symbol_data
#                         data_dict[trading_symbol]['difference'] = '+'
#                     elif difference < 0:
#                         data_dict[trading_symbol] = symbol_data
#                         data_dict[trading_symbol]['difference'] = '-'
#                     else:
#                         data_dict[trading_symbol] = symbol_data
#                         data_dict[trading_symbol]['difference'] = '='
#             previous_dict = data_dict
#             # print(diff)
#             if transmit_data:
#                 transmit_data = False
#             yield f"data:{json.dumps(data_dict)}\n\n"
#             time.sleep(60)

#     return Response(generate_data(), mimetype='text/event-stream')

# @app.route("/data_stream")
# def event_stream():
#     def generate_data():
#         global transmit_data, previous_dict
#         while True:
#             for trading_symbol, symbol_data in data_dict.items():
#                 if trading_symbol not in previous_dict:
#                         # New trading symbol, add all inner details
#                     data_dict[trading_symbol] = symbol_data
#                     data_dict[trading_symbol]['difference'] = '='
#                 # else:
#                 #     prev_symbol_data = previous_dict[trading_symbol]
#                 #     prev_ltp = prev_symbol_data['data']['ltp']
#                 #     current_ltp = symbol_data['data']['ltp']
#                 #     difference = current_ltp - prev_ltp
#                 #     if difference > 0:
#                 #         data_dict[trading_symbol] = symbol_data
#                 #         data_dict[trading_symbol]['difference'] = '+'
#                 #     elif difference < 0:
#                 #         data_dict[trading_symbol] = symbol_data
#                 #         data_dict[trading_symbol]['difference'] = '-'
#                 #     else:
#                 #         data_dict[trading_symbol] = symbol_data
#                 #         data_dict[trading_symbol]['difference'] = '='
#                 data_dict_str = json.dumps(data_dict, indent=4)
#                 previous_dict = data_dict.copy()
#                 data_dict = {}  # Clear the data dictionary
#                 if transmit_data:
#                     transmit_data = False  # Reset the flag
#                 yield f"data : {data_dict_str}\n\n"

#     return Response(generate_data(), mimetype='text/event-stream')


   

def listen_to_socket():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the socket
        sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")

        # Send the initial request to the server
        send_initial_request(sock)

        # Start listening for data
        packet_buffer = b''  # Buffer to accumulate received data
        while True:
            received_data = sock.recv(130)  # Adjust the buffer size as needed
            if not received_data:
                break

            packet_buffer += received_data
            while len(packet_buffer) >= 130:  # Process complete packets
                packet_data = packet_buffer[:130]
                packet_buffer = packet_buffer[130:]
                process_packet(packet_data)

    except ConnectionRefusedError:
        print(f"Connection refused to {HOST}:{PORT}")
    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Close the socket connection
        sock.close()
        print("Socket connection closed")

def send_initial_request(sock):
    # Send the initial request as a single byte
    request = struct.pack('!B', 1)
    sock.sendall(request)
    print("Initial request sent to the server")

def process_packet(data):
    global batch_timestamp

    packet_length = struct.unpack('<I', data[0:4])[0]
    trading_symbol = data[4:34].decode('utf-8').rstrip('\x00')
    sequence_number = struct.unpack('<q', data[34:42])[0]
    timestamp = struct.unpack('<q', data[42:50])[0]
    timestamp_seconds = timestamp / 1000
    dt = datetime.datetime.fromtimestamp(timestamp_seconds)
    formatted_datetime = dt.strftime('%Y-%m-%d %H:%M:%S')
    ltp = struct.unpack('<q', data[50:58])[0] / 100.0
    ltq = struct.unpack('<q', data[58:66])[0]
    total_traded_volume = struct.unpack('<q', data[66:74])[0]
    best_bid = struct.unpack('<q', data[74:82])[0] / 100.0
    best_bid_qty = struct.unpack('<q', data[82:90])[0]
    best_ask = struct.unpack('<q', data[90:98])[0] / 100.0
    best_ask_qty = struct.unpack('<q', data[98:106])[0]
    open_interest = struct.unpack('<q', data[106:114])[0]
    prev_close_price = struct.unpack('<q', data[114:122])[0] / 100.0
    prev_open_interest = struct.unpack('<q', data[122:130])[0]
    option_type = re.search(r'([A-Z]+)$', trading_symbol).group(1)
    iv = 0 
    ot=option_type[0].lower()
    try:
        strike_price_match = re.search(r'[A-Z]+\d{2}(\d+)', trading_symbol).group(1)
        strike_price=int(strike_price_match)
    except:
        strike_price = 0

    if trading_symbol in ['ALLBANKS', 'MAINIDX', 'FINANCIALS', 'MIDCAPS']:
        data_dict_indexes[trading_symbol]['LTP'] = ltp
        # data_dict_indexes[trading_symbol]['*Change'] = ltp - prev_close_price

    elif trading_symbol not in ['ALLBANKS', 'MAINIDX', 'FINANCIALS', 'MIDCAPS'] or ot != 'x':
        underlying = re.search(r'^([A-Z]+)', trading_symbol).group(1)
        if underlying == "MIDCAP":
            underlying = "MIDCAPS"

        date_match = re.search(r'\d{2}[A-Z]{3}\d{2}', trading_symbol)
        expiry_date = date_match.group()

        risk_free_rate = 0.05
        dividend_yield = 0.0

        option_price = (best_bid + best_ask) / 2.0

        date_format = "%d%b%y"
        date_object = datetime.datetime.strptime(expiry_date, date_format).date()
        expiration_time = datetime.time(15, 30)
        expiration_datetime = datetime.datetime.combine(date_object, expiration_time)
        current_datetime = datetime.datetime.now()
        time_difference = expiration_datetime - current_datetime

        if time_difference < datetime.timedelta(0) or ot == 'x':
            iv = -2
        else:
            time_to_expiration = time_difference.total_seconds() / (365.25 * 24.0 * 60.0 * 60.0)
            try:
                iv = implied_volatility(option_price, data_dict_indexes[underlying]['LTP'], strike_price,
                                        time_to_expiration, risk_free_rate, dividend_yield, ot)
            except:
                iv = -1

        if trading_symbol not in data_dict:
            data_dict[trading_symbol] = {
                'strike': strike_price,
                'expiry': expiry_date,
                'call': option_type,
                'data': {}
            }

        data_dict[trading_symbol]['data']['OI'] = open_interest
        data_dict[trading_symbol]['data']['Change_in_oi'] = open_interest - prev_open_interest
        data_dict[trading_symbol]['data']['volume'] = total_traded_volume
        data_dict[trading_symbol]['data']['iv'] = iv * 100
        data_dict[trading_symbol]['data']['ltp'] = ltp
        data_dict[trading_symbol]['data']['chnge'] = ltp - prev_close_price
        data_dict[trading_symbol]['data']['bid_qty'] = best_bid_qty
        data_dict[trading_symbol]['data']['bid'] = best_bid
        data_dict[trading_symbol]['data']['ask'] = best_ask
        data_dict[trading_symbol]['data']['ask_qty'] = best_ask_qty
        data_dict[trading_symbol]['data']['Sequence number'] = sequence_number

    with data_lock:
        batch_timestamp = dt  # Update the batch timestamp
# Start the socket listener in a background thread
socket_thread = threading.Thread(target=listen_to_socket)
socket_thread.start()

# Run the Flask app
if __name__ == '__main__':
    app.run(threaded=True)
