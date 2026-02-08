import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useHistory, useLocation } from '@docusaurus/router';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const { login } = useAuth();
  const history = useHistory();
  const { siteConfig } = useDocusaurusContext();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const result = await login(formData.username, formData.password);
    if (result.success) {
      // Redirect to home or previous page
      history.push('/');
    } else {
      setError(result.error);
    }
  };

  return (
    <Layout title={`Login - ${siteConfig.title}`} description="Login to your account">
      <div style={{ padding: '2rem', maxWidth: '400px', margin: '0 auto' }}>
        <h1>Login</h1>
        {error && <div className="alert alert--danger">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="margin-bottom--md">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className="form-control"
            />
          </div>
          <div className="margin-bottom--md">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="form-control"
            />
          </div>
          <button type="submit" className="button button--primary">
            Login
          </button>
        </form>
        <div style={{ marginTop: '1rem' }}>
          Don't have an account? <Link to="/auth/signup">Sign up here</Link>
        </div>
      </div>
    </Layout>
  );
};

export default LoginPage;