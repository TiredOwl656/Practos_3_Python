
import json
from datetime import datetime
import os


class User:

    def __init__(self, username, password, role):
        self._username = username
        self._password = password
        self._role = role
        self._cart = []
        self._history = []

    def get_username(self):
        return self._username

    def get_role(self):
        return self._role

    def get_password(self):
        return self._password

    def get_cart(self):
        return self._cart

    def get_history(self):
        return self._history

    def set_password(self, new_password):
        self._password = new_password

    def add_to_cart(self, product):
        self._cart.append(product)

    def clear_cart(self):
        self._cart = []

    def add_to_history(self, products):
        self._history.extend(products)

    def view_cart(self, sort_criteria=None):
        if not self._cart:
            print("Корзина пуста.")
            return

        if sort_criteria:
            sorted_cart = self.sort_cart(sort_criteria)
        else:
            sorted_cart = self._cart

        total_cost = sum(product.get_price() for product in self._cart)

        print("-" * 30)
        print("{:<20} {:<10}".format("Название", "Цена"))
        print("-" * 30)
        for product in sorted_cart:
            print("{:<20} {:<10.2f}".format(product.get_name(), product.get_price()))
        print("-" * 30)
        print(f"Итоговая стоимость: {total_cost:.2f}")

    def sort_cart(self, sort_criteria):
        if sort_criteria == "price":
            return sorted(self._cart, key=lambda x: x.get_price())
        elif sort_criteria == "price_desc":
            return sorted(self._cart, key=lambda x: x.get_price(), reverse=True)
        elif sort_criteria == "name":
            return sorted(self._cart, key=lambda x: x.get_name().lower())
        elif sort_criteria == "name_desc":
            return sorted(self._cart, key=lambda x: x.get_name().lower(), reverse=True)
        else:
            return self._cart

    def view_purchase_history(self):
        if not self._history:
            print("История покупок пуста.")
            return

        print("\nИстория покупок:")
        for i, purchase in enumerate(self._history):
            print(f"--- Покупка {i + 1} ---")
            print(f"Название: {purchase.get_name()}")
            print(f"Цена: {purchase.get_price():.2f}")
            print(f"Дата покупки: {purchase.get_purchase_date()}")
            print("-" * 20)

    def __str__(self):
        return f"User(username='{self._username}', role='{self._role}')"

    def to_dict(self):
        return {
            "username": self._username,
            "password": self._password,
            "role": self._role,
            "cart": [p.to_dict() for p in self._cart],
            "history": [p.to_dict() for p in self._history],
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data['username'], data['password'], data['role'])
        return user


class Admin(User):

    def __init__(self, username, password):
        super().__init__(username, password, role="admin")

    def manage_users(self, user_manager):
        user_manager.manage_users()

    def manage_products(self, product_manager):
        product_manager.manage_products()

    def view_statistics(self, user_manager):
        user_manager.show_statistics()

    def __str__(self):
        return f"Admin(username='{self._username}')"

    @classmethod
    def from_dict(cls, data):
        admin = cls(data['username'], data['password'])
        admin._cart = [Product.from_dict(p) for p in data['cart']]
        admin._history = [Product.from_dict(p) for p in data['history']]
        return admin


class Customer(User):

    def __init__(self, username, password):
        super().__init__(username, password, role="user")

    def browse_products(self, product_manager):
        product_manager.show_products()

    def add_to_cart(self, product, product_manager):
        if product.get_quantity() > 0:
            super().add_to_cart(product)
            product.decrease_quantity(1)
            print("Товар добавлен в корзину!")
        else:
            print("Товар отсутствует на складе.")

    def checkout(self):
        self.view_cart()
        if input("Подтвердить покупку? (y/n): ").lower() == "y":
            for product in self.get_cart():
                product.set_purchase_date(datetime.now().isoformat())
            self.add_to_history(self.get_cart())
            self.clear_cart()
            print("Покупка завершена!")
        else:
            print("Покупка отменена.")

    def __str__(self):
        return f"Customer(username='{self._username}')"

    @classmethod
    def from_dict(cls, data):
        customer = cls(data['username'], data['password'])
        customer._cart = [Product.from_dict(p) for p in data['cart']]
        customer._history = [Product.from_dict(p) for p in data['history']]
        return customer


