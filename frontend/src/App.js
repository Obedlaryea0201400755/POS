import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [user, setUser] = useState(null);
  const [sales, setSales] = useState([]);

  const login = async () => {
    try {
      const response = await axios.post('/login', { username, password });
      setToken(response.data.access_token);
      const decoded = jwtDecode(response.data.access_token);
      setUser(decoded.identity);
    } catch (error) {
      console.error('Login failed', error);
    }
  };

  const getSales = async () => {
    try {
      const response = await axios.get('/sales', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSales(response.data);
    } catch (error) {
      console.error('Failed to fetch sales', error);
    }
  };

  useEffect(() => {
    if (user && user.role === 'admin') {
      getSales();
    }
  }, [user]);

  return (
    <div className="App">
      {!token ? (
        <div>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button onClick={login}>Login</button>
        </div>
      ) : (
        <div>
          <h1>Welcome to the POS</h1>
          <p>You are logged in as {user && user.username}</p>
          {user && user.role === 'admin' && (
            <div>
              <h2>Sales Report</h2>
              <ul>
                {sales.map((sale) => (
                  <li key={sale.id}>
                    Product ID: {sale.product_id}, Quantity: {sale.quantity}, Total: ${sale.total_price}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
