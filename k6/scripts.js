import http from "k6/http";
import { check, sleep } from "k6";
import { b64encode } from "k6/encoding";

// 配置選項
export let options = {
    setupTimeout: "5m",
    cloud: {
        // Project: checkin
        projectID: 3730775,
        // Test runs with the same name groups test runs together.
        name: 'Test (19/12/2024-15:33:59)'
    },
    scenarios: {
        stress_test: {
            executor: "ramping-arrival-rate",
            startRate: 1,
            timeUnit: "1s",
            preAllocatedVUs: 50,
            maxVUs: 100,
            stages: [
                { target: 50, duration: "30s" },
                { target: 100, duration: "45s" },
                { target: 400, duration: "60s" },
            ],
        },
    },
    thresholds: {
        http_req_duration: ["p(95)<500"], // 95% 的請求在 500 毫秒內完成
    },
};

const BASE_URL = "https://backend-service-72785805306.asia-east1.run.app/api";

// 固定範圍的用戶 ID
const user_start = 500;
const USER_IDS = Array.from({ length: 20 }, (_, i) => i + user_start); // 20 users

export function setup() {
    // 創建活動
    const now = new Date(); // 獲取當前 UTC 時間
    const startTimeUTC = now.toISOString(); // 活動開始時間 (UTC)
    const endTimeUTC = new Date(now.getTime() + 3600000).toISOString(); // 活動結束時間 (UTC, 加 1 小時)

    let createEventRes = http.post(
        `${BASE_URL}/event/create`,
        JSON.stringify({
            name: `Event_${Math.random().toString(36).substring(7)}`,
            description: "Test Event",
            start_time: startTimeUTC,
            end_time: endTimeUTC,
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

    // 創建隊伍
    const TEAM_NAME = `Team_${Math.random().toString(36).substring(7)}`;
    let createTeamRes = http.post(
        `${BASE_URL}/event/${eventId}/team/create`,
        JSON.stringify({
            name: TEAM_NAME,
            description: "Test Team",
        }),
        {
            headers: { "Content-Type": "application/json" },
        }
    );

    // 檢查返回值
    const responseJson = createTeamRes.json();
    const createdTeamId = responseJson.team_id;

    if (!createdTeamId) {
        throw new Error(`Failed to create team: ${JSON.stringify(responseJson)}`);
    }

    console.log(`Team created successfully with ID: ${createdTeamId}`);

    // 加入隊伍
    const userId = USER_IDS[Math.floor(Math.random() * USER_IDS.length)];
    let joinRes = http.post(`${BASE_URL}/event/${eventId}/teams/join`, JSON.stringify({ user_id: userId, team_id: createdTeamId }), {
        headers: { "Content-Type": "application/json" },
    });

    check(joinRes, {
        "User joined team successfully": res => res.status === 200
    });

    console.log(`User ${userId} join attempt for Team ${createdTeamId}: ${joinRes.status}`);

    // 上傳打卡
    const COMMENT = `Test Comment ${Math.random().toString(36).substring(7)}`;
    const PHOTO = b64encode("This is a test photo content"); // 模擬 Base64 照片

    let uploadRes = http.post(
        `${BASE_URL}/event/${eventId}/upload`,
        JSON.stringify({
            user_id: userId,
            comment: COMMENT,
            photo: PHOTO,
        }),
        {
            headers: { "Content-Type": "application/json" },
        }
    );

    check(uploadRes, {
        "Check-in uploaded successfully": res => res.status === 200,
    });

    sleep(1); // 模擬等待
}
