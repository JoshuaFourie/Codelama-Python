import React from 'react';
import Image from 'next/image';
import Link from 'next/link';

const Header = () => {
  // App branding constants - you can move these to a config file later
  const APP_NAME = "J's CodeBuddy AI";
  const APP_TAGLINE = "Your Python & PowerShell Coding Assistant";
  
  return (
    <header className="header">
      <div className="container">
        <div className="header-container">
          <div className="logo-container">
            <Link href="/">
              <Image 
                src="/logo.png" 
                alt={APP_NAME} 
                width={40} 
                height={40} 
                className="logo-image"
              />
            </Link>
          </div>
          <div className="title-container">
            <h1 className="app-title">{APP_NAME}</h1>
            <p className="app-tagline">{APP_TAGLINE}</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;