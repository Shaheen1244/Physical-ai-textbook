import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useHistory, useLocation } from '@docusaurus/router';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });
  const [error, setError] = useState('');
  const { register } = useAuth();
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

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    const result = await register(
      formData.username,
      formData.email,
      formData.password,
      formData.fullName
    );

    if (result.success) {
      // Redirect to home or login page
      history.push('/');
    } else {
      setError(result.error);
    }
  };

  return (
    <Layout title={`Sign Up - ${siteConfig.title}`} description="Create a new account">
      <div style={{ padding: '2rem', maxWidth: '400px', margin: '0 auto' }}>
        <h1>Sign Up</h1>
        {error && <div className="alert alert--danger">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="margin-bottom--md">
            <label htmlFor="fullName">Full Name</label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              className="form-control"
            />
          </div>
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
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
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
          <div className="margin-bottom--md">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              className="form-control"
            />
          </div>
          <button type="submit" className="button button--primary">
            Sign Up
          </button>
        </form>
        <div style={{ marginTop: '1rem' }}>
          Already have an account? <Link to="/auth/login">Login here</Link>
        </div>
      </div>
    </Layout>
  );
};

export default SignupPage;