import http from "k6/http";
import { check } from "k6";

export let options = {
    scenarios: {
        stability_test: {
            executor: "constant-arrival-rate",
            rate: 100, // 每秒固定 100 個請求
            timeUnit: "1s",
            duration: "10m", // 測試持續 10 分鐘
            preAllocatedVUs: 100, // 預分配 100 虛擬用戶
            maxVUs: 200, // 最大 200 虛擬用戶
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
