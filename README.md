# Django E-commerce Platform

A production-grade Django 5 e-commerce platform for clothing, built with modern best practices and prepared for Kubernetes, Helm, and ArgoCD deployment.

## Features

### Core Functionality
- **User Management**: Custom User model with email-based authentication and role-based access control (Admin, Staff, Customer)
- **Product Catalog**: Category management, product listings with variants (size, color), inventory tracking
- **Shopping Cart**: Session-based and user-based carts with automatic merging
- **Order Management**: Full order lifecycle (Pending → Paid → Processing → Shipped → Delivered → Cancelled)
- **Payment Processing**: Stripe integration ready with webhook support
- **Address Management**: Multiple shipping/billing addresses per user

### Technical Features
- **Modular Monolith**: Cleanly separated Django apps
- **Domain-Driven Design**: Clear separation of concerns
- **12-Factor App**: Environment-driven configuration
- **Production-Ready**: Security headers, CSRF protection, secure cookies
- **DevOps Ready**: Health check endpoint, stateless design
- **Future-Proof**: Redis and Celery placeholders for caching and async tasks

## Architecture

```
django_ecommerce/
├── apps/
│   ├── accounts/          # Custom User, Profile, Address models
│   ├── products/          # Category, Product, ProductVariant, ProductImage
│   ├── orders/            # Cart, CartItem, Order, OrderItem
│   ├── payments/          # Payment, PaymentLog, Refund
│   └── core/              # Base models, health check, home view
├── config/
│   └── settings/
│       ├── base.py        # Shared settings
│       ├── dev.py         # Development settings
│       └── prod.py        # Production settings
├── templates/             # Django templates
├── static/                # CSS, JS, images
├── requirements/          # Dependency management
└── scripts/               # Utility scripts
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django_ecommerce
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Create database**
   ```bash
   createdb django_ecommerce
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit http://localhost:8000 to see the application.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | False |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | localhost |
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `REDIS_URL` | Redis connection URL | Optional |
| `STRIPE_PUBLIC_KEY` | Stripe public key | Optional |
| `STRIPE_SECRET_KEY` | Stripe secret key | Optional |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | Optional |

See `.env.example` for complete list.

### Production Deployment

1. **Set environment to production**
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.prod
   ```

2. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn -c scripts/gunicorn.conf.py config.wsgi:application
   ```

## Database Schema

### Accounts App
- **User**: Custom user model with email authentication
- **UserProfile**: Extended user information
- **Address**: Shipping/billing addresses

### Products App
- **Category**: Product categories with hierarchy
- **Product**: Main product model with inventory tracking
- **ProductImage**: Product images with primary designation
- **ProductVariant**: Size/color variants

### Orders App
- **Cart**: Shopping cart (session/user-based)
- **CartItem**: Items in cart
- **Order**: Order with full lifecycle
- **OrderItem**: Items in order (snapshot data)

### Payments App
- **Payment**: Payment transactions
- **PaymentLog**: Audit trail
- **Refund**: Refund records

## API Endpoints

### Core
- `GET /` - Home page
- `GET /health/` - Health check endpoint

### Accounts
- `GET /accounts/login/` - Login
- `GET /accounts/register/` - Register
- `GET /accounts/profile/` - User profile
- `GET /accounts/addresses/` - Address management

### Products
- `GET /products/` - Product listing
- `GET /products/<slug>/` - Product detail
- `GET /products/category/<slug>/` - Category detail
- `GET /products/search/?q=<query>` - Product search

### Orders
- `GET /orders/cart/` - Shopping cart
- `POST /orders/cart/add/<slug>/` - Add to cart
- `GET /orders/checkout/` - Checkout
- `GET /orders/order/<order_number>/` - Order detail

### Payments
- `GET /payments/process/<order_number>/` - Payment page
- `POST /payments/webhook/stripe/` - Stripe webhook

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts
python manage.py test apps.products
python manage.py test apps.orders

# Run with coverage
coverage run manage.py test
coverage report
```

## Security Considerations

- **CSRF Protection**: Enabled on all forms
- **Secure Cookies**: HttpOnly, Secure, SameSite in production
- **Password Validation**: Minimum 10 characters, complexity requirements
- **XSS Protection**: Django's auto-escaping in templates
- **SQL Injection**: Protected by Django ORM
- **Clickjacking**: X-Frame-Options header
- **Content Security Policy**: Ready for django-csp integration

## Future Enhancements

- [ ] REST API with Django REST Framework
- [ ] GraphQL API with Graphene
- [ ] Real-time notifications with WebSockets
- [ ] Advanced search with Elasticsearch
- [ ] Multi-currency support
- [ ] Multi-language support (i18n)
- [ ] Product reviews and ratings
- [ ] Wishlist functionality
- [ ] Coupon/promo code system
- [ ] Advanced analytics dashboard

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Support

For support, email support@djangoshop.com or open an issue on GitHub.
