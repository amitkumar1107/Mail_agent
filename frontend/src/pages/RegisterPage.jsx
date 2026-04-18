import React, { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button, Card, Input } from '../components/UI'
import { authService } from '../services/api'

const OTP_COOLDOWN_SECONDS = 60

const RegisterPage = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  })

  const [showOtpStep, setShowOtpStep] = useState(false)
  const [otpEmail, setOtpEmail] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [otpLoading, setOtpLoading] = useState(false)
  const [otpStatus, setOtpStatus] = useState('')
  const [otpError, setOtpError] = useState('')
  const [cooldown, setCooldown] = useState(0)

  useEffect(() => {
    if (cooldown <= 0) return undefined

    const timer = setInterval(() => {
      setCooldown((prev) => (prev > 0 ? prev - 1 : 0))
    }, 1000)

    return () => clearInterval(timer)
  }, [cooldown])

  const parseApiError = (err, fallback) => {
    const apiData = err.response?.data
    if (typeof apiData === 'string') return apiData
    if (apiData?.detail) return apiData.detail
    if (apiData && typeof apiData === 'object') {
      const firstField = Object.keys(apiData)[0]
      const firstError = Array.isArray(apiData[firstField]) ? apiData[firstField][0] : apiData[firstField]
      return firstError || fallback
    }
    return fallback
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)

    try {
      const response = await authService.signup(
        formData.email,
        formData.username,
        formData.password
      )

      const email = formData.email.trim().toLowerCase()
      setOtpEmail(email)
      setShowOtpStep(true)
      setOtpError('')
      setOtpStatus(response.data?.message || 'Account created. OTP sent to your email.')
      setCooldown(OTP_COOLDOWN_SECONDS)
    } catch (err) {
      setError(parseApiError(err, 'Signup failed'))
    } finally {
      setLoading(false)
    }
  }

  const handleRequestOtp = async (isResend = false) => {
    if (!otpEmail.trim()) {
      setOtpError('Please enter your email first.')
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
      setOtpError(parseApiError(err, 'Failed to request OTP'))
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

      setOtpStatus(response.data?.message || 'Email verified successfully.')
      setOtpCode('')

      navigate('/login', {
        replace: true,
        state: {
          email: otpEmail.trim().toLowerCase(),
          message: 'Email verified successfully. Please login now.',
        },
      })
    } catch (err) {
      setOtpError(parseApiError(err, 'OTP verification failed'))
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
            <p className="text-white/60">{showOtpStep ? 'Verify your email' : 'Create your account'}</p>
          </div>

          {!showOtpStep && (
            <form onSubmit={handleSubmit} className="space-y-5">
              <Input
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="your@email.com"
                required
              />

              <Input
                label="Username"
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="Choose a username"
                required
              />

              <Input
                label="Password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Create a strong password"
                required
              />

              <Input
                label="Confirm Password"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                placeholder="Confirm your password"
                required
              />

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
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </form>
          )}

          {showOtpStep && (
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
          )}

          <div className="my-6 flex items-center gap-3">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-sm text-white/50">or</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          <p className="text-center text-white/60 text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-secondary hover:text-brand-primary transition-smooth font-semibold">
              Login
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

export default RegisterPage
