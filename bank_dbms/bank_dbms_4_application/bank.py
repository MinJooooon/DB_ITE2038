import pymysql as pms
from datetime import datetime

connection = pms.connect(
    host='localhost',
    port=3306,
    user='root',
    password='',
    db='mysql'
)

cursor = connection.cursor()


def create_bank_dbms():
    cursor.execute('CREATE DATABASE IF NOT EXISTS BANK;')
    cursor.execute('use BANK')

    cursor.execute('CREATE TABLE IF NOT EXISTS BRANCH ('
                   'branch_name VARCHAR(20) NOT NULL,'
                   'branch_id INT NOT NULL AUTO_INCREMENT,'
                   'PRIMARY KEY (branch_id),'
                   'UNIQUE (branch_name) );')

    cursor.execute('CREATE TABLE IF NOT EXISTS ADMINISTRATOR ('
                   'administrator_name VARCHAR(20) NOT NULL,'
                   'administrator_id INT NOT NULL AUTO_INCREMENT,'
                   'branch_id INT NOT NULL DEFAULT 1,'
                   'birth_date DATE NOT NULL,'
                   'administrator_address VARCHAR(20) NOT NULL,'
                   'PRIMARY KEY (administrator_id),'
                   'FOREIGN KEY (branch_id) REFERENCES BRANCH(branch_id) '
                   'ON DELETE SET DEFAULT ON UPDATE CASCADE );')

    cursor.execute('CREATE TABLE IF NOT EXISTS USER ('
                   'user_name VARCHAR(20) NOT NULL,'
                   'user_ssn VARCHAR(14) NOT NULL,'
                   'user_address VARCHAR(20) NOT NULL,'
                   'user_id INT NOT NULL AUTO_INCREMENT,'
                   'belong_branch_id INT NOT NULL DEFAULT 1,'
                   'treated_administrator_id INT NOT NULL DEFAULT 1,'
                   'PRIMARY KEY (user_id),'
                   'FOREIGN KEY (belong_branch_id) REFERENCES BRANCH(branch_id)'
                   'ON DELETE SET DEFAULT ON UPDATE CASCADE,'
                   'FOREIGN KEY (treated_administrator_id) REFERENCES ADMINISTRATOR(administrator_id)'
                   'ON DELETE SET DEFAULT ON UPDATE CASCADE,'
                   'UNIQUE(user_ssn) );')

    cursor.execute('CREATE TABLE IF NOT EXISTS USER_NATIONALITY ('
                   'user_id INT NOT NULL,'
                   'nationality VARCHAR(56) NOT NULL,'
                   'PRIMARY KEY (user_id, nationality),'
                   'FOREIGN KEY (user_id) REFERENCES USER(user_id)'
                   'ON DELETE CASCADE );')

    cursor.execute('CREATE TABLE IF NOT EXISTS USER_PHONE_NUMBER ('
                   'user_id INT NOT NULL,'
                   'phone_number VARCHAR(13) NOT NULL,'
                   'PRIMARY KEY (user_id, phone_number),'
                   'FOREIGN KEY (user_id) REFERENCES USER(user_id)'
                   'ON DELETE CASCADE );')

    cursor.execute('CREATE TABLE IF NOT EXISTS ACCOUNT ('
                   'account_number VARCHAR(17) NOT NULL,'
                   'account_user_id INT NOT NULL,'
                   'account_type VARCHAR(20) NOT NULL,'
                   'account_opening_date DATE NOT NULL,'
                   'account_balance INT NOT NULL DEFAULT 0,'
                   'PRIMARY KEY (account_number),'
                   'FOREIGN KEY (account_user_id) REFERENCES USER(user_id)'
                   'ON DELETE CASCADE );')

    cursor.execute('CREATE TABLE IF NOT EXISTS TRANSACTION_BREAKDOWN ('
                   'transaction_account_number VARCHAR(17) NOT NULL,'
                   'transaction_index INT NOT NULL AUTO_INCREMENT,'
                   'transaction_date DATE NOT NULL,'
                   'transaction_type VARCHAR(20) NOT NULL,'
                   'transaction_amount INT NOT NULL,'
                   'PRIMARY KEY (transaction_index),'
                   'FOREIGN KEY (transaction_account_number) REFERENCES ACCOUNT(account_number)'
                   'ON DELETE CASCADE );')

    cursor.execute('CREATE TABLE IF NOT EXISTS ADMINISTRATOR_PHONE_NUMBER ('
                   'administrator_id INT NOT NULL,'
                   'phone_number VARCHAR(13) NOT NULL,'
                   'PRIMARY KEY (administrator_id, phone_number),'
                   'FOREIGN KEY (administrator_id) REFERENCES ADMINISTRATOR(administrator_id)'
                   'ON DELETE CASCADE );')

    cursor.execute('CREATE TABLE IF NOT EXISTS ADMINISTRATION_BREAKDOWN ('
                   'administrator_id INT NOT NULL,'
                   'administration_index INT NOT NULL AUTO_INCREMENT,'
                   'administration_date DATE NOT NULL,'
                   'treated_account_number VARCHAR(17) NOT NULL,'
                   'administration_type VARCHAR(20) NOT NULL,'
                   'PRIMARY KEY (administration_index),'
                   'FOREIGN KEY (treated_account_number) REFERENCES ACCOUNT(account_number) '
                   'ON DELETE CASCADE, '
                   'FOREIGN KEY (administrator_id) REFERENCES ADMINISTRATOR(administrator_id) '
                   'ON DELETE CASCADE);')
    connection.commit()


