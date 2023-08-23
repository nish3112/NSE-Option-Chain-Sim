# TODO : DONE -- Calc the iv  
# TODO:  DONE -- BUT ALL THE IV IS - CAUSE IT HAS EXPIRED -- Can put a check condition that if it is less than todays date dont add it to the dict
# TODO : DONE -- Its just passing values and not storing or updating it check that -- half the values are empty becuase of that 
# TODO : DONE -- CHECK THE NUMBERS DATA IS WRONG MOSTLY
# TODO : DONE  -- Figure out CE and PE 
# TODO : DONE  -- Do the dict stuff and send the data to the frontend via api 
# TODO : DONE -- load data in table
# TODO : DONE -- LOGO
# TODO : Cell blink background
# TODO : INTO THE MONEY OUT OF MONEY
# TODO : Pass expiry date as well and expiry date filter
# TODO : Filters 
# TODO : Refactor everything
# TODO : Make a about and what used website also caution 
# TODO : Screenshots and working flow 
# TODO : Docker
# TODO : HOST it somewhere


import json
import threading
from flask import Flask, Response
from flask_cors import CORS
import struct
import socket
import re
import datetime as dt
import time
from py_vollib.black_scholes_merton.implied_volatility import implied_volatility
from waitress import serve

app = Flask(__name__)
CORS(app)

HOST = 'localhost'
PORT = 8102

current_option_values = {   
    "data": {}
}

current_ltp_values = {
  "data": {
    "MAINIDX": {
      "underlying": "MAINIDX",
      "LTP": 18563.05
    },
    "FINANCIALS": {
       "underlying": "FINANCIALS",
       "LTP": 19408.6
    },
    "MIDCAPS": {
       "underlying": "MIDCAPS",
       "LTP": 43994.6
    },
    "ALLBANKS": {
       "underlying": "ALLBANKS", 
       "LTP": 7862.05
    }
  }
}


@app.route('/api/current_ltp_values', methods=['GET'])
def stream_ltp_values():
    """
    This function streams the current market INDEX prices
    For now, it streams 4 indexes - MAINIDX,FINANCIALS,MIDCAPS,ALLBANKS
    All the data that is processed is stored in the dictionary - current_ltp_values
    Later the dictionary is converted into a json dump.
    The Json dump is sent via the response stream every 15 seconds

    """
    def generate_ltp():
        while True:
            json_data = json.dumps(current_ltp_values)
            yield f"data:{json_data}\n\n"
            time.sleep(15)

    return Response(generate_ltp(), mimetype='text/event-stream')


@app.route('/api/current_option_values', methods = ['GET'])
def stream_option_values():
    """
    This function streams the current market OPTION prices
    All the data that is processed is stored in the dictionary - current_option_values
    Later the dictionary is converted into a json dump.
    The Json dump is sent via the response stream every 15 seconds
    """
    def generate_option():
        while True:
            json_data = json.dumps(current_option_values)
            yield f"data:{json_data} \n\n"
            time.sleep(15)
    return Response(generate_option(),mimetype='text/event-stream')
    

