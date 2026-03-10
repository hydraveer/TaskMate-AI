// src/components/Chat.jsx

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

function Chat() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  // Get token from localStorage
  const token = localStorage.getItem('token');

  // Redirect if not logged in
  useEffect(() => {
    if (!token) {
      navigate('/login');
    } else {
      fetchTasks();
    }
  }, [token, navigate]);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      const response = await fetch('http://localhost:8000/tasks', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setTasks(data);
      }
    } catch (err) {
      console.error('Error fetching tasks:', err);
    }
  };

  // Send message to AI
  const handleSend = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Add user message to chat
    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: message })
      });

      const data = await response.json();

      // Add AI response to chat
      const aiMessage = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, aiMessage]);

      // Refresh tasks
      fetchTasks();
    } catch (err) {
      console.error('Error:', err);
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, something went wrong. Please try again.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🤖</span>
            <h1 className="text-2xl font-bold text-gray-800">TaskMate AI</h1>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Tasks Sidebar */}
        <aside className="w-80 bg-white border-r border-gray-200 p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Your Tasks</h2>
          
          {tasks.length === 0 ? (
            <p className="text-gray-500 text-sm">No tasks yet. Ask AI to create one!</p>
          ) : (
            <div className="space-y-2">
              {tasks.map(task => (
                <div
                  key={task.id}
                  className={`p-3 rounded-lg border ${
                    task.completed 
                      ? 'bg-green-50 border-green-200' 
                      : 'bg-white border-gray-200'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <div className="mt-1">
                      {task.completed ? '✓' : '○'}
                    </div>
                    <div className="flex-1">
                      <p className={`text-sm font-medium ${
                        task.completed ? 'text-gray-500 line-through' : 'text-gray-800'
                      }`}>
                        {task.title}
                      </p>
                      {task.description && (
                        <p className="text-xs text-gray-500 mt-1">
                          {task.description}
                        </p>
                      )}
                      {task.due_date && (
                        <p className="text-xs text-gray-400 mt-1">
                          Due: {new Date(task.due_date).toLocaleDateString()}
                        </p>
                      )}
                      <span className={`inline-block text-xs px-2 py-0.5 rounded mt-1 ${
                        task.priority === 'high' ? 'bg-red-100 text-red-700' :
                        task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {task.priority}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </aside>

        {/* Chat Area */}
        <main className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-20">
                <p className="text-lg mb-2">👋 Hi! I'm your task assistant.</p>
                <p className="text-sm">Try saying: "Add task to buy groceries"</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-2xl px-4 py-3 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-800 shadow-sm border border-gray-200'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-800 shadow-sm border border-gray-200 px-4 py-3 rounded-2xl">
                  <p className="text-sm">Thinking...</p>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Box */}
          <div className="border-t border-gray-200 bg-white p-4">
            <form onSubmit={handleSend} className="max-w-4xl mx-auto">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type a message... (e.g., 'Add task to buy milk tomorrow')"
                  disabled={loading}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={loading || !message.trim()}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Chat;