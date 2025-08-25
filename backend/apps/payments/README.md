# Stripe Payments Integration

This module provides comprehensive Stripe payment integration for the RecruiterAI backend, focusing on product management and payment processing.

## 🚀 Features

- **Product Management**: Create, read, update, delete Stripe products
- **Secure API**: All endpoints require authentication
- **Comprehensive Documentation**: Full OpenAPI/Swagger documentation
- **Error Handling**: Robust error handling for Stripe API failures
- **Metadata Support**: Custom metadata for products
- **Image Support**: Product image URLs management

## 📁 Structure

```
apps/payments/
├── __init__.py
├── apps.py              # App configuration
├── admin.py             # Django admin (minimal)
├── models.py            # Django models (for future use)
├── serializers.py       # API serializers
├── views.py             # API views
├── urls.py              # URL routing
├── stripe_service.py    # Stripe service layer
└── README.md           # This file
```

## 🔧 Configuration

### 1. Environment Variables

Add these to your `.env` file:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
```

### 2. Stripe Account Setup

1. Create a [Stripe account](https://stripe.com)
2. Get your API keys from the Stripe Dashboard
3. For testing, use test keys (start with `pk_test_` and `sk_test_`)
4. For production, use live keys (start with `pk_live_` and `sk_live_`)

## 🛠 API Endpoints

All endpoints are prefixed with `/api/payments/`

### Product Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products/` | List all products |
| `POST` | `/products/create/` | Create a new product |
| `GET` | `/products/{id}/` | Get product by ID |
| `PUT/PATCH` | `/products/{id}/update/` | Update product |
| `DELETE` | `/products/{id}/delete/` | Delete product |

### Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/config/` | Get Stripe configuration |

## 📝 Usage Examples

### 1. Create a Product

```bash
curl -X POST http://localhost:8000/api/payments/products/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Premium Recruitment Plan",
    "description": "Access to premium features for 1 month",
    "active": true,
    "metadata": {
      "plan_type": "premium",
      "duration": "1_month"
    }
  }'
```

### 2. List Products

```bash
curl -X GET "http://localhost:8000/api/payments/products/?limit=10&active=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Get Product Details

```bash
curl -X GET http://localhost:8000/api/payments/products/prod_ABC123/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Update Product

```bash
curl -X PUT http://localhost:8000/api/payments/products/prod_ABC123/update/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Premium Plan",
    "description": "Updated description",
    "active": false
  }'
```

### 5. Delete Product

```bash
curl -X DELETE http://localhost:8000/api/payments/products/prod_ABC123/delete/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔒 Authentication

All endpoints require authentication using Bearer tokens:

```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Use the authentication endpoints to get access tokens:
- Register: `POST /api/authentication/register/`
- Login: `POST /api/authentication/login/`

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "message": "Product created successfully",
  "product": {
    "id": "prod_ABC123",
    "name": "Premium Plan",
    "description": "Access to premium features",
    "active": true,
    "created": 1640995200,
    "updated": 1640995200,
    "metadata": {},
    "images": [],
    "url": null
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Failed to create product in Stripe",
  "error": "Invalid request: name is required"
}
```

## 🧪 Testing

### 1. Using Test Cards

For testing, use Stripe's test card numbers:
- **Success**: `4242424242424242`
- **Decline**: `4000000000000002`
- **Insufficient funds**: `4000000000009995`

### 2. API Testing

Test the endpoints using:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **Postman**: Import the OpenAPI schema
- **curl**: Use the examples above

## 🔍 Monitoring

### Stripe Dashboard
Monitor your payments and products in the [Stripe Dashboard](https://dashboard.stripe.com):
- View all products and their status
- Monitor payment activity
- Access detailed logs and analytics

### Application Logs
Check Django logs for Stripe integration issues:
```bash
# View logs
docker compose logs web

# Follow logs
docker compose logs -f web
```

## 🛡 Security Best Practices

1. **Never expose secret keys**: Keep `STRIPE_SECRET_KEY` secure
2. **Use HTTPS in production**: Stripe requires HTTPS for webhooks
3. **Validate webhooks**: Implement webhook signature verification
4. **Rate limiting**: Implement rate limiting for API endpoints
5. **Input validation**: All inputs are validated using serializers

## 🚀 Deployment

### Development
```bash
# Start with Docker
docker compose -f docker-compose.simple.yml up

# Or run locally
python manage.py runserver
```

### Production
1. Set production Stripe keys
2. Enable HTTPS
3. Configure webhooks
4. Set up monitoring
5. Implement rate limiting

## 📚 Advanced Features (Future)

- **Subscriptions**: Recurring payment management
- **Webhooks**: Real-time payment notifications
- **Invoices**: Automated invoice generation
- **Customers**: Customer management integration
- **Payment Methods**: Saved payment methods
- **Analytics**: Payment analytics and reporting

## 🤝 Support

For Stripe-specific issues:
- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Support](https://support.stripe.com)

For integration issues:
- Check the application logs
- Review the Stripe Dashboard
- Test with Stripe's test environment
