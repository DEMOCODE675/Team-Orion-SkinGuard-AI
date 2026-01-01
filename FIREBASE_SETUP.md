# Firebase Setup for SkinGuard AI (local dev)

Follow these concise steps to configure Firebase for the app.

1. Create a Firebase project

- Go to https://console.firebase.google.com/ and create a new project.

2. Enable Email/Password Authentication

- Project Settings → Authentication → Sign-in method → enable "Email/Password".

3. Get Web API Key & Auth Domain

- Project Settings → General → Your apps → Add web app (if needed).
- Note the "apiKey" (Web API Key) and "authDomain" (e.g. your-project.firebaseapp.com).

4. Optional: Service Account (only if you need admin features)

- Project Settings → Service accounts → Generate new private key → download JSON.
- Place it at: `frontend/firebase_creds.json` (do NOT commit this file).

5. Create .env at project root

- File: `c:\Users\priya\Music\AI-cancer\.env`
- Example contents (fill with your real values):
  FIREBASE_API_KEY=your-firebase-api-key
  FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
  FIREBASE_PROJECT_ID=your-project-id
  FIREBASE_DB_URL=https://your-project.firebaseio.com
  FIREBASE_STORAGE_BUCKET=your-project.appspot.com

6. Add to .gitignore

- Ensure you ignore secrets:
  ```
  .env
  frontend/firebase_creds.json
  ```

7. Install Python dependencies

- Run:
  pip install pyrebase4 python-dotenv

8. How the code uses these values

- The frontend auth reads the .env variables (via python-dotenv) and initializes Pyrebase.
- Optional service account (if used) goes to `frontend/firebase_creds.json` for server/admin tasks.

9. Test locally

- Start the Streamlit UI:
  streamlit run frontend/streamlit_app.py
- Use the sidebar to Sign Up with email/password, then Log In and test image upload → Analyze.

Troubleshooting

- "Login failed": verify API key and authDomain in `.env`.
- If using a custom domain or restrictions, ensure Authorized domains include `localhost`.
- For admin operations (server-side), prefer Firebase Admin SDK with a service account JSON (not needed for simple email/password sign-in via Pyrebase).

That's it — fill .env, install deps, and run the app.
