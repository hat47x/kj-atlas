import assert from "node:assert/strict";

function parseArgs(argv) {
  const args = {
    writeBaseUrl: "http://127.0.0.1:8080/api",
    readBaseUrl: null,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--write-base-url") {
      args.writeBaseUrl = argv[++index];
    } else if (value === "--read-base-url") {
      args.readBaseUrl = argv[++index];
    } else {
      throw new Error(`unknown argument: ${value}`);
    }
  }
  args.readBaseUrl ??= args.writeBaseUrl;
  return args;
}

function normalizeBaseUrl(value) {
  if (!value) {
    throw new Error("base URL must not be empty");
  }
  return value.replace(/\/$/, "");
}

async function requireOk(response, operation) {
  if (response.ok) {
    return;
  }
  const detail = await response.text();
  throw new Error(`${operation} failed: HTTP ${response.status}: ${detail}`);
}

const args = parseArgs(process.argv.slice(2));
const writeBaseUrl = normalizeBaseUrl(args.writeBaseUrl);
const readBaseUrl = normalizeBaseUrl(args.readBaseUrl);
const docId = `doc_e2e_preflight_${Date.now()}_${process.pid}`;
const timestamp = new Date().toISOString();

// Keep this fixture aligned with the DocumentV1 shape already exercised by
// realistic_user_journey_expansion.spec.ts. The preflight intentionally uses
// only deterministic synthetic content; it never depends on seeded/user data.
const document = {
  version: 1,
  id: docId,
  title: "E2E storage preflight",
  createdAt: timestamp,
  updatedAt: timestamp,
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    {
      id: "preflight-card-1",
      text: "deterministic synthetic preflight card",
      x: 120,
      y: 120,
    },
  ],
  edges: [],
  islands: [],
};

const putUrl = `${writeBaseUrl}/docs/${encodeURIComponent(docId)}`;
const getUrl = `${readBaseUrl}/docs/${encodeURIComponent(docId)}`;

const putResponse = await fetch(putUrl, {
  method: "PUT",
  headers: { "content-type": "application/json" },
  body: JSON.stringify(document),
});
await requireOk(putResponse, "PUT document");
const putEtag = putResponse.headers.get("etag");
assert.ok(putEtag, "PUT response must include ETag");
const putPayload = await putResponse.json();
assert.equal(putPayload.id, docId, "PUT response document id must match the created id");

const getResponse = await fetch(getUrl);
await requireOk(getResponse, "GET document");
const getEtag = getResponse.headers.get("etag");
assert.ok(getEtag, "GET response must include ETag");
const getPayload = await getResponse.json();

assert.deepEqual(getPayload, putPayload, "GET must return the payload persisted by PUT");
assert.equal(getEtag, putEtag, "GET and PUT ETags must match for unchanged content");

console.log(
  JSON.stringify({
    status: "pass",
    docId,
    writeBaseUrl,
    readBaseUrl,
    etag: getEtag,
  }),
);
