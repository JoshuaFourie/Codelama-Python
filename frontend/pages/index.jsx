import React from 'react';
import Head from 'next/head';
import Layout from '../components/layout/Layout';
import ChatBox from '../components/chat/ChatBox';
import DarkModeDebugger from '../components/DarkModeDebugger'; // Add this import

export default function Home() {
  return (
    <>
      <Head>
        <title>J's CodeBuddy AI - Python & PowerShell Coding Assistant</title>
        <meta name="description" content="Your AI coding assistant for Python and PowerShell" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <DarkModeDebugger /> {/* Add the Dark Mode Debugger */}
      
      <Layout>
        <div className="tab-content">
          <ChatBox />
        </div>
      </Layout>
    </>
  );
}