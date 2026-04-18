import React, { useEffect, useState } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button, Card, Input } from '../components/UI'
import { authService } from '../services/api'
import { useAuth } from '../hooks/useAuth'

const OTP_COOLDOWN_SECONDS = 60

const LoginPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [infoMessage, setInfoMessage] = useState(location.state?.message || '')
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })

  const [otpEmail, setOtpEmail] = useState(location.state?.email || '')
  const [otpCode, setOtpCode] = useState('')
  const [otpLoading, setOtpLoading] = useState(false)
  const [otpStatus, setOtpStatus] = useState('')
  const [otpError, setOtpError] = useState('')
  const [cooldown, setCooldown] = useState(0)

  useEffect(() => {
    const queryEmail = new URLSearchParams(location.search).get('email')
    if (queryEmail && !otpEmail) {
      setOtpEmail(queryEmail)
    }
  }, [location.search, otpEmail])

  useEffect(() => {
    if (cooldown <= 0) return undefined

    const timer = setInterval(() => {
      setCooldown((prev) => (prev > 0 ? prev - 1 : 0))
    }, 1000)

    return () => clearInterval(timer)
  }, [cooldown])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authService.login(formData.username, formData.password)
      const { access, refresh } = response.data.tokens
      login(access, refresh)
      navigate('/chat')
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed'
      setError(message)

      if (message.toLowerCase().includes('invalid credentials')) {
        setInfoMessage('If you just signed up, verify your email with OTP below, then try login again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRequestOtp = async (isResend = false) => {
    if (!otpEmail.trim()) {
      setOtpError('Please enter your signup email first.')
      setOtpStatus('')
      return
    }

    if (cooldown > 0) {
      setOtpError(`Please wait ${cooldown}s before requesting another OTP.`)
      setOtpStatus('')
      return
    }

    setOtpLoading(true)
    setOtpError('')
    setOtpStatus(isResend ? 'Resending OTP...' : 'Requesting OTP...')

    try {
      const response = await authService.requestOtp(otpEmail.trim().toLowerCase())
      setOtpStatus(response.data?.message || 'If this email exists, OTP has been sent.')
      setCooldown(OTP_COOLDOWN_SECONDS)
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to request OTP'
      setOtpError(message)
      setOtpStatus('')
    } finally {
      setOtpLoading(false)
    }
  }

  const handleVerifyOtp = async (e) => {
    e.preventDefault()

    if (!otpEmail.trim() || !otpCode.trim()) {
      setOtpError('Please enter both email and OTP code.')
      setOtpStatus('')
      return
    }

    setOtpLoading(true)
    setOtpError('')
    setOtpStatus('Verifying OTP...')

    try {
      const response = await authService.verifyOtp(
        otpEmail.trim().toLowerCase(),
        otpCode.trim()
      )
      setOtpStatus(response.data?.message || 'Email verified successfully. You can login now.')
      setOtpCode('')
      setInfoMessage('Email verified. Please login with your username and password.')
    } catch (err) {
      const message = err.response?.data?.detail || 'OTP verification failed'
      setOtpError(message)
      setOtpStatus('')
    } finally {
      setOtpLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-md"
      >
        <Card className="p-8">
          <div className="text-center mb-8">
            <h1 className="gradient-text text-3xl font-bold mb-2">AI Mail</h1>
            <p className="text-white/60">Welcome back</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Username"
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              placeholder="Enter your username"
              required
            />

            <Input
              label="Password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Enter your password"
              required
            />

            {infoMessage && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 rounded bg-blue-500/20 border border-blue-500/50 text-blue-200 text-sm"
              >
                {infoMessage}
              </motion.div>
            )}

            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 rounded bg-red-500/20 border border-red-500/50 text-red-300 text-sm"
              >
                {error}
              </motion.div>
            )}

            <Button
              variant="primary"
              className="w-full"
              disabled={loading}
              type="submit"
            >
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>

          <div className="my-6 flex items-center gap-3">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-sm text-white/50">OTP verification</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <Input
              label="Email"
              type="email"
              value={otpEmail}
              onChange={(e) => setOtpEmail(e.target.value)}
              placeholder="Enter your signup email"
              required
            />

            <div className="grid grid-cols-2 gap-3">
              <Button
                variant="primary"
                type="button"
                onClick={() => handleRequestOtp(false)}
                disabled={otpLoading || cooldown > 0}
                className="w-full"
              >
                Request OTP
              </Button>
              <Button
                variant="secondary"
                type="button"
                onClick={() => handleRequestOtp(true)}
                disabled={otpLoading || cooldown > 0}
                className="w-full"
              >
                {cooldown > 0 ? `Resend (${cooldown}s)` : 'Resend OTP'}
              </Button>
            </div>

            <Input
              label="OTP Code"
              type="text"
              inputMode="numeric"
              maxLength={6}
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value)}
              placeholder="Enter 6-digit OTP"
              required
            />

            {otpStatus && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 rounded bg-green-500/20 border border-green-500/50 text-green-300 text-sm"
              >
                {otpStatus}
              </motion.div>
            )}

            {otpError && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 rounded bg-red-500/20 border border-red-500/50 text-red-300 text-sm"
              >
                {otpError}
              </motion.div>
            )}

            <Button
              variant="primary"
              className="w-full"
              disabled={otpLoading}
              type="submit"
            >
              {otpLoading ? 'Processing...' : 'Verify OTP'}
            </Button>
          </form>

          <div className="my-6 flex items-center gap-3">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-sm text-white/50">or</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          <p className="text-center text-white/60 text-sm">
            Don't have an account?{' '}
            <Link to="/register" className="text-brand-secondary hover:text-brand-primary transition-smooth font-semibold">
              Sign up
            </Link>
          </p>

          <div className="mt-6 pt-6 border-t border-white/10 text-center">
            <Link to="/">
              <Button variant="ghost" size="sm" className="text-white/60 hover:text-white">
                {'← Back to home'}
              </Button>
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}

export default LoginPage
