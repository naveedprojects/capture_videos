import bluetooth
import json
import os
import subprocess

FILE_PATH = "wifi_credentials.json"
RESPONSE_PATH = "connection_response.txt"

def setup_bluetooth_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    bluetooth.advertise_service(server_sock, "WiFiConfigurator",
                                service_id="00001101-0000-1000-8000-00805F9B34FB",
                                service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE])

    print(f"Waiting for connection on RFCOMM channel {port}")
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")

    return server_sock, client_sock

def receive_file_via_bluetooth(client_sock):
    with open(FILE_PATH, 'wb') as f:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            f.write(data)
    print(f"Received file and saved to {FILE_PATH}")

def connect_to_wifi():
    with open(FILE_PATH, 'r') as f:
        wifi_info = json.load(f)

    ssid = wifi_info.get("SSID")
    password = wifi_info.get("password")

    if not ssid or not password:
        return False, "Missing SSID or password in the JSON file."

    wpa_supplicant_conf = f"""
    network={{
        ssid="{ssid}"
        psk="{password}"
    }}
    """
    
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as file:
        file.write(wpa_supplicant_conf)

    try:
        subprocess.run(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"], check=True)
        subprocess.run(["sudo", "ifdown", "wlan0"], check=True)
        subprocess.run(["sudo", "ifup", "wlan0"], check=True)
    except subprocess.CalledProcessError as e:
        return False, str(e)

    result = subprocess.run(["ping", "-c", "4", "8.8.8.8"], stdout=subprocess.PIPE)
    if result.returncode == 0:
        return True, None
    else:
        return False, "Ping test failed."

def send_response_via_bluetooth(client_sock, message):
    with open(RESPONSE_PATH, 'w') as f:
        f.write(message)

    with open(RESPONSE_PATH, 'rb') as f:
        data = f.read(1024)
        while data:
            client_sock.send(data)
            data = f.read(1024)
    print(f"Sent response: {message}")

def main():
    while True:
        server_sock, client_sock = setup_bluetooth_server()
        try:
            receive_file_via_bluetooth(client_sock)

            success, error = connect_to_wifi()
            if success:
                send_response_via_bluetooth(client_sock, "Connection successful")
            else:
                send_response_via_bluetooth(client_sock, f"Connection failed: {error}")
        except Exception as e:
            print(f"An error occurred: {e}")
            send_response_via_bluetooth(client_sock, f"An error occurred: {e}")
        finally:
            client_sock.close()
            server_sock.close()

if __name__ == "__main__":
    main()
