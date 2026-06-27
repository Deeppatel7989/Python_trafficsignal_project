import json
import os
import getpass
import re
import random
from datetime import datetime
from functools import wraps

FILE = "bankData.json"

class InsufficientBalanceError(Exception):
    pass

def load_data():
    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)
    
def save_data(data):

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def login_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.bank_name:
            print("Please Login First")
            return
        return func(self,*args,**kwargs)
    return wrapper

def otp_generator():

    while True:
        yield random.randint(1000,9999)

def transection_id():

    while True:
        yield random.randint(100000,999999)

class HistoryIterator:
    def __init__(self,history):
        self.history = history
        self.index = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.history):
            raise StopIteration
        
        item  = self.history[self.index]

        self.index += 1

        return item 
    
class ATM :
    
    bank_name = "MY BANK"

    def __init__(self, username, data):

        self.__account_no = data[username]["account_no"]
        self.__username = username
        self.__balance = data[username]["balance"]
        self.__pin = data[username]["pin"]
        self.__history = data[username]["history"]
        self.__data = data

    @property
    def balance(self):
        return self.__balance
    
    @classmethod
    def bank_info(cls):
        print(f"\n Welcome to {cls.bank_name}")

    @staticmethod
    def validate_pin(pin):
        return len(str(pin)) == 4 and str(pin).isdigit()
    
    def save(self):
        self.__data[self.__username]["balance"] = self.__balance
        self.__data[self.__username]["pin"] = self.__pin
        self.__data[self.__username]["history"] = self.__history
        save_data(self.__data)

    @login_required
    def show_account_details(self):
        print("\n===== ACCOUNT DETAILS =====")

        print("Username       :", self.__username)
        print("Account Number :", self.__account_no)
        print("Balance        :", self.__balance)


    @login_required
    def deposit(self, amt):

        if amt <= 0:
            print("Invalid Amount")
            return
        self.__balance += amt

        time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        txn_id = next(transection_id())

        self.__history.append(f"{time} -> TXN : {txn_id} -> Deposited : {amt}")

        self.save()

        print(f"{amt} Deposited Successfully")

    @login_required
    def withdraw(self, amt):

        otp_gen = otp_generator()

        otp = next(otp_gen)

        print("OTP :", otp)

        try:
            user_otp = int(input("Enter OTP : "))

        except ValueError:
            print("Invalid OTP")
            return

        if user_otp != otp:
            print("Wrong OTP")
            return

        if amt <= 0:
            print("Invalid Amount")
            return

        try:

            if amt > self.__balance:
                raise InsufficientBalanceError(
                    "Insufficient Balance"
                )

            self.__balance -= amt

            time = datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )

            txn_id = next(transection_id())

            self.__history.append(
                f"{time} -> TXN : {txn_id} -> Withdraw : {amt}"
            )

            self.save()

            print(f"{amt} Withdraw Successfully")

        except InsufficientBalanceError as e:
            print(e)

    @login_required
    def show_balance(self):

        print(f"\nAvailable Balance : {self.balance}")

    def history_generator(self):

        for transaction in self.__history:
            yield transaction   

    @login_required
    def show_history(self):

        if not self.__history:
            print("No Transaction Found")
            return

        print("\n===== TRANSACTION HISTORY =====")

        iterator = HistoryIterator(self.__history)

        for h in iterator:
            print("->", h)
    
    @login_required
    def change_pin(self):

        old_pin = getpass.getpass("Enter Old PIN : ")

        if not old_pin.isdigit():
            print("PIN Must Contain Numbers Only")
            return

        if int(old_pin) != self.__pin:
            print("Wrong PIN")
            return

        new_pin = getpass.getpass(
            "Enter New PIN : "
        )

        if not ATM.validate_pin(new_pin):
            print("PIN Must Be 4 Digits")
            return

        confirm_pin = getpass.getpass(
            "Confirm New PIN : "
        )

        if new_pin != confirm_pin:
            print("PIN Does Not Match")
            return

        self.__pin = int(new_pin)

        self.save()

        print("PIN Changed Successfully")
    
    @login_required
    def transfer_money(self):

        receiver = input(
            "Enter Receiver Username : "
        )

        if receiver not in self.__data:
            print("Receiver Not Found")
            return

        if receiver == self.__username:
            print("Cannot Transfer To Yourself")
            return

        try:
            amt = int(input("Enter Amount : "))

        except ValueError:
            print("Invalid Amount")
            return

        if amt <= 0:
            print("Invalid Amount")
            return

        try:

            if amt > self.__balance:
                raise InsufficientBalanceError(
                    "Insufficient Balance"
                )

            otp = next(otp_generator())

            print("OTP :", otp)

            user_otp = int(input("Enter OTP : "))

            if user_otp != otp:
                print("Wrong OTP")
                return

            self.__balance -= amt

            self.__data[receiver]["balance"] += amt

            time = datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )

            txn_id = next(transection_id())

            self.__history.append(
                f"{time} -> TXN : {txn_id} -> Sent : {amt} To {receiver}"
            )

            self.__data[receiver]["history"].append(
                f"{time} -> TXN : {txn_id} -> Received : {amt} From {self.__username}"
            )

            self.save()

            save_data(self.__data)

            print("Money Transferred Successfully")

        except InsufficientBalanceError as e:
            print(e)
    @login_required
    def delete_account(self):

        pin = getpass.getpass(
            "Enter PIN : "
        )

        if not pin.isdigit():
            print("PIN Must Be Numbers")
            return False

        if int(pin) != self.__pin:
            print("Wrong PIN")
            return False

        confirm = input(
            "Delete Account? (Y/N): "
        ).upper()

        if confirm != "Y":
            print("Cancelled")
            return False

        del self.__data[self.__username]

        save_data(self.__data)

        print("Account Deleted Successfully")

        return True
    
