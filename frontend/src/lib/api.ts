import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

const api = axios.create({
  // 배포 환경과 로컬 환경 모두에서 작동하도록 상대 경로 사용
  baseURL: import.meta.env.DEV ? 'http://localhost:8000/api/v1' : '/api/v1',
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
