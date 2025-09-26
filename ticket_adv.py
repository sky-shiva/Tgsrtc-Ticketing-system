from flask import Flask, request, render_template_string
import threading
import qrcode
import os
import socket
import time
from datetime import datetime

payment_done = False

def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

app = Flask(__name__)

@app.route("/pay")
def pay_page():
    global payment_done
    amt = request.args.get("amount")
    if payment_done:
        return "<h2>payment already completed</h2>"
    return render_template_string("""
        <h2>🚌 Pay ₹{{amount}} to TGSRTC</h2>
        <form action="/confirm" method="post">
            <input type="hidden" name="amount" value="{{amount}}">
            <button type="submit">PAY NOW</button>
        </form>
    """,amount=amt)

@app.route("/confirm", methods=["POST"])
def confirm_payment():
    global payment_done
    payment_done = True
    return "<h1>✅ Payment Successful!<br>Ticket will print on terminal.</h1>"

def start_flask():
    ip = get_my_ip()
    print(f"\nhttp://{ip}:5000/pay?amount=AMOUNT_HERE")
    app.run(host="0.0.0.0", port=5000)

class TicketCollector:
    total_earnings = 0

    @classmethod
    def collect_fare(cls, amount):
        cls.total_earnings += amount

    @classmethod
    def show_total(cls):
        print(f"\nTotal Balance: ₹{cls.total_earnings}\n")

