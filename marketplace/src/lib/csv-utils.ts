import { promises as fs } from "fs";
import path from "path";
import { parse } from "csv-parse/sync";
// import { stringify } from "csv-stringify/sync";
import type { Listing } from "@/types/listing";

const csvFilePath = path.join(process.cwd(), "src/data/listings.csv");

interface CSVRecord {
  id: string;
  title: string;
  description: string;
  price: string;
  location: string;
  imageUrl: string;
  datePosted: string;
  sellerName: string;
}

export async function getListings(): Promise<Listing[]> {
  try {
    const fileContent = await fs.readFile(csvFilePath, "utf-8");
    // eslint-disable-next-line @typescript-eslint/no-unsafe-call
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true,
    }) as CSVRecord[];

    return records.map((record) => ({
      ...record,
      price: parseFloat(record.price),
    }));
  } catch (error) {
    console.error("Error reading listings:", error);
    return [];
  }
}

export async function getListing(id: string): Promise<Listing | null> {
  const listings = await getListings();
  return listings.find((listing) => listing.id === id) ?? null;
}

// export async function addListing(listing: Omit<Listing, 'id' | 'datePosted'>): Promise<Listing> {
//   const listings = await getListings();
//   const newListing: Listing = {
//     ...listing,
//     id: (listings.length + 1).toString(),
//     datePosted: new Date().toISOString().split('T')[0]
//   };

//   const newListings = [...listings, newListing];
//   const csv = stringify(newListings, { header: true });
//   await fs.writeFile(csvFilePath, csv);

//   return newListing;
// }
