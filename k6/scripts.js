import http from "k6/http";
import { check, sleep } from "k6";
import { b64encode } from "k6/encoding";

// 配置選項
export let options = {
    setupTimeout: "5m",
    scenarios: {
        stress_test: {
            executor: "ramping-arrival-rate",
            startRate: 1,
            timeUnit: "1s",
            preAllocatedVUs: 50,
            maxVUs: 200,
            stages: [
                { target: 100, duration: "1m" },
                { target: 250, duration: "30s" },
                { target: 500, duration: "60s" },
            ],
        },
    },
    thresholds: {
        http_req_duration: ["p(95)<500"], // 95% 的請求在 500 毫秒內完成
    },
};

const BASE_URL = "https://backend-service-72785805306.asia-east1.run.app/api";

// 固定範圍的用戶 ID
const user_start = 429;
const USER_IDS = Array.from({ length: 20 }, (_, i) => i + user_start); // 20 users

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

    // 建立隊伍
    const TEAMS_TO_CREATE = 20;

    for (let i = 0; i < TEAMS_TO_CREATE; i++) {
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

        // 上傳多筆檢錄
        const UPLOAD_COUNT = 5; // 每個隊伍上傳 5 次

        for (let j = 0; j < UPLOAD_COUNT; j++) {
            const userId = USER_IDS[Math.floor(Math.random() * USER_IDS.length)];

            const dummyPhoto = b64encode("dummy image data"); // 模擬 Base64 照片數據
            let uploadRes = http.post(
                `${BASE_URL}/event/${eventId}/upload`,
                JSON.stringify({
                    user_id: userId,
                    comment: `Check-in comment ${j + 1} for Team ${createdTeamId}`,
                    photo: dummyPhoto,
                }),
                {
                    headers: { "Content-Type": "application/json" },
                }
            );

            check(uploadRes, {
                "Photo uploaded successfully": res => res.status === 200,
            });

            console.log(
                `Upload ${j + 1} completed for User ${userId} in Team ${createdTeamId}`
            );

            sleep(1); // 模擬上傳完成後的等待時間
        }
    }
}