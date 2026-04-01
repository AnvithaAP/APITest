import http from 'k6/http';

export const options = {
  scenarios: {
    ramp: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 20 },
        { duration: '30s', target: 50 },
        { duration: '30s', target: 0 },
      ],
    },
  },
};

export default function () { http.get('https://jsonplaceholder.typicode.com/comments'); }
