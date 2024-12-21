import http from "k6/http";
import { check } from "k6";

export let options = {
    scenarios: {
        stress_test: {
            executor: "ramping-arrival-rate",
            startRate: 50, // 每秒起始 50 個請求
            timeUnit: "1s",
            stages: [
                { target: 200, duration: "2m" }, // 2 分鐘內增加到每秒 200 個請求
                { target: 500, duration: "3m" }, // 接下來 3 分鐘增加到每秒 500 個請求
                { target: 1000, duration: "5m" }, // 最後 5 分鐘增加到每秒 1000 個請求
            ],
            preAllocatedVUs: 500,
            maxVUs: 1000, // 最大 1000 虛擬用戶
        },
    },
    thresholds: {
        http_req_duration: ["p(95)<1000"], // 95% 的請求在 1000 毫秒內完成
    },
};

const BASE_URL = "http://localhost/api";

export default function () {
    let res = http.get(`${BASE_URL}/test-endpoint`);
    check(res, {
        "Response status is 200": (r) => r.status === 200,
    });
}
