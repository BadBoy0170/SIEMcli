import json
import logging
from datetime import datetime, timedelta
import re
from collections import defaultdict, deque
import threading
import time
from queue import Empty

class LogAnalyzer:
    def __init__(self, event_queue):
        self.event_queue = event_queue
        self.logger = logging.getLogger(__name__)
        self.event_patterns = self.load_patterns()
        self.event_history = deque(maxlen=10000)
        self.alert_history = defaultdict(list)
        self.correlation_rules = self.load_correlation_rules()
        self.setup_analyzers()
        
    def load_patterns(self):
        """Load pattern definitions"""
        return {
            'brute_force': {
                'pattern': r'Failed login attempt|Authentication failure',
                'threshold': 5,
                'timeframe': 300,  # 5 minutes
                'severity': 'HIGH'
            },
            'privilege_escalation': {
                'pattern': r'sudo|su\s|privilege|elevation',
                'threshold': 3,
                'timeframe': 600,  # 10 minutes
                'severity': 'CRITICAL'
            },
            'data_exfiltration': {
                'pattern': r'large file transfer|unusual network activity|data transfer',
                'threshold': 2,
                'timeframe': 900,  # 15 minutes
                'severity': 'CRITICAL'
            },
            'system_crash': {
                'pattern': r'kernel panic|system halt|crash dump',
                'threshold': 1,
                'timeframe': 300,
                'severity': 'CRITICAL'
            }
        }
        
    def load_correlation_rules(self):
        """Load event correlation rules"""
        return [
            {
                'name': 'potential_attack',
                'events': ['brute_force', 'privilege_escalation'],
                'timeframe': 900,  # 15 minutes
                'severity': 'CRITICAL'
            },
            {
                'name': 'data_breach',
                'events': ['privilege_escalation', 'data_exfiltration'],
                'timeframe': 1800,  # 30 minutes
                'severity': 'CRITICAL'
            }
        ]
        
    def setup_analyzers(self):
        """Setup different types of analyzers"""
        self.analyzers = {
            'pattern': self.analyze_patterns,
            'correlation': self.analyze_correlations,
            'frequency': self.analyze_frequency,
            'sequence': self.analyze_sequence
        }
        
    def analyze_event(self, event):
        """Analyze a single event using all analyzers"""
        results = []
        for analyzer_name, analyzer_func in self.analyzers.items():
            try:
                result = analyzer_func(event)
                if result:
                    results.extend(result)
            except Exception as e:
                self.logger.error(f"Error in {analyzer_name} analyzer: {str(e)}")
                
        return results
        
    def analyze_patterns(self, event):
        """Analyze event against known patterns"""
        matches = []
        content = event['content'].lower()
        
        for pattern_name, pattern_info in self.event_patterns.items():
            if re.search(pattern_info['pattern'], content, re.IGNORECASE):
                # Check threshold in timeframe
                recent_matches = [
                    e for e in self.event_history
                    if re.search(pattern_info['pattern'], e['content'], re.IGNORECASE)
                    and datetime.fromisoformat(e['timestamp']) > 
                    datetime.now() - timedelta(seconds=pattern_info['timeframe'])
                ]
                
                if len(recent_matches) >= pattern_info['threshold']:
                    match = {
                        'type': pattern_name,
                        'severity': pattern_info['severity'],
                        'matched_events': len(recent_matches),
                        'timestamp': datetime.now().isoformat(),
                        'description': f"Pattern {pattern_name} matched {len(recent_matches)} times"
                    }
                    matches.append(match)
                    
        return matches
        
    def analyze_correlations(self, event):
        """Analyze event correlations"""
        correlations = []
        
        for rule in self.correlation_rules:
            # Check if current event matches any rule events
            matching_patterns = [
                pattern for pattern in rule['events']
                if any(alert['type'] == pattern 
                    for alert in self.alert_history[event['source']]
                    if datetime.fromisoformat(alert['timestamp']) >
                    datetime.now() - timedelta(seconds=rule['timeframe']))
            ]
            
            if len(matching_patterns) == len(rule['events']):
                correlation = {
                    'type': 'correlation',
                    'rule_name': rule['name'],
                    'severity': rule['severity'],
                    'timestamp': datetime.now().isoformat(),
                    'description': f"Correlation rule {rule['name']} triggered"
                }
                correlations.append(correlation)
                
        return correlations
        
    def analyze_frequency(self, event):
        """Analyze event frequency"""
        alerts = []
        content = event['content'].lower()
        
        # Count similar events in the last 5 minutes
        recent_similar = [
            e for e in self.event_history
            if e['source'] == event['source']
            and self.calculate_similarity(e['content'], content) > 0.8
            and datetime.fromisoformat(e['timestamp']) >
            datetime.now() - timedelta(minutes=5)
        ]
        
        if len(recent_similar) > 10:  # Alert on high frequency
            alert = {
                'type': 'frequency',
                'severity': 'WARNING',
                'count': len(recent_similar),
                'timestamp': datetime.now().isoformat(),
                'description': f"High frequency of similar events detected: {len(recent_similar)} in 5 minutes"
            }
            alerts.append(alert)
            
        return alerts
        
    def analyze_sequence(self, event):
        """Analyze event sequences"""
        alerts = []
        
        # Look for specific sequences of events
        recent_events = list(self.event_history)[-5:]  # Last 5 events
        if len(recent_events) >= 3:
            # Example: Failed login followed by successful login and privilege escalation
            if (self.contains_pattern(recent_events[-3], 'Failed login') and
                self.contains_pattern(recent_events[-2], 'Successful login') and
                self.contains_pattern(recent_events[-1], 'sudo|su')):
                
                alert = {
                    'type': 'sequence',
                    'severity': 'HIGH',
                    'timestamp': datetime.now().isoformat(),
                    'description': "Suspicious login sequence detected"
                }
                alerts.append(alert)
                
        return alerts
        
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        # Simple similarity based on common words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0
        
    def contains_pattern(self, event, pattern):
        """Check if event contains pattern"""
        return bool(re.search(pattern, event['content'], re.IGNORECASE))
        
    def handle_alerts(self, alerts):
        """Handle generated alerts"""
        for alert in alerts:
            self.logger.warning(f"Alert generated: {json.dumps(alert, indent=2)}")
            # Store alert in history
            self.alert_history[alert['type']].append(alert)
            # Here you would implement notification system, dashboard updates, etc.
            
    def run(self):
        """Main execution loop"""
        self.logger.info("Starting Log Analyzer")
        
        try:
            while True:
                try:
                    # Get event from queue (non-blocking)
                    event = self.event_queue.get_nowait()
                    
                    # Store event in history
                    self.event_history.append(event)
                    
                    # Analyze event
                    alerts = self.analyze_event(event)
                    
                    # Handle any generated alerts
                    if alerts:
                        self.handle_alerts(alerts)
                        
                except Empty:
                    # No events in queue, sleep briefly
                    time.sleep(0.1)
                except Exception as e:
                    self.logger.error(f"Error processing event: {str(e)}")
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            self.logger.info("Stopping Log Analyzer")
        except Exception as e:
            self.logger.error(f"Critical error in Log Analyzer: {str(e)}") 