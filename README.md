# PocketSmart AI

PocketSmart AI is a budget-planning web application that helps users organize spending for home interiors, parties, and jewelry. It uses Google Gemini to generate recommendations based on each user's budget and preferences. The application also provides account registration and login, a personal dashboard, and a history of saved recommendations.

## Features

- **Home planner:** Generate a room-by-room furnishing and decor plan using a total budget, room list, style, preferences, and selected shopping platforms.
- **Party planner:** Generate an event budget based on event type, guest count, venue, food preferences, and selected party needs.
- **Jewelry planner:** Get recommendations based on budget, occasion, jewelry types, metal, and style preferences. An outfit image can be included for visual analysis.
- **Accounts:** Register and log in to access the planners and personal pages. Passwords are stored as hashes.
- **Recommendation history:** View and clear saved recommendations for the signed-in account.
- **Responsive web interface:** Use the landing page, dashboard, planners, and history page in a browser.

## How it works

After registering or signing in, a user selects a planner and enters a budget along with relevant preferences. PocketSmart sends those details to the Google Gemini API, then displays the generated plan and saves it to the user's recommendation history. Saved recommendations can be revisited or cleared from the history page.

AI suggestions and prices are generated content, not live product listings or guaranteed quotes. Check product availability, current prices, and event costs with the relevant provider before making a purchase or booking.

## Technology

- Python and FastAPI
- Google Gemini API (`google-genai`)
- Jinja2, HTML, CSS, and JavaScript
- JWT authentication with `python-jose`, password hashing with `passlib` and `bcrypt`
- Pillow for image handling
- In-memory storage for user accounts and recommendation history

## Project structure

```text
.
├── app.py                 # FastAPI application and shared pages/API routes
├── auth.py                # Password hashing and JWT authentication helpers
├── models.py              # Pydantic user and token models
├── state.py               # In-memory recommendation history
├── requirements.txt       # Python dependencies
├── routers/
│   ├── auth.py            # Registration, login, logout, and session routes
│   ├── home.py            # Home planner page and recommendation endpoint
│   ├── party.py           # Party planner page and recommendation endpoint
│   └── jewelry.py         # Jewelry planner page and recommendation endpoint
├── templates/             # Jinja2 pages for the app and planners
└── static/
	└── styles.css         # Shared stylesheet
```

## Run locally

### Requirements

- Python installed and available from the command line
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- Internet access for Gemini-powered recommendations

### Setup

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/PocketSmart-AI-Your-Smart-Budget-Recommendation-Assistant.git
cd PocketSmart-AI-Your-Smart-Budget-Recommendation-Assistant
```

Open a terminal in the directory containing `app.py`. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS or Linux, activate it with:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a file named `.env` beside `app.py` and add your credentials:

```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_long_random_secret
```

`GEMINI_API_KEY` is required when the application starts. `SECRET_KEY` signs login tokens; set a long, private value and do not share or commit it. Never use a public or production secret in a repository.

Start the development server:

```bash
uvicorn app:app --reload
```

Open [http://localhost:8000](http://localhost:8000). 

## Main routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Landing page |
| `GET` | `/register` | Registration page |
| `POST` | `/register` | Create an account |
| `GET` | `/login` | Login page |
| `POST` | `/token` | Sign in and receive an access token/cookie |
| `GET` | `/logout` | Sign out |
| `GET` | `/dashboard` | Signed-in user's dashboard |
| `GET` | `/history` | Signed-in user's recommendation history page |
| `GET`, `DELETE` | `/api/history` | Read or clear the signed-in user's history |
| `GET` | `/home-planner` | Home planner page |
| `POST` | `/generate-home` | Generate a home plan |
| `GET` | `/party-planner` | Party planner page |
| `POST` | `/generate-party` | Generate a party plan |
| `GET` | `/jewelry-planner` | Jewelry planner page |
| `POST` | `/generate-jewelry` | Generate jewelry recommendations |
| `POST` | `/recommendations-details` | Generate detailed product recommendations |
| `GET` | `/session-info`, `/session-data` | Read account/session information |
| `GET` | `/startup` | Basic application status response |

Planner, dashboard, and history routes require authentication. Requests to the generation endpoints should use the request fields shown in the corresponding planner forms or API documentation.

## Notes

- **Data is temporary:** Account records and recommendation history are held in memory. They are cleared when the process stops, and this setup is not shared across multiple server workers.
- **Development use:** The app currently uses an in-memory user store and permissive CORS settings. Before deploying publicly, use persistent storage, review authentication and cookie settings, restrict allowed origins, and configure production secrets and HTTPS.
- **API usage:** Gemini-powered features require a valid API key and may be subject to Google's availability, quotas, and billing terms.
- **Generated recommendations:** Verify prices, products, links, and venue information independently.

## Team Members

G Vidya

G Keerthika

G Keerthana

A Vidya Bharathi

B Dhanalakshmi
