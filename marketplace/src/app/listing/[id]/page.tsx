import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import Link from "next/link";
import type { Listing } from "@/types/listing";
import { notFound } from "next/navigation";
import { formatDistanceToNow } from "date-fns";

async function getListing(id: string) {
  const res = await fetch(`http://localhost:3000/api/listings/${id}`, {
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json() as Promise<Listing>;
}

export default async function ListingPage({
  params,
}: {
  params: { id: string };
}) {
  // eslint-disable-next-line @typescript-eslint/await-thenable
  const { id } = await params;
  const listing = await getListing(id);

  if (!listing) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="mx-auto max-w-4xl">
        <Link
          href="/"
          className="mb-6 inline-block text-blue-600 hover:text-blue-800"
        >
          ← Back to Listings
        </Link>

        <Card>
          <CardHeader className="p-0">
            <div className="relative h-96 w-full">
              <Image
                src={listing.imageUrl}
                alt={listing.title}
                fill
                className="object-cover"
              />
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="mb-4">
              <h1 className="text-3xl font-bold">{listing.title}</h1>
              <p className="mt-2 text-3xl font-bold text-green-600">
                ${listing.price.toFixed(2)}
              </p>
            </div>

            <div className="mb-6">
              <h2 className="text-xl font-semibold">Description</h2>
              <p className="mt-2 text-gray-600">{listing.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
              <div>
                <strong>Location:</strong>
                <p>{listing.location}</p>
              </div>
              <div>
                <strong>Posted by:</strong>
                <p>{listing.sellerName}</p>
              </div>
              <div>
                <p>
                  Listed{" "}
                  {formatDistanceToNow(new Date(listing.datePosted), {
                    addSuffix: true,
                  })}
                </p>
              </div>
            </div>

            <div className="mt-8">
              <form
                action={async () => {
                  "use server";
                  const res = await fetch(
                    "http://localhost:3000/api/conversations",
                    {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ listingId: listing.id }),
                    },
                  );
                  const data = await res.json();
                  if (data.conversationId) {
                    window.location.href = `/conversation/${data.conversationId}`;
                  }
                }}
              >
                <Button type="submit" className="w-full">
                  Message Seller
                </Button>
              </form>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
