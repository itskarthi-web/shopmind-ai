import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { FiSend, FiShoppingBag, FiStar } from 'react-icons/fi';
import './App.css';

const API_URL = 'http://127.0.0.1:8000';
const SESSION_ID = 'user_' + Math.random().toString(36).substr(2, 9);

function ProductCard({ product }) {
  const price =
    product.discount_price !== 'nan'
      ? product.discount_price
      : product.actual_price;

  return (
    <div className="product-card">
      {product.image ? (
        <img
          src={product.image}
          alt="product"
          className="product-image"
          onError={(e) => {
            e.target.style.display = 'none';
          }}
        />
      ) : null}

      <div className="product-info">
        <p className="product-name">{product.name.substring(0, 80)}...</p>

        <div className="product-meta">
          <span className="product-price">Rs.{price}</span>
          {product.discount_pct > 0 ? (
            <span className="product-discount">{product.discount_pct}% off</span>
          ) : null}
        </div>

        <div className="product-rating">
          <FiStar className="star-icon" />
          <span>{product.ratings}/5</span>
          <span className="review-count">({product.no_of_ratings} reviews)</span>
        </div>

        {product.link ? (
          <a
            href={product.link}
            target="_blank"
            rel="noopener noreferrer"
            className="product-link"
          >
            View on Amazon
          </a>
        ) : null}
      </div>
    </div>
  );
}

function Message({ msg }) {
  return (
    <div className={'message-wrapper ' + msg.role}>
      <div className={'message-bubble ' + msg.role}>
        <p>{msg.content}</p>
      </div>

      {msg.products && msg.products.length > 0 ? (
        <div className="products-grid">
          {msg.products.slice(0, 3).map(function (product, i) {
            return <ProductCard key={i} product={product} />;
          })}
        </div>
      ) : null}
    </div>
  );
}

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        'Hi! I am ShopMind AI, your personal shopping assistant. Tell me what you are looking for and I will find the best products for you. Try: I want wireless headphones under 2000 rupees',
      products: [],
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(function () {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  function sendMessage() {
    if (!input.trim() || loading) return;

    var userMessage = input.trim();
    setInput('');

    setMessages(function (prev) {
      return prev.concat([{ role: 'user', content: userMessage, products: [] }]);
    });

    setLoading(true);

    axios
      .post(API_URL + '/chat', {
        message: userMessage,
        session_id: SESSION_ID,
      })
      .then(function (response) {
        setMessages(function (prev) {
          return prev.concat([
            {
              role: 'assistant',
              content: response.data.reply,
              products: response.data.products || [],
            },
          ]);
        });
        setLoading(false);
      })
      .catch(function () {
        setMessages(function (prev) {
          return prev.concat([
            {
              role: 'assistant',
              content:
                'Sorry, I could not connect. Please make sure the API server is running on port 8000.',
              products: [],
            },
          ]);
        });
        setLoading(false);
      });
  }

  function handleKeyPress(e) {
    if (e.key === 'Enter') {
      sendMessage();
    }
  }

  var suggestions = [
    'Headphones under 2000 rupees',
    'Cricket bat under 1000 rupees',
    'Best gaming laptop',
    'Caps under 300 rupees',
  ];

  return (
    <div className="app">
      <div className="header">
        <FiShoppingBag className="header-icon" />
        <div>
          <h1>ShopMind AI</h1>
          <p>Your Intelligent Shopping Assistant</p>
        </div>
        <div className="status-dot" />
      </div>

      <div className="suggestions">
        {suggestions.map(function (s, i) {
          return (
            <button
              key={i}
              className="chip"
              onClick={function () {
                setInput(s);
              }}
            >
              {s}
            </button>
          );
        })}
      </div>

      <div className="chat-area">
        {messages.map(function (msg, i) {
          return <Message key={i} msg={msg} />;
        })}

        {loading ? (
          <div className="message-wrapper assistant">
            <div className="message-bubble assistant loading">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        ) : null}

        <div ref={bottomRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={function (e) {
            setInput(e.target.value);
          }}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything... e.g. Best phone under 15000"
          disabled={loading}
          className="chat-input"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="send-button"
        >
          <FiSend />
        </button>
      </div>
    </div>
  );
}

export default App;