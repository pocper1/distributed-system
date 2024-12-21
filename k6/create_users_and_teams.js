import http from "k6/http";
import { check, sleep } from "k6";

// Configuration Options
export let options = {
    setupTimeout: "10m",
    scenarios: {
        create_entities: {
            executor: "ramping-arrival-rate",
            startRate: 1,
            timeUnit: "1s",
            preAllocatedVUs: 100,
            maxVUs: 500,
            stages: [
                { target: 100, duration: "1m" },
                { target: 300, duration: "2m" },
                { target: 500, duration: "3m" },
            ],
        },
    },
};

const BASE_URL = "http://localhost/api";
const HEADERS = { "Content-Type": "application/json" };
const USERS_COUNT = 1000;
const TEAMS_COUNT = 2000;

// Function to create users
function createUsers() {
    let userIds = [];
    for (let i = 0; i < USERS_COUNT; i++) {
        let res = http.post(
            `${BASE_URL}/user/register`,
            JSON.stringify({
                username: `user_${i}`,
                password: "password123",
                email: `user_${i}@example.com`,
            }),
            { headers: HEADERS }
        );

        const success = check(res, {
            "Status is 200": (r) => r.status === 200,
        });

        if (success) {
            try {
                const responseBody = res.json();
                if (responseBody.task_id) {
                    userIds.push(responseBody.task_id);
                    console.log(`User registration initiated: Task ID = ${responseBody.task_id}`);
                } else {
                    console.error("Unexpected response:", responseBody);
                }
            } catch (err) {
                console.error("JSON parsing failed:", res.body);
            }
        } else {
            console.error("User creation failed:", res.body);
        }

        sleep(0.1);
    }
    return userIds;
}

// Function to create teams and let users join
function createTeamsAndJoinUsers(eventId, userIds) {
    let teamIds = [];
    for (let i = 0; i < TEAMS_COUNT; i++) {
        let res = http.post(
            `${BASE_URL}/event/${eventId}/team/create`,
            JSON.stringify({
                name: `team_${i}`,
                description: `Team number ${i}`,
            }),
            { headers: HEADERS }
        );

        const success = check(res, {
            "Team creation status is 200": (r) => r.status === 200,
        });

        if (success) {
            try {
                let teamId = res.json().team_id;
                if (teamId) {
                    teamIds.push(teamId);

                    const randomUserId = userIds[Math.floor(Math.random() * userIds.length)];
                    let joinRes = http.post(
                        `${BASE_URL}/event/${eventId}/team/${teamId}/join`,
                        JSON.stringify({ user_id: randomUserId }),
                        { headers: HEADERS }
                    );

                    check(joinRes, {
                        "User joined team successfully": (r) => r.status === 200,
                    });

                    console.log(`User ${randomUserId} joined Team ${teamId}`);
                } else {
                    console.error(`Failed to create team: ${res.body}`);
                }
            } catch (err) {
                console.error("JSON parsing failed for team creation:", res.body);
            }
        } else {
            console.error("Team creation failed:", res.body);
        }

        sleep(0.1);
    }
    return teamIds;
}

// Setup Phase
export function setup() {
    const now = new Date();
    const oneHourLater = new Date(now.getTime() + 3600000); // Add one hour

    // Initiate event creation
    let eventRes = http.post(
        `${BASE_URL}/event/create`,
        JSON.stringify({
            name: `Event_${Date.now()}`,
            description: "Test Event",
            start_time: now.toISOString(), // Ensure ISO format with UTC timezone
            end_time: oneHourLater.toISOString(),
        }),
        { headers: HEADERS }
    );

    console.log(`Event creation response: ${eventRes.body}`);

    // Check if the event creation request was successful
    check(eventRes, {
        "Event creation request succeeded": (r) => r.status === 200,
    });

    let taskId;
    try {
        const responseBody = eventRes.json();
        taskId = responseBody.task_id;
    } catch (err) {
        throw new Error(`Failed to parse event creation response: ${eventRes.body}`);
    }

    if (!taskId) {
        console.error("Event creation failed. Response body:", eventRes.body);
        throw new Error("Task ID not returned.");
    }

    console.log(`Event creation task initiated with Task ID: ${taskId}`);

    // Polling to get the event_id after task completion
    let eventId = null;
    const maxRetries = 30; // Maximum number of polling attempts
    const retryDelay = 2;   // Seconds between retries

    for (let i = 0; i < maxRetries; i++) {
        sleep(retryDelay); // Wait before polling

        let statusRes = http.get(`${BASE_URL}/event/status/${taskId}`, { headers: HEADERS });

        check(statusRes, {
            "Status endpoint request succeeded": (r) => r.status === 200,
        });

        try {
            const statusBody = statusRes.json();
            if (statusBody.status === "SUCCESS" && statusBody.result && statusBody.result.event_id) {
                eventId = statusBody.result.event_id;
                console.log(`Event created successfully with ID: ${eventId}`);
                break;
            } else if (statusBody.status === "FAILURE") {
                throw new Error(`Task failed with error: ${statusBody.error}`);
            } else {
                console.log(`Task status: ${statusBody.status}. Waiting for completion...`);
            }
        } catch (err) {
            console.error(`Error parsing status response: ${statusRes.body}`);
        }
    }

    if (!eventId) {
        throw new Error("Failed to retrieve Event ID after polling.");
    }

    // Proceed to create users and teams
    const userIds = createUsers();
    const teamIds = createTeamsAndJoinUsers(eventId, userIds);

    return { eventId, userIds, teamIds };
}

// Main Function: Simulate Execution Tasks
export default function (data) {
    const { eventId, userIds, teamIds } = data;

    // Randomly select a user and a team to join
    const randomUserId = userIds[Math.floor(Math.random() * userIds.length)];
    const randomTeamId = teamIds[Math.floor(Math.random() * teamIds.length)];

    let res = http.post(
        `${BASE_URL}/event/${eventId}/teams/join`,
        JSON.stringify({
            user_id: randomUserId,
            team_id: randomTeamId,
        }),
        { headers: HEADERS }
    );

    check(res, {
        "Submission successful": (r) => r.status === 200,
    });

    sleep(1); // Wait before the next iteration
}
