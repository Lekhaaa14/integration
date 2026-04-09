const axios = require('axios');

const BASE_URL = 'http://localhost:3000';

// Resource options for each log type
const employeeResources = ['/db/orders', '/db/users', '/api/products'];
const vendorResources = ['/api/admin', '/customer-data', '/vendor-api'];
const aiResources = ['/ml-data', '/analytics', '/customer-data'];

// Helper function to get random element from array
function getRandomElement(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// Helper function to generate random timestamp in last 30 days
function getRandomTimestamp() {
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const randomTime = thirtyDaysAgo.getTime() + Math.random() * (now.getTime() - thirtyDaysAgo.getTime());
  return new Date(randomTime);
}

// Helper function to check if time is outside working hours
function isOutsideWorkingHours(date) {
  const hour = date.getHours();
  return hour < 9 || hour >= 17;
}

// Generate employee log (400 total)
function generateEmployeeLog() {
  const timestamp = getRandomTimestamp();
  return {
    user_id: `emp_${Math.floor(Math.random() * 1000)}`,
    role: getRandomElement(['admin', 'analyst']),
    resource: getRandomElement(employeeResources),
    action: 'read',
    source: 'web_app',
    timestamp: timestamp.toISOString()
  };
}

// Generate vendor log (400 total)
function generateVendorLog() {
  const timestamp = getRandomTimestamp();
  return {
    user_id: `vendor_${Math.floor(Math.random() * 500)}`,
    role: 'vendor',
    resource: getRandomElement(vendorResources),
    action: 'read',
    source: 'vendor_api',
    timestamp: timestamp.toISOString()
  };
}

// Generate AI system log (200 total)
function generateAISystemLog() {
  const timestamp = getRandomTimestamp();
  return {
    user_id: 'ai_system',
    role: 'ai-system',
    resource: getRandomElement(aiResources),
    action: 'read',
    source: 'ml_pipeline',
    timestamp: timestamp.toISOString()
  };
}

// Main function to send all logs
async function sendLogs() {
  let count = 0;

  try {
    // Send 400 employee logs
    for (let i = 0; i < 400; i++) {
      const log = generateEmployeeLog();
      await axios.post(`${BASE_URL}/logs`, log);
      count++;
      if (count % 100 === 0) {
        console.log(`Progress: sent ${count} logs`);
      }
    }

    // Send 400 vendor logs
    for (let i = 0; i < 400; i++) {
      const log = generateVendorLog();
      await axios.post(`${BASE_URL}/logs`, log);
      count++;
      if (count % 100 === 0) {
        console.log(`Progress: sent ${count} logs`);
      }
    }

    // Send 200 AI system logs
    for (let i = 0; i < 200; i++) {
      const log = generateAISystemLog();
      await axios.post(`${BASE_URL}/logs`, log);
      count++;
      if (count % 100 === 0) {
        console.log(`Progress: sent ${count} logs`);
      }
    }

    console.log('Done sending 1000 logs');
  } catch (error) {
    console.error('Error sending logs:', error.message);
    process.exit(1);
  }
}

sendLogs();
