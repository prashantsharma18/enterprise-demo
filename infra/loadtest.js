import http from 'k6/http';
import { sleep } from 'k6';

export default function () {
  http.get('http://enterprise-demo-active:8080/');
  sleep(0.1);
}

export const options = {
  vus: 10,
  duration: '30s',
};