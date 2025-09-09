import { useEffect, useRef } from 'react'
import { io } from 'socket.io-client'
import { useAuth } from '../context/AuthContext'

export const useSockets = () => {
  const { user, isAuthenticated } = useAuth()
  const socketRef = useRef(null)

  useEffect(() => {
    if (isAuthenticated && user) {
      // Connect to SocketIO server
      socketRef.current = io('/', {
        transports: ['websocket', 'polling']
      })

      // Join user's personal room
      socketRef.current.emit('join_user_room', { user_id: user.id })

      // Handle connection events
      socketRef.current.on('connect', () => {
        console.log('Connected to server')
      })

      socketRef.current.on('disconnect', () => {
        console.log('Disconnected from server')
      })

      // Cleanup on unmount
      return () => {
        if (socketRef.current) {
          socketRef.current.emit('leave_user_room', { user_id: user.id })
          socketRef.current.disconnect()
        }
      }
    }
  }, [isAuthenticated, user])

  const onParseStarted = (callback) => {
    if (socketRef.current) {
      socketRef.current.on('parse_started', callback)
    }
  }

  const onParseFinished = (callback) => {
    if (socketRef.current) {
      socketRef.current.on('parse_finished', callback)
    }
  }

  const onMatchFinished = (callback) => {
    if (socketRef.current) {
      socketRef.current.on('match_finished', callback)
    }
  }

  const onProgressUpdate = (callback) => {
    if (socketRef.current) {
      socketRef.current.on('progress_update', callback)
    }
  }

  const onBulkMatchProgress = (callback) => {
    if (socketRef.current) {
      socketRef.current.on('bulk_match_progress', callback)
    }
  }

  const onBulkMatchFinished = (callback) => {
    if (socketRef.current) {
      socketRef.current.on('bulk_match_finished', callback)
    }
  }

  const removeAllListeners = () => {
    if (socketRef.current) {
      socketRef.current.removeAllListeners()
    }
  }

  return {
    socket: socketRef.current,
    onParseStarted,
    onParseFinished,
    onMatchFinished,
    onProgressUpdate,
    onBulkMatchProgress,
    onBulkMatchFinished,
    removeAllListeners
  }
}
