import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import json
import logging
from datetime import datetime, timedelta
import threading
from collections import deque
import time
import re
import yaml
from queue import Empty

class SignatureDatabase:
    def __init__(self):
        self.signatures = {
            'malware': [
                {
                    'name': 'Generic Backdoor',
                    'pattern': r'(backdoor|reverse shell|reverse_shell|bind shell|bind_shell)',
                    'severity': 'CRITICAL'
                },
                {
                    'name': 'Command Injection',
                    'pattern': r';.*(\||>|<|\$\(|`)',
                    'severity': 'CRITICAL'
                },
                {
                    'name': 'SQL Injection',
                    'pattern': r'(\'|--|\#|/\*|\*/|;|union\s+select|select.*from)',
                    'severity': 'CRITICAL'
                }
            ],
            'privilege_escalation': [
                {
                    'name': 'Sudo Abuse',
                    'pattern': r'(sudo\s+-i|sudo\s+su|sudo.*-s\s+\/bin\/bash)',
                    'severity': 'HIGH'
                },
                {
                    'name': 'SUID Exploitation',
                    'pattern': r'(chmod.*\+s|chmod.*u\+s|chmod.*4755)',
                    'severity': 'HIGH'
                }
            ],
            'data_exfiltration': [
                {
                    'name': 'Suspicious Data Transfer',
                    'pattern': r'(base64.*curl|wget.*pastebin|nc.*-e|netcat.*-e)',
                    'severity': 'HIGH'
                },
                {
                    'name': 'Suspicious File Access',
                    'pattern': r'(cat.*\/etc\/shadow|cat.*\/etc\/passwd|access.*\.ssh)',
                    'severity': 'HIGH'
                }
            ],
            'reconnaissance': [
                {
                    'name': 'Network Scanning',
                    'pattern': r'(nmap|port scan|nikto|dirb|gobuster)',
                    'severity': 'MEDIUM'
                },
                {
                    'name': 'System Enumeration',
                    'pattern': r'(whoami|id\s|uname\s+-a|cat.*\/proc)',
                    'severity': 'MEDIUM'
                }
            ]
        }
        
    def load_custom_signatures(self, filepath):
        """Load custom signatures from YAML file"""
        try:
            with open(filepath, 'r') as f:
                custom_sigs = yaml.safe_load(f)
                for category, sigs in custom_sigs.items():
                    if category not in self.signatures:
                        self.signatures[category] = []
                    self.signatures[category].extend(sigs)
        except Exception as e:
            logging.error(f"Error loading custom signatures: {e}")

    def match_signatures(self, content):
        """Match content against all signatures"""
        if not content:
            return []
            
        matches = []
        for category, signatures in self.signatures.items():
            for sig in signatures:
                if re.search(sig['pattern'], content, re.IGNORECASE):
                    match = {
                        'category': category,
                        'signature': sig['name'],
                        'severity': sig['severity'],
                        'pattern': sig['pattern']
                    }
                    matches.append(match)
        return matches

