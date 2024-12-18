import { addMessage, getConversation } from "@/lib/conversation-utils";
import { NextResponse } from "next/server";
import type { Message } from "@/types/message";

export async function GET(
  request: Request,
  { params }: { params: { id: string } },
) {
  try {
    const messages = await getConversation(params.id);
    return NextResponse.json(messages);
  } catch (error) {
    console.error("Error fetching messages:", error);
    return NextResponse.json(
      { error: "Failed to fetch messages" },
      { status: 500 },
    );
  }
}

export async function POST(
  request: Request,
  { params }: { params: { id: string } },
) {
  try {
    const message = await request.json() as Omit<Message, "dateTime">;
    const fullMessage: Message = {
      ...message,
      dateTime: new Date(),
    };

    await addMessage(params.id, fullMessage);
    return NextResponse.json(fullMessage, { status: 201 });
  } catch (error) {
    console.error("Error sending message:", error);
    return NextResponse.json(
      { error: "Failed to send message" },
      { status: 500 },
    );
  }
} 