def user_interface():
    print()
    print("==============================")
    print("User Interface")
    print("0.Return to Previous Menu")
    print("1.Deposit/Withdrawal")
    print("2.Check Deposit/Withdrawal Details")
    print("3.User Registration")
    print("4.User Deletion")
    print("5.User Info Change")
    print("6.Account Registration")
    print("7.Account Deletion")
    print("==============================")
    print("Input: ", end='')
    user_command = int(input())
    if user_command == 0:
        return

    elif user_command == 1:  # Deposit/Withdrawal
        account_number = input("Please enter your account number: ")
        cursor.execute("SELECT * FROM account WHERE account_number=%s;", account_number)
        result = cursor.fetchone()
        if result is None:
            print("There's no account for that account number! Please try again")
            return

        tr_type = input("Please enter your transaction type(D:Deposit/W:Withdrawal): ")
        if tr_type != "D" and tr_type != "W":
            print("Please enter one of D or P")
            return

        tr_amount = int(input("Please enter your transaction amount: "))

        tr_date = datetime.today().strftime('%Y-%m-%d')

        if tr_type == "D":
            cursor.execute("UPDATE account SET account_balance = account_balance + %s WHERE account_number = %s",
                           (tr_amount, account_number))
            cursor.execute("INSERT INTO "
                           "TRANSACTION_BREAKDOWN"
                           "(transaction_account_number,transaction_date,transaction_type,transaction_amount) "
                           "values(%s,%s,\"Deposit\",%s)", (account_number, tr_date, tr_amount))
            print("Deposit Successful!")
        elif tr_type == "W":
            cursor.execute("SELECT account_balance FROM account WHERE account_number=%s", account_number)
            result = cursor.fetchone()
            balance = result[0]
            if balance < tr_amount:
                print("The withdrawal amount is higher than the balance")
                print("This account balance is " + str(balance))
                return
            cursor.execute("UPDATE account SET account_balance = account_balance - %s WHERE account_number = %s",
                           (tr_amount, account_number))
            cursor.execute("INSERT INTO "
                           "TRANSACTION_BREAKDOWN"
                           "(transaction_account_number,transaction_date,transaction_type,transaction_amount) "
                           "values(%s,%s,\"Withdrawal\",%s)", (account_number, tr_date, tr_amount))
            print("Withdrawal Successful!")

    elif user_command == 2:  # Check Deposit/Withdrawal Details
        account_number = input("Please enter your account number: ")
        cursor.execute("SELECT * FROM transaction_breakdown WHERE transaction_account_number=%s", account_number)
        result_set = cursor.fetchall()
        if result_set == ():
            print("There's no transaction breakdown for that account number! Please try again")
            return
        print()
        for row in result_set:
            print("Date: " + str(row[2]))
            print("Type: " + row[3])
            print("Amount: " + str(row[4]))
            print()

    elif user_command == 3:  # User Registration
        user_name = input("Enter user's name you want to register(Up to 20 letters): ")
        if len(user_name) > 20:
            print("You can enter up to 20 letters of your name. Please try again")
            return
        user_ssn = input("Enter user's ssn you want to register(ex.990101-1234567): ")
        if len(user_ssn) != 14 or user_ssn[6] != "-":
            print("You should enter your ssn according to the style. Please try again.(ex.990101-1234567)")
            return
        user_address = input("Enter user's address you want to register(ex.Seoul): ")
        if len(user_address) > 20:
            print("You can enter up to 20 letters of your address. Please try again.")
            return

        user_branch = int(input("Enter user's branch id you want to register: "))
        cursor.execute("SELECT * FROM branch WHERE branch_id=%s;", user_branch)
        result = cursor.fetchone()
        if result is None:
            print("There's no branch for that id! Please try again.")
            return

        user_administrator_id = int(input("Enter the id of administrator manage the user: "))
        cursor.execute("SELECT * FROM administrator WHERE administrator_id=%s", user_administrator_id)
        result1 = cursor.fetchone()
        if result1 is None:
            print("There's no administrator for that id! Please try again.")
            return

        print("Enter user's nationalities you want to register")
        print("if more than two, please enter them all with comma")
        print("ex.Korea,USA")
        user_nationalities = input("nationality: ")
        nationalities_list = user_nationalities.split(",")
        for n in nationalities_list:
            if len(n) > 56:
                print("You can enter up to 56 letters of your nationality. Please try again.")
                return

        print("Enter user's phone numbers you want to register")
        print("if more than two, please enter them all with comma")
        print("ex.010-1234-5678,010-2345-6789")
        user_phone_numbers = input("phone number: ")
        phone_numbers_list = user_phone_numbers.split(",")
        for p in phone_numbers_list:
            if len(p) != 13 or p[3] != "-" or p[8] != "-":
                print("You should enter your phone number according to the style. Please try again.(ex.010-1234-5678)")
                return

        cursor.execute("INSERT INTO "
                       "USER(user_name,user_ssn,user_address,belong_branch_id,treated_administrator_id) "
                       "values(%s,%s,%s,%s,%s)",
                       (user_name, user_ssn, user_address, user_branch, user_administrator_id))
        connection.commit()

        # 방금 register한 user의 id 탐색
        cursor.execute("SELECT MAX(user_id) AS registered_id FROM user")
        result = cursor.fetchone()
        user_id = result[0]

        for nation in nationalities_list:
            cursor.execute("INSERT INTO USER_NATIONALITY values(%s,%s)", (user_id, nation))

        for num in phone_numbers_list:
            cursor.execute("INSERT INTO USER_PHONE_NUMBER values(%s,%s)", (user_id, num))

        print("User registration Successful!")

    elif user_command == 4:  # User Deletion
        user_id = int(input("Enter user's id you want to delete: "))
        cursor.execute("SELECT user_id FROM user WHERE user_id=%s", user_id)
        result = cursor.fetchone()
        if result is None:
            print("There is no user for that user id!")
        else:
            cursor.execute("SELECT account_balance FROM account WHERE account_user_id=%s", user_id)
            result_set = cursor.fetchall()
            if result_set != ():
                for row in result_set:
                    if row[0] != 0:
                        print("This user have some accounts whose balance is not 0")
                        print("User can be deleted only when all of having account's balance are 0")
                        return
            cursor.execute("DELETE FROM user WHERE user_id=%s;", user_id)
            print("user's id for \"" + str(user_id) + "\" has been deleted")

    elif user_command == 5:  # User Info Change
        user_id = int(input("Enter user's id you want to change: "))
        cursor.execute("SELECT user_id FROM user WHERE user_id=%s", user_id)
        result = cursor.fetchone()
        if result is None:
            print("There is no user for that user id!")
        else:
            category = input("Which info you want to change?"
                             "(N:Name, A:Address, B:Branch, Admin:Administrator, Nation:Nationality, P:PhoneNumber): ")
            if category == "N":
                new_name = input("Enter new name(Up to 20 letters): ")
                if len(new_name) > 20:
                    print("You can enter up to 20 letters of your name. Please try again.")
                    return
                cursor.execute("UPDATE user SET user_name=%s WHERE user_id=%s",
                               (new_name, user_id))
                print("Name change successful!")

            elif category == "A":
                new_address = input("Enter new address(ex.Seoul): ")
                if len(new_address) > 20:
                    print("You can enter up to 20 letters of your address. Please try again.")
                    return
                cursor.execute("UPDATE user SET user_address=%s WHERE user_id=%s",
                               (new_address, user_id))
                print("Address change successful!")

            elif category == "B":
                new_branch = int(input("Enter new branch_id: "))
                cursor.execute("SELECT * FROM branch WHERE branch_id = %s", new_branch)
                result = cursor.fetchone()
                if result is None:
                    print("There is no such branch id!")
                    return
                cursor.execute("UPDATE user SET belong_branch_id=%s WHERE user_id=%s",
                               (new_branch, user_id))
                print("Branch change successful!")

            elif category == "Admin":
                new_admin = int(input("Enter new administrator_id: "))
                cursor.execute("SELECT * FROM administrator WHERE administrator_id = %s", new_admin)
                result = cursor.fetchone()
                if result is None:
                    print("There is no such administrator id!")
                    return
                cursor.execute("UPDATE user SET treated_administrator_id=%s WHERE user_id=%s",
                               (new_admin, user_id))
                print("Administrator change successful!")

            elif category == "Nation":
                nation_command = input("Enter the command you want(Add:A, Delete: D): ")
                if nation_command == "A":
                    new_nation = input("Enter your new nationality: ")
                    if len(new_nation) > 56:
                        print("You can enter up to 56 letters of your nationality. Please try again.")
                        return
                    cursor.execute("INSERT INTO user_nationality values(%s,%s)", (user_id, new_nation))
                    print("Nationality addition successful!")
                elif nation_command == "D":
                    origin_nation = input("Enter your existing nationality: ")
                    cursor.execute("SELECT nationality FROM user_nationality WHERE user_id=%s and nationality=%s",
                                   (user_id, origin_nation))
                    result = cursor.fetchone()
                    if result is None:
                        print("There is no such nationality!")
                        return
                    cursor.execute("DELETE FROM user_nationality WHERE user_id=%s and nationality=%s",
                                   (user_id, origin_nation))
                    print("Nationality deletion successful!")
                else:
                    print("Please enter A or D")

            elif category == "P":
                phone_command = input("Enter the command you want(Add:A, Delete: D): ")
                if phone_command == "A":
                    new_phone = input("Enter your new phone number(ex.010-1234-5678): ")
                    if len(new_phone) != 13 or new_phone[3] != "-" or new_phone[8] != "-":
                        print("You should enter your phone number according to the style. "
                              "Please try again.(ex.010-1234-5678)")
                        return
                    cursor.execute("INSERT INTO user_phone_number values(%s,%s)", (user_id, new_phone))
                    print("Phone number addition successful!")
                elif phone_command == "D":
                    origin_phone = input("Enter your existing phone number: ")
                    cursor.execute("SELECT phone_number FROM user_phone_number WHERE user_id=%s and phone_number=%s",
                                   (user_id, origin_phone))
                    result = cursor.fetchone()
                    if result is None:
                        print("There is no such phone number!")
                        return
                    cursor.execute("DELETE FROM user_phone_number WHERE user_id=%s and phone_number=%s",
                                   (user_id, origin_phone))
                    print("Phone number deletion successful!")
                else:
                    print("Please enter A or D")

            else:
                print("Please enter one of N, A, B, Admin, Nation, P")

    elif user_command == 6:  # Account Registration
        account_number = input("Enter account number you want to register(Up to 17 letters): ")
        if len(account_number) > 17:
            print("You can enter up to 17 letters of your account number. Please try again.")
            return
        cursor.execute("SELECT * FROM account WHERE account_number = %s;", account_number)
        account_result = cursor.fetchone()
        if account_result is not None:
            print("That account number already exists")
            return

        user_id = int(input("Enter user's id of the account you want to register: "))
        cursor.execute("SELECT * FROM user WHERE user_id=%s;", user_id)
        result = cursor.fetchone()
        if result is None:
            print("There's no user for that id! Please try again")
            return

        # 계좌 최대 3개까지 개설
        cursor.execute("SELECT COUNT(*) FROM account WHERE account_user_id=%s", user_id)
        count = cursor.fetchone()
        if count[0] >= 3:
            print("User cannot have more thant 3 accounts")
            return

        account_type = ""
        type_initial = input("Enter the type of account want to register(B:Bankbook, I:Installment saving, C:CMA):")
        if type_initial == "B":
            account_type = "Bankbook"
        elif type_initial == "I":
            account_type = "Installment"
        elif type_initial == "C":
            account_type = "CMA"
        else:
            print("Please enter one of B, I, C")
            return

        account_opening_date = datetime.today().strftime('%Y-%m-%d')

        cursor.execute("INSERT INTO "
                       "ACCOUNT values(%s,%s,%s,%s,0)", (account_number, user_id, account_type, account_opening_date))

        print("Account registration Successful!")

    elif user_command == 7:  # Account Deletion
        account_number = input("Enter account number you want to delete: ")
        cursor.execute("SELECT account_balance FROM account WHERE account_number=%s", account_number)
        result = cursor.fetchone()
        if result is None:
            print("There is no account for that account number!")
        else:
            balance = result[0]
            if balance != 0:
                print("You can delete the account with a balance of 0")
                return
            else:
                cursor.execute("DELETE FROM account WHERE account_number=%s;", account_number)
                print("account for \"" + account_number + "\" has been deleted")

    else:
        print("Wrong Input! Please try again")

    connection.commit()