class Product:

    def __init__(self, name, price, quantity, purchase_date=None):
        self._name = name
        self._price = price
        self._quantity = quantity
        self._purchase_date = purchase_date

    def get_name(self):
        return self._name

    def set_name(self, new_name):
        self._name = new_name

    def get_price(self):
        return self._price

    def set_price(self, new_price):
        if new_price > 0:
            self._price = new_price
        else:
            print("Цена должна быть больше 0.")

    def get_quantity(self):
        return self._quantity

    def set_quantity(self, new_quantity):
        if new_quantity >= 0:
            self._quantity = new_quantity
        else:
            print("Количество не может быть отрицательным.")

    def decrease_quantity(self, amount):
        if amount > 0 and self._quantity >= amount:
            self._quantity -= amount
        else:
            print("Недостаточно товара на складе.")

    def get_purchase_date(self):
        return self._purchase_date

    def set_purchase_date(self, date):
        self._purchase_date = date

    def __str__(self):
        return f"Product(name='{self._name}', price={self._price}, quantity={self._quantity}, purchase_date={self._purchase_date})"

    def to_dict(self):
        return {
            "name": self._name,
            "price": self._price,
            "quantity": self._quantity,
            "purchase_date": self._purchase_date,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['name'], data['price'], data['quantity'], data.get('purchase_date'))


class ProductManager:

    def __init__(self, products_data=None, data_file="products.json"):
        self._products = []
        self._data_file = data_file
        self.load_data()

    def add_product(self, name, price, quantity):
        product = Product(name, price, quantity)
        self._products.append(product)
        self.save_data()
        print("Товар добавлен!")

    def delete_product(self, name):
        self._products[:] = [p for p in self._products if p.get_name() != name]
        self.save_data()
        print(f"Товар '{name}' удален.")

    def edit_product(self, index, new_name, new_price, new_quantity):
        if 0 <= index < len(self._products):
            product = self._products[index]
            if new_name:
                product.set_name(new_name)
            if new_price:
                try:
                    new_price = float(new_price)
                    product.set_price(new_price)
                except ValueError:
                    print("Неверный формат цены.")
            if new_quantity:
                try:
                    new_quantity = int(new_quantity)
                    product.set_quantity(new_quantity)
                except ValueError:
                    print("Неверный формат количества.")
            self.save_data()
            print("Товар успешно отредактирован.")
        else:
            print("Неверный номер товара.")

    def show_products(self, sorted_products=None):
        if not self._products:
            print("Товаров нет в наличии.")
            return

        products_to_display = sorted_products if sorted_products is not None else self._products

        print("-" * 30)
        print("{:<20} {:<10} {:<10}".format("Название", "Цена", "Количество"))
        print("-" * 30)
        for i, product in enumerate(products_to_display):
            print(f"{i + 1}. {product.get_name():<20} {product.get_price():<10.2f} {product.get_quantity():<10}")
        print("-" * 30)

    def sort_products(self, sort_criteria):
        if sort_criteria == "price":
            return sorted(self._products, key=lambda x: x.get_price())
        elif sort_criteria == "price_desc":
            return sorted(self._products, key=lambda x: x.get_price(), reverse=True)
        elif sort_criteria == "quantity":
            return sorted(self._products, key=lambda x: x.get_quantity())
        elif sort_criteria == "quantity_desc":
            return sorted(self._products, key=lambda x: x.get_quantity(), reverse=True)
        elif sort_criteria == "name":
            return sorted(self._products, key=lambda x: x.get_name().lower())
        elif sort_criteria == "name_desc":
            return sorted(self._products, key=lambda x: x.get_name().lower(), reverse=True)
        else:
            return self._products

    def manage_products(self):
        while True:
            print("\nРедактирование данных:")
            print("1. Добавить товар")
            print("2. Удалить товар")
            print("3. Изменить информацию о товаре")
            print("4. Назад")
            choice = input("Выберите действие: ")
            try:
                if choice == "1":
                    name = input("Введите название товара: ")
                    while True:
                        try:
                            price = float(input("Введите цену: "))
                            if price <= 0:
                                raise ValueError("Цена должна быть больше нуля.")
                            break
                        except ValueError as e:
                            print(f"Ошибка: {e}. Пожалуйста, введите число больше 0.")
                    while True:
                        try:
                            quantity = int(input("Введите количество: "))
                            if quantity < 0:
                                raise ValueError("Количество не может быть отрицательным.")
                            break
                        except ValueError as e:
                            print(f"Ошибка: {e}. Пожалуйста, введите целое число больше или равное 0.")
                    self.add_product(name, price, quantity)

                elif choice == "2":
                    name = input("Введите название товара для удаления: ")
                    self.delete_product(name)
                elif choice == "3":
                    self.show_products()
                    try:
                        product_index = int(input("Введите номер товара для редактирования: ")) - 1
                        if 0 <= product_index < len(self._products):
                            product = self._products[product_index]
                            new_name = input(f"Новое название товара ({product.get_name()}): ") or None
                            new_price = input(f"Новая цена товара ({product.get_price()}): ") or None
                            new_quantity = input(f"Новое количество товара ({product.get_quantity()}): ") or None
                            self.edit_product(product_index, new_name, new_price, new_quantity)

                        else:
                            print("Неверный номер товара.")
                    except (ValueError, IndexError) as e:
                        print(f"Ошибка при редактировании товара: {e}")
                elif choice == "4":
                    break
                else:
                    print("Неверный выбор.")
            except Exception as e:
                print(f"Ошибка в меню управления товарами: {e}")

    def get_products(self):
        return self._products

    def load_data(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), self._data_file)

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._products = [Product.from_dict(p) for p in data] 
            print("Данные о товарах загружены.")
        except FileNotFoundError:
            print("Файл с данными о товарах не найден. Создан новый.")
            self._products = []
            self.save_data()
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON. Файл поврежден или пуст.")
            self._products = []
            self.save_data()
        except Exception as e:
            print(f"Произошла ошибка при загрузке данных о товарах: {e}")

    def save_data(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), self._data_file)

            data = [p.to_dict() for p in self._products]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Данные о товарах сохранены.")
        except Exception as e:
            print(f"Произошла ошибка при сохранении данных о товарах: {e}")


