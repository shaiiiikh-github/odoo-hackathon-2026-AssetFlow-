import { useContext } from "react";
import { AssetRequestContext } from "../context/AssetRequestContext";

export default function useAssetRequests() {
  const context = useContext(AssetRequestContext);

  if (!context) {
    throw new Error("useAssetRequests must be used within an AssetRequestProvider");
  }

  return context;
}