def admin_interface():
    print()
    print("==============================")
    print("Administrator Interface")
    print("0.Return to Previous Menu")
    print("1.Administer Account")
    print("2.Check Administration Details")
    print("3.User Search")
    print("4.Account Search")
    print("5.Administrator Registration")
    print("6.Administrator Deletion")
    print("7.Administrator Info Change")
    print("8.Administrator Search")
    print("9.Branch Registration")
    print("10.Branch Deletion")
    print("11.Branch Info Change")
    print("12.Branch Search")
    print("==============================")
    print("Input: ", end='')
    admin_command = int(input())
    if admin_command == 0:
        return

    elif admin_command == 1:  # Administer Account
        administrator_id = int(input("Please enter your administrator id: "))
        cursor.execute("SELECT * FROM administrator WHERE administrator_id=%s", administrator_id)
        result = cursor.fetchone()
        if result is None:
            print("There's no administrator for that administrator id! Please try again")

        account_number = input("Please enter the account number you want to administer: ")
        cursor.execute("SELECT * FROM account WHERE account_number=%s;", account_number)
        result1 = cursor.fetchone()
        if result1 is None:
            print("There's no account for that account number! Please try again")
            return
        user_id = result1[1]
        cursor.execute("SELECT treated_administrator_id FROM user WHERE user_id=%s", user_id)
        result2 = cursor.fetchone()
        user_admin_id = result2[0]
        if administrator_id != user_admin_id:
            print("Administrators can only administer accounts assigned to them")
            return

        admin_date = datetime.today().strftime('%Y-%m-%d')

        admin_type = ""
        type_initial = input("Enter the type of administration"
                             "(C:Check Issue, A:Account Bookkeeping:, P: Pattern Analysis): ")
        if type_initial == "C":
            admin_type = "Check Issue"
        elif type_initial == "A":
            admin_type = "Account Bookkeeping"
        elif type_initial == "P":
            admin_type = "Pattern Analysis"
        else:
            print("Please enter one of C, A, P")
            return

        cursor.execute("INSERT INTO administration_breakdown"
                       "(administrator_id,administration_date,treated_account_number,administration_type) "
                       "values(%s,%s,%s,%s)", (administrator_id, admin_date, account_number, admin_type))
        print("Administer Successful!")

    elif admin_command == 2:  # Check Administration Details
        detail_command = input("Which search option you want?(Admin, Account): ")
        if detail_command == "Admin":
            administrator_id = int(input("Please enter administrator id: "))
            cursor.execute("SELECT * FROM administration_breakdown WHERE administrator_id=%s", administrator_id)
            result_set = cursor.fetchall()
            if result_set == ():
                print("There's no administration breakdown for that administrator id! Please try again")
                return
            print()
            for row in result_set:
                print("Date: " + str(row[2]))
                print("Administrator ID: " + str(row[0]))
                print("Account Number: " + row[3])
                print("Type: " + row[4])
                print()

        elif detail_command == "Account":
            account_number = input("Please enter account number: ")
            cursor.execute("SELECT * FROM administration_breakdown WHERE treated_account_number=%s", account_number)
            result_set = cursor.fetchall()
            if result_set == ():
                print("There's no administration breakdown for that account number! Please try again")
                return
            print()
            for row in result_set:
                print("Date: " + str(row[2]))
                print("Administrator ID: " + str(row[0]))
                print("Account Number: " + row[3])
                print("Type: " + row[4])
                print()
        else:
            print("Please enter one of Admin or Account")

    elif admin_command == 3:  # User Search
        search_command = input("Which search option do you want?(A:All, S:Specific): ")
        if search_command == "A":
            cursor.execute("SELECT * FROM user;")
            result_set = cursor.fetchall()
            if result_set == ():
                print("There's no users")
                return
            for row in result_set:
                print("Name: " + row[0])
                print("Ssn: " + row[1])
                print("Address: " + row[2])
                print("User ID: " + str(row[3]))
                print("Belonging branch id: " + str(row[4]))
                print("Treating administrator id: " + str(row[5]))
                user_id = row[3]

                cursor.execute("SELECT nationality FROM user_nationality WHERE user_id=%s", user_id)
                result_nationalities = cursor.fetchall()
                print("Nationalities: ", end='')
                if result_nationalities == ():
                    print()
                for nation in result_nationalities:
                    if nation is result_nationalities[-1]:
                        print(nation[0])
                    else:
                        print(nation[0] + ", ", end='')

                cursor.execute("SELECT phone_number FROM user_phone_number WHERE user_id=%s", user_id)
                result_phones = cursor.fetchall()
                print("Phone numbers: ", end='')
                if result_phones == ():
                    print()
                for num in result_phones:
                    if num is result_phones[-1]:
                        print(num[0])
                    else:
                        print(num[0] + ", ", end='')

                cursor.execute("SELECT account_number FROM account WHERE account_user_id=%s", user_id)
                result_accounts = cursor.fetchall()
                print("Account numbers: ", end='')
                if result_accounts == ():
                    print()
                for num in result_accounts:
                    if num is result_accounts[-1]:
                        print(num[0])
                    else:
                        print(num[0] + ", ", end='')
                print()

        elif search_command == "S":
            user_id = int(input("Enter user's id you want to search: "))
            cursor.execute("SELECT user_id FROM user WHERE user_id=%s", user_id)
            result = cursor.fetchone()
            if result is None:
                print("There is no user for that user id!")
            else:
                cursor.execute("SELECT * FROM user WHERE user_id=%s", user_id)
                result = cursor.fetchone()

                print("Name: " + result[0])
                print("Ssn: " + result[1])
                print("Address: " + result[2])
                print("User ID: " + str(result[3]))
                print("Belonging branch id: " + str(result[4]))
                print("Treating administrator id: " + str(result[5]))

                cursor.execute("SELECT nationality FROM user_nationality WHERE user_id=%s", user_id)
                result_nationalities = cursor.fetchall()
                print("Nationalities: ", end='')
                if result_nationalities == ():
                    print()
                for nation in result_nationalities:
                    if nation is result_nationalities[-1]:
                        print(nation[0])
                    else:
                        print(nation[0] + ", ", end='')

                cursor.execute("SELECT phone_number FROM user_phone_number WHERE user_id=%s", user_id)
                result_phones = cursor.fetchall()
                print("Phone numbers: ", end='')
                if result_phones == ():
                    print()
                for num in result_phones:
                    if num is result_phones[-1]:
                        print(num[0])
                    else:
                        print(num[0] + ", ", end='')

                cursor.execute("SELECT account_number FROM account WHERE account_user_id=%s", user_id)
                result_accounts = cursor.fetchall()
                print("Account numbers: ", end='')
                if result_accounts == ():
                    print()
                for num in result_accounts:
                    if num is result_accounts[-1]:
                        print(num[0])
                    else:
                        print(num[0] + ", ", end='')

        else:
            print("Please enter one of A, S")

    elif admin_command == 4:  # Account Search
        search_command = input("Which search option do you want?(A:All, S:Specific): ")
        if search_command == "A":
            cursor.execute("SELECT * FROM account;")
            result_set = cursor.fetchall()
            if result_set == ():
                print("There's no accounts")
                return
            for row in result_set:
                print("Account number: " + row[0])
                print("Account user id: " + str(row[1]))
                print("Account type: " + row[2])
                print("Account opening date: " + str(row[3]))
                print("Account balance: " + str(row[4]))
                print()

        elif search_command == "S":
            account_number = input("Enter account number you want to search: ")
            cursor.execute("SELECT account_number FROM account WHERE account_number=%s", account_number)
            result = cursor.fetchone()
            if result is None:
                print("There is no account for that account_number!")
            else:
                cursor.execute("SELECT * FROM account WHERE account_number=%s", account_number)
                result = cursor.fetchone()

                print("Account number: " + result[0])
                print("Account user id: " + str(result[1]))
                print("Account type: " + result[2])
                print("Account opening date: " + str(result[3]))
                print("Account balance: " + str(result[4]))
        else:
            print("Please enter one of A, S")

    elif admin_command == 5:  # Administrator Registration
        admin_name = input("Enter administrator's name you want to register(Up to 20 letters): ")
        if len(admin_name) > 20:
            print("You can enter up to 20 letters of your name. Please try again.")
            return
        admin_branch = int(input("Enter administrator's working branch id you want to register: "))
        cursor.execute("SELECT * FROM branch WHERE branch_id=%s;", admin_branch)
        result = cursor.fetchone()
        if result is None:
            print("There's no branch for that id! Please try again")
            return
        admin_birth = input("Enter administrator's birthdate you want to register(ex.2021-01-01): ")
        if len(admin_birth) != 10 or admin_birth[4] != "-" or admin_birth[7] != "-":
            print("You should enter your birth date according to the style. Please try again.(ex.2021-01-01)")
            return
        admin_address = input("Enter administrator's address you want to register(ex.Seoul): ")
        if len(admin_address) > 20:
            print("You can enter up to 20 letters of your address. Please try again.")
            return

        print("Enter administrator's phone numbers you want to register")
        print("if more than two, please enter them all with comma")
        print("ex.010-1234-5678,010-2345-6789")
        admin_phone_numbers = input("phone number: ")
        phone_numbers_list = admin_phone_numbers.split(",")
        for p in phone_numbers_list:
            if len(p) != 13 or p[3] != "-" or p[8] != "-":
                print("You should enter your phone number according to the style. Please try again.(ex.010-1234-5678)")
                return

        cursor.execute("INSERT INTO "
                       "ADMINISTRATOR(administrator_name,branch_id,birth_date,administrator_address) "
                       "values(%s,%s,%s,%s)", (admin_name, admin_branch, admin_birth, admin_address))
        connection.commit()

        # 방금 register한 administrator의 id
        cursor.execute("SELECT MAX(administrator_id) AS registered_id FROM administrator")
        result = cursor.fetchone()
        admin_id = result[0]

        for num in phone_numbers_list:
            cursor.execute("INSERT INTO ADMINISTRATOR_PHONE_NUMBER values(%s,%s)", (admin_id, num))

        print("Administrator registration Successful!")

    elif admin_command == 6:  # Administrator Deletion
        admin_id = int(input("Enter administrator's id you want to delete: "))
        cursor.execute("SELECT administrator_id FROM administrator WHERE administrator_id=%s", admin_id)
        result = cursor.fetchone()
        if result is None:
            print("There is no administrator for that administrator_id!")
        else:
            cursor.execute("DELETE FROM administrator WHERE administrator_id=%s;", admin_id)
            print("administrator's id for \"" + str(admin_id) + "\" has been deleted")

    elif admin_command == 7:  # Administrator Info Change
        admin_id = int(input("Enter administrator's id you want to change: "))
        cursor.execute("SELECT * FROM administrator WHERE administrator_id=%s", admin_id)
        result = cursor.fetchone()
        if result is None:
            print("There is no administrator for that administrator_id!")
        else:
            category = input("Which info you want to change?(N:Name, B:Branch, A:Address, P:PhoneNumber):")
            if category == "N":
                new_name = input("Enter new name(Up to 20 letters): ")
                if len(new_name) > 20:
                    print("You can enter up to 20 letters of your name. Please try again.")
                    return
                cursor.execute("UPDATE administrator SET administrator_name=%s WHERE administrator_id=%s",
                               (new_name, admin_id))
                print("Name change successful!")

            elif category == "B":
                new_branch = int(input("Enter new branch_id: "))
                cursor.execute("SELECT * FROM branch WHERE branch_id=%s", new_branch)
                result = cursor.fetchone()
                if result is None:
                    print("There is no such branch id!")
                    return
                cursor.execute("UPDATE administrator SET branch_id=%s WHERE administrator_id=%s",
                               (new_branch, admin_id))
                print("Branch change successful!")

            elif category == "A":
                new_address = input("Enter new address(ex.Seoul): ")
                if len(new_address) > 20:
                    print("You can enter up to 20 letters of your address. Please try again.")
                    return
                cursor.execute("UPDATE administrator SET administrator_address=%s WHERE administrator_id=%s",
                               (new_address, admin_id))
                print("Address change successful!")

            elif category == "P":
                phone_command = input("Enter the command you want(Add:A, Delete: D): ")
                if phone_command == "A":
                    new_phone = input("Enter your new phone number: ")
                    if len(new_phone) != 13 or new_phone[3] != "-" or new_phone[8] != "-":
                        print(
                            "You should enter your phone number according to the style. "
                            "Please try again.(ex.010-1234-5678)")
                        return
                    cursor.execute("INSERT INTO administrator_phone_number(administrator_id,phone_number)"
                                   "values(%s,%s)", (admin_id, new_phone))
                    print("Phone number addition successful!")
                elif phone_command == "D":
                    origin_phone = input("Enter your existing phone number: ")
                    cursor.execute("SELECT phone_number FROM administrator_phone_number "
                                   "WHERE administrator_id=%s and phone_number=%s",
                                   (admin_id, origin_phone))
                    result = cursor.fetchone()
                    if result is None:
                        print("There's no such phone number!")
                        return
                    cursor.execute("DELETE FROM administrator_phone_number "
                                   "WHERE administrator_id=%s and phone_number=%s",
                                   (admin_id, origin_phone))
                    print("Phone number deletion successful!")
                else:
                    print("Please enter A or D")

            else:
                print("Please enter one of N, B, A, P")

    elif admin_command == 8:  # Administrator Search
        search_command = input("Which search option do you want?(A:All, S:Specific): ")
        if search_command == "A":
            cursor.execute("SELECT * FROM administrator")
            result_set = cursor.fetchall()
            if result_set == ():
                print("There's no administrators")
                return
            for row in result_set:
                print("Name: " + row[0])
                print("Administrator id: " + str(row[1]))
                print("Branch id: " + str(row[2]))
                print("Birth date: " + str(row[3].strftime('%Y-%m-%d')))
                print("Address: " + row[4])
                admin_id = row[1]

                cursor.execute("SELECT phone_number FROM administrator_phone_number WHERE administrator_id=%s",
                               admin_id)
                result_phones = cursor.fetchall()
                print("Phone numbers: ", end='')
                if result_phones == ():
                    print()
                for num in result_phones:
                    if num is result_phones[-1]:
                        print(num[0])
                    else:
                        print(num[0] + ", ", end='')
                print()

        elif search_command == "S":
            admin_id = int(input("Enter administrator's id you want to search: "))
            cursor.execute("SELECT administrator_id FROM administrator WHERE administrator_id=%s", admin_id)
            result = cursor.fetchone()
            if result is None:
                print("There is no administrator for that administrator id!")
            else:
                cursor.execute("SELECT * FROM administrator WHERE administrator_id=%s", admin_id)
                result = cursor.fetchone()

                print("Name: " + result[0])
                print("Administrator id: " + str(result[1]))
                print("Branch id: " + str(result[2]))
                print("Birth date: " + str(result[3].strftime('%Y-%m-%d')))
                print("Address: " + result[4])

                cursor.execute("SELECT phone_number FROM administrator_phone_number WHERE administrator_id=%s",
                               admin_id)
                result_phones = cursor.fetchall()
                print("Phone numbers: ", end='')
                if result_phones == ():
                    print()
                for num in result_phones:
                    if num is result_phones[-1]:
                        print(num[0])
                    else:
                        print(num[0] + ", ", end='')
        else:
            print("Please enter one of A, S")

    elif admin_command == 9:  # Branch Registration
        branch_name = input("Enter the branch name you want to register: ")
        if len(branch_name) > 20:
            print("You can enter up to 20 letters of branch name. Please try again.")
            return
        cursor.execute("SELECT branch_name FROM branch WHERE branch_name=%s;", branch_name)
        result = cursor.fetchone()

        if result is not None:
            print("The name of the branch already exists")
            return
        else:
            cursor.execute("INSERT INTO BRANCH(branch_name) values(%s)", branch_name)
            print("Branch Registration Success!")

    elif admin_command == 10:  # Branch Deletion
        branch_name = input("Enter the branch name you want to delete: ")
        cursor.execute("SELECT branch_name FROM branch WHERE branch_name=%s;", branch_name)
        result = cursor.fetchone()
        if result is None:
            print("There's no branch for that name!")
        else:
            cursor.execute("DELETE FROM branch WHERE branch_name=%s;", branch_name)
            print("\"" + branch_name + "\" branch has been deleted")

    elif admin_command == 11:  # Branch Info Change
        branch_name = input("Enter the branch name you want to change: ")
        cursor.execute("SELECT branch_name FROM branch WHERE branch_name=%s;", branch_name)
        result = cursor.fetchone()
        if result is None:
            print("There's no branch for that name!")
        else:
            new_name = input("Enter the new branch name: ")
            if len(new_name) > 20:
                print("You can enter up to 20 letters of branch name. Please try again.")
                return
            cursor.execute("UPDATE branch SET branch_name=%s WHERE branch_name=%s;", (new_name, branch_name))
            print("\"" + branch_name + "\" branch has been changed to \"" + new_name + "\" branch")

    elif admin_command == 12:  # Branch Search
        search_command = input("Which search option do you want?(A:All, S:Specific): ")
        if search_command == "A":
            cursor.execute("SELECT * FROM branch;")
            result_set = cursor.fetchall()
            if result_set == ():
                print("There's no branches")
                return
            for row in result_set:
                print("Branch name: " + row[0])
                print("Branch ID: " + str(row[1]))
                print()
        elif search_command == "S":
            branch_search_command = input("Which search criteria you want?(N:branch_name, I:branch_id):")
            if branch_search_command == "N":
                branch_name = input("Enter the branch name you want to search: ")
                cursor.execute("SELECT * FROM branch WHERE branch_name=%s;", branch_name)
                result = cursor.fetchone()
                if result is None:
                    print("There's no branch for that name!")
                else:
                    print("Branch name: " + result[0])
                    print("Branch ID: " + str(result[1]))

            elif branch_search_command == "I":
                branch_id = int(input("Enter the branch id you want to search: "))
                cursor.execute("SELECT * FROM branch WHERE branch_id=%s;", branch_id)
                result = cursor.fetchone()
                if result is None:
                    print("There's no branch for that id!")
                else:
                    print("Branch name: " + result[0])
                    print("Branch ID: " + str(result[1]))

            else:
                print("Please enter one of N, I")
        else:
            print("Please enter one of A, S")

    else:
        print("Wrong Input! Please try again")

    connection.commit()


def main():
    create_bank_dbms()

    print("Welcome to Bank DBMS")

    while True:
        print()
        print("==============================")
        print("Select Service:")
        print("0.Exit")
        print("1.User")
        print("2.Administrator")
        print("==============================")
        print("Input: ", end='')
        command = int(input())
        if command == 0:
            break
        elif command == 1:
            user_interface()
        elif command == 2:
            admin_interface()
        else:
            print("Wrong Input! Please try again")

    connection.commit()
    connection.close()


if __name__ == '__main__':
    main()
