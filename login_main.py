import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget, QFrame
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
# from after_login import MainWindow

class DatabaseConnection:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(host='localhost', user='root', password='', database='login')
            self.cur = self.conn.cursor()
            print('Connection successful')
        except mysql.connector.Error as err:
            print('Connection failed:', err)

    def close(self):
        self.cur.close()
        self.conn.close()

class LoginApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        loadUi("loginpage.ui", self)

        self.db = DatabaseConnection()

        self.login.clicked.connect(self.get_data)
        self.new_2.clicked.connect(self.new_acc)

    def get_data(self):
        self.u_id = self.user_id.text()
        self.pin = self.password.text()

        sql = "SELECT * FROM infos WHERE id = %s and pin = %s"
        d = (self.u_id, self.pin)

        try:
            self.db.cur.execute(sql, d)
            self.result = self.db.cur.fetchone()
            if self.result is not None:
                if self.u_id == str(self.result[1]) and self.pin == self.result[2]:
                    self.after_login()

                else:
                    QMessageBox.warning(self, 'Invalid Pin or Id', 'Invalid login credentials')
            else:
                QMessageBox.warning(self, 'No User Found', 'No user found with the provided credentials')
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Database Error', f'Database error: {err}')

    def first_page(self):
        loadUi('loginpage.ui', self)
        # Reconnect the buttons on the home page
        self.login.clicked.connect(self.get_data)
        self.new_2.clicked.connect(self.new_acc)

    def new_acc(self):
        loadUi('new_acc.ui', self)
        self.create_new.clicked.connect(self.to_db)
        self.home.clicked.connect(self.first_page)

    def to_db(self):
        temp_name = self.new_name.text()
        temp_id = self.new_id.text()
        temp_pin = self.new_pin.text()

        # Check if the user ID is already in use
        sql_check = 'SELECT id FROM infos WHERE id = %s'
        self.db.cur.execute(sql_check, (temp_id,))
        temp1_id = self.db.cur.fetchone()

        if temp1_id is None:
            # Insert the new account into the database
            sql_insert = 'INSERT INTO infos (id, pin, name) VALUES (%s, %s, %s)'
            self.db.cur.execute(sql_insert, (temp_id, temp_pin, temp_name))
            self.db.conn.commit()
            QMessageBox.information(self, 'Success', 'Account Created Successfully', QMessageBox.Ok)
            self.first_page()  # Go back to the login page after account creation
        else:
            QMessageBox.warning(self, 'Warning', 'The selected user ID is already in use', QMessageBox.Ok)

    def closeEvent(self, event):
        self.db.close()
    def set_label_texts(self, label_texts):
        for label_name, text_value in label_texts.items():
            label = self.profile.findChild(QtWidgets.QLabel, label_name)
            if label:
                label.setText(str(text_value))

    def after_login(self):
        loadUi('main.ui', self) 
        label_names = ['name', 'bank_id', 'balance']
        text_values = [f'Welcome {self.result[0]}', self.result[1], self.result[3]]
        label_texts = dict(zip(label_names, text_values))
        
        self.set_label_texts(label_texts)
        self.balance = self.balance.text()
        # self.balance = int(self.balance)
        self.current_page()
        # Connect push buttons 
        self.pushButton_2.clicked.connect(self.current_page)
        self.pushButton_3.clicked.connect(self.show_transaction)
        self.pushButton_5.clicked.connect(self.show_settings)

    def current_page(self):
        self.stackedWidget.setCurrentWidget(self.profile)
        self.deposit.clicked.connect(self.deposit_method)
        self.withdraw_2.clicked.connect(self.withdraw_method)
    def withdraw_method(self):
        self.stackedWidget.setCurrentWidget(self.withdraw_page)
        self.confirm_2.clicked.connect(self.click_w)
    def deposit_method(self):
        self.stackedWidget.setCurrentWidget(self.deposite_page)
        self.confirm.clicked.connect(self.click_d)
        self.confirm.setEnabled(True)
    def latest_balance(self):
        sql = 'SELECT balance FROM infos WHERE id = %s'
        d = (self.u_id,)
        self.db.cur.execute(sql, d)
        self.l_balance = self.db.cur.fetchone()
        return self.l_balance[0]

        
    def click_w(self):
        entered_pin = self.lineEdit_3.text()  # Get the entered PIN from the QLineEdit
        self.lineEdit_3.clear()
        if entered_pin == self.pin:
            amount = self.lineEdit_4.text()
            self.lineEdit_4.clear()
            try:
                amount = int(amount)
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid amount.')
                return  # Exit the function if the amount is not a valid integer
            
            balance = self.latest_balance()
            rem = balance - amount
            if rem > 500:
                sql = 'UPDATE infos SET balance = balance - %s WHERE id = %s'
                data = (amount, self.result[1])
 
                try:
                    self.db.cur.execute(sql, data)
                    self.db.conn.commit()
                    upd_balance = self.result[3] - amount  # Update the result with the new balance
                    self.set_label_texts({'balance': upd_balance})
                    QMessageBox.information(self, 'Success', 'Withdrawl successfully', QMessageBox.Ok)
                except mysql.connector.Error as err:
                    QMessageBox.critical(self, 'Database Error', f'Database error: {err}')
            else:
                QMessageBox.warning(self,'Insufficient Balance', 'Your Balance is less than Rs.500')
        else:
            QMessageBox.warning(self, 'Invalid PIN', 'Invalid PIN entered. Please try again.')


    def click_d(self):
        entered_pin = self.lineEdit_2.text()  # Get the entered PIN from the QLineEdit
        self.lineEdit_2.clear()
        pin = str(self.latest_pin())
        if entered_pin == pin:
            amount = self.lineEdit.text()
            self.lineEdit.clear()
            try:
                amount = int(amount)
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid amount.')
                return  # Exit the function if the amount is not a valid integer

            sql = 'UPDATE infos SET balance = balance + %s WHERE id = %s'
            data = (amount, self.result[1])

            try:
                self.db.cur.execute(sql, data)
                self.db.conn.commit()
                upd_balance = self.result[3] + amount  # Update the result with the new balance
                self.set_label_texts({'balance': f'RS.{upd_balance}'})
                QMessageBox.information(self, 'Success', 'Deposited successfully', QMessageBox.Ok)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, 'Database Error', f'Database error: {err}')
        else:
            QMessageBox.warning(self, 'Invalid PIN', 'Invalid PIN entered. Please try again.')
    def latest_pin(self):
        sql = 'SELECT pin FROM infos WHERE id = %s'
        d = (self.u_id,)
        self.db.cur.execute(sql, d)
        pin = self.db.cur.fetchone()

        if pin:
            self.pin = pin[0]  # Update the self.pin attribute with the latest PIN
            return self.pin
        else:
            return None


    def show_transaction(self):
        self.stackedWidget.setCurrentWidget(self.transfer)
        self.pushButton.clicked.connect(self.transaction)
    def transaction(self):
        r_id = self.lineEdit_6.text()
        self.lineEdit_6.clear()

        sql = 'SELECT * FROM infos WHERE id = %s'
        self.db.cur.execute(sql, (r_id,))
        result = self.db.cur.fetchone()

  
        if result is not None:
            amt = self.lineEdit_10.text()
            self.lineEdit_10.clear()
            entered_pin = self.lineEdit_9.text()
            self.lineEdit_9.clear()
            pin = self.latest_pin()
            pin = str(pin)

            if pin == entered_pin:
                try:
                    amt = int(amt)
                    self.balance = int(self.balance)
                    self.set_label_texts({'balance':f'{self.balance - amt}'})
                    rem = self.balance - amt
                    if rem > 500:
                        sql = 'UPDATE infos SET balance = balance + %s WHERE id = %s'
                        d = (amt, r_id)
                        self.db.cur.execute(sql, d)
                        self.db.conn.commit()
                        sql = 'UPDATE infos SET balance = balance - %s WHERE id = %s'
                        d = (amt, self.u_id)
                        self.db.cur.execute(sql, d)
                        self.db.conn.commit()
                        QMessageBox.information(self, 'Success', f'Rs.{amt} has been transfer to bank id {r_id}', QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self,'Insufficient Balance', 'Your Balance is less than Rs.500')
                except Exception as e:
                    QMessageBox.warning(self, 'Invalid INPUT', 'Invalid Id or Amount')
            else:
                QMessageBox.warning(self, 'Invalid PIN', 'Invalid PIN entered. Please try again.')
        else:
            QMessageBox.warning(self, 'Invalid ID', 'Invalid Id')
            return

    def show_settings(self):
        self.stackedWidget.setCurrentWidget(self.setting)
        self.switch_2.clicked.connect(self.first_page)
        self.reset.clicked.connect(self.pin_reset)
        self.log_out.clicked.connect(self.close_page)
    def pin_reset(self):
        self.stackedWidget.setCurrentWidget(self.reset_page)
        self.confirm_3.clicked.connect(self.reset_confirm)
    
    def reset_confirm(self):
        n_pin = self.lineEdit_5.text()
        self.lineEdit_5.clear()
        try:
            n_pin = int(n_pin)
            sql = 'UPDATE infos SET pin = %s WHERE id = %s'
            d = (n_pin, self.u_id)
            self.db.cur.execute(sql,d)
            self.db.conn.commit()
            QMessageBox.information(self, 'Success', 'Pin Changed', QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f'Database error: {e}')

    def close_page(self):
        sys.exit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec_())
