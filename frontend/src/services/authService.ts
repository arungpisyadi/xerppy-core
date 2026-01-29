/** Authentication service for API calls */

const API_URL = 'http://localhost:8003/api/v1';

interface TokenResponse {
  access_token: string;
  token_type: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  roles: string[];
  created_at: string;
}

class AuthService {
  private tokenKey = 'xerppy_token';
  private userKey = 'xerppy_user';

  /**
   * Login user with email/username and password
   */
  async login(username: string, password: string): Promise<User> {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: TokenResponse = await response.json();
    
    // Store token
    localStorage.setItem(this.tokenKey, data.access_token);
    
    // Get user info
    const user = await this.getCurrentUser();
    
    return user;
  }

  /**
   * Logout user - clears stored credentials
   */
  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  /**
   * Get current user from API
   */
  async getCurrentUser(): Promise<User> {
    const token = this.getToken();
    
    if (!token) {
      throw new Error('No token found');
    }

    const response = await fetch(`${API_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      this.logout();
      throw new Error('Failed to get user');
    }

    const user: User = await response.json();
    localStorage.setItem(this.userKey, JSON.stringify(user));
    
    return user;
  }

  /**
   * Get cached user from localStorage
   */
  getCachedUser(): User | null {
    const userStr = localStorage.getItem(this.userKey);
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  }

  /**
   * Get JWT token from storage
   */
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Register new user
   */
  async register(username: string, email: string, password: string): Promise<User> {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    // Auto login after registration
    return this.login(username, password);
  }
}

export const authService = new AuthService();
export type { User };
