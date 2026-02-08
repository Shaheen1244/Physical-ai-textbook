import React, { useEffect } from 'react';
import { useHistory, useLocation } from '@docusaurus/router';
import { useAuth } from '../../context/AuthContext';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

const GithubCallbackPage = () => {
  const history = useHistory();
  const location = useLocation();
  const { loginWithToken } = useAuth();
  const { siteConfig } = useDocusaurusContext();

  useEffect(() => {
    const handleGithubCallback = async () => {
      // Extract code from URL query parameters
      const urlParams = new URLSearchParams(location.search);
      const code = urlParams.get('code');
      const error = urlParams.get('error');

      if (error) {
        console.error('GitHub OAuth error:', error);
        alert(`GitHub login failed: ${error}`);
        history.push('/auth/login');
        return;
      }

      if (!code) {
        console.error('No authorization code found in URL');
        history.push('/auth/login');
        return;
      }

      try {
        // Exchange code for token with backend
        const response = await fetch('http://localhost:8000/auth/github', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'GitHub login failed');
        }

        // Use the new loginWithToken function to handle the response
        const result = await loginWithToken(data);

        if (result.success) {
          // Redirect to home or previous page
          history.push('/');
        } else {
          throw new Error(result.error || 'Login failed');
        }
      } catch (err) {
        console.error('GitHub callback error:', err);
        alert(`GitHub login failed: ${err.message}`);
        history.push('/auth/login');
      }
    };

    handleGithubCallback();
  }, [location, history, loginWithToken]);

  return (
    <Layout title={`GitHub Login - ${siteConfig.title}`} description="Completing GitHub login">
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Logging in with GitHub...</h1>
        <p>Please wait while we complete the authentication process.</p>
      </div>
    </Layout>
  );
};

export default GithubCallbackPage;