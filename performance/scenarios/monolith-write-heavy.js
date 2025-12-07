import http from "k6/http";
import { check, group, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const HEADERS = { "Content-Type": "application/json" };

export const options = {
  stages: [
    { duration: "20s", target: 6 },
    { duration: "50s", target: 6 },
    { duration: "20s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<1500"],
    checks: ["rate>0.9"],
  },
  summaryTrendStats: ["avg", "min", "med", "p(90)", "p(95)", "p(99)"],
  setupTimeout: "120s",
};

function employeePayload() {
  const suffix = Math.random().toString(16).slice(2, 8);
  return {
    name: `Name-${suffix}`,
    lastname: `Lastname-${suffix}`,
    salary: 48000 + Math.floor(Math.random() * 20000),
    address: `Street ${Math.floor(Math.random() * 500)}`,
    in_vacation: Math.random() > 0.8,
  };
}

export function setup() {
  const seeded = [];
  for (let i = 0; i < 8; i += 1) {
    const res = http.post(
      `${BASE_URL}/employees`,
      JSON.stringify(employeePayload()),
      { headers: HEADERS }
    );
    if (res.status === 201) {
      seeded.push(res.json().id);
    }
  }
  return { seeded };
}

export default function (data) {
  const createPayload = employeePayload();

  group("create employee", () => {
    const res = http.post(
      `${BASE_URL}/employees`,
      JSON.stringify(createPayload),
      { headers: HEADERS }
    );
    check(res, {
      "employee created": (r) => r.status === 201,
      "payload echoed": (r) => r.json("name") === createPayload.name,
    });

    if (res.status === 201) {
      const createdId = res.json("id");
      const updatedPayload = { ...createPayload, salary: createPayload.salary + 1500 };

      group("update employee", () => {
        const updateRes = http.put(
          `${BASE_URL}/employees/${createdId}`,
          JSON.stringify(updatedPayload),
          { headers: HEADERS }
        );
        check(updateRes, {
          "employee updated": (r) => r.status === 200,
          "salary updated": (r) => r.json("salary") === updatedPayload.salary,
        });
      });
    }
  });

  if (data.seeded.length) {
    const randomId =
      data.seeded[Math.floor(Math.random() * data.seeded.length)];
    group("touch existing employee", () => {
      const payload = { ...employeePayload(), in_vacation: true };
      const res = http.put(
        `${BASE_URL}/employees/${randomId}`,
        JSON.stringify(payload),
        { headers: HEADERS }
      );
      check(res, {
        "existing updated": (r) => r.status === 200 || r.status === 404,
      });
    });
  }

  sleep(1);
}
