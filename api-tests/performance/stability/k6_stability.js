import http from 'k6/http';

export const options = { vus: 20, duration: '10m' };

export default function () { http.get('https://jsonplaceholder.typicode.com/albums'); }
