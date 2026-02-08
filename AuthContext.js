import React, { createContext, useContext, useReducer, useEffect } from 'react';

const AuthContext = createContext();

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        loading: false,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token
      };
    case 'LOGIN_FAILURE':
      return { ...state, loading: false, error: action.payload };
    case 'LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        token: null
      };
    case 'SET_USER':
      return {
        ...state,
        user: action.payload
      };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, {
    isAuthenticated: false,
    user: null,
    token: null,
    loading: false,
    error: null
  });

  // Check for existing token on app start
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and set user
      const user = localStorage.getItem('user');
      if (user) {
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: {
            token,
            user: JSON.parse(user)
          }
        });
      }
    }
  }, []);

  const login = async (username, password) => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Store token and user
      localStorage.setItem('token', data.access_token);
      const tokenPayload = JSON.parse(atob(data.access_token.split('.')[1]));
      const userInfo = {
        id: tokenPayload.sub,
        username
      };
      localStorage.setItem('user', JSON.stringify(userInfo));

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          token: data.access_token,
          user: userInfo
        }
      });

      return { success: true };
    } catch (error) {
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: error.message
      });
      return { success: false, error: error.message };
    }
  };

  const loginWithToken = async (tokenData) => {
    dispatch({ type: 'LOGIN_START' });

    try {
      // Store token and user from GitHub OAuth response
      localStorage.setItem('token', tokenData.access_token);
      const userInfo = tokenData.user || {
        id: tokenData.access_token ? JSON.parse(atob(tokenData.access_token.split('.')[1])).sub : null,
        username: tokenData.access_token ? JSON.parse(atob(tokenData.access_token.split('.')[1])).sub : null
      };
      localStorage.setItem('user', JSON.stringify(userInfo));

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          token: tokenData.access_token,
          user: userInfo
        }
      });

      return { success: true };
    } catch (error) {
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: error.message
      });
      return { success: false, error: error.message };
    }
  };

  const register = async (username, email, password, fullName = '') => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          email,
          password,
          full_name: fullName
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      // Store token and user
      localStorage.setItem('token', data.access_token);
      const tokenPayload = JSON.parse(atob(data.access_token.split('.')[1]));
      const userInfo = {
        id: tokenPayload.sub,
        username
      };
      localStorage.setItem('user', JSON.stringify(userInfo));

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          token: data.access_token,
          user: userInfo
        }
      });

      return { success: true };
    } catch (error) {
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: error.message
      });
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    dispatch({ type: 'LOGOUT' });
  };

  const value = {
    ...state,
    login,
    register,
    logout,
    loginWithToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};