class UserManager:

    def __init__(self, data_file="users.json"):
        self._users = {}
        self._data_file = data_file
        self.load_data()

    def register_user(self, username, password, role):
        if username in self._users:
            print("Пользователь с таким именем уже существует. Выберите другое имя.")
            return

        if role == "admin":
            user = Admin(username, password)
        elif role == "user":
            user = Customer(username, password)
        else:
            print("Неверная роль.")
            return

        self._users[username] = user
        self.save_data()
        print("Регистрация прошла успешно!")

    def login(self, username, password):
        user = self._users.get(username)
        if user and user.get_password() == password:
            return user
        else:
            print("Неверный логин или пароль. Пожалуйста, проверьте введенные данные.")
            return None

    def delete_user(self, username):
        if username in self._users:
            del self._users[username]
            self.save_data()
            print(f"Пользователь {username} удален.")
        else:
            print("Пользователь не найден.")

    def change_user_role(self, username, new_role):
        user = self._users.get(username)
        if user:
            if new_role in ["user", "admin"]:
                if new_role == "admin":
                    new_user = Admin(user.get_username(), user.get_password())
                else:
                    new_user = Customer(user.get_username(), user.get_password())

                new_user._cart = user.get_cart()
                new_user._history = user.get_history()

                self._users[username] = new_user
                self.save_data()
                print(f"Роль пользователя {username} изменена на {new_role}.")
            else:
                print("Неверная роль. Введите 'user' или 'admin'.")
        else:
            print("Пользователь не найден.")

    def change_user_password(self, username, new_password):
        user = self._users.get(username)
        if user:
            user.set_password(new_password)
            self.save_data()
            print(f"Пароль пользователя {username} успешно изменен.")
        else:
            print("Пользователь не найден.")

    def list_users(self):
        if not self._users:
            print("Нет зарегистрированных пользователей.")
            return

        print("\nСписок пользователей:")
        for i, (username, user) in enumerate(self._users.items()):
            print(f"{i + 1}. Имя пользователя: {username}, Роль: {user.get_role()}")

    def manage_users(self):
        while True:
            self.list_users()

            print("\nВыберите действие: ")
            print("1 - добавить пользователя")
            print("2 - изменить роль пользователя")
            print("3 - изменить пароль пользователя")
            print("4 - удалить пользователя")
            print("5 - назад")
            action = input()
            try:
                if action == '1':
                    username = input("Введите имя пользователя: ")
                    while True:
                        password = input("Введите пароль: ")
                        confirm_password = input("Повторите пароль: ")
                        if password == confirm_password:
                            break
                        else:
                            print("Пароли не совпадают. Пожалуйста, повторите ввод.")
                    while True:
                        role = input("Роль (user/admin): ").lower()
                        if role in ["user", "admin"]:
                            break
                        else:
                            print("Неверная роль. Введите 'user' или 'admin'.")
                    self.register_user(username, password, role)
                elif action == '2':
                    username = input("Введите имя пользователя для изменения роли: ")
                    new_role = input("Введите новую роль (user/admin): ").lower()
                    self.change_user_role(username, new_role)
                elif action == '3':
                    username = input("Введите имя пользователя для изменения пароля: ")
                    while True:
                        new_password = input(f"Введите новый пароль для пользователя {username}: ")
                        confirm_password = input(f"Повторите новый пароль для пользователя {username}: ")
                        if new_password == confirm_password:
                            break
                        else:
                            print("Пароли не совпадают. Пожалуйста, повторите ввод.")
                    self.change_user_password(username, new_password)
                elif action == '4':
                    username = input("Введите имя пользователя для удаления: ")
                    self.delete_user(username)
                elif action == '5':
                    break
                else:
                    print("Неверный выбор.")
            except Exception as e:
                print(f"Произошла ошибка: {e}")

    def show_statistics(self):
        total_purchases = 0
        total_revenue = 0
        for username, user in self._users.items():
            for purchase in user.get_history():
                total_purchases += 1
                total_revenue += purchase.get_price()

        if total_purchases > 0:
            average_purchase_value = total_revenue / total_purchases
            print(f"\nСтатистика:")
            print(f"Общее количество покупок: {total_purchases}")
            print(f"Общая выручка: {total_revenue:.2f}")
            print(f"Средняя стоимость покупки: {average_purchase_value:.2f}")
        else:
            print("\nСтатистика пока недоступна (нет покупок).")

    def get_users(self):
        return self._users  

    def load_data(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), self._data_file)

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for username, user_data in data.items():
                    role = user_data['role']
                    if role == 'admin':
                        self._users[username] = Admin.from_dict(user_data)
                    else:
                        self._users[username] = Customer.from_dict(user_data)
            print("Данные о пользователях загружены.")
        except FileNotFoundError:
            print("Файл с данными о пользователях не найден. Создан новый.")
            self._users = {}
            self.save_data() 
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON. Файл поврежден или пуст.")
            self._users = {} 
            self.save_data() 
        except Exception as e:
            print(f"Произошла ошибка при загрузке данных о пользователях: {e}")

    def save_data(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), self._data_file)

            data = {username: user.to_dict() for username, user in self._users.items()}
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Данные о пользователях сохранены.")
        except Exception as e:
            print(f"Произошла ошибка при сохранении данных о пользователях: {e}")


