import React, { useEffect, useState } from "react";
import L from "leaflet";
import { MapContainer } from "react-leaflet/MapContainer";
import { TileLayer } from "react-leaflet/TileLayer";
import { Marker } from "react-leaflet/Marker";
import { Popup } from "react-leaflet/Popup";
import { Polyline } from "react-leaflet/Polyline";
import { nodes, edges } from "../utils/constants";
import "leaflet/dist/leaflet.css";

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

export default function Map({ path }) {
  const [markers, setMarkers] = useState([]);
  const [polylines, setPolylines] = useState([]);

  useEffect(() => {
    let optimalPathEdges = [];

    // Pairwise iteration of path
    for (let index = 0; index < path.length - 1; index++) {
      let current = path[index];
      let next = path[index + 1];

      optimalPathEdges.push([current, next]);

      // loop back around if we are done traversing
      if (index == path.length - 2) {
        let first = path[0];

        optimalPathEdges.push([next, first]);
      }
    }

    setMarkers(path);
    setPolylines(optimalPathEdges);
  }, [path]);

  return (
    <MapContainer
      // Center of contiguous US
      center={[37.0902, -95.7129]}
      // Shows all 49 states
      zoom={5}
      style={{ width: "100vw", height: "100vh" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {markers.map((position, index) => {
        return (
          <Marker
              key={`marker-${index}`}
              position={position}>
            <Popup
                keepInView={true}
            >
              <p>Position: {position.id}</p>
              <p>Index: {index + 1}</p>
            </Popup>
          </Marker>
        );
      })}
      {polylines.map((positions, index) => {
        return <Polyline key={`polyline-${index}`} positions={positions} />;
      })}
    </MapContainer>
  );
}
