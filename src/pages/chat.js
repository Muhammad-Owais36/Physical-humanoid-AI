import React from 'react';
import Chatbot from '../components/Chatbot';
import Layout from '@theme/Layout';

export default function ChatPage() {
  return (
    <Layout title="Chat with AI" description="AI Chatbot Interface">
      <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', minHeight: '600px' }}>
        <h1>AI Chatbot</h1>
        <p>Ask questions and get responses from our AI assistant.</p>
        <Chatbot />
      </div>
    </Layout>
  );
}