class Ticket:
    bus_no = 5249
    driver_name = "Srinivas"
    ticket_collector = "Srinu"

    def __init__(self):
        self.pickup = None
        self.drop = None
        self.fare = None
        self.count = 1
        self.total = 0

    def take_ticket(self):
        print("\nChoose the path:")
        print("1. Parigi → Hyderabad")
        print("2. Hyderabad → Parigi")
        path = input("Enter path number (1 or 2): ").strip()

        if path == '1':
            self.use_route("Parigi → Hyderabad")
        elif path == '2':
            self.use_route("Hyderabad → Parigi")
        else:
            print("Invalid path selected.")

    def use_route(self, direction):
        if direction == "Parigi → Hyderabad":
            destinations = ["Parigi", "Pudur", "Manneguda", "Chittampally", "Chevella",
                            "Moinabad", "Langarhouz", "Mehdipatnam", "Hyderabad"]
        else:
            destinations = ["Hyderabad", "Mehdipatnam", "Langarhouz", "Moinabad", "Chevella",
                            "Chittampally", "Manneguda", "Pudur", "Parigi"]

        prices = self.get_prices()

        self.pickup = input("Enter your pickup location: ").strip().title()
        if self.pickup in destinations:
            idx = destinations.index(self.pickup)
            print("\nAvailable drop locations:")
            for d in destinations[idx + 1:]:
                print("-", d)

            self.drop = input("Enter your drop location: ").strip().title()
            if self.drop in destinations[idx + 1:]:
                self.count = int(input("Enter number of tickets: "))
                self.fare = prices.get((self.pickup, self.drop), None)
                if self.fare:
                    self.total = self.fare * self.count
                    self.generate_qr_and_wait()
                    self.print_ticket()
                    TicketCollector.collect_fare(self.total)
                else:
                    print("Fare not found.")
            else:
                print("Invalid drop location.")
        else:
            print("Invalid pickup location.")

    def generate_qr_and_wait(self):
        global payment_done
        payment_done = False
        ip = get_my_ip()
        url = f"http://{ip}:5000/pay?amount={self.total}"
        qr = qrcode.make(url)
        qr.save("qr.png")
        os.startfile("qr.png")
        print(f"\nScan QR to pay ₹{self.total}")
        while not payment_done:
            time.sleep(1)

    def print_ticket(self):
        print("\n" + "=" * 50)
        print("         TGSRTC Travels         ")
        print("=" * 50)
        print(f"{self.pickup}  -->  {self.drop}\n")
        print(f"Tickets     : {self.count}")
        print(f"Fare/ticket : ₹{self.fare}")
        print(f"Total Fare  : ₹{self.total}")
        print(f"Status      : Confirmed")
        print(f"Date & Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 40)
        print("Bus Info")
        print("=" * 40)
        print(f"Driver       : {Ticket.driver_name}")
        print(f"Collector    : {Ticket.ticket_collector}")
        print(f"Bus No       : {Ticket.bus_no}")
        print("=" * 50)
        print("THANK YOU")
        print("=" * 50)

    def get_prices(self):
        return {
            ("Parigi", "Pudur"): 30, ("Parigi", "Manneguda"): 40, ("Parigi", "Chittampally"): 50,
            ("Parigi", "Chevella"): 60, ("Parigi", "Moinabad"): 90, ("Parigi", "Langarhouz"): 110,
            ("Parigi", "Mehdipatnam"): 130, ("Parigi", "Hyderabad"): 130,
            ("Pudur", "Manneguda"): 10, ("Pudur", "Chittampally"): 30, ("Pudur", "Chevella"): 60,
            ("Pudur", "Moinabad"): 60, ("Pudur", "Langarhouz"): 90, ("Pudur", "Mehdipatnam"): 110,
            ("Pudur", "Hyderabad"): 110, ("Manneguda", "Chittampally"): 10,
            ("Manneguda", "Chevella"): 40, ("Manneguda", "Moinabad"): 70,
            ("Manneguda", "Langarhouz"): 90, ("Manneguda", "Mehdipatnam"): 110,
            ("Manneguda", "Hyderabad"): 110, ("Chittampally", "Chevella"): 30,
            ("Chittampally", "Moinabad"): 60, ("Chittampally", "Langarhouz"): 70,
            ("Chittampally", "Mehdipatnam"): 90, ("Chittampally", "Hyderabad"): 90,
            ("Chevella", "Moinabad"): 50, ("Chevella", "Langarhouz"): 70,
            ("Chevella", "Mehdipatnam"): 80, ("Chevella", "Hyderabad"): 80,
            ("Moinabad", "Langarhouz"): 40, ("Moinabad", "Mehdipatnam"): 50,
            ("Moinabad", "Hyderabad"): 50, ("Langarhouz", "Mehdipatnam"): 30,
            ("Langarhouz", "Hyderabad"): 30, ("Hyderabad", "Mehdipatnam"): 30,
            ("Hyderabad", "Langarhouz"): 60, ("Hyderabad", "Moinabad"): 80,
            ("Hyderabad", "Chevella"): 90, ("Hyderabad", "Chittampally"): 110,
            ("Hyderabad", "Manneguda"): 120, ("Hyderabad", "Pudur"): 130,
            ("Hyderabad", "Parigi"): 130, ("Mehdipatnam", "Langarhouz"): 30,
            ("Mehdipatnam", "Moinabad"): 50, ("Mehdipatnam", "Chevella"): 80,
            ("Mehdipatnam", "Chittampally"): 90, ("Mehdipatnam", "Manneguda"): 110,
            ("Mehdipatnam", "Pudur"): 110, ("Mehdipatnam", "Parigi"): 130,
            ("Langarhouz", "Moinabad"): 40, ("Langarhouz", "Chevella"): 70,
            ("Langarhouz", "Chittampally"): 70, ("Langarhouz", "Manneguda"): 90,
            ("Langarhouz", "Pudur"): 90, ("Langarhouz", "Parigi"): 110,
            ("Moinabad", "Chevella"): 50, ("Moinabad", "Chittampally"): 60,
            ("Moinabad", "Manneguda"): 70, ("Moinabad", "Pudur"): 90,
            ("Moinabad", "Parigi"): 90, ("Chevella", "Chittampally"): 30,
            ("Chevella", "Manneguda"): 40, ("Chevella", "Pudur"): 60,
            ("Chevella", "Parigi"): 60, ("Chittampally", "Manneguda"): 10,
            ("Chittampally", "Pudur"): 30, ("Chittampally", "Parigi"): 50,
            ("Manneguda", "Pudur"): 10, ("Manneguda", "Parigi"): 40,
            ("Pudur", "Parigi"): 30
        }

threading.Thread(target=start_flask, daemon=True).start()

print("Welcome to Telangana Bus Ticketing System")
while True:
    print("\nMenu:\n1. Book a new ticket\n2. Show total earnings\n3. Exit")
    choice = input("Enter your choice (1/2/3): ").strip()
    if choice == "1":
        Ticket().take_ticket()
    elif choice == "2":
        TicketCollector.show_total()
    elif choice == "3":
        print("Thank you. Safe journey!")
        break
    else:
        print("Invalid choice.")
