import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App.jsx'
import TestPage from './TestPage.jsx'
import Test2 from './components/Test2.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/test" element={<TestPage />} />
        <Route path="/test2" element={<Test2 />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