# --- Main ---

def main():
    user_manager = UserManager()
    product_manager = ProductManager()

    while True:
        print("\nМеню:")
        print("1. Регистрация")
        print("2. Вход")
        print("3. Выход")

        choice = input("Выберите действие: ")
        try:
            if choice == "1":
                username = input("Введите имя пользователя: ")
                while True:
                    password = input("Введите пароль: ")
                    confirm_password = input("Повторите пароль: ")
                    if password == confirm_password:
                        break
                    else:
                        print("Пароли не совпадают. Пожалуйста, повторите ввод.")
                while True:
                    role = input("Роль (user/admin): ").lower()
                    if role in ["user", "admin"]:
                        break
                    else:
                        print("Неверная роль. Введите 'user' или 'admin'.")
                user_manager.register_user(username, password, role)
            elif choice == "2":
                username = input("Введите имя пользователя: ")
                password = input("Введите пароль: ")
                user = user_manager.login(username, password)
                if user:
                    if isinstance(user, Admin):
                        admin_menu(user, user_manager, product_manager)
                    elif isinstance(user, Customer):
                        user_menu(user, product_manager)
            elif choice == "3":
                break
            else:
                print("Неверный выбор.")
        except Exception as e:
            print(f"Произошла неожиданная ошибка: {e}")


