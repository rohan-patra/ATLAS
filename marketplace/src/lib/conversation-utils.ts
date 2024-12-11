import { promises as fs } from "fs";
import path from "path";
import { parse } from "csv-parse/sync";
import { stringify } from "csv-stringify/sync";
import { randomUUID } from "crypto";
import type { Message } from "@/types/message";

const CONVERSATIONS_DIR = path.join(process.cwd(), "src/data/conversations");

// Ensure conversations directory exists
async function ensureConversationsDir() {
  try {
    await fs.mkdir(CONVERSATIONS_DIR, { recursive: true });
  } catch (error) {
    console.error("Error creating conversations directory:", error);
  }
}

interface CSVMessage {
  dateTime: string;
  content: string;
  sender: string;
  type: string;
  price?: string;
}

export async function createConversation(listingId: string): Promise<string> {
  await ensureConversationsDir();
  const conversationId = randomUUID();
  const filePath = path.join(CONVERSATIONS_DIR, `${conversationId}.csv`);
  
  // Create empty CSV with headers
  const headers = "dateTime,content,sender,type,price\n";
  await fs.writeFile(filePath, headers);
  
  return conversationId;
}

export async function getConversation(conversationId: string): Promise<Message[]> {
  try {
    const filePath = path.join(CONVERSATIONS_DIR, `${conversationId}.csv`);
    const fileContent = await fs.readFile(filePath, "utf-8");
    
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true,
    }) as CSVMessage[];

    return records.map((record): Message => {
      const baseMessage = {
        dateTime: new Date(record.dateTime),
        sender: record.sender as "buyer" | "seller",
      };

      if (record.type === "offer") {
        return {
          ...baseMessage,
          content: {
            type: "offer",
            price: parseFloat(record.price!),
          },
        };
      } else if (record.type === "accepted") {
        return {
          ...baseMessage,
          content: {
            type: "accepted",
            price: parseFloat(record.price!),
          },
        };
      } else {
        return {
          ...baseMessage,
          content: record.content,
        };
      }
    });
  } catch (error) {
    console.error("Error reading conversation:", error);
    return [];
  }
}

export async function addMessage(conversationId: string, message: Message): Promise<void> {
  const filePath = path.join(CONVERSATIONS_DIR, `${conversationId}.csv`);
  const messages = await getConversation(conversationId);
  
  const newRecord: CSVMessage = {
    dateTime: message.dateTime.toISOString(),
    sender: message.sender,
    type: typeof message.content === "string" ? "text" : message.content.type,
    content: typeof message.content === "string" 
      ? message.content 
      : "",
    price: typeof message.content === "string" 
      ? undefined 
      : message.content.price.toString(),
  };

  const allRecords = [...messages.map(msg => {
    const record: CSVMessage = {
      dateTime: msg.dateTime.toISOString(),
      sender: msg.sender,
      type: typeof msg.content === "string" ? "text" : msg.content.type,
      content: typeof msg.content === "string" ? msg.content : "",
      price: typeof msg.content === "string" 
        ? undefined 
        : msg.content.price.toString(),
    };
    return record;
  }), newRecord];

  const csv = stringify(allRecords, { 
    header: true,
    columns: ["dateTime", "content", "sender", "type", "price"],
  });
  
  await fs.writeFile(filePath, csv);
} 