def listen_to_socket():
    """
    Listen to a socket for incoming data packets and process them.

    This function establishes a socket connection to a specified host and port
    and continuously listens for incoming data packets. The received data is
    accumulated in a packet buffer and then decoded using the `decode_packet`
    function. The function continues to listen until the connection is closed or
    an error occurs.

    Note that the data packets are assumed to have a fixed length of 130 bytes.

    Exceptions:
        - ConnectionRefusedError: If the connection to the specified host and
          port is refused.
        - Exception: For any other exceptions that might occur during the socket
          connection or data processing.

    Returns:
        None
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")
        send_initial_request(sock)
        packet_buffer = b'' 
        while True:
            received_data = sock.recv(130) 
            if not received_data:
                break

            packet_buffer += received_data
            while len(packet_buffer) >= 130: 
                packet_data = packet_buffer[:130]
                packet_buffer = packet_buffer[130:]
                decode_packet(packet_data)

    except ConnectionRefusedError:
        print(f"Connection refused to {HOST}:{PORT}")
    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        sock.close()
        print("Socket connection closed")


def send_initial_request(sock):
    """
    Send an initial request to the server over the provided socket.

    This function sends an initial request to the server using the provided
    socket. The request is sent as a single byte, packed using the 'struct'
    module. The packed request is then sent using the 'sendall' method of the
    socket.

    Args:
        sock (socket.socket): The socket over which the request will be sent.

    Returns:
        None
    """
    request = struct.pack('!B', 1)
    sock.sendall(request)
    print("Initial request sent to the server")


def decode_packet(data):
    """
    Decode a binary data packet and extract relevant information.

    This function takes a binary data packet as input and decodes it to extract
    various fields, such as trading symbol, sequence number, timestamp, last
    traded price (LTP), etc. 
    The extracted information is stored in a dictionary for further processing.

    Args:
        data (bytes): The binary data packet to be decoded.

    Returns:
        None
    """
    packet = {}
    packet_length = struct.unpack('<I', data[0:4])[0]
    packet['trading_symbol'] = data[4:34].decode('utf-8').rstrip('\x00')
    packet['sequence_number'] = struct.unpack('<q', data[34:42])[0]
    timestamp = struct.unpack('<q', data[42:50])[0]
    timestamp_seconds = timestamp / 1000
    date = dt.datetime.fromtimestamp(timestamp_seconds)
    packet['formatted_datetime'] = date.strftime('%Y-%m-%d %H:%M:%S')
    packet['ltp'] = struct.unpack('<q', data[50:58])[0] / 100.0
    packet['ltq'] = struct.unpack('<q', data[58:66])[0]
    packet['total_traded_volume'] = struct.unpack('<q', data[66:74])[0]
    packet['best_bid'] = struct.unpack('<q', data[74:82])[0] / 100.0
    packet['bid_qty'] = struct.unpack('<q', data[82:90])[0]
    packet['best_ask'] = struct.unpack('<q', data[90:98])[0] / 100.0
    packet['ask_qty'] = struct.unpack('<q', data[98:106])[0]
    packet['open_interest'] = struct.unpack('<q', data[106:114])[0]
    packet['prev_close_price'] = struct.unpack('<q', data[114:122])[0] / 100.0
    packet['prev_open_interest'] = struct.unpack('<q', data[122:130])[0]

    preprocess_data(packet)
    

def preprocess_data(packet):
    """
    Preprocess the decoded data packet and update option values.

    This function takes a dictionary(packet) containing the decoded data packet and
    performs preprocessing tasks on the data, including calculating implied
    volatility, updating option values, and storing the information for
    underlying assets and options.

    Args:
        packet (dict): The dictionary containing the decoded data packet.

    Returns:
        None
    """

    global current_option_values, current_ltp_values
    # If its not LTP
    if(packet['trading_symbol'].endswith("PE") or packet['trading_symbol'].endswith("CE")):
        try:
            strike_price_match = re.search(r'[A-Z]+\d{2}(\d+)', packet['trading_symbol']).group(1)
            strike_price=int(strike_price_match)
        except:
            strike_price = 0
        
        underlying = re.search(r'^([A-Z]+)', packet['trading_symbol']).group(1)
        if underlying == "MIDCAP":
            underlying = "MIDCAPS"

        date_match = re.search(r'\d{2}[A-Z]{3}\d{2}', packet['trading_symbol'])
        expiry_date = date_match.group()

        option_price = (packet['best_bid'] + packet['best_ask']) / 2.0

        date_format = "%d%b%y"
        date_object = dt.datetime.strptime(expiry_date, date_format).date()
        expiration_time = dt.time(15, 30)
        expiration_datetime = dt.datetime.combine(date_object, expiration_time)
        # current_datetime = dt.datetime.now()
        # Simulating at the time of hackathon
        current_datetime = dt.datetime(2023, 7, 1, 12, 45)
        time_difference = expiration_datetime - current_datetime
        time_to_expiration = time_difference.total_seconds() / (365.25 * 24.0 * 60.0 * 60.0)
        option_type = re.search(r'([A-Z]+)$', packet['trading_symbol']).group(1)
        iv = 0
        # CHECK IV
        try:
            iv = implied_volatility(current_ltp_values["data"][underlying]["LTP"], option_price, strike_price, time_to_expiration, 0.05, 0, 'c' if option_type == "CE" else 'p')
        except:
            iv = "-"

        current_option_values["data"].setdefault(underlying, {})
        current_option_values["data"][underlying].setdefault(str(strike_price), {"calls": {}, "puts":{}})
        
        if(option_type == "PE"):
            option_type = "puts"
        elif(option_type == "CE"):
            option_type = "calls"
     

        # Update the "puts" or "calls" data for the underlying and strike price
        current_option_values["data"][underlying][str(strike_price)][option_type] = {
            "oi": packet["open_interest"],
            "change in oi": packet["open_interest"] - packet["prev_open_interest"],
            "Volume": packet["total_traded_volume"],
            "iv": iv,
            "ltp": packet["ltp"],
            "change": packet["ltp"] - packet["prev_close_price"],
            "bid quantity": packet["bid_qty"],
            "bid": packet["best_bid"],
            "ask": packet["best_ask"],
            "ask quantity": packet["ask_qty"]
        }

        
    else:
        # if is ltp
        underlying = re.search(r'^([A-Z]+)', packet['trading_symbol']).group(1)
        if underlying == "MIDCAP":
            underlying = "MIDCAPS"
    
        ltp_data = {
            "underlying": underlying,
            "LTP": packet['ltp']
        }

        current_ltp_values["data"][underlying] = ltp_data

        
# Run the Flask app
if __name__ == '__main__':
    socket_thread = threading.Thread(target=listen_to_socket)
    socket_thread.start()
    
    # app.run(host='0.0.0.0', port=5000, threaded = True)
    serve(app, host='0.0.0.0', port=5000)