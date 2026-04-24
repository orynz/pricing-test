import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

const api = axios.create({
  // 도메인 정보를 완전히 제거하고 상대 경로만 사용합니다.
  // 로컬 개발 시에는 vite.config.ts의 proxy 설정을 통해 백엔드로 전달됩니다.
  baseURL: '/api/v1',
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
