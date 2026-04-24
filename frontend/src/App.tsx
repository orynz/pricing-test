import { useState, useEffect } from 'react';
import { supabase } from './lib/api';
import api from './lib/api';

function App() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [apiResult, setApiResult] = useState<any>(null);

  useEffect(() => {
    // 세션 체크
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // 인증 상태 변경 리스너
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      if (!session) setApiResult(null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogin = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: window.location.origin }
      });
      if (error) throw error;
    } catch (error: any) {
      alert("로그인 에러: " + error.message);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setApiResult(null);
  };

  const fetchMyInfo = async () => {
    try {
      setApiResult("호출 중...");
      // baseURL이 적용된 api 인스턴스 사용
      const response = await api.get('/auth/me');
      setApiResult(response.data);
    } catch (error: any) {
      console.error("API Error Detail:", error);
      setApiResult({ 
        error: error.response?.data || error.message,
        status: error.response?.status,
        url: error.config?.url // 어디로 요청을 보냈는지 확인용
      });
    }
  };

  if (loading) return <div style={{ padding: '20px' }}>로딩 중...</div>;

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h1 style={{ color: '#1a73e8', textAlign: 'center' }}>🚀 Core Platform Test Console</h1>

      <div style={{ padding: '20px', border: '1px solid #ddd', borderLeft: '4px solid #1a73e8', borderRadius: '8px', marginBottom: '20px', backgroundColor: '#fff' }}>
        <h3>1. Authentication</h3>
        {user ? (
          <div>
            <p>로그인됨: <strong>{user.email}</strong></p>
            <button onClick={handleLogout} style={{ padding: '10px 20px', backgroundColor: '#f1f3f4', border: '1px solid #dadce0', borderRadius: '4px', cursor: 'pointer' }}>로그아웃</button>
          </div>
        ) : (
          <button onClick={handleLogin} style={{ padding: '12px 24px', backgroundColor: '#4285f4', color: 'white', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}>
            Google 계정으로 로그인
          </button>
        )}
      </div>

      <div style={{ padding: '20px', border: '1px solid #ddd', borderLeft: '4px solid #34a853', borderRadius: '8px', backgroundColor: '#fff', marginBottom: '20px' }}>
        <h3>2. Backend API Test</h3>
        <p style={{ fontSize: '14px', color: '#666' }}>백엔드 서버(localhost:8000) 통신 테스트</p>
        <button 
          onClick={fetchMyInfo} 
          disabled={!user}
          style={{ 
            padding: '10px 20px', 
            backgroundColor: user ? '#34a853' : '#ccc', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: user ? 'pointer' : 'not-allowed',
            fontWeight: 'bold'
          }}
        >
          내 정보 확인 (/auth/me)
        </button>

        {apiResult && (
          <div style={{ marginTop: '20px' }}>
            <strong>API Response:</strong>
            <pre style={{ backgroundColor: '#202124', color: '#e8eaed', padding: '15px', borderRadius: '8px', overflowX: 'auto', fontSize: '13px' }}>
              {typeof apiResult === 'string' ? apiResult : JSON.stringify(apiResult, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div style={{ padding: '20px', border: '1px solid #ddd', borderLeft: '4px solid #fbbc04', borderRadius: '8px', backgroundColor: '#fff' }}>
        <h3>3. Premium Plans</h3>
        <p style={{ fontSize: '14px', color: '#666' }}>Polar.sh를 통한 요금제 구독 및 평생 라이선스 구매</p>
        <PricingSection user={user} />
      </div>
    </div>
  );
}

function PricingSection({ user }: { user: any }) {
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      api.get('/billing/plans').then(res => setPlans(res.data)).catch(err => console.error(err));
    }
  }, [user]);

  const handleCheckout = async (planCode: string) => {
    try {
      setLoading(true);
      const res = await api.post('/billing/checkout', {
        plan_code: planCode,
        success_url: window.location.origin + "?payment=success"
      });
      // Polar 결제창으로 이동
      window.location.href = res.data.url;
    } catch (err: any) {
      alert(err.response?.data?.detail || "결제 세션 생성 실패");
    } finally {
      setLoading(false);
    }
  };

  if (!user) return <p>로그인 후 요금제를 확인할 수 있습니다.</p>;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '20px' }}>
      {plans.map((plan) => (
        <div key={plan.id} style={{ border: '1px solid #eee', padding: '16px', borderRadius: '8px', textAlign: 'center', backgroundColor: '#fafafa' }}>
          <h4 style={{ margin: '0 0 8px 0' }}>{plan.display_name}</h4>
          <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '0 0 8px 0' }}>
            ${(plan.price_amount / 100).toFixed(2)}
            <span style={{ fontSize: '12px', color: '#888' }}>{plan.interval ? ` / ${plan.interval}` : ''}</span>
          </p>
          <ul style={{ textAlign: 'left', fontSize: '12px', paddingLeft: '20px', color: '#555' }}>
            <li>최대 {plan.max_devices}대 기기</li>
            <li>{plan.plan_code === 'lifetime' ? '영구 소장' : '구독 기간 내 사용'}</li>
          </ul>
          <button 
            disabled={loading || plan.plan_code === 'free'}
            onClick={() => handleCheckout(plan.plan_code)}
            style={{ 
              marginTop: '12px', 
              width: '100%', 
              padding: '8px', 
              backgroundColor: plan.plan_code === 'free' ? '#ccc' : '#fbbc04',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 'bold',
              cursor: plan.plan_code === 'free' ? 'default' : 'pointer'
            }}
          >
            {plan.plan_code === 'free' ? '기본 제공' : '선택하기'}
          </button>
        </div>
      ))}
    </div>
  );
}

export default App;
