import http from 'k6/http';
import { sleep } from 'k6';
import { check } from 'k6';

export const options = {
    stages: [
        { duration: '1m', target: 50 },  // 起始輕負載
        { duration: '3m', target: 200 }, // 中等負載
        { duration: '2m', target: 500 }, // 高負載
        { duration: '2m', target: 1000 }, // 尖峰負載
    ],
};

export default function () {
    const url = 'http://<API_URL>/upload_checkin';
    const payload = JSON.stringify({
        team_id: Math.floor(Math.random() * 1000), // 隨機團隊ID
        member_id: Math.floor(Math.random() * 5000), // 隨機會員ID
        timestamp: new Date().toISOString(),
        is_new_member: Math.random() < 0.3, // 30% 機率為新會員
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const res = http.post(url, payload, params);
    check(res, { 'status was 200': (r) => r.status === 200 });
    sleep(1);
}
