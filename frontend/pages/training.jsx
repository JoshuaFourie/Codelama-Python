import React from 'react';
import Head from 'next/head';
import Layout from '../components/layout/Layout';
import TrainingDataManager from '../components/settings/TrainingDataManager';

export default function Training() {
  return (
    <>
      <Head>
        <title>Training Data - J's CodeBuddy AI</title>
        <meta name="description" content="Manage training data for your AI assistant" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Layout>
        <div className="tab-content">
          <TrainingDataManager />
        </div>
      </Layout>
    </>
  );
}