def admin_menu(admin, user_manager, product_manager):
    while True:
        print("\nМеню администратора:")
        print("1. Просмотреть товары")
        print("2. Управление пользователями")
        print("3. Управление товаром")
        print("4. Просмотр статистики")
        print("5. Выйти")

        choice = input("Выберите действие: ")
        try:
            if choice == "1":
                product_manager.show_products()
            elif choice == "2":
                admin.manage_users(user_manager)
            elif choice == "3":
                admin.manage_products(product_manager)
            elif choice == "4":
                admin.view_statistics(user_manager)
            elif choice == "5":
                break
            else:
                print("Неверный выбор.")
        except Exception as e:
            print(f"Произошла ошибка в меню администратора: {e}")


def user_menu(customer, product_manager):
    while True:
        print("\nМеню пользователя:")
        print("1. Просмотреть товары")
        print("2. Добавить в корзину")
        print("3. Просмотреть корзину")
        print("4. Оформить заказ")
        print("5. История покупок")
        print("6. Выйти")

        choice = input("Выберите действие: ")
        try:
            if choice == "1":
                while True:
                    print("\nСортировка товаров:")
                    print("1. Сортировать по цене (по возрастанию)")
                    print("2. Сортировать по цене (по убыванию)")
                    print("3. Сортировать по количеству (по возрастанию)")
                    print("4. Сортировать по количеству (по убыванию)")
                    print("5. Сортировать по названию (A-Я)")
                    print("6. Сортировать по названию (Я-А)")
                    print("7. Не сортировать")
                    sort_choice = input("Выберите способ сортировки: ")
                    if sort_choice in ["1", "2", "3", "4", "5", "6", "7"]:
                        break
                    else:
                        print("Неверный выбор. Пожалуйста, выберите число от 1 до 7.")

                sorted_products = None
                if sort_choice == "1":
                    sorted_products = product_manager.sort_products("price")
                elif sort_choice == "2":
                    sorted_products = product_manager.sort_products("price_desc")
                elif sort_choice == "3":
                    sorted_products = product_manager.sort_products("quantity")
                elif sort_choice == "4":
                    sorted_products = product_manager.sort_products("quantity_desc")
                elif sort_choice == "5":
                    sorted_products = product_manager.sort_products("name")
                elif sort_choice == "6":
                    sorted_products = product_manager.sort_products("name_desc")
                else:
                    sorted_products = product_manager.get_products()

                product_manager.show_products(sorted_products)

            elif choice == "2":
                product_manager.show_products()
                try:
                    product_index = int(input("Введите номер товара: ")) - 1
                    products = product_manager.get_products()
                    if 0 <= product_index < len(products):
                        product = products[product_index]
                        customer.add_to_cart(product, product_manager)
                    else:
                        print("Неверный номер товара.")
                except (ValueError, IndexError) as e:
                    print(f"Ошибка: {e}. Пожалуйста, проверьте введенный номер товара.")

            elif choice == "3":
                while True:
                    print("\nСортировка корзины:")
                    print("1. Сортировать по цене (по возрастанию)")
                    print("2. Сортировать по цене (по убыванию)")
                    print("3. Сортировать по названию (A-Я)")
                    print("4. Сортировать по названию (Я-А)")
                    print("5. Не сортировать")
                    sort_choice = input("Выберите способ сортировки: ")
                    if sort_choice in ["1", "2", "3", "4", "5"]:
                        break
                    else:
                        print("Неверный выбор. Пожалуйста, выберите число от 1 до 5.")

                if sort_choice == "1":
                    customer.view_cart("price")
                elif sort_choice == "2":
                    customer.view_cart("price_desc")
                elif sort_choice == "3":
                    customer.view_cart("name")
                elif sort_choice == "4":
                    customer.view_cart("name_desc")
                else:
                    customer.view_cart()
            elif choice == "4":
                customer.checkout()
            elif choice == "5":
                customer.view_purchase_history()
            elif choice == "6":
                break
            else:
                print("Неверный выбор.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
