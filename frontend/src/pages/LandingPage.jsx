import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button, Card } from '../components/UI'

const LandingPage = () => {
  const features = [
    {
      icon: '✍️',
      title: 'AI Email Generation',
      description: 'Describe your email in natural language and let AI draft it perfectly.',
    },
    {
      icon: '🎤',
      title: 'Voice Commands',
      description: 'Use voice input to compose emails hands-free.',
    },
    {
      icon: '🔔',
      title: 'Smart Reminders',
      description: 'Never forget important dates with intelligent reminders.',
    },
    {
      icon: '👥',
      title: 'Contact Management',
      description: 'Organize and manage all your contacts in one place.',
    },
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-blue-900 to-purple-900 text-white overflow-hidden">
      {/* Navigation */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="fixed top-0 left-0 right-0 z-50 glass m-4 md:m-6"
      >
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="gradient-text text-2xl font-bold">AI Mail</h1>
          <div className="flex gap-4">
            <Link to="/login">
              <Button variant="secondary" size="sm">
                Login
              </Button>
            </Link>
            <Link to="/register">
              <Button variant="primary" size="sm">
                Sign Up
              </Button>
            </Link>
          </div>
        </div>
      </motion.nav>

      <div className="min-h-screen flex flex-col justify-center items-center px-4 md:px-8 pt-32">
        {/* Hero Section */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="text-center max-w-4xl mx-auto mb-20"
        >
          <motion.div variants={itemVariants} className="mb-6">
            <div className="text-6xl md:text-7xl font-bold mb-4 gradient-text">
              Your AI Email Assistant
            </div>
            <div className="text-xl md:text-2xl text-white/70 mb-8">
              That Thinks for You
            </div>
            <p className="text-lg text-white/60 mb-8 max-w-2xl mx-auto">
              Compose professional emails instantly using natural language. Let AI handle the writing while you focus on what matters.
            </p>
          </motion.div>

          <motion.div
            variants={itemVariants}
            className="flex gap-4 justify-center flex-wrap mb-16"
          >
            <Link to="/register">
              <Button variant="primary" size="lg">
                🚀 Get Started
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="lg">
                📧 Try Demo
              </Button>
            </Link>
          </motion.div>

          {/* Decorative Circle */}
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 0.1 }}
            transition={{ duration: 1 }}
            className="absolute inset-0 -z-10 bg-gradient-to-b from-brand-primary to-brand-secondary rounded-full blur-3xl w-96 h-96 mx-auto"
          />
        </motion.div>

        {/* Features */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl w-full my-20"
        >
          {features.map((feature, idx) => (
            <motion.div key={idx} variants={itemVariants}>
              <Card className="text-center h-full hover-lift">
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-bold mb-2">{feature.title}</h3>
                <p className="text-sm text-white/60">{feature.description}</p>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* About Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto my-20 text-center"
        >
          <Card className="p-8">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-2xl font-bold mb-4 gradient-text">
              Built for Modern Professionals
            </h3>
            <p className="text-white/70 leading-relaxed mb-6">
              Stop wasting hours composing emails. Our AI understands context and generates professional, 
              personalized messages in seconds. Focus on relationships, not writing.
            </p>
            <div className="text-sm text-white/60">
              Trusted by professionals worldwide • Powered by Advanced AI
            </div>
          </Card>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="my-20 text-center"
        >
          <Link to="/register">
            <Button variant="primary" size="lg" className="px-12">
              Start Free Trial
            </Button>
          </Link>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        className="border-t border-white/10 py-8 px-6 text-center text-white/50 text-sm"
      >
        <p>© 2026 AI Mail Assistant. Revolutionizing how you communicate.</p>
      </motion.footer>
    </div>
  )
}

export default LandingPage
