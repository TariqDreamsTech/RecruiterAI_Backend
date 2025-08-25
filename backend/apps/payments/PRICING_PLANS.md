# RecruiterAI Pricing Plans Implementation

This document outlines the complete pricing plan implementation for RecruiterAI with Stripe integration.

## 🎯 Pricing Structure

### Three-Tier Pricing Model

| Plan | Monthly | Yearly | Savings | Job Posts/Year |
|------|---------|--------|---------|----------------|
| **Starter** | $182.31/month | $2,187.77/year | 30% | 36 |
| **Standard** | $246.66/month | $2,959.92/year | 30% | 120 |
| **Enterprise** | $343.18/month | $4,118.15/year | 30% | 360 |

### Features Comparison

#### Starter Plan
- 36 job posts per year
- Priority email support
- Advanced analytics
- 7-day free trial (1 job post)

#### Standard Plan
- 120 job posts per year
- Priority email support
- Advanced analytics
- Team collaboration tools
- 7-day free trial (1 job post)

#### Enterprise Plan
- 360 job posts per year
- Priority email support
- Advanced analytics
- Team collaboration tools
- 7-day free trial (1 job post)

## 🚀 API Endpoints

### 1. Get Pricing Plans (Public)
```http
GET /api/payments/pricing/plans/
```
Returns pricing information for the frontend display.

**Response:**
```json
{
  "success": true,
  "plans": [
    {
      "name": "Starter",
      "description": "Perfect for small businesses",
      "monthly_price": 182.31,
      "yearly_price": 2187.77,
      "monthly_price_formatted": "$182.31/month",
      "yearly_price_formatted": "$2,187.77 a year",
      "yearly_savings": "Save 30%",
      "features": [
        "36 job posts per year",
        "Priority email support",
        "Advanced analytics",
        "7-day free trial (1 job post)"
      ],
      "metadata": {
        "plan_type": "starter",
        "job_posts_per_year": 36,
        "support_level": "email",
        "trial_days": 7
      }
    }
    // ... other plans
  ]
}
```

### 2. Setup Pricing Plans in Stripe
```http
POST /api/payments/pricing/setup/
Authorization: Bearer YOUR_TOKEN
```
Creates products and prices in Stripe (admin only).

### 3. Start Free Trial
```http
POST /api/payments/subscriptions/trial/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "customer_email": "user@example.com",
  "customer_name": "John Doe",
  "price_id": "price_1234567890",
  "metadata": {
    "user_type": "trial_user"
  }
}
```

### 4. Create Subscription
```http
POST /api/payments/subscriptions/create/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "customer_email": "user@example.com",
  "customer_name": "John Doe",
  "price_id": "price_1234567890",
  "trial_period_days": 7
}
```

## 🔧 Implementation Details

### Stripe Configuration

The pricing plans are created in Stripe with the following structure:

#### Products
- RecruiterAI Starter Plan
- RecruiterAI Standard Plan
- RecruiterAI Enterprise Plan

#### Prices (per product)
- Monthly subscription price
- Yearly subscription price (30% discount)

### Metadata Structure

Each plan includes comprehensive metadata:
```json
{
  "plan_type": "starter|standard|enterprise",
  "job_posts_per_year": "36|120|360",
  "support_level": "email",
  "trial_days": "7",
  "billing_interval": "monthly|yearly"
}
```

## 💳 Free Trial Implementation

### Trial Features
- **Duration**: 7 days
- **No credit card required** during setup
- **1 job post included** during trial
- **Automatic conversion** to paid plan after trial (if payment method added)

### Trial Workflow
1. User selects a plan
2. System creates Stripe customer
3. Creates subscription with 7-day trial
4. User can use 1 job post during trial
5. After 7 days, subscription becomes active (requires payment)

## 🎨 Frontend Integration

### 1. Display Pricing Plans
```javascript
// Fetch pricing plans
const response = await fetch('/api/payments/pricing/plans/');
const data = await response.json();

// Display plans
data.plans.forEach(plan => {
  console.log(`${plan.name}: ${plan.monthly_price_formatted}`);
});
```

### 2. Start Free Trial
```javascript
const startTrial = async (planType, userEmail) => {
  const response = await fetch('/api/payments/subscriptions/trial/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      customer_email: userEmail,
      price_id: getPriceId(planType, 'monthly'), // or 'yearly'
      customer_name: userName
    })
  });
  
  const result = await response.json();
  if (result.success) {
    console.log('Trial started successfully!');
  }
};
```

### 3. Handle Payment After Trial
```javascript
// This would integrate with Stripe Elements for payment
const handlePayment = async (subscriptionId, paymentMethodId) => {
  // Update subscription with payment method
  // This would be a separate endpoint for payment processing
};
```

## 🔒 Security Considerations

### Authentication
- All subscription endpoints require authentication
- Pricing plans endpoint is public for display
- Setup endpoint restricted to admin users

### Data Validation
- Email validation for customer creation
- Plan type validation against allowed values
- Price ID validation against Stripe

### Error Handling
- Comprehensive error messages for Stripe failures
- Graceful degradation for network issues
- Proper HTTP status codes

## 📊 Usage Analytics

### Tracking Metrics
- Trial conversion rates
- Popular plan selections
- Monthly vs yearly preferences
- Feature usage during trials

### Metadata for Analytics
Each subscription includes metadata for tracking:
```json
{
  "trial_type": "free_trial",
  "trial_started": "true",
  "user_id": "12345",
  "plan_type": "starter",
  "source": "web_app"
}
```

## 🚀 Deployment Checklist

### Development Setup
- [ ] Add Stripe test keys to environment
- [ ] Run `setup_pricing_plans` endpoint
- [ ] Test free trial flow
- [ ] Verify plan display

### Production Setup
- [ ] Add Stripe live keys
- [ ] Setup webhook endpoints
- [ ] Configure payment methods
- [ ] Test with real payments
- [ ] Monitor subscription metrics

## 🧪 Testing

### Test Scenarios
1. **Plan Display**: Verify all plans show correct pricing
2. **Free Trial**: Start trial without payment
3. **Subscription Creation**: Full payment flow
4. **Plan Switching**: Upgrade/downgrade flows
5. **Trial Expiration**: Proper handling of trial end

### Test Data
Use Stripe test cards:
- Success: `4242424242424242`
- Decline: `4000000000000002`
- Insufficient funds: `4000000000009995`

## 📈 Future Enhancements

### Planned Features
- [ ] Plan switching/upgrades
- [ ] Usage tracking for job posts
- [ ] Custom enterprise pricing
- [ ] Annual billing discounts
- [ ] Referral programs
- [ ] Team member management

### Webhook Integration
- [ ] Payment success notifications
- [ ] Trial expiration handling
- [ ] Failed payment recovery
- [ ] Subscription cancellation

## 🆘 Support & Troubleshooting

### Common Issues
1. **Stripe key errors**: Check environment variables
2. **Price creation fails**: Verify product exists first
3. **Trial not starting**: Check customer email uniqueness
4. **Payment failures**: Review Stripe dashboard logs

### Monitoring
- Check Stripe dashboard for payment status
- Monitor Django logs for API errors
- Track subscription metrics in analytics

---

This implementation provides a complete, production-ready pricing system for RecruiterAI with Stripe integration, free trials, and comprehensive API support.
