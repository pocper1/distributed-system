import http from "k6/http";
import { check, sleep } from "k6";

// 配置選項
export let options = {
    setupTimeout: "5m",
    scenarios: {
        stress_test: {
            executor: "ramping-arrival-rate",
            startRate: 1000,
            timeUnit: "1s",
            preAllocatedVUs: 2000,
            maxVUs: 5000,
            stages: [
                { target: 2000, duration: "1m" },
                { target: 5000, duration: "1m" },
                { target: 10000, duration: "1m" },
            ],
        },
    },
    thresholds: {
        http_req_duration: ["p(95)<500"], // 95% 的請求在 500 毫秒內完成
    },
};

const BASE_URL = "http://localhost:8000/api";

// 固定範圍的用戶 ID
const USER_IDS = Array.from({ length: 20 }, (_, i) => i + 86); // 用戶 ID 為 86 到 103

export function setup() {
    // 創建用戶
    USER_IDS.forEach(userId => {
        const username = `user_${userId}`;
        const response = http.post(
            `${BASE_URL}/user/register`,
            JSON.stringify({
                username: username,
                email: username + "@gmail.com",
                password: "password123", // 假設簡單的默認密碼
            }),
            {
                headers: { "Content-Type": "application/json" },
            }
        );

        check(response, {
            [`User ${username} created`]: res => res.status === 200 || res.status === 409, // 409 表示用戶已存在
        });

        if (response.status !== 200 && response.status !== 409) {
            throw new Error(`Failed to create user ${username}: ${response.body}`);
        }
    });

    console.log("All users created successfully.");

    // 創建活動
    const now = new Date();
    const utcPlus8 = new Date(now.getTime() + 8 * 60 * 60 * 1000); // 加 8 小時

    let createEventRes = http.post(
        `${BASE_URL}/event/create`,
        JSON.stringify({
            name: `Event_${Math.random().toString(36).substring(7)}`,
            description: "Test Event",
            start_time: utcPlus8.toISOString(), // 開始時間為 UTC+8
            end_time: new Date(utcPlus8.getTime() + 3600000).toISOString(), // 活動持續 1 小時
        }),
        {
            headers: { "Content-Type": "application/json" },
        }
    );

    check(createEventRes, {
        "Event created successfully": res => res.status === 200,
    });

    const responseBody = createEventRes.json();
    const eventId = responseBody.event_id;

    if (!eventId) {
        throw new Error("Failed to create event: Event ID not returned.");
    }

    console.log(`Event created successfully with ID: ${eventId}`);
    return { eventId };
}

export default function (data) {
    const eventId = data.eventId;

    // 隨機選擇一個用戶
    const userId = USER_IDS[Math.floor(Math.random() * USER_IDS.length)];

    // 創建隊伍
    let createTeamRes = http.post(
        `${BASE_URL}/event/${eventId}/team/create`,
        JSON.stringify({
            name: `Team_${Math.random().toString(36).substring(7)}`,
            description: "Test Team",
        }),
        {
            headers: { "Content-Type": "application/json" },
        }
    );

    check(createTeamRes, {
        "Team created successfully": res => res.status === 200,
    });

    const createdTeamId = createTeamRes.json("team_id");
    if (!createdTeamId) {
        throw new Error("Failed to create team: Team ID not returned.");
    }

    console.log(`Team created successfully with ID: ${createdTeamId}`);

    sleep(1); // 模擬創建隊伍後的等待時間

    // 加入隊伍
    let joinTeamRes = http.post(
        `${BASE_URL}/event/${eventId}/teams/join`,
        JSON.stringify({
            user_id: userId,
            team_id: createdTeamId,
        }),
        {
            headers: { "Content-Type": "application/json" },
        }
    );

    check(joinTeamRes, {
        "User joined team successfully": res => res.status === 200,
    });

    console.log(`User ${userId} joined Team ${createdTeamId}`);

    sleep(1); // 模擬用戶加入隊伍後的等待時間

    // 上傳照片到活動
    const dummyPhoto = Buffer.from("dummy image data").toString("base64"); // 模擬 Base64 照片數據
    let uploadRes = http.post(
        `${BASE_URL}/event/${eventId}/upload`,
        JSON.stringify({
            user_id: userId,
            comment: `Check-in comment for Team ${createdTeamId}`,
            photo: dummyPhoto,
        }),
        {
            headers: { "Content-Type": "application/json" },
        }
    );

    check(uploadRes, {
        "Photo uploaded successfully": res => res.status === 200,
    });

    console.log(`Photo uploaded successfully for User ${userId} in Event ${eventId}`);
    sleep(1); // 模擬上傳完成後的等待時間
}
