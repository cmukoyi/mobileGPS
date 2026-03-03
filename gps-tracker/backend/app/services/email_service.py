import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
import os

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "mailhog")
        self.smtp_port = int(os.getenv("SMTP_PORT", "1025"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@bletracker.com")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        
    def generate_pin(self) -> str:
        """Generate a 6-digit PIN"""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    def send_verification_pin(self, to_email: str, pin: str) -> bool:
        """Send verification PIN via email"""
        try:
            # Development mode - print to console (but still send email)
            if self.debug:
                print(f"\n{'='*60}")
                print(f"📧 VERIFICATION PIN for {to_email}")
                print(f"     PIN: {pin}")
                print(f"{'='*60}\n")
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Your BLE Tracker Verification Code'
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Plain text version
            text = f"""
            Your verification code is: {pin}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            BLE Tracker Team
            """
            
            # HTML version
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <h2 style="color: #173C64;">BLE Tracker Verification</h2>
                  <p>Your verification code is:</p>
                  <div style="background-color: #f4f4f4; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                    <h1 style="color: #173C64; font-size: 36px; letter-spacing: 8px; margin: 0;">{pin}</h1>
                  </div>
                  <p style="color: #666;">This code will expire in <strong>10 minutes</strong>.</p>
                  <p style="color: #666;">If you didn't request this code, please ignore this email.</p>
                  <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                  <p style="color: #999; font-size: 12px;">Best regards,<br>BLE Tracker Team</p>
                </div>
              </body>
            </html>
            """
            
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, first_name: Optional[str] = None) -> bool:
        """Send welcome email after successful registration"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Welcome to BLE Tracker'
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            name = first_name if first_name else "there"
            
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <h2 style="color: #173C64;">Welcome to BLE Tracker!</h2>
                  <p>Hi {name},</p>
                  <p>Thank you for joining BLE Tracker. Your account has been successfully created.</p>
                  <p>You can now start adding and tracking your BLE devices.</p>
                  <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                  <p style="color: #999; font-size: 12px;">Best regards,<br>BLE Tracker Team</p>
                </div>
              </body>
            </html>
            """
            
            part = MIMEText(html, 'html')
            msg.attach(part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            return False

    def send_geofence_alert(
        self, 
        to_email: str, 
        event_type: str,  # 'entry' or 'exit'
        poi_name: str,
        tracker_name: str,
        latitude: float,
        longitude: float,
        timestamp: str
    ) -> bool:
        """Send geofence alert email when tracker enters or exits a POI"""
        try:
            # Development mode - print to console (but still send email)
            if self.debug:
                print(f"\n{'='*60}")
                print(f"🚨 GEOFENCE ALERT for {to_email}")
                print(f"     Event: {event_type.upper()}")
                print(f"     POI: {poi_name}")
                print(f"     Tracker: {tracker_name}")
                print(f"     Location: {latitude}, {longitude}")
                print(f"     Time: {timestamp}")
                print(f"{'='*60}\n")
            
            event_emoji = "🟢" if event_type == "entry" else "🔴"
            event_action = "entered" if event_type == "entry" else "exited"
            event_color = "#4CAF50" if event_type == "entry" else "#F44336"
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'{event_emoji} Geofence Alert: {tracker_name} {event_action} {poi_name}'
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Plain text version
            text = f"""
            Geofence Alert
            
            Your tracker "{tracker_name}" has {event_action} the geofenced area "{poi_name}".
            
            Event: {event_type.upper()}
            Location: {poi_name}
            Tracker: {tracker_name}
            Coordinates: {latitude}, {longitude}
            Time: {timestamp}
            
            View location on map: https://www.google.com/maps?q={latitude},{longitude}
            
            Best regards,
            BLE Tracker Team
            """
            
            # HTML version
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <div style="background-color: {event_color}; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 32px;">{event_emoji} Geofence Alert</h1>
                  </div>
                  <div style="background-color: #f4f4f4; padding: 30px; border-radius: 0 0 8px 8px;">
                    <p style="font-size: 18px; margin-top: 0;">
                      Your tracker <strong>"{tracker_name}"</strong> has <strong style="color: {event_color};">{event_action}</strong> 
                      the geofenced area <strong>"{poi_name}"</strong>.
                    </p>
                    
                    <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
                      <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Event:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; color: {event_color}; font-weight: bold;">
                          {event_type.upper()}
                        </td>
                      </tr>
                      <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Location:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{poi_name}</td>
                      </tr>
                      <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Tracker:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{tracker_name}</td>
                      </tr>
                      <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Coordinates:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{latitude:.6f}, {longitude:.6f}</td>
                      </tr>
                      <tr>
                        <td style="padding: 10px;"><strong>Time:</strong></td>
                        <td style="padding: 10px;">{timestamp}</td>
                      </tr>
                    </table>
                    
                    <div style="text-align: center; margin: 30px 0;">
                      <a href="https://www.google.com/maps?q={latitude},{longitude}" 
                         style="display: inline-block; background-color: #173C64; color: white; 
                                padding: 12px 30px; text-decoration: none; border-radius: 5px; 
                                font-weight: bold;">
                        📍 View on Map
                      </a>
                    </div>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                      To stop receiving these alerts, you can disable email notifications in your app settings 
                      or disarm the geofence for this tracker.
                    </p>
                  </div>
                  <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                  <p style="color: #999; font-size: 12px;">Best regards,<br>BLE Tracker Team</p>
                </div>
              </body>
            </html>
            """
            
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Error sending geofence alert email: {e}")
            return False

