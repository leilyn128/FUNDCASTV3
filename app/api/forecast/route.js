export async function GET() {
  const res = await fetch("http://192.168.100.180:8000/forecast", {
    cache: "no-store"
  });

  if (!res.ok) {
    return new Response(
      JSON.stringify({ error: "Failed to fetch forecast" }),
      { status: 500 }
    );
  }

  const data = await res.json();
  return Response.json(data);
}