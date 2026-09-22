import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { getMe } from '../api/auth'

const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      user: null,

      setAuth: (token, user) => {
        localStorage.setItem('medichat_token', token)
        set({ token, user })
      },

      // Called after login/signup — fetches full user profile from /api/auth/me
      hydrateUser: async () => {
        const { token, user } = get()
        if (token && !user) {
          try {
            const { data } = await getMe()
            set({ user: data })
          } catch {
            // token invalid — leave it to the 401 interceptor to handle
          }
        }
      },

      logout: () => {
        localStorage.removeItem('medichat_token')
        set({ token: null, user: null })
      },
    }),
    {
      name: 'medichat-auth',
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
)

export default useAuthStore
