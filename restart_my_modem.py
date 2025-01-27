import tkinter as tk
from tkinter import ttk
import requests
import re
import threading
import subprocess
import time

# Modem sıfırlama işlemi
def reset_modem():
    url = 'http://192.168.0.1'

    # HTTP GET isteği gönder
    response = requests.get(url)

    # Eğer istek başarılıysa, HTML içeriğini analiz et
    if response.status_code == 200:
        # HTML içeriğinden 'CSRFValue' adlı input'un value değerini çekmek için regex kullan
        match = re.search(r'<input type="hidden" name="CSRFValue" value=(\d+)>', response.text)

        if match:
            csrf_value = match.group(1)  # İlk parantez içindeki değeri al
            url = 'http://192.168.0.1/goform/login'
            data = {
                'CSRFValue': csrf_value,
                'loginUsername': '',
                'loginPassword': 'admin',
                'logoffUser': 0
            }
            response = requests.post(url, data=data)
            if response.text:
                print('Access to the interface established!')
                url = 'http://192.168.0.1/RgSecurity.asp'
                response = requests.get(url)
                match = re.search(r'<input type="hidden" name="CSRFValue" value=(\d+)>', response.text)
                csrf_value = match.group(1)
                data = {
                    'CSRFValue': csrf_value,
                    'HttpUserId': '',
                    'Password': '',
                    'PasswordReEnter': '',
                    'RestoreConfirmPop': 0,
                    'RestoreFactoryNo': 0x00,
                    'mCmReset': 1
                }
                url = 'http://192.168.0.1/goform/RgSecurity'
                response = requests.post(url, data=data)
                print('Modem is restarting, please wait......')

                # Progress bar'ı doldur
                fill_progressbar()

                # Ping işlemini başlat
                ping_modem()

        else:
            print("CSRFValue not found")
    else:
        print(f"error: {response.status_code}")

# Progress bar'ı doldurma fonksiyonu
def fill_progressbar():
    for i in range(101):
        progressbar['value'] = i
        root.update_idletasks()
        time.sleep(1.2)  # 120 saniye süresince dolmasını sağlar

# Ping işlemi (modem için)
def ping_modem():
    while True:
        response = subprocess.run(['ping', '-n', '1', '192.168.0.1'], stdout=subprocess.PIPE)
        if response.returncode == 0:  # Modem geri geldi
            label_status.config(text="Connection with the modem established", fg="green")
            break
        time.sleep(1)  # 1 saniye arayla ping at

# İnternet bağlantısı kontrolü
def check_internet():
    while True:
        response = subprocess.run(['ping', '-n', '1', 'google.com'], stdout=subprocess.PIPE)
        if response.returncode == 0:  # İnternet bağlantısı var
            internet_status_label.config(text="Internet Connection: Available", fg="green")
        else:  # İnternet bağlantısı yok
            internet_status_label.config(text="Internet Connection: Unavailable", fg="red")
        time.sleep(2)  # 2 saniye arayla kontrol et

# GUI kısmı
root = tk.Tk()
root.title("Restart My Modem - v1.0 Feyzullah Akyuz")
root.geometry("400x300")
root.config(bg="#f0f0f0")

# Başlık
label = tk.Label(root, text="Modem Reset - Technicolor ", font=("Arial", 14), bg="#f0f0f0")
label.pack(pady=10)

# RESET butonu
reset_button = tk.Button(root, text="RESET", command=lambda: threading.Thread(target=reset_modem).start(),
                         font=("Arial", 12), bg="#ff5733", fg="white", relief="raised", padx=20, pady=10)
reset_button.pack(pady=20)

# Progress bar
progressbar = ttk.Progressbar(root, length=300, mode='determinate', maximum=100)
progressbar.pack(pady=20)

# Durum etiketi
label_status = tk.Label(root, text="Press the Reset button to restart...", font=("Arial", 12), bg="#f0f0f0")
label_status.pack(pady=10)

# İnternet bağlantısı etiketi
internet_status_label = tk.Label(root, text="Internet Connection: Checking...", font=("Arial", 12), bg="#f0f0f0")
internet_status_label.pack(pady=10)

# İnternet bağlantısını kontrol etme işlemi
threading.Thread(target=check_internet, daemon=True).start()

# Başlat
root.mainloop()
