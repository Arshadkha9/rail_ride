import { MapPin, Navigation, Radio } from 'lucide-react';
import type { LiveRide } from '@/types';
import { Badge, getStatusBadgeVariant } from '@/components/ui/Badge';

interface LiveMapProps {
  rides: LiveRide[];
  selectedRideId?: string | null;
  onSelectRide?: (ride: LiveRide) => void;
}

export function LiveMap({ rides, selectedRideId, onSelectRide }: LiveMapProps) {
  const activeRides = rides.filter(
    (r) => r.status === 'in_progress' || r.status === 'accepted'
  );

  return (
    <div className="live-map-container">
      <div className="live-map">
        <div className="live-map-grid" />
        <div className="live-map-overlay">
          <div className="live-map-header">
            <Navigation size={18} />
            <span>Live Ride Map</span>
            <Badge variant="success" dot>
              {activeRides.length} active
            </Badge>
          </div>

          <div className="live-map-markers">
            {activeRides.map((ride, index) => {
              const left = 15 + ((index * 23 + 17) % 70);
              const top = 20 + ((index * 31 + 11) % 60);
              const isSelected = ride.id === selectedRideId;

              return (
                <button
                  key={ride.id}
                  className={`map-marker ${isSelected ? 'selected' : ''}`}
                  style={{ left: `${left}%`, top: `${top}%` }}
                  onClick={() => onSelectRide?.(ride)}
                  title={`${ride.user_name} - ${ride.status}`}
                >
                  <MapPin size={20} />
                  <span className="map-marker-pulse" />
                </button>
              );
            })}

            {activeRides.length === 0 && (
              <div className="live-map-empty">
                <Radio size={32} />
                <p>No active rides on the map</p>
              </div>
            )}
          </div>

          <div className="live-map-legend">
            <div className="legend-item">
              <span className="legend-dot legend-dot-active" />
              Active ride
            </div>
            <div className="legend-item">
              <span className="legend-dot legend-dot-pickup" />
              Pickup point
            </div>
            <div className="legend-item">
              <span className="legend-dot legend-dot-dropoff" />
              Dropoff point
            </div>
          </div>
        </div>
      </div>

      {selectedRideId && (
        <div className="live-map-sidebar">
          {rides
            .filter((r) => r.id === selectedRideId)
            .map((ride) => (
              <div key={ride.id} className="live-ride-detail">
                <div className="live-ride-detail-header">
                  <span className="live-ride-id">#{ride.id.slice(0, 8)}</span>
                  <Badge variant={getStatusBadgeVariant(ride.status)} dot>
                    {ride.status.replace('_', ' ')}
                  </Badge>
                </div>
                <div className="live-ride-route">
                  <div className="route-point">
                    <span className="route-dot pickup" />
                    <div>
                      <span className="route-label">Pickup</span>
                      <span className="route-address">{ride.pickup.address}</span>
                    </div>
                  </div>
                  <div className="route-line" />
                  <div className="route-point">
                    <span className="route-dot dropoff" />
                    <div>
                      <span className="route-label">Dropoff</span>
                      <span className="route-address">{ride.dropoff.address}</span>
                    </div>
                  </div>
                </div>
                <div className="live-ride-meta">
                  <div>
                    <span className="meta-label">Passenger</span>
                    <span>{ride.user_name}</span>
                  </div>
                  <div>
                    <span className="meta-label">Driver</span>
                    <span>{ride.driver_name ?? 'Unassigned'}</span>
                  </div>
                  <div>
                    <span className="meta-label">Fare</span>
                    <span>${ride.fare.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