class AIDetectionEngine:
    def __init__(self, event_queue):
        self.logger = logging.getLogger(__name__)
        self.event_queue = event_queue
        self.event_history = deque(maxlen=10000)  # Store last 10000 events
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.feature_extractors = {
            'system': self.extract_system_features,
            'network': self.extract_network_features,
            'application': self.extract_application_features
        }
        self.signature_db = SignatureDatabase()
        self.setup_neural_network()
        
        # Try to load custom signatures if available
        try:
            self.signature_db.load_custom_signatures('config/custom_signatures.yaml')
        except Exception as e:
            self.logger.warning(f"Could not load custom signatures: {e}")
        
    def setup_neural_network(self):
        """Initialize deep learning model for pattern recognition"""
        inputs = tf.keras.Input(shape=(20,))
        x = tf.keras.layers.Dense(64, activation='relu')(inputs)
        x = tf.keras.layers.Dropout(0.2)(x)
        x = tf.keras.layers.Dense(32, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        x = tf.keras.layers.Dense(16, activation='relu')(x)
        outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
        
        self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
    def extract_features(self, event):
        """Extract features based on event type"""
        if not event or 'source' not in event or 'content' not in event:
            return np.zeros(20)
            
        extractor = self.feature_extractors.get(event['source'], self.extract_generic_features)
        return extractor(event)
        
    def extract_system_features(self, event):
        """Extract features from system events"""
        features = np.zeros(20)
        content = event.get('content', '').lower()
        
        # Feature engineering for system events
        features[0] = 1 if 'error' in content else 0
        features[1] = 1 if 'warning' in content else 0
        features[2] = 1 if 'critical' in content else 0
        features[3] = len(content.split())
        features[4] = content.count('failed')
        features[5] = 1 if 'permission denied' in content else 0
        features[6] = 1 if 'crash' in content else 0
        features[7] = 1 if 'kernel' in content else 0
        
        return features
        
    def extract_network_features(self, event):
        """Extract features from network events"""
        features = np.zeros(20)
        content = event.get('content', '').lower()
        
        # Feature engineering for network events
        features[0] = 1 if '404' in content else 0
        features[1] = 1 if '500' in content else 0
        features[2] = 1 if '403' in content else 0
        features[3] = 1 if 'denied' in content else 0
        features[4] = 1 if 'timeout' in content else 0
        features[5] = content.count('failed')
        features[6] = len(content.split())
        
        return features
        
    def extract_application_features(self, event):
        """Extract features from application events"""
        features = np.zeros(20)
        content = event.get('content', '').lower()
        
        # Feature engineering for application events
        features[0] = 1 if 'exception' in content else 0
        features[1] = 1 if 'error' in content else 0
        features[2] = content.count('failed')
        features[3] = len(content.split())
        features[4] = 1 if 'null' in content else 0
        features[5] = 1 if 'undefined' in content else 0
        features[6] = 1 if 'crash' in content else 0
        
        return features
        
    def extract_generic_features(self, event):
        """Extract generic features for unknown event types"""
        features = np.zeros(20)
        content = event.get('content', '').lower()
        
        # Generic feature extraction
        features[0] = len(content)
        features[1] = len(content.split())
        features[2] = sum(c.isdigit() for c in content)
        features[3] = sum(not c.isalnum() for c in content)
        
        return features
        
    def detect_anomalies(self, events_batch):
        """Detect anomalies in a batch of events"""
        if not events_batch:
            return []
            
        anomalies = []
        
        # Signature-based detection
        for event in events_batch:
            if not event:
                continue
                
            content = event.get('content', '')
            signature_matches = self.signature_db.match_signatures(content)
            
            if signature_matches:
                for match in signature_matches:
                    anomaly = {
                        'event': event,
                        'detection_type': 'signature',
                        'signature_match': match,
                        'timestamp': datetime.now().isoformat(),
                        'severity': match['severity']
                    }
                    anomalies.append(anomaly)
            
        # Extract features for ML-based detection
        features = np.array([self.extract_features(event) for event in events_batch if event])
        
        if len(features) > 0:
            # Scale features
            scaled_features = self.scaler.fit_transform(features)
            
            # Detect anomalies using Isolation Forest
            anomaly_scores = self.anomaly_detector.fit_predict(scaled_features)
            
            # Deep learning prediction
            dl_predictions = self.model.predict(scaled_features, verbose=0)
            
            # Combine ML predictions
            for i, (event, score, dl_pred) in enumerate(zip(events_batch, anomaly_scores, dl_predictions)):
                if event and (score == -1 or dl_pred > 0.8):  # Anomaly detected by either method
                    anomaly = {
                        'event': event,
                        'detection_type': 'ml',
                        'anomaly_score': float(dl_pred[0]),
                        'timestamp': datetime.now().isoformat(),
                        'severity': 'HIGH' if dl_pred > 0.9 else 'MEDIUM'
                    }
                    anomalies.append(anomaly)
                
        return anomalies
        
    def analyze_patterns(self):
        """Analyze patterns in event history"""
        if len(self.event_history) < 100:
            return
            
        # Convert events to feature matrix
        features = np.array([self.extract_features(event) for event in self.event_history if event])
        
        if len(features) > 0:
            scaled_features = self.scaler.fit_transform(features)
            
            # Train model on historical data
            labels = np.zeros(len(features))  # Assuming all historical events are normal
            self.model.fit(scaled_features, labels, epochs=5, verbose=0)
        
    def run(self):
        """Main execution loop"""
        self.logger.info("Starting AI Detection Engine")
        
        # Start pattern analysis in a separate thread
        pattern_thread = threading.Thread(target=self.periodic_pattern_analysis)
        pattern_thread.daemon = True
        pattern_thread.start()
        
        try:
            while True:
                try:
                    # Process events in batches
                    events_batch = []
                    
                    # Try to collect up to 10 events
                    for _ in range(10):
                        try:
                            event = self.event_queue.get_nowait()
                            if event:
                                events_batch.append(event)
                        except Empty:
                            break
                    
                    if events_batch:
                        anomalies = self.detect_anomalies(events_batch)
                        if anomalies:
                            self.handle_anomalies(anomalies)
                            
                        # Store valid events in history
                        self.event_history.extend([e for e in events_batch if e])
                    
                    time.sleep(0.1)  # Prevent tight loop
                    
                except Exception as e:
                    self.logger.error(f"Error in AI Detection Engine: {str(e)}")
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            self.logger.info("Stopping AI Detection Engine")
        except Exception as e:
            self.logger.error(f"Critical error in AI Detection Engine: {str(e)}")
            
    def periodic_pattern_analysis(self):
        """Periodically analyze patterns"""
        while True:
            self.analyze_patterns()
            time.sleep(300)  # Analyze every 5 minutes
            
    def handle_anomalies(self, anomalies):
        """Handle detected anomalies"""
        for anomaly in anomalies:
            self.logger.warning(f"Anomaly detected: {json.dumps(anomaly, indent=2)}")
            # Here you would implement alert generation, notification, etc. 