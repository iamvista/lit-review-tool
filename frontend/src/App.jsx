import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { authService } from './services/auth'

// Pages
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import ReadingView from './pages/ReadingView'
import NetworkAnalysis from './pages/NetworkAnalysis'
import AIAnalysis from './pages/AIAnalysis'
import Settings from './pages/Settings'

// Protected Route Component
function ProtectedRoute({ children }) {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  return children
}

// Public Route Component (redirect if already logged in)
function PublicRoute({ children }) {
  if (authService.isAuthenticated()) {
    return <Navigate to="/projects" replace />
  }
  return children
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          }
        />
        <Route
          path="/reset-password"
          element={
            <PublicRoute>
              <ResetPassword />
            </PublicRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <Projects />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId"
          element={
            <ProtectedRoute>
              <ProjectDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/reading"
          element={
            <ProtectedRoute>
              <ReadingView />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/network"
          element={
            <ProtectedRoute>
              <NetworkAnalysis />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId/ai-analysis"
          element={
            <ProtectedRoute>
              <AIAnalysis />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />

        {/* Default Route */}
        <Route path="/" element={<Navigate to="/projects" replace />} />
      </Routes>
    </Router>
  )
}

export default App
