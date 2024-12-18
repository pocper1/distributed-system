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
const user_start = 549;
const USER_IDS = Array.from({ length: 20 }, (_, i) => i + user_start); // 20 users

export function setup() {
    // 創建活動
    const now = new Date();
    const utcPlus8 = new Date(now.getTime() + 8 * 60 * 60 * 1000); // 加 8 小時

    let createEventRes = http.post(
        `${BASE_URL}/event/create`,
        JSON.stringify({
            name: `Event_${Math.random().toString(36).substring(7)}`,
            description: "Test Event",
            start_time: utcPlus8.toISOString(),
            end_time: new Date(utcPlus8.getTime() + 3600000).toISOString(),
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
    let joinRes = http.post(`${BASE_URL}/event/${eventId}/team/${createdTeamId}/join`, JSON.stringify({ user_id: userId }), {
        headers: { "Content-Type": "application/json" },
    });

    check(joinRes, {
        "User joined team successfully": res => res.status === 200,
        "User already a member": res => res.status === 400,
    });

    console.log(`User ${userId} join attempt for Team ${createdTeamId}: ${joinRes.status}`);
    console.log(`${joinRes.body}`);
    
    sleep(1); // 模擬等待
}
