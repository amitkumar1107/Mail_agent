import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 via-blue-900 to-purple-900">
        <div className="animate-pulse">
          <div className="w-12 h-12 rounded-full border-4 border-brand-primary border-t-brand-secondary animate-spin mx-auto" />
          <p className="text-white/60 mt-4 text-center">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute
