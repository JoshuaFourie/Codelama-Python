import '../styles/globals.css';
import '../styles/components.css';
import { useEffect } from 'react';
import Head from 'next/head';
import Router from 'next/router';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';
import 'prismjs/themes/prism-tomorrow.css';
import { AppProvider } from '../context/AppContext';

// Configure NProgress
NProgress.configure({ showSpinner: false });

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    // Setup loading indicator for page transitions
    const startProgress = () => NProgress.start();
    const stopProgress = () => NProgress.done();

    Router.events.on('routeChangeStart', startProgress);
    Router.events.on('routeChangeComplete', stopProgress);
    Router.events.on('routeChangeError', stopProgress);

    // Ensure dark mode is applied
    document.documentElement.classList.add('dark');
    document.body.classList.add('dark');

    return () => {
      Router.events.off('routeChangeStart', startProgress);
      Router.events.off('routeChangeComplete', stopProgress);
      Router.events.off('routeChangeError', stopProgress);
    };
  }, []);

  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content="CodeBuddy AI - Python & PowerShell Coding Assistant" />
        <meta name="theme-color" content="#111827" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link 
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" 
          rel="stylesheet" 
        />
      </Head>
      <AppProvider>
        <div className="dark">
          <Component {...pageProps} />
        </div>
      </AppProvider>
    </>
  );
}

export default MyApp;