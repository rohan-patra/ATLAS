import { getListings } from "@/lib/csv-utils";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const listings = await getListings();
    return NextResponse.json(listings);
  } catch (error) {
    console.error("Error fetching listings:", error);
    return NextResponse.json(
      { error: "Failed to fetch listings" },
      { status: 500 },
    );
  }
}

// export async function POST(request: Request) {
//   try {
//     const body = await request.json();
//     const newListing = await addListing(body);
//     return NextResponse.json(newListing, { status: 201 });
//   } catch (error) {
//     return NextResponse.json({ error: 'Failed to create listing' }, { status: 500 });
//   }
// }
