import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  // We are commenting out StrictMode to diagnose the connection issue.
  // This will prevent the component from mounting twice in development.
  // <React.StrictMode>
    <App />
  // </React.StrictMode>,
)
