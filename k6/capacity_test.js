import http from "k6/http";
import { check } from "k6";

export let options = {
    scenarios: {
        capacity_test: {
            executor: "ramping-arrival-rate",
            startRate: 10, // 每秒起始 10 個請求
            timeUnit: "1s",
            stages: [
                { target: 50, duration: "2m" }, // 2 分鐘內增加到每秒 50 個請求
                { target: 100, duration: "3m" }, // 接下來 3 分鐘增加到每秒 100 個請求
                { target: 200, duration: "5m" }, // 最後 5 分鐘增加到每秒 200 個請求
            ],
            preAllocatedVUs: 200,
            maxVUs: 400, // 最大 400 虛擬用戶
        },
    },
    thresholds: {
        http_req_duration: ["p(95)<500"], // 95% 的請求在 500 毫秒內完成
    },
};

const BASE_URL = "http://localhost/api";

export default function () {
    let res = http.get(`${BASE_URL}/test-endpoint`);
    check(res, {
        "Response status is 200": (r) => r.status === 200,
    });
}
