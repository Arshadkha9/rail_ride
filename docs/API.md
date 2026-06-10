# RailRide API Documentation

Full interactive documentation is available at **http://localhost:8000/docs** (Swagger UI) when the backend is running.

Base URL: `https://api.railride.com/api/v1` (production) or `http://localhost:8000/api/v1` (local)

---

## Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

### Register
```
POST /auth/register
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "mobile": "+919876543210",
  "password": "SecurePass123"
}
```

### Email Login
```
POST /auth/login/email
{ "email": "john@example.com", "password": "SecurePass123" }
```

### Mobile OTP Login
```
POST /auth/login/mobile        → sends OTP
POST /auth/otp/verify          → returns tokens
```

### Refresh Token
```
POST /auth/refresh
{ "refresh_token": "<token>" }
```

### Profile
```
GET  /auth/profile
PUT  /auth/profile
POST /auth/change-password
```

---

## Railway Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/railway/trains/search` | Search trains by route/name/number |
| GET | `/railway/trains/{number}` | Train details |
| GET | `/railway/pnr/{pnr}` | PNR status check |
| GET | `/railway/trains/{number}/live` | Live train status |
| GET | `/railway/trains/{number}/schedule` | Station-wise schedule |
| GET | `/railway/stations/search` | Search stations |
| GET | `/railway/stations/nearby` | Nearby stations by lat/lng |
| GET | `/railway/favorites` | User's favorite trains |
| POST | `/railway/favorites` | Add favorite train |
| DELETE | `/railway/favorites/{id}` | Remove favorite |

### Example: Train Search
```json
POST /railway/trains/search
{
  "source": "NDLS",
  "destination": "BCT",
  "date": "2026-06-15"
}
```

### Example: PNR Status
```
GET /railway/pnr/1234567890
```

---

## Ride Booking Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rides/estimate` | Fare estimate |
| POST | `/rides/book` | Book a ride |
| GET | `/rides/{id}` | Ride details |
| GET | `/rides/{id}/track` | Current tracking info |
| POST | `/rides/{id}/cancel` | Cancel ride |
| POST | `/rides/{id}/rate` | Rate completed ride |
| GET | `/rides/active` | User's active ride |

### Book Ride
```json
POST /rides/book
{
  "ride_type": "taxi",
  "pickup_latitude": 28.6139,
  "pickup_longitude": 77.2090,
  "pickup_address": "Connaught Place, New Delhi",
  "dropoff_latitude": 28.5562,
  "dropoff_longitude": 77.1000,
  "dropoff_address": "IGI Airport, New Delhi"
}
```

---

## WebSocket — Live Tracking

```
ws://localhost:8000/ws/tracking/{ride_id}?token=<access_token>
```

**Server → Client messages:**
```json
{
  "type": "location_update",
  "ride_id": 42,
  "driver_lat": 28.6150,
  "driver_lng": 77.2100,
  "eta_minutes": 5,
  "status": "in_progress"
}
```

**Driver → Server:**
```json
{
  "type": "location",
  "latitude": 28.6150,
  "longitude": 77.2100
}
```

---

## Wallet & Payments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/wallet/balance` | Current balance |
| POST | `/wallet/add-money` | Top up wallet |
| GET | `/wallet/transactions` | Transaction history |
| POST | `/wallet/upi/initiate` | Start UPI payment |
| POST | `/wallet/upi/confirm` | Confirm UPI payment |

---

## Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications` | List notifications |
| GET | `/notifications/unread-count` | Unread count |
| PATCH | `/notifications/{id}/read` | Mark as read |
| PATCH | `/notifications/read-all` | Mark all read |

---

## Trips

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trips` | Trip history (train + ride) |
| POST | `/trips/complaints` | Submit complaint |

---

## Admin API

Prefix: `/admin` — requires admin JWT.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/auth/login` | Admin login |
| GET | `/admin/dashboard/stats` | Dashboard metrics |
| GET/POST/PATCH/DELETE | `/admin/users/*` | User management |
| GET/POST/PATCH/DELETE | `/admin/drivers/*` | Driver management |
| GET | `/admin/rides`, `/admin/rides/live` | Ride monitoring |
| GET | `/admin/revenue` | Revenue analytics |
| GET/POST | `/admin/notifications/*` | Broadcast notifications |
| GET/PATCH | `/admin/complaints/*` | Complaint management |

### Admin Login
```json
POST /admin/auth/login
{ "email": "admin@railride.com", "password": "Admin@123" }
```

---

## Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Ride not found"
  },
  "request_id": "abc-123"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request / validation error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 409 | Conflict (duplicate) |
| 422 | Validation error |
| 500 | Internal server error |
