export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "*");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const backendHost = process.env.BACKEND_URL || "https://config-extremely-magnificent-conference.trycloudflare.com";
  const targetUrl = `${backendHost.replace(/\/$/, "")}/api/history`;

  try {
    const response = await fetch(targetUrl, {
      headers: { "Bypass-Tunnel-Remainder": "true" },
    });
    if (response.ok) {
      const data = await response.json();
      return res.status(200).json(data);
    }
    return res.status(200).json([]);
  } catch {
    return res.status(200).json([]);
  }
}
