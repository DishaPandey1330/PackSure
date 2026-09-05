export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "*");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const backendHost = process.env.BACKEND_URL || "https://config-extremely-magnificent-conference.trycloudflare.com";
  const targetUrl = `${backendHost.replace(/\/$/, "")}/api/scan`;

  try {
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        "content-type": req.headers["content-type"] || "",
        "Bypass-Tunnel-Remainder": "true",
      },
      body: req.method === "POST" ? req : undefined,
      duplex: "half",
    });

    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const data = await response.json();
      return res.status(response.status).json(data);
    } else {
      const text = await response.text();
      return res.status(response.status).json({ error: `Backend non-JSON response: ${text.slice(0, 200)}` });
    }
  } catch (error) {
    return res.status(500).json({ error: `Vercel Proxy Error: ${error.message}` });
  }
}
