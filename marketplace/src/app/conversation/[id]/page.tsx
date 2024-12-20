import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import type { Message } from "@/types/message";

async function getMessages(conversationId: string) {
  const res = await fetch(
    `http://localhost:3000/api/conversations/${conversationId}/messages`,
    { cache: "no-store" },
  );
  if (!res.ok) return [];
  return res.json() as Promise<Message[]>;
}

function MessageBubble({ message }: { message: Message }) {
  const isOffer = typeof message.content !== "string";
  const isBuyer = message.sender === "buyer";
  const bubbleClass = `rounded-lg p-3 max-w-[80%] ${
    isBuyer ? "bg-blue-500 text-white ml-auto" : "bg-gray-200"
  }`;

  return (
    <div className={`mb-4 ${isBuyer ? "text-right" : "text-left"}`}>
      <div className={bubbleClass}>
        {isOffer ? (
          <div>
            <p className="font-semibold">
              {message.content.type === "offer"
                ? "New Offer:"
                : "Offer Accepted:"}
            </p>
            <p className="text-lg">${message.content.price.toFixed(2)}</p>
          </div>
        ) : (
          <p>{message.content}</p>
        )}
        <p className="mt-1 text-xs opacity-70">
          {formatDistanceToNow(message.dateTime, { addSuffix: true })}
        </p>
      </div>
    </div>
  );
}

export default async function ConversationPage({
  params,
}: {
  params: { id: string };
}) {
  const { id: conversationId } = await params;
  const messages = await getMessages(conversationId);

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="mx-auto max-w-2xl">
        <Link
          href="/"
          className="mb-6 inline-block text-blue-600 hover:text-blue-800"
        >
          ← Back to Listings
        </Link>

        <Card>
          <CardHeader>
            <CardTitle>Conversation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-6 max-h-[600px] overflow-y-auto">
              {messages.map((message, index) => (
                <MessageBubble key={index} message={message} />
              ))}
            </div>

            <form
              action={async (formData: FormData) => {
                "use server";

                const content = formData.get("message") as string;
                const type = formData.get("type") as string;
                const price = formData.get("price") as string;

                let messageContent: string | { type: "offer"; price: number };
                if (type === "offer" && price) {
                  messageContent = {
                    type: "offer",
                    price: parseFloat(price),
                  };
                } else {
                  messageContent = content;
                }

                await fetch(
                  `http://localhost:3000/api/conversations/${params.id}/messages`,
                  {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                      content: messageContent,
                      sender: "buyer", // For now, hardcode as buyer
                    }),
                  },
                );
              }}
            >
              <div className="flex gap-2">
                <Input
                  type="text"
                  name="message"
                  placeholder="Type a message..."
                  className="flex-1"
                />
                <Button type="submit">Send</Button>
              </div>
              <div className="mt-4 flex gap-2">
                <Input
                  type="number"
                  name="price"
                  placeholder="Offer amount..."
                  step="0.01"
                  min="0"
                />
                <input type="hidden" name="type" value="offer" />
                <Button type="submit" variant="secondary">
                  Make Offer
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
