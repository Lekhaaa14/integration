require('dotenv').config();
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());
const LEKHA_URL = process.env.LEKHA_URL || 'http://localhost:3000';
const PORT = process.env.PORT || 4000;
const mock = (log) => ({
  purpose: log.role === 'vendor' ? 'VENDOR' : log.role === 'ai-system' ? 'AI' : 'OPERATIONAL',
  risk_score: log.anomaly_flag ? 85 : log.role === 'vendor' ? 65 : 20,
  policy_violation: log.role === 'vendor' && ['/customer-data','/api/admin'].includes(log.resource),
  violated_rule: log.role === 'vendor' && ['/customer-data','/api/admin'].includes(log.resource) ? 'Vendor accessing PII' : null,
  reason: `Risk assessed for role: ${log.role}, resource: ${log.resource}`
});
app.get('/health', (req, res) => res.json({ status: 'integration layer running', mock_mode: true }));
app.post('/demo-pipeline', async (req, res) => {
  try {
    const step1 = await axios.post(`${LEKHA_URL}/logs`, req.body);
    const saved = step1.data.log || step1.data;
    const step2 = mock(saved);
    res.json({ step1_ingested: saved, step2_analyzed: step2, final: { user_id: saved.user_id, resource: saved.resource, anomaly_flag: saved.anomaly_flag, ...step2 }});
  } catch(e) { res.status(500).json({ error: e.message }); }
});
app.get('/access-intelligence', async (req, res) => {
  try {
    const r = await axios.get(`${LEKHA_URL}/logs?limit=20`);
    const logs = r.data.logs || r.data || [];
    res.json(logs.map(l => ({ user_id: l.user_id, role: l.role, resource: l.resource, anomaly_flag: l.anomaly_flag, ...mock(l) })));
  } catch(e) { res.status(500).json({ error: e.message }); }
});
app.get('/dashboard-summary', async (req, res) => {
  try {
    const r = await axios.get(`${LEKHA_URL}/logs?limit=1000`);
    const logs = r.data.logs || r.data || [];
    res.json({ total_logs: logs.length, anomalies: logs.filter(l => l.anomaly_flag).length, vendor_logs: logs.filter(l => l.role === 'vendor').length, high_risk: logs.filter(l => l.anomaly_flag && l.role === 'vendor').length });
  } catch(e) { res.status(500).json({ error: e.message }); }
});
app.get('/user-intelligence/:user_id', async (req, res) => {
  try {
    const r = await axios.get(`${LEKHA_URL}/logs?user_id=${req.params.user_id}`);
    const logs = r.data.logs || r.data || [];
    res.json({ user_id: req.params.user_id, total_logs: logs.length, anomalies: logs.filter(l => l.anomaly_flag).length, logs });
  } catch(e) { res.status(500).json({ error: e.message }); }
});
app.listen(PORT, () => console.log('Integration server running on port ' + PORT));