data = load_data()

ATM.bank_info()

while True:

    print("\n===== MAIN MENU =====")
    print("1. Create Account")
    print("2. Login")
    print("3. Exit")

    choice = input("Enter Choice : ")

    if choice == "1":

        username = input(
            "Create Username : "
        )

        if not re.match(
            r'^[A-Za-z0-9_@#$*]+$',
            username
        ):
            print("Invalid Username")
            continue

        if username in data:
            print("Username Already Exists")
            continue

        pin = getpass.getpass(
            "Create 4 Digit PIN : "
        )

        if not ATM.validate_pin(pin):
            print("PIN Must Be 4 Digits")
            continue

        try:
            balance = int(
                input("Enter Initial Balance : ₹")
            )

        except ValueError:
            print("Invalid Balance")
            continue

        if balance < 0:
            print("Balance Cannot Be Negative")
            continue

        while True:

            account_no = random.randint(
                100000,
                999999
            )

            exists = False

            for user in data.values():

                if user["account_no"] == account_no:
                    exists = True
                    break

            if not exists:
                break

        data[username] = {
            "account_no": account_no,
            "pin": int(pin),
            "balance": balance,
            "history": []
        }

        save_data(data)

        print("Account Created Successfully")
        print("Account Number :", account_no)

    elif choice == "2":

        username = input("Enter Username : ")

        if username not in data:
            print("Account Not Found")
            continue

        try:
            pin = int(
                getpass.getpass("Enter PIN : ")
            )

        except ValueError:
            print("Invalid PIN")
            continue

        if pin != data[username]["pin"]:
            print("Wrong PIN")
            continue

        print(f"\nWelcome {username}")

        atm = ATM(username, data)

        while True:

            print("\n===== ATM MENU =====")
            print("1. Deposit")
            print("2. Withdraw")
            print("3. Check Balance")
            print("4. Transaction History")
            print("5. Change PIN")
            print("6. Transfer Money")
            print("7. Account Details")
            print("8. Delete Account")
            print("9. Logout")

            ch = input("Enter Choice : ")

            if ch == "1":

                try:
                    amt = int(
                        input("Enter Amount : ₹")
                    )

                    atm.deposit(amt)

                except ValueError:
                    print("Invalid Amount")

            elif ch == "2":

                try:
                    amt = int(
                        input("Enter Amount : ₹")
                    )

                    atm.withdraw(amt)

                except ValueError:
                    print("Invalid Amount")

            elif ch == "3":
                atm.show_balance()

            elif ch == "4":
                atm.show_history()

            elif ch == "5":
                atm.change_pin()

            elif ch == "6":
                atm.transfer_money()

            elif ch == "7":
                atm.show_account_details()

            elif ch == "8":

                deleted = atm.delete_account()

                if deleted:
                    break

            elif ch == "9":

                print("Logged Out Successfully")
                break

            else:
                print("Invalid Choice")

    elif choice == "3":

        print("Thank You For Using ATM")
        break

    else:
        print("Invalid Choice")




    