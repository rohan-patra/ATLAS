type StructuredOffer = {
  type: "offer";
  price: number;
};

type OfferAccepted = {
  type: "accepted";
  price: number;
};

export type Message =
  | { dateTime: Date; content: StructuredOffer; sender: "buyer" }
  | { dateTime: Date; content: OfferAccepted; sender: "seller" }
  | { dateTime: Date; content: string; sender: "buyer" | "seller" };
