import axios from 'axios';

export async function loginApi(username: string, password: string) {
  const { data } = await axios.post('/api/auth/login', { username, password });
  return data;
}
