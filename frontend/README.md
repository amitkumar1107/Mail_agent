# AI Mail Assistant - React Frontend

A modern, professional React SPA for the AI Mail Assistant application.

## Features

- 🎨 Beautiful dark theme with glassmorphism design
- 💬 Real-time chat interface with AI email generation
- 🎤 Voice input support
- 📊 Comprehensive dashboard with analytics
- 👥 Contact management system
- 🔔 Smart reminders
- 📝 Email templates
- 🔐 Secure authentication
- 📱 Fully responsive design

## Tech Stack

- **React 18** - UI framework
- **React Router v6** - Navigation
- **Framer Motion** - Animations
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Vite** - Build tool

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Environment Setup

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=AI Mail Assistant
```

### Development

```bash
npm run dev
```

The app will open at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx              # Main app component
│   ├── index.jsx            # Entry point
│   ├── components/
│   │   ├── UI.jsx           # Reusable UI components
│   │   ├── Sidebar.jsx      # Navigation sidebar
│   │   ├── Topbar.jsx       # Top navigation
│   │   ├── ChatBox.jsx      # Chat interface
│   │   ├── Dashboard.jsx    # Dashboard stats
│   │   ├── ContactsPage.jsx # Contacts management
│   │   ├── RemindersPage.jsx # Reminders
│   │   ├── TemplatesPage.jsx # Email templates
│   │   └── HistoryPage.jsx  # Activity history
│   ├── pages/
│   │   ├── LandingPage.jsx  # Home page
│   │   ├── LoginPage.jsx    # Login
│   │   ├── RegisterPage.jsx # Registration
│   │   └── HomePage.jsx     # Main app layout
│   ├── contexts/
│   │   ├── AuthContext.jsx  # Auth state
│   │   └── ChatContext.jsx  # Chat state
│   ├── hooks/
│   │   └── useAuth.js       # Auth hook
│   ├── services/
│   │   └── api.js           # API client
│   └── styles/
│       └── globals.css      # Global styles
├── public/                  # Static assets
├── index.html              # HTML entry
├── vite.config.js          # Vite config
├── tailwind.config.js      # Tailwind config
└── package.json            # Dependencies

```

## API Integration

The frontend connects to the Django backend API at `http://localhost:8000/api`.

### Endpoints Used

- `POST /auth/login/` - User login
- `POST /auth/signup/` - User registration
- `POST /mail/commands/parse/` - Parse email command
- `POST /mail/drafts/preview/` - Generate email preview
- `POST /mail/drafts/confirm/` - Send/edit/cancel draft
- `GET /mail/insights/dashboard/` - Dashboard data
- `GET /contacts/` - Fetch contacts
- `POST /contacts/` - Create contact
- `GET /reminders/` - Fetch reminders
- `POST /reminders/` - Create reminder
- `POST /voice/transcribe/` - Voice transcription

## Key Features

### Authentication

- Separate login and register pages
- JWT token-based authentication
- Protected routes
- Auto-logout on token expiry

### Chat Assistant

- Real-time message display
- AI email generation
- Email preview before sending
- Voice input support
- Typing animations

### Dashboard

- Key statistics (emails sent, reminders, contacts)
- AI suggestions
- Frequent contacts list
- Upcoming events
- Recent activity

### Contact Management

- Add new contacts
- View contact list
- Relationship categorization
- Search functionality

### Reminders

- Create reminders for contacts
- Multiple reminder types (birthday, anniversary, follow-up)
- Date-based notifications

## Styling

The app uses Tailwind CSS with custom configuration for:

- Dark theme (`dark-*` colors)
- Brand colors (primary: `#6C63FF`, secondary: `#00D4FF`)
- Glassmorphism effect classes
- Custom animations

## Performance

- Code splitting with React Router
- Lazy loading of components
- Optimized animations with Framer Motion
- Efficient state management
- API request caching

## Development Tips

- Use `npm run dev` for HMR development
- Check browser console for debugging
- Use DevTools React extension for component inspection
- Monitor network tab for API calls

## Deployment

Build the frontend:

```bash
npm run build
```

The `dist` folder contains production-ready files.

### Deployment Options

1. **Vercel** - Recommended for React apps
2. **Netlify** - Great for static sites
3. **Docker** - Create a Dockerfile for containerization
4. **Backend Static Files** - Serve from Django as static files

Example Docker setup:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Troubleshooting

### CORS Issues

Ensure Django backend has proper CORS headers configured:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

### API Connection Issues

- Check `VITE_API_URL` in `.env`
- Ensure backend is running
- Check browser network tab
- Verify authentication tokens

### Build Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

© 2026 AI Mail Assistant
