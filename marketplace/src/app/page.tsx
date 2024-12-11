import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Image from "next/image";
import Link from "next/link";
import type { Listing } from "@/types/listing";
import { formatDistanceToNow } from "date-fns";

async function getListings() {
  const res = await fetch("http://localhost:3000/api/listings", {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch listings");
  return res.json() as Promise<Listing[]>;
}

export default async function HomePage() {
  const listings = await getListings();

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="mx-auto max-w-7xl">
        <h1 className="mb-8 text-4xl font-bold">Marketplace</h1>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {listings.map((listing) => (
            <Link key={listing.id} href={`/listing/${listing.id}`}>
              <Card className="h-full overflow-hidden transition-shadow hover:shadow-lg">
                <CardHeader className="p-0">
                  <div className="relative h-48 w-full">
                    <Image
                      src={listing.imageUrl}
                      alt={listing.title}
                      fill
                      className="object-cover"
                    />
                  </div>
                </CardHeader>
                <CardContent className="p-4">
                  <CardTitle className="mb-2">{listing.title}</CardTitle>
                  <label className="text-sm text-gray-500">Ask</label>
                  <p className="text-2xl font-bold text-green-600">
                    ${listing.price.toFixed(2)}
                  </p>
                  <p className="mt-2 text-sm text-gray-600">
                    {listing.location}
                  </p>
                </CardContent>
                <CardFooter className="p-4 pt-0 text-sm text-gray-500">
                  Listed{" "}
                  {formatDistanceToNow(new Date(listing.datePosted), {
                    addSuffix: true,
                  })}
                </CardFooter>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
