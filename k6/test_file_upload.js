import http from "k6/http";
import { check, sleep } from "k6";

export let options = {
    setupTimeout: "10m",
    scenarios: {
        file_upload: {
            executor: "ramping-arrival-rate",
            startRate: 1,
            timeUnit: "1s",
            preAllocatedVUs: 100,
            maxVUs: 500,
            stages: [
                { target: 100, duration: "2m" },
                { target: 300, duration: "3m" },
                { target: 500, duration: "2m" },
            ],
        },
    },
};

const BASE_URL = "http://localhost/api";
const USERS_COUNT = 1000;

// 初始化階段：創建用戶數組
export function setup() {
    let users = [];
    for (let i = 0; i < USERS_COUNT; i++) {
        users.push({
            id: i,
            username: `user_${i}`,
        });
    }
    return { users };
}

// 主函數：輪流上傳文件
export default function (data) {
    const { users } = data;

    // 隨機選擇一個用戶
    const user = users[Math.floor(Math.random() * users.length)];
    const fileContent = "This is a test file content.";
    const encodedFile = btoa(fileContent);

    let res = http.post(
        `${BASE_URL}/upload`,
        JSON.stringify({
            user_id: user.id,
            file_name: `${user.username}_file.txt`,
            file_content: encodedFile,
        }),
        { headers: { "Content-Type": "application/json" } }
    );

    check(res, {
        "File uploaded successfully": (r) => r.status === 200,
    });

    sleep(1); // 模擬延遲
}
