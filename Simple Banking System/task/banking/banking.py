# Write your code here
import random
import sqlite3


class BankingSystem:
    random.seed()
    conn = None

    def __init__(self):
        self.bank_accounts = {}
        self.conn = sqlite3.connect('card.s3db')
        c = self.conn.cursor()
        c.execute('''SELECT count(name) from sqlite_master where type ="table" and name = "card"''')
        if c.fetchone()[0] == 1:
            print('Table exists')
        else:
            c.execute('''CREATE TABLE card 
            ([id] INTEGER primary key, [number] TEXT, [pin] TEXT, [balance] INTEGER DEFAULT 0)''')
        self.conn.commit()

    def login(self) -> str:
        card_num = input('Enter your card number:\n')
        pin = input('Enter your PIN:')
        curr = self.conn.cursor()
        curr.execute(f"select count(*) from card where number = {card_num} and pin ={pin}")
        if curr.fetchone()[0] > 0:
            print('You have successfully logged in!')
            while True:
                user_choice = input(
                    '1. Balance\n2. Add Income\n 3. Do Transfer\n 4. Close Account \n5. Log out\n0. Exit\n')
                if user_choice == '1':
                    print(f'\nBalance: {self.get_balance(card_num)}\n')
                elif user_choice == '2':
                    self.add_income(card_num)
                elif user_choice == '3':
                    self.do_transfer(card_num)
                elif user_choice == '4':
                    self.close_account(card_num)
                    return user_choice
                elif user_choice == '5':
                    print('You have successfully logged out!')
                    return user_choice
                elif user_choice == '0':
                    return 'exit'
        else:
            print('Wrong card number or PIN!')
            return ''

    def create_account(self):
        created = False
        new_acct_num = ''
        curr = self.conn.cursor()
        while not created:
            new_acct = random.randint(100000000, 999999999)
            bank_id_num = '400000' + str(new_acct)
            check_sum = self.get_check_sum(bank_id_num)
            new_acct_num = bank_id_num + check_sum
            curr.execute(f"select count(*) from card where number = {new_acct_num}")

            if curr.fetchone()[0] == 0:
                created = True

        # print(len(new_acct_num))
        new_pin = str(random.randint(1000, 10000))
        self.bank_accounts[new_acct_num] = new_pin
        curr.execute(f"insert into card (number, pin, balance) values({new_acct_num}, {new_pin}, 0)")
        self.conn.commit()
        print('Your card has been created')
        print('Your card number:')
        print(new_acct_num)
        print('Your card PIN:')
        print(new_pin)

    def get_check_sum(self, bank_id_num) -> str:
        chars = list(bank_id_num)
        digits = [int(num) for num in chars]
        sum = 0
        for i in range(len(digits)):
            if i % 2 == 0:
                digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9

            sum += digits[i]

        for i in range(10):
            if (sum + i) % 10 == 0:
                return str(i)

    def get_balance(self, card_num):
        curr = self.conn.cursor()
        curr.execute(f'select cd.balance from card cd where number = {card_num}')
        return curr.fetchone()[0]

    def add_income(self, card_num):
        income = input('\nEnter Income: ')
        balance = self.get_balance(card_num)
        new_balance = int(income) + balance
        curr = self.conn.cursor()
        curr.execute(f'update card set balance = {new_balance} where number = {card_num}')

        self.conn.commit()
        print('Income was added!\n')

    def do_transfer(self, card_num):

        print('Transfer')
        dest_card = input('Enter card number:')
        if dest_card == card_num:
            print("You can't transfer money to the same account!")
            return
        wrong_card_num = False
        if len(dest_card) != 16:
            wrong_card_num = True
        if not wrong_card_num:
            last_digit = dest_card[len(dest_card) - 1]
            check_sum = self.get_check_sum(dest_card[0:len(dest_card) - 1])
            if check_sum != last_digit:
                wrong_card_num = True

        if wrong_card_num:
            print('Probably you made a mistake in the card number. Please try again!')
            return

        curr = self.conn.cursor()
        curr.execute(f"select count(*) from card where number = {dest_card} ")
        if curr.fetchone()[0] == 0:
            print("Such a card does not exist.")
            return
        transfer_amt = int(input('Enter how much money you want to transfer:'))
        balance = self.get_balance(card_num)
        dest_balance = self.get_balance(dest_card)
        if balance < transfer_amt:
            print('Not enough money!')
        else:
            new_dest_balance = dest_balance + transfer_amt
            new_balance = balance - transfer_amt
            curr.execute(f'update card set balance = {new_balance} where number = {card_num}')
            curr.execute(f'update card set balance = {new_dest_balance} where number = {dest_card}')
            self.conn.commit()
            print('Success!')

    def close_account(self, card_num):
        curr = self.conn.cursor()
        curr.execute(f'delete from card where number ={card_num}')
        self.conn.commit()
        print('The account has been closed!')


isExit = False

banking_system = BankingSystem()

while not isExit:
    user_choice = input('1. Create an account\n' +
                        '2. Log into account\n'
                        '0. Exit\n')

    if user_choice == '0':
        isExit = True
    elif user_choice == '2':
        ret_str = banking_system.login()
        if ret_str == 'exit':
            isExit = True
    elif user_choice == '1':
        banking_system.create_account()

print('Bye!')
