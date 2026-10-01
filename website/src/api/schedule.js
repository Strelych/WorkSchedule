import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000/api/web',
})

export function getSchedule(year, month) {
  return client.get('/schedule', {
    params: { year, month },
    headers: { 'X-Access-Token': sessionStorage.getItem('valet-access-token') || '' },
  })
}

export function getStats(year, month) {
  return client.get('/stats', {
    params: { year, month },
    headers: { 'X-Access-Token': sessionStorage.getItem('valet-access-token') || '' },
  })
}

export function getEmployees() {
  return client.get('/employees', {
    headers: { 'X-Access-Token': sessionStorage.getItem('valet-access-token') || '' },
  })
}
