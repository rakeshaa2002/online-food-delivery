# Pentagon Bites Food Delivery

A Django-based food delivery web application where users can browse food items, add them to a cart, place orders, and pay via Cash on Delivery or Stripe online payment.

---

## Features

- Browse a menu of food items with images and descriptions
- Add items to a shopping cart and update quantities
- View and manage your cart
- Place orders with Cash on Delivery or Online Payment (Stripe)
- View and delete your order history
- Responsive and modern UI

---

## Tech Stack

- **Backend:** Django 4.x
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (default, can be changed)
- **Payments:** Stripe API (test mode)

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd fooddelivery
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```
Or manually:
```sh
pip install django stripe
```

### 3. Stripe Setup

- Register at [Stripe](https://dashboard.stripe.com/register) and get your **test secret key**.
- In `orders/views.py`, set your Stripe secret key:
  ```python
  stripe.api_key = 'sk_test_...'
  ```
- You can find your key in the Stripe dashboard under **Developers > API keys**.

### 4. Database Migration

```sh
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (optional, for admin access)

```sh
python manage.py createsuperuser
```

### 6. Run the Development Server

```sh
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Folder Structure

```
fooddelivery/
├── fooddelivery/         # Django project settings
├── orders/              # Main app: models, views, templates
│   ├── templates/
│   │   ├── home.html
│   │   ├── cart.html
│   │   └── my_orders.html
│   └── static/
│       ├── style.css
│       └── script.js
├── media/               # Uploaded images
├── db.sqlite3           # SQLite database
└── manage.py
```

---

## Payment Integration

- **Cash on Delivery:** Order is placed directly.
- **Online Payment:** Redirects to Stripe Checkout. On success, order is placed.

---

## Customization

- Add or edit food items via Django admin (`/admin/`).
- Change currency or payment settings in `views.py` and Stripe dashboard.

---

## License

MIT License

---

## Credits

- [Django](https://www.djangoproject.com/)
- [Stripe](https://stripe.com/)
- [Boxicons](https://boxicons.com/) for icons

---

**Enjoy your food delivery app!**