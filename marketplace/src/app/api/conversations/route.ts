import { createConversation } from "@/lib/conversation-utils";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const { listingId } = await request.json();
    if (!listingId) {
      return NextResponse.json(
        { error: "Listing ID is required" },
        { status: 400 },
      );
    }

    const conversationId = await createConversation(listingId);
    return NextResponse.json({ conversationId }, { status: 201 });
  } catch (error) {
    console.error("Error creating conversation:", error);
    return NextResponse.json(
      { error: "Failed to create conversation" },
      { status: 500 },
    );
  }
} 