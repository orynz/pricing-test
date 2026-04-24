import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

const api = axios.create({
  // 호스트네임이 localhost가 아니면 무조건 상대 경로 '/api/v1' 사용
  baseURL: isLocalhost ? 'http://localhost:8000/api/v1' : '/api/v1',
});

// 모든 요청에 JWT와 Project ID 추가
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  
  config.headers['x-project-id'] = import.meta.env.VITE_PROJECT_ID;
  
  return config;
});

export default api;
