import React from 'react';
import Navbar from '@theme-original/Navbar';
import AuthComponent from '../../components/AuthComponent';

function NavbarWrapper(props) {
  return (
    <>
      <Navbar {...props} />
      <div style={{
        position: 'absolute',
        right: '20px',
        top: '20px',
        zIndex: 1000
      }}>
        <AuthComponent />
      </div>
    </>
  );
}

export default NavbarWrapper;