import http from 'k6/http';

export const options = { scenarios: { cap: { executor: 'constant-vus', vus: 50, duration: '1m' } } };

export default function () { http.get('https://jsonplaceholder.typicode.com/posts'); }
