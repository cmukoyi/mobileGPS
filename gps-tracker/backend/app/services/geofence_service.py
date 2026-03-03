"""
Geofence monitoring service for POI entry/exit detection
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import POI, BLETag, POITrackerLink, GeofenceAlert, GeofenceEventType, User, POIType
from app.services.email_service import EmailService
import math
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


class GeofenceService:
    """Service for monitoring geofences and generating entry/exit alerts"""
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in meters
        """
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        distance = R * c
        return distance
    
    @staticmethod
    def is_inside_geofence(
        lat: float, lon: float, 
        poi_lat: float, poi_lon: float, 
        radius: float
    ) -> bool:
        """Check if coordinates are inside a geofence"""
        distance = GeofenceService.calculate_distance(lat, lon, poi_lat, poi_lon)
        return distance <= radius
    
    @staticmethod
    def check_geofences_for_tracker(
        db: Session,
        tracker_id: str,
        current_lat: float,
        current_lon: float,
        user_id: str
    ) -> List[GeofenceAlert]:
        """
        Check all armed POIs for a tracker and generate alerts if needed
        Returns list of generated alerts
        """
        # Get all armed POIs for this tracker
        armed_links = db.query(POITrackerLink).filter(
            and_(
                POITrackerLink.tracker_id == tracker_id,
                POITrackerLink.is_armed == True
            )
        ).all()
        
        if not armed_links:
            return []
        
        generated_alerts = []
        
        for link in armed_links:
            poi = db.query(POI).filter(
                and_(
                    POI.id == link.poi_id,
                    POI.is_active == True
                )
            ).first()
            
            if not poi:
                continue
            
            # Handle different POI types
            if poi.poi_type == 'single':
                # Single location POI - monitor entry/exit at origin
                alerts = GeofenceService._check_single_poi(
                    db, poi, tracker_id, user_id, current_lat, current_lon
                )
                generated_alerts.extend(alerts)
            
            elif poi.poi_type == 'route':
                # Delivery route - monitor exit from origin and entry to destination
                alerts = GeofenceService._check_route_poi(
                    db, poi, tracker_id, user_id, current_lat, current_lon
                )
                generated_alerts.extend(alerts)
        
        if generated_alerts:
            db.commit()
        
        return generated_alerts
    
    @staticmethod
    def _check_single_poi(
        db: Session,
        poi: POI,
        tracker_id: str,
        user_id: str,
        current_lat: float,
        current_lon: float
    ) -> List[GeofenceAlert]:
        """Check single location POI for entry/exit events"""
        alerts = []
        
        # Check if tracker is inside this geofence
        is_inside = GeofenceService.is_inside_geofence(
            current_lat, current_lon,
            poi.latitude, poi.longitude,
            poi.radius
        )
        
        # Get the last alert for this POI-tracker combination
        last_alert = db.query(GeofenceAlert).filter(
            and_(
                GeofenceAlert.poi_id == poi.id,
                GeofenceAlert.tracker_id == tracker_id
            )
        ).order_by(GeofenceAlert.created_at.desc()).first()
        
        # Determine if we should generate an alert
        should_alert = False
        event_type = None
        
        if last_alert:
            # Check if state changed
            was_inside = (last_alert.event_type == GeofenceEventType.ENTRY)
            
            # Only alert if state changed and some time has passed (debouncing)
            time_since_last = datetime.now(timezone.utc) - last_alert.created_at
            debounce_seconds = 60  # Don't alert more than once per minute
            
            if time_since_last.total_seconds() > debounce_seconds:
                if is_inside and not was_inside:
                    should_alert = True
                    event_type = GeofenceEventType.ENTRY
                elif not is_inside and was_inside:
                    should_alert = True
                    event_type = GeofenceEventType.EXIT
        else:
            # First time checking this POI-tracker combo
            if is_inside:
                should_alert = True
                event_type = GeofenceEventType.ENTRY
        
        # Generate alert if needed
        if should_alert and event_type:
            alert = GeofenceAlert(
                poi_id=poi.id,
                tracker_id=tracker_id,
                user_id=user_id,
                event_type=event_type,
                latitude=current_lat,
                longitude=current_lon,
                is_read=False
            )
            db.add(alert)
            alerts.append(alert)
            
            logger.info(
                f"Single POI alert: {event_type.value} for {poi.name}, tracker {tracker_id}"
            )
            
            # Send email alert
            GeofenceService._send_email_alert(
                db, user_id, tracker_id, poi, event_type, current_lat, current_lon
            )
        
        return alerts
    
    @staticmethod
    def _check_route_poi(
        db: Session,
        poi: POI,
        tracker_id: str,
        user_id: str,
        current_lat: float,
        current_lon: float
    ) -> List[GeofenceAlert]:
        """Check delivery route POI for origin exit and destination entry"""
        alerts = []
        
        if not poi.destination_latitude or not poi.destination_longitude:
            logger.warning(f"Route POI {poi.id} missing destination coordinates")
            return alerts
        
        # Check origin (FROM) geofence - we care about EXITS
        is_at_origin = GeofenceService.is_inside_geofence(
            current_lat, current_lon,
            poi.latitude, poi.longitude,
            poi.radius
        )
        
        # Check destination (TO) geofence - we care about ENTRIES
        is_at_destination = GeofenceService.is_inside_geofence(
            current_lat, current_lon,
            poi.destination_latitude, poi.destination_longitude,
            poi.destination_radius or 150.0
        )
        
        # Get last two alerts for this route
        last_alerts = db.query(GeofenceAlert).filter(
            and_(
                GeofenceAlert.poi_id == poi.id,
                GeofenceAlert.tracker_id == tracker_id
            )
        ).order_by(GeofenceAlert.created_at.desc()).limit(2).all()
        
        last_alert = last_alerts[0] if last_alerts else None
        
        # Debouncing
        if last_alert:
            time_since_last = datetime.now(timezone.utc) - last_alert.created_at
            if time_since_last.total_seconds() < 60:  # 60 second debounce
                return alerts
        
        # Check for package leaving origin
        if last_alert and last_alert.event_type == GeofenceEventType.ENTRY:
            # Last event was entering origin, check if we've left
            if not is_at_origin:
                alert = GeofenceAlert(
                    poi_id=poi.id,
                    tracker_id=tracker_id,
                    user_id=user_id,
                    event_type=GeofenceEventType.EXIT,
                    latitude=current_lat,
                    longitude=current_lon,
                    is_read=False
                )
                db.add(alert)
                alerts.append(alert)
                logger.info(f"Route alert: Package LEFT origin for {poi.name}")
                GeofenceService._send_email_alert(
                    db, user_id, tracker_id, poi, GeofenceEventType.EXIT, 
                    current_lat, current_lon, location_name="origin"
                )
        
        # Check for package arriving at destination
        elif not last_alert or (last_alert and last_alert.event_type == GeofenceEventType.EXIT):
            # Either no events yet, or last event was leaving origin
            if is_at_destination:
                alert = GeofenceAlert(
                    poi_id=poi.id,
                    tracker_id=tracker_id,
                    user_id=user_id,
                    event_type=GeofenceEventType.ENTRY,
                    latitude=current_lat,
                    longitude=current_lon,
                    is_read=False
                )
                db.add(alert)
                alerts.append(alert)
                logger.info(f"Route alert: Package ARRIVED at destination for {poi.name}")
                GeofenceService._send_email_alert(
                    db, user_id, tracker_id, poi, GeofenceEventType.ENTRY, 
                    current_lat, current_lon, location_name="destination"
                )
        
        # First check - package is at origin
        elif not last_alert and is_at_origin:
            alert = GeofenceAlert(
                poi_id=poi.id,
                tracker_id=tracker_id,
                user_id=user_id,
                event_type=GeofenceEventType.ENTRY,
                latitude=current_lat,
                longitude=current_lon,
                is_read=False
            )
            db.add(alert)
            alerts.append(alert)
            logger.info(f"Route alert: Package AT origin for {poi.name}")
            GeofenceService._send_email_alert(
                db, user_id, tracker_id, poi, GeofenceEventType.ENTRY, 
                current_lat, current_lon, location_name="origin"
            )
        
        return alerts
    
    @staticmethod
    def _send_email_alert(
        db: Session,
        user_id: str,
        tracker_id: str,
        poi: POI,
        event_type: GeofenceEventType,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None
    ):
        """Send email alert for geofence event"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not getattr(user, 'email_alerts_enabled', True):
                return
            
            # Get tracker details
            tracker = db.query(BLETag).filter(BLETag.id == tracker_id).first()
            if tracker:
                # Priority: description > device_name > IMEI (last 4 digits) > generic name
                if tracker.description:
                    tracker_name = tracker.description
                elif tracker.device_name:
                    tracker_name = tracker.device_name
                elif tracker.imei:
                    # Use last 4 digits of IMEI for user-friendly identification
                    tracker_name = f"GPS Tracker ({tracker.imei[-4:]})"
                else:
                    tracker_name = "GPS Tracker"
            else:
                tracker_name = "GPS Tracker"
            
            # Customize message for routes
            if poi.poi_type == 'route' and location_name:
                if event_type == GeofenceEventType.EXIT and location_name == "origin":
                    event_description = f"left origin"
                elif event_type == GeofenceEventType.ENTRY and location_name == "destination":
                    event_description = f"arrived at destination"
                else:
                    event_description = f"at {location_name}"
            else:
                event_description = event_type.value
            
            # Send email
            email_service = EmailService()
            email_service.send_geofence_alert(
                to_email=user.email,
                event_type=event_description,
                poi_name=poi.name,
                tracker_name=tracker_name,
                latitude=latitude,
                longitude=longitude,
                timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            )
            logger.info(f"Email alert sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    @staticmethod
    def get_user_alerts(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> Tuple[List[GeofenceAlert], int, int]:
        """
        Get alerts for a user
        Returns: (alerts, total_count, unread_count)
        """
        query = db.query(GeofenceAlert).filter(GeofenceAlert.user_id == user_id)
        
        if unread_only:
            query = query.filter(GeofenceAlert.is_read == False)
        
        total_count = query.count()
        unread_count = db.query(GeofenceAlert).filter(
            and_(
                GeofenceAlert.user_id == user_id,
                GeofenceAlert.is_read == False
            )
        ).count()
        
        alerts = query.order_by(
            GeofenceAlert.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return alerts, total_count, unread_count
    
    @staticmethod
    def mark_alerts_read(db: Session, alert_ids: List[str], user_id: str) -> int:
        """
        Mark alerts as read
        Returns number of alerts updated
        """
        result = db.query(GeofenceAlert).filter(
            and_(
                GeofenceAlert.id.in_(alert_ids),
                GeofenceAlert.user_id == user_id
            )
        ).update({GeofenceAlert.is_read: True}, synchronize_session=False)
        
        db.commit()
        return result
    
    @staticmethod
    def mark_all_alerts_read(db: Session, user_id: str) -> int:
        """
        Mark all alerts for a user as read
        Returns number of alerts updated
        """
        result = db.query(GeofenceAlert).filter(
            and_(
                GeofenceAlert.user_id == user_id,
                GeofenceAlert.is_read == False
            )
        ).update({GeofenceAlert.is_read: True}, synchronize_session=False)
        
        db.commit()
        return result
