import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(50)<200', 'p(95)<500', 'p(99)<1000'],
  },
};

export default function () {
  const res = http.get('https://jsonplaceholder.typicode.com